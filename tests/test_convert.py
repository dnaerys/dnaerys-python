"""Tests for proto→dataclass and dataclass→proto conversion functions.

Each test constructs proto message objects directly using the generated
``dnaerys_pb2`` classes — no mocking of proto construction.
"""

from __future__ import annotations

from dnaerys._convert import (
    annotation_filter_to_proto,
    convert_alleles_with_stats_response_to_top_chi2,
    convert_alleles_with_stats_response_to_top_hwe,
    convert_cluster_nodes_response,
    convert_cohort,
    convert_count_alleles_response,
    convert_count_samples_response,
    convert_dataset_info_response,
    convert_fstat_x_response,
    convert_health_response,
    convert_kinship_response,
    convert_prs_info,
    convert_prs_response,
    convert_relatedness,
    convert_response_metadata,
    convert_sample_kinship_response,
    convert_sample_relatedness,
    convert_sample_score,
    convert_sample_stat,
    convert_samples_response,
    convert_sex_mismatch_response,
    convert_variant,
    convert_variant_with_stats,
)
from dnaerys._enums import (
    AlphaMissense,
    Chromosome,
    Consequence,
    Impact,
    KinshipDegree,
    RefAssembly,
    VariantType,
)
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._types import (
    AnnotationFilter,
    ClusterNodesResult,
    Cohort,
    CountResult,
    DatasetInfo,
    FstatXResult,
    HealthResult,
    KinshipResult,
    PrsInfo,
    PrsResult,
    Relatedness,
    ResponseMetadata,
    SampleKinshipResult,
    SampleRelatedness,
    SampleScore,
    SamplesResult,
    SampleStat,
    SexMismatchResult,
    TopChi2Result,
    TopHweResult,
    Variant,
    VariantWithStats,
)


# ---------------------------------------------------------------------------
# Variant conversion
# ---------------------------------------------------------------------------


class TestConvertVariant:
    def test_convert_variant_basic(self):
        proto = pb2.Variant(
            chr=1,
            start=100,
            end=100,
            ref="A",
            alt="T",
            af=0.5,
            ac=1.0,
            an=2,
            homc=0,
            hetc=1,
            misc=0,
            homfc=0,
            hetfc=0,
            misfc=0,
            gnomADe=0.1,
            gnomADg=0.2,
            cadd_raw=3.5,
            cadd_phred=15.0,
            am_score=0.8,
            amino_acids="A/V",
            biallelic=True,
        )
        v = convert_variant(proto)
        assert isinstance(v, Variant)
        assert v.chr == Chromosome.CHR_1
        assert v.start == 100
        assert v.end == 100
        assert v.ref == "A"
        assert v.alt == "T"
        assert v.af == 0.5
        assert v.ac == 1.0
        assert v.an == 2
        assert v.homc == 0
        assert v.hetc == 1
        assert v.misc == 0
        assert v.homfc == 0
        assert v.hetfc == 0
        assert v.misfc == 0
        assert abs(v.gnomad_exomes_af - 0.1) < 1e-6
        assert abs(v.gnomad_genomes_af - 0.2) < 1e-6
        assert abs(v.cadd_raw - 3.5) < 1e-6
        assert abs(v.cadd_phred - 15.0) < 1e-6
        assert abs(v.am_score - 0.8) < 1e-6
        assert v.amino_acids == "A/V"
        assert v.biallelic is True

    def test_convert_variant_chromosome_is_enum(self):
        proto = pb2.Variant(chr=23, start=1, end=1, ref="G", alt="C")
        v = convert_variant(proto)
        assert isinstance(v.chr, Chromosome)
        assert v.chr == Chromosome.CHR_X

    def test_convert_variant_gnomad_field_mapping(self):
        proto = pb2.Variant(
            chr=1, start=1, end=1, ref="A", alt="T",
            gnomADe=0.5, gnomADg=0.3,
        )
        v = convert_variant(proto)
        assert abs(v.gnomad_exomes_af - 0.5) < 1e-6
        assert abs(v.gnomad_genomes_af - 0.3) < 1e-6

    def test_convert_variant_zero_annotation_fields(self):
        proto = pb2.Variant(
            chr=1, start=1, end=1, ref="A", alt="T",
            gnomADe=0.0, gnomADg=0.0, cadd_raw=0.0, cadd_phred=0.0, am_score=0.0,
        )
        v = convert_variant(proto)
        assert v.gnomad_exomes_af == 0.0
        assert v.gnomad_genomes_af == 0.0
        assert v.cadd_raw == 0.0
        assert v.cadd_phred == 0.0
        assert v.am_score == 0.0


# ---------------------------------------------------------------------------
# VariantWithStats conversion
# ---------------------------------------------------------------------------


class TestConvertVariantWithStats:
    def _make_proto(self, **overrides):
        variant_kwargs = {
            "chr": 1, "start": 200, "end": 200, "ref": "G", "alt": "C",
            "af": 0.3, "ac": 2.0, "an": 6, "homc": 1, "hetc": 2,
            "misc": 0, "homfc": 0, "hetfc": 1, "misfc": 0,
            "gnomADe": 0.15, "gnomADg": 0.25,
            "cadd_raw": 1.5, "cadd_phred": 10.0, "am_score": 0.6,
            "amino_acids": "R/Q", "biallelic": True,
        }
        stats_kwargs = {
            "vaf": 0.4, "vac": 1.5, "van": 4, "vhomc": 0, "vhetc": 1,
            "vhomfc": 0, "vhetfc": 0,
            "phwe": 0.05, "pchi2": 0.01, "ibc": 0.02,
        }
        # The 'or' field must be set via **kwargs
        or_val = overrides.pop("or_val", 1.5)
        stats_kwargs.update(overrides)
        return pb2.VariantWithStats(
            variant=pb2.Variant(**variant_kwargs),
            **stats_kwargs,
            **{"or": or_val},
        )

    def test_convert_variant_with_stats_flattened(self):
        proto = self._make_proto()
        v = convert_variant_with_stats(proto)
        # Variant fields are flattened — accessible directly, not via .variant
        assert v.chr == Chromosome.CHR_1
        assert v.start == 200
        assert v.ref == "G"
        assert v.alt == "C"

    def test_convert_variant_with_stats_all_fields(self):
        proto = self._make_proto()
        v = convert_variant_with_stats(proto)
        assert isinstance(v, VariantWithStats)
        # All 21 variant fields
        assert v.chr == Chromosome.CHR_1
        assert v.start == 200
        assert v.end == 200
        assert v.ref == "G"
        assert v.alt == "C"
        assert abs(v.af - 0.3) < 1e-6
        assert abs(v.ac - 2.0) < 1e-6
        assert v.an == 6
        assert v.homc == 1
        assert v.hetc == 2
        assert v.misc == 0
        assert v.homfc == 0
        assert v.hetfc == 1
        assert v.misfc == 0
        assert abs(v.gnomad_exomes_af - 0.15) < 1e-6
        assert abs(v.gnomad_genomes_af - 0.25) < 1e-6
        assert abs(v.cadd_raw - 1.5) < 1e-6
        assert abs(v.cadd_phred - 10.0) < 1e-6
        assert abs(v.am_score - 0.6) < 1e-6
        assert v.amino_acids == "R/Q"
        assert v.biallelic is True
        # 11 stats fields
        assert abs(v.vaf - 0.4) < 1e-6
        assert abs(v.vac - 1.5) < 1e-6
        assert v.van == 4
        assert v.vhomc == 0
        assert v.vhetc == 1
        assert v.vhomfc == 0
        assert v.vhetfc == 0
        assert abs(v.phwe - 0.05) < 1e-6
        assert abs(v.pchi2 - 0.01) < 1e-6
        assert abs(v.odds_ratio - 1.5) < 1e-6
        assert abs(v.ibc - 0.02) < 1e-6

    def test_convert_variant_with_stats_odds_ratio_mapping(self):
        # Verify proto field 'or' maps to odds_ratio
        proto = self._make_proto(or_val=2.75)
        v = convert_variant_with_stats(proto)
        assert abs(v.odds_ratio - 2.75) < 1e-6


# ---------------------------------------------------------------------------
# Response metadata
# ---------------------------------------------------------------------------


class TestConvertResponseMetadata:
    def test_convert_response_metadata_basic(self):
        proto = pb2.AllelesResponse(
            incomplete_cluster=True,
            affected=True,
            elapsed_ms=150,
            elapsed_db_ms=80,
            node_id="node-1",
        )
        m = convert_response_metadata(proto)
        assert isinstance(m, ResponseMetadata)
        assert m.elapsed_ms == 150
        assert m.elapsed_db_ms == 80
        assert m.node_id == "node-1"
        assert m.incomplete_cluster is True
        assert m.affected is True

    def test_convert_response_metadata_no_affected(self):
        # KinshipResponse has no 'affected' field — should default to False
        proto = pb2.KinshipResponse(
            incomplete_cluster=True,
            elapsed_ms=200,
            elapsed_db_ms=100,
            node_id="node-2",
        )
        m = convert_response_metadata(proto)
        assert m.affected is False
        assert m.incomplete_cluster is True
        assert m.elapsed_ms == 200


# ---------------------------------------------------------------------------
# Count responses
# ---------------------------------------------------------------------------


class TestConvertCountResponses:
    def test_convert_count_alleles_response(self):
        proto = pb2.CountAllelesResponse(
            count=42,
            incomplete_cluster=False,
            affected=False,
            elapsed_ms=50,
            elapsed_db_ms=30,
            node_id="n1",
        )
        result = convert_count_alleles_response(proto)
        assert isinstance(result, CountResult)
        assert result.count == 42
        assert result.metadata.elapsed_ms == 50
        assert result.metadata.node_id == "n1"

    def test_convert_count_samples_response(self):
        proto = pb2.CountSamplesResponse(
            count=10,
            incomplete_cluster=False,
            affected=False,
            elapsed_ms=25,
            elapsed_db_ms=15,
            node_id="n2",
        )
        result = convert_count_samples_response(proto)
        assert isinstance(result, CountResult)
        assert result.count == 10
        assert result.metadata.elapsed_ms == 25


# ---------------------------------------------------------------------------
# Samples response
# ---------------------------------------------------------------------------


class TestConvertSamplesResponse:
    def test_convert_samples_response(self):
        proto = pb2.SamplesResponse(
            samples=["sample1", "sample2", "sample3"],
            incomplete_cluster=False,
            affected=False,
            elapsed_ms=30,
            elapsed_db_ms=20,
            node_id="n1",
        )
        result = convert_samples_response(proto)
        assert isinstance(result, SamplesResult)
        assert result.samples == ("sample1", "sample2", "sample3")
        assert isinstance(result.samples, tuple)
        assert result.metadata.elapsed_ms == 30


# ---------------------------------------------------------------------------
# Infrastructure responses
# ---------------------------------------------------------------------------


class TestConvertInfrastructure:
    def test_convert_health_response(self):
        proto = pb2.HealthResponse(status="ok")
        result = convert_health_response(proto)
        assert isinstance(result, HealthResult)
        assert result.status == "ok"

    def test_convert_cluster_nodes_response(self):
        proto = pb2.ClusterNodesResponse(
            active_nodes=["node-a", "node-b"],
            inactive_nodes=["node-c"],
            total_nodes=3,
            elapsed_ms=10,
        )
        result = convert_cluster_nodes_response(proto)
        assert isinstance(result, ClusterNodesResult)
        assert result.active_nodes == ("node-a", "node-b")
        assert result.inactive_nodes == ("node-c",)
        assert result.total_nodes == 3
        assert result.elapsed_ms == 10

    def test_convert_dataset_info_response(self):
        cohort_proto = pb2.Cohort(
            cohort_name="test-cohort",
            samples_count=100,
            female_count=50,
            male_count=50,
            female_samples_names=["f1", "f2"],
            male_samples_names=["m1", "m2"],
            synthetic=False,
        )
        prs_proto = pb2.PRS(name="prs1", desc="Test PRS", cardinality=500)
        proto = pb2.DatasetInfoResponse(
            cohorts=[cohort_proto],
            samples_total=100,
            females_total=50,
            males_total=50,
            variants_total=1000000,
            assembly=2,  # GRCh38
            rto=False,
            prs=[prs_proto],
            timestamp="2024-01-01T00:00:00Z",
            data_format=1,
            notes="test notes",
            rings_total=4,
            elapsed_ms=100,
            node_id="node-1",
        )
        result = convert_dataset_info_response(proto)
        assert isinstance(result, DatasetInfo)
        assert len(result.cohorts) == 1
        assert result.cohorts[0].cohort_name == "test-cohort"
        assert result.samples_total == 100
        assert result.assembly == RefAssembly.GRCh38
        assert len(result.prs) == 1
        assert result.prs[0].name == "prs1"
        assert result.prs[0].description == "Test PRS"
        assert result.elapsed_ms == 100
        assert result.node_id == "node-1"

    def test_convert_cohort(self):
        proto = pb2.Cohort(
            cohort_name="cohort-A",
            samples_count=200,
            female_count=110,
            male_count=90,
            female_samples_names=["fa", "fb"],
            male_samples_names=["ma"],
            synthetic=True,
        )
        result = convert_cohort(proto)
        assert isinstance(result, Cohort)
        assert result.cohort_name == "cohort-A"
        assert result.samples_count == 200
        assert result.female_count == 110
        assert result.male_count == 90
        assert result.female_sample_names == ("fa", "fb")
        assert result.male_sample_names == ("ma",)
        assert result.synthetic is True

    def test_convert_prs_info(self):
        proto = pb2.PRS(name="prs-abc", desc="A test PRS", cardinality=250)
        result = convert_prs_info(proto)
        assert isinstance(result, PrsInfo)
        assert result.name == "prs-abc"
        assert result.description == "A test PRS"
        assert result.cardinality == 250


# ---------------------------------------------------------------------------
# Statistical responses
# ---------------------------------------------------------------------------


class TestConvertStatistical:
    def test_convert_prs_response(self):
        score = pb2.SampleScore(
            sample="s1", scores_sum=1.5,
            hethom_cardinality=10, ref_cardinality=5,
            mis_cardinality=2, imputed_sum=0.3,
        )
        proto = pb2.PRSResponse(
            prs_name="prs1",
            sample_scores=[score],
            dominant=True,
            recessive=False,
            prs_cardinality=500,
            incomplete_cluster=False,
            elapsed_ms=100,
            elapsed_db_ms=80,
            node_id="n1",
        )
        result = convert_prs_response(proto)
        assert isinstance(result, PrsResult)
        assert result.prs_name == "prs1"
        assert len(result.sample_scores) == 1
        assert result.sample_scores[0].sample == "s1"
        assert result.dominant is True
        assert result.recessive is False
        assert result.prs_cardinality == 500
        assert result.metadata.elapsed_ms == 100

    def test_convert_sample_score(self):
        proto = pb2.SampleScore(
            sample="s-test",
            scores_sum=2.5,
            hethom_cardinality=15,
            ref_cardinality=8,
            mis_cardinality=3,
            imputed_sum=0.7,
        )
        result = convert_sample_score(proto)
        assert isinstance(result, SampleScore)
        assert result.sample == "s-test"
        assert abs(result.scores_sum - 2.5) < 1e-6
        assert result.hethom_cardinality == 15
        assert result.ref_cardinality == 8
        assert result.mis_cardinality == 3
        assert abs(result.imputed_sum - 0.7) < 1e-6

    def test_convert_sex_mismatch_response(self):
        male = pb2.SampleStat(
            sample="m1", reported_sex="male", observed_sex="female", f_stat=0.3,
        )
        female = pb2.SampleStat(
            sample="f1", reported_sex="female", observed_sex="male", f_stat=0.9,
        )
        proto = pb2.SexMismatchResponse(
            mismatch_males=[male],
            mismatch_females=[female],
            incomplete_cluster=False,
            elapsed_ms=50,
            elapsed_db_ms=30,
            node_id="n1",
        )
        result = convert_sex_mismatch_response(proto)
        assert isinstance(result, SexMismatchResult)
        assert len(result.mismatch_males) == 1
        assert result.mismatch_males[0].sample == "m1"
        assert len(result.mismatch_females) == 1
        assert result.mismatch_females[0].sample == "f1"
        assert result.metadata.elapsed_ms == 50

    def test_convert_sample_stat(self):
        proto = pb2.SampleStat(
            sample="sample-x",
            reported_sex="male",
            observed_sex="female",
            f_stat=0.42,
        )
        result = convert_sample_stat(proto)
        assert isinstance(result, SampleStat)
        assert result.sample == "sample-x"
        assert result.reported_sex == "male"
        assert result.observed_sex == "female"
        assert abs(result.f_stat - 0.42) < 1e-6

    def test_convert_fstat_x_response(self):
        m = pb2.SampleStat(sample="m1", reported_sex="male", observed_sex="male", f_stat=0.95)
        f = pb2.SampleStat(sample="f1", reported_sex="female", observed_sex="female", f_stat=0.1)
        proto = pb2.FstatXResponse(
            males=[m], females=[f],
            incomplete_cluster=False,
            elapsed_ms=40, elapsed_db_ms=25, node_id="n1",
        )
        result = convert_fstat_x_response(proto)
        assert isinstance(result, FstatXResult)
        assert len(result.males) == 1
        assert len(result.females) == 1
        assert result.males[0].sample == "m1"
        assert result.metadata.elapsed_ms == 40

    def test_convert_kinship_response(self):
        rel = pb2.Relatedness(
            sample1="s1", sample2="s2",
            degree=2,  # FIRST_DEGREE
            phi_bwf=0.25,
        )
        proto = pb2.KinshipResponse(
            rel=[rel],
            incomplete_cluster=False,
            elapsed_ms=60, elapsed_db_ms=40, node_id="n1",
        )
        result = convert_kinship_response(proto)
        assert isinstance(result, KinshipResult)
        assert len(result.pairs) == 1
        assert result.pairs[0].sample1 == "s1"
        assert result.pairs[0].sample2 == "s2"
        assert result.metadata.elapsed_ms == 60

    def test_convert_relatedness(self):
        proto = pb2.Relatedness(
            sample1="alice", sample2="bob",
            degree=1,  # TWINS_MONOZYGOTIC
            phi_bwf=0.48,
        )
        result = convert_relatedness(proto)
        assert isinstance(result, Relatedness)
        assert result.sample1 == "alice"
        assert result.sample2 == "bob"
        assert result.degree == KinshipDegree.TWINS_MONOZYGOTIC
        assert isinstance(result.degree, KinshipDegree)
        assert abs(result.phi_bwf - 0.48) < 1e-6

    def test_convert_sample_kinship_response(self):
        rel = pb2.RelatednessPerSample(
            sample="ds1", degree=3, phi_bwf=0.1,
            common_loci=5000,
            nHetS1=100, nHetS2=120, nHetS1S2=50, nHomOp=10,
        )
        proto = pb2.SampleKinshipResponse(
            rel=[rel],
            accepted_snvs=10000,
            incomplete_cluster=False,
            elapsed_ms=70, elapsed_db_ms=50, node_id="n1",
        )
        result = convert_sample_kinship_response(proto)
        assert isinstance(result, SampleKinshipResult)
        assert len(result.relatives) == 1
        assert result.accepted_snvs == 10000
        assert result.metadata.elapsed_ms == 70

    def test_convert_sample_relatedness(self):
        proto = pb2.RelatednessPerSample(
            sample="ds-sample",
            degree=2,  # FIRST_DEGREE
            phi_bwf=0.22,
            common_loci=8000,
            nHetS1=200,
            nHetS2=180,
            nHetS1S2=90,
            nHomOp=15,
        )
        result = convert_sample_relatedness(proto)
        assert isinstance(result, SampleRelatedness)
        assert result.sample == "ds-sample"
        assert result.degree == KinshipDegree.FIRST_DEGREE
        assert abs(result.phi_bwf - 0.22) < 1e-6
        assert result.common_loci == 8000
        assert result.n_het_s1 == 200
        assert result.n_het_s2 == 180
        assert result.n_het_s1s2 == 90
        assert result.n_hom_op == 15

    def test_convert_top_hwe_result(self):
        vws = pb2.VariantWithStats(
            variant=pb2.Variant(
                chr=1, start=100, end=100, ref="A", alt="T",
                af=0.5, ac=1.0, an=2, homc=0, hetc=1,
                gnomADe=0.1, gnomADg=0.2,
                amino_acids="X/Y", biallelic=True,
            ),
            vaf=0.3, vac=1.0, van=4, vhomc=0, vhetc=1,
            phwe=0.001, pchi2=0.05, ibc=0.01,
            **{"or": 1.2},
        )
        proto = pb2.AllelesWithStatsResponse(
            variants=[vws],
            incomplete_cluster=False, affected=False,
            elapsed_ms=100, elapsed_db_ms=80, node_id="n1",
        )
        result = convert_alleles_with_stats_response_to_top_hwe(proto)
        assert isinstance(result, TopHweResult)
        assert len(result.variants) == 1
        assert result.variants[0].chr == Chromosome.CHR_1
        assert result.metadata.elapsed_ms == 100

    def test_convert_top_chi2_result(self):
        vws = pb2.VariantWithStats(
            variant=pb2.Variant(
                chr=2, start=500, end=500, ref="C", alt="G",
                af=0.1, ac=0.5, an=10, homc=0, hetc=1,
                gnomADe=0.0, gnomADg=0.0,
                amino_acids="", biallelic=True,
            ),
            vaf=0.2, vac=0.5, van=5, vhomc=0, vhetc=1,
            phwe=0.5, pchi2=0.003, ibc=0.0,
            **{"or": 3.5},
        )
        proto = pb2.AllelesWithStatsResponse(
            variants=[vws],
            incomplete_cluster=False, affected=False,
            elapsed_ms=200, elapsed_db_ms=150, node_id="n2",
        )
        result = convert_alleles_with_stats_response_to_top_chi2(proto)
        assert isinstance(result, TopChi2Result)
        assert len(result.variants) == 1
        assert result.variants[0].chr == Chromosome.CHR_2
        assert abs(result.variants[0].odds_ratio - 3.5) < 1e-6
        assert result.metadata.elapsed_ms == 200


# ---------------------------------------------------------------------------
# AnnotationFilter → proto
# ---------------------------------------------------------------------------


class TestAnnotationFilterToProto:
    def test_annotation_filter_to_proto_empty(self):
        af = AnnotationFilter()
        proto = annotation_filter_to_proto(af)
        assert isinstance(proto, pb2.Annotations)
        # All defaults — repeated fields empty, floats 0.0, bools False
        assert len(proto.consequence) == 0
        assert len(proto.impact) == 0
        assert proto.af_lt == 0.0
        assert proto.biallelicOnly is False

    def test_annotation_filter_to_proto_consequence(self):
        af = AnnotationFilter(consequence=[Consequence.MISSENSE_VARIANT])
        proto = annotation_filter_to_proto(af)
        assert len(proto.consequence) == 1
        assert proto.consequence[0] == int(Consequence.MISSENSE_VARIANT)

    def test_annotation_filter_to_proto_multiple_impacts(self):
        af = AnnotationFilter(impact=[Impact.HIGH, Impact.MODERATE])
        proto = annotation_filter_to_proto(af)
        assert len(proto.impact) == 2
        assert int(Impact.HIGH) in proto.impact
        assert int(Impact.MODERATE) in proto.impact

    def test_annotation_filter_to_proto_float_fields(self):
        af = AnnotationFilter(af_lt=0.01, gnomad_exomes_af_gt=0.001)
        proto = annotation_filter_to_proto(af)
        assert abs(proto.af_lt - 0.01) < 1e-6
        assert abs(proto.gnomad_exomes_af_gt - 0.001) < 1e-6
        # Unset fields remain at proto default 0.0
        assert proto.af_gt == 0.0

    def test_annotation_filter_to_proto_bool_fields(self):
        af = AnnotationFilter(biallelic_only=True, exclude_males=True)
        proto = annotation_filter_to_proto(af)
        assert proto.biallelicOnly is True
        assert proto.excludeMales is True
        assert proto.multiallelicOnly is False
        assert proto.excludeFemales is False

    def test_annotation_filter_to_proto_all_fields(self):
        af = AnnotationFilter(
            variant_type=[VariantType.SNV],
            consequence=[Consequence.MISSENSE_VARIANT],
            impact=[Impact.HIGH],
            clin_significance=[],
            af_lt=0.05,
            af_gt=0.001,
            gnomad_exomes_af_lt=0.1,
            gnomad_exomes_af_gt=0.0001,
            gnomad_genomes_af_lt=0.2,
            gnomad_genomes_af_gt=0.0002,
            cadd_raw_lt=5.0,
            cadd_raw_gt=1.0,
            cadd_phred_lt=30.0,
            cadd_phred_gt=10.0,
            am_score_lt=0.9,
            am_score_gt=0.1,
            biallelic_only=True,
            exclude_females=True,
        )
        proto = annotation_filter_to_proto(af)
        assert len(proto.variant_type) == 1
        assert proto.variant_type[0] == int(VariantType.SNV)
        assert len(proto.consequence) == 1
        assert len(proto.impact) == 1
        assert abs(proto.af_lt - 0.05) < 1e-6
        assert abs(proto.af_gt - 0.001) < 1e-6
        assert abs(proto.gnomad_exomes_af_lt - 0.1) < 1e-6
        assert abs(proto.gnomad_genomes_af_lt - 0.2) < 1e-6
        assert abs(proto.cadd_raw_lt - 5.0) < 1e-6
        assert abs(proto.cadd_phred_gt - 10.0) < 1e-6
        assert abs(proto.am_score_lt - 0.9) < 1e-6
        assert abs(proto.am_score_gt - 0.1) < 1e-6
        assert proto.biallelicOnly is True
        assert proto.excludeFemales is True
        assert proto.multiallelicOnly is False
        assert proto.excludeMales is False
