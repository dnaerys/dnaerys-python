"""Tests for dnaerys._enums — enum definitions and resolution functions."""

import pytest

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


# -----------------------------------------------------------------------
# Chromosome resolution
# -----------------------------------------------------------------------


class TestResolveChromosome:
    def test_resolve_chromosome_chr_prefix(self):
        assert resolve_chromosome("chr1") == Chromosome.CHR1

    def test_resolve_chromosome_number_only(self):
        assert resolve_chromosome("1") == Chromosome.CHR1

    def test_resolve_chromosome_uppercase(self):
        assert resolve_chromosome("CHR1") == Chromosome.CHR1

    def test_resolve_chromosome_sex_x(self):
        assert resolve_chromosome("X") == Chromosome.CHRX

    def test_resolve_chromosome_sex_chrx(self):
        assert resolve_chromosome("chrX") == Chromosome.CHRX

    def test_resolve_chromosome_mt(self):
        assert resolve_chromosome("MT") == Chromosome.CHRMT

    def test_resolve_chromosome_chrmt(self):
        assert resolve_chromosome("chrMT") == Chromosome.CHRMT

    def test_resolve_chromosome_case_insensitive(self):
        assert resolve_chromosome("Chr1") == Chromosome.CHR1

    def test_resolve_chromosome_enum_passthrough(self):
        assert resolve_chromosome(Chromosome.CHR1) == Chromosome.CHR1

    def test_resolve_chromosome_int_passthrough(self):
        assert resolve_chromosome(1) == Chromosome.CHR1

    def test_resolve_chromosome_invalid_string(self):
        with pytest.raises(ValueError, match="Unknown chromosome"):
            resolve_chromosome("chr99")

    def test_resolve_chromosome_empty_string(self):
        with pytest.raises(ValueError, match="Unknown chromosome"):
            resolve_chromosome("")

    def test_resolve_chromosome_y(self):
        assert resolve_chromosome("Y") == Chromosome.CHRY

    def test_resolve_chromosome_all_numeric(self):
        for i in range(1, 23):
            assert resolve_chromosome(str(i)) == Chromosome(i)


# -----------------------------------------------------------------------
# Generic enum resolution
# -----------------------------------------------------------------------


class TestResolveEnum:
    def test_resolve_enum_consequence_exact(self):
        assert (
            resolve_enum(Consequence, "MISSENSE_VARIANT")
            == Consequence.MISSENSE_VARIANT
        )

    def test_resolve_enum_consequence_lowercase(self):
        assert (
            resolve_enum(Consequence, "missense_variant")
            == Consequence.MISSENSE_VARIANT
        )

    def test_resolve_enum_consequence_mixed_case(self):
        assert (
            resolve_enum(Consequence, "Missense_Variant")
            == Consequence.MISSENSE_VARIANT
        )

    def test_resolve_enum_impact(self):
        assert resolve_enum(Impact, "high") == Impact.HIGH

    def test_resolve_enum_passthrough(self):
        assert resolve_enum(Impact, Impact.HIGH) == Impact.HIGH

    def test_resolve_enum_invalid(self):
        with pytest.raises(ValueError, match="Unknown Impact"):
            resolve_enum(Impact, "EXTREME")

    def test_resolve_enum_error_message_lists_valid_values(self):
        with pytest.raises(ValueError) as exc_info:
            resolve_enum(Impact, "EXTREME")
        msg = str(exc_info.value)
        for member in Impact:
            assert member.name in msg


# -----------------------------------------------------------------------
# Assembly resolution
# -----------------------------------------------------------------------


class TestResolveAssembly:
    def test_resolve_assembly_grch38(self):
        assert resolve_assembly("GRCh38") == RefAssembly.GRCh38

    def test_resolve_assembly_grch37(self):
        assert resolve_assembly("GRCh37") == RefAssembly.GRCh37

    def test_resolve_assembly_case_insensitive(self):
        assert resolve_assembly("grch38") == RefAssembly.GRCh38

    def test_resolve_assembly_passthrough(self):
        assert resolve_assembly(RefAssembly.GRCh38) == RefAssembly.GRCh38

    def test_resolve_assembly_invalid(self):
        with pytest.raises(ValueError, match="Unknown assembly"):
            resolve_assembly("hg19")


# -----------------------------------------------------------------------
# Enum member counts (proto sync verification)
# -----------------------------------------------------------------------


class TestEnumMemberCounts:
    def test_chromosome_member_count(self):
        assert len(Chromosome) == 25

    def test_variant_type_member_count(self):
        assert len(VariantType) == 34

    def test_consequence_member_count(self):
        assert len(Consequence) == 41

    def test_impact_member_count(self):
        assert len(Impact) == 4

    def test_feature_type_member_count(self):
        assert len(FeatureType) == 3

    def test_bio_type_member_count(self):
        assert len(BioType) == 47

    def test_clin_significance_member_count(self):
        assert len(ClinSignificance) == 19

    def test_sift_member_count(self):
        assert len(SIFT) == 2

    def test_polyphen_member_count(self):
        assert len(PolyPhen) == 4

    def test_alpha_missense_member_count(self):
        assert len(AlphaMissense) == 3

    def test_kinship_degree_member_count(self):
        assert len(KinshipDegree) == 5

    def test_ref_assembly_member_count(self):
        assert len(RefAssembly) == 2


# -----------------------------------------------------------------------
# IntEnum interoperability
# -----------------------------------------------------------------------


class TestIntEnumInterop:
    def test_chromosome_int_value(self):
        assert int(Chromosome.CHR1) == 1

    def test_consequence_int_value(self):
        assert int(Consequence.MISSENSE_VARIANT) == 11


# -----------------------------------------------------------------------
# No UNSPECIFIED members exposed
# -----------------------------------------------------------------------


class TestNoUnspecified:
    def test_enums_exclude_unspecified(self):
        all_enums = [
            Chromosome,
            RefAssembly,
            VariantType,
            FeatureType,
            BioType,
            Consequence,
            Impact,
            SIFT,
            PolyPhen,
            ClinSignificance,
            AlphaMissense,
            KinshipDegree,
        ]
        for enum_cls in all_enums:
            for member in enum_cls:
                assert member.value != 0, (
                    f"{enum_cls.__name__}.{member.name} has value 0 "
                    f"(UNSPECIFIED should not be exposed)"
                )
