"""Integration tests for paginate_variants using the fake gRPC server.

The fake servicer returns the same canned chunks on every RPC call, so
the PaginatedQuery never sees an empty result and cannot exhaust naturally.
These tests therefore verify the factory method, parameter forwarding, and
first-page correctness — full pagination and exhaustion are thoroughly
covered in test_pagination.py with mock fetch callables.
"""

from __future__ import annotations

import pytest

from dnaerys import (
    AnnotationFilter,
    Bracket,
    Impact,
    Page,
    PaginatedQuery,
    Region,
)
from tests.conftest import make_alleles_response, make_variant_proto


class TestPaginateVariantsFactory:
    def test_paginate_variants_returns_paginated_query(self, client, fake_servicer):
        q = client.paginate_variants(
            region=Region("chr1", 100, 200),
            page_size=10,
        )
        assert isinstance(q, PaginatedQuery)

    def test_paginate_variants_region(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=3),
        ]
        q = client.paginate_variants(
            region=Region("chr1", 100, 200),
            page_size=2,
            buffer_size=5000,
        )
        page = q.next_page()
        assert isinstance(page, Page)
        assert len(page.variants) == 2
        assert page.page_number == 1

    def test_paginate_variants_regions(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_variants(
            regions=[Region("chr1", 100, 200), Region("chr2", 300, 400)],
            page_size=3,
            buffer_size=5000,
        )
        page = q.next_page()
        assert len(page.variants) == 3

    def test_paginate_variants_bracket(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_variants(
            bracket=Bracket("chr1", 100, 200, 300, 400),
            page_size=3,
            buffer_size=5000,
        )
        page = q.next_page()
        assert len(page.variants) == 3

    def test_paginate_variants_with_samples(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_variants(
            region=Region("chr1", 100, 200),
            samples=["SAMPLE_A"],
            page_size=3,
            buffer_size=5000,
        )
        page = q.next_page()
        assert len(page.variants) == 3

    def test_paginate_variants_with_annotations(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_variants(
            region=Region("chr1", 100, 200),
            annotations=AnnotationFilter(impact=[Impact.HIGH]),
            page_size=3,
            buffer_size=5000,
        )
        page = q.next_page()
        assert len(page.variants) == 3

    def test_paginate_variants_custom_buffer_size(self, client, fake_servicer):
        """With buffer_size=2 and page_size=1, verify multiple pages from one buffer fill."""
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=2),
        ]
        q = client.paginate_variants(
            region=Region("chr1", 100, 200),
            page_size=1,
            buffer_size=2,
        )
        page1 = q.next_page()
        assert len(page1.variants) == 1
        assert page1.page_number == 1

        page2 = q.next_page()
        assert len(page2.variants) == 1
        assert page2.page_number == 2


class TestPaginateVariantsWithStatsFactory:
    def test_paginate_variants_with_stats_returns_paginated_query(self, client, fake_servicer):
        from tests.conftest import make_alleles_with_stats_response
        q = client.paginate_variants_with_stats(
            regions=[Region("chr1", 100, 200)],
            page_size=10,
        )
        assert isinstance(q, PaginatedQuery)

    def test_paginate_variants_with_stats_first_page(self, client, fake_servicer):
        from tests.conftest import make_alleles_with_stats_response
        fake_servicer.variant_with_stats_chunks = [
            make_alleles_with_stats_response(n_variants=4),
        ]
        q = client.paginate_variants_with_stats(
            regions=[Region("chr1", 100, 200)],
            page_size=2,
            buffer_size=5000,
        )
        page = q.next_page()
        assert isinstance(page, Page)
        assert len(page.variants) == 2
        assert page.page_number == 1

    def test_paginate_variants_with_stats_with_annotations(self, client, fake_servicer):
        from tests.conftest import make_alleles_with_stats_response
        fake_servicer.variant_with_stats_chunks = [
            make_alleles_with_stats_response(n_variants=4),
        ]
        q = client.paginate_variants_with_stats(
            regions=[Region("chr1", 100, 200)],
            annotations=AnnotationFilter(impact=[Impact.HIGH]),
            page_size=3,
            buffer_size=5000,
        )
        page = q.next_page()
        assert len(page.variants) == 3


class TestPaginateInheritanceFactory:
    def test_paginate_de_novo_first_page(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_de_novo(
            page_size=2,
            parent1="P1", parent2="P2", proband="C1",
            region=Region("chr1", 100, 200),
        )
        page = q.next_page()
        assert isinstance(page, Page)
        assert len(page.variants) == 2
        assert page.page_number == 1

    def test_paginate_het_dominant_first_page(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_het_dominant(
            page_size=2,
            affected_parent="AP", unaffected_parent="UP",
            affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        page = q.next_page()
        assert isinstance(page, Page)
        assert len(page.variants) == 2

    def test_paginate_hom_recessive_first_page(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_hom_recessive(
            page_size=2,
            unaffected_parent1="UP1", unaffected_parent2="UP2",
            affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        page = q.next_page()
        assert isinstance(page, Page)
        assert len(page.variants) == 2

    def test_paginate_de_novo_with_annotations(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=4),
        ]
        q = client.paginate_de_novo(
            page_size=3,
            parent1="P1", parent2="P2", proband="C1",
            region=Region("chr1", 100, 200),
            annotations=AnnotationFilter(impact=[Impact.HIGH]),
        )
        page = q.next_page()
        assert len(page.variants) == 3
