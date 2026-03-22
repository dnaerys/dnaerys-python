"""Dispatch routing for mapping user parameters to specific gRPC RPCs and request messages.

Each dispatch function validates user parameters, constructs the appropriate
protobuf request message, and invokes the correct stub method.  Streaming RPCs
return a gRPC iterator; unary RPCs return the response proto directly.
"""

from __future__ import annotations

from typing import Iterator

from dnaerys._convert import annotation_filter_to_proto
from dnaerys._enums import RefAssembly
from dnaerys._exceptions import DnaerysInvalidRequestError
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._proto import dnaerys_pb2_grpc
from dnaerys._types import AnnotationFilter, Bracket, Region


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_exactly_one(**kwargs: object) -> None:
    """Ensure exactly one of the keyword arguments is not None.

    Raises
    ------
    DnaerysInvalidRequestError
        If zero or more than one argument is not None.
    """
    set_names = [name for name, val in kwargs.items() if val is not None]
    if len(set_names) == 0:
        all_names = ", ".join(kwargs)
        raise DnaerysInvalidRequestError(
            f"exactly one of {all_names} must be provided"
        )
    if len(set_names) > 1:
        all_names = ", ".join(kwargs)
        got = ", ".join(set_names)
        raise DnaerysInvalidRequestError(
            f"only one of {all_names} can be provided, got: {got}"
        )


# ---------------------------------------------------------------------------
# Internal field construction helpers
# ---------------------------------------------------------------------------


def _ann_kwargs(annotations: AnnotationFilter | None) -> dict:
    if annotations is not None:
        return {"ann": annotation_filter_to_proto(annotations)}
    return {}


def _variant_length_kwargs(
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> dict:
    kw: dict = {}
    if variant_min_length is not None:
        kw["variantMinLength"] = variant_min_length
    if variant_max_length is not None:
        kw["variantMaxLength"] = variant_max_length
    return kw


def _skip_limit_kwargs(skip: int | None, limit: int | None) -> dict:
    kw: dict = {}
    if skip is not None:
        kw["skip"] = skip
    if limit is not None:
        kw["limit"] = limit
    return kw


def _common_kwargs(
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> dict:
    return {
        "hom": hom,
        "het": het,
        "assembly": int(assembly),
        **_ann_kwargs(annotations),
        **_variant_length_kwargs(variant_min_length, variant_max_length),
    }


def _region_kwargs(region: Region) -> dict:
    return {
        "chr": int(region.chr),
        "start": region.start,
        "end": region.end,
        "ref": region.ref or "",
        "alt": region.alt or "",
    }


def _bracket_kwargs(bracket: Bracket) -> dict:
    return {
        "chr": int(bracket.chr),
        "start_min": bracket.start_min,
        "start_max": bracket.start_max,
        "end_min": bracket.end_min,
        "end_max": bracket.end_max,
        "ref": bracket.ref or "",
        "alt": bracket.alt or "",
    }


def _multi_region_kwargs(regions: list[Region]) -> dict:
    return {
        "chr": [int(r.chr) for r in regions],
        "start": [r.start for r in regions],
        "end": [r.end for r in regions],
        "ref": [r.ref or "" for r in regions],
        "alt": [r.alt or "" for r in regions],
    }


# ---------------------------------------------------------------------------
# Request builders — Alleles (select variants, has skip/limit)
# ---------------------------------------------------------------------------


def _build_alleles_in_region_request(
    region: Region,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInRegionRequest:
    return pb2.AllelesInRegionRequest(
        **_region_kwargs(region),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_alleles_in_region_in_samples_request(
    region: Region,
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInRegionInSamplesRequest:
    return pb2.AllelesInRegionInSamplesRequest(
        **_region_kwargs(region),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_alleles_in_bracket_request(
    bracket: Bracket,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInBracketRequest:
    return pb2.AllelesInBracketRequest(
        **_bracket_kwargs(bracket),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_alleles_in_bracket_in_samples_request(
    bracket: Bracket,
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInBracketInSamplesRequest:
    return pb2.AllelesInBracketInSamplesRequest(
        **_bracket_kwargs(bracket),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_alleles_in_multi_regions_request(
    regions: list[Region],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInMultiRegionsRequest:
    return pb2.AllelesInMultiRegionsRequest(
        **_multi_region_kwargs(regions),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_alleles_in_multi_regions_in_samples_request(
    regions: list[Region],
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.AllelesInMultiRegionsInSamplesRequest:
    return pb2.AllelesInMultiRegionsInSamplesRequest(
        **_multi_region_kwargs(regions),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


# ---------------------------------------------------------------------------
# Request builders — Count Alleles (NO skip/limit)
# ---------------------------------------------------------------------------


def _build_count_alleles_in_region_request(
    region: Region,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInRegionRequest:
    return pb2.CountAllelesInRegionRequest(
        **_region_kwargs(region),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


def _build_count_alleles_in_region_in_samples_request(
    region: Region,
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInRegionInSamplesRequest:
    return pb2.CountAllelesInRegionInSamplesRequest(
        **_region_kwargs(region),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


def _build_count_alleles_in_bracket_request(
    bracket: Bracket,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInBracketRequest:
    return pb2.CountAllelesInBracketRequest(
        **_bracket_kwargs(bracket),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


def _build_count_alleles_in_bracket_in_samples_request(
    bracket: Bracket,
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInBracketInSamplesRequest:
    return pb2.CountAllelesInBracketInSamplesRequest(
        **_bracket_kwargs(bracket),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


def _build_count_alleles_in_multi_regions_request(
    regions: list[Region],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInMultiRegionsRequest:
    return pb2.CountAllelesInMultiRegionsRequest(
        **_multi_region_kwargs(regions),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


def _build_count_alleles_in_multi_regions_in_samples_request(
    regions: list[Region],
    samples: list[str],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
) -> pb2.CountAllelesInMultiRegionsInSamplesRequest:
    return pb2.CountAllelesInMultiRegionsInSamplesRequest(
        **_multi_region_kwargs(regions),
        samples=samples,
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
    )


# ---------------------------------------------------------------------------
# Request builders — Samples (has skip/limit)
# ---------------------------------------------------------------------------


def _build_samples_in_region_request(
    region: Region,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.SamplesInRegionRequest:
    return pb2.SamplesInRegionRequest(
        **_region_kwargs(region),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


def _build_samples_in_multi_regions_request(
    regions: list[Region],
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
) -> pb2.SamplesInMultiRegionsRequest:
    return pb2.SamplesInMultiRegionsRequest(
        **_multi_region_kwargs(regions),
        **_common_kwargs(hom, het, annotations, assembly, variant_min_length, variant_max_length),
        **_skip_limit_kwargs(skip, limit),
    )


# ---------------------------------------------------------------------------
# Dispatch functions
# ---------------------------------------------------------------------------


def dispatch_select_variants(
    stub: dnaerys_pb2_grpc.DnaerysServiceStub,
    *,
    region: Region | None,
    regions: list[Region] | None,
    bracket: Bracket | None,
    samples: list[str] | None,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
    timeout: float | None,
) -> Iterator:
    """Route to the correct SelectVariants* streaming RPC.

    Dispatch table:
        bracket + samples -> SelectVariantsInBracketInSamples
        bracket           -> SelectVariantsInBracket
        regions + samples -> SelectVariantsInMultiRegionsInSamples
        regions           -> SelectVariantsInMultiRegions
        region + samples  -> SelectVariantsInRegionInSamples
        region            -> SelectVariantsInRegion
    """
    _validate_exactly_one(region=region, regions=regions, bracket=bracket)
    common = (hom, het, annotations, assembly, variant_min_length, variant_max_length)

    if bracket is not None:
        if samples:
            request = _build_alleles_in_bracket_in_samples_request(
                bracket, samples, *common, skip, limit,
            )
            return stub.SelectVariantsInBracketInSamples(request, timeout=timeout)
        request = _build_alleles_in_bracket_request(bracket, *common, skip, limit)
        return stub.SelectVariantsInBracket(request, timeout=timeout)

    if regions is not None:
        if samples:
            request = _build_alleles_in_multi_regions_in_samples_request(
                regions, samples, *common, skip, limit,
            )
            return stub.SelectVariantsInMultiRegionsInSamples(request, timeout=timeout)
        request = _build_alleles_in_multi_regions_request(regions, *common, skip, limit)
        return stub.SelectVariantsInMultiRegions(request, timeout=timeout)

    # region is not None (guaranteed by _validate_exactly_one)
    if samples:
        request = _build_alleles_in_region_in_samples_request(
            region, samples, *common, skip, limit,  # type: ignore[arg-type]
        )
        return stub.SelectVariantsInRegionInSamples(request, timeout=timeout)
    request = _build_alleles_in_region_request(region, *common, skip, limit)  # type: ignore[arg-type]
    return stub.SelectVariantsInRegion(request, timeout=timeout)


def dispatch_select_variants_with_stats(
    stub: dnaerys_pb2_grpc.DnaerysServiceStub,
    *,
    region: Region | None,
    regions: list[Region] | None,
    samples: list[str] | None,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
    timeout: float | None,
) -> Iterator:
    """Route to the correct SelectVariants*WithStats streaming RPC.

    Dispatch table:
        regions + samples -> SelectVariantsInMultiRegionsInSamplesWithStats
        regions           -> SelectVariantsInMultiRegionsWithStats
        region + samples  -> SelectVariantsInRegionInSamplesWithStats
        region (no samples) -> wraps to [region], SelectVariantsInMultiRegionsWithStats
    """
    _validate_exactly_one(region=region, regions=regions)

    # Normalise single-region without samples to multi-region path.
    if region is not None and not samples:
        regions = [region]
        region = None

    common = (hom, het, annotations, assembly, variant_min_length, variant_max_length)

    if regions is not None:
        if samples:
            request = _build_alleles_in_multi_regions_in_samples_request(
                regions, samples, *common, skip, limit,
            )
            return stub.SelectVariantsInMultiRegionsInSamplesWithStats(
                request, timeout=timeout,
            )
        request = _build_alleles_in_multi_regions_request(regions, *common, skip, limit)
        return stub.SelectVariantsInMultiRegionsWithStats(request, timeout=timeout)

    # region is not None with samples (guaranteed by above normalisation)
    request = _build_alleles_in_region_in_samples_request(
        region, samples, *common, skip, limit,  # type: ignore[arg-type]
    )
    return stub.SelectVariantsInRegionInSamplesWithStats(request, timeout=timeout)


def dispatch_count_variants(
    stub: dnaerys_pb2_grpc.DnaerysServiceStub,
    *,
    region: Region | None,
    regions: list[Region] | None,
    bracket: Bracket | None,
    samples: list[str] | None,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    timeout: float | None,
) -> pb2.CountAllelesResponse:
    """Route to the correct CountVariants* unary RPC.

    Note: count variant requests have no skip/limit parameters.

    Dispatch table:
        bracket + samples -> CountVariantsInBracketInSamples
        bracket           -> CountVariantsInBracket
        regions + samples -> CountVariantsInMultiRegionsInSamples
        regions           -> CountVariantsInMultiRegions
        region + samples  -> CountVariantsInRegionInSamples
        region            -> CountVariantsInRegion
    """
    _validate_exactly_one(region=region, regions=regions, bracket=bracket)
    common = (hom, het, annotations, assembly, variant_min_length, variant_max_length)

    if bracket is not None:
        if samples:
            request = _build_count_alleles_in_bracket_in_samples_request(
                bracket, samples, *common,
            )
            return stub.CountVariantsInBracketInSamples(request, timeout=timeout)
        request = _build_count_alleles_in_bracket_request(bracket, *common)
        return stub.CountVariantsInBracket(request, timeout=timeout)

    if regions is not None:
        if samples:
            request = _build_count_alleles_in_multi_regions_in_samples_request(
                regions, samples, *common,
            )
            return stub.CountVariantsInMultiRegionsInSamples(request, timeout=timeout)
        request = _build_count_alleles_in_multi_regions_request(regions, *common)
        return stub.CountVariantsInMultiRegions(request, timeout=timeout)

    # region is not None
    if samples:
        request = _build_count_alleles_in_region_in_samples_request(
            region, samples, *common,  # type: ignore[arg-type]
        )
        return stub.CountVariantsInRegionInSamples(request, timeout=timeout)
    request = _build_count_alleles_in_region_request(region, *common)  # type: ignore[arg-type]
    return stub.CountVariantsInRegion(request, timeout=timeout)


def dispatch_select_samples(
    stub: dnaerys_pb2_grpc.DnaerysServiceStub,
    *,
    region: Region | None,
    regions: list[Region] | None,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    skip: int | None,
    limit: int | None,
    timeout: float | None,
) -> pb2.SamplesResponse:
    """Route to the correct SelectSamples* unary RPC.

    Dispatch table:
        regions -> SelectSamplesInMultiRegions
        region  -> SelectSamplesInRegion
    """
    _validate_exactly_one(region=region, regions=regions)
    common = (hom, het, annotations, assembly, variant_min_length, variant_max_length)

    if regions is not None:
        request = _build_samples_in_multi_regions_request(regions, *common, skip, limit)
        return stub.SelectSamplesInMultiRegions(request, timeout=timeout)

    request = _build_samples_in_region_request(region, *common, skip, limit)  # type: ignore[arg-type]
    return stub.SelectSamplesInRegion(request, timeout=timeout)


def dispatch_count_samples(
    stub: dnaerys_pb2_grpc.DnaerysServiceStub,
    *,
    region: Region | None,
    regions: list[Region] | None,
    hom: bool,
    het: bool,
    annotations: AnnotationFilter | None,
    assembly: RefAssembly,
    variant_min_length: int | None,
    variant_max_length: int | None,
    timeout: float | None,
) -> pb2.CountSamplesResponse:
    """Route to the correct CountSamples* unary RPC.

    Dispatch table:
        regions -> CountSamplesInMultiRegions
        region  -> CountSamplesInRegion
    """
    _validate_exactly_one(region=region, regions=regions)
    common = (hom, het, annotations, assembly, variant_min_length, variant_max_length)

    if regions is not None:
        request = _build_samples_in_multi_regions_request(regions, *common, None, None)
        return stub.CountSamplesInMultiRegions(request, timeout=timeout)

    request = _build_samples_in_region_request(region, *common, None, None)  # type: ignore[arg-type]
    return stub.CountSamplesInRegion(request, timeout=timeout)
