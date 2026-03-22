"""Proto ↔ dataclass conversion functions for the Dnaerys client library.

Each function in this module converts between a protobuf-generated message
class (from ``dnaerys_pb2``) and the corresponding Python dataclass defined
in ``_types``.  Response conversions go proto → dataclass; the sole request
conversion (``annotation_filter_to_proto``) goes dataclass → proto.

All field-name mappings between proto and Python are documented in the
function that performs the conversion.
"""

from __future__ import annotations

from dnaerys._enums import Chromosome, KinshipDegree, RefAssembly
from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys._types import (
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
    AnnotationFilter,
)


# ---------------------------------------------------------------------------
# Proto response → Python dataclass
# ---------------------------------------------------------------------------


def convert_variant(proto: pb2.Variant) -> Variant:
    """Convert a ``pb2.Variant`` proto message to a ``Variant`` dataclass.

    Field mapping:
        proto.gnomADe → gnomad_exomes_af
        proto.gnomADg → gnomad_genomes_af
        All other fields share the same name.
    """
    return Variant(
        chr=Chromosome(proto.chr),
        start=proto.start,
        end=proto.end,
        ref=proto.ref,
        alt=proto.alt,
        af=proto.af,
        ac=proto.ac,
        an=proto.an,
        homc=proto.homc,
        hetc=proto.hetc,
        misc=proto.misc,
        homfc=proto.homfc,
        hetfc=proto.hetfc,
        misfc=proto.misfc,
        gnomad_exomes_af=proto.gnomADe,
        gnomad_genomes_af=proto.gnomADg,
        cadd_raw=proto.cadd_raw,
        cadd_phred=proto.cadd_phred,
        am_score=proto.am_score,
        amino_acids=proto.amino_acids,
        biallelic=proto.biallelic,
    )


def convert_variant_with_stats(proto: pb2.VariantWithStats) -> VariantWithStats:
    """Convert a ``pb2.VariantWithStats`` proto message to a ``VariantWithStats`` dataclass.

    The proto nests variant fields inside ``proto.variant`` (a ``pb2.Variant``
    sub-message).  This function flattens them so the Python dataclass has all
    fields at the top level.

    Field mapping:
        proto.variant.chr      → chr
        proto.variant.gnomADe  → gnomad_exomes_af
        proto.variant.gnomADg  → gnomad_genomes_af
        proto.variant.*        → * (same name for all other Variant fields)
        getattr(proto, 'or')   → odds_ratio

    The proto field ``or`` (field number 11) is a Python reserved keyword.
    The protobuf runtime makes it accessible via ``getattr(proto, 'or')``.
    The generated .pyi stub excludes it from ``__slots__`` but includes
    ``OR_FIELD_NUMBER`` as a class variable.  The accessor name used here
    is: ``getattr(proto, 'or')``.
    """
    v = proto.variant
    return VariantWithStats(
        chr=Chromosome(v.chr),
        start=v.start,
        end=v.end,
        ref=v.ref,
        alt=v.alt,
        af=v.af,
        ac=v.ac,
        an=v.an,
        homc=v.homc,
        hetc=v.hetc,
        misc=v.misc,
        homfc=v.homfc,
        hetfc=v.hetfc,
        misfc=v.misfc,
        gnomad_exomes_af=v.gnomADe,
        gnomad_genomes_af=v.gnomADg,
        cadd_raw=v.cadd_raw,
        cadd_phred=v.cadd_phred,
        am_score=v.am_score,
        amino_acids=v.amino_acids,
        biallelic=v.biallelic,
        vaf=proto.vaf,
        vac=proto.vac,
        van=proto.van,
        vhomc=proto.vhomc,
        vhetc=proto.vhetc,
        vhomfc=proto.vhomfc,
        vhetfc=proto.vhetfc,
        phwe=proto.phwe,
        pchi2=proto.pchi2,
        # Proto field "or" is a Python reserved keyword.
        # Accessor: getattr(proto, 'or')
        odds_ratio=getattr(proto, "or"),
        ibc=proto.ibc,
    )


def convert_response_metadata(proto: object) -> ResponseMetadata:
    """Extract ``ResponseMetadata`` from any proto response that carries timing/health fields.

    Converts from proto response messages (``AllelesResponse``,
    ``CountAllelesResponse``, ``CountSamplesResponse``, ``SamplesResponse``,
    ``PRSResponse``, ``SexMismatchResponse``, ``FstatXResponse``,
    ``KinshipResponse``, ``SampleKinshipResponse``, ``AllelesWithStatsResponse``)
    to the ``ResponseMetadata`` dataclass.

    Responses that lack the ``affected`` field (e.g. ``PRSResponse``,
    ``KinshipResponse``) default to ``affected=False``.
    """
    return ResponseMetadata(
        elapsed_ms=int(proto.elapsed_ms),
        elapsed_db_ms=int(getattr(proto, "elapsed_db_ms", 0)),
        node_id=proto.node_id,
        incomplete_cluster=getattr(proto, "incomplete_cluster", False),
        affected=getattr(proto, "affected", False),
    )


def convert_count_alleles_response(proto: pb2.CountAllelesResponse) -> CountResult:
    """Convert a ``pb2.CountAllelesResponse`` to a ``CountResult`` dataclass."""
    return CountResult(
        count=int(proto.count),
        metadata=convert_response_metadata(proto),
    )


def convert_count_samples_response(proto: pb2.CountSamplesResponse) -> CountResult:
    """Convert a ``pb2.CountSamplesResponse`` to a ``CountResult`` dataclass."""
    return CountResult(
        count=int(proto.count),
        metadata=convert_response_metadata(proto),
    )


def convert_samples_response(proto: pb2.SamplesResponse) -> SamplesResult:
    """Convert a ``pb2.SamplesResponse`` to a ``SamplesResult`` dataclass."""
    return SamplesResult(
        samples=tuple(proto.samples),
        metadata=convert_response_metadata(proto),
    )


def convert_health_response(proto: pb2.HealthResponse) -> HealthResult:
    """Convert a ``pb2.HealthResponse`` to a ``HealthResult`` dataclass.

    ``HealthResponse`` has only a ``status`` field — no metadata (D4 resolution).
    """
    return HealthResult(status=proto.status)


def convert_cluster_nodes_response(proto: pb2.ClusterNodesResponse) -> ClusterNodesResult:
    """Convert a ``pb2.ClusterNodesResponse`` to a ``ClusterNodesResult`` dataclass.

    ``ClusterNodesResponse`` has ``elapsed_ms`` but no ``incomplete_cluster``,
    ``affected``, ``elapsed_db_ms``, or ``node_id`` (D4 resolution).
    """
    return ClusterNodesResult(
        active_nodes=tuple(proto.active_nodes),
        inactive_nodes=tuple(proto.inactive_nodes),
        total_nodes=proto.total_nodes,
        elapsed_ms=int(proto.elapsed_ms),
    )


def convert_cohort(proto: pb2.Cohort) -> Cohort:
    """Convert a ``pb2.Cohort`` to a ``Cohort`` dataclass.

    Field mapping:
        proto.female_samples_names → female_sample_names
        proto.male_samples_names   → male_sample_names
    """
    return Cohort(
        cohort_name=proto.cohort_name,
        samples_count=proto.samples_count,
        female_count=proto.female_count,
        male_count=proto.male_count,
        female_sample_names=tuple(proto.female_samples_names),
        male_sample_names=tuple(proto.male_samples_names),
        synthetic=proto.synthetic,
    )


def convert_prs_info(proto: pb2.PRS) -> PrsInfo:
    """Convert a ``pb2.PRS`` (catalog entry) to a ``PrsInfo`` dataclass.

    Field mapping:
        proto.desc → description
    """
    return PrsInfo(
        name=proto.name,
        description=proto.desc,
        cardinality=proto.cardinality,
    )


def convert_dataset_info_response(proto: pb2.DatasetInfoResponse) -> DatasetInfo:
    """Convert a ``pb2.DatasetInfoResponse`` to a ``DatasetInfo`` dataclass.

    ``DatasetInfoResponse`` has ``elapsed_ms`` and ``node_id`` as direct
    attributes — it does NOT use ``ResponseMetadata`` (D4 resolution).
    """
    return DatasetInfo(
        cohorts=tuple(convert_cohort(c) for c in proto.cohorts),
        samples_total=proto.samples_total,
        females_total=proto.females_total,
        males_total=proto.males_total,
        variants_total=proto.variants_total,
        assembly=RefAssembly(proto.assembly),
        rto=proto.rto,
        prs=tuple(convert_prs_info(p) for p in proto.prs),
        timestamp=proto.timestamp,
        data_format=proto.data_format,
        notes=proto.notes,
        rings_total=proto.rings_total,
        elapsed_ms=int(proto.elapsed_ms),
        node_id=proto.node_id,
    )


def convert_sample_score(proto: pb2.SampleScore) -> SampleScore:
    """Convert a ``pb2.SampleScore`` to a ``SampleScore`` dataclass."""
    return SampleScore(
        sample=proto.sample,
        scores_sum=proto.scores_sum,
        hethom_cardinality=proto.hethom_cardinality,
        ref_cardinality=proto.ref_cardinality,
        mis_cardinality=proto.mis_cardinality,
        imputed_sum=proto.imputed_sum,
    )


def convert_prs_response(proto: pb2.PRSResponse) -> PrsResult:
    """Convert a ``pb2.PRSResponse`` to a ``PrsResult`` dataclass."""
    return PrsResult(
        prs_name=proto.prs_name,
        sample_scores=tuple(convert_sample_score(s) for s in proto.sample_scores),
        dominant=proto.dominant,
        recessive=proto.recessive,
        prs_cardinality=proto.prs_cardinality,
        metadata=convert_response_metadata(proto),
    )


def convert_sample_stat(proto: pb2.SampleStat) -> SampleStat:
    """Convert a ``pb2.SampleStat`` to a ``SampleStat`` dataclass."""
    return SampleStat(
        sample=proto.sample,
        reported_sex=proto.reported_sex,
        observed_sex=proto.observed_sex,
        f_stat=proto.f_stat,
    )


def convert_sex_mismatch_response(proto: pb2.SexMismatchResponse) -> SexMismatchResult:
    """Convert a ``pb2.SexMismatchResponse`` to a ``SexMismatchResult`` dataclass."""
    return SexMismatchResult(
        mismatch_males=tuple(convert_sample_stat(s) for s in proto.mismatch_males),
        mismatch_females=tuple(convert_sample_stat(s) for s in proto.mismatch_females),
        metadata=convert_response_metadata(proto),
    )


def convert_fstat_x_response(proto: pb2.FstatXResponse) -> FstatXResult:
    """Convert a ``pb2.FstatXResponse`` to a ``FstatXResult`` dataclass."""
    return FstatXResult(
        males=tuple(convert_sample_stat(s) for s in proto.males),
        females=tuple(convert_sample_stat(s) for s in proto.females),
        metadata=convert_response_metadata(proto),
    )


def convert_relatedness(proto: pb2.Relatedness) -> Relatedness:
    """Convert a ``pb2.Relatedness`` to a ``Relatedness`` dataclass."""
    return Relatedness(
        sample1=proto.sample1,
        sample2=proto.sample2,
        degree=KinshipDegree(proto.degree),
        phi_bwf=proto.phi_bwf,
    )


def convert_kinship_response(proto: pb2.KinshipResponse) -> KinshipResult:
    """Convert a ``pb2.KinshipResponse`` to a ``KinshipResult`` dataclass."""
    return KinshipResult(
        pairs=tuple(convert_relatedness(r) for r in proto.rel),
        metadata=convert_response_metadata(proto),
    )


def convert_sample_relatedness(proto: pb2.RelatednessPerSample) -> SampleRelatedness:
    """Convert a ``pb2.RelatednessPerSample`` to a ``SampleRelatedness`` dataclass.

    Field mapping (camelCase proto → snake_case Python):
        proto.nHetS1   → n_het_s1
        proto.nHetS2   → n_het_s2
        proto.nHetS1S2 → n_het_s1s2
        proto.nHomOp   → n_hom_op
    """
    return SampleRelatedness(
        sample=proto.sample,
        degree=KinshipDegree(proto.degree),
        phi_bwf=proto.phi_bwf,
        common_loci=proto.common_loci,
        n_het_s1=proto.nHetS1,
        n_het_s2=proto.nHetS2,
        n_het_s1s2=proto.nHetS1S2,
        n_hom_op=proto.nHomOp,
    )


def convert_sample_kinship_response(proto: pb2.SampleKinshipResponse) -> SampleKinshipResult:
    """Convert a ``pb2.SampleKinshipResponse`` to a ``SampleKinshipResult`` dataclass."""
    return SampleKinshipResult(
        relatives=tuple(convert_sample_relatedness(r) for r in proto.rel),
        accepted_snvs=proto.accepted_snvs,
        metadata=convert_response_metadata(proto),
    )


def convert_alleles_with_stats_response_to_top_hwe(
    proto: pb2.AllelesWithStatsResponse,
) -> TopHweResult:
    """Convert a ``pb2.AllelesWithStatsResponse`` (from TopNHWE) to ``TopHweResult``."""
    return TopHweResult(
        variants=tuple(convert_variant_with_stats(v) for v in proto.variants),
        metadata=convert_response_metadata(proto),
    )


def convert_alleles_with_stats_response_to_top_chi2(
    proto: pb2.AllelesWithStatsResponse,
) -> TopChi2Result:
    """Convert a ``pb2.AllelesWithStatsResponse`` (from TopNchi2) to ``TopChi2Result``."""
    return TopChi2Result(
        variants=tuple(convert_variant_with_stats(v) for v in proto.variants),
        metadata=convert_response_metadata(proto),
    )


# ---------------------------------------------------------------------------
# Python → proto (request conversion)
# ---------------------------------------------------------------------------


def annotation_filter_to_proto(af: AnnotationFilter) -> pb2.Annotations:
    """Convert an ``AnnotationFilter`` dataclass to a ``pb2.Annotations`` proto message.

    Maps all 25 ``AnnotationFilter`` snake_case fields to their proto
    counterparts.  The proto ``Annotations`` message uses camelCase for
    boolean fields:

        biallelic_only     → biallelicOnly
        multiallelic_only  → multiallelicOnly
        exclude_males      → excludeMales
        exclude_females    → excludeFemales

    And a different name for clinical significance:

        clin_significance  → clinsgn

    All other field names are identical between the dataclass and proto.
    Float fields that are ``None`` in the dataclass are omitted (proto
    default of 0.0 means "no filter").
    """
    kwargs: dict = {}

    # Repeated enum fields — pass int values (IntEnum is int-compatible)
    if af.variant_type:
        kwargs["variant_type"] = [int(v) for v in af.variant_type]
    if af.feature_type:
        kwargs["feature_type"] = [int(v) for v in af.feature_type]
    if af.bio_type:
        kwargs["bio_type"] = [int(v) for v in af.bio_type]
    if af.consequence:
        kwargs["consequence"] = [int(v) for v in af.consequence]
    if af.impact:
        kwargs["impact"] = [int(v) for v in af.impact]
    if af.clin_significance:
        kwargs["clinsgn"] = [int(v) for v in af.clin_significance]
    if af.sift:
        kwargs["sift"] = [int(v) for v in af.sift]
    if af.polyphen:
        kwargs["polyphen"] = [int(v) for v in af.polyphen]
    if af.am_class:
        kwargs["am_class"] = [int(v) for v in af.am_class]

    # Float fields — only set if not None (proto 0.0 = "no filter")
    if af.af_lt is not None:
        kwargs["af_lt"] = af.af_lt
    if af.af_gt is not None:
        kwargs["af_gt"] = af.af_gt
    if af.gnomad_exomes_af_lt is not None:
        kwargs["gnomad_exomes_af_lt"] = af.gnomad_exomes_af_lt
    if af.gnomad_exomes_af_gt is not None:
        kwargs["gnomad_exomes_af_gt"] = af.gnomad_exomes_af_gt
    if af.gnomad_genomes_af_lt is not None:
        kwargs["gnomad_genomes_af_lt"] = af.gnomad_genomes_af_lt
    if af.gnomad_genomes_af_gt is not None:
        kwargs["gnomad_genomes_af_gt"] = af.gnomad_genomes_af_gt
    if af.cadd_raw_lt is not None:
        kwargs["cadd_raw_lt"] = af.cadd_raw_lt
    if af.cadd_raw_gt is not None:
        kwargs["cadd_raw_gt"] = af.cadd_raw_gt
    if af.cadd_phred_lt is not None:
        kwargs["cadd_phred_lt"] = af.cadd_phred_lt
    if af.cadd_phred_gt is not None:
        kwargs["cadd_phred_gt"] = af.cadd_phred_gt
    if af.am_score_lt is not None:
        kwargs["am_score_lt"] = af.am_score_lt
    if af.am_score_gt is not None:
        kwargs["am_score_gt"] = af.am_score_gt

    # Boolean fields — camelCase proto names
    if af.biallelic_only:
        kwargs["biallelicOnly"] = True
    if af.multiallelic_only:
        kwargs["multiallelicOnly"] = True
    if af.exclude_males:
        kwargs["excludeMales"] = True
    if af.exclude_females:
        kwargs["excludeFemales"] = True

    return pb2.Annotations(**kwargs)
