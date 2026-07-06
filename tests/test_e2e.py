"""End-to-end tests against a live Dnaerys cluster.

All tests are decorated with @pytest.mark.e2e and are skipped by default.
Run with: pytest tests/test_e2e.py -m e2e

The target server is read from the DNAERYS_HOST environment variable
(default: db.dnaerys.org:443, TLS enabled).
"""

import os

import pytest

from dnaerys import DnaerysClient, Region

# A region owned by a single ring whose variant count far exceeds the server-side
# per-ring cap, so its (capped) payload must be *relayed* between rings — this is
# what exercised the Akka Remote message-size defect (Artery/TCP -> Aeron/UDP).
# The count must stay >> the cap: if the cap were ever removed, the uncapped
# relayed payload would be oversized again, which is the regression this guards.
_RELAY_REGION = ("chr1", 1, 1_000_000)
# Enough calls that the load balancer round-robins across rings (the test skips
# if fewer than two rings are sampled). Each call's payload is server-capped, so
# this is by far the heaviest e2e download (~5000 variants x _RELAY_CALLS).
_RELAY_CALLS = 24
# ...which is why the relay test is OPT-IN: it is skipped by default (even under
# -m e2e) and only runs when DNAERYS_RUN_RELAY_TEST is set. Run it before a
# release, e.g.: DNAERYS_RUN_RELAY_TEST=1 pytest tests/test_e2e.py -m e2e
_RUN_RELAY = os.environ.get("DNAERYS_RUN_RELAY_TEST", "").lower() in ("1", "true", "yes")

# A SMALL region straddling the ring0/ring1 boundary (ring0 ends chr2:124139668,
# ring1 starts chr2:124139721), so it is owned by TWO rings with no duplication.
# ~150 variants (well under the per-ring cap) — deliberately tiny so the
# cross-ring pagination/limit regression tests below stay cheap for downstream
# CI, while still exercising the multi-owner relay+merge path.
_MULTI_RING_REGION = ("chr2", 124_139_000, 124_140_500)
_MULTI_RING_SPLIT = (124_139_668, 124_139_721)  # last ring0 pos, first ring1 pos


@pytest.fixture(scope="module")
def e2e_client():
    host = os.environ.get("DNAERYS_HOST", "db.dnaerys.org:443")
    with DnaerysClient(host) as client:
        yield client


@pytest.mark.e2e
def test_e2e_health(e2e_client):
    result = e2e_client.health()
    assert result.status, "Expected a non-empty health status string"


@pytest.mark.e2e
def test_e2e_cluster_nodes(e2e_client):
    result = e2e_client.cluster_nodes()
    assert len(result.active_nodes) >= 1, "Expected at least 1 active node"
    assert result.total_nodes >= 1


@pytest.mark.e2e
def test_e2e_dataset_info(e2e_client):
    result = e2e_client.dataset_info()
    assert result.samples_total > 0, "Expected samples_total > 0"
    assert len(result.cohorts) >= 1, "Expected at least 1 cohort"
    assert result.assembly is not None


@pytest.mark.e2e
def test_e2e_select_variants(e2e_client):
    region = Region("chr1", 1, 1_000_000)
    # limit keeps the download small; this test only checks shape, not volume.
    variants = e2e_client.select_variants(region=region, limit=100).to_list()
    assert len(variants) > 0, "Expected variants in chr1:1-1000000"
    v = variants[0]
    assert v.chr is not None
    assert v.start >= 1
    assert v.ref


@pytest.mark.e2e
@pytest.mark.skipif(
    not _RUN_RELAY,
    reason="heavy cross-ring relay test (~5000 variants/call); "
           "set DNAERYS_RUN_RELAY_TEST=1 to run",
)
def test_e2e_select_variants_consistent_across_rings(e2e_client):
    """Streaming ``select_variants`` must return the SAME non-empty result no
    matter which ring the load balancer routes each call to.

    Regression test for the Akka Remote defect (Artery/TCP -> Aeron/UDP) where
    oversized *relayed* variant payloads were silently discarded: a region owned
    by one ring returned data only when a call happened to land on that ring, and
    an empty stream from every peer. ``count`` was unaffected (it relays a small
    aggregate, not the payload) — that asymmetry is the tell. With the server-side
    per-ring cap the result is capped, but it must be identical from every ring.

    The k8s Service round-robins each RPC to a different ring, so we issue many
    calls, record the responding ring(s) from the response metadata, and assert
    every ring returns the same, non-empty size.
    """
    chrom, start, end = _RELAY_REGION
    region = Region(chrom, start, end)

    sizes: list[int] = []
    sizes_by_ring: dict[str, set[int]] = {}
    rings_seen: set[str] = set()
    for _ in range(_RELAY_CALLS):
        stream = e2e_client.select_variants(region=region)
        n = len(stream.to_list())
        sizes.append(n)
        # metadata.node_id is a comma-joined set of every ring that stamped a
        # chunk (the owner ring(s) plus the receiving ring); split to per-ring.
        for ring in filter(None, stream.metadata.node_id.split(",")):
            rings_seen.add(ring)
            sizes_by_ring.setdefault(ring, set()).add(n)

    # Guard against a false pass: if routing never left a single ring, the
    # cross-ring relay path was not exercised, so the result is inconclusive.
    if len(rings_seen) < 2:
        pytest.skip(
            f"routing only reached {sorted(rings_seen)} in {_RELAY_CALLS} calls; "
            "cannot test cross-ring relay consistency"
        )

    detail = {r: sorted(v) for r, v in sorted(sizes_by_ring.items())}
    # The classic failure: some ring(s) return an empty stream while others don't.
    assert min(sizes) > 0, (
        f"select_variants returned an EMPTY stream from some ring(s) for "
        f"{chrom}:{start}-{end} — cross-ring relay regression "
        f"(payload discarded / not forwarded). per-ring sizes={detail}"
    )
    # And every ring must agree on the (capped) size.
    assert len(set(sizes)) == 1, (
        f"select_variants returned inconsistent sizes across rings for "
        f"{chrom}:{start}-{end} — relay/truncation regression. "
        f"sizes={sorted(set(sizes))}; per-ring sizes={detail}"
    )


@pytest.mark.e2e
def test_e2e_paginate_across_rings_complete(e2e_client):
    """``paginate_variants`` must return EVERY variant of a region owned by two
    rings — no gaps, no duplicates.

    Regression for the per-ring cap (R1.20.0): ``skip``/``limit`` are per ring,
    so a refill that kept only ``buffer_size`` variants would discard the second
    ring's window every page. Here ``buffer_size`` is deliberately smaller than
    each ring's share, forcing multiple relayed round-trips; a broken refill
    would drop one ring and the unique count would fall short of ``count``.
    """
    chrom, start, end = _MULTI_RING_REGION
    lo, hi = _MULTI_RING_SPLIT
    region = Region(chrom, start, end)

    total = e2e_client.count_variants(region=region).count
    ring0 = e2e_client.count_variants(region=Region(chrom, start, lo)).count
    ring1 = e2e_client.count_variants(region=Region(chrom, hi, end)).count
    # Guard: the region must actually straddle the boundary, else this is not a
    # cross-ring test (the dataset's partitioning may have shifted).
    assert ring0 > 0 and ring1 > 0, (
        f"{chrom}:{start}-{end} no longer spans both rings "
        f"(ring0={ring0}, ring1={ring1}); choose a region across the boundary"
    )
    assert total == ring0 + ring1

    seen: set[tuple] = set()
    dups = 0
    # Per-ring window (buffer_size) < each ring's share; page_size > buffer_size.
    for page in e2e_client.paginate_variants(
        region=region, page_size=50, buffer_size=20,
    ):
        for v in page.variants:
            key = (int(v.chr), v.start, v.ref, v.alt)
            if key in seen:
                dups += 1
            seen.add(key)

    assert dups == 0, f"pagination returned {dups} duplicate variants across rings"
    assert len(seen) == total, (
        f"pagination returned {len(seen)}/{total} unique variants "
        f"(ring0={ring0}, ring1={ring1}) — cross-ring completeness regression"
    )


@pytest.mark.e2e
def test_e2e_select_variants_limit_across_rings(e2e_client):
    """A global ``limit`` on a two-ring region must merge both rings and cap
    exactly: a ``limit`` above the total returns everything (both rings), and a
    smaller ``limit`` returns exactly that many."""
    chrom, start, end = _MULTI_RING_REGION
    region = Region(chrom, start, end)
    total = e2e_client.count_variants(region=region).count
    assert total > 2, "need several variants across the boundary for this test"

    all_v = e2e_client.select_variants(region=region, limit=total + 50).to_list()
    assert len(all_v) == total, (
        f"limit>total returned {len(all_v)}/{total} — a ring was dropped"
    )

    k = total // 2
    capped = e2e_client.select_variants(region=region, limit=k).to_list()
    assert len(capped) == k, f"global limit not honoured: got {len(capped)}, want {k}"


@pytest.mark.e2e
def test_e2e_count_variants(e2e_client):
    region = Region("chr1", 1, 1_000_000)
    result = e2e_client.count_variants(region=region)
    assert result.count > 0, "Expected count > 0 for chr1:1-1000000"


@pytest.mark.e2e
def test_e2e_select_variants_with_stats(e2e_client):
    region = Region("chr1", 1, 1_000_000)
    stream = e2e_client.select_variants_with_stats(
        regions=[region], samples=["__nonexistent_sample__"],
    )
    variants = stream.to_list()
    # Even with a nonexistent sample, the structure should be correct.
    # If variants are returned, stats fields should be populated.
    if variants:
        v = variants[0]
        assert hasattr(v, "phwe")
        assert hasattr(v, "pchi2")
        assert hasattr(v, "odds_ratio")
        assert hasattr(v, "ibc")


@pytest.mark.e2e
def test_e2e_select_samples(e2e_client):
    region = Region("chr1", 1, 1_000_000)
    result = e2e_client.select_samples(region=region)
    assert len(result.samples) > 0, "Expected samples in chr1:1-1000000"
    assert isinstance(result.samples[0], str)


@pytest.mark.e2e
def test_e2e_count_samples(e2e_client):
    region = Region("chr1", 1, 1_000_000)
    result = e2e_client.count_samples(region=region)
    assert result.count > 0, "Expected sample count > 0 for chr1:1-1000000"


@pytest.mark.e2e
def test_e2e_select_samples_hom_ref(e2e_client):
    from dnaerys import Chromosome, SamplesResult

    result = e2e_client.select_samples_hom_ref(chr=Chromosome.CHR1, position=100_000)
    assert isinstance(result, SamplesResult)
    assert isinstance(result.samples, tuple)


@pytest.mark.e2e
def test_e2e_to_dataframe(e2e_client):
    pd = pytest.importorskip("pandas")
    region = Region("chr1", 1, 1_000_000)
    stream = e2e_client.select_variants(region=region, limit=100)
    df = stream.to_dataframe()

    expected_columns = {
        "chr", "start", "end", "ref", "alt", "af", "ac", "an",
        "hom_samples", "het_samples", "mis_samples",
        "hom_samples_fx", "het_samples_fx", "mis_samples_fx",
        "hom_samples_mxy", "het_samples_mxy", "mis_samples_mxy",
        "gnomad_exomes_af", "gnomad_genomes_af", "cadd_raw", "cadd_phred",
        "am_score", "amino_acids", "biallelic",
    }
    assert expected_columns.issubset(set(df.columns)), (
        f"Missing columns: {expected_columns - set(df.columns)}"
    )
    assert len(df) > 0, "Expected non-empty DataFrame"
