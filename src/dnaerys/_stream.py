"""Stream wrapper classes for Dnaerys gRPC streaming responses.

``VariantStream`` and ``VariantWithStatsStream`` wrap gRPC server-streaming
iterators, flattening chunked proto responses into individual Python
dataclass objects.  They accumulate per-chunk metadata (timing, cluster
health) and expose it via a ``.metadata`` property.

Both classes are iterable and support:

- ``for variant in stream:`` — yields one variant at a time
- ``stream.to_list()`` — terminal; exhausts the stream and returns a list
- ``stream.to_dataframe()`` — terminal; exhausts the stream and returns
  a pandas DataFrame (requires ``pandas``)
"""

from __future__ import annotations

import warnings
from collections.abc import Iterable, Iterator

import grpc

from dnaerys._convert import convert_variant, convert_variant_with_stats
from dnaerys._enums import Chromosome
from dnaerys._exceptions import (
    DnaerysIncompleteResultWarning,
    raise_for_grpc_error,
)
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._types import ResponseMetadata, Variant, VariantWithStats


class VariantStream:
    """Synchronous iterator wrapper yielding ``Variant`` objects from a gRPC stream.

    Wraps an ``Iterable[pb2.AllelesResponse]`` and yields individual
    ``Variant`` dataclass instances.  The underlying gRPC stream delivers
    variants in chunks (``AllelesResponse`` messages with ``repeated Variant``);
    this class flattens them into a single-item-at-a-time iterator.

    Metadata (timing, cluster health) is accumulated across all consumed
    chunks and available via the ``.metadata`` property at any time.

    Warning
    -------
    ``to_list()`` and ``to_dataframe()`` are terminal operations.  After
    either is called, the internal iterator is exhausted.  Materialising
    genome-wide results may require substantial memory.  Consider iterating
    with the generator for large result sets.
    """

    def __init__(
        self,
        proto_iterator: Iterable[pb2.AllelesResponse],
        *,
        limit: int | None = None,
    ) -> None:
        """Initialise a ``VariantStream`` from a gRPC streaming iterator.

        Parameters
        ----------
        proto_iterator : Iterable[pb2.AllelesResponse]
            The raw gRPC streaming iterator.
        limit : int or None
            Maximum number of variants to yield.  ``None`` means no cap.
        """
        self._proto_iter = iter(proto_iterator)
        self._current_variants: list[Variant] = []
        self._current_idx = 0
        self._exhausted = False
        self._warned = False
        self._limit = limit
        self._emitted = 0

        # Metadata accumulators
        self._incomplete_cluster = False
        self._affected = False
        self._elapsed_ms = 0
        self._elapsed_db_ms = 0
        self._node_ids: set[str] = set()

    @property
    def metadata(self) -> ResponseMetadata:
        """Accumulated metadata from all consumed chunks.

        Before any chunks have been consumed, returns defaults
        (``elapsed_ms=0``, ``incomplete_cluster=False``, etc.).
        The ``node_id`` field is a comma-separated sorted string of
        all node IDs seen; empty string if no chunks consumed.
        """
        return ResponseMetadata(
            elapsed_ms=self._elapsed_ms,
            elapsed_db_ms=self._elapsed_db_ms,
            node_id=",".join(sorted(self._node_ids)) if self._node_ids else "",
            incomplete_cluster=self._incomplete_cluster,
            affected=self._affected,
        )

    def _accumulate_metadata(self, chunk: pb2.AllelesResponse) -> None:
        """Accumulate metadata from a single chunk.

        Rules:
        - incomplete_cluster: OR across all chunks (once True, stays True)
        - affected: OR across all chunks (once True, stays True)
        - elapsed_ms: max() across all chunks
        - elapsed_db_ms: max() across all chunks
        - node_ids: set union across all chunks
        """
        self._incomplete_cluster = self._incomplete_cluster or chunk.incomplete_cluster
        self._affected = self._affected or chunk.affected
        self._elapsed_ms = max(self._elapsed_ms, int(chunk.elapsed_ms))
        self._elapsed_db_ms = max(self._elapsed_db_ms, int(chunk.elapsed_db_ms))
        if chunk.node_id:
            self._node_ids.add(chunk.node_id)

        # Emit warning exactly once per stream on the first chunk with affected=True
        if chunk.affected and not self._warned:
            warnings.warn(
                "Results may be incomplete: cluster nodes holding "
                "potentially relevant data were unreachable.",
                DnaerysIncompleteResultWarning,
                stacklevel=3,
            )
            self._warned = True

    def __iter__(self) -> Iterator[Variant]:
        """Return the iterator (self)."""
        return self

    def __next__(self) -> Variant:
        """Return the next ``Variant`` from the stream.

        Raises ``StopIteration`` when the stream is exhausted or the
        limit is reached.  gRPC errors during iteration are caught and
        re-raised as the appropriate ``DnaerysError`` subclass.
        """
        if self._limit is not None and self._emitted >= self._limit:
            raise StopIteration

        # Serve from the current chunk buffer first
        while self._current_idx >= len(self._current_variants):
            if self._exhausted:
                raise StopIteration
            # Fetch the next chunk
            try:
                chunk = next(self._proto_iter)
            except StopIteration:
                self._exhausted = True
                raise
            except grpc.RpcError as e:
                self._exhausted = True
                raise_for_grpc_error(e)

            self._accumulate_metadata(chunk)
            self._current_variants = [
                convert_variant(v) for v in chunk.variants
            ]
            self._current_idx = 0

        variant = self._current_variants[self._current_idx]
        self._current_idx += 1
        self._emitted += 1
        return variant

    def to_list(self) -> list[Variant]:
        """Exhaust the stream and return all remaining variants as a list.

        This is a terminal operation.  After calling ``to_list()``, further
        iteration yields nothing.

        Materialising genome-wide results may require substantial memory.
        Consider iterating with the generator for large result sets.
        """
        return list(self)

    def to_dataframe(self) -> "object":
        """Exhaust the stream and return a pandas ``DataFrame``.

        This is a terminal operation.  Requires ``pandas`` to be installed.

        Returns
        -------
        pandas.DataFrame
            DataFrame with 21 columns matching the ``Variant`` fields.
            The ``chr`` column contains human-readable strings
            (``"chr1"``, ``"chrX"``, ``"chrMT"``), not enum int values.

        Raises
        ------
        ImportError
            If ``pandas`` is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install dnaerys[pandas]"
            )

        variants = self.to_list()
        if not variants:
            return _make_empty_variant_dataframe(pd)

        data = {
            "chr": [_chr_display(v.chr) for v in variants],
            "start": [v.start for v in variants],
            "end": [v.end for v in variants],
            "ref": [v.ref for v in variants],
            "alt": [v.alt for v in variants],
            "af": [v.af for v in variants],
            "ac": [v.ac for v in variants],
            "an": [v.an for v in variants],
            "homc": [v.homc for v in variants],
            "hetc": [v.hetc for v in variants],
            "misc": [v.misc for v in variants],
            "homfc": [v.homfc for v in variants],
            "hetfc": [v.hetfc for v in variants],
            "misfc": [v.misfc for v in variants],
            "gnomad_exomes_af": [v.gnomad_exomes_af for v in variants],
            "gnomad_genomes_af": [v.gnomad_genomes_af for v in variants],
            "cadd_raw": [v.cadd_raw for v in variants],
            "cadd_phred": [v.cadd_phred for v in variants],
            "am_score": [v.am_score for v in variants],
            "amino_acids": [v.amino_acids for v in variants],
            "biallelic": [v.biallelic for v in variants],
        }
        df = pd.DataFrame(data)
        return _apply_variant_dtypes(df, pd)


class VariantWithStatsStream:
    """Synchronous iterator wrapper yielding ``VariantWithStats`` from a gRPC stream.

    Same semantics as ``VariantStream`` but wraps
    ``Iterable[pb2.AllelesWithStatsResponse]`` and yields
    ``VariantWithStats`` dataclass instances with 32 fields (21 variant +
    11 statistics).

    Metadata accumulation, warning emission, and terminal operation rules
    are identical to ``VariantStream``.
    """

    def __init__(
        self,
        proto_iterator: Iterable[pb2.AllelesWithStatsResponse],
        *,
        limit: int | None = None,
    ) -> None:
        """Initialise a ``VariantWithStatsStream`` from a gRPC streaming iterator.

        Parameters
        ----------
        proto_iterator : Iterable[pb2.AllelesWithStatsResponse]
            The raw gRPC streaming iterator.
        limit : int or None
            Maximum number of variants to yield.  ``None`` means no cap.
        """
        self._proto_iter = iter(proto_iterator)
        self._current_variants: list[VariantWithStats] = []
        self._current_idx = 0
        self._exhausted = False
        self._warned = False
        self._limit = limit
        self._emitted = 0

        # Metadata accumulators
        self._incomplete_cluster = False
        self._affected = False
        self._elapsed_ms = 0
        self._elapsed_db_ms = 0
        self._node_ids: set[str] = set()

    @property
    def metadata(self) -> ResponseMetadata:
        """Accumulated metadata from all consumed chunks.

        Same accumulation rules as ``VariantStream.metadata``.
        """
        return ResponseMetadata(
            elapsed_ms=self._elapsed_ms,
            elapsed_db_ms=self._elapsed_db_ms,
            node_id=",".join(sorted(self._node_ids)) if self._node_ids else "",
            incomplete_cluster=self._incomplete_cluster,
            affected=self._affected,
        )

    def _accumulate_metadata(self, chunk: pb2.AllelesWithStatsResponse) -> None:
        """Accumulate metadata from a single chunk."""
        self._incomplete_cluster = self._incomplete_cluster or chunk.incomplete_cluster
        self._affected = self._affected or chunk.affected
        self._elapsed_ms = max(self._elapsed_ms, int(chunk.elapsed_ms))
        self._elapsed_db_ms = max(self._elapsed_db_ms, int(chunk.elapsed_db_ms))
        if chunk.node_id:
            self._node_ids.add(chunk.node_id)

        if chunk.affected and not self._warned:
            warnings.warn(
                "Results may be incomplete: cluster nodes holding "
                "potentially relevant data were unreachable.",
                DnaerysIncompleteResultWarning,
                stacklevel=3,
            )
            self._warned = True

    def __iter__(self) -> Iterator[VariantWithStats]:
        """Return the iterator (self)."""
        return self

    def __next__(self) -> VariantWithStats:
        """Return the next ``VariantWithStats`` from the stream.

        Raises ``StopIteration`` when exhausted or the limit is reached.
        gRPC errors are converted to ``DnaerysError`` subclasses.
        """
        if self._limit is not None and self._emitted >= self._limit:
            raise StopIteration

        while self._current_idx >= len(self._current_variants):
            if self._exhausted:
                raise StopIteration
            try:
                chunk = next(self._proto_iter)
            except StopIteration:
                self._exhausted = True
                raise
            except grpc.RpcError as e:
                self._exhausted = True
                raise_for_grpc_error(e)

            self._accumulate_metadata(chunk)
            self._current_variants = [
                convert_variant_with_stats(v) for v in chunk.variants
            ]
            self._current_idx = 0

        variant = self._current_variants[self._current_idx]
        self._current_idx += 1
        self._emitted += 1
        return variant

    def to_list(self) -> list[VariantWithStats]:
        """Exhaust the stream and return all remaining variants as a list.

        This is a terminal operation.

        Materialising genome-wide results may require substantial memory.
        Consider iterating with the generator for large result sets.
        """
        return list(self)

    def to_dataframe(self) -> "object":
        """Exhaust the stream and return a pandas ``DataFrame``.

        This is a terminal operation.  Requires ``pandas`` to be installed.

        Returns
        -------
        pandas.DataFrame
            DataFrame with 32 columns matching the ``VariantWithStats`` fields.
            The ``chr`` column contains human-readable strings.

        Raises
        ------
        ImportError
            If ``pandas`` is not installed.
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for to_dataframe(). "
                "Install it with: pip install dnaerys[pandas]"
            )

        variants = self.to_list()
        if not variants:
            return _make_empty_variant_with_stats_dataframe(pd)

        data = {
            "chr": [_chr_display(v.chr) for v in variants],
            "start": [v.start for v in variants],
            "end": [v.end for v in variants],
            "ref": [v.ref for v in variants],
            "alt": [v.alt for v in variants],
            "af": [v.af for v in variants],
            "ac": [v.ac for v in variants],
            "an": [v.an for v in variants],
            "homc": [v.homc for v in variants],
            "hetc": [v.hetc for v in variants],
            "misc": [v.misc for v in variants],
            "homfc": [v.homfc for v in variants],
            "hetfc": [v.hetfc for v in variants],
            "misfc": [v.misfc for v in variants],
            "gnomad_exomes_af": [v.gnomad_exomes_af for v in variants],
            "gnomad_genomes_af": [v.gnomad_genomes_af for v in variants],
            "cadd_raw": [v.cadd_raw for v in variants],
            "cadd_phred": [v.cadd_phred for v in variants],
            "am_score": [v.am_score for v in variants],
            "amino_acids": [v.amino_acids for v in variants],
            "biallelic": [v.biallelic for v in variants],
            "vaf": [v.vaf for v in variants],
            "vac": [v.vac for v in variants],
            "van": [v.van for v in variants],
            "vhomc": [v.vhomc for v in variants],
            "vhetc": [v.vhetc for v in variants],
            "vhomfc": [v.vhomfc for v in variants],
            "vhetfc": [v.vhetfc for v in variants],
            "phwe": [v.phwe for v in variants],
            "pchi2": [v.pchi2 for v in variants],
            "odds_ratio": [v.odds_ratio for v in variants],
            "ibc": [v.ibc for v in variants],
        }
        df = pd.DataFrame(data)
        return _apply_variant_with_stats_dtypes(df, pd)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

# Chromosome enum → human-readable string display mapping
_CHR_DISPLAY: dict[Chromosome, str] = {
    Chromosome.CHR_MT: "chrMT",
    Chromosome.CHR_X: "chrX",
    Chromosome.CHR_Y: "chrY",
}
for _i in range(1, 23):
    _CHR_DISPLAY[Chromosome(_i)] = f"chr{_i}"


def _chr_display(c: Chromosome) -> str:
    """Return the human-readable string for a Chromosome enum value."""
    return _CHR_DISPLAY[c]


def _apply_variant_dtypes(df: object, pd: object) -> object:
    """Apply the specified dtypes to a Variant DataFrame (21 columns)."""
    return df.astype({
        "chr": "object",
        "start": "int32",
        "end": "int32",
        "ref": "object",
        "alt": "object",
        "af": "float32",
        "ac": "float32",
        "an": "int32",
        "homc": "int32",
        "hetc": "int32",
        "misc": "int32",
        "homfc": "int32",
        "hetfc": "int32",
        "misfc": "int32",
        "gnomad_exomes_af": "float32",
        "gnomad_genomes_af": "float32",
        "cadd_raw": "float32",
        "cadd_phred": "float32",
        "am_score": "float32",
        "amino_acids": "object",
        "biallelic": "bool",
    })


def _apply_variant_with_stats_dtypes(df: object, pd: object) -> object:
    """Apply the specified dtypes to a VariantWithStats DataFrame (32 columns)."""
    return df.astype({
        "chr": "object",
        "start": "int32",
        "end": "int32",
        "ref": "object",
        "alt": "object",
        "af": "float32",
        "ac": "float32",
        "an": "int32",
        "homc": "int32",
        "hetc": "int32",
        "misc": "int32",
        "homfc": "int32",
        "hetfc": "int32",
        "misfc": "int32",
        "gnomad_exomes_af": "float32",
        "gnomad_genomes_af": "float32",
        "cadd_raw": "float32",
        "cadd_phred": "float32",
        "am_score": "float32",
        "amino_acids": "object",
        "biallelic": "bool",
        "vaf": "float32",
        "vac": "float32",
        "van": "int32",
        "vhomc": "int32",
        "vhetc": "int32",
        "vhomfc": "int32",
        "vhetfc": "int32",
        "phwe": "float32",
        "pchi2": "float32",
        "odds_ratio": "float32",
        "ibc": "float32",
    })


def _make_empty_variant_dataframe(pd: object) -> object:
    """Create an empty DataFrame with correct Variant column dtypes."""
    df = pd.DataFrame(columns=[
        "chr", "start", "end", "ref", "alt", "af", "ac", "an",
        "homc", "hetc", "misc", "homfc", "hetfc", "misfc",
        "gnomad_exomes_af", "gnomad_genomes_af", "cadd_raw", "cadd_phred",
        "am_score", "amino_acids", "biallelic",
    ])
    return _apply_variant_dtypes(df, pd)


def _make_empty_variant_with_stats_dataframe(pd: object) -> object:
    """Create an empty DataFrame with correct VariantWithStats column dtypes."""
    df = pd.DataFrame(columns=[
        "chr", "start", "end", "ref", "alt", "af", "ac", "an",
        "homc", "hetc", "misc", "homfc", "hetfc", "misfc",
        "gnomad_exomes_af", "gnomad_genomes_af", "cadd_raw", "cadd_phred",
        "am_score", "amino_acids", "biallelic",
        "vaf", "vac", "van", "vhomc", "vhetc", "vhomfc", "vhetfc",
        "phwe", "pchi2", "odds_ratio", "ibc",
    ])
    return _apply_variant_with_stats_dtypes(df, pd)
