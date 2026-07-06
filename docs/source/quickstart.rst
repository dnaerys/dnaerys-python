Quick Start
===========

This guide shows the common usage patterns. All examples assume a
connection to ``db.dnaerys.org:443``.

Connecting
----------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   # TLS connection (default)
   with DnaerysClient("db.dnaerys.org:443") as client:
       result = client.health()
       print(result.status)

Plain HTTP (no TLS) for development:

.. code-block:: python

   client = DnaerysClient("localhost:8001", tls=False)

Selecting variants
------------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region, Bracket

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Single region
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546), limit=2,
       ):
           print(v)

       # Multiple regions
       regions = [
           Region("chr17", 7661779, 7687546),
           Region("chr2", 10000, 20000),
       ]
       for v in client.select_variants(regions=regions, limit=2):
           print(v)

       # Bracket query (structural variants)
       bracket = Bracket(
           "chr2",
           start_min=10000, start_max=11000,
           end_min=20000, end_max=21000,
       )
       for v in client.select_variants(bracket=bracket):
           print(v)

       # In specific samples
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           samples=["NA10842", "HG00418"],
           limit=2,
       ):
           print(v)

Variants with Statistics
------------------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       stream = client.select_variants_with_stats(
           regions=[Region("chr17", 7661779, 7687546)],
           samples=["NA10842", "HG00418"],
           limit=2,
       )
       for v in stream:
           print(
               f"{v.ref}>{v.alt}: phwe={v.phwe}, pchi2={v.pchi2}, "
               f"odds_ratio={v.odds_ratio}, ibc={v.ibc}"
           )

Counting variants
-----------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       result = client.count_variants(
           region=Region("chr17", 7661779, 7687546),
       )
       print(f"Count: {result.count}")
       print(f"Elapsed: {result.metadata.elapsed_ms}ms")

Sample queries
--------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region, Chromosome

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Select samples with variants in a region
       result = client.select_samples(
           region=Region("chr17", 7661779, 7687546), limit=2,
       )
       print(f"Samples: {result.samples}")

       # Count samples
       result = client.count_samples(
           region=Region("chr17", 7661779, 7687546),
       )
       print(f"Sample count: {result.count}")

       # Select homozygous reference samples
       result = client.select_samples_hom_ref(
           chr=Chromosome.CHR17, position=7661841,
       )
       print(f"Hom-ref samples: {result.samples}")

Inheritance queries
-------------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       region = Region("chr17", 7661779, 7687546)

       # De novo candidates
       for v in client.select_de_novo(
           parent1="HG00418",
           parent2="HG00419",
           proband="HG00420",
           region=region,
       ):
           print(v)

       # Heterozygous dominant
       for v in client.select_het_dominant(
           affected_parent="HG00418",
           unaffected_parent="HG00419",
           affected_child="HG00420",
           region=region,
       ):
           print(v)

       # Homozygous recessive
       for v in client.select_hom_recessive(
           unaffected_parent1="HG00418",
           unaffected_parent2="HG00419",
           affected_child="HG00420",
           region=region,
       ):
           print(v)

Paginated queries
-----------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Paginate variants
       for page in client.paginate_variants(
           region=Region("chr17", 7661779, 7687546),
           page_size=100,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

       # Paginate variants with statistics
       for page in client.paginate_variants_with_stats(
           regions=[Region("chr17", 7661779, 7687546)],
           samples=["NA10842", "HG00418"],
           page_size=50,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

       # Paginate inheritance queries
       for page in client.paginate_de_novo(
           parent1="HG00418", parent2="HG00419", proband="HG00420",
           region=Region("chr17", 10000000, 15000000),
           page_size=100,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

       # Also available: paginate_het_dominant, paginate_hom_recessive

Kinship
-------

.. code-block:: python

   from dnaerys import DnaerysClient

   with DnaerysClient("db.dnaerys.org:443") as client:
       # All-pairs kinship for a cohort
       result = client.kinship(cohort_name="cohort1")
       for r in result.pairs:
           print(
               f"{r.sample1} - {r.sample2}: degree={r.degree.name}, "
               f"phi={r.phi_bwf}"
           )

       # Pairwise kinship between two samples
       result = client.kinship_duo(
           sample1="SAMPLE_001", sample2="SAMPLE_002",
       )
       for r in result.pairs:
           print(f"phi={r.phi_bwf}, degree={r.degree.name}")

Annotation filters
------------------

.. code-block:: python

   from dnaerys import (
       DnaerysClient, Region, AnnotationFilter,
       Consequence, Impact,
   )

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(
           consequence=[
               Consequence.MISSENSE_VARIANT,
               Consequence.STOP_GAINED,
           ],
           clin_significance=["PATHOGENIC", "LIKELY_PATHOGENIC"],
           impact=[Impact.HIGH, Impact.MODERATE],
       )
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(v)

Materialising results
---------------------

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       stream = client.select_variants(
           region=Region("chr17", 7661779, 7687546),
       )

       # Collect all variants into a list
       variants = stream.to_list()
       print(f"Got {len(variants)} variants")

       # Or convert to a pandas DataFrame
       # (requires: pip install dnaerys[pandas])
       stream = client.select_variants(
           region=Region("chr17", 7661779, 7687546),
       )
       df = stream.to_dataframe()
       print(df.head())
