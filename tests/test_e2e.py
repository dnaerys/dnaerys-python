"""End-to-end tests against a live Dnaerys cluster.

All tests are decorated with @pytest.mark.e2e and are skipped by default.
Run with: pytest tests/test_e2e.py -m e2e

The target server is read from the DNAERYS_HOST environment variable
(default: db.dnaerys.org:443, TLS enabled).
"""

import os

import pytest

from dnaerys import DnaerysClient, Region


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
    variants = e2e_client.select_variants(region=region).to_list()
    assert len(variants) > 0, "Expected variants in chr1:1-1000000"
    v = variants[0]
    assert v.chr is not None
    assert v.start >= 1
    assert v.ref


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

    result = e2e_client.select_samples_hom_ref(chr=Chromosome.CHR_1, position=100_000)
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
        "homc", "hetc", "misc", "homfc", "hetfc", "misfc",
        "gnomad_exomes_af", "gnomad_genomes_af", "cadd_raw", "cadd_phred",
        "am_score", "amino_acids", "biallelic",
    }
    assert expected_columns.issubset(set(df.columns)), (
        f"Missing columns: {expected_columns - set(df.columns)}"
    )
    assert len(df) > 0, "Expected non-empty DataFrame"
