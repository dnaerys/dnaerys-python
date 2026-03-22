from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RefAssembly(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ASSEMBLY_UNSPECIFIED: _ClassVar[RefAssembly]
    GRCh37: _ClassVar[RefAssembly]
    GRCh38: _ClassVar[RefAssembly]

class Chromosome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHROMOSOME_UNSPECIFIED: _ClassVar[Chromosome]
    CHR_1: _ClassVar[Chromosome]
    CHR_2: _ClassVar[Chromosome]
    CHR_3: _ClassVar[Chromosome]
    CHR_4: _ClassVar[Chromosome]
    CHR_5: _ClassVar[Chromosome]
    CHR_6: _ClassVar[Chromosome]
    CHR_7: _ClassVar[Chromosome]
    CHR_8: _ClassVar[Chromosome]
    CHR_9: _ClassVar[Chromosome]
    CHR_10: _ClassVar[Chromosome]
    CHR_11: _ClassVar[Chromosome]
    CHR_12: _ClassVar[Chromosome]
    CHR_13: _ClassVar[Chromosome]
    CHR_14: _ClassVar[Chromosome]
    CHR_15: _ClassVar[Chromosome]
    CHR_16: _ClassVar[Chromosome]
    CHR_17: _ClassVar[Chromosome]
    CHR_18: _ClassVar[Chromosome]
    CHR_19: _ClassVar[Chromosome]
    CHR_20: _ClassVar[Chromosome]
    CHR_21: _ClassVar[Chromosome]
    CHR_22: _ClassVar[Chromosome]
    CHR_X: _ClassVar[Chromosome]
    CHR_Y: _ClassVar[Chromosome]
    CHR_MT: _ClassVar[Chromosome]

class VariantType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    VARIANTTYPE_UNSPECIFIED: _ClassVar[VariantType]
    SNV: _ClassVar[VariantType]
    INSERTION: _ClassVar[VariantType]
    DELETION: _ClassVar[VariantType]
    INDEL: _ClassVar[VariantType]
    SUBSTITUTION: _ClassVar[VariantType]
    INVERSION: _ClassVar[VariantType]
    TRANSLOCATION: _ClassVar[VariantType]
    DUPLICATION: _ClassVar[VariantType]
    ALU_INSERTION: _ClassVar[VariantType]
    COMPLEX_STRUCTURAL_ALTERATION: _ClassVar[VariantType]
    COMPLEX_SUBSTITUTION: _ClassVar[VariantType]
    COPY_NUMBER_GAIN: _ClassVar[VariantType]
    COPY_NUMBER_LOSS: _ClassVar[VariantType]
    COPY_NUMBER_VARIATION: _ClassVar[VariantType]
    INTERCHROMOSOMAL_BREAKPOINT: _ClassVar[VariantType]
    INTERCHROMOSOMAL_TRANSLOCATION: _ClassVar[VariantType]
    INTRACHROMOSOMAL_BREAKPOINT: _ClassVar[VariantType]
    INTRACHROMOSOMAL_TRANSLOCATION: _ClassVar[VariantType]
    LOSS_OF_HETEROZYGOSITY: _ClassVar[VariantType]
    MOBILE_ELEMENT_DELETION: _ClassVar[VariantType]
    MOBILE_ELEMENT_INSERTION: _ClassVar[VariantType]
    NOVEL_SEQUENCE_INSERTION: _ClassVar[VariantType]
    SHORT_TANDEM_REPEAT_VARIATION: _ClassVar[VariantType]
    TANDEM_DUPLICATION: _ClassVar[VariantType]
    PROBE: _ClassVar[VariantType]
    ALU_DELETION: _ClassVar[VariantType]
    HERV_DELETION: _ClassVar[VariantType]
    HERV_INSERTION: _ClassVar[VariantType]
    LINE1_DELETION: _ClassVar[VariantType]
    LINE1_INSERTION: _ClassVar[VariantType]
    SVA_DELETION: _ClassVar[VariantType]
    SVA_INSERTION: _ClassVar[VariantType]
    COMPLEX_CHROMOSOMAL_REARRANGEMENT: _ClassVar[VariantType]
    SEQUENCE_ALTERATION: _ClassVar[VariantType]

class FeatureType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FEATURETYPE_UNSPECIFIED: _ClassVar[FeatureType]
    TRANSCRIPT: _ClassVar[FeatureType]
    REGULATORYFEATURE: _ClassVar[FeatureType]
    MOTIFFEATURE: _ClassVar[FeatureType]

class BioType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    BIOTYPE_UNSPECIFIED: _ClassVar[BioType]
    PROCESSED_TRANSCRIPT: _ClassVar[BioType]
    LNCRNA: _ClassVar[BioType]
    ANTISENSE: _ClassVar[BioType]
    MACRO_LNCRNA: _ClassVar[BioType]
    NON_CODING: _ClassVar[BioType]
    RETAINED_INTRON: _ClassVar[BioType]
    SENSE_INTRONIC: _ClassVar[BioType]
    SENSE_OVERLAPPING: _ClassVar[BioType]
    LINCRNA: _ClassVar[BioType]
    NCRNA: _ClassVar[BioType]
    MIRNA: _ClassVar[BioType]
    MISCRNA: _ClassVar[BioType]
    PIRNA: _ClassVar[BioType]
    RRNA: _ClassVar[BioType]
    SIRNA: _ClassVar[BioType]
    SNRNA: _ClassVar[BioType]
    SNORNA: _ClassVar[BioType]
    TRNA: _ClassVar[BioType]
    VAULTRNA: _ClassVar[BioType]
    PROTEIN_CODING: _ClassVar[BioType]
    PSEUDOGENE: _ClassVar[BioType]
    IG_PSEUDOGENE: _ClassVar[BioType]
    POLYMORPHIC_PSEUDOGENE: _ClassVar[BioType]
    PROCESSED_PSEUDOGENE: _ClassVar[BioType]
    TRANSCRIBED_PSEUDOGENE: _ClassVar[BioType]
    TRANSLATED_PSEUDOGENE: _ClassVar[BioType]
    UNITARY_PSEUDOGENE: _ClassVar[BioType]
    UNPROCESSED_PSEUDOGENE: _ClassVar[BioType]
    READTHROUGH: _ClassVar[BioType]
    STOP_CODON_READTHROUGH: _ClassVar[BioType]
    TEC: _ClassVar[BioType]
    TR_GENE: _ClassVar[BioType]
    TR_C_GENE: _ClassVar[BioType]
    TR_D_GENE: _ClassVar[BioType]
    TR_J_GENE: _ClassVar[BioType]
    TR_V_GENE: _ClassVar[BioType]
    IG_GENE: _ClassVar[BioType]
    IG_C_GENE: _ClassVar[BioType]
    IG_D_GENE: _ClassVar[BioType]
    IG_J_GENE: _ClassVar[BioType]
    IG_V_GENE: _ClassVar[BioType]
    NONSENSE_MEDIATED_DECAY: _ClassVar[BioType]
    PROMOTER: _ClassVar[BioType]
    PROMOTER_FLANKING_REGION: _ClassVar[BioType]
    ENHANCER: _ClassVar[BioType]
    CTCF_BINDING_SITE: _ClassVar[BioType]
    OPEN_CHROMATIN_REGION: _ClassVar[BioType]

class Consequence(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CONSEQUENCE_UNSPECIFIED: _ClassVar[Consequence]
    TRANSCRIPT_ABLATION: _ClassVar[Consequence]
    SPLICE_ACCEPTOR_VARIANT: _ClassVar[Consequence]
    SPLICE_DONOR_VARIANT: _ClassVar[Consequence]
    STOP_GAINED: _ClassVar[Consequence]
    FRAMESHIFT_VARIANT: _ClassVar[Consequence]
    STOP_LOST: _ClassVar[Consequence]
    START_LOST: _ClassVar[Consequence]
    TRANSCRIPT_AMPLIFICATION: _ClassVar[Consequence]
    INFRAME_INSERTION: _ClassVar[Consequence]
    INFRAME_DELETION: _ClassVar[Consequence]
    MISSENSE_VARIANT: _ClassVar[Consequence]
    PROTEIN_ALTERING_VARIANT: _ClassVar[Consequence]
    SPLICE_REGION_VARIANT: _ClassVar[Consequence]
    INCOMPLETE_TERMINAL_CODON_VARIANT: _ClassVar[Consequence]
    START_RETAINED_VARIANT: _ClassVar[Consequence]
    STOP_RETAINED_VARIANT: _ClassVar[Consequence]
    SYNONYMOUS_VARIANT: _ClassVar[Consequence]
    CODING_SEQUENCE_VARIANT: _ClassVar[Consequence]
    MATURE_MIRNA_VARIANT: _ClassVar[Consequence]
    FIVE_PRIME_UTR_VARIANT: _ClassVar[Consequence]
    THREE_PRIME_UTR_VARIANT: _ClassVar[Consequence]
    NON_CODING_TRANSCRIPT_EXON_VARIANT: _ClassVar[Consequence]
    INTRON_VARIANT: _ClassVar[Consequence]
    NMD_TRANSCRIPT_VARIANT: _ClassVar[Consequence]
    NON_CODING_TRANSCRIPT_VARIANT: _ClassVar[Consequence]
    UPSTREAM_GENE_VARIANT: _ClassVar[Consequence]
    DOWNSTREAM_GENE_VARIANT: _ClassVar[Consequence]
    TFBS_ABLATION: _ClassVar[Consequence]
    TFBS_AMPLIFICATION: _ClassVar[Consequence]
    TF_BINDING_SITE_VARIANT: _ClassVar[Consequence]
    REGULATORY_REGION_ABLATION: _ClassVar[Consequence]
    REGULATORY_REGION_AMPLIFICATION: _ClassVar[Consequence]
    FEATURE_ELONGATION: _ClassVar[Consequence]
    REGULATORY_REGION_VARIANT: _ClassVar[Consequence]
    FEATURE_TRUNCATION: _ClassVar[Consequence]
    INTERGENIC_VARIANT: _ClassVar[Consequence]
    SPLICE_POLYPYRIMIDINE_TRACT_VARIANT: _ClassVar[Consequence]
    SPLICE_DONOR_5TH_BASE_VARIANT: _ClassVar[Consequence]
    SPLICE_DONOR_REGION_VARIANT: _ClassVar[Consequence]
    CODING_TRANSCRIPT_VARIANT: _ClassVar[Consequence]
    SEQUENCE_VARIANT: _ClassVar[Consequence]

class Impact(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    IMPACT_UNSPECIFIED: _ClassVar[Impact]
    HIGH: _ClassVar[Impact]
    MODERATE: _ClassVar[Impact]
    LOW: _ClassVar[Impact]
    MODIFIER: _ClassVar[Impact]

class SIFT(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SIFT_UNSPECIFIED: _ClassVar[SIFT]
    TOLERATED: _ClassVar[SIFT]
    DELETERIOUS: _ClassVar[SIFT]

class PolyPhen(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POLYPHEN_UNSPECIFIED: _ClassVar[PolyPhen]
    BENIGN: _ClassVar[PolyPhen]
    POSSIBLY_DAMAGING: _ClassVar[PolyPhen]
    PROBABLY_DAMAGING: _ClassVar[PolyPhen]
    UNKNOWN: _ClassVar[PolyPhen]

class ClinSignificance(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CLNSIG_UNSPECIFIED: _ClassVar[ClinSignificance]
    CLNSIG_BENIGN: _ClassVar[ClinSignificance]
    LIKELY_BENIGN: _ClassVar[ClinSignificance]
    UNCERTAIN_SIGNIFICANCE: _ClassVar[ClinSignificance]
    LIKELY_PATHOGENIC: _ClassVar[ClinSignificance]
    PATHOGENIC: _ClassVar[ClinSignificance]
    DRUG_RESPONSE: _ClassVar[ClinSignificance]
    ASSOCIATION: _ClassVar[ClinSignificance]
    RISK_FACTOR: _ClassVar[ClinSignificance]
    PROTECTIVE: _ClassVar[ClinSignificance]
    AFFECTS: _ClassVar[ClinSignificance]
    CONFERS_SENSITIVITY: _ClassVar[ClinSignificance]
    CONFLICTING_INTERPRETATIONS: _ClassVar[ClinSignificance]
    NOT_PROVIDED: _ClassVar[ClinSignificance]
    OTHER: _ClassVar[ClinSignificance]
    LIKELY_PATHOGENIC_LOW_PENETRANCE: _ClassVar[ClinSignificance]
    PATHOGENIC_LOW_PENETRANCE: _ClassVar[ClinSignificance]
    UNCERTAIN_RISK_ALLELE: _ClassVar[ClinSignificance]
    LIKELY_RISK_ALLELE: _ClassVar[ClinSignificance]
    ESTABLISHED_RISK_ALLELE: _ClassVar[ClinSignificance]

class AlphaMissense(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    AM_UNSPECIFIED: _ClassVar[AlphaMissense]
    AM_LIKELY_BENIGN: _ClassVar[AlphaMissense]
    AM_LIKELY_PATHOGENIC: _ClassVar[AlphaMissense]
    AM_AMBIGUOUS: _ClassVar[AlphaMissense]

class KinshipDegree(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    KINSHIP_UNSPECIFIED: _ClassVar[KinshipDegree]
    TWINS_MONOZYGOTIC: _ClassVar[KinshipDegree]
    FIRST_DEGREE: _ClassVar[KinshipDegree]
    SECOND_DEGREE: _ClassVar[KinshipDegree]
    THIRD_DEGREE: _ClassVar[KinshipDegree]
    UNRELATED: _ClassVar[KinshipDegree]
ASSEMBLY_UNSPECIFIED: RefAssembly
GRCh37: RefAssembly
GRCh38: RefAssembly
CHROMOSOME_UNSPECIFIED: Chromosome
CHR_1: Chromosome
CHR_2: Chromosome
CHR_3: Chromosome
CHR_4: Chromosome
CHR_5: Chromosome
CHR_6: Chromosome
CHR_7: Chromosome
CHR_8: Chromosome
CHR_9: Chromosome
CHR_10: Chromosome
CHR_11: Chromosome
CHR_12: Chromosome
CHR_13: Chromosome
CHR_14: Chromosome
CHR_15: Chromosome
CHR_16: Chromosome
CHR_17: Chromosome
CHR_18: Chromosome
CHR_19: Chromosome
CHR_20: Chromosome
CHR_21: Chromosome
CHR_22: Chromosome
CHR_X: Chromosome
CHR_Y: Chromosome
CHR_MT: Chromosome
VARIANTTYPE_UNSPECIFIED: VariantType
SNV: VariantType
INSERTION: VariantType
DELETION: VariantType
INDEL: VariantType
SUBSTITUTION: VariantType
INVERSION: VariantType
TRANSLOCATION: VariantType
DUPLICATION: VariantType
ALU_INSERTION: VariantType
COMPLEX_STRUCTURAL_ALTERATION: VariantType
COMPLEX_SUBSTITUTION: VariantType
COPY_NUMBER_GAIN: VariantType
COPY_NUMBER_LOSS: VariantType
COPY_NUMBER_VARIATION: VariantType
INTERCHROMOSOMAL_BREAKPOINT: VariantType
INTERCHROMOSOMAL_TRANSLOCATION: VariantType
INTRACHROMOSOMAL_BREAKPOINT: VariantType
INTRACHROMOSOMAL_TRANSLOCATION: VariantType
LOSS_OF_HETEROZYGOSITY: VariantType
MOBILE_ELEMENT_DELETION: VariantType
MOBILE_ELEMENT_INSERTION: VariantType
NOVEL_SEQUENCE_INSERTION: VariantType
SHORT_TANDEM_REPEAT_VARIATION: VariantType
TANDEM_DUPLICATION: VariantType
PROBE: VariantType
ALU_DELETION: VariantType
HERV_DELETION: VariantType
HERV_INSERTION: VariantType
LINE1_DELETION: VariantType
LINE1_INSERTION: VariantType
SVA_DELETION: VariantType
SVA_INSERTION: VariantType
COMPLEX_CHROMOSOMAL_REARRANGEMENT: VariantType
SEQUENCE_ALTERATION: VariantType
FEATURETYPE_UNSPECIFIED: FeatureType
TRANSCRIPT: FeatureType
REGULATORYFEATURE: FeatureType
MOTIFFEATURE: FeatureType
BIOTYPE_UNSPECIFIED: BioType
PROCESSED_TRANSCRIPT: BioType
LNCRNA: BioType
ANTISENSE: BioType
MACRO_LNCRNA: BioType
NON_CODING: BioType
RETAINED_INTRON: BioType
SENSE_INTRONIC: BioType
SENSE_OVERLAPPING: BioType
LINCRNA: BioType
NCRNA: BioType
MIRNA: BioType
MISCRNA: BioType
PIRNA: BioType
RRNA: BioType
SIRNA: BioType
SNRNA: BioType
SNORNA: BioType
TRNA: BioType
VAULTRNA: BioType
PROTEIN_CODING: BioType
PSEUDOGENE: BioType
IG_PSEUDOGENE: BioType
POLYMORPHIC_PSEUDOGENE: BioType
PROCESSED_PSEUDOGENE: BioType
TRANSCRIBED_PSEUDOGENE: BioType
TRANSLATED_PSEUDOGENE: BioType
UNITARY_PSEUDOGENE: BioType
UNPROCESSED_PSEUDOGENE: BioType
READTHROUGH: BioType
STOP_CODON_READTHROUGH: BioType
TEC: BioType
TR_GENE: BioType
TR_C_GENE: BioType
TR_D_GENE: BioType
TR_J_GENE: BioType
TR_V_GENE: BioType
IG_GENE: BioType
IG_C_GENE: BioType
IG_D_GENE: BioType
IG_J_GENE: BioType
IG_V_GENE: BioType
NONSENSE_MEDIATED_DECAY: BioType
PROMOTER: BioType
PROMOTER_FLANKING_REGION: BioType
ENHANCER: BioType
CTCF_BINDING_SITE: BioType
OPEN_CHROMATIN_REGION: BioType
CONSEQUENCE_UNSPECIFIED: Consequence
TRANSCRIPT_ABLATION: Consequence
SPLICE_ACCEPTOR_VARIANT: Consequence
SPLICE_DONOR_VARIANT: Consequence
STOP_GAINED: Consequence
FRAMESHIFT_VARIANT: Consequence
STOP_LOST: Consequence
START_LOST: Consequence
TRANSCRIPT_AMPLIFICATION: Consequence
INFRAME_INSERTION: Consequence
INFRAME_DELETION: Consequence
MISSENSE_VARIANT: Consequence
PROTEIN_ALTERING_VARIANT: Consequence
SPLICE_REGION_VARIANT: Consequence
INCOMPLETE_TERMINAL_CODON_VARIANT: Consequence
START_RETAINED_VARIANT: Consequence
STOP_RETAINED_VARIANT: Consequence
SYNONYMOUS_VARIANT: Consequence
CODING_SEQUENCE_VARIANT: Consequence
MATURE_MIRNA_VARIANT: Consequence
FIVE_PRIME_UTR_VARIANT: Consequence
THREE_PRIME_UTR_VARIANT: Consequence
NON_CODING_TRANSCRIPT_EXON_VARIANT: Consequence
INTRON_VARIANT: Consequence
NMD_TRANSCRIPT_VARIANT: Consequence
NON_CODING_TRANSCRIPT_VARIANT: Consequence
UPSTREAM_GENE_VARIANT: Consequence
DOWNSTREAM_GENE_VARIANT: Consequence
TFBS_ABLATION: Consequence
TFBS_AMPLIFICATION: Consequence
TF_BINDING_SITE_VARIANT: Consequence
REGULATORY_REGION_ABLATION: Consequence
REGULATORY_REGION_AMPLIFICATION: Consequence
FEATURE_ELONGATION: Consequence
REGULATORY_REGION_VARIANT: Consequence
FEATURE_TRUNCATION: Consequence
INTERGENIC_VARIANT: Consequence
SPLICE_POLYPYRIMIDINE_TRACT_VARIANT: Consequence
SPLICE_DONOR_5TH_BASE_VARIANT: Consequence
SPLICE_DONOR_REGION_VARIANT: Consequence
CODING_TRANSCRIPT_VARIANT: Consequence
SEQUENCE_VARIANT: Consequence
IMPACT_UNSPECIFIED: Impact
HIGH: Impact
MODERATE: Impact
LOW: Impact
MODIFIER: Impact
SIFT_UNSPECIFIED: SIFT
TOLERATED: SIFT
DELETERIOUS: SIFT
POLYPHEN_UNSPECIFIED: PolyPhen
BENIGN: PolyPhen
POSSIBLY_DAMAGING: PolyPhen
PROBABLY_DAMAGING: PolyPhen
UNKNOWN: PolyPhen
CLNSIG_UNSPECIFIED: ClinSignificance
CLNSIG_BENIGN: ClinSignificance
LIKELY_BENIGN: ClinSignificance
UNCERTAIN_SIGNIFICANCE: ClinSignificance
LIKELY_PATHOGENIC: ClinSignificance
PATHOGENIC: ClinSignificance
DRUG_RESPONSE: ClinSignificance
ASSOCIATION: ClinSignificance
RISK_FACTOR: ClinSignificance
PROTECTIVE: ClinSignificance
AFFECTS: ClinSignificance
CONFERS_SENSITIVITY: ClinSignificance
CONFLICTING_INTERPRETATIONS: ClinSignificance
NOT_PROVIDED: ClinSignificance
OTHER: ClinSignificance
LIKELY_PATHOGENIC_LOW_PENETRANCE: ClinSignificance
PATHOGENIC_LOW_PENETRANCE: ClinSignificance
UNCERTAIN_RISK_ALLELE: ClinSignificance
LIKELY_RISK_ALLELE: ClinSignificance
ESTABLISHED_RISK_ALLELE: ClinSignificance
AM_UNSPECIFIED: AlphaMissense
AM_LIKELY_BENIGN: AlphaMissense
AM_LIKELY_PATHOGENIC: AlphaMissense
AM_AMBIGUOUS: AlphaMissense
KINSHIP_UNSPECIFIED: KinshipDegree
TWINS_MONOZYGOTIC: KinshipDegree
FIRST_DEGREE: KinshipDegree
SECOND_DEGREE: KinshipDegree
THIRD_DEGREE: KinshipDegree
UNRELATED: KinshipDegree

class HealthRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class HealthResponse(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: str
    def __init__(self, status: _Optional[str] = ...) -> None: ...

class ClusterNodesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ClusterNodesResponse(_message.Message):
    __slots__ = ("active_nodes", "inactive_nodes", "total_nodes", "elapsed_ms")
    ACTIVE_NODES_FIELD_NUMBER: _ClassVar[int]
    INACTIVE_NODES_FIELD_NUMBER: _ClassVar[int]
    TOTAL_NODES_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    active_nodes: _containers.RepeatedScalarFieldContainer[str]
    inactive_nodes: _containers.RepeatedScalarFieldContainer[str]
    total_nodes: int
    elapsed_ms: int
    def __init__(self, active_nodes: _Optional[_Iterable[str]] = ..., inactive_nodes: _Optional[_Iterable[str]] = ..., total_nodes: _Optional[int] = ..., elapsed_ms: _Optional[int] = ...) -> None: ...

class DatasetInfoRequest(_message.Message):
    __slots__ = ("return_samples_names",)
    RETURN_SAMPLES_NAMES_FIELD_NUMBER: _ClassVar[int]
    return_samples_names: bool
    def __init__(self, return_samples_names: bool = ...) -> None: ...

class DatasetInfoResponse(_message.Message):
    __slots__ = ("cohorts", "samples_total", "females_total", "males_total", "variants_total", "assembly", "rto", "prs", "timestamp", "data_format", "notes", "rings_total", "elapsed_ms", "node_id")
    COHORTS_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_TOTAL_FIELD_NUMBER: _ClassVar[int]
    FEMALES_TOTAL_FIELD_NUMBER: _ClassVar[int]
    MALES_TOTAL_FIELD_NUMBER: _ClassVar[int]
    VARIANTS_TOTAL_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    RTO_FIELD_NUMBER: _ClassVar[int]
    PRS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DATA_FORMAT_FIELD_NUMBER: _ClassVar[int]
    NOTES_FIELD_NUMBER: _ClassVar[int]
    RINGS_TOTAL_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    cohorts: _containers.RepeatedCompositeFieldContainer[Cohort]
    samples_total: int
    females_total: int
    males_total: int
    variants_total: int
    assembly: RefAssembly
    rto: bool
    prs: _containers.RepeatedCompositeFieldContainer[PRS]
    timestamp: str
    data_format: int
    notes: str
    rings_total: int
    elapsed_ms: int
    node_id: str
    def __init__(self, cohorts: _Optional[_Iterable[_Union[Cohort, _Mapping]]] = ..., samples_total: _Optional[int] = ..., females_total: _Optional[int] = ..., males_total: _Optional[int] = ..., variants_total: _Optional[int] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., rto: bool = ..., prs: _Optional[_Iterable[_Union[PRS, _Mapping]]] = ..., timestamp: _Optional[str] = ..., data_format: _Optional[int] = ..., notes: _Optional[str] = ..., rings_total: _Optional[int] = ..., elapsed_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class Cohort(_message.Message):
    __slots__ = ("cohort_name", "samples_count", "female_count", "male_count", "female_samples_names", "male_samples_names", "synthetic")
    COHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_COUNT_FIELD_NUMBER: _ClassVar[int]
    FEMALE_COUNT_FIELD_NUMBER: _ClassVar[int]
    MALE_COUNT_FIELD_NUMBER: _ClassVar[int]
    FEMALE_SAMPLES_NAMES_FIELD_NUMBER: _ClassVar[int]
    MALE_SAMPLES_NAMES_FIELD_NUMBER: _ClassVar[int]
    SYNTHETIC_FIELD_NUMBER: _ClassVar[int]
    cohort_name: str
    samples_count: int
    female_count: int
    male_count: int
    female_samples_names: _containers.RepeatedScalarFieldContainer[str]
    male_samples_names: _containers.RepeatedScalarFieldContainer[str]
    synthetic: bool
    def __init__(self, cohort_name: _Optional[str] = ..., samples_count: _Optional[int] = ..., female_count: _Optional[int] = ..., male_count: _Optional[int] = ..., female_samples_names: _Optional[_Iterable[str]] = ..., male_samples_names: _Optional[_Iterable[str]] = ..., synthetic: bool = ...) -> None: ...

class PRS(_message.Message):
    __slots__ = ("name", "desc", "cardinality")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    name: str
    desc: str
    cardinality: int
    def __init__(self, name: _Optional[str] = ..., desc: _Optional[str] = ..., cardinality: _Optional[int] = ...) -> None: ...

class Annotations(_message.Message):
    __slots__ = ("variant_type", "feature_type", "bio_type", "consequence", "impact", "clinsgn", "af_lt", "af_gt", "gnomad_exomes_af_lt", "gnomad_exomes_af_gt", "gnomad_genomes_af_lt", "gnomad_genomes_af_gt", "sift", "polyphen", "cadd_raw_lt", "cadd_raw_gt", "cadd_phred_lt", "cadd_phred_gt", "am_score_lt", "am_score_gt", "am_class", "biallelicOnly", "multiallelicOnly", "excludeMales", "excludeFemales")
    VARIANT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TYPE_FIELD_NUMBER: _ClassVar[int]
    BIO_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONSEQUENCE_FIELD_NUMBER: _ClassVar[int]
    IMPACT_FIELD_NUMBER: _ClassVar[int]
    CLINSGN_FIELD_NUMBER: _ClassVar[int]
    AF_LT_FIELD_NUMBER: _ClassVar[int]
    AF_GT_FIELD_NUMBER: _ClassVar[int]
    GNOMAD_EXOMES_AF_LT_FIELD_NUMBER: _ClassVar[int]
    GNOMAD_EXOMES_AF_GT_FIELD_NUMBER: _ClassVar[int]
    GNOMAD_GENOMES_AF_LT_FIELD_NUMBER: _ClassVar[int]
    GNOMAD_GENOMES_AF_GT_FIELD_NUMBER: _ClassVar[int]
    SIFT_FIELD_NUMBER: _ClassVar[int]
    POLYPHEN_FIELD_NUMBER: _ClassVar[int]
    CADD_RAW_LT_FIELD_NUMBER: _ClassVar[int]
    CADD_RAW_GT_FIELD_NUMBER: _ClassVar[int]
    CADD_PHRED_LT_FIELD_NUMBER: _ClassVar[int]
    CADD_PHRED_GT_FIELD_NUMBER: _ClassVar[int]
    AM_SCORE_LT_FIELD_NUMBER: _ClassVar[int]
    AM_SCORE_GT_FIELD_NUMBER: _ClassVar[int]
    AM_CLASS_FIELD_NUMBER: _ClassVar[int]
    BIALLELICONLY_FIELD_NUMBER: _ClassVar[int]
    MULTIALLELICONLY_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEMALES_FIELD_NUMBER: _ClassVar[int]
    EXCLUDEFEMALES_FIELD_NUMBER: _ClassVar[int]
    variant_type: _containers.RepeatedScalarFieldContainer[VariantType]
    feature_type: _containers.RepeatedScalarFieldContainer[FeatureType]
    bio_type: _containers.RepeatedScalarFieldContainer[BioType]
    consequence: _containers.RepeatedScalarFieldContainer[Consequence]
    impact: _containers.RepeatedScalarFieldContainer[Impact]
    clinsgn: _containers.RepeatedScalarFieldContainer[ClinSignificance]
    af_lt: float
    af_gt: float
    gnomad_exomes_af_lt: float
    gnomad_exomes_af_gt: float
    gnomad_genomes_af_lt: float
    gnomad_genomes_af_gt: float
    sift: _containers.RepeatedScalarFieldContainer[SIFT]
    polyphen: _containers.RepeatedScalarFieldContainer[PolyPhen]
    cadd_raw_lt: float
    cadd_raw_gt: float
    cadd_phred_lt: float
    cadd_phred_gt: float
    am_score_lt: float
    am_score_gt: float
    am_class: _containers.RepeatedScalarFieldContainer[AlphaMissense]
    biallelicOnly: bool
    multiallelicOnly: bool
    excludeMales: bool
    excludeFemales: bool
    def __init__(self, variant_type: _Optional[_Iterable[_Union[VariantType, str]]] = ..., feature_type: _Optional[_Iterable[_Union[FeatureType, str]]] = ..., bio_type: _Optional[_Iterable[_Union[BioType, str]]] = ..., consequence: _Optional[_Iterable[_Union[Consequence, str]]] = ..., impact: _Optional[_Iterable[_Union[Impact, str]]] = ..., clinsgn: _Optional[_Iterable[_Union[ClinSignificance, str]]] = ..., af_lt: _Optional[float] = ..., af_gt: _Optional[float] = ..., gnomad_exomes_af_lt: _Optional[float] = ..., gnomad_exomes_af_gt: _Optional[float] = ..., gnomad_genomes_af_lt: _Optional[float] = ..., gnomad_genomes_af_gt: _Optional[float] = ..., sift: _Optional[_Iterable[_Union[SIFT, str]]] = ..., polyphen: _Optional[_Iterable[_Union[PolyPhen, str]]] = ..., cadd_raw_lt: _Optional[float] = ..., cadd_raw_gt: _Optional[float] = ..., cadd_phred_lt: _Optional[float] = ..., cadd_phred_gt: _Optional[float] = ..., am_score_lt: _Optional[float] = ..., am_score_gt: _Optional[float] = ..., am_class: _Optional[_Iterable[_Union[AlphaMissense, str]]] = ..., biallelicOnly: bool = ..., multiallelicOnly: bool = ..., excludeMales: bool = ..., excludeFemales: bool = ...) -> None: ...

class AllelesInRegionRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesInBracketRequest(_message.Message):
    __slots__ = ("chr", "start_min", "start_max", "end_min", "end_max", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_MIN_FIELD_NUMBER: _ClassVar[int]
    START_MAX_FIELD_NUMBER: _ClassVar[int]
    END_MIN_FIELD_NUMBER: _ClassVar[int]
    END_MAX_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start_min: int
    start_max: int
    end_min: int
    end_max: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start_min: _Optional[int] = ..., start_max: _Optional[int] = ..., end_min: _Optional[int] = ..., end_max: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesInBracketInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start_min", "start_max", "end_min", "end_max", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "samples", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_MIN_FIELD_NUMBER: _ClassVar[int]
    START_MAX_FIELD_NUMBER: _ClassVar[int]
    END_MIN_FIELD_NUMBER: _ClassVar[int]
    END_MAX_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start_min: int
    start_max: int
    end_min: int
    end_max: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    samples: _containers.RepeatedScalarFieldContainer[str]
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start_min: _Optional[int] = ..., start_max: _Optional[int] = ..., end_min: _Optional[int] = ..., end_max: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., samples: _Optional[_Iterable[str]] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesInRegionInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "samples", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    samples: _containers.RepeatedScalarFieldContainer[str]
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., samples: _Optional[_Iterable[str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesInMultiRegionsRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: _containers.RepeatedScalarFieldContainer[Chromosome]
    start: _containers.RepeatedScalarFieldContainer[int]
    end: _containers.RepeatedScalarFieldContainer[int]
    ref: _containers.RepeatedScalarFieldContainer[str]
    alt: _containers.RepeatedScalarFieldContainer[str]
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Iterable[_Union[Chromosome, str]]] = ..., start: _Optional[_Iterable[int]] = ..., end: _Optional[_Iterable[int]] = ..., ref: _Optional[_Iterable[str]] = ..., alt: _Optional[_Iterable[str]] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesInMultiRegionsInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "samples", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: _containers.RepeatedScalarFieldContainer[Chromosome]
    start: _containers.RepeatedScalarFieldContainer[int]
    end: _containers.RepeatedScalarFieldContainer[int]
    ref: _containers.RepeatedScalarFieldContainer[str]
    alt: _containers.RepeatedScalarFieldContainer[str]
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    samples: _containers.RepeatedScalarFieldContainer[str]
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Iterable[_Union[Chromosome, str]]] = ..., start: _Optional[_Iterable[int]] = ..., end: _Optional[_Iterable[int]] = ..., ref: _Optional[_Iterable[str]] = ..., alt: _Optional[_Iterable[str]] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., samples: _Optional[_Iterable[str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class AllelesResponse(_message.Message):
    __slots__ = ("variants", "incomplete_cluster", "affected", "elapsed_ms", "elapsed_db_ms", "node_id")
    VARIANTS_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    variants: _containers.RepeatedCompositeFieldContainer[Variant]
    incomplete_cluster: bool
    affected: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, variants: _Optional[_Iterable[_Union[Variant, _Mapping]]] = ..., incomplete_cluster: bool = ..., affected: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class Variant(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "af", "ac", "an", "homc", "hetc", "misc", "homfc", "hetfc", "misfc", "gnomADe", "gnomADg", "cadd_raw", "cadd_phred", "am_score", "amino_acids", "biallelic")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    AF_FIELD_NUMBER: _ClassVar[int]
    AC_FIELD_NUMBER: _ClassVar[int]
    AN_FIELD_NUMBER: _ClassVar[int]
    HOMC_FIELD_NUMBER: _ClassVar[int]
    HETC_FIELD_NUMBER: _ClassVar[int]
    MISC_FIELD_NUMBER: _ClassVar[int]
    HOMFC_FIELD_NUMBER: _ClassVar[int]
    HETFC_FIELD_NUMBER: _ClassVar[int]
    MISFC_FIELD_NUMBER: _ClassVar[int]
    GNOMADE_FIELD_NUMBER: _ClassVar[int]
    GNOMADG_FIELD_NUMBER: _ClassVar[int]
    CADD_RAW_FIELD_NUMBER: _ClassVar[int]
    CADD_PHRED_FIELD_NUMBER: _ClassVar[int]
    AM_SCORE_FIELD_NUMBER: _ClassVar[int]
    AMINO_ACIDS_FIELD_NUMBER: _ClassVar[int]
    BIALLELIC_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    af: float
    ac: float
    an: int
    homc: int
    hetc: int
    misc: int
    homfc: int
    hetfc: int
    misfc: int
    gnomADe: float
    gnomADg: float
    cadd_raw: float
    cadd_phred: float
    am_score: float
    amino_acids: str
    biallelic: bool
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., af: _Optional[float] = ..., ac: _Optional[float] = ..., an: _Optional[int] = ..., homc: _Optional[int] = ..., hetc: _Optional[int] = ..., misc: _Optional[int] = ..., homfc: _Optional[int] = ..., hetfc: _Optional[int] = ..., misfc: _Optional[int] = ..., gnomADe: _Optional[float] = ..., gnomADg: _Optional[float] = ..., cadd_raw: _Optional[float] = ..., cadd_phred: _Optional[float] = ..., am_score: _Optional[float] = ..., amino_acids: _Optional[str] = ..., biallelic: bool = ...) -> None: ...

class AllelesWithStatsResponse(_message.Message):
    __slots__ = ("variants", "incomplete_cluster", "affected", "elapsed_ms", "elapsed_db_ms", "node_id")
    VARIANTS_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    variants: _containers.RepeatedCompositeFieldContainer[VariantWithStats]
    incomplete_cluster: bool
    affected: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, variants: _Optional[_Iterable[_Union[VariantWithStats, _Mapping]]] = ..., incomplete_cluster: bool = ..., affected: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class VariantWithStats(_message.Message):
    __slots__ = ("variant", "vaf", "vac", "van", "vhomc", "vhetc", "vhomfc", "vhetfc", "phwe", "pchi2", "ibc")
    VARIANT_FIELD_NUMBER: _ClassVar[int]
    VAF_FIELD_NUMBER: _ClassVar[int]
    VAC_FIELD_NUMBER: _ClassVar[int]
    VAN_FIELD_NUMBER: _ClassVar[int]
    VHOMC_FIELD_NUMBER: _ClassVar[int]
    VHETC_FIELD_NUMBER: _ClassVar[int]
    VHOMFC_FIELD_NUMBER: _ClassVar[int]
    VHETFC_FIELD_NUMBER: _ClassVar[int]
    PHWE_FIELD_NUMBER: _ClassVar[int]
    PCHI2_FIELD_NUMBER: _ClassVar[int]
    OR_FIELD_NUMBER: _ClassVar[int]
    IBC_FIELD_NUMBER: _ClassVar[int]
    variant: Variant
    vaf: float
    vac: float
    van: int
    vhomc: int
    vhetc: int
    vhomfc: int
    vhetfc: int
    phwe: float
    pchi2: float
    ibc: float
    def __init__(self, variant: _Optional[_Union[Variant, _Mapping]] = ..., vaf: _Optional[float] = ..., vac: _Optional[float] = ..., van: _Optional[int] = ..., vhomc: _Optional[int] = ..., vhetc: _Optional[int] = ..., vhomfc: _Optional[int] = ..., vhetfc: _Optional[int] = ..., phwe: _Optional[float] = ..., pchi2: _Optional[float] = ..., ibc: _Optional[float] = ..., **kwargs) -> None: ...

class TopNchi2Request(_message.Message):
    __slots__ = ("n", "samples", "seq")
    N_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    n: int
    samples: _containers.RepeatedScalarFieldContainer[str]
    seq: bool
    def __init__(self, n: _Optional[int] = ..., samples: _Optional[_Iterable[str]] = ..., seq: bool = ...) -> None: ...

class TopNHWERequest(_message.Message):
    __slots__ = ("n", "seq")
    N_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    n: int
    seq: bool
    def __init__(self, n: _Optional[int] = ..., seq: bool = ...) -> None: ...

class SamplesInRegionRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class SamplesInMultiRegionsRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: _containers.RepeatedScalarFieldContainer[Chromosome]
    start: _containers.RepeatedScalarFieldContainer[int]
    end: _containers.RepeatedScalarFieldContainer[int]
    ref: _containers.RepeatedScalarFieldContainer[str]
    alt: _containers.RepeatedScalarFieldContainer[str]
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Iterable[_Union[Chromosome, str]]] = ..., start: _Optional[_Iterable[int]] = ..., end: _Optional[_Iterable[int]] = ..., ref: _Optional[_Iterable[str]] = ..., alt: _Optional[_Iterable[str]] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class SamplesHomRefRequest(_message.Message):
    __slots__ = ("chr", "position", "assembly", "skip", "limit")
    CHR_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    position: int
    assembly: RefAssembly
    skip: int
    limit: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., position: _Optional[int] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class SamplesResponse(_message.Message):
    __slots__ = ("samples", "incomplete_cluster", "affected", "elapsed_ms", "elapsed_db_ms", "node_id")
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    samples: _containers.RepeatedScalarFieldContainer[str]
    incomplete_cluster: bool
    affected: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, samples: _Optional[_Iterable[str]] = ..., incomplete_cluster: bool = ..., affected: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class DeNovoRequest(_message.Message):
    __slots__ = ("parent1", "parent2", "proband", "chr", "start", "end", "ref", "alt", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    PARENT1_FIELD_NUMBER: _ClassVar[int]
    PARENT2_FIELD_NUMBER: _ClassVar[int]
    PROBAND_FIELD_NUMBER: _ClassVar[int]
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    parent1: str
    parent2: str
    proband: str
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, parent1: _Optional[str] = ..., parent2: _Optional[str] = ..., proband: _Optional[str] = ..., chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class HetDominantRequest(_message.Message):
    __slots__ = ("affected_parent", "unaffected_parent", "affected_child", "chr", "start", "end", "ref", "alt", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    AFFECTED_PARENT_FIELD_NUMBER: _ClassVar[int]
    UNAFFECTED_PARENT_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_CHILD_FIELD_NUMBER: _ClassVar[int]
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    affected_parent: str
    unaffected_parent: str
    affected_child: str
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, affected_parent: _Optional[str] = ..., unaffected_parent: _Optional[str] = ..., affected_child: _Optional[str] = ..., chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class HomRecessiveRequest(_message.Message):
    __slots__ = ("unaffected_parent1", "unaffected_parent2", "affected_child", "chr", "start", "end", "ref", "alt", "ann", "assembly", "variantMinLength", "variantMaxLength", "skip", "limit")
    UNAFFECTED_PARENT1_FIELD_NUMBER: _ClassVar[int]
    UNAFFECTED_PARENT2_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_CHILD_FIELD_NUMBER: _ClassVar[int]
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    unaffected_parent1: str
    unaffected_parent2: str
    affected_child: str
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    skip: int
    limit: int
    def __init__(self, unaffected_parent1: _Optional[str] = ..., unaffected_parent2: _Optional[str] = ..., affected_child: _Optional[str] = ..., chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class PRSRequest(_message.Message):
    __slots__ = ("prs_name", "cohort_name", "samples", "dominant", "recessive")
    PRS_NAME_FIELD_NUMBER: _ClassVar[int]
    COHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    DOMINANT_FIELD_NUMBER: _ClassVar[int]
    RECESSIVE_FIELD_NUMBER: _ClassVar[int]
    prs_name: str
    cohort_name: str
    samples: _containers.RepeatedScalarFieldContainer[str]
    dominant: bool
    recessive: bool
    def __init__(self, prs_name: _Optional[str] = ..., cohort_name: _Optional[str] = ..., samples: _Optional[_Iterable[str]] = ..., dominant: bool = ..., recessive: bool = ...) -> None: ...

class PRSResponse(_message.Message):
    __slots__ = ("prs_name", "sample_scores", "dominant", "recessive", "prs_cardinality", "incomplete_cluster", "elapsed_ms", "elapsed_db_ms", "node_id")
    PRS_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLE_SCORES_FIELD_NUMBER: _ClassVar[int]
    DOMINANT_FIELD_NUMBER: _ClassVar[int]
    RECESSIVE_FIELD_NUMBER: _ClassVar[int]
    PRS_CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    prs_name: str
    sample_scores: _containers.RepeatedCompositeFieldContainer[SampleScore]
    dominant: bool
    recessive: bool
    prs_cardinality: int
    incomplete_cluster: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, prs_name: _Optional[str] = ..., sample_scores: _Optional[_Iterable[_Union[SampleScore, _Mapping]]] = ..., dominant: bool = ..., recessive: bool = ..., prs_cardinality: _Optional[int] = ..., incomplete_cluster: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class SampleScore(_message.Message):
    __slots__ = ("sample", "scores_sum", "hethom_cardinality", "ref_cardinality", "mis_cardinality", "imputed_sum")
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    SCORES_SUM_FIELD_NUMBER: _ClassVar[int]
    HETHOM_CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    REF_CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    MIS_CARDINALITY_FIELD_NUMBER: _ClassVar[int]
    IMPUTED_SUM_FIELD_NUMBER: _ClassVar[int]
    sample: str
    scores_sum: float
    hethom_cardinality: int
    ref_cardinality: int
    mis_cardinality: int
    imputed_sum: float
    def __init__(self, sample: _Optional[str] = ..., scores_sum: _Optional[float] = ..., hethom_cardinality: _Optional[int] = ..., ref_cardinality: _Optional[int] = ..., mis_cardinality: _Optional[int] = ..., imputed_sum: _Optional[float] = ...) -> None: ...

class FstatXRequest(_message.Message):
    __slots__ = ("cohort_name", "samples", "aaf_threshold", "female_threshold", "male_threshold", "include_par", "seq")
    COHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    AAF_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    FEMALE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    MALE_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    INCLUDE_PAR_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    cohort_name: str
    samples: _containers.RepeatedScalarFieldContainer[str]
    aaf_threshold: float
    female_threshold: float
    male_threshold: float
    include_par: bool
    seq: bool
    def __init__(self, cohort_name: _Optional[str] = ..., samples: _Optional[_Iterable[str]] = ..., aaf_threshold: _Optional[float] = ..., female_threshold: _Optional[float] = ..., male_threshold: _Optional[float] = ..., include_par: bool = ..., seq: bool = ...) -> None: ...

class SexMismatchResponse(_message.Message):
    __slots__ = ("mismatch_males", "mismatch_females", "incomplete_cluster", "elapsed_ms", "elapsed_db_ms", "node_id")
    MISMATCH_MALES_FIELD_NUMBER: _ClassVar[int]
    MISMATCH_FEMALES_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    mismatch_males: _containers.RepeatedCompositeFieldContainer[SampleStat]
    mismatch_females: _containers.RepeatedCompositeFieldContainer[SampleStat]
    incomplete_cluster: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, mismatch_males: _Optional[_Iterable[_Union[SampleStat, _Mapping]]] = ..., mismatch_females: _Optional[_Iterable[_Union[SampleStat, _Mapping]]] = ..., incomplete_cluster: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class SampleStat(_message.Message):
    __slots__ = ("sample", "reported_sex", "observed_sex", "f_stat")
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    REPORTED_SEX_FIELD_NUMBER: _ClassVar[int]
    OBSERVED_SEX_FIELD_NUMBER: _ClassVar[int]
    F_STAT_FIELD_NUMBER: _ClassVar[int]
    sample: str
    reported_sex: str
    observed_sex: str
    f_stat: float
    def __init__(self, sample: _Optional[str] = ..., reported_sex: _Optional[str] = ..., observed_sex: _Optional[str] = ..., f_stat: _Optional[float] = ...) -> None: ...

class FstatXResponse(_message.Message):
    __slots__ = ("males", "females", "incomplete_cluster", "elapsed_ms", "elapsed_db_ms", "node_id")
    MALES_FIELD_NUMBER: _ClassVar[int]
    FEMALES_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    males: _containers.RepeatedCompositeFieldContainer[SampleStat]
    females: _containers.RepeatedCompositeFieldContainer[SampleStat]
    incomplete_cluster: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, males: _Optional[_Iterable[_Union[SampleStat, _Mapping]]] = ..., females: _Optional[_Iterable[_Union[SampleStat, _Mapping]]] = ..., incomplete_cluster: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class KinshipRequest(_message.Message):
    __slots__ = ("cohort_name", "samples", "degree", "threshold", "seq")
    COHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    cohort_name: str
    samples: _containers.RepeatedScalarFieldContainer[str]
    degree: KinshipDegree
    threshold: float
    seq: bool
    def __init__(self, cohort_name: _Optional[str] = ..., samples: _Optional[_Iterable[str]] = ..., degree: _Optional[_Union[KinshipDegree, str]] = ..., threshold: _Optional[float] = ..., seq: bool = ...) -> None: ...

class KinshipDuoRequest(_message.Message):
    __slots__ = ("sample1", "sample2", "seq")
    SAMPLE1_FIELD_NUMBER: _ClassVar[int]
    SAMPLE2_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    sample1: str
    sample2: str
    seq: bool
    def __init__(self, sample1: _Optional[str] = ..., sample2: _Optional[str] = ..., seq: bool = ...) -> None: ...

class KinshipTrioRequest(_message.Message):
    __slots__ = ("sample1", "sample2", "sample3", "degree", "threshold", "seq")
    SAMPLE1_FIELD_NUMBER: _ClassVar[int]
    SAMPLE2_FIELD_NUMBER: _ClassVar[int]
    SAMPLE3_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    sample1: str
    sample2: str
    sample3: str
    degree: KinshipDegree
    threshold: float
    seq: bool
    def __init__(self, sample1: _Optional[str] = ..., sample2: _Optional[str] = ..., sample3: _Optional[str] = ..., degree: _Optional[_Union[KinshipDegree, str]] = ..., threshold: _Optional[float] = ..., seq: bool = ...) -> None: ...

class KinshipResponse(_message.Message):
    __slots__ = ("rel", "incomplete_cluster", "elapsed_ms", "elapsed_db_ms", "node_id")
    REL_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    rel: _containers.RepeatedCompositeFieldContainer[Relatedness]
    incomplete_cluster: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, rel: _Optional[_Iterable[_Union[Relatedness, _Mapping]]] = ..., incomplete_cluster: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class Relatedness(_message.Message):
    __slots__ = ("sample1", "sample2", "degree", "phi_bwf")
    SAMPLE1_FIELD_NUMBER: _ClassVar[int]
    SAMPLE2_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    PHI_BWF_FIELD_NUMBER: _ClassVar[int]
    sample1: str
    sample2: str
    degree: KinshipDegree
    phi_bwf: float
    def __init__(self, sample1: _Optional[str] = ..., sample2: _Optional[str] = ..., degree: _Optional[_Union[KinshipDegree, str]] = ..., phi_bwf: _Optional[float] = ...) -> None: ...

class SampleKinshipRequest(_message.Message):
    __slots__ = ("sample_vcf", "cohort_name", "degree", "threshold", "seq")
    SAMPLE_VCF_FIELD_NUMBER: _ClassVar[int]
    COHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    SEQ_FIELD_NUMBER: _ClassVar[int]
    sample_vcf: str
    cohort_name: str
    degree: KinshipDegree
    threshold: float
    seq: bool
    def __init__(self, sample_vcf: _Optional[str] = ..., cohort_name: _Optional[str] = ..., degree: _Optional[_Union[KinshipDegree, str]] = ..., threshold: _Optional[float] = ..., seq: bool = ...) -> None: ...

class SampleKinshipResponse(_message.Message):
    __slots__ = ("rel", "accepted_snvs", "incomplete_cluster", "elapsed_ms", "elapsed_db_ms", "node_id")
    REL_FIELD_NUMBER: _ClassVar[int]
    ACCEPTED_SNVS_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    rel: _containers.RepeatedCompositeFieldContainer[RelatednessPerSample]
    accepted_snvs: int
    incomplete_cluster: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, rel: _Optional[_Iterable[_Union[RelatednessPerSample, _Mapping]]] = ..., accepted_snvs: _Optional[int] = ..., incomplete_cluster: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class RelatednessPerSample(_message.Message):
    __slots__ = ("sample", "degree", "phi_bwf", "common_loci", "nHetS1", "nHetS2", "nHetS1S2", "nHomOp")
    SAMPLE_FIELD_NUMBER: _ClassVar[int]
    DEGREE_FIELD_NUMBER: _ClassVar[int]
    PHI_BWF_FIELD_NUMBER: _ClassVar[int]
    COMMON_LOCI_FIELD_NUMBER: _ClassVar[int]
    NHETS1_FIELD_NUMBER: _ClassVar[int]
    NHETS2_FIELD_NUMBER: _ClassVar[int]
    NHETS1S2_FIELD_NUMBER: _ClassVar[int]
    NHOMOP_FIELD_NUMBER: _ClassVar[int]
    sample: str
    degree: KinshipDegree
    phi_bwf: float
    common_loci: int
    nHetS1: int
    nHetS2: int
    nHetS1S2: int
    nHomOp: int
    def __init__(self, sample: _Optional[str] = ..., degree: _Optional[_Union[KinshipDegree, str]] = ..., phi_bwf: _Optional[float] = ..., common_loci: _Optional[int] = ..., nHetS1: _Optional[int] = ..., nHetS2: _Optional[int] = ..., nHetS1S2: _Optional[int] = ..., nHomOp: _Optional[int] = ...) -> None: ...

class CountAllelesInRegionRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ...) -> None: ...

class CountAllelesInRegionInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "samples")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start: int
    end: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    samples: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., samples: _Optional[_Iterable[str]] = ...) -> None: ...

class CountAllelesInBracketRequest(_message.Message):
    __slots__ = ("chr", "start_min", "start_max", "end_min", "end_max", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_MIN_FIELD_NUMBER: _ClassVar[int]
    START_MAX_FIELD_NUMBER: _ClassVar[int]
    END_MIN_FIELD_NUMBER: _ClassVar[int]
    END_MAX_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start_min: int
    start_max: int
    end_min: int
    end_max: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start_min: _Optional[int] = ..., start_max: _Optional[int] = ..., end_min: _Optional[int] = ..., end_max: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ...) -> None: ...

class CountAllelesInBracketInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start_min", "start_max", "end_min", "end_max", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "samples")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_MIN_FIELD_NUMBER: _ClassVar[int]
    START_MAX_FIELD_NUMBER: _ClassVar[int]
    END_MIN_FIELD_NUMBER: _ClassVar[int]
    END_MAX_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    chr: Chromosome
    start_min: int
    start_max: int
    end_min: int
    end_max: int
    ref: str
    alt: str
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    samples: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, chr: _Optional[_Union[Chromosome, str]] = ..., start_min: _Optional[int] = ..., start_max: _Optional[int] = ..., end_min: _Optional[int] = ..., end_max: _Optional[int] = ..., ref: _Optional[str] = ..., alt: _Optional[str] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., samples: _Optional[_Iterable[str]] = ...) -> None: ...

class CountAllelesInMultiRegionsRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    chr: _containers.RepeatedScalarFieldContainer[Chromosome]
    start: _containers.RepeatedScalarFieldContainer[int]
    end: _containers.RepeatedScalarFieldContainer[int]
    ref: _containers.RepeatedScalarFieldContainer[str]
    alt: _containers.RepeatedScalarFieldContainer[str]
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    def __init__(self, chr: _Optional[_Iterable[_Union[Chromosome, str]]] = ..., start: _Optional[_Iterable[int]] = ..., end: _Optional[_Iterable[int]] = ..., ref: _Optional[_Iterable[str]] = ..., alt: _Optional[_Iterable[str]] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ...) -> None: ...

class CountAllelesInMultiRegionsInSamplesRequest(_message.Message):
    __slots__ = ("chr", "start", "end", "ref", "alt", "hom", "het", "ann", "assembly", "variantMinLength", "variantMaxLength", "samples")
    CHR_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REF_FIELD_NUMBER: _ClassVar[int]
    ALT_FIELD_NUMBER: _ClassVar[int]
    HOM_FIELD_NUMBER: _ClassVar[int]
    HET_FIELD_NUMBER: _ClassVar[int]
    ANN_FIELD_NUMBER: _ClassVar[int]
    ASSEMBLY_FIELD_NUMBER: _ClassVar[int]
    VARIANTMINLENGTH_FIELD_NUMBER: _ClassVar[int]
    VARIANTMAXLENGTH_FIELD_NUMBER: _ClassVar[int]
    SAMPLES_FIELD_NUMBER: _ClassVar[int]
    chr: _containers.RepeatedScalarFieldContainer[Chromosome]
    start: _containers.RepeatedScalarFieldContainer[int]
    end: _containers.RepeatedScalarFieldContainer[int]
    ref: _containers.RepeatedScalarFieldContainer[str]
    alt: _containers.RepeatedScalarFieldContainer[str]
    hom: bool
    het: bool
    ann: Annotations
    assembly: RefAssembly
    variantMinLength: int
    variantMaxLength: int
    samples: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, chr: _Optional[_Iterable[_Union[Chromosome, str]]] = ..., start: _Optional[_Iterable[int]] = ..., end: _Optional[_Iterable[int]] = ..., ref: _Optional[_Iterable[str]] = ..., alt: _Optional[_Iterable[str]] = ..., hom: bool = ..., het: bool = ..., ann: _Optional[_Union[Annotations, _Mapping]] = ..., assembly: _Optional[_Union[RefAssembly, str]] = ..., variantMinLength: _Optional[int] = ..., variantMaxLength: _Optional[int] = ..., samples: _Optional[_Iterable[str]] = ...) -> None: ...

class CountAllelesResponse(_message.Message):
    __slots__ = ("count", "incomplete_cluster", "affected", "elapsed_ms", "elapsed_db_ms", "node_id")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    count: int
    incomplete_cluster: bool
    affected: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, count: _Optional[int] = ..., incomplete_cluster: bool = ..., affected: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...

class CountSamplesResponse(_message.Message):
    __slots__ = ("count", "incomplete_cluster", "affected", "elapsed_ms", "elapsed_db_ms", "node_id")
    COUNT_FIELD_NUMBER: _ClassVar[int]
    INCOMPLETE_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    AFFECTED_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_MS_FIELD_NUMBER: _ClassVar[int]
    ELAPSED_DB_MS_FIELD_NUMBER: _ClassVar[int]
    NODE_ID_FIELD_NUMBER: _ClassVar[int]
    count: int
    incomplete_cluster: bool
    affected: bool
    elapsed_ms: int
    elapsed_db_ms: int
    node_id: str
    def __init__(self, count: _Optional[int] = ..., incomplete_cluster: bool = ..., affected: bool = ..., elapsed_ms: _Optional[int] = ..., elapsed_db_ms: _Optional[int] = ..., node_id: _Optional[str] = ...) -> None: ...
