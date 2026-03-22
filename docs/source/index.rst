Dnaerys Python Client Library
=============================

A Python client library for `Dnaerys <https://dnaerys.org/>`_, a high-performance
genome variant store. This library wraps ~36 gRPC RPCs into ~27 Pythonic methods,
handles enum resolution, proto-to-dataclass conversion, streaming iteration, and
translates gRPC errors into a clean exception hierarchy.

**Proto version:** R1.17.8

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           limit=10,
       ):
           print(f"chr{v.chr.value} {v.start} {v.ref}>{v.alt} AF={v.af}")

Key features:

- **Streaming iteration** — variant results arrive as lazy iterators; memory
  usage stays constant regardless of result set size.
- **Pagination** — ``paginate_*`` methods manage server-side pagination internally,
  serving clean fixed-size pages.
- **Frozen dataclasses** — all result types are immutable, slotted dataclasses.
- **Annotation filters** — filter by VEP annotations, allele frequency,
  CADD, AlphaMissense, PolyPhen, SIFT, ClinVar significance, and more.
- **Inheritance queries** — de novo, heterozygous dominant, and homozygous
  recessive variant detection.
- **Kinship analysis** — KING-based kinship estimation for cohorts, duos,
  trios, and external samples.

| `Source code on GitHub <https://github.com/dnaerys/dnaerys-python>`_

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart
   connection

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   pagination
   annotations
   caveats
   errors

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
   changelog
