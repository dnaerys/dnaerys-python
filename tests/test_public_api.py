"""Public API surface tests — verify exports, docstrings, and hygiene."""

import importlib
import os
import re

import dnaerys


def test_all_public_symbols_importable():
    """Every name in dnaerys.__all__ is accessible via getattr and importable."""
    missing = []
    for name in dnaerys.__all__:
        try:
            getattr(dnaerys, name)
        except AttributeError:
            missing.append(name)

    assert not missing, f"Symbols in __all__ but not accessible: {missing}"

    # Dynamic import check for a representative subset
    subset = [
        "DnaerysClient",
        "Region",
        "Chromosome",
        "Variant",
        "VariantStream",
        "DnaerysError",
        "PROTO_VERSION",
        "AnnotationFilter",
        "CountResult",
    ]
    for name in subset:
        mod = importlib.import_module("dnaerys")
        obj = getattr(mod, name, None)
        assert obj is not None, f"from dnaerys import {name} failed"


def test_all_public_symbols_have_docstring():
    """Every class/function in dnaerys.__all__ has a non-empty __doc__."""
    missing_doc = []
    for name in dnaerys.__all__:
        obj = getattr(dnaerys, name)
        doc = getattr(obj, "__doc__", None)
        if doc is None or not doc.strip():
            missing_doc.append(name)

    assert not missing_doc, (
        f"Symbols missing docstrings: {missing_doc}"
    )


def test_no_hardcoded_paths():
    """No hardcoded absolute paths in source files (excluding _proto/ generated files).

    Checks for /scratch/, /home/, or /g/data/ patterns outside of string
    assignments to variables named *ROOT* or *PATH*.
    """
    src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src", "dnaerys")
    proto_dir = os.path.join(src_dir, "_proto")

    # Pattern for suspicious absolute paths
    path_pattern = re.compile(r'(?:/scratch/|/home/|/g/data/)')
    # Pattern for acceptable variable assignments (ROOT or PATH in the name)
    assignment_pattern = re.compile(r'^\s*\w*(ROOT|PATH)\w*\s*=')

    violations = []

    for dirpath, _dirnames, filenames in os.walk(src_dir):
        # Skip generated proto files
        if dirpath.startswith(proto_dir):
            continue
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            filepath = os.path.join(dirpath, filename)
            with open(filepath) as f:
                for lineno, line in enumerate(f, 1):
                    if path_pattern.search(line) and not assignment_pattern.match(line):
                        relpath = os.path.relpath(filepath, src_dir)
                        violations.append(f"{relpath}:{lineno}: {line.rstrip()}")

    assert not violations, (
        f"Hardcoded absolute paths found:\n" + "\n".join(violations)
    )


def test_proto_version_constant():
    """PROTO_VERSION constant matches the expected schema version."""
    assert dnaerys.PROTO_VERSION == "R1.17.8"
