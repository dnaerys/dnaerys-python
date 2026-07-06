"""Tests for VariantStream and VariantWithStatsStream wrappers.

Factories build complete proto messages with sensible non-zero defaults so
that field-value assertions in tests are meaningful.
"""

from __future__ import annotations

import warnings
from unittest import mock

import pytest

from dnaerys._enums import Chromosome
from dnaerys._exceptions import DnaerysIncompleteResultWarning
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._stream import VariantStream, VariantWithStatsStream
from dnaerys._types import ResponseMetadata, Variant, VariantWithStats


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def make_variant_proto(**overrides) -> pb2.Variant:
    """Build a ``pb2.Variant`` with sensible non-zero defaults.

    All defaults produce a biallelic chr1 SNV at position 100 with non-zero
    counts and annotations so that tests can assert on specific values.
    """
    defaults = {
        "chr": 1,
        "start": 100,
        "end": 100,
        "ref": "A",
        "alt": "T",
        "af": 0.5,
        "ac": 1.0,
        "an": 2,
        "hom_samples": 0,
        "het_samples": 1,
        "mis_samples": 0,
        "hom_samples_fx": 0,
        "het_samples_fx": 0,
        "mis_samples_fx": 0,
        "gnomADe": 0.1,
        "gnomADg": 0.2,
        "cadd_raw": 3.5,
        "cadd_phred": 15.0,
        "am_score": 0.8,
        "amino_acids": "A/V",
        "biallelic": True,
    }
    defaults.update(overrides)
    return pb2.Variant(**defaults)


def make_alleles_response(n_variants: int = 2, **meta_overrides) -> pb2.AllelesResponse:
    """Build an ``AllelesResponse`` chunk with *n_variants* variants.

    Each variant differs by start position (100, 101, 102, ...) so they
    are distinguishable in tests.  Metadata fields have non-zero defaults.
    """
    meta_defaults = {
        "incomplete_cluster": False,
        "affected": False,
        "elapsed_ms": 100,
        "elapsed_db_ms": 50,
        "node_id": "node-1",
    }
    meta_defaults.update(meta_overrides)
    variants = [make_variant_proto(start=100 + i) for i in range(n_variants)]
    return pb2.AllelesResponse(variants=variants, **meta_defaults)


def make_variant_with_stats_proto(**overrides) -> pb2.VariantWithStats:
    """Build a ``pb2.VariantWithStats`` with sensible non-zero defaults.

    The nested ``variant`` sub-message uses ``make_variant_proto`` defaults.
    Stats fields have non-zero values by default.
    """
    variant_overrides = {}
    stats_defaults = {
        "vaf": 0.4,
        "vac": 1.5,
        "van": 4,
        "v_hom_samples": 0,
        "v_het_samples": 1,
        "v_hom_samples_fx": 0,
        "v_het_samples_fx": 0,
        "phwe": 0.05,
        "pchi2": 0.01,
        "ibc": 0.02,
    }
    or_val = overrides.pop("or_val", 1.5)

    # Allow overriding nested variant fields via 'variant_*' keys
    for k in list(overrides):
        if k.startswith("variant_"):
            variant_overrides[k[8:]] = overrides.pop(k)

    stats_defaults.update(overrides)
    return pb2.VariantWithStats(
        variant=make_variant_proto(**variant_overrides),
        **stats_defaults,
        **{"or": or_val},
    )


def make_alleles_with_stats_response(
    n_variants: int = 2, **meta_overrides
) -> pb2.AllelesWithStatsResponse:
    """Build an ``AllelesWithStatsResponse`` chunk with *n_variants* variants."""
    meta_defaults = {
        "incomplete_cluster": False,
        "affected": False,
        "elapsed_ms": 100,
        "elapsed_db_ms": 50,
        "node_id": "node-1",
    }
    meta_defaults.update(meta_overrides)
    variants = [
        make_variant_with_stats_proto(variant_start=100 + i)
        for i in range(n_variants)
    ]
    return pb2.AllelesWithStatsResponse(variants=variants, **meta_defaults)


# ---------------------------------------------------------------------------
# VariantStream tests
# ---------------------------------------------------------------------------


class TestVariantStream:
    def test_variant_stream_single_chunk(self):
        chunk = make_alleles_response(n_variants=3)
        stream = VariantStream(iter([chunk]))
        variants = list(stream)
        assert len(variants) == 3
        assert all(isinstance(v, Variant) for v in variants)

    def test_variant_stream_multiple_chunks(self):
        chunk1 = make_alleles_response(n_variants=2, elapsed_ms=100, node_id="n1")
        chunk2 = make_alleles_response(n_variants=1, elapsed_ms=200, node_id="n2")
        stream = VariantStream(iter([chunk1, chunk2]))
        variants = list(stream)
        assert len(variants) == 3

    def test_variant_stream_empty_iterator(self):
        stream = VariantStream(iter([]))
        variants = list(stream)
        assert variants == []

    def test_variant_stream_metadata_single_chunk(self):
        chunk = make_alleles_response(
            n_variants=1,
            incomplete_cluster=True,
            affected=True,
            elapsed_ms=150,
            elapsed_db_ms=80,
            node_id="node-A",
        )
        stream = VariantStream(iter([chunk]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DnaerysIncompleteResultWarning)
            list(stream)  # exhaust
        m = stream.metadata
        assert m.elapsed_ms == 150
        assert m.elapsed_db_ms == 80
        assert m.node_id == "node-A"
        assert m.incomplete_cluster is True
        assert m.affected is True

    def test_variant_stream_metadata_accumulation_elapsed_ms(self):
        c1 = make_alleles_response(n_variants=1, elapsed_ms=100)
        c2 = make_alleles_response(n_variants=1, elapsed_ms=200)
        stream = VariantStream(iter([c1, c2]))
        list(stream)
        assert stream.metadata.elapsed_ms == 200

    def test_variant_stream_metadata_accumulation_elapsed_db_ms(self):
        c1 = make_alleles_response(n_variants=1, elapsed_db_ms=30)
        c2 = make_alleles_response(n_variants=1, elapsed_db_ms=70)
        stream = VariantStream(iter([c1, c2]))
        list(stream)
        assert stream.metadata.elapsed_db_ms == 70

    def test_variant_stream_metadata_accumulation_incomplete_cluster(self):
        c1 = make_alleles_response(n_variants=1, incomplete_cluster=False)
        c2 = make_alleles_response(n_variants=1, incomplete_cluster=True)
        stream = VariantStream(iter([c1, c2]))
        list(stream)
        assert stream.metadata.incomplete_cluster is True

    def test_variant_stream_metadata_accumulation_affected(self):
        c1 = make_alleles_response(n_variants=1, affected=False)
        c2 = make_alleles_response(n_variants=1, affected=True)
        stream = VariantStream(iter([c1, c2]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DnaerysIncompleteResultWarning)
            list(stream)
        assert stream.metadata.affected is True

    def test_variant_stream_metadata_accumulation_node_ids(self):
        c1 = make_alleles_response(n_variants=1, node_id="node2")
        c2 = make_alleles_response(n_variants=1, node_id="node1")
        stream = VariantStream(iter([c1, c2]))
        list(stream)
        # sorted comma-joined
        assert stream.metadata.node_id == "node1,node2"

    def test_variant_stream_metadata_before_consumption(self):
        chunk = make_alleles_response(n_variants=2)
        stream = VariantStream(iter([chunk]))
        m = stream.metadata
        assert m.elapsed_ms == 0
        assert m.elapsed_db_ms == 0
        assert m.node_id == ""
        assert m.incomplete_cluster is False
        assert m.affected is False

    def test_variant_stream_incomplete_warning_emitted(self):
        chunk = make_alleles_response(n_variants=1, affected=True)
        stream = VariantStream(iter([chunk]))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(stream)
        dnaerys_warnings = [x for x in w if issubclass(x.category, DnaerysIncompleteResultWarning)]
        assert len(dnaerys_warnings) == 1

    def test_variant_stream_incomplete_warning_emitted_once(self):
        c1 = make_alleles_response(n_variants=1, affected=True)
        c2 = make_alleles_response(n_variants=1, affected=True)
        c3 = make_alleles_response(n_variants=1, affected=True)
        stream = VariantStream(iter([c1, c2, c3]))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(stream)
        dnaerys_warnings = [x for x in w if issubclass(x.category, DnaerysIncompleteResultWarning)]
        assert len(dnaerys_warnings) == 1

    def test_variant_stream_no_warning_when_not_affected(self):
        chunk = make_alleles_response(n_variants=1, affected=False)
        stream = VariantStream(iter([chunk]))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(stream)
        dnaerys_warnings = [x for x in w if issubclass(x.category, DnaerysIncompleteResultWarning)]
        assert len(dnaerys_warnings) == 0

    def test_variant_stream_incomplete_no_affected_no_warning(self):
        chunk = make_alleles_response(
            n_variants=1, incomplete_cluster=True, affected=False,
        )
        stream = VariantStream(iter([chunk]))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(stream)
        dnaerys_warnings = [x for x in w if issubclass(x.category, DnaerysIncompleteResultWarning)]
        assert len(dnaerys_warnings) == 0

    def test_variant_stream_to_list(self):
        chunk = make_alleles_response(n_variants=3)
        stream = VariantStream(iter([chunk]))
        result = stream.to_list()
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(v, Variant) for v in result)

    def test_variant_stream_to_list_exhausts_generator(self):
        chunk = make_alleles_response(n_variants=3)
        stream = VariantStream(iter([chunk]))
        stream.to_list()
        # Subsequent iteration yields nothing
        assert list(stream) == []

    def test_variant_stream_to_dataframe(self):
        pd = pytest.importorskip("pandas")
        chunk = make_alleles_response(n_variants=2)
        stream = VariantStream(iter([chunk]))
        df = stream.to_dataframe()
        assert len(df) == 2
        assert list(df.columns) == [
            "chr", "start", "end", "ref", "alt", "af", "ac", "an",
            "hom_samples", "het_samples", "mis_samples",
            "hom_samples_fx", "het_samples_fx", "mis_samples_fx",
            "hom_samples_mxy", "het_samples_mxy", "mis_samples_mxy",
            "gnomad_exomes_af", "gnomad_genomes_af",
            "cadd_raw", "cadd_phred", "am_score", "amino_acids", "biallelic",
        ]
        assert len(df.columns) == 24
        # Verify dtypes
        assert df["chr"].dtype == object
        assert df["start"].dtype.name == "int32"
        assert df["af"].dtype.name == "float32"
        assert df["biallelic"].dtype == bool

    def test_variant_stream_to_dataframe_no_pandas(self):
        chunk = make_alleles_response(n_variants=1)
        stream = VariantStream(iter([chunk]))
        with mock.patch.dict("sys.modules", {"pandas": None}):
            with pytest.raises(ImportError) as exc_info:
                stream.to_dataframe()
            assert str(exc_info.value) == (
                "pandas is required for to_dataframe(). "
                "Install it with: pip install dnaerys[pandas]"
            )

    def test_variant_stream_partial_consumption_metadata(self):
        # 3 chunks of 2 variants each = 6 variants total
        c1 = make_alleles_response(n_variants=2, elapsed_ms=100, node_id="n1")
        c2 = make_alleles_response(n_variants=2, elapsed_ms=200, node_id="n2")
        c3 = make_alleles_response(n_variants=1, elapsed_ms=300, node_id="n3")
        stream = VariantStream(iter([c1, c2, c3]))
        # Consume only 2 variants (all from chunk 1)
        count = 0
        for _ in stream:
            count += 1
            if count == 2:
                break
        # Only chunk 1 was consumed
        m = stream.metadata
        assert m.elapsed_ms == 100
        assert m.node_id == "n1"

    def test_variant_stream_to_dataframe_chr_as_string(self):
        pd = pytest.importorskip("pandas")
        v1 = make_variant_proto(chr=1)   # CHR1
        v2 = make_variant_proto(chr=23)  # CHRX
        v3 = make_variant_proto(chr=25)  # CHRMT
        chunk = pb2.AllelesResponse(
            variants=[v1, v2, v3],
            elapsed_ms=10, elapsed_db_ms=5, node_id="n1",
        )
        stream = VariantStream(iter([chunk]))
        df = stream.to_dataframe()
        chr_values = list(df["chr"])
        assert chr_values == ["chr1", "chrX", "chrMT"]


# ---------------------------------------------------------------------------
# VariantWithStatsStream tests
# ---------------------------------------------------------------------------


class TestVariantWithStatsStream:
    def test_variant_with_stats_stream_yields_correct_type(self):
        chunk = make_alleles_with_stats_response(n_variants=2)
        stream = VariantWithStatsStream(iter([chunk]))
        for v in stream:
            assert isinstance(v, VariantWithStats)

    def test_variant_with_stats_stream_multiple_chunks(self):
        c1 = make_alleles_with_stats_response(n_variants=2)
        c2 = make_alleles_with_stats_response(n_variants=1)
        stream = VariantWithStatsStream(iter([c1, c2]))
        variants = list(stream)
        assert len(variants) == 3

    def test_variant_with_stats_stream_metadata_accumulation(self):
        c1 = make_alleles_with_stats_response(
            n_variants=1, elapsed_ms=100, elapsed_db_ms=50,
            node_id="n1", incomplete_cluster=False, affected=False,
        )
        c2 = make_alleles_with_stats_response(
            n_variants=1, elapsed_ms=300, elapsed_db_ms=200,
            node_id="n2", incomplete_cluster=True, affected=True,
        )
        stream = VariantWithStatsStream(iter([c1, c2]))
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DnaerysIncompleteResultWarning)
            list(stream)
        m = stream.metadata
        assert m.elapsed_ms == 300
        assert m.elapsed_db_ms == 200
        assert m.incomplete_cluster is True
        assert m.affected is True
        assert m.node_id == "n1,n2"

    def test_variant_with_stats_stream_warning(self):
        chunk = make_alleles_with_stats_response(n_variants=1, affected=True)
        stream = VariantWithStatsStream(iter([chunk]))
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            list(stream)
        dnaerys_warnings = [x for x in w if issubclass(x.category, DnaerysIncompleteResultWarning)]
        assert len(dnaerys_warnings) == 1

    def test_variant_with_stats_stream_to_list(self):
        chunk = make_alleles_with_stats_response(n_variants=3)
        stream = VariantWithStatsStream(iter([chunk]))
        result = stream.to_list()
        assert isinstance(result, list)
        assert len(result) == 3
        assert all(isinstance(v, VariantWithStats) for v in result)

    def test_variant_with_stats_stream_to_dataframe(self):
        pd = pytest.importorskip("pandas")
        chunk = make_alleles_with_stats_response(n_variants=2)
        stream = VariantWithStatsStream(iter([chunk]))
        df = stream.to_dataframe()
        assert len(df) == 2
        expected_cols = [
            "chr", "start", "end", "ref", "alt", "af", "ac", "an",
            "hom_samples", "het_samples", "mis_samples",
            "hom_samples_fx", "het_samples_fx", "mis_samples_fx",
            "hom_samples_mxy", "het_samples_mxy", "mis_samples_mxy",
            "gnomad_exomes_af", "gnomad_genomes_af",
            "cadd_raw", "cadd_phred", "am_score", "amino_acids", "biallelic",
            "vaf", "vac", "van",
            "v_hom_samples", "v_het_samples",
            "v_hom_samples_fx", "v_het_samples_fx",
            "v_hom_samples_mxy", "v_het_samples_mxy",
            "phwe", "pchi2", "odds_ratio", "ibc",
        ]
        assert list(df.columns) == expected_cols
        assert len(df.columns) == 37
        # Verify dtypes for stats columns
        assert df["vaf"].dtype.name == "float32"
        assert df["van"].dtype.name == "int32"
        assert df["odds_ratio"].dtype.name == "float32"
        assert df["ibc"].dtype.name == "float32"


# ---------------------------------------------------------------------------
# VariantStream limit tests
# ---------------------------------------------------------------------------


class TestVariantStreamLimit:
    def test_limit_caps_variants(self):
        chunk = make_alleles_response(n_variants=10)
        stream = VariantStream(iter([chunk]), limit=5)
        assert len(list(stream)) == 5

    def test_limit_none_yields_all(self):
        chunk = make_alleles_response(n_variants=10)
        stream = VariantStream(iter([chunk]), limit=None)
        assert len(list(stream)) == 10

    def test_limit_zero_yields_nothing(self):
        chunk = make_alleles_response(n_variants=5)
        stream = VariantStream(iter([chunk]), limit=0)
        assert list(stream) == []

    def test_limit_mid_chunk(self):
        c1 = make_alleles_response(n_variants=4)
        c2 = make_alleles_response(n_variants=4)
        stream = VariantStream(iter([c1, c2]), limit=5)
        assert len(list(stream)) == 5

    def test_limit_larger_than_available(self):
        chunk = make_alleles_response(n_variants=3)
        stream = VariantStream(iter([chunk]), limit=100)
        assert len(list(stream)) == 3

    def test_to_list_respects_limit(self):
        chunk = make_alleles_response(n_variants=10)
        stream = VariantStream(iter([chunk]), limit=3)
        assert len(stream.to_list()) == 3

    def test_to_dataframe_respects_limit(self):
        pd = pytest.importorskip("pandas")
        chunk = make_alleles_response(n_variants=10)
        stream = VariantStream(iter([chunk]), limit=4)
        df = stream.to_dataframe()
        assert len(df) == 4

    def test_limit_metadata_reflects_consumed_chunks(self):
        c1 = make_alleles_response(n_variants=3, elapsed_ms=100, node_id="n1")
        c2 = make_alleles_response(n_variants=3, elapsed_ms=200, node_id="n2")
        stream = VariantStream(iter([c1, c2]), limit=2)
        list(stream)
        # Only chunk 1 should have been consumed
        assert stream.metadata.elapsed_ms == 100
        assert stream.metadata.node_id == "n1"


# ---------------------------------------------------------------------------
# VariantWithStatsStream limit tests
# ---------------------------------------------------------------------------


class TestVariantWithStatsStreamLimit:
    def test_limit_caps_variants(self):
        chunk = make_alleles_with_stats_response(n_variants=10)
        stream = VariantWithStatsStream(iter([chunk]), limit=5)
        assert len(list(stream)) == 5

    def test_limit_none_yields_all(self):
        chunk = make_alleles_with_stats_response(n_variants=10)
        stream = VariantWithStatsStream(iter([chunk]), limit=None)
        assert len(list(stream)) == 10

    def test_limit_zero_yields_nothing(self):
        chunk = make_alleles_with_stats_response(n_variants=5)
        stream = VariantWithStatsStream(iter([chunk]), limit=0)
        assert list(stream) == []

    def test_limit_mid_chunk(self):
        c1 = make_alleles_with_stats_response(n_variants=4)
        c2 = make_alleles_with_stats_response(n_variants=4)
        stream = VariantWithStatsStream(iter([c1, c2]), limit=5)
        assert len(list(stream)) == 5

    def test_limit_larger_than_available(self):
        chunk = make_alleles_with_stats_response(n_variants=3)
        stream = VariantWithStatsStream(iter([chunk]), limit=100)
        assert len(list(stream)) == 3

    def test_to_list_respects_limit(self):
        chunk = make_alleles_with_stats_response(n_variants=10)
        stream = VariantWithStatsStream(iter([chunk]), limit=3)
        assert len(stream.to_list()) == 3

    def test_to_dataframe_respects_limit(self):
        pd = pytest.importorskip("pandas")
        chunk = make_alleles_with_stats_response(n_variants=10)
        stream = VariantWithStatsStream(iter([chunk]), limit=4)
        df = stream.to_dataframe()
        assert len(df) == 4

    def test_limit_metadata_reflects_consumed_chunks(self):
        c1 = make_alleles_with_stats_response(n_variants=3, elapsed_ms=100, node_id="n1")
        c2 = make_alleles_with_stats_response(n_variants=3, elapsed_ms=200, node_id="n2")
        stream = VariantWithStatsStream(iter([c1, c2]), limit=2)
        list(stream)
        assert stream.metadata.elapsed_ms == 100
        assert stream.metadata.node_id == "n1"
