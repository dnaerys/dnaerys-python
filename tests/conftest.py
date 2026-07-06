"""Fake gRPC server fixtures and test factories for Stage 3 integration tests."""

from __future__ import annotations

import time
from concurrent import futures

import grpc
import pytest

from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._proto import dnaerys_pb2_grpc
from dnaerys import DnaerysClient


# ---------------------------------------------------------------------------
# Proto test factories
# ---------------------------------------------------------------------------


def make_variant_proto(**overrides) -> pb2.Variant:
    """Create a pb2.Variant with sensible defaults.  Override any field via kwargs."""
    defaults = {
        "chr": pb2.CHR1,
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
        "hom_samples_mxy": 0,
        "het_samples_mxy": 0,
        "mis_samples_mxy": 0,
        "gnomADe": 0.01,
        "gnomADg": 0.02,
        "cadd_raw": 1.5,
        "cadd_phred": 10.0,
        "am_score": 0.3,
        "amino_acids": "",
        "biallelic": True,
    }
    defaults.update(overrides)
    return pb2.Variant(**defaults)


def make_variant_with_stats_proto(**overrides) -> pb2.VariantWithStats:
    """Create a pb2.VariantWithStats with sensible defaults."""
    variant_overrides = {}
    stats_overrides = {}
    variant_keys = {
        "chr", "start", "end", "ref", "alt", "af", "ac", "an",
        "hom_samples", "het_samples", "mis_samples",
        "hom_samples_fx", "het_samples_fx", "mis_samples_fx",
        "hom_samples_mxy", "het_samples_mxy", "mis_samples_mxy",
        "gnomADe", "gnomADg", "cadd_raw", "cadd_phred", "am_score",
        "amino_acids", "biallelic",
    }
    for k, v in overrides.items():
        if k in variant_keys:
            variant_overrides[k] = v
        else:
            stats_overrides[k] = v
    defaults = {
        "variant": make_variant_proto(**variant_overrides),
        "vaf": 0.5,
        "vac": 1.0,
        "van": 2,
        "v_hom_samples": 0,
        "v_het_samples": 1,
        "v_hom_samples_fx": 0,
        "v_het_samples_fx": 0,
        "v_hom_samples_mxy": 0,
        "v_het_samples_mxy": 0,
        "phwe": 1.0,
        "pchi2": 0.5,
        "ibc": 0.0,
    }
    defaults.update(stats_overrides)
    return pb2.VariantWithStats(**defaults)


def make_alleles_response(n_variants=2, **meta_overrides) -> pb2.AllelesResponse:
    """Create a pb2.AllelesResponse with *n_variants* default variants."""
    defaults = {
        "incomplete_cluster": False,
        "affected": False,
        "elapsed_ms": 10,
        "elapsed_db_ms": 5,
        "node_id": "node-1",
    }
    defaults.update(meta_overrides)
    variants = [
        make_variant_proto(start=100 + i, end=100 + i)
        for i in range(n_variants)
    ]
    return pb2.AllelesResponse(variants=variants, **defaults)


def make_alleles_with_stats_response(n_variants=2, **meta_overrides) -> pb2.AllelesWithStatsResponse:
    """Create a pb2.AllelesWithStatsResponse with *n_variants* default variants."""
    defaults = {
        "incomplete_cluster": False,
        "affected": False,
        "elapsed_ms": 10,
        "elapsed_db_ms": 5,
        "node_id": "node-1",
    }
    defaults.update(meta_overrides)
    variants = [
        make_variant_with_stats_proto(start=100 + i, end=100 + i)
        for i in range(n_variants)
    ]
    return pb2.AllelesWithStatsResponse(variants=variants, **defaults)


# ---------------------------------------------------------------------------
# Fake servicer
# ---------------------------------------------------------------------------


class FakeDnaerysServicer(dnaerys_pb2_grpc.DnaerysServiceServicer):
    """In-process gRPC servicer with canned responses for testing.

    Attributes can be set per-test to customise behaviour:
      - variant_chunks: list of AllelesResponse to yield for select RPCs
      - variant_with_stats_chunks: list for stats RPCs
      - count_response: CountAllelesResponse for count variant RPCs
      - samples_response: SamplesResponse
      - count_samples_response: CountSamplesResponse
      - health_response: HealthResponse
      - cluster_nodes_response: ClusterNodesResponse
      - dataset_info_response: DatasetInfoResponse
      - prs_response: PRSResponse
      - sex_mismatch_response: SexMismatchResponse
      - fstat_x_response: FstatXResponse
      - kinship_response: KinshipResponse
      - sample_kinship_response: SampleKinshipResponse
      - top_hwe_response: AllelesWithStatsResponse
      - top_chi2_response: AllelesWithStatsResponse
      - error_to_raise: grpc.StatusCode | None
      - sleep_seconds: float | None
      - last_request: stores the last request proto received
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        """Reset all canned responses to defaults."""
        self.variant_chunks: list[pb2.AllelesResponse] = [
            make_alleles_response(n_variants=2),
        ]
        self.variant_with_stats_chunks: list[pb2.AllelesWithStatsResponse] = [
            make_alleles_with_stats_response(n_variants=2),
        ]
        # Ring-simulation mode: when `rings`/`stats_rings` is set, streaming RPCs
        # honour the request's per-ring `skip`/`limit` and the server `ring_cap`,
        # modelling the real cluster (data partitioned across owner rings, no
        # duplication, each ring's response hard-capped). Used to test pagination
        # completeness and strong-limit batching. `None` -> static-chunk mode.
        self.rings: list[list[pb2.Variant]] | None = None
        self.stats_rings: list[list[pb2.VariantWithStats]] | None = None
        self.ring_cap: int | None = None
        self.chunk_size: int = 50
        self.count_response = pb2.CountAllelesResponse(
            count=42, elapsed_ms=5, elapsed_db_ms=2, node_id="node-1",
        )
        self.samples_response = pb2.SamplesResponse(
            samples=["SAMPLE_A", "SAMPLE_B"],
            elapsed_ms=5, elapsed_db_ms=2, node_id="node-1",
        )
        self.count_samples_response = pb2.CountSamplesResponse(
            count=10, elapsed_ms=5, elapsed_db_ms=2, node_id="node-1",
        )
        self.health_response = pb2.HealthResponse(status="SERVING")
        self.cluster_nodes_response = pb2.ClusterNodesResponse(
            active_nodes=["node-1", "node-2"],
            inactive_nodes=[],
            total_nodes=2,
            elapsed_ms=1,
        )
        self.dataset_info_response = pb2.DatasetInfoResponse(
            cohorts=[pb2.Cohort(cohort_name="test-cohort", samples_count=100)],
            samples_total=100,
            females_total=50,
            males_total=50,
            variants_total=1000,
            assembly=pb2.GRCh38,
            rto=False,
            prs=[pb2.PRS(name="PRS001", desc="test PRS", cardinality=50)],
            timestamp="2024-01-01T00:00:00Z",
            data_format=1,
            notes="test",
            rings_total=4,
            elapsed_ms=10,
            node_id="node-1",
        )
        self.prs_response = pb2.PRSResponse(
            prs_name="PRS001",
            sample_scores=[pb2.SampleScore(sample="S1", scores_sum=1.5)],
            dominant=False,
            recessive=False,
            prs_cardinality=50,
            elapsed_ms=5,
            node_id="node-1",
        )
        self.sex_mismatch_response = pb2.SexMismatchResponse(
            mismatch_males=[],
            mismatch_females=[],
            elapsed_ms=5,
            node_id="node-1",
        )
        self.fstat_x_response = pb2.FstatXResponse(
            males=[pb2.SampleStat(sample="M1", f_stat=0.9)],
            females=[pb2.SampleStat(sample="F1", f_stat=0.1)],
            elapsed_ms=5,
            node_id="node-1",
        )
        self.kinship_response = pb2.KinshipResponse(
            rel=[pb2.Relatedness(
                sample1="S1", sample2="S2",
                degree=pb2.FIRST_DEGREE, phi_bwf=0.25,
            )],
            elapsed_ms=5,
            node_id="node-1",
        )
        self.sample_kinship_response = pb2.SampleKinshipResponse(
            rel=[],
            accepted_snvs=1000,
            elapsed_ms=5,
            node_id="node-1",
        )
        self.top_hwe_response = make_alleles_with_stats_response(n_variants=1)
        self.top_chi2_response = make_alleles_with_stats_response(n_variants=1)
        self.error_to_raise: grpc.StatusCode | None = None
        self.sleep_seconds: float | None = None
        self.last_request = None

    def _maybe_error_or_sleep(self, context):
        if self.sleep_seconds:
            time.sleep(self.sleep_seconds)
        if self.error_to_raise is not None:
            context.abort(self.error_to_raise, "test error")

    # -- Infrastructure --

    def Health(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.health_response

    def ClusterNodes(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.cluster_nodes_response

    def DatasetInfo(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.dataset_info_response

    # -- Ring-simulation helpers --

    def configure_rings(self, ring_sizes, *, cap=None, chunk_size=50, start_base=1000):
        """Populate per-owner-ring variant partitions honouring skip/limit/cap.

        ``ring_sizes[i]`` variants go to ring ``i``; every variant gets a
        globally-unique ``start`` (disjoint ranges per ring) so callers can
        detect gaps/duplicates by inspecting the set of returned ``start``
        positions.  ``cap`` is the server per-ring hard limit and is also
        advertised through ``dataset_info`` so the client discovers it.
        """
        self.ring_cap = cap
        self.chunk_size = chunk_size
        self.rings = []
        pos = start_base
        for size in ring_sizes:
            self.rings.append(
                [make_variant_proto(start=pos + j, end=pos + j) for j in range(size)]
            )
            pos += size + 10  # keep each ring's start range disjoint
        if cap is not None:
            self.dataset_info_response.max_variants_per_ring = cap

    def configure_stats_rings(self, ring_sizes, *, cap=None, chunk_size=50, start_base=1000):
        """Like :meth:`configure_rings` but for the with-stats streaming path."""
        self.ring_cap = cap
        self.chunk_size = chunk_size
        self.stats_rings = []
        pos = start_base
        for size in ring_sizes:
            self.stats_rings.append(
                [make_variant_with_stats_proto(start=pos + j, end=pos + j) for j in range(size)]
            )
            pos += size + 10
        if cap is not None:
            self.dataset_info_response.max_variants_per_ring = cap

    def _window_bounds(self, request):
        """Return (skip, window) applying the request limit and the server cap."""
        skip = getattr(request, "skip", 0) or 0
        req_limit = getattr(request, "limit", 0) or 0
        window = req_limit if req_limit and req_limit > 0 else (1 << 31) - 1
        if self.ring_cap is not None:
            window = min(window, self.ring_cap)
        return skip, window

    def _yield_ring_chunks(self, request, rings, response_cls):
        """Yield per-ring windowed chunks + a terminal empty (receiver) chunk."""
        skip, window = self._window_bounds(request)
        for ring_idx, ring in enumerate(rings):
            win = ring[skip:skip + window]
            for i in range(0, len(win), self.chunk_size):
                yield response_cls(
                    variants=win[i:i + self.chunk_size],
                    incomplete_cluster=False, affected=False,
                    elapsed_ms=10, elapsed_db_ms=5, node_id=f"ring-{ring_idx}",
                )
        # Terminal empty chunk stamped by the receiving ring (models the relay);
        # a batch that yields only this chunk signals all rings are exhausted.
        yield response_cls(
            variants=[], incomplete_cluster=False, affected=False,
            elapsed_ms=10, elapsed_db_ms=5, node_id="receiver",
        )

    # -- Variant streaming RPCs (yield from variant_chunks) --

    def _yield_variant_chunks(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        if self.rings is not None:
            yield from self._yield_ring_chunks(request, self.rings, pb2.AllelesResponse)
            return
        yield from self.variant_chunks

    def SelectVariantsInRegion(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectVariantsInRegionInSamples(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectVariantsInBracket(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectVariantsInBracketInSamples(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectVariantsInMultiRegions(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectVariantsInMultiRegionsInSamples(self, request, context):
        return self._yield_variant_chunks(request, context)

    # -- Variant with stats streaming RPCs --

    def _yield_variant_with_stats_chunks(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        if self.stats_rings is not None:
            yield from self._yield_ring_chunks(
                request, self.stats_rings, pb2.AllelesWithStatsResponse,
            )
            return
        yield from self.variant_with_stats_chunks

    def SelectVariantsInRegionInSamplesWithStats(self, request, context):
        return self._yield_variant_with_stats_chunks(request, context)

    def SelectVariantsInMultiRegionsWithStats(self, request, context):
        return self._yield_variant_with_stats_chunks(request, context)

    def SelectVariantsInMultiRegionsInSamplesWithStats(self, request, context):
        return self._yield_variant_with_stats_chunks(request, context)

    # -- Count variant RPCs --

    def _return_count(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.count_response

    def CountVariantsInRegion(self, request, context):
        return self._return_count(request, context)

    def CountVariantsInRegionInSamples(self, request, context):
        return self._return_count(request, context)

    def CountVariantsInBracket(self, request, context):
        return self._return_count(request, context)

    def CountVariantsInBracketInSamples(self, request, context):
        return self._return_count(request, context)

    def CountVariantsInMultiRegions(self, request, context):
        return self._return_count(request, context)

    def CountVariantsInMultiRegionsInSamples(self, request, context):
        return self._return_count(request, context)

    # -- Sample RPCs --

    def SelectSamplesInRegion(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.samples_response

    def CountSamplesInRegion(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.count_samples_response

    def SelectSamplesInMultiRegions(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.samples_response

    def CountSamplesInMultiRegions(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.count_samples_response

    def SelectSamplesHomReference(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.samples_response

    def CountSamplesHomReference(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.count_samples_response

    # -- Inheritance RPCs --

    def SelectDeNovo(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectHetDominant(self, request, context):
        return self._yield_variant_chunks(request, context)

    def SelectHomRecessive(self, request, context):
        return self._yield_variant_chunks(request, context)

    # -- Statistics RPCs --

    def TopNHWE(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.top_hwe_response

    def TopNchi2(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.top_chi2_response

    def Prs(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.prs_response

    def SexMismatchCheck(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.sex_mismatch_response

    def FstatX(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.fstat_x_response

    # -- Kinship RPCs --

    def Kinship(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.kinship_response

    def KinshipDuo(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.kinship_response

    def KinshipTrio(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.kinship_response

    def SampleKinship(self, request, context):
        self.last_request = request
        self._maybe_error_or_sleep(context)
        return self.sample_kinship_response


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_servicer_instance = FakeDnaerysServicer()


@pytest.fixture(scope="session")
def grpc_server():
    """Start an in-process gRPC server on a random localhost port.

    Returns (server, port, servicer) tuple.
    """
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    dnaerys_pb2_grpc.add_DnaerysServiceServicer_to_server(_servicer_instance, server)
    port = server.add_insecure_port("[::]:0")
    server.start()
    yield server, port, _servicer_instance
    server.stop(grace=0)


@pytest.fixture
def fake_servicer(grpc_server):
    """Return the FakeDnaerysServicer, reset to defaults for each test."""
    _, _, servicer = grpc_server
    servicer.reset()
    return servicer


@pytest.fixture
def client(grpc_server):
    """Return a DnaerysClient connected to the fake server (tls=False)."""
    _, port, _ = grpc_server
    with DnaerysClient(f"localhost:{port}", tls=False) as c:
        yield c
