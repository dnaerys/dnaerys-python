"""Input and result dataclasses for the Dnaerys client library.

All dataclasses use ``frozen=True, slots=True`` for immutability and memory
efficiency.  Input types (``Region``, ``Bracket``, ``AnnotationFilter``)
perform validation and enum resolution in ``__post_init__``.  Result types
are plain data containers populated by the proto→dataclass conversion layer
(Stage 2).

Coordinates throughout the library are **1-based, inclusive** on both ends,
matching the Dnaerys proto convention.
"""

from __future__ import annotations

import warnings
from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Any

from dnaerys._enums import (
    AlphaMissense,
    BioType,
    Chromosome,
    ClinSignificance,
    Consequence,
    FeatureType,
    Impact,
    KinshipDegree,
    PolyPhen,
    RefAssembly,
    SIFT,
    VariantType,
    resolve_chromosome,
    resolve_enum,
)

__all__ = [
    # Input types
    "Region",
    "Bracket",
    "AnnotationFilter",
    # Core result types
    "Variant",
    "VariantWithStats",
    # Response wrappers
    "ResponseMetadata",
    "CountResult",
    "SamplesResult",
    "HealthResult",
    "ClusterNodesResult",
    "DatasetInfo",
    "Cohort",
    "PrsInfo",
    "PrsResult",
    "SampleScore",
    "SexMismatchResult",
    "SampleStat",
    "FstatXResult",
    "KinshipResult",
    "Relatedness",
    "SampleKinshipResult",
    "SampleRelatedness",
    "TopHweResult",
    "TopChi2Result",
]


# ---------------------------------------------------------------------------
# Input types
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Region:
    """A genomic region defined by chromosome, start, and end coordinates.

    Parameters
    ----------
    chr : Chromosome | str | int
        Chromosome identifier.  Strings like ``"chr1"``, ``"1"``, ``"X"``,
        ``"chrMT"`` are resolved to ``Chromosome`` enum members in
        ``__post_init__``.
    start : int
        1-based inclusive start position.  Must be >= 1.
    end : int
        1-based inclusive end position.  Must be >= *start*.
        For a single-nucleotide variant (SNV), ``start == end``.
    ref : str | None
        Reference allele.  Optional; ``None`` means no filtering by
        reference allele.
    alt : str | None
        Alternative allele.  Optional; ``None`` means no filtering by
        alternative allele.

    Raises
    ------
    ValueError
        If *start* < 1, or *end* < *start*, or *chr* cannot be resolved.
    """

    chr: Chromosome  # type: ignore[assignment]  # accepts str/int at construction
    start: int
    end: int
    ref: str | None = None
    alt: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "chr", resolve_chromosome(self.chr))

        if self.start < 1:
            raise ValueError(
                f"start must be >= 1, got {self.start}"
            )
        if self.end < self.start:
            raise ValueError(
                f"end ({self.end}) must be >= start ({self.start})"
            )


@dataclass(frozen=True, slots=True)
class Bracket:
    """A bracket query region for structural variant searches.

    Defines a pair of coordinate ranges: one for variant start positions
    (``start_min``–``start_max``) and one for end positions
    (``end_min``–``end_max``).  This follows the GA4GH Beacon Bracket Query
    specification.

    See https://docs.genomebeacons.org/variant-queries/#beacon-bracket-queries

    Parameters
    ----------
    chr : Chromosome | str | int
        Chromosome identifier, resolved in ``__post_init__``.
    start_min : int
        1-based inclusive minimum start position.  Must be >= 1.
    start_max : int
        1-based inclusive maximum start position.  Must be >= *start_min*.
    end_min : int
        1-based inclusive minimum end position.  Must be >= 1.
    end_max : int
        1-based inclusive maximum end position.  Must be >= *end_min*.
    ref : str | None
        Reference allele.  Optional.
    alt : str | None
        Alternative allele.  Optional.

    Raises
    ------
    ValueError
        If any position < 1, *start_min* > *start_max*, or
        *end_min* > *end_max*.
    """

    chr: Chromosome  # type: ignore[assignment]
    start_min: int
    start_max: int
    end_min: int
    end_max: int
    ref: str | None = None
    alt: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "chr", resolve_chromosome(self.chr))

        for name in ("start_min", "start_max", "end_min", "end_max"):
            val = getattr(self, name)
            if val < 1:
                raise ValueError(f"{name} must be >= 1, got {val}")

        if self.start_min > self.start_max:
            raise ValueError(
                f"start_min ({self.start_min}) must be <= start_max ({self.start_max})"
            )
        if self.end_min > self.end_max:
            raise ValueError(
                f"end_min ({self.end_min}) must be <= end_max ({self.end_max})"
            )


def _resolve_enum_sequence(
    enum_cls: type, values: Sequence[Any],
) -> tuple:
    """Resolve a sequence of enum members or strings to a tuple of enum members.

    Each element is passed through ``resolve_enum``; strings are resolved
    case-insensitively by name.  The result is a tuple for immutability.
    """
    return tuple(resolve_enum(enum_cls, v) for v in values)


def _warn_empty_range(
    lt_name: str,
    lt_val: float | None,
    gt_name: str,
    gt_val: float | None,
) -> None:
    """Emit a warning if a lt/gt pair defines an empty range.

    The server interprets ``field > gt_val AND field < lt_val``.  If
    ``gt_val >= lt_val``, no value can satisfy both conditions, so the
    filter produces no results.  This is warned (not raised) because the
    server accepts it.
    """
    if lt_val is not None and gt_val is not None and gt_val >= lt_val:
        warnings.warn(
            f"{gt_name} ({gt_val}) >= {lt_name} ({lt_val}): "
            f"filter defines an empty range (no value can satisfy "
            f"both {gt_name.split('.')[-1]} > {gt_val} and "
            f"{lt_name.split('.')[-1]} < {lt_val})",
            stacklevel=3,
        )


@dataclass(frozen=True, slots=True)
class AnnotationFilter:
    """Filter criteria for variant annotation-based queries.

    All enum sequence fields accept either enum members or strings (resolved
    case-insensitively at construction).  Fields within a repeated enum are
    OR'd together; different fields are AND'd.

    For float bound pairs (e.g. ``af_lt`` / ``af_gt``), the server applies
    ``field > gt AND field < lt``.  A value of ``None`` means "no filter"
    (the proto's 0.0 default, which means "unset", is mapped to ``None``
    for clarity).  Setting both with ``gt >= lt`` defines an empty range;
    a warning is emitted but the filter is still constructed.

    Parameters
    ----------
    variant_type : Sequence[VariantType | str]
        Sequence Ontology variant class terms to include (OR'd).
    feature_type : Sequence[FeatureType | str]
        VEP feature types to include (OR'd).
    bio_type : Sequence[BioType | str]
        VEP biotypes to include (OR'd).
    consequence : Sequence[Consequence | str]
        Sequence Ontology consequence terms to include (OR'd).
    impact : Sequence[Impact | str]
        VEP impact levels to include (OR'd).
    clin_significance : Sequence[ClinSignificance | str]
        ClinVar clinical significance categories to include (OR'd).
        Proto field name: ``clinsgn``.
    af_lt : float | None
        Include variants with dataset allele frequency < this value.
    af_gt : float | None
        Include variants with dataset allele frequency > this value.
    gnomad_exomes_af_lt : float | None
        Include variants with gnomAD exomes AF < this value.  Note: unannotated
        variants / those absent from gnomAD (gnomAD exomes AF = 0) are included.
    gnomad_exomes_af_gt : float | None
        Include variants with gnomAD exomes AF > this value.
    gnomad_genomes_af_lt : float | None
        Include variants with gnomAD genomes AF < this value.  Note: unannotated
        variants / those absent from gnomAD (gnomAD genomes AF = 0) are included.
    gnomad_genomes_af_gt : float | None
        Include variants with gnomAD genomes AF > this value.
    sift : Sequence[SIFT | str]
        SIFT prediction terms to include (OR'd).
    polyphen : Sequence[PolyPhen | str]
        PolyPhen prediction terms to include (OR'd).
    cadd_raw_lt : float | None
        Include variants with CADD raw score < this value.
    cadd_raw_gt : float | None
        Include variants with CADD raw score > this value.
    cadd_phred_lt : float | None
        Include variants with CADD phred score < this value.
    cadd_phred_gt : float | None
        Include variants with CADD phred score > this value.
    am_score_lt : float | None
        Include variants with AlphaMissense score < this value.
        Mutually exclusive with *am_class* — setting both raises
        ``ValueError`` because the server silently ignores ``am_class``
        when score bounds are present.
    am_score_gt : float | None
        Include variants with AlphaMissense score > this value.
        Mutually exclusive with *am_class*.
    am_class : Sequence[AlphaMissense | str]
        AlphaMissense pathogenicity classes to include (OR'd).
        Only effective when neither ``am_score_lt`` nor ``am_score_gt``
        are set.
    biallelic_only : bool
        If ``True``, include only biallelic sites (exclude multiallelic).
        Mutually exclusive with *multiallelic_only*.
    multiallelic_only : bool
        If ``True``, include only multiallelic sites (exclude biallelic).
        Mutually exclusive with *biallelic_only*.
    exclude_males : bool
        If ``True``, exclude male samples from selection.
        Mutually exclusive with *exclude_females*.
    exclude_females : bool
        If ``True``, exclude female samples from selection.
        Mutually exclusive with *exclude_males*.

    Raises
    ------
    ValueError
        If ``biallelic_only`` and ``multiallelic_only`` are both ``True``.
        If ``am_score_lt`` or ``am_score_gt`` is set together with a
        non-empty ``am_class``.
        If ``exclude_males`` and ``exclude_females`` are both ``True``.
        If an enum string value cannot be resolved.
    """

    variant_type: tuple[VariantType, ...] = ()
    feature_type: tuple[FeatureType, ...] = ()
    bio_type: tuple[BioType, ...] = ()
    consequence: tuple[Consequence, ...] = ()
    impact: tuple[Impact, ...] = ()
    clin_significance: tuple[ClinSignificance, ...] = ()
    af_lt: float | None = None
    af_gt: float | None = None
    gnomad_exomes_af_lt: float | None = None
    gnomad_exomes_af_gt: float | None = None
    gnomad_genomes_af_lt: float | None = None
    gnomad_genomes_af_gt: float | None = None
    sift: tuple[SIFT, ...] = ()
    polyphen: tuple[PolyPhen, ...] = ()
    cadd_raw_lt: float | None = None
    cadd_raw_gt: float | None = None
    cadd_phred_lt: float | None = None
    cadd_phred_gt: float | None = None
    am_score_lt: float | None = None
    am_score_gt: float | None = None
    am_class: tuple[AlphaMissense, ...] = ()
    biallelic_only: bool = False
    multiallelic_only: bool = False
    exclude_males: bool = False
    exclude_females: bool = False

    def __post_init__(self) -> None:
        # 1. Resolve all enum sequence fields from Sequence[Enum|str] → tuple[Enum,...]
        _enum_fields: list[tuple[str, type]] = [
            ("variant_type", VariantType),
            ("feature_type", FeatureType),
            ("bio_type", BioType),
            ("consequence", Consequence),
            ("impact", Impact),
            ("clin_significance", ClinSignificance),
            ("sift", SIFT),
            ("polyphen", PolyPhen),
            ("am_class", AlphaMissense),
        ]
        for attr, enum_cls in _enum_fields:
            raw = getattr(self, attr)
            resolved = _resolve_enum_sequence(enum_cls, raw)
            object.__setattr__(self, attr, resolved)

        # 2. Mutual exclusion: biallelic_only + multiallelic_only
        if self.biallelic_only and self.multiallelic_only:
            raise ValueError(
                "biallelic_only and multiallelic_only are mutually exclusive"
            )

        # 3. Mutual exclusion: am_score bounds + am_class
        if (self.am_score_lt is not None or self.am_score_gt is not None) and self.am_class:
            raise ValueError(
                "am_score_lt/am_score_gt and am_class are mutually exclusive: "
                "the server silently ignores am_class when score bounds are "
                "present. Use one or the other."
            )

        # 4. Mutual exclusion: exclude_males + exclude_females
        if self.exclude_males and self.exclude_females:
            raise ValueError(
                "exclude_males and exclude_females are mutually exclusive "
                "(both True would produce an empty result set)"
            )

        # 5–6. Warn on empty lt/gt ranges
        _range_pairs: list[tuple[str, str]] = [
            ("af_lt", "af_gt"),
            ("gnomad_exomes_af_lt", "gnomad_exomes_af_gt"),
            ("gnomad_genomes_af_lt", "gnomad_genomes_af_gt"),
            ("cadd_raw_lt", "cadd_raw_gt"),
            ("cadd_phred_lt", "cadd_phred_gt"),
            ("am_score_lt", "am_score_gt"),
        ]
        for lt_name, gt_name in _range_pairs:
            _warn_empty_range(
                lt_name, getattr(self, lt_name),
                gt_name, getattr(self, gt_name),
            )


# ---------------------------------------------------------------------------
# Result types — core data
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Variant:
    """A genomic variant with population-level statistics.

    All coordinates are 1-based, inclusive.  For SNVs, ``start == end``.

    Annotation float fields (``gnomad_exomes_af``, ``gnomad_genomes_af``,
    ``cadd_raw``, ``cadd_phred``, ``am_score``) use ``0.0`` as a sentinel
    meaning "not annotated" — this mirrors the proto convention where the
    default float value (0.0) indicates absence of annotation data.

    Parameters
    ----------
    chr : Chromosome
        Chromosome this variant is on.
    start : int
        1-based inclusive start position.
    end : int
        1-based inclusive end position.
    ref : str
        Reference allele (uppercase).
    alt : str
        Alternative allele (uppercase).
    af : float
        Dataset allele frequency.
    ac : float
        Dataset allele count.  ``float`` because heterozygous loci on sex
        chromosomes outside PAR in males are counted as 0.5.
    an : int
        Dataset allele number (excludes samples with missing genotypes).
    hom_samples : int
        Number of all samples with a homozygous genotype.
    het_samples : int
        Number of all samples with a heterozygous genotype.
    mis_samples : int
        Number of all samples with a missing (no-call) genotype.
    hom_samples_fx : int
        Number of female samples with a homozygous genotype in the X
        chromosome only; 0 outside X.
    het_samples_fx : int
        Number of female samples with a heterozygous genotype in the X
        chromosome only; 0 outside X.
    mis_samples_fx : int
        Number of female samples with a missing (no-call) genotype in the X
        chromosome only; 0 outside X.
    hom_samples_mxy : int
        Number of male samples with a homozygous genotype in the X & Y
        chromosomes only; 0 outside X and Y.
    het_samples_mxy : int
        Number of male samples with a heterozygous genotype in the X & Y
        chromosomes only; 0 outside X and Y.
    mis_samples_mxy : int
        Number of male samples with a missing (no-call) genotype in the X & Y
        chromosomes only; 0 outside X and Y.
    gnomad_exomes_af : float
        gnomAD exomes allele frequency.  0.0 = not annotated.
        Proto field: ``gnomADe``.
    gnomad_genomes_af : float
        gnomAD genomes allele frequency.  0.0 = not annotated.
        Proto field: ``gnomADg``.
    cadd_raw : float
        CADD raw score.  0.0 = not annotated.
    cadd_phred : float
        CADD phred-scaled score.  0.0 = not annotated.
    am_score : float
        AlphaMissense pathogenicity score.  0.0 = not annotated.
    amino_acids : str
        Amino acid substitution (HGVSp or VEP Amino_acids notation).
    biallelic : bool
        Whether the variant was biallelic in the input VCFs.
    """

    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    af: float
    ac: float
    an: int
    hom_samples: int
    het_samples: int
    mis_samples: int
    hom_samples_fx: int
    het_samples_fx: int
    mis_samples_fx: int
    hom_samples_mxy: int
    het_samples_mxy: int
    mis_samples_mxy: int
    gnomad_exomes_af: float
    gnomad_genomes_af: float
    cadd_raw: float
    cadd_phred: float
    am_score: float
    amino_acids: str
    biallelic: bool


@dataclass(frozen=True, slots=True)
class VariantWithStats:
    """A variant with additional virtual-cohort counters and population statistics.

    All ``Variant`` fields are flattened (not nested) for ergonomic access.
    The virtual cohort counters (``vaf``, ``vac``, etc.) reflect the subset
    of samples specified in the query.  The population statistics (``phwe``,
    ``pchi2``, etc.) are computed over the full dataset population.

    The ``odds_ratio`` field corresponds to the proto field ``or``, which is
    a Python reserved keyword and cannot be used as an attribute name.

    All annotation float sentinels and coordinate conventions are identical
    to ``Variant``.

    Parameters
    ----------
    chr–biallelic : see ``Variant``
    vaf : float
        Virtual cohort allele frequency.
    vac : float
        Virtual cohort allele count.
    van : int
        Virtual cohort allele number.
    v_hom_samples : int
        Number of samples with a homozygous genotype within the virtual cohort.
    v_het_samples : int
        Number of samples with a heterozygous genotype within the virtual cohort.
    v_hom_samples_fx : int
        Number of female samples with a homozygous genotype in the X chromosome
        only within the virtual cohort; 0 outside X.
    v_het_samples_fx : int
        Number of female samples with a heterozygous genotype in the X chromosome
        only within the virtual cohort; 0 outside X.
    v_hom_samples_mxy : int
        Number of male samples with a homozygous genotype in the X & Y
        chromosomes only within the virtual cohort; 0 outside X and Y.
    v_het_samples_mxy : int
        Number of male samples with a heterozygous genotype in the X & Y
        chromosomes only within the virtual cohort; 0 outside X and Y.
    phwe : float
        P-value for Hardy-Weinberg equilibrium chi-squared test.
    pchi2 : float
        P-value for Pearson's chi-squared test (cases vs. controls).
    odds_ratio : float
        Odds ratio from the chi-squared test.  Proto field: ``or``.
    ibc : float
        F-statistic (inbreeding coefficient).
    """

    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    af: float
    ac: float
    an: int
    hom_samples: int
    het_samples: int
    mis_samples: int
    hom_samples_fx: int
    het_samples_fx: int
    mis_samples_fx: int
    hom_samples_mxy: int
    het_samples_mxy: int
    mis_samples_mxy: int
    gnomad_exomes_af: float
    gnomad_genomes_af: float
    cadd_raw: float
    cadd_phred: float
    am_score: float
    amino_acids: str
    biallelic: bool
    vaf: float
    vac: float
    van: int
    v_hom_samples: int
    v_het_samples: int
    v_hom_samples_fx: int
    v_het_samples_fx: int
    v_hom_samples_mxy: int
    v_het_samples_mxy: int
    phwe: float
    pchi2: float
    odds_ratio: float
    ibc: float


# ---------------------------------------------------------------------------
# Result types — response wrappers
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ResponseMetadata:
    """Metadata from a Dnaerys server response.

    Carried by most response types to provide timing, node identification,
    and cluster health information.

    Parameters
    ----------
    elapsed_ms : int
        Server-side wall-clock time from request receipt to response, in
        milliseconds.
    elapsed_db_ms : int
        Database engine processing time, in milliseconds.
    node_id : str
        Identifier of the cluster node that served the response.
    incomplete_cluster : bool
        ``True`` if the cluster had unreachable nodes at response time.
    affected : bool
        ``True`` if unreachable nodes could have affected the completeness
        of this response.  Only meaningful when ``incomplete_cluster`` is
        also ``True``.
    """

    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    incomplete_cluster: bool
    affected: bool


@dataclass(frozen=True, slots=True)
class CountResult:
    """Result from a variant or sample count query.

    The result is a dataclass, not an int.  Arithmetic requires accessing
    ``.count`` explicitly: ``result.count + 10``, not ``result + 10``.

    Parameters
    ----------
    count : int
        The number of matching variants or samples.
    metadata : ResponseMetadata
        Server response metadata (timing, cluster health).
    """

    count: int
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class SamplesResult:
    """Result from a sample selection query.

    Parameters
    ----------
    samples : tuple[str, ...]
        Unique sample names matching the query criteria.
    metadata : ResponseMetadata
        Server response metadata.
    """

    samples: tuple[str, ...]
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class HealthResult:
    """Result from the Health RPC.

    Parameters
    ----------
    status : str
        Server health status string (e.g. ``"ok"``).
    """

    status: str


@dataclass(frozen=True, slots=True)
class ClusterNodesResult:
    """Result from the ClusterNodes RPC.

    Parameters
    ----------
    active_nodes : tuple[str, ...]
        Names/IDs of nodes in the "up" state.
    inactive_nodes : tuple[str, ...]
        Names/IDs of nodes in any state other than "up".
    total_nodes : int
        Total number of nodes in the cluster at the time of the request.
    elapsed_ms : int
        Server-side wall-clock time in milliseconds.
    """

    active_nodes: tuple[str, ...]
    inactive_nodes: tuple[str, ...]
    total_nodes: int
    elapsed_ms: int


@dataclass(frozen=True, slots=True)
class Cohort:
    """A sample cohort within a dataset.

    Parameters
    ----------
    cohort_name : str
        Name of the cohort.
    samples_count : int
        Total number of samples in the cohort.
    female_count : int
        Number of female samples.
    male_count : int
        Number of male samples.
    female_sample_names : tuple[str, ...]
        Female sample names.  Proto field: ``female_samples_names``.
    male_sample_names : tuple[str, ...]
        Male sample names.  Proto field: ``male_samples_names``.
    synthetic : bool
        Whether the cohort is synthetic.
    """

    cohort_name: str
    samples_count: int
    female_count: int
    male_count: int
    female_sample_names: tuple[str, ...]
    male_sample_names: tuple[str, ...]
    synthetic: bool


@dataclass(frozen=True, slots=True)
class PrsInfo:
    """Polygenic risk score catalog entry.

    Parameters
    ----------
    name : str
        PRS name as loaded into the dataset.
    description : str
        PRS description.  Proto field: ``desc``.
    cardinality : int
        Number of effect alleles in the PRS.
    """

    name: str
    description: str
    cardinality: int


@dataclass(frozen=True, slots=True)
class DatasetInfo:
    """Comprehensive dataset metadata from the DatasetInfo RPC.

    Parameters
    ----------
    cohorts : tuple[Cohort, ...]
        Cohorts within the dataset.
    samples_total : int
        Total number of samples in the dataset.
    females_total : int
        Total number of female samples.
    males_total : int
        Total number of male samples.
    variants_total : int
        Total number of variants in the dataset.
    assembly : RefAssembly
        Reference genome assembly.
    rto : bool
        Whether the dataset is in runtime-optimized mode.
    prs : tuple[PrsInfo, ...]
        Available PRS catalogs.
    timestamp : str
        Dataset creation timestamp.
    data_format : int
        Data format version.
    notes : str
        Freeform notes.
    rings_total : int
        Total number of data rings.
    elapsed_ms : int
        Server-side wall-clock time in milliseconds.
    node_id : str
        Node that served the response.
    max_variants_per_ring : int
        Hard cap on the number of variants each individual ring returns per
        request.  A query may request fewer, but never more, from any one ring.
        ``0`` if the server did not advertise a cap (older servers); the client
        then falls back to a built-in default.  Used internally to size
        pagination buffers and strong-``limit`` batches so results are complete.
    """

    cohorts: tuple[Cohort, ...]
    samples_total: int
    females_total: int
    males_total: int
    variants_total: int
    assembly: RefAssembly
    rto: bool
    prs: tuple[PrsInfo, ...]
    timestamp: str
    data_format: int
    notes: str
    rings_total: int
    elapsed_ms: int
    node_id: str
    max_variants_per_ring: int = 0


@dataclass(frozen=True, slots=True)
class Relatedness:
    """Pairwise relatedness result between two samples.

    Parameters
    ----------
    sample1 : str
        First sample name.
    sample2 : str
        Second sample name.
    degree : KinshipDegree
        Estimated degree of relatedness.
    phi_bwf : float
        KING "between-family" robust kinship coefficient.
    """

    sample1: str
    sample2: str
    degree: KinshipDegree
    phi_bwf: float


@dataclass(frozen=True, slots=True)
class KinshipResult:
    """Result from Kinship, KinshipDuo, or KinshipTrio RPCs.

    Parameters
    ----------
    pairs : tuple[Relatedness, ...]
        Pairwise relatedness estimates.
    metadata : ResponseMetadata
        Server response metadata.
    """

    pairs: tuple[Relatedness, ...]
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class SampleRelatedness:
    """Relatedness of a dataset sample to an external sample of interest.

    Parameters
    ----------
    sample : str
        Dataset sample name.
    degree : KinshipDegree
        Estimated degree of relatedness.
    phi_bwf : float
        KING kinship coefficient.
    common_loci : int
        Number of common autosomal biallelic SNV loci used for the estimate.
    n_het_s1 : int
        Heterozygous alt GT count in the external sample.
        Proto field: ``nHetS1``.
    n_het_s2 : int
        Heterozygous alt GT count in the dataset sample.
        Proto field: ``nHetS2``.
    n_het_s1s2 : int
        Loci where both samples are heterozygous.
        Proto field: ``nHetS1S2``.
    n_hom_op : int
        Loci where samples are opposite homozygous.
        Proto field: ``nHomOp``.
    """

    sample: str
    degree: KinshipDegree
    phi_bwf: float
    common_loci: int
    n_het_s1: int
    n_het_s2: int
    n_het_s1s2: int
    n_hom_op: int


@dataclass(frozen=True, slots=True)
class SampleKinshipResult:
    """Result from the SampleKinship RPC (external sample vs. dataset).

    Parameters
    ----------
    relatives : tuple[SampleRelatedness, ...]
        Related dataset samples and their kinship measures.
    accepted_snvs : int
        Number of valid autosomal biallelic SNVs accepted from the input VCF.
    metadata : ResponseMetadata
        Server response metadata.
    """

    relatives: tuple[SampleRelatedness, ...]
    accepted_snvs: int
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class SampleScore:
    """Per-sample polygenic risk score from the PRS RPC.

    Parameters
    ----------
    sample : str
        Sample name.
    scores_sum : float
        Sum of PRS scores (equivalent to Plink ``--score sum``).
    hethom_cardinality : int
        Number of effect alleles with het or hom genotypes contributing
        to ``scores_sum``.
    ref_cardinality : int
        Number of effect alleles with reference genotypes.  Negative in
        runtime-optimized mode.
    mis_cardinality : int
        Number of effect alleles with missing genotypes.
    imputed_sum : float
        Sum of imputed scores for missing alleles.
    """

    sample: str
    scores_sum: float
    hethom_cardinality: int
    ref_cardinality: int
    mis_cardinality: int
    imputed_sum: float


@dataclass(frozen=True, slots=True)
class PrsResult:
    """Result from the PRS RPC.

    Parameters
    ----------
    prs_name : str
        PRS name.
    sample_scores : tuple[SampleScore, ...]
        Per-sample PRS scores.
    dominant : bool
        Whether the ``dominant`` scoring mode was used.
    recessive : bool
        Whether the ``recessive`` scoring mode was used.
    prs_cardinality : int
        Total number of effect variants in the PRS.
    metadata : ResponseMetadata
        Server response metadata.
    """

    prs_name: str
    sample_scores: tuple[SampleScore, ...]
    dominant: bool
    recessive: bool
    prs_cardinality: int
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class SampleStat:
    """Per-sample sex statistics from SexMismatch or FstatX RPCs.

    Parameters
    ----------
    sample : str
        Sample name.
    reported_sex : str
        Sex as reported during ETL.
    observed_sex : str
        Sex as observed via F-statistic analysis.
    f_stat : float
        F-statistic value for the sample.
    """

    sample: str
    reported_sex: str
    observed_sex: str
    f_stat: float


@dataclass(frozen=True, slots=True)
class SexMismatchResult:
    """Result from the SexMismatchCheck RPC.

    Parameters
    ----------
    mismatch_males : tuple[SampleStat, ...]
        Samples reported as male but observed as female.
    mismatch_females : tuple[SampleStat, ...]
        Samples reported as female but observed as male.
    metadata : ResponseMetadata
        Server response metadata.
    """

    mismatch_males: tuple[SampleStat, ...]
    mismatch_females: tuple[SampleStat, ...]
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class FstatXResult:
    """Result from the FstatX RPC.

    Parameters
    ----------
    males : tuple[SampleStat, ...]
        F-statistics for samples with reported male sex.
    females : tuple[SampleStat, ...]
        F-statistics for samples with reported female sex.
    metadata : ResponseMetadata
        Server response metadata.
    """

    males: tuple[SampleStat, ...]
    females: tuple[SampleStat, ...]
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class TopHweResult:
    """Result from the TopNHWE RPC.

    Parameters
    ----------
    variants : tuple[VariantWithStats, ...]
        Top N variants by HWE p-value significance.
    metadata : ResponseMetadata
        Server response metadata.
    """

    variants: tuple[VariantWithStats, ...]
    metadata: ResponseMetadata


@dataclass(frozen=True, slots=True)
class TopChi2Result:
    """Result from the TopNchi2 RPC.

    Parameters
    ----------
    variants : tuple[VariantWithStats, ...]
        Top N variants by chi-squared test p-value significance.
    metadata : ResponseMetadata
        Server response metadata.
    """

    variants: tuple[VariantWithStats, ...]
    metadata: ResponseMetadata
