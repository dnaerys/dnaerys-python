"""Enum types mirroring the Dnaerys proto enums, with string alias resolution.

All 12 ``IntEnum`` classes correspond 1:1 to the proto enums defined in
``dnaerys.proto`` (R1.17.8).  The ``UNSPECIFIED = 0`` sentinel from each proto
enum is deliberately excluded — it has no meaning in client code and would
pollute autocompletion.

Integer values match the proto exactly, so enum members can be passed directly
wherever the gRPC stub expects an integer enum value.
"""

from __future__ import annotations

import enum
from typing import TypeVar

__all__ = [
    "Chromosome",
    "RefAssembly",
    "VariantType",
    "FeatureType",
    "BioType",
    "Consequence",
    "Impact",
    "SIFT",
    "PolyPhen",
    "ClinSignificance",
    "AlphaMissense",
    "KinshipDegree",
    "resolve_chromosome",
    "resolve_enum",
    "resolve_assembly",
]

E = TypeVar("E", bound=enum.IntEnum)


# ---------------------------------------------------------------------------
# Enum definitions — values match dnaerys.proto R1.17.8 exactly
# ---------------------------------------------------------------------------


class Chromosome(enum.IntEnum):
    """Human chromosome identifiers.

    25 members: autosomes 1–22, sex chromosomes X and Y, and mitochondrial DNA.
    Integer values match the proto ``Chromosome`` enum (``CHR_1`` = 1 … ``CHR_MT`` = 25).
    ``CHROMOSOME_UNSPECIFIED`` (0) is excluded.
    """

    CHR_1 = 1
    CHR_2 = 2
    CHR_3 = 3
    CHR_4 = 4
    CHR_5 = 5
    CHR_6 = 6
    CHR_7 = 7
    CHR_8 = 8
    CHR_9 = 9
    CHR_10 = 10
    CHR_11 = 11
    CHR_12 = 12
    CHR_13 = 13
    CHR_14 = 14
    CHR_15 = 15
    CHR_16 = 16
    CHR_17 = 17
    CHR_18 = 18
    CHR_19 = 19
    CHR_20 = 20
    CHR_21 = 21
    CHR_22 = 22
    CHR_X = 23
    CHR_Y = 24
    CHR_MT = 25


class RefAssembly(enum.IntEnum):
    """Reference genome assembly versions.

    ``GRCh37`` (hg19) and ``GRCh38`` (hg38).  The Dnaerys server defaults to
    GRCh38 when the assembly is unspecified.
    """

    GRCh37 = 1
    GRCh38 = 2


class VariantType(enum.IntEnum):
    """Sequence Ontology variant class terms.

    34 members corresponding to the proto ``VariantType`` enum.
    See https://asia.ensembl.org/info/genome/variation/prediction/classification.html#classes
    """

    SNV = 1
    INSERTION = 2
    DELETION = 3
    INDEL = 4
    SUBSTITUTION = 5
    INVERSION = 6
    TRANSLOCATION = 7
    DUPLICATION = 8
    ALU_INSERTION = 9
    COMPLEX_STRUCTURAL_ALTERATION = 10
    COMPLEX_SUBSTITUTION = 11
    COPY_NUMBER_GAIN = 12
    COPY_NUMBER_LOSS = 13
    COPY_NUMBER_VARIATION = 14
    INTERCHROMOSOMAL_BREAKPOINT = 15
    INTERCHROMOSOMAL_TRANSLOCATION = 16
    INTRACHROMOSOMAL_BREAKPOINT = 17
    INTRACHROMOSOMAL_TRANSLOCATION = 18
    LOSS_OF_HETEROZYGOSITY = 19
    MOBILE_ELEMENT_DELETION = 20
    MOBILE_ELEMENT_INSERTION = 21
    NOVEL_SEQUENCE_INSERTION = 22
    SHORT_TANDEM_REPEAT_VARIATION = 23
    TANDEM_DUPLICATION = 24
    PROBE = 25
    ALU_DELETION = 26
    HERV_DELETION = 27
    HERV_INSERTION = 28
    LINE1_DELETION = 29
    LINE1_INSERTION = 30
    SVA_DELETION = 31
    SVA_INSERTION = 32
    COMPLEX_CHROMOSOMAL_REARRANGEMENT = 33
    SEQUENCE_ALTERATION = 34


class FeatureType(enum.IntEnum):
    """VEP feature types.

    3 members: ``TRANSCRIPT``, ``REGULATORYFEATURE``, ``MOTIFFEATURE``.
    """

    TRANSCRIPT = 1
    REGULATORYFEATURE = 2
    MOTIFFEATURE = 3


class BioType(enum.IntEnum):
    """VEP biotypes for transcripts and regulatory features.

    47 members corresponding to the proto ``BioType`` enum.
    See https://asia.ensembl.org/info/genome/genebuild/biotypes.html
    """

    PROCESSED_TRANSCRIPT = 1
    LNCRNA = 2
    ANTISENSE = 3
    MACRO_LNCRNA = 4
    NON_CODING = 5
    RETAINED_INTRON = 6
    SENSE_INTRONIC = 7
    SENSE_OVERLAPPING = 8
    LINCRNA = 9
    NCRNA = 10
    MIRNA = 11
    MISCRNA = 12
    PIRNA = 13
    RRNA = 14
    SIRNA = 15
    SNRNA = 16
    SNORNA = 17
    TRNA = 18
    VAULTRNA = 19
    PROTEIN_CODING = 20
    PSEUDOGENE = 21
    IG_PSEUDOGENE = 22
    POLYMORPHIC_PSEUDOGENE = 23
    PROCESSED_PSEUDOGENE = 24
    TRANSCRIBED_PSEUDOGENE = 25
    TRANSLATED_PSEUDOGENE = 26
    UNITARY_PSEUDOGENE = 27
    UNPROCESSED_PSEUDOGENE = 28
    READTHROUGH = 29
    STOP_CODON_READTHROUGH = 30
    TEC = 31
    TR_GENE = 32
    TR_C_GENE = 33
    TR_D_GENE = 34
    TR_J_GENE = 35
    TR_V_GENE = 36
    IG_GENE = 37
    IG_C_GENE = 38
    IG_D_GENE = 39
    IG_J_GENE = 40
    IG_V_GENE = 41
    NONSENSE_MEDIATED_DECAY = 42
    PROMOTER = 43
    PROMOTER_FLANKING_REGION = 44
    ENHANCER = 45
    CTCF_BINDING_SITE = 46
    OPEN_CHROMATIN_REGION = 47


class Consequence(enum.IntEnum):
    """Sequence Ontology variant consequence terms.

    41 members corresponding to the proto ``Consequence`` enum.
    See https://asia.ensembl.org/info/genome/variation/prediction/predicted_data.html#consequences
    """

    TRANSCRIPT_ABLATION = 1
    SPLICE_ACCEPTOR_VARIANT = 2
    SPLICE_DONOR_VARIANT = 3
    STOP_GAINED = 4
    FRAMESHIFT_VARIANT = 5
    STOP_LOST = 6
    START_LOST = 7
    TRANSCRIPT_AMPLIFICATION = 8
    INFRAME_INSERTION = 9
    INFRAME_DELETION = 10
    MISSENSE_VARIANT = 11
    PROTEIN_ALTERING_VARIANT = 12
    SPLICE_REGION_VARIANT = 13
    INCOMPLETE_TERMINAL_CODON_VARIANT = 14
    START_RETAINED_VARIANT = 15
    STOP_RETAINED_VARIANT = 16
    SYNONYMOUS_VARIANT = 17
    CODING_SEQUENCE_VARIANT = 18
    MATURE_MIRNA_VARIANT = 19
    FIVE_PRIME_UTR_VARIANT = 20
    THREE_PRIME_UTR_VARIANT = 21
    NON_CODING_TRANSCRIPT_EXON_VARIANT = 22
    INTRON_VARIANT = 23
    NMD_TRANSCRIPT_VARIANT = 24
    NON_CODING_TRANSCRIPT_VARIANT = 25
    UPSTREAM_GENE_VARIANT = 26
    DOWNSTREAM_GENE_VARIANT = 27
    TFBS_ABLATION = 28
    TFBS_AMPLIFICATION = 29
    TF_BINDING_SITE_VARIANT = 30
    REGULATORY_REGION_ABLATION = 31
    REGULATORY_REGION_AMPLIFICATION = 32
    FEATURE_ELONGATION = 33
    REGULATORY_REGION_VARIANT = 34
    FEATURE_TRUNCATION = 35
    INTERGENIC_VARIANT = 36
    SPLICE_POLYPYRIMIDINE_TRACT_VARIANT = 37
    SPLICE_DONOR_5TH_BASE_VARIANT = 38
    SPLICE_DONOR_REGION_VARIANT = 39
    CODING_TRANSCRIPT_VARIANT = 40
    SEQUENCE_VARIANT = 41


class Impact(enum.IntEnum):
    """VEP impact severity levels.

    4 members ordered from most to least severe:
    ``HIGH``, ``MODERATE``, ``LOW``, ``MODIFIER``.
    """

    HIGH = 1
    MODERATE = 2
    LOW = 3
    MODIFIER = 4


class SIFT(enum.IntEnum):
    """SIFT prediction terms for amino acid substitution impact.

    See https://sift.bii.a-star.edu.sg/
    """

    TOLERATED = 1
    DELETERIOUS = 2


class PolyPhen(enum.IntEnum):
    """PolyPhen-2 prediction terms for amino acid substitution impact."""

    BENIGN = 1
    POSSIBLY_DAMAGING = 2
    PROBABLY_DAMAGING = 3
    UNKNOWN = 4


class ClinSignificance(enum.IntEnum):
    """ClinVar clinical significance categories.

    19 members corresponding to the proto ``ClinSignificance`` enum.
    See https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/
    """

    CLNSIG_BENIGN = 1
    LIKELY_BENIGN = 2
    UNCERTAIN_SIGNIFICANCE = 3
    LIKELY_PATHOGENIC = 4
    PATHOGENIC = 5
    DRUG_RESPONSE = 6
    ASSOCIATION = 7
    RISK_FACTOR = 8
    PROTECTIVE = 9
    AFFECTS = 10
    CONFERS_SENSITIVITY = 11
    CONFLICTING_INTERPRETATIONS = 12
    NOT_PROVIDED = 13
    OTHER = 14
    LIKELY_PATHOGENIC_LOW_PENETRANCE = 15
    PATHOGENIC_LOW_PENETRANCE = 16
    UNCERTAIN_RISK_ALLELE = 17
    LIKELY_RISK_ALLELE = 18
    ESTABLISHED_RISK_ALLELE = 19


class AlphaMissense(enum.IntEnum):
    """AlphaMissense pathogenicity classification.

    See https://www.science.org/doi/10.1126/science.adg7492

    Thresholds: ``AM_LIKELY_BENIGN`` (score < 0.34),
    ``AM_LIKELY_PATHOGENIC`` (score > 0.564), ``AM_AMBIGUOUS`` (otherwise).
    """

    AM_LIKELY_BENIGN = 1
    AM_LIKELY_PATHOGENIC = 2
    AM_AMBIGUOUS = 3


class KinshipDegree(enum.IntEnum):
    """Kinship relatedness degree classifications.

    Based on the KING robust kinship estimator phi_bwf thresholds:
    ``TWINS_MONOZYGOTIC`` (> 0.354), ``FIRST_DEGREE`` (0.177–0.354),
    ``SECOND_DEGREE`` (0.0884–0.177), ``THIRD_DEGREE`` (0.0442–0.0884),
    ``UNRELATED`` (< 0.0442).

    See https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3025716
    """

    TWINS_MONOZYGOTIC = 1
    FIRST_DEGREE = 2
    SECOND_DEGREE = 3
    THIRD_DEGREE = 4
    UNRELATED = 5


# ---------------------------------------------------------------------------
# Chromosome alias lookup — explicit dict, no fuzzy matching
# ---------------------------------------------------------------------------

def _build_chromosome_aliases() -> dict[str, Chromosome]:
    """Build a case-insensitive alias dict for chromosome resolution.

    All keys are stored lowercase.  The following alias forms are supported
    for each chromosome:

    Autosomes 1–22:
        ``"chr1"``, ``"chr_1"``, ``"1"`` → ``Chromosome.CHR_1``

    Sex chromosomes:
        ``"chrx"``, ``"chr_x"``, ``"x"`` → ``Chromosome.CHR_X``
        ``"chry"``, ``"chr_y"``, ``"y"`` → ``Chromosome.CHR_Y``

    Mitochondrial:
        ``"chrmt"``, ``"chr_mt"``, ``"mt"`` → ``Chromosome.CHR_MT``
    """
    aliases: dict[str, Chromosome] = {}

    # Autosomes 1–22
    for i in range(1, 23):
        member = Chromosome(i)
        aliases[str(i)] = member
        aliases[f"chr{i}"] = member
        aliases[f"chr_{i}"] = member

    # Sex chromosomes
    aliases["x"] = Chromosome.CHR_X
    aliases["chrx"] = Chromosome.CHR_X
    aliases["chr_x"] = Chromosome.CHR_X

    aliases["y"] = Chromosome.CHR_Y
    aliases["chry"] = Chromosome.CHR_Y
    aliases["chr_y"] = Chromosome.CHR_Y

    # Mitochondrial
    aliases["mt"] = Chromosome.CHR_MT
    aliases["chrmt"] = Chromosome.CHR_MT
    aliases["chr_mt"] = Chromosome.CHR_MT

    return aliases


_CHROMOSOME_ALIASES: dict[str, Chromosome] = _build_chromosome_aliases()


# ---------------------------------------------------------------------------
# Resolution functions
# ---------------------------------------------------------------------------


def resolve_chromosome(value: Chromosome | str | int) -> Chromosome:
    """Resolve a chromosome identifier to a ``Chromosome`` enum member.

    Parameters
    ----------
    value : Chromosome | str | int
        Accepts:

        - A ``Chromosome`` enum member (returned as-is).
        - An integer 1–25 (converted via ``Chromosome(value)``).
        - A string alias (case-insensitive):
          ``"chr1"`` / ``"CHR_1"`` / ``"1"`` for autosomes,
          ``"chrX"`` / ``"X"`` for sex chromosomes,
          ``"chrMT"`` / ``"MT"`` for mitochondrial DNA.

    Returns
    -------
    Chromosome
        The resolved enum member.

    Raises
    ------
    ValueError
        If *value* is a string that does not match any known alias.
    TypeError
        If *value* is neither a ``Chromosome``, ``str``, nor ``int``.
    """
    if isinstance(value, Chromosome):
        return value

    if isinstance(value, int):
        return Chromosome(value)

    if isinstance(value, str):
        result = _CHROMOSOME_ALIASES.get(value.lower())
        if result is not None:
            return result

        valid = sorted(_CHROMOSOME_ALIASES.keys())
        raise ValueError(
            f"Unknown chromosome {value!r}. "
            f"Valid inputs: {', '.join(valid)}"
        )

    raise TypeError(
        f"Expected Chromosome, str, or int, got {type(value).__name__}"
    )


def resolve_enum(enum_cls: type[E], value: E | str) -> E:
    """Resolve a string to an enum member by exact name (case-insensitive).

    Parameters
    ----------
    enum_cls : type[IntEnum]
        The target enum class.
    value : IntEnum | str
        Either an existing member of *enum_cls* (returned as-is) or a string
        matching a member name case-insensitively.

    Returns
    -------
    IntEnum
        The resolved enum member.

    Raises
    ------
    ValueError
        If *value* is a string that does not match any member name in
        *enum_cls*.  The error message lists all valid member names.
    """
    if isinstance(value, enum_cls):
        return value

    if isinstance(value, str):
        upper = value.upper()
        for member in enum_cls:
            if member.name == upper:
                return member

        valid_names = [m.name for m in enum_cls]
        raise ValueError(
            f"Unknown {enum_cls.__name__} value {value!r}. "
            f"Valid values: {', '.join(valid_names)}"
        )

    raise TypeError(
        f"Expected {enum_cls.__name__} or str, got {type(value).__name__}"
    )


def resolve_assembly(value: RefAssembly | str) -> RefAssembly:
    """Resolve a reference assembly identifier to a ``RefAssembly`` enum member.

    Parameters
    ----------
    value : RefAssembly | str
        Accepts a ``RefAssembly`` member or a string: ``"GRCh37"``,
        ``"GRCh38"`` (case-insensitive).

    Returns
    -------
    RefAssembly
        The resolved enum member.

    Raises
    ------
    ValueError
        If *value* is a string that does not match a known assembly name.
    """
    if isinstance(value, RefAssembly):
        return value

    if isinstance(value, str):
        upper = value.upper()
        for member in RefAssembly:
            if member.name.upper() == upper:
                return member

        valid_names = [m.name for m in RefAssembly]
        raise ValueError(
            f"Unknown assembly {value!r}. "
            f"Valid values: {', '.join(valid_names)}"
        )

    raise TypeError(
        f"Expected RefAssembly or str, got {type(value).__name__}"
    )
