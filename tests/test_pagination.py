"""Unit tests for PaginatedQuery and Page — no gRPC dependency."""

from __future__ import annotations

from collections import deque
from dataclasses import FrozenInstanceError
from unittest.mock import Mock

import pytest

from dnaerys._enums import Chromosome
from dnaerys._pagination import Page, PaginatedQuery
from dnaerys._types import ResponseMetadata, Variant


# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------


def make_fake_variant(start: int) -> Variant:
    return Variant(
        chr=Chromosome.CHR_1, start=start, end=start,
        ref="A", alt="T", af=0.5, ac=1.0, an=2,
        homc=0, hetc=1, misc=0, homfc=0, hetfc=0, misfc=0,
        gnomad_exomes_af=0.0, gnomad_genomes_af=0.0,
        cadd_raw=0.0, cadd_phred=0.0, am_score=0.0,
        amino_acids="", biallelic=True,
    )


def make_fake_stream(
    variants: list[Variant],
    *,
    elapsed_ms: int = 10,
    elapsed_db_ms: int = 5,
    node_id: str = "node-1",
    incomplete_cluster: bool = False,
    affected: bool = False,
) -> Mock:
    stream = Mock()
    stream.to_list.return_value = variants
    stream.metadata = ResponseMetadata(
        elapsed_ms=elapsed_ms,
        elapsed_db_ms=elapsed_db_ms,
        node_id=node_id,
        incomplete_cluster=incomplete_cluster,
        affected=affected,
    )
    return stream


def make_fetch(batches: list[list[Variant]], **meta_overrides):
    """Return a fetch callable that yields batches in order.

    Each call to fetch() pops from the front of *batches*.
    When batches is empty, returns an empty stream.
    *meta_overrides* can be a list of dicts (one per batch) or a single dict.
    """
    call_count = [0]

    def fetch(skip: int, limit: int):
        idx = call_count[0]
        call_count[0] += 1
        variants = batches[idx] if idx < len(batches) else []
        if isinstance(meta_overrides.get("per_call"), list):
            kw = meta_overrides["per_call"][idx] if idx < len(meta_overrides["per_call"]) else {}
        else:
            kw = {k: v for k, v in meta_overrides.items() if k != "per_call"}
        return make_fake_stream(variants, **kw)

    fetch.call_count = call_count
    return fetch


def make_tracking_fetch(batches: list[list[Variant]]):
    """Return a fetch callable that records (skip, limit) args."""
    calls: list[tuple[int, int]] = []

    def fetch(skip: int, limit: int):
        calls.append((skip, limit))
        idx = len(calls) - 1
        variants = batches[idx] if idx < len(batches) else []
        return make_fake_stream(variants)

    fetch.calls = calls
    return fetch


# ---------------------------------------------------------------------------
# Construction validation
# ---------------------------------------------------------------------------


class TestConstructionValidation:
    def test_page_size_zero_raises(self):
        with pytest.raises(ValueError, match="page_size must be >= 1"):
            PaginatedQuery(lambda s, l: None, page_size=0)

    def test_page_size_negative_raises(self):
        with pytest.raises(ValueError, match="page_size must be >= 1"):
            PaginatedQuery(lambda s, l: None, page_size=-1)

    def test_buffer_size_less_than_page_size_raises(self):
        with pytest.raises(ValueError, match="buffer_size must be >= page_size"):
            PaginatedQuery(lambda s, l: None, page_size=100, buffer_size=50)

    def test_valid_construction(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10, buffer_size=100)
        assert q.page_size == 10
        assert q.buffer_size == 100
        assert q.total_fetched == 0
        assert q.has_more is True


# ---------------------------------------------------------------------------
# Page dataclass
# ---------------------------------------------------------------------------


class TestPageDataclass:
    def test_page_is_frozen(self):
        page = Page(variants=(), page_number=1)
        with pytest.raises(FrozenInstanceError):
            page.variants = ()  # type: ignore[misc]

    def test_page_fields(self):
        v = make_fake_variant(100)
        page = Page(variants=(v,), page_number=3)
        assert isinstance(page.variants, tuple)
        assert page.page_number == 3
        assert page.variants[0] is v


# ---------------------------------------------------------------------------
# Basic pagination
# ---------------------------------------------------------------------------


class TestBasicPagination:
    def test_single_page_exact(self):
        variants = [make_fake_variant(i) for i in range(10)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=10)

        page = q.next_page()
        assert len(page.variants) == 10
        with pytest.raises(StopIteration):
            q.next_page()

    def test_multiple_pages_from_single_buffer(self):
        variants = [make_fake_variant(i) for i in range(25)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=25)

        pages = list(q)
        assert len(pages) == 3
        assert len(pages[0].variants) == 10
        assert len(pages[1].variants) == 10
        assert len(pages[2].variants) == 5

    def test_multiple_refills(self):
        b1 = [make_fake_variant(i) for i in range(10)]
        b2 = [make_fake_variant(10 + i) for i in range(10)]
        fetch = make_fetch([b1, b2, []])
        q = PaginatedQuery(fetch, page_size=5, buffer_size=10)

        pages = list(q)
        assert len(pages) == 4
        assert all(len(p.variants) == 5 for p in pages)


# ---------------------------------------------------------------------------
# Buffer mechanics
# ---------------------------------------------------------------------------


class TestBufferMechanics:
    def test_buffer_uses_deque(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10)
        assert isinstance(q._buffer, deque)

    def test_buffer_consumption_order(self):
        variants = [make_fake_variant(i) for i in range(5)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=3, buffer_size=5)

        page1 = q.next_page()
        assert [v.start for v in page1.variants] == [0, 1, 2]
        page2 = q.next_page()
        assert [v.start for v in page2.variants] == [3, 4]


# ---------------------------------------------------------------------------
# Exhaustion and termination
# ---------------------------------------------------------------------------


class TestExhaustion:
    def test_empty_result_set(self):
        fetch = make_fetch([[]])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=10)
        with pytest.raises(StopIteration):
            q.next_page()

    def test_fewer_than_buffer_size_not_terminal(self):
        b1 = [make_fake_variant(i) for i in range(3)]
        fetch = make_fetch([b1, []])
        q = PaginatedQuery(fetch, page_size=2, buffer_size=10)

        page1 = q.next_page()
        assert len(page1.variants) == 2
        page2 = q.next_page()
        assert len(page2.variants) == 1
        with pytest.raises(StopIteration):
            q.next_page()

    def test_offset_advances_by_buffer_size(self):
        b1 = [make_fake_variant(i) for i in range(3)]
        b2 = [make_fake_variant(i) for i in range(3)]
        fetch = make_tracking_fetch([b1, b2, []])
        q = PaginatedQuery(fetch, page_size=2, buffer_size=10)

        list(q)
        assert fetch.calls[0] == (0, 10)
        assert fetch.calls[1] == (10, 10)
        assert fetch.calls[2] == (20, 10)


# ---------------------------------------------------------------------------
# has_more semantics
# ---------------------------------------------------------------------------


class TestHasMore:
    def test_has_more_before_first_call(self):
        fetch = make_fetch([[make_fake_variant(1)], []])
        q = PaginatedQuery(fetch, page_size=1, buffer_size=1)
        assert q.has_more is True

    def test_has_more_during_iteration(self):
        variants = [make_fake_variant(i) for i in range(5)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=2, buffer_size=5)

        q.next_page()
        assert q.has_more is True
        q.next_page()
        assert q.has_more is True

    def test_has_more_after_exhaustion(self):
        variants = [make_fake_variant(i) for i in range(2)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=2, buffer_size=2)

        list(q)
        assert q.has_more is False

    def test_has_more_false_after_empty_result(self):
        fetch = make_fetch([[]])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=10)

        pages = list(q)
        assert pages == []
        assert q.has_more is False


# ---------------------------------------------------------------------------
# total_fetched
# ---------------------------------------------------------------------------


class TestTotalFetched:
    def test_total_fetched_zero_initially(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10)
        assert q.total_fetched == 0

    def test_total_fetched_accumulates(self):
        variants = [make_fake_variant(i) for i in range(30)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=30)

        list(q)
        assert q.total_fetched == 30

    def test_total_fetched_includes_last_short_page(self):
        variants = [make_fake_variant(i) for i in range(23)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=10, buffer_size=23)

        pages = list(q)
        assert q.total_fetched == 23
        assert sum(len(p.variants) for p in pages) == 23


# ---------------------------------------------------------------------------
# Metadata accumulation
# ---------------------------------------------------------------------------


class TestMetadata:
    def test_metadata_defaults_before_refill(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10)
        m = q.metadata
        assert m.elapsed_ms == 0
        assert m.elapsed_db_ms == 0
        assert m.node_id == ""
        assert m.incomplete_cluster is False
        assert m.affected is False

    def test_metadata_accumulated_across_refills(self):
        b1 = [make_fake_variant(i) for i in range(5)]
        b2 = [make_fake_variant(i) for i in range(5)]

        call_count = [0]

        def fetch(skip, limit):
            idx = call_count[0]
            call_count[0] += 1
            if idx == 0:
                return make_fake_stream(
                    b1, elapsed_ms=100, elapsed_db_ms=50,
                    node_id="node-A", incomplete_cluster=False, affected=False,
                )
            elif idx == 1:
                return make_fake_stream(
                    b2, elapsed_ms=200, elapsed_db_ms=30,
                    node_id="node-B", incomplete_cluster=True, affected=True,
                )
            else:
                return make_fake_stream([], node_id="")

        q = PaginatedQuery(fetch, page_size=3, buffer_size=5)
        list(q)

        m = q.metadata
        assert m.elapsed_ms == 200
        assert m.elapsed_db_ms == 50
        assert m.incomplete_cluster is True
        assert m.affected is True
        assert set(m.node_id.split(",")) == {"node-A", "node-B"}


# ---------------------------------------------------------------------------
# Iterator protocol
# ---------------------------------------------------------------------------


class TestIteratorProtocol:
    def test_for_loop(self):
        variants = [make_fake_variant(i) for i in range(7)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=3, buffer_size=7)

        pages = []
        for page in q:
            pages.append(page)

        assert len(pages) == 3
        assert len(pages[0].variants) == 3
        assert len(pages[1].variants) == 3
        assert len(pages[2].variants) == 1

    def test_iterator_returns_self(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10)
        assert iter(q) is q


# ---------------------------------------------------------------------------
# Context manager
# ---------------------------------------------------------------------------


class TestContextManager:
    def test_context_manager_clears_buffer(self):
        variants = [make_fake_variant(i) for i in range(10)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=5, buffer_size=10)

        with q:
            q.next_page()

        assert q.has_more is False

    def test_context_manager_returns_self(self):
        q = PaginatedQuery(lambda s, l: None, page_size=10)
        with q as ctx:
            assert ctx is q

    def test_usable_without_context_manager(self):
        variants = [make_fake_variant(i) for i in range(3)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=2, buffer_size=3)

        page = q.next_page()
        assert len(page.variants) == 2


# ---------------------------------------------------------------------------
# Independence
# ---------------------------------------------------------------------------


class TestIndependence:
    def test_two_queries_independent(self):
        v1 = [make_fake_variant(i) for i in range(5)]
        v2 = [make_fake_variant(100 + i) for i in range(3)]

        q1 = PaginatedQuery(make_fetch([v1, []]), page_size=5, buffer_size=5)
        q2 = PaginatedQuery(make_fetch([v2, []]), page_size=3, buffer_size=3)

        p1 = q1.next_page()
        p2 = q2.next_page()

        assert len(p1.variants) == 5
        assert len(p2.variants) == 3
        assert p1.variants[0].start == 0
        assert p2.variants[0].start == 100


# ---------------------------------------------------------------------------
# Page numbering
# ---------------------------------------------------------------------------


class TestPageNumbering:
    def test_page_numbers_start_at_one(self):
        variants = [make_fake_variant(i) for i in range(10)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=5, buffer_size=10)

        p1 = q.next_page()
        p2 = q.next_page()
        assert p1.page_number == 1
        assert p2.page_number == 2


# ---------------------------------------------------------------------------
# Last page shorter than page_size
# ---------------------------------------------------------------------------


class TestLastPageShorter:
    def test_last_page_can_be_shorter(self):
        variants = [make_fake_variant(i) for i in range(7)]
        fetch = make_fetch([variants, []])
        q = PaginatedQuery(fetch, page_size=5, buffer_size=7)

        pages = list(q)
        assert len(pages) == 2
        assert len(pages[0].variants) == 5
        assert len(pages[1].variants) == 2
