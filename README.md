[![PyPI version](https://img.shields.io/pypi/v/dnaerys)](https://pypi.org/project/dnaerys/) [![Python versions](https://img.shields.io/pypi/pyversions/dnaerys)](https://pypi.org/project/dnaerys/) [![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE) [![Documentation](https://readthedocs.org/projects/dnaerys/badge/)](https://dnaerys-python.readthedocs.io)

# Dnaerys Python Client

Python client library for [Dnaerys](https://dnaerys.org/), a high-performance
distributed genome variant database. Dnaerys stores indexed variant and sample
data for large cohorts and serves queries with millisecond latency, including
VEP annotations, allele frequencies, and pathogenicity predictions. This library
wraps the gRPC API into Pythonic methods with streaming iteration, pagination,
and frozen dataclass results. It is designed for bioinformaticians and data
scientists working with cohort-scale genomic data.

**Full documentation:** [dnaerys-python.readthedocs.io](https://dnaerys-python.readthedocs.io)

## Requirements

Python 3.12 or later.

## Installation

```bash
pip install dnaerys
pip install dnaerys[pandas]   # for to_dataframe() support
```

## Quick Start

```python
from dnaerys import (
    DnaerysClient, Region, AnnotationFilter, Consequence, Impact,
)

tp53 = Region("chr17", 7661779, 7687546)

with DnaerysClient("db.dnaerys.org:443") as client:
    ann = AnnotationFilter(
        impact=[Impact.HIGH, Impact.MODERATE],
        consequence=[Consequence.MISSENSE_VARIANT],
        clin_significance=["PATHOGENIC", "LIKELY_PATHOGENIC"],
    )

    stream = client.select_variants(
        region=tp53,
        annotations=ann,
        limit=10,
    )

    for variant in stream:
        print(variant)

    # Check response metadata
    print(f"Elapsed: {stream.metadata.elapsed_ms}ms")
```

## Features

- **Streaming iteration** — variant results arrive as lazy iterators with constant memory usage.
- **Pagination** — `paginate_*` methods serve fixed-size pages with transparent buffer refills.
- **Annotation filtering** — filter by VEP annotations, AF, CADD, AlphaMissense, PolyPhen, SIFT, ClinVar significance, and more.
- **Inheritance queries** — detect de novo, heterozygous dominant, and homozygous recessive variants across trios.
- **Kinship analysis** — KING-based kinship estimation for cohorts, duos, trios, and external samples.
- **Frozen dataclasses** — all result types are immutable, slotted, and hashable; safe to cache, copy, and use as dict keys.
- **Clean exception hierarchy** — gRPC status codes map to specific exception classes with `is_retryable` flags.
- **pandas integration** — call `to_dataframe()` on any variant stream to get a DataFrame.

## Documentation

Full documentation including API reference, pagination guide, annotation filter
reference, and connection options is available at
[dnaerys-python.readthedocs.io](https://dnaerys-python.readthedocs.io). The API reference
covers all 27 public methods on `DnaerysClient`.

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome. Please open an issue to discuss proposed changes
before submitting a pull request. Bug reports and feature requests can be
filed at [github.com/dnaerys/dnaerys-python/issues](https://github.com/dnaerys/dnaerys-python/issues).
