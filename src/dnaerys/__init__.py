"""Dnaerys Python client library for the Dnaerys genomic data service.

This library provides a Pythonic interface to the Dnaerys gRPC service,
which offers high-performance variant and sample queries over indexed
genomic datasets.

Proto version: R1.17.8
"""

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
    resolve_assembly,
    resolve_chromosome,
    resolve_enum,
)
from dnaerys._exceptions import (
    DnaerysAuthenticationError,
    DnaerysConnectionError,
    DnaerysError,
    DnaerysIncompleteResultWarning,
    DnaerysInvalidRequestError,
    DnaerysNotFoundError,
    DnaerysResourceExhausted,
    DnaerysServerError,
)
from dnaerys._client import DnaerysClient
from dnaerys._pagination import Page, PaginatedQuery
from dnaerys._stream import (
    VariantStream,
    VariantWithStatsStream,
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

PROTO_VERSION: str = "R1.17.8"
"""Protocol buffer schema version that this library targets."""

__all__ = [
    # Proto version
    "PROTO_VERSION",
    # Client
    "DnaerysClient",
    # Enums
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
    # Enum resolution
    "resolve_chromosome",
    "resolve_enum",
    "resolve_assembly",
    # Input types
    "Region",
    "Bracket",
    "AnnotationFilter",
    # Core result types
    "Variant",
    "VariantWithStats",
    # Stream wrappers
    "VariantStream",
    "VariantWithStatsStream",
    # Pagination
    "Page",
    "PaginatedQuery",
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
    # Exceptions
    "DnaerysError",
    "DnaerysConnectionError",
    "DnaerysAuthenticationError",
    "DnaerysNotFoundError",
    "DnaerysInvalidRequestError",
    "DnaerysServerError",
    "DnaerysResourceExhausted",
    "DnaerysIncompleteResultWarning",
]
