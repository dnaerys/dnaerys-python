"""Integration tests for DnaerysClient against an in-process fake gRPC server."""

from __future__ import annotations

import warnings

import grpc
import pytest

from dnaerys import (
    DnaerysClient,
    DnaerysAuthenticationError,
    DnaerysConnectionError,
    DnaerysIncompleteResultWarning,
    DnaerysInvalidRequestError,
    DnaerysNotFoundError,
    DnaerysResourceExhausted,
    DnaerysServerError,
    Region,
    Bracket,
    Variant,
    VariantWithStats,
    VariantStream,
    VariantWithStatsStream,
    PaginatedQuery,
    CountResult,
    SamplesResult,
    HealthResult,
    ClusterNodesResult,
    DatasetInfo,
    PrsResult,
    SexMismatchResult,
    FstatXResult,
    KinshipResult,
    SampleKinshipResult,
    TopHweResult,
    TopChi2Result,
)
from dnaerys._proto import dnaerys_pb2 as pb2
from tests.conftest import (
    make_alleles_response,
    make_alleles_with_stats_response,
)


# ---------------------------------------------------------------------------
# Infrastructure methods
# ---------------------------------------------------------------------------


class TestInfrastructure:
    def test_health(self, client, fake_servicer):
        result = client.health()
        assert isinstance(result, HealthResult)
        assert result.status == "SERVING"

    def test_cluster_nodes(self, client, fake_servicer):
        result = client.cluster_nodes()
        assert isinstance(result, ClusterNodesResult)
        assert "node-1" in result.active_nodes
        assert result.total_nodes == 2

    def test_dataset_info(self, client, fake_servicer):
        result = client.dataset_info()
        assert isinstance(result, DatasetInfo)
        assert result.samples_total == 100
        assert len(result.cohorts) == 1
        assert result.cohorts[0].cohort_name == "test-cohort"
        assert len(result.prs) == 1

    def test_dataset_info_with_sample_names(self, client, fake_servicer):
        fake_servicer.dataset_info_response = pb2.DatasetInfoResponse(
            cohorts=[pb2.Cohort(
                cohort_name="test",
                samples_count=2,
                female_count=1,
                male_count=1,
                female_samples_names=["F1"],
                male_samples_names=["M1"],
            )],
            samples_total=2,
            assembly=pb2.GRCh38,
            elapsed_ms=5,
            node_id="node-1",
        )
        result = client.dataset_info(return_sample_names=True)
        assert result.cohorts[0].female_sample_names == ("F1",)
        assert result.cohorts[0].male_sample_names == ("M1",)


# ---------------------------------------------------------------------------
# Variant select — full call path
# ---------------------------------------------------------------------------


class TestSelectVariants:
    def test_select_variants_region(self, client, fake_servicer):
        stream = client.select_variants(region=Region("chr1", 100, 200))
        assert isinstance(stream, VariantStream)
        variants = stream.to_list()
        assert len(variants) == 2
        assert all(isinstance(v, Variant) for v in variants)

    def test_select_variants_region_in_samples(self, client, fake_servicer):
        stream = client.select_variants(
            region=Region("chr1", 100, 200), samples=["S1"],
        )
        variants = stream.to_list()
        assert len(variants) == 2

    def test_select_variants_bracket(self, client, fake_servicer):
        stream = client.select_variants(
            bracket=Bracket("chr1", 100, 200, 300, 400),
        )
        variants = stream.to_list()
        assert len(variants) == 2

    def test_select_variants_multi_regions(self, client, fake_servicer):
        stream = client.select_variants(
            regions=[Region("chr1", 100, 200), Region("chr2", 300, 400)],
        )
        variants = stream.to_list()
        assert len(variants) == 2

    def test_select_variants_with_stats_region_samples(self, client, fake_servicer):
        stream = client.select_variants_with_stats(
            region=Region("chr1", 100, 200), samples=["S1"],
        )
        assert isinstance(stream, VariantWithStatsStream)
        variants = stream.to_list()
        assert len(variants) == 2
        assert all(isinstance(v, VariantWithStats) for v in variants)

    def test_select_variants_with_stats_multi_regions(self, client, fake_servicer):
        stream = client.select_variants_with_stats(
            regions=[Region("chr1", 100, 200)],
        )
        variants = stream.to_list()
        assert len(variants) == 2


# ---------------------------------------------------------------------------
# Variant count
# ---------------------------------------------------------------------------


class TestCountVariants:
    def test_count_variants_region(self, client, fake_servicer):
        result = client.count_variants(region=Region("chr1", 100, 200))
        assert isinstance(result, CountResult)
        assert result.count == 42

    def test_count_variants_bracket(self, client, fake_servicer):
        result = client.count_variants(
            bracket=Bracket("chr1", 100, 200, 300, 400),
        )
        assert result.count == 42

    def test_count_variants_multi_regions_in_samples(self, client, fake_servicer):
        result = client.count_variants(
            regions=[Region("chr1", 100, 200)],
            samples=["S1"],
        )
        assert result.count == 42


# ---------------------------------------------------------------------------
# Sample queries
# ---------------------------------------------------------------------------


class TestSampleQueries:
    def test_select_samples_region(self, client, fake_servicer):
        result = client.select_samples(region=Region("chr1", 100, 200))
        assert isinstance(result, SamplesResult)
        assert "SAMPLE_A" in result.samples

    def test_count_samples_region(self, client, fake_servicer):
        result = client.count_samples(region=Region("chr1", 100, 200))
        assert isinstance(result, CountResult)
        assert result.count == 10

    def test_select_samples_hom_ref(self, client, fake_servicer):
        result = client.select_samples_hom_ref(chr="chr1", position=100)
        assert isinstance(result, SamplesResult)
        assert "SAMPLE_A" in result.samples

    def test_count_samples_hom_ref(self, client, fake_servicer):
        result = client.count_samples_hom_ref(chr="chr1", position=100)
        assert isinstance(result, CountResult)
        assert result.count == 10


# ---------------------------------------------------------------------------
# Inheritance
# ---------------------------------------------------------------------------


class TestInheritance:
    def test_select_de_novo(self, client, fake_servicer):
        stream = client.select_de_novo(
            parent1="P1", parent2="P2", proband="C1",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(stream, VariantStream)
        assert len(stream.to_list()) == 2

    def test_select_het_dominant(self, client, fake_servicer):
        stream = client.select_het_dominant(
            affected_parent="AP", unaffected_parent="UP", affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(stream, VariantStream)
        assert len(stream.to_list()) == 2

    def test_select_hom_recessive(self, client, fake_servicer):
        stream = client.select_hom_recessive(
            unaffected_parent1="UP1", unaffected_parent2="UP2",
            affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(stream, VariantStream)
        assert len(stream.to_list()) == 2


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------


class TestStatistics:
    def test_top_hwe(self, client, fake_servicer):
        result = client.top_hwe(n=10)
        assert isinstance(result, TopHweResult)
        assert len(result.variants) == 1

    def test_top_chi2(self, client, fake_servicer):
        result = client.top_chi2(n=10, samples=["S1"])
        assert isinstance(result, TopChi2Result)
        assert len(result.variants) == 1

    def test_prs(self, client, fake_servicer):
        result = client.prs(prs_name="PRS001", cohort_name="test-cohort")
        assert isinstance(result, PrsResult)
        assert result.prs_name == "PRS001"

    def test_sex_mismatch_check(self, client, fake_servicer):
        result = client.sex_mismatch_check(cohort_name="test-cohort")
        assert isinstance(result, SexMismatchResult)

    def test_fstat_x(self, client, fake_servicer):
        result = client.fstat_x(cohort_name="test-cohort")
        assert isinstance(result, FstatXResult)
        assert len(result.males) == 1


# ---------------------------------------------------------------------------
# Kinship
# ---------------------------------------------------------------------------


class TestKinship:
    def test_kinship(self, client, fake_servicer):
        result = client.kinship(cohort_name="test-cohort")
        assert isinstance(result, KinshipResult)
        assert len(result.pairs) == 1

    def test_kinship_duo(self, client, fake_servicer):
        result = client.kinship_duo(sample1="S1", sample2="S2")
        assert isinstance(result, KinshipResult)

    def test_kinship_trio(self, client, fake_servicer):
        result = client.kinship_trio(sample1="S1", sample2="S2", sample3="S3")
        assert isinstance(result, KinshipResult)

    def test_sample_kinship(self, client, fake_servicer):
        result = client.sample_kinship(sample_vcf="data.vcf")
        assert isinstance(result, SampleKinshipResult)
        assert result.accepted_snvs == 1000


# ---------------------------------------------------------------------------
# Streaming behaviour
# ---------------------------------------------------------------------------


class TestStreaming:
    def test_streaming_multiple_chunks(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=2),
            make_alleles_response(n_variants=3),
            make_alleles_response(n_variants=1),
        ]
        stream = client.select_variants(region=Region("chr1", 100, 200))
        variants = stream.to_list()
        assert len(variants) == 6

    def test_streaming_metadata_accumulation(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=1, elapsed_ms=10, node_id="n1"),
            make_alleles_response(n_variants=1, elapsed_ms=20, node_id="n2"),
        ]
        stream = client.select_variants(region=Region("chr1", 100, 200))
        stream.to_list()
        meta = stream.metadata
        assert meta.elapsed_ms == 20  # max
        assert set(meta.node_id.split(",")) == {"n1", "n2"}

    def test_streaming_to_list(self, client, fake_servicer):
        stream = client.select_variants(region=Region("chr1", 100, 200))
        result = stream.to_list()
        assert isinstance(result, list)
        assert all(isinstance(v, Variant) for v in result)

    def test_streaming_to_dataframe(self, client, fake_servicer):
        pytest.importorskip("pandas")
        stream = client.select_variants(region=Region("chr1", 100, 200))
        df = stream.to_dataframe()
        assert len(df) == 2
        assert "chr" in df.columns


# ---------------------------------------------------------------------------
# Incomplete cluster warning
# ---------------------------------------------------------------------------


class TestIncompleteClusterWarning:
    def test_unary_affected_warning(self, client, fake_servicer):
        fake_servicer.count_response = pb2.CountAllelesResponse(
            count=5, affected=True, elapsed_ms=5, node_id="n1",
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.count_variants(region=Region("chr1", 100, 200))
        warning_types = [x.category for x in w]
        assert DnaerysIncompleteResultWarning in warning_types

    def test_streaming_affected_warning(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=1, affected=True),
        ]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            stream = client.select_variants(region=Region("chr1", 100, 200))
            stream.to_list()
        warning_types = [x.category for x in w]
        assert DnaerysIncompleteResultWarning in warning_types

    def test_streaming_affected_warning_once(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=1, affected=True),
            make_alleles_response(n_variants=1, affected=True),
            make_alleles_response(n_variants=1, affected=True),
        ]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            stream = client.select_variants(region=Region("chr1", 100, 200))
            stream.to_list()
        inc_warnings = [x for x in w if x.category is DnaerysIncompleteResultWarning]
        assert len(inc_warnings) == 1

    def test_unary_incomplete_not_affected_no_warning(self, client, fake_servicer):
        fake_servicer.count_response = pb2.CountAllelesResponse(
            count=5, incomplete_cluster=True, affected=False,
            elapsed_ms=5, node_id="n1",
        )
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            client.count_variants(region=Region("chr1", 100, 200))
        warning_types = [x.category for x in w]
        assert DnaerysIncompleteResultWarning not in warning_types


# ---------------------------------------------------------------------------
# Timeout
# ---------------------------------------------------------------------------


class TestTimeout:
    def test_timeout_raises_connection_error(self, fake_servicer, grpc_server):
        _, port, _ = grpc_server
        fake_servicer.sleep_seconds = 5.0
        with DnaerysClient(f"localhost:{port}", tls=False, default_timeout=0.1) as c:
            with pytest.raises(DnaerysConnectionError):
                c.count_variants(region=Region("chr1", 100, 200))


# ---------------------------------------------------------------------------
# Error propagation
# ---------------------------------------------------------------------------


class TestErrorPropagation:
    def test_invalid_argument_raises_invalid_request(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.INVALID_ARGUMENT
        with pytest.raises(DnaerysInvalidRequestError):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_unavailable_raises_connection_error(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.UNAVAILABLE
        with pytest.raises(DnaerysConnectionError):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_unauthenticated_raises_auth_error(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.UNAUTHENTICATED
        with pytest.raises(DnaerysAuthenticationError):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_not_found_raises_not_found_error(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.NOT_FOUND
        with pytest.raises(DnaerysNotFoundError):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_internal_raises_server_error(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.INTERNAL
        with pytest.raises(DnaerysServerError):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_resource_exhausted_raises_resource_exhausted(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.RESOURCE_EXHAUSTED
        with pytest.raises(DnaerysResourceExhausted):
            client.count_variants(region=Region("chr1", 100, 200))

    def test_error_chaining(self, client, fake_servicer):
        fake_servicer.error_to_raise = grpc.StatusCode.INTERNAL
        with pytest.raises(DnaerysServerError) as exc_info:
            client.count_variants(region=Region("chr1", 100, 200))
        assert exc_info.value.__cause__ is not None


# ---------------------------------------------------------------------------
# Connection lifecycle
# ---------------------------------------------------------------------------


class TestConnectionLifecycle:
    def test_context_manager(self, fake_servicer, grpc_server):
        _, port, _ = grpc_server
        with DnaerysClient(f"localhost:{port}", tls=False) as c:
            result = c.health()
            assert result.status == "SERVING"

    def test_close(self, fake_servicer, grpc_server):
        _, port, _ = grpc_server
        c = DnaerysClient(f"localhost:{port}", tls=False)
        result = c.health()
        assert result.status == "SERVING"
        c.close()

    def test_tls_false(self, fake_servicer, grpc_server):
        _, port, _ = grpc_server
        with DnaerysClient(f"localhost:{port}", tls=False) as c:
            assert c.health().status == "SERVING"


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


class TestValidation:
    def test_select_variants_no_location_raises(self, client, fake_servicer):
        with pytest.raises(DnaerysInvalidRequestError):
            client.select_variants()

    def test_select_variants_with_stats_single_region(self, client, fake_servicer):
        stream = client.select_variants_with_stats(region=Region("chr1", 100, 200))
        assert isinstance(stream, VariantWithStatsStream)
        variants = stream.to_list()
        assert len(variants) == 2

    def test_kinship_degree_and_threshold_raises(self, client, fake_servicer):
        with pytest.raises(DnaerysInvalidRequestError, match="mutually exclusive"):
            client.kinship(
                cohort_name="test", degree="FIRST_DEGREE", threshold=0.1,
            )

    def test_prs_no_cohort_no_samples_raises(self, client, fake_servicer):
        with pytest.raises(DnaerysInvalidRequestError, match="at least one"):
            client.prs(prs_name="PRS001")

    def test_default_hom_het_sent_to_server(self, client, fake_servicer):
        client.count_variants(region=Region("chr1", 100, 200))
        request = fake_servicer.last_request
        assert request.hom is True
        assert request.het is True


# ---------------------------------------------------------------------------
# Strong limit enforcement
# ---------------------------------------------------------------------------


class TestStrongLimit:
    def test_select_variants_limit_caps_results(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=5),
        ]
        stream = client.select_variants(
            region=Region("chr1", 100, 200), limit=1,
        )
        assert len(stream.to_list()) == 1

    def test_select_variants_limit_none_yields_all(self, client, fake_servicer):
        fake_servicer.variant_chunks = [
            make_alleles_response(n_variants=5),
        ]
        stream = client.select_variants(
            region=Region("chr1", 100, 200), limit=None,
        )
        assert len(stream.to_list()) == 5

    def test_select_variants_with_stats_limit_caps_results(self, client, fake_servicer):
        fake_servicer.variant_with_stats_chunks = [
            make_alleles_with_stats_response(n_variants=5),
        ]
        stream = client.select_variants_with_stats(
            regions=[Region("chr1", 100, 200)], limit=2,
        )
        assert len(stream.to_list()) == 2


# ---------------------------------------------------------------------------
# Skip removal — TypeError when passing skip= to public methods
# ---------------------------------------------------------------------------


class TestSkipRemoval:
    def test_select_variants_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.select_variants(
                region=Region("chr1", 100, 200), skip=5,
            )

    def test_select_variants_with_stats_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.select_variants_with_stats(
                regions=[Region("chr1", 100, 200)], skip=5,
            )

    def test_count_samples_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.count_samples(
                region=Region("chr1", 100, 200), skip=1,
            )

    def test_count_samples_rejects_limit(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.count_samples(
                region=Region("chr1", 100, 200), limit=1,
            )

    def test_select_de_novo_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.select_de_novo(
                parent1="P1", parent2="P2", proband="C1",
                region=Region("chr1", 100, 200), skip=5,
            )

    def test_select_het_dominant_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.select_het_dominant(
                affected_parent="AP", unaffected_parent="UP",
                affected_child="AC",
                region=Region("chr1", 100, 200), skip=5,
            )

    def test_select_hom_recessive_rejects_skip(self, client, fake_servicer):
        with pytest.raises(TypeError):
            client.select_hom_recessive(
                unaffected_parent1="UP1", unaffected_parent2="UP2",
                affected_child="AC",
                region=Region("chr1", 100, 200), skip=5,
            )


# ---------------------------------------------------------------------------
# Inheritance pagination
# ---------------------------------------------------------------------------


class TestInheritancePagination:
    def test_paginate_de_novo_returns_paginated_query(self, client, fake_servicer):
        q = client.paginate_de_novo(
            page_size=10,
            parent1="P1", parent2="P2", proband="C1",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(q, PaginatedQuery)

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
        assert len(page.variants) == 2
        assert page.page_number == 1

    def test_paginate_het_dominant_returns_paginated_query(self, client, fake_servicer):
        q = client.paginate_het_dominant(
            page_size=10,
            affected_parent="AP", unaffected_parent="UP",
            affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(q, PaginatedQuery)

    def test_paginate_hom_recessive_returns_paginated_query(self, client, fake_servicer):
        q = client.paginate_hom_recessive(
            page_size=10,
            unaffected_parent1="UP1", unaffected_parent2="UP2",
            affected_child="AC",
            region=Region("chr1", 100, 200),
        )
        assert isinstance(q, PaginatedQuery)

    def test_paginate_variants_with_stats_returns_paginated_query(self, client, fake_servicer):
        q = client.paginate_variants_with_stats(
            page_size=10,
            regions=[Region("chr1", 100, 200)],
        )
        assert isinstance(q, PaginatedQuery)

    def test_paginate_variants_with_stats_first_page(self, client, fake_servicer):
        fake_servicer.variant_with_stats_chunks = [
            make_alleles_with_stats_response(n_variants=4),
        ]
        q = client.paginate_variants_with_stats(
            page_size=2,
            regions=[Region("chr1", 100, 200)],
        )
        page = q.next_page()
        assert len(page.variants) == 2
        assert page.page_number == 1
