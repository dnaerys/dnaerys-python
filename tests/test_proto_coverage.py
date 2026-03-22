"""Proto enum coverage tests — verify every proto enum value has a Python IntEnum member.

Each test checks that the set of non-UNSPECIFIED (non-zero) proto enum values
exactly matches the set of Python IntEnum member values.  This catches:
- Proto values added in a newer schema version without a corresponding Python member.
- Python members that don't correspond to any proto value (typos, stale values).
"""

from dnaerys._proto import dnaerys_pb2 as pb2
from dnaerys import (
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
)


def test_chromosome_proto_coverage():
    proto_values = {v.number for v in pb2.Chromosome.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in Chromosome}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_ref_assembly_proto_coverage():
    proto_values = {v.number for v in pb2.RefAssembly.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in RefAssembly}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_variant_type_proto_coverage():
    proto_values = {v.number for v in pb2.VariantType.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in VariantType}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_feature_type_proto_coverage():
    proto_values = {v.number for v in pb2.FeatureType.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in FeatureType}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_bio_type_proto_coverage():
    proto_values = {v.number for v in pb2.BioType.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in BioType}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_consequence_proto_coverage():
    proto_values = {v.number for v in pb2.Consequence.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in Consequence}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_impact_proto_coverage():
    proto_values = {v.number for v in pb2.Impact.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in Impact}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_sift_proto_coverage():
    proto_values = {v.number for v in pb2.SIFT.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in SIFT}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_polyphen_proto_coverage():
    proto_values = {v.number for v in pb2.PolyPhen.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in PolyPhen}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_clin_significance_proto_coverage():
    proto_values = {v.number for v in pb2.ClinSignificance.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in ClinSignificance}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_alpha_missense_proto_coverage():
    proto_values = {v.number for v in pb2.AlphaMissense.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in AlphaMissense}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"


def test_kinship_degree_proto_coverage():
    proto_values = {v.number for v in pb2.KinshipDegree.DESCRIPTOR.values if v.number != 0}
    python_values = {int(m) for m in KinshipDegree}
    assert proto_values == python_values, \
        f"Missing: {proto_values - python_values}, Extra: {python_values - proto_values}"
