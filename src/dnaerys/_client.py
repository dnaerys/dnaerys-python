"""DnaerysClient — main entry point for the Dnaerys genomic data service.

Provides a Pythonic interface to the Dnaerys gRPC service, mapping ~20
public methods to 36 underlying RPCs.  All methods resolve enum/assembly
parameters, route through the dispatch layer (where applicable), convert
proto responses to frozen dataclasses, and translate gRPC errors into the
``DnaerysError`` hierarchy.

Usage::

    with DnaerysClient("db.dnaerys.org:443") as client:
        for v in client.select_variants(region=Region("chr1", 1000, 5000)):
            print(v)
"""

from __future__ import annotations

import warnings
from typing import Any

import grpc

from dnaerys._channel import create_channel
from dnaerys._convert import (
    annotation_filter_to_proto,
    convert_alleles_with_stats_response_to_top_chi2,
    convert_alleles_with_stats_response_to_top_hwe,
    convert_cluster_nodes_response,
    convert_count_alleles_response,
    convert_count_samples_response,
    convert_dataset_info_response,
    convert_fstat_x_response,
    convert_health_response,
    convert_kinship_response,
    convert_prs_response,
    convert_sample_kinship_response,
    convert_samples_response,
    convert_sex_mismatch_response,
)
from dnaerys._dispatch import (
    dispatch_count_samples,
    dispatch_count_variants,
    dispatch_select_samples,
    dispatch_select_variants,
    dispatch_select_variants_with_stats,
)
from dnaerys._enums import (
    Chromosome,
    KinshipDegree,
    RefAssembly,
    resolve_assembly,
    resolve_chromosome,
    resolve_enum,
)
from dnaerys._exceptions import (
    DnaerysIncompleteResultWarning,
    DnaerysInvalidRequestError,
    raise_for_grpc_error,
)
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._proto import dnaerys_pb2_grpc
from dnaerys._pagination import PaginatedQuery
from dnaerys._stream import VariantStream, VariantWithStatsStream
from dnaerys._types import (
    AnnotationFilter,
    Bracket,
    ClusterNodesResult,
    CountResult,
    DatasetInfo,
    FstatXResult,
    HealthResult,
    KinshipResult,
    PrsResult,
    Region,
    SampleKinshipResult,
    SamplesResult,
    SexMismatchResult,
    TopChi2Result,
    TopHweResult,
)


def _warn_affected(metadata: object) -> None:
    """Emit DnaerysIncompleteResultWarning if metadata.affected is True."""
    if getattr(metadata, "affected", False):
        warnings.warn(
            "Results may be incomplete: cluster nodes holding "
            "potentially relevant data were unreachable.",
            DnaerysIncompleteResultWarning,
            stacklevel=3,
        )


class DnaerysClient:
    """Client for the Dnaerys genomic data service.

    Parameters
    ----------
    target : str
        Server address in ``host:port`` format.
    tls : bool
        If ``True`` (default), create a secure TLS channel.
    credentials : grpc.ChannelCredentials | None
        Custom TLS credentials.  If ``None`` and *tls* is ``True``,
        default SSL credentials are used.
    options : dict[str, Any] | None
        gRPC channel options as ``{key: value}`` pairs.
    default_timeout : float | None
        Default per-call timeout in seconds.  ``None`` means no timeout.
    assembly : RefAssembly | str
        Default reference assembly for all queries.  Can be overridden
        per-method.

    Usage::

        with DnaerysClient("db.dnaerys.org:443") as client:
            for v in client.select_variants(region=Region("chr1", 1000, 5000)):
                print(v)
    """

    def __init__(
        self,
        target: str = "db.dnaerys.org:443",
        *,
        tls: bool = True,
        credentials: grpc.ChannelCredentials | None = None,
        options: dict[str, Any] | None = None,
        default_timeout: float | None = None,
        assembly: RefAssembly | str = RefAssembly.GRCh38,
    ) -> None:
        self._assembly = resolve_assembly(assembly) if isinstance(assembly, str) else assembly
        self._default_timeout = default_timeout
        self._channel = create_channel(target, tls=tls, credentials=credentials, options=options)
        self._stub = dnaerys_pb2_grpc.DnaerysServiceStub(self._channel)

    # -- Context manager ----------------------------------------------------

    def __enter__(self) -> DnaerysClient:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    def close(self) -> None:
        """Close the underlying gRPC channel."""
        self._channel.close()

    # -- Internal helpers ---------------------------------------------------

    def _timeout(self, timeout: float | None) -> float | None:
        return timeout if timeout is not None else self._default_timeout

    def _asm(self, assembly: RefAssembly | str | None) -> RefAssembly:
        if assembly is None:
            return self._assembly
        return resolve_assembly(assembly) if isinstance(assembly, str) else assembly

    # ======================================================================
    # Infrastructure (3 methods)
    # ======================================================================

    def health(self, *, timeout: float | None = None) -> HealthResult:
        """Check server health status."""
        try:
            response = self._stub.Health(
                pb2.HealthRequest(), timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_health_response(response)

    def cluster_nodes(self, *, timeout: float | None = None) -> ClusterNodesResult:
        """Return cluster node status."""
        try:
            response = self._stub.ClusterNodes(
                pb2.ClusterNodesRequest(), timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_cluster_nodes_response(response)

    def dataset_info(
        self,
        *,
        return_sample_names: bool = False,
        timeout: float | None = None,
    ) -> DatasetInfo:
        """Return dataset information (cohorts, PRS catalog, assembly, etc.)."""
        try:
            response = self._stub.DatasetInfo(
                pb2.DatasetInfoRequest(return_samples_names=return_sample_names),
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_dataset_info_response(response)

    # ======================================================================
    # Variant queries (3 methods)
    # ======================================================================

    def _select_variants(
        self,
        *,
        skip: int | None,
        limit: int | None,
        region: Region | None = None,
        regions: list[Region] | None = None,
        bracket: Bracket | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select variants (internal, keeps skip+limit for pagination)."""
        raw_iter = dispatch_select_variants(
            self._stub,
            region=region,
            regions=regions,
            bracket=bracket,
            samples=samples,
            hom=hom,
            het=het,
            annotations=annotations,
            assembly=self._asm(assembly),
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            skip=skip,
            limit=limit,
            timeout=self._timeout(timeout),
        )
        return VariantStream(raw_iter, limit=limit)

    def select_variants(
        self,
        *,
        region: Region | None = None,
        regions: list[Region] | None = None,
        bracket: Bracket | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select variants matching the given criteria (streaming)."""
        return self._select_variants(
            skip=None,
            limit=limit,
            region=region,
            regions=regions,
            bracket=bracket,
            samples=samples,
            hom=hom,
            het=het,
            annotations=annotations,
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            assembly=assembly,
            timeout=timeout,
        )

    def paginate_variants(
        self,
        *,
        page_size: int,
        buffer_size: int = 5000,
        region: Region | None = None,
        regions: list[Region] | None = None,
        bracket: Bracket | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> PaginatedQuery:
        """Create a paginated query for variants."""
        def fetch(skip: int, limit: int) -> VariantStream:
            return self._select_variants(
                skip=skip, limit=limit,
                region=region, regions=regions, bracket=bracket,
                samples=samples, hom=hom, het=het,
                annotations=annotations,
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                assembly=assembly, timeout=timeout,
            )
        return PaginatedQuery(fetch, page_size=page_size, buffer_size=buffer_size)

    def _select_variants_with_stats(
        self,
        *,
        skip: int | None,
        limit: int | None,
        region: Region | None = None,
        regions: list[Region] | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantWithStatsStream:
        """Select variants with stats (internal, keeps skip+limit for pagination)."""
        raw_iter = dispatch_select_variants_with_stats(
            self._stub,
            region=region,
            regions=regions,
            samples=samples,
            hom=hom,
            het=het,
            annotations=annotations,
            assembly=self._asm(assembly),
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            skip=skip,
            limit=limit,
            timeout=self._timeout(timeout),
        )
        return VariantWithStatsStream(raw_iter, limit=limit)

    def select_variants_with_stats(
        self,
        *,
        region: Region | None = None,
        regions: list[Region] | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantWithStatsStream:
        """Select variants with per-variant statistics (streaming).

        Accepts a single ``region`` or a list of ``regions``, with or
        without ``samples``.  A single region without samples is
        automatically routed to the multi-region RPC transparently.
        """
        return self._select_variants_with_stats(
            skip=None,
            limit=limit,
            region=region,
            regions=regions,
            samples=samples,
            hom=hom,
            het=het,
            annotations=annotations,
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            assembly=assembly,
            timeout=timeout,
        )

    def paginate_variants_with_stats(
        self,
        *,
        page_size: int,
        buffer_size: int = 5000,
        region: Region | None = None,
        regions: list[Region] | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> PaginatedQuery:
        """Create a paginated query for variants with statistics."""
        def fetch(skip: int, limit: int) -> VariantWithStatsStream:
            return self._select_variants_with_stats(
                skip=skip, limit=limit,
                region=region, regions=regions,
                samples=samples, hom=hom, het=het,
                annotations=annotations,
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                assembly=assembly, timeout=timeout,
            )
        return PaginatedQuery(fetch, page_size=page_size, buffer_size=buffer_size)

    def count_variants(
        self,
        *,
        region: Region | None = None,
        regions: list[Region] | None = None,
        bracket: Bracket | None = None,
        samples: list[str] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> CountResult:
        """Count variants matching the given criteria."""
        try:
            response = dispatch_count_variants(
                self._stub,
                region=region,
                regions=regions,
                bracket=bracket,
                samples=samples,
                hom=hom,
                het=het,
                annotations=annotations,
                assembly=self._asm(assembly),
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_count_alleles_response(response)
        _warn_affected(result.metadata)
        return result

    # ======================================================================
    # Sample queries (4 methods)
    # ======================================================================

    def select_samples(
        self,
        *,
        region: Region | None = None,
        regions: list[Region] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        skip: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> SamplesResult:
        """Select samples with variants in the given region(s)."""
        try:
            response = dispatch_select_samples(
                self._stub,
                region=region,
                regions=regions,
                hom=hom,
                het=het,
                annotations=annotations,
                assembly=self._asm(assembly),
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                skip=skip,
                limit=limit,
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_samples_response(response)
        _warn_affected(result.metadata)
        return result

    def count_samples(
        self,
        *,
        region: Region | None = None,
        regions: list[Region] | None = None,
        hom: bool = True,
        het: bool = True,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> CountResult:
        """Count samples with variants in the given region(s)."""
        try:
            response = dispatch_count_samples(
                self._stub,
                region=region,
                regions=regions,
                hom=hom,
                het=het,
                annotations=annotations,
                assembly=self._asm(assembly),
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_count_samples_response(response)
        _warn_affected(result.metadata)
        return result

    def select_samples_hom_ref(
        self,
        *,
        chr: Chromosome | str | int,
        position: int,
        skip: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> SamplesResult:
        """Select samples with homozygous reference calls at a position."""
        kwargs: dict[str, object] = {
            "chr": int(resolve_chromosome(chr)),
            "position": position,
            "assembly": int(self._asm(assembly)),
        }
        if skip is not None:
            kwargs["skip"] = skip
        if limit is not None:
            kwargs["limit"] = limit
        try:
            response = self._stub.SelectSamplesHomReference(
                pb2.SamplesHomRefRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_samples_response(response)
        _warn_affected(result.metadata)
        return result

    def count_samples_hom_ref(
        self,
        *,
        chr: Chromosome | str | int,
        position: int,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> CountResult:
        """Count samples with homozygous reference calls at a position."""
        try:
            response = self._stub.CountSamplesHomReference(
                pb2.SamplesHomRefRequest(
                    chr=int(resolve_chromosome(chr)),
                    position=position,
                    assembly=int(self._asm(assembly)),
                ),
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_count_samples_response(response)
        _warn_affected(result.metadata)
        return result

    # ======================================================================
    # Inheritance (3 methods)
    # ======================================================================

    def _build_inheritance_kwargs(
        self,
        region: Region,
        annotations: AnnotationFilter | None,
        variant_min_length: int | None,
        variant_max_length: int | None,
        skip: int | None,
        limit: int | None,
        assembly: RefAssembly | str | None,
    ) -> dict:
        """Build common kwargs for inheritance request protos."""
        kw: dict = {
            "chr": int(region.chr),
            "start": region.start,
            "end": region.end,
            "ref": region.ref or "",
            "alt": region.alt or "",
            "assembly": int(self._asm(assembly)),
        }
        if annotations is not None:
            kw["ann"] = annotation_filter_to_proto(annotations)
        if variant_min_length is not None:
            kw["variantMinLength"] = variant_min_length
        if variant_max_length is not None:
            kw["variantMaxLength"] = variant_max_length
        if skip is not None:
            kw["skip"] = skip
        if limit is not None:
            kw["limit"] = limit
        return kw

    def _select_de_novo(
        self,
        *,
        skip: int | None,
        limit: int | None,
        parent1: str,
        parent2: str,
        proband: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select de novo variants (internal, keeps skip+limit for pagination)."""
        kw = self._build_inheritance_kwargs(
            region, annotations, variant_min_length, variant_max_length,
            skip, limit, assembly,
        )
        request = pb2.DeNovoRequest(
            parent1=parent1, parent2=parent2, proband=proband, **kw,
        )
        raw_iter = self._stub.SelectDeNovo(request, timeout=self._timeout(timeout))
        return VariantStream(raw_iter, limit=limit)

    def select_de_novo(
        self,
        *,
        parent1: str,
        parent2: str,
        proband: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select de novo candidate variants in a proband (streaming)."""
        return self._select_de_novo(
            skip=None, limit=limit,
            parent1=parent1, parent2=parent2, proband=proband,
            region=region, annotations=annotations,
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            assembly=assembly, timeout=timeout,
        )

    def paginate_de_novo(
        self,
        *,
        page_size: int,
        buffer_size: int = 5000,
        parent1: str,
        parent2: str,
        proband: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> PaginatedQuery:
        """Create a paginated query for de novo candidate variants."""
        def fetch(skip: int, limit: int) -> VariantStream:
            return self._select_de_novo(
                skip=skip, limit=limit,
                parent1=parent1, parent2=parent2, proband=proband,
                region=region, annotations=annotations,
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                assembly=assembly, timeout=timeout,
            )
        return PaginatedQuery(fetch, page_size=page_size, buffer_size=buffer_size)

    def _select_het_dominant(
        self,
        *,
        skip: int | None,
        limit: int | None,
        affected_parent: str,
        unaffected_parent: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select het dominant variants (internal, keeps skip+limit for pagination)."""
        kw = self._build_inheritance_kwargs(
            region, annotations, variant_min_length, variant_max_length,
            skip, limit, assembly,
        )
        request = pb2.HetDominantRequest(
            affected_parent=affected_parent,
            unaffected_parent=unaffected_parent,
            affected_child=affected_child,
            **kw,
        )
        raw_iter = self._stub.SelectHetDominant(request, timeout=self._timeout(timeout))
        return VariantStream(raw_iter, limit=limit)

    def select_het_dominant(
        self,
        *,
        affected_parent: str,
        unaffected_parent: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select heterozygous dominant candidate variants (streaming)."""
        return self._select_het_dominant(
            skip=None, limit=limit,
            affected_parent=affected_parent,
            unaffected_parent=unaffected_parent,
            affected_child=affected_child,
            region=region, annotations=annotations,
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            assembly=assembly, timeout=timeout,
        )

    def paginate_het_dominant(
        self,
        *,
        page_size: int,
        buffer_size: int = 5000,
        affected_parent: str,
        unaffected_parent: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> PaginatedQuery:
        """Create a paginated query for heterozygous dominant candidate variants."""
        def fetch(skip: int, limit: int) -> VariantStream:
            return self._select_het_dominant(
                skip=skip, limit=limit,
                affected_parent=affected_parent,
                unaffected_parent=unaffected_parent,
                affected_child=affected_child,
                region=region, annotations=annotations,
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                assembly=assembly, timeout=timeout,
            )
        return PaginatedQuery(fetch, page_size=page_size, buffer_size=buffer_size)

    def _select_hom_recessive(
        self,
        *,
        skip: int | None,
        limit: int | None,
        unaffected_parent1: str,
        unaffected_parent2: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select hom recessive variants (internal, keeps skip+limit for pagination)."""
        kw = self._build_inheritance_kwargs(
            region, annotations, variant_min_length, variant_max_length,
            skip, limit, assembly,
        )
        request = pb2.HomRecessiveRequest(
            unaffected_parent1=unaffected_parent1,
            unaffected_parent2=unaffected_parent2,
            affected_child=affected_child,
            **kw,
        )
        raw_iter = self._stub.SelectHomRecessive(request, timeout=self._timeout(timeout))
        return VariantStream(raw_iter, limit=limit)

    def select_hom_recessive(
        self,
        *,
        unaffected_parent1: str,
        unaffected_parent2: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        limit: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> VariantStream:
        """Select homozygous recessive candidate variants (streaming)."""
        return self._select_hom_recessive(
            skip=None, limit=limit,
            unaffected_parent1=unaffected_parent1,
            unaffected_parent2=unaffected_parent2,
            affected_child=affected_child,
            region=region, annotations=annotations,
            variant_min_length=variant_min_length,
            variant_max_length=variant_max_length,
            assembly=assembly, timeout=timeout,
        )

    def paginate_hom_recessive(
        self,
        *,
        page_size: int,
        buffer_size: int = 5000,
        unaffected_parent1: str,
        unaffected_parent2: str,
        affected_child: str,
        region: Region,
        annotations: AnnotationFilter | None = None,
        variant_min_length: int | None = None,
        variant_max_length: int | None = None,
        assembly: RefAssembly | str | None = None,
        timeout: float | None = None,
    ) -> PaginatedQuery:
        """Create a paginated query for homozygous recessive candidate variants."""
        def fetch(skip: int, limit: int) -> VariantStream:
            return self._select_hom_recessive(
                skip=skip, limit=limit,
                unaffected_parent1=unaffected_parent1,
                unaffected_parent2=unaffected_parent2,
                affected_child=affected_child,
                region=region, annotations=annotations,
                variant_min_length=variant_min_length,
                variant_max_length=variant_max_length,
                assembly=assembly, timeout=timeout,
            )
        return PaginatedQuery(fetch, page_size=page_size, buffer_size=buffer_size)

    # ======================================================================
    # Statistics (5 methods)
    # ======================================================================

    def top_hwe(
        self,
        *,
        n: int,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> TopHweResult:
        """Return top N variants by Hardy-Weinberg equilibrium p-value."""
        try:
            response = self._stub.TopNHWE(
                pb2.TopNHWERequest(n=n, seq=sequential),
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_alleles_with_stats_response_to_top_hwe(response)
        _warn_affected(result.metadata)
        return result

    def top_chi2(
        self,
        *,
        n: int,
        samples: list[str],
        sequential: bool = False,
        timeout: float | None = None,
    ) -> TopChi2Result:
        """Return top N variants by chi-squared test p-value."""
        try:
            response = self._stub.TopNchi2(
                pb2.TopNchi2Request(n=n, samples=samples, seq=sequential),
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        result = convert_alleles_with_stats_response_to_top_chi2(response)
        _warn_affected(result.metadata)
        return result

    def prs(
        self,
        *,
        prs_name: str,
        cohort_name: str | None = None,
        samples: list[str] | None = None,
        dominant: bool = False,
        recessive: bool = False,
        timeout: float | None = None,
    ) -> PrsResult:
        """Calculate polygenic risk scores."""
        if cohort_name is None and not samples:
            raise DnaerysInvalidRequestError(
                "at least one of cohort_name or samples must be provided"
            )
        kwargs: dict[str, object] = {
            "prs_name": prs_name,
            "dominant": dominant,
            "recessive": recessive,
        }
        if cohort_name is not None:
            kwargs["cohort_name"] = cohort_name
        if samples:
            kwargs["samples"] = samples
        try:
            response = self._stub.Prs(
                pb2.PRSRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_prs_response(response)

    def sex_mismatch_check(
        self,
        *,
        cohort_name: str | None = None,
        samples: list[str] | None = None,
        aaf_threshold: float | None = None,
        female_threshold: float = 0.7,
        male_threshold: float = 0.7,
        include_par: bool = False,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> SexMismatchResult:
        """Run sex mismatch check based on X-chromosome F-statistics."""
        if cohort_name is None and not samples:
            raise DnaerysInvalidRequestError(
                "at least one of cohort_name or samples must be provided"
            )
        kwargs: dict[str, object] = {
            "female_threshold": female_threshold,
            "male_threshold": male_threshold,
            "include_par": include_par,
            "seq": sequential,
        }
        if cohort_name is not None:
            kwargs["cohort_name"] = cohort_name
        if samples:
            kwargs["samples"] = samples
        if aaf_threshold is not None:
            kwargs["aaf_threshold"] = aaf_threshold
        try:
            response = self._stub.SexMismatchCheck(
                pb2.FstatXRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_sex_mismatch_response(response)

    def fstat_x(
        self,
        *,
        cohort_name: str | None = None,
        samples: list[str] | None = None,
        aaf_threshold: float | None = None,
        include_par: bool = False,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> FstatXResult:
        """Calculate F-statistics for X chromosome."""
        if cohort_name is None and not samples:
            raise DnaerysInvalidRequestError(
                "at least one of cohort_name or samples must be provided"
            )
        kwargs: dict[str, object] = {
            "include_par": include_par,
            "seq": sequential,
        }
        if cohort_name is not None:
            kwargs["cohort_name"] = cohort_name
        if samples:
            kwargs["samples"] = samples
        if aaf_threshold is not None:
            kwargs["aaf_threshold"] = aaf_threshold
        try:
            response = self._stub.FstatX(
                pb2.FstatXRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_fstat_x_response(response)

    # ======================================================================
    # Kinship (4 methods)
    # ======================================================================

    def kinship(
        self,
        *,
        cohort_name: str | None = None,
        samples: list[str] | None = None,
        degree: KinshipDegree | str | None = None,
        threshold: float | None = None,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> KinshipResult:
        """Calculate kinship coefficients for all sample pairs."""
        if cohort_name is None and not samples:
            raise DnaerysInvalidRequestError(
                "at least one of cohort_name or samples must be provided"
            )
        if degree is not None and threshold is not None:
            raise DnaerysInvalidRequestError(
                "degree and threshold are mutually exclusive"
            )
        kwargs: dict[str, object] = {"seq": sequential}
        if cohort_name is not None:
            kwargs["cohort_name"] = cohort_name
        if samples:
            kwargs["samples"] = samples
        if degree is not None:
            kwargs["degree"] = int(
                resolve_enum(KinshipDegree, degree) if isinstance(degree, str) else degree
            )
        if threshold is not None:
            kwargs["threshold"] = threshold
        try:
            response = self._stub.Kinship(
                pb2.KinshipRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_kinship_response(response)

    def kinship_duo(
        self,
        *,
        sample1: str,
        sample2: str,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> KinshipResult:
        """Calculate kinship coefficient between two samples."""
        try:
            response = self._stub.KinshipDuo(
                pb2.KinshipDuoRequest(
                    sample1=sample1, sample2=sample2, seq=sequential,
                ),
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_kinship_response(response)

    def kinship_trio(
        self,
        *,
        sample1: str,
        sample2: str,
        sample3: str,
        degree: KinshipDegree | str | None = None,
        threshold: float | None = None,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> KinshipResult:
        """Calculate kinship coefficients for a trio."""
        if degree is not None and threshold is not None:
            raise DnaerysInvalidRequestError(
                "degree and threshold are mutually exclusive"
            )
        kwargs: dict[str, object] = {
            "sample1": sample1,
            "sample2": sample2,
            "sample3": sample3,
            "seq": sequential,
        }
        if degree is not None:
            kwargs["degree"] = int(
                resolve_enum(KinshipDegree, degree) if isinstance(degree, str) else degree
            )
        if threshold is not None:
            kwargs["threshold"] = threshold
        try:
            response = self._stub.KinshipTrio(
                pb2.KinshipTrioRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_kinship_response(response)

    def sample_kinship(
        self,
        *,
        sample_vcf: str,
        cohort_name: str | None = None,
        degree: KinshipDegree | str | None = None,
        threshold: float | None = None,
        sequential: bool = False,
        timeout: float | None = None,
    ) -> SampleKinshipResult:
        """Find relatives of a sample (provided as VCF) in the dataset."""
        kwargs: dict[str, object] = {
            "sample_vcf": sample_vcf,
            "seq": sequential,
        }
        if cohort_name is not None:
            kwargs["cohort_name"] = cohort_name
        if degree is not None:
            kwargs["degree"] = int(
                resolve_enum(KinshipDegree, degree) if isinstance(degree, str) else degree
            )
        if threshold is not None:
            kwargs["threshold"] = threshold
        try:
            response = self._stub.SampleKinship(
                pb2.SampleKinshipRequest(**kwargs),  # type: ignore[arg-type]
                timeout=self._timeout(timeout),
            )
        except grpc.RpcError as e:
            raise_for_grpc_error(e)
        return convert_sample_kinship_response(response)
