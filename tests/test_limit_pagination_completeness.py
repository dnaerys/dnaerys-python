"""Completeness tests for the per-ring server cap (R1.20.0).

The Dnaerys cluster caps each ring's streaming response at a hard limit and
applies ``skip``/``limit`` **per ring** (data is range-partitioned across owner
rings with no duplication).  Two client guarantees must hold on top of that:

- **Strong ``limit``** (``select_*``): a hard *global* cap that may exceed the
  per-ring cap, delivered by internal ``skip``-batched requests that keep every
  owner ring's full window.
- **Pagination** (``paginate_*``): walk every ring's partition with no gaps or
  duplicates, using a constant per-ring window ``<=`` the cap and keeping the
  full (multi-owner) response each round-trip.

These use the ring-simulation mode of the fake servicer (``configure_rings`` /
``configure_stats_rings``), which honours per-ring ``skip``/``limit``/cap.
"""

from __future__ import annotations

import pytest

from dnaerys import Region

_REGION = Region("chr1", 1, 1_000_000)


def _proto_start(v) -> int:
    """Start position of a ring proto (``pb2.Variant`` or ``pb2.VariantWithStats``)."""
    return v.variant.start if hasattr(v, "variant") else v.start


def _expected_starts(rings) -> set[int]:
    """The full set of unique variant start positions across all rings."""
    return {_proto_start(v) for ring in rings for v in ring}


# ---------------------------------------------------------------------------
# Strong limit (Finding 3) — internal skip-batching
# ---------------------------------------------------------------------------


class TestStrongLimitBatching:
    def test_limit_below_cap_single_ring(self, client, fake_servicer):
        fake_servicer.configure_rings([12], cap=5)
        got = client.select_variants(region=_REGION, limit=3).to_list()
        assert len(got) == 3
        assert len({v.start for v in got}) == 3  # no duplicates

    def test_limit_spans_multiple_batches_single_ring(self, client, fake_servicer):
        # cap=5, limit=8 -> needs two batches (skip 0 then 5) from one ring.
        fake_servicer.configure_rings([12], cap=5)
        got = client.select_variants(region=_REGION, limit=8).to_list()
        assert len(got) == 8
        assert len({v.start for v in got}) == 8

    def test_limit_exceeds_cap_but_below_total(self, client, fake_servicer):
        fake_servicer.configure_rings([12], cap=5)
        got = client.select_variants(region=_REGION, limit=10).to_list()
        assert len(got) == 10  # > per-ring cap, still honoured exactly

    def test_limit_larger_than_total_returns_all(self, client, fake_servicer):
        fake_servicer.configure_rings([12], cap=5)
        got = client.select_variants(region=_REGION, limit=1000).to_list()
        assert len(got) == 12  # exhausted; no infinite batching
        assert {v.start for v in got} == _expected_starts(fake_servicer.rings)

    def test_limit_multi_owner_complete(self, client, fake_servicer):
        # THE multi-owner case: a single request can only yield cap*owners=10,
        # but limit=1000 must batch to the full 12+7=19 with no gaps/dups.
        fake_servicer.configure_rings([12, 7], cap=5)
        got = client.select_variants(region=_REGION, limit=1000).to_list()
        assert len(got) == 19
        assert {v.start for v in got} == _expected_starts(fake_servicer.rings)

    def test_limit_multi_owner_partial_exact(self, client, fake_servicer):
        fake_servicer.configure_rings([12, 7], cap=5)
        got = client.select_variants(region=_REGION, limit=15).to_list()
        assert len(got) == 15
        assert len({v.start for v in got}) == 15

    def test_limit_zero_yields_nothing(self, client, fake_servicer):
        fake_servicer.configure_rings([12], cap=5)
        got = client.select_variants(region=_REGION, limit=0).to_list()
        assert got == []

    def test_limit_none_is_single_capped_request(self, client, fake_servicer):
        # limit=None -> one request; each ring returns up to its cap (truncated
        # for large regions), i.e. cap * owners, NOT batched to completeness.
        fake_servicer.configure_rings([12, 7], cap=5)
        got = client.select_variants(region=_REGION, limit=None).to_list()
        assert len(got) == 10  # 5 per ring, capped

    def test_with_stats_limit_multi_owner_complete(self, client, fake_servicer):
        fake_servicer.configure_stats_rings([9, 6], cap=4)
        got = client.select_variants_with_stats(
            regions=[_REGION], limit=1000,
        ).to_list()
        assert len(got) == 15
        assert {v.start for v in got} == _expected_starts(fake_servicer.stats_rings)

    def test_with_stats_limit_exact(self, client, fake_servicer):
        fake_servicer.configure_stats_rings([9, 6], cap=4)
        got = client.select_variants_with_stats(regions=[_REGION], limit=11).to_list()
        assert len(got) == 11

    @pytest.mark.parametrize("method,kwargs", [
        ("select_de_novo", dict(parent1="P1", parent2="P2", proband="C1")),
        ("select_het_dominant", dict(
            affected_parent="AP", unaffected_parent="UP", affected_child="AC")),
        ("select_hom_recessive", dict(
            unaffected_parent1="U1", unaffected_parent2="U2", affected_child="AC")),
    ])
    def test_inheritance_limit_batches(self, client, fake_servicer, method, kwargs):
        # Inheritance RPCs stream over the variant ring path.
        fake_servicer.configure_rings([12], cap=5)
        stream = getattr(client, method)(region=_REGION, limit=8, **kwargs)
        got = stream.to_list()
        assert len(got) == 8
        assert len({v.start for v in got}) == 8


# ---------------------------------------------------------------------------
# Pagination completeness (Finding 1)
# ---------------------------------------------------------------------------


def _drain(query) -> list:
    variants = []
    for page in query:
        variants.extend(page.variants)
    return variants


class TestPaginationCompleteness:
    def test_single_ring_complete(self, client, fake_servicer):
        fake_servicer.configure_rings([23], cap=5)
        q = client.paginate_variants(region=_REGION, page_size=4, buffer_size=5)
        got = _drain(q)
        starts = [v.start for v in got]
        assert len(starts) == 23
        assert set(starts) == _expected_starts(fake_servicer.rings)  # no gaps
        assert len(starts) == len(set(starts))  # no duplicates

    def test_multi_owner_complete(self, client, fake_servicer):
        # Regression for the client-cap-in-refill bug: the old refill trimmed
        # each round-trip to buffer_size, discarding ring 1's window every page
        # and keeping only ~ring 0. buffer_size defaults to the cap.
        fake_servicer.configure_rings([23, 11], cap=5)
        q = client.paginate_variants(region=_REGION, page_size=10)
        got = _drain(q)
        starts = [v.start for v in got]
        assert len(starts) == 34
        assert set(starts) == _expected_starts(fake_servicer.rings)
        assert len(starts) == len(set(starts))

    def test_multi_owner_three_rings_uneven(self, client, fake_servicer):
        fake_servicer.configure_rings([17, 5, 30], cap=6)
        q = client.paginate_variants(region=_REGION, page_size=7, buffer_size=6)
        got = _drain(q)
        starts = [v.start for v in got]
        assert len(starts) == 52
        assert set(starts) == _expected_starts(fake_servicer.rings)
        assert len(starts) == len(set(starts))

    def test_with_stats_multi_owner_complete(self, client, fake_servicer):
        fake_servicer.configure_stats_rings([14, 9], cap=4)
        q = client.paginate_variants_with_stats(regions=[_REGION], page_size=6)
        got = _drain(q)
        starts = [v.start for v in got]
        assert len(starts) == 23
        assert set(starts) == _expected_starts(fake_servicer.stats_rings)

    def test_de_novo_multi_owner_complete(self, client, fake_servicer):
        fake_servicer.configure_rings([13, 8], cap=5)
        q = client.paginate_de_novo(
            region=_REGION, page_size=5,
            parent1="P1", parent2="P2", proband="C1",
        )
        got = _drain(q)
        assert {v.start for v in got} == _expected_starts(fake_servicer.rings)
        assert len(got) == 21


# ---------------------------------------------------------------------------
# buffer_size resolution against the server cap
# ---------------------------------------------------------------------------


class TestBufferSizeResolution:
    def test_defaults_to_server_cap(self, client, fake_servicer):
        fake_servicer.configure_rings([10], cap=1234)
        q = client.paginate_variants(region=_REGION, page_size=5)
        assert q.buffer_size == 1234

    def test_fallback_when_cap_not_advertised(self, client, fake_servicer):
        # dataset_info reports max_variants_per_ring=0 (default) -> fallback 5000.
        q = client.paginate_variants(region=_REGION, page_size=5)
        assert q.buffer_size == 5000

    def test_below_cap_is_respected(self, client, fake_servicer):
        fake_servicer.configure_rings([10], cap=100)
        q = client.paginate_variants(region=_REGION, page_size=5, buffer_size=20)
        assert q.buffer_size == 20

    def test_above_cap_clamped_with_warning(self, client, fake_servicer):
        fake_servicer.configure_rings([23, 11], cap=5)
        with pytest.warns(UserWarning, match="clamping"):
            q = client.paginate_variants(
                region=_REGION, page_size=4, buffer_size=10,
            )
        assert q.buffer_size == 5
        # ...and results are still complete despite the oversized request.
        got = _drain(q)
        assert {v.start for v in got} == _expected_starts(fake_servicer.rings)

    def test_zero_buffer_size_rejected(self, client, fake_servicer):
        with pytest.raises(ValueError, match="buffer_size"):
            client.paginate_variants(region=_REGION, page_size=1, buffer_size=0)


# ---------------------------------------------------------------------------
# Server cap discovery is exposed on DatasetInfo
# ---------------------------------------------------------------------------


class TestCapDiscovery:
    def test_dataset_info_exposes_cap(self, client, fake_servicer):
        fake_servicer.dataset_info_response.max_variants_per_ring = 4096
        info = client.dataset_info()
        assert info.max_variants_per_ring == 4096

    def test_cap_is_cached(self, client, fake_servicer):
        fake_servicer.configure_rings([10], cap=321)
        # First use triggers a dataset_info lookup and caches the cap.
        client.paginate_variants(region=_REGION, page_size=5)
        # Change the server's advertised cap; the client must keep the cached one.
        fake_servicer.dataset_info_response.max_variants_per_ring = 999
        q = client.paginate_variants(region=_REGION, page_size=5)
        assert q.buffer_size == 321
