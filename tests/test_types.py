"""Tests for dnaerys._types — input and result dataclasses."""

import warnings

import pytest

from dnaerys._enums import (
    AlphaMissense,
    Chromosome,
    Consequence,
    Impact,
    KinshipDegree,
    RefAssembly,
)
from dnaerys._types import (
    AnnotationFilter,
    Bracket,
    ClusterNodesResult,
    Cohort,
    CountResult,
    DatasetInfo,
    FstatXResult,
    HealthResult,
    KinshipResult,
    PrsInfo,
    PrsResult,
    Region,
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


# -----------------------------------------------------------------------
# Helper: build a ResponseMetadata for result type tests
# -----------------------------------------------------------------------


def _meta(**overrides):
    defaults = dict(
        elapsed_ms=100,
        elapsed_db_ms=50,
        node_id="node-1",
        incomplete_cluster=False,
        affected=False,
    )
    defaults.update(overrides)
    return ResponseMetadata(**defaults)


# -----------------------------------------------------------------------
# Region
# -----------------------------------------------------------------------


class TestRegion:
    def test_region_basic_construction(self):
        r = Region("chr1", 100, 200)
        assert r.chr == Chromosome.CHR1
        assert r.start == 100
        assert r.end == 200

    def test_region_with_ref_alt(self):
        r = Region("chr1", 100, 200, ref="A", alt="T")
        assert r.ref == "A"
        assert r.alt == "T"

    def test_region_enum_chr(self):
        r = Region(Chromosome.CHR1, 100, 200)
        assert r.chr == Chromosome.CHR1

    def test_region_start_gt_end_raises(self):
        with pytest.raises(ValueError, match="end.*must be >= start"):
            Region("chr1", 200, 100)

    def test_region_zero_start_raises(self):
        with pytest.raises(ValueError, match="start must be >= 1"):
            Region("chr1", 0, 100)

    def test_region_negative_start_raises(self):
        with pytest.raises(ValueError, match="start must be >= 1"):
            Region("chr1", -1, 100)

    def test_region_equal_start_end(self):
        r = Region("chr1", 100, 100)
        assert r.start == r.end == 100

    def test_region_frozen(self):
        r = Region("chr1", 100, 200)
        with pytest.raises(AttributeError):
            r.start = 5  # type: ignore[misc]


# -----------------------------------------------------------------------
# Bracket
# -----------------------------------------------------------------------


class TestBracket:
    def test_bracket_basic_construction(self):
        b = Bracket("chr1", 100, 200, 300, 400)
        assert b.chr == Chromosome.CHR1
        assert b.start_min == 100
        assert b.start_max == 200
        assert b.end_min == 300
        assert b.end_max == 400

    def test_bracket_with_ref_alt(self):
        b = Bracket("chr1", 100, 200, 300, 400, ref="A", alt="T")
        assert b.ref == "A"
        assert b.alt == "T"

    def test_bracket_start_min_gt_start_max_raises(self):
        with pytest.raises(ValueError, match="start_min.*must be <= start_max"):
            Bracket("chr1", 200, 100, 300, 400)

    def test_bracket_end_min_gt_end_max_raises(self):
        with pytest.raises(ValueError, match="end_min.*must be <= end_max"):
            Bracket("chr1", 100, 200, 400, 300)

    def test_bracket_zero_position_raises(self):
        with pytest.raises(ValueError, match="must be >= 1"):
            Bracket("chr1", 0, 200, 300, 400)

    def test_bracket_frozen(self):
        b = Bracket("chr1", 100, 200, 300, 400)
        with pytest.raises(AttributeError):
            b.start_min = 5  # type: ignore[misc]


# -----------------------------------------------------------------------
# AnnotationFilter
# -----------------------------------------------------------------------


class TestAnnotationFilter:
    def test_annotation_filter_defaults(self):
        af = AnnotationFilter()
        assert af.variant_type == ()
        assert af.consequence == ()
        assert af.af_lt is None
        assert af.biallelic_only is False

    def test_annotation_filter_consequence_enum(self):
        af = AnnotationFilter(consequence=[Consequence.MISSENSE_VARIANT])
        assert af.consequence == (Consequence.MISSENSE_VARIANT,)
        assert isinstance(af.consequence, tuple)

    def test_annotation_filter_consequence_string(self):
        af = AnnotationFilter(consequence=["missense_variant"])
        assert af.consequence == (Consequence.MISSENSE_VARIANT,)

    def test_annotation_filter_consequence_mixed(self):
        af = AnnotationFilter(
            consequence=[Consequence.MISSENSE_VARIANT, "frameshift_variant"]
        )
        assert af.consequence == (
            Consequence.MISSENSE_VARIANT,
            Consequence.FRAMESHIFT_VARIANT,
        )

    def test_annotation_filter_multiple_impacts(self):
        af = AnnotationFilter(impact=[Impact.HIGH, Impact.MODERATE])
        assert af.impact == (Impact.HIGH, Impact.MODERATE)
        assert isinstance(af.impact, tuple)

    def test_annotation_filter_biallelic_multiallelic_raises(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            AnnotationFilter(biallelic_only=True, multiallelic_only=True)

    def test_annotation_filter_am_score_and_class_raises(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            AnnotationFilter(
                am_score_lt=0.5,
                am_class=[AlphaMissense.AM_LIKELY_PATHOGENIC],
            )

    def test_annotation_filter_am_score_gt_and_class_raises(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            AnnotationFilter(
                am_score_gt=0.3,
                am_class=[AlphaMissense.AM_LIKELY_PATHOGENIC],
            )

    def test_annotation_filter_exclude_males_females_raises(self):
        with pytest.raises(ValueError, match="mutually exclusive"):
            AnnotationFilter(exclude_males=True, exclude_females=True)

    def test_annotation_filter_af_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(af_lt=0.01, af_gt=0.05)

    def test_annotation_filter_gnomad_exomes_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(gnomad_exomes_af_lt=0.01, gnomad_exomes_af_gt=0.05)

    def test_annotation_filter_gnomad_genomes_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(
                gnomad_genomes_af_lt=0.01, gnomad_genomes_af_gt=0.05
            )

    def test_annotation_filter_cadd_raw_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(cadd_raw_lt=10.0, cadd_raw_gt=20.0)

    def test_annotation_filter_cadd_phred_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(cadd_phred_lt=10.0, cadd_phred_gt=20.0)

    def test_annotation_filter_am_score_range_warning(self):
        with pytest.warns(UserWarning, match="empty range"):
            AnnotationFilter(am_score_lt=0.3, am_score_gt=0.5)

    def test_annotation_filter_valid_af_range_no_warning(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            AnnotationFilter(af_lt=0.05, af_gt=0.01)

    def test_annotation_filter_float_fields(self):
        af = AnnotationFilter(af_lt=0.01)
        assert af.af_lt == 0.01

    def test_annotation_filter_frozen(self):
        af = AnnotationFilter()
        with pytest.raises(AttributeError):
            af.af_lt = 0.5  # type: ignore[misc]

    def test_annotation_filter_invalid_consequence_string(self):
        with pytest.raises(ValueError, match="Unknown Consequence"):
            AnnotationFilter(consequence=["NONEXISTENT"])


# -----------------------------------------------------------------------
# Result dataclass construction (sanity checks)
# -----------------------------------------------------------------------


class TestVariant:
    def test_variant_construction(self):
        v = Variant(
            chr=Chromosome.CHR1,
            start=100,
            end=100,
            ref="A",
            alt="T",
            af=0.05,
            ac=10.0,
            an=200,
            hom_samples=2,
            het_samples=6,
            mis_samples=0,
            hom_samples_fx=1,
            het_samples_fx=3,
            mis_samples_fx=0,
            hom_samples_mxy=4,
            het_samples_mxy=5,
            mis_samples_mxy=1,
            gnomad_exomes_af=0.04,
            gnomad_genomes_af=0.03,
            cadd_raw=1.5,
            cadd_phred=15.0,
            am_score=0.7,
            amino_acids="A/T",
            biallelic=True,
        )
        assert v.chr == Chromosome.CHR1
        assert v.start == 100
        assert v.end == 100
        assert v.ref == "A"
        assert v.alt == "T"
        assert v.af == 0.05
        assert v.ac == 10.0
        assert v.an == 200
        assert v.hom_samples == 2
        assert v.het_samples == 6
        assert v.mis_samples == 0
        assert v.hom_samples_fx == 1
        assert v.het_samples_fx == 3
        assert v.mis_samples_fx == 0
        assert v.hom_samples_mxy == 4
        assert v.het_samples_mxy == 5
        assert v.mis_samples_mxy == 1
        assert v.gnomad_exomes_af == 0.04
        assert v.gnomad_genomes_af == 0.03
        assert v.cadd_raw == 1.5
        assert v.cadd_phred == 15.0
        assert v.am_score == 0.7
        assert v.amino_acids == "A/T"
        assert v.biallelic is True

    def test_variant_frozen(self):
        v = Variant(
            chr=Chromosome.CHR1, start=100, end=100, ref="A", alt="T",
            af=0.05, ac=10.0, an=200, hom_samples=2, het_samples=6, mis_samples=0, hom_samples_fx=1,
            het_samples_fx=3, mis_samples_fx=0, hom_samples_mxy=0, het_samples_mxy=0, mis_samples_mxy=0,
            gnomad_exomes_af=0.0, gnomad_genomes_af=0.0,
            cadd_raw=0.0, cadd_phred=0.0, am_score=0.0, amino_acids="",
            biallelic=True,
        )
        with pytest.raises(AttributeError):
            v.start = 5  # type: ignore[misc]


class TestVariantWithStats:
    def test_variant_with_stats_construction(self):
        vws = VariantWithStats(
            chr=Chromosome.CHR1, start=100, end=100, ref="A", alt="T",
            af=0.05, ac=10.0, an=200, hom_samples=2, het_samples=6, mis_samples=0, hom_samples_fx=1,
            het_samples_fx=3, mis_samples_fx=0, hom_samples_mxy=4, het_samples_mxy=5, mis_samples_mxy=1,
            gnomad_exomes_af=0.04, gnomad_genomes_af=0.03,
            cadd_raw=1.5, cadd_phred=15.0, am_score=0.7, amino_acids="A/T",
            biallelic=True,
            vaf=0.1, vac=5.0, van=50, v_hom_samples=1, v_het_samples=3, v_hom_samples_fx=0, v_het_samples_fx=1,
            v_hom_samples_mxy=2, v_het_samples_mxy=3,
            phwe=0.5, pchi2=0.01, odds_ratio=2.5, ibc=0.02,
        )
        assert vws.chr == Chromosome.CHR1
        assert vws.vaf == 0.1
        assert vws.vac == 5.0
        assert vws.van == 50
        assert vws.v_hom_samples == 1
        assert vws.v_het_samples == 3
        assert vws.v_hom_samples_fx == 0
        assert vws.v_het_samples_fx == 1
        assert vws.v_hom_samples_mxy == 2
        assert vws.v_het_samples_mxy == 3
        assert vws.phwe == 0.5
        assert vws.pchi2 == 0.01
        assert vws.odds_ratio == 2.5
        assert vws.ibc == 0.02

    def test_variant_with_stats_has_all_variant_fields(self):
        vws = VariantWithStats(
            chr=Chromosome.CHRX, start=50, end=60, ref="G", alt="C",
            af=0.1, ac=20.0, an=200, hom_samples=5, het_samples=10, mis_samples=2, hom_samples_fx=2,
            het_samples_fx=4, mis_samples_fx=1, hom_samples_mxy=3, het_samples_mxy=2, mis_samples_mxy=1,
            gnomad_exomes_af=0.0, gnomad_genomes_af=0.0,
            cadd_raw=0.0, cadd_phred=0.0, am_score=0.0, amino_acids="",
            biallelic=False,
            vaf=0.0, vac=0.0, van=0, v_hom_samples=0, v_het_samples=0, v_hom_samples_fx=0, v_het_samples_fx=0,
            v_hom_samples_mxy=0, v_het_samples_mxy=0,
            phwe=0.0, pchi2=0.0, odds_ratio=0.0, ibc=0.0,
        )
        assert vws.chr == Chromosome.CHRX
        assert vws.start == 50
        assert vws.end == 60
        assert vws.ref == "G"
        assert vws.alt == "C"
        assert vws.biallelic is False


class TestCountResult:
    def test_count_result_construction(self):
        r = CountResult(count=42, metadata=_meta())
        assert r.count == 42
        assert r.metadata.elapsed_ms == 100


class TestSamplesResult:
    def test_samples_result_construction(self):
        r = SamplesResult(samples=("s1", "s2"), metadata=_meta())
        assert r.samples == ("s1", "s2")
        assert r.metadata.node_id == "node-1"


class TestResponseMetadata:
    def test_response_metadata_construction(self):
        m = ResponseMetadata(
            elapsed_ms=100, elapsed_db_ms=50, node_id="node-1",
            incomplete_cluster=True, affected=False,
        )
        assert m.elapsed_ms == 100
        assert m.elapsed_db_ms == 50
        assert m.node_id == "node-1"
        assert m.incomplete_cluster is True
        assert m.affected is False


class TestHealthResult:
    def test_health_result_construction(self):
        h = HealthResult(status="ok")
        assert h.status == "ok"


class TestClusterNodesResult:
    def test_cluster_nodes_result_construction(self):
        c = ClusterNodesResult(
            active_nodes=("n1", "n2"),
            inactive_nodes=("n3",),
            total_nodes=3,
            elapsed_ms=15,
        )
        assert c.active_nodes == ("n1", "n2")
        assert c.inactive_nodes == ("n3",)
        assert c.total_nodes == 3
        assert c.elapsed_ms == 15


class TestDatasetInfo:
    def test_dataset_info_construction(self):
        cohort = Cohort(
            cohort_name="test_cohort",
            samples_count=100,
            female_count=50,
            male_count=50,
            female_sample_names=("f1", "f2"),
            male_sample_names=("m1", "m2"),
            synthetic=False,
        )
        prs = PrsInfo(name="PRS_TEST", description="Test PRS", cardinality=50)
        di = DatasetInfo(
            cohorts=(cohort,),
            samples_total=100,
            females_total=50,
            males_total=50,
            variants_total=1000000,
            assembly=RefAssembly.GRCh38,
            rto=False,
            prs=(prs,),
            timestamp="2024-01-01T00:00:00Z",
            data_format=1,
            notes="test",
            rings_total=4,
            elapsed_ms=200,
            node_id="node-1",
        )
        assert di.cohorts[0].cohort_name == "test_cohort"
        assert di.assembly == RefAssembly.GRCh38
        assert di.prs[0].name == "PRS_TEST"
        assert di.variants_total == 1000000


class TestCohort:
    def test_cohort_construction(self):
        c = Cohort(
            cohort_name="c1",
            samples_count=10,
            female_count=5,
            male_count=5,
            female_sample_names=("f1",),
            male_sample_names=("m1",),
            synthetic=False,
        )
        assert c.cohort_name == "c1"
        assert c.samples_count == 10
        assert c.female_count == 5
        assert c.male_count == 5
        assert c.female_sample_names == ("f1",)
        assert c.male_sample_names == ("m1",)
        assert c.synthetic is False


class TestPrsInfo:
    def test_prs_info_construction(self):
        p = PrsInfo(name="PRS1", description="desc", cardinality=100)
        assert p.name == "PRS1"
        assert p.description == "desc"
        assert p.cardinality == 100


class TestPrsResult:
    def test_prs_result_construction(self):
        score = SampleScore(
            sample="s1", scores_sum=1.5, hethom_cardinality=10,
            ref_cardinality=5, mis_cardinality=2, imputed_sum=0.3,
        )
        r = PrsResult(
            prs_name="PRS1",
            sample_scores=(score,),
            dominant=True,
            recessive=False,
            prs_cardinality=50,
            metadata=_meta(),
        )
        assert r.prs_name == "PRS1"
        assert r.sample_scores[0].sample == "s1"
        assert r.dominant is True
        assert r.recessive is False
        assert r.prs_cardinality == 50


class TestSampleScore:
    def test_sample_score_construction(self):
        ss = SampleScore(
            sample="s1", scores_sum=1.5, hethom_cardinality=10,
            ref_cardinality=5, mis_cardinality=2, imputed_sum=0.3,
        )
        assert ss.sample == "s1"
        assert ss.scores_sum == 1.5
        assert ss.hethom_cardinality == 10
        assert ss.ref_cardinality == 5
        assert ss.mis_cardinality == 2
        assert ss.imputed_sum == 0.3


class TestSexMismatchResult:
    def test_sex_mismatch_result_construction(self):
        stat = SampleStat(
            sample="s1", reported_sex="male", observed_sex="female", f_stat=0.3,
        )
        r = SexMismatchResult(
            mismatch_males=(stat,),
            mismatch_females=(),
            metadata=_meta(),
        )
        assert r.mismatch_males[0].sample == "s1"
        assert r.mismatch_females == ()


class TestSampleStat:
    def test_sample_stat_construction(self):
        ss = SampleStat(
            sample="s1", reported_sex="male", observed_sex="male", f_stat=0.9,
        )
        assert ss.sample == "s1"
        assert ss.reported_sex == "male"
        assert ss.observed_sex == "male"
        assert ss.f_stat == 0.9


class TestFstatXResult:
    def test_fstat_x_result_construction(self):
        male_stat = SampleStat(
            sample="m1", reported_sex="male", observed_sex="male", f_stat=0.95,
        )
        female_stat = SampleStat(
            sample="f1", reported_sex="female", observed_sex="female",
            f_stat=0.1,
        )
        r = FstatXResult(
            males=(male_stat,),
            females=(female_stat,),
            metadata=_meta(),
        )
        assert r.males[0].f_stat == 0.95
        assert r.females[0].f_stat == 0.1


class TestKinshipResult:
    def test_kinship_result_construction(self):
        rel = Relatedness(
            sample1="s1", sample2="s2",
            degree=KinshipDegree.FIRST_DEGREE, phi_bwf=0.25,
        )
        r = KinshipResult(pairs=(rel,), metadata=_meta())
        assert r.pairs[0].sample1 == "s1"
        assert r.pairs[0].degree == KinshipDegree.FIRST_DEGREE


class TestRelatedness:
    def test_relatedness_construction(self):
        rel = Relatedness(
            sample1="s1", sample2="s2",
            degree=KinshipDegree.SECOND_DEGREE, phi_bwf=0.12,
        )
        assert rel.sample1 == "s1"
        assert rel.sample2 == "s2"
        assert rel.degree == KinshipDegree.SECOND_DEGREE
        assert rel.phi_bwf == 0.12


class TestSampleKinshipResult:
    def test_sample_kinship_result_construction(self):
        sr = SampleRelatedness(
            sample="s1", degree=KinshipDegree.THIRD_DEGREE, phi_bwf=0.06,
            common_loci=10000, n_het_s1=500, n_het_s2=600,
            n_het_s1s2=200, n_hom_op=10,
        )
        r = SampleKinshipResult(
            relatives=(sr,), accepted_snvs=50000, metadata=_meta(),
        )
        assert r.relatives[0].sample == "s1"
        assert r.accepted_snvs == 50000


class TestSampleRelatedness:
    def test_sample_relatedness_construction(self):
        sr = SampleRelatedness(
            sample="s1", degree=KinshipDegree.UNRELATED, phi_bwf=0.01,
            common_loci=20000, n_het_s1=1000, n_het_s2=1100,
            n_het_s1s2=400, n_hom_op=5,
        )
        assert sr.sample == "s1"
        assert sr.degree == KinshipDegree.UNRELATED
        assert sr.phi_bwf == 0.01
        assert sr.common_loci == 20000
        assert sr.n_het_s1 == 1000
        assert sr.n_het_s2 == 1100
        assert sr.n_het_s1s2 == 400
        assert sr.n_hom_op == 5


class TestTopHweResult:
    def test_top_hwe_result_construction(self):
        vws = VariantWithStats(
            chr=Chromosome.CHR1, start=100, end=100, ref="A", alt="T",
            af=0.05, ac=10.0, an=200, hom_samples=2, het_samples=6, mis_samples=0, hom_samples_fx=1,
            het_samples_fx=3, mis_samples_fx=0, hom_samples_mxy=0, het_samples_mxy=0, mis_samples_mxy=0,
            gnomad_exomes_af=0.0, gnomad_genomes_af=0.0,
            cadd_raw=0.0, cadd_phred=0.0, am_score=0.0, amino_acids="",
            biallelic=True,
            vaf=0.0, vac=0.0, van=0, v_hom_samples=0, v_het_samples=0, v_hom_samples_fx=0, v_het_samples_fx=0,
            v_hom_samples_mxy=0, v_het_samples_mxy=0,
            phwe=1e-10, pchi2=0.0, odds_ratio=0.0, ibc=0.0,
        )
        r = TopHweResult(variants=(vws,), metadata=_meta())
        assert r.variants[0].phwe == 1e-10


class TestTopChi2Result:
    def test_top_chi2_result_construction(self):
        vws = VariantWithStats(
            chr=Chromosome.CHR1, start=100, end=100, ref="A", alt="T",
            af=0.05, ac=10.0, an=200, hom_samples=2, het_samples=6, mis_samples=0, hom_samples_fx=1,
            het_samples_fx=3, mis_samples_fx=0, hom_samples_mxy=0, het_samples_mxy=0, mis_samples_mxy=0,
            gnomad_exomes_af=0.0, gnomad_genomes_af=0.0,
            cadd_raw=0.0, cadd_phred=0.0, am_score=0.0, amino_acids="",
            biallelic=True,
            vaf=0.0, vac=0.0, van=0, v_hom_samples=0, v_het_samples=0, v_hom_samples_fx=0, v_het_samples_fx=0,
            v_hom_samples_mxy=0, v_het_samples_mxy=0,
            phwe=0.0, pchi2=1e-5, odds_ratio=3.2, ibc=0.0,
        )
        r = TopChi2Result(variants=(vws,), metadata=_meta())
        assert r.variants[0].pchi2 == 1e-5
        assert r.variants[0].odds_ratio == 3.2
