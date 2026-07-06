"""Tests for dispatch routing logic in dnaerys._dispatch."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from dnaerys._dispatch import (
    _validate_exactly_one,
    dispatch_count_samples,
    dispatch_count_variants,
    dispatch_select_samples,
    dispatch_select_variants,
    dispatch_select_variants_with_stats,
)
from dnaerys._enums import Chromosome, RefAssembly
from dnaerys._exceptions import DnaerysInvalidRequestError
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._types import AnnotationFilter, Bracket, Region


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_stub() -> MagicMock:
    """Create a mock DnaerysServiceStub with all RPC methods."""
    return MagicMock()


REGION = Region("chr1", 100, 200)
REGION2 = Region("chr2", 300, 400, ref="G", alt="C")
REGIONS = [REGION, REGION2]
BRACKET = Bracket("chr1", 100, 200, 300, 400)
SAMPLES = ["S1", "S2"]

COMMON = {
    "hom": True,
    "het": True,
    "annotations": None,
    "assembly": RefAssembly.GRCh38,
    "variant_min_length": None,
    "variant_max_length": None,
}


# ---------------------------------------------------------------------------
# _validate_exactly_one
# ---------------------------------------------------------------------------


class TestValidateExactlyOne:
    def test_one_set(self):
        _validate_exactly_one(a=1, b=None, c=None)

    def test_none_set_raises(self):
        with pytest.raises(DnaerysInvalidRequestError, match="exactly one"):
            _validate_exactly_one(a=None, b=None)

    def test_multiple_set_raises(self):
        with pytest.raises(DnaerysInvalidRequestError, match="only one"):
            _validate_exactly_one(a=1, b=2, c=None)


# ---------------------------------------------------------------------------
# dispatch_select_variants
# ---------------------------------------------------------------------------


class TestDispatchSelectVariants:
    def test_dispatch_select_variants_region(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=REGION, regions=None, bracket=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInRegion.assert_called_once()

    def test_dispatch_select_variants_region_in_samples(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=REGION, regions=None, bracket=None, samples=SAMPLES,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInRegionInSamples.assert_called_once()

    def test_dispatch_select_variants_bracket(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=None, regions=None, bracket=BRACKET, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInBracket.assert_called_once()

    def test_dispatch_select_variants_bracket_in_samples(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=None, regions=None, bracket=BRACKET, samples=SAMPLES,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInBracketInSamples.assert_called_once()

    def test_dispatch_select_variants_multi_regions(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=None, regions=REGIONS, bracket=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInMultiRegions.assert_called_once()

    def test_dispatch_select_variants_multi_regions_in_samples(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=None, regions=REGIONS, bracket=None, samples=SAMPLES,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInMultiRegionsInSamples.assert_called_once()

    def test_dispatch_select_variants_no_location_raises(self):
        stub = _make_stub()
        with pytest.raises(DnaerysInvalidRequestError, match="exactly one"):
            dispatch_select_variants(
                stub, region=None, regions=None, bracket=None, samples=None,
                skip=None, limit=None, timeout=None, **COMMON,
            )

    def test_dispatch_select_variants_multiple_locations_raises(self):
        stub = _make_stub()
        with pytest.raises(DnaerysInvalidRequestError, match="only one"):
            dispatch_select_variants(
                stub, region=REGION, regions=None, bracket=BRACKET, samples=None,
                skip=None, limit=None, timeout=None, **COMMON,
            )

    def test_dispatch_select_variants_request_fields(self):
        stub = _make_stub()
        ann = AnnotationFilter(af_lt=0.05)
        dispatch_select_variants(
            stub, region=REGION, regions=None, bracket=None, samples=None,
            hom=True, het=False,
            annotations=ann,
            assembly=RefAssembly.GRCh37,
            variant_min_length=10,
            variant_max_length=100,
            skip=5, limit=50, timeout=30.0,
        )
        call_args = stub.SelectVariantsInRegion.call_args
        request = call_args[0][0]
        assert request.chr == int(Chromosome.CHR1)
        assert request.start == 100
        assert request.end == 200
        assert request.hom is True
        assert request.het is False
        assert request.assembly == int(RefAssembly.GRCh37)
        assert request.variantMinLength == 10
        assert request.variantMaxLength == 100
        assert request.skip == 5
        assert request.limit == 50
        assert request.ann.af_lt == pytest.approx(0.05)
        assert call_args[1]["timeout"] == 30.0


# ---------------------------------------------------------------------------
# dispatch_select_variants_with_stats
# ---------------------------------------------------------------------------


class TestDispatchSelectVariantsWithStats:
    def test_dispatch_select_variants_with_stats_region_samples(self):
        stub = _make_stub()
        dispatch_select_variants_with_stats(
            stub, region=REGION, regions=None, samples=SAMPLES,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInRegionInSamplesWithStats.assert_called_once()

    def test_dispatch_select_variants_with_stats_regions(self):
        stub = _make_stub()
        dispatch_select_variants_with_stats(
            stub, region=None, regions=REGIONS, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInMultiRegionsWithStats.assert_called_once()

    def test_dispatch_select_variants_with_stats_regions_samples(self):
        stub = _make_stub()
        dispatch_select_variants_with_stats(
            stub, region=None, regions=REGIONS, samples=SAMPLES,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInMultiRegionsInSamplesWithStats.assert_called_once()

    def test_dispatch_select_variants_with_stats_single_region_no_samples(self):
        stub = _make_stub()
        dispatch_select_variants_with_stats(
            stub, region=REGION, regions=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectVariantsInMultiRegionsWithStats.assert_called_once()

    def test_dispatch_select_variants_with_stats_single_region_wraps_to_list(self):
        stub = _make_stub()
        dispatch_select_variants_with_stats(
            stub, region=REGION, regions=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        request = stub.SelectVariantsInMultiRegionsWithStats.call_args[0][0]
        assert list(request.chr) == [int(Chromosome.CHR1)]
        assert list(request.start) == [100]
        assert list(request.end) == [200]

    def test_dispatch_select_variants_with_stats_no_location_raises(self):
        stub = _make_stub()
        with pytest.raises(DnaerysInvalidRequestError, match="exactly one"):
            dispatch_select_variants_with_stats(
                stub, region=None, regions=None, samples=None,
                skip=None, limit=None, timeout=None, **COMMON,
            )


# ---------------------------------------------------------------------------
# dispatch_count_variants
# ---------------------------------------------------------------------------


class TestDispatchCountVariants:
    def test_dispatch_count_variants_region(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=REGION, regions=None, bracket=None, samples=None,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInRegion.assert_called_once()

    def test_dispatch_count_variants_region_in_samples(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=REGION, regions=None, bracket=None, samples=SAMPLES,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInRegionInSamples.assert_called_once()

    def test_dispatch_count_variants_bracket(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=None, regions=None, bracket=BRACKET, samples=None,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInBracket.assert_called_once()

    def test_dispatch_count_variants_bracket_in_samples(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=None, regions=None, bracket=BRACKET, samples=SAMPLES,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInBracketInSamples.assert_called_once()

    def test_dispatch_count_variants_multi_regions(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=None, regions=REGIONS, bracket=None, samples=None,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInMultiRegions.assert_called_once()

    def test_dispatch_count_variants_multi_regions_in_samples(self):
        stub = _make_stub()
        dispatch_count_variants(
            stub, region=None, regions=REGIONS, bracket=None, samples=SAMPLES,
            timeout=None, **COMMON,
        )
        stub.CountVariantsInMultiRegionsInSamples.assert_called_once()


# ---------------------------------------------------------------------------
# dispatch_select_samples / dispatch_count_samples
# ---------------------------------------------------------------------------


class TestDispatchSamples:
    def test_dispatch_select_samples_region(self):
        stub = _make_stub()
        dispatch_select_samples(
            stub, region=REGION, regions=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectSamplesInRegion.assert_called_once()

    def test_dispatch_select_samples_multi_regions(self):
        stub = _make_stub()
        dispatch_select_samples(
            stub, region=None, regions=REGIONS,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        stub.SelectSamplesInMultiRegions.assert_called_once()

    def test_dispatch_select_samples_no_location_raises(self):
        stub = _make_stub()
        with pytest.raises(DnaerysInvalidRequestError, match="exactly one"):
            dispatch_select_samples(
                stub, region=None, regions=None,
                skip=None, limit=None, timeout=None, **COMMON,
            )

    def test_dispatch_count_samples_region(self):
        stub = _make_stub()
        dispatch_count_samples(
            stub, region=REGION, regions=None,
            timeout=None, **COMMON,
        )
        stub.CountSamplesInRegion.assert_called_once()

    def test_dispatch_count_samples_multi_regions(self):
        stub = _make_stub()
        dispatch_count_samples(
            stub, region=None, regions=REGIONS,
            timeout=None, **COMMON,
        )
        stub.CountSamplesInMultiRegions.assert_called_once()


# ---------------------------------------------------------------------------
# Multi-region request construction
# ---------------------------------------------------------------------------


class TestMultiRegionDecomposition:
    def test_dispatch_multi_region_decomposes_regions(self):
        stub = _make_stub()
        r1 = Region("chr1", 100, 200)
        r2 = Region("chr2", 300, 400)
        dispatch_select_variants(
            stub, region=None, regions=[r1, r2], bracket=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        request = stub.SelectVariantsInMultiRegions.call_args[0][0]
        assert list(request.chr) == [int(Chromosome.CHR1), int(Chromosome.CHR2)]
        assert list(request.start) == [100, 300]
        assert list(request.end) == [200, 400]

    def test_dispatch_multi_region_ref_alt_from_regions(self):
        stub = _make_stub()
        r1 = Region("chr1", 100, 200, ref="A", alt="T")
        r2 = Region("chr2", 300, 400)  # ref=None, alt=None → ""
        dispatch_select_variants(
            stub, region=None, regions=[r1, r2], bracket=None, samples=None,
            skip=None, limit=None, timeout=None, **COMMON,
        )
        request = stub.SelectVariantsInMultiRegions.call_args[0][0]
        assert list(request.ref) == ["A", ""]
        assert list(request.alt) == ["T", ""]


# ---------------------------------------------------------------------------
# Default hom/het
# ---------------------------------------------------------------------------


class TestDefaultHomHet:
    def test_dispatch_default_hom_het_true(self):
        stub = _make_stub()
        dispatch_select_variants(
            stub, region=REGION, regions=None, bracket=None, samples=None,
            hom=True, het=True, annotations=None, assembly=RefAssembly.GRCh38,
            variant_min_length=None, variant_max_length=None,
            skip=None, limit=None, timeout=None,
        )
        request = stub.SelectVariantsInRegion.call_args[0][0]
        assert request.hom is True
        assert request.het is True
