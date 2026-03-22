Annotation Filters
==================

Overview
--------

:class:`~dnaerys.AnnotationFilter` lets you restrict variant queries by
annotation criteria — consequence, impact, allele frequency, predictive
scores, clinical significance, and more.  Pass it via the ``annotations``
parameter to any of these methods:

- :meth:`~dnaerys.DnaerysClient.select_variants`
- :meth:`~dnaerys.DnaerysClient.count_variants`
- :meth:`~dnaerys.DnaerysClient.select_samples`
- :meth:`~dnaerys.DnaerysClient.count_samples`
- :meth:`~dnaerys.DnaerysClient.select_de_novo`
- :meth:`~dnaerys.DnaerysClient.select_het_dominant`
- :meth:`~dnaerys.DnaerysClient.select_hom_recessive`
- :meth:`~dnaerys.DnaerysClient.paginate_variants`
- :meth:`~dnaerys.DnaerysClient.paginate_variants_with_stats`
- :meth:`~dnaerys.DnaerysClient.paginate_de_novo`
- :meth:`~dnaerys.DnaerysClient.paginate_het_dominant`
- :meth:`~dnaerys.DnaerysClient.paginate_hom_recessive`

**AND/OR semantics:** different fields are AND'd together; multiple values
within a single field are OR'd.  For example, if you set
``consequence=[Consequence.MISSENSE_VARIANT, Consequence.STOP_GAINED]`` and
``impact=[Impact.HIGH]``, Dnaerys returns variants that match (MISSENSE_VARIANT
**OR** STOP_GAINED) **AND** (HIGH impact).

All enum fields accept either enum members or case-insensitive strings:

.. code-block:: python

   from dnaerys import AnnotationFilter, Consequence

   # These are equivalent:
   ann = AnnotationFilter(consequence=[Consequence.MISSENSE_VARIANT])
   ann = AnnotationFilter(consequence=["MISSENSE_VARIANT"])
   ann = AnnotationFilter(consequence=["missense_variant"])


Variant consequences and impact (VEP)
--------------------------------------

The :class:`~dnaerys.Consequence` enum has 41 members corresponding to
`Sequence Ontology consequence terms
<https://asia.ensembl.org/info/genome/variation/prediction/predicted_data.html#consequences>`_.
Each consequence is assigned an :class:`~dnaerys.Impact` level by VEP.

**High impact** consequences cause protein truncation or loss of function:

- ``TRANSCRIPT_ABLATION``
- ``SPLICE_ACCEPTOR_VARIANT``, ``SPLICE_DONOR_VARIANT``
- ``STOP_GAINED``, ``STOP_LOST``, ``START_LOST``
- ``FRAMESHIFT_VARIANT``
- ``TRANSCRIPT_AMPLIFICATION``

**Moderate impact** consequences alter the protein but do not truncate it:

- ``MISSENSE_VARIANT``
- ``INFRAME_INSERTION``, ``INFRAME_DELETION``
- ``PROTEIN_ALTERING_VARIANT``

**Low impact** consequences are unlikely to change protein behaviour:

- ``SYNONYMOUS_VARIANT``
- ``SPLICE_REGION_VARIANT``
- ``START_RETAINED_VARIANT``, ``STOP_RETAINED_VARIANT``

**Modifier** consequences affect non-coding or intergenic regions:

- ``INTRON_VARIANT``
- ``UPSTREAM_GENE_VARIANT``, ``DOWNSTREAM_GENE_VARIANT``
- ``INTERGENIC_VARIANT``

Filtering by individual consequences
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, Consequence

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(consequence=[
           Consequence.STOP_GAINED,
           Consequence.FRAMESHIFT_VARIANT,
           Consequence.SPLICE_ACCEPTOR_VARIANT,
           Consequence.SPLICE_DONOR_VARIANT,
       ])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(v)

Using Impact as a shortcut
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Instead of listing every high-impact consequence individually, use the
:class:`~dnaerys.Impact` enum:

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, Impact

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(impact=[Impact.HIGH])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(v)

Combining consequence and impact
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Fields are AND'd, so you can combine them for precision — for example, to
select only missense variants that VEP classifies as moderate impact:

.. code-block:: python

   ann = AnnotationFilter(
       consequence=[Consequence.MISSENSE_VARIANT],
       impact=[Impact.MODERATE],
   )


Variant types
-------------

The :class:`~dnaerys.VariantType` enum has 34 members covering short variants
and structural variants.  Common short variant types:

- ``SNV`` — single nucleotide variant
- ``INSERTION``, ``DELETION``, ``INDEL``
- ``SUBSTITUTION``

See `Ensembl variant classes
<https://asia.ensembl.org/info/genome/variation/prediction/classification.html#classes>`_
for the full classification.

Filtering to SNVs only
^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, VariantType

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(variant_type=[VariantType.SNV])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
           limit=10
       ):
           print(v)


Clinical significance (ClinVar)
--------------------------------

The :class:`~dnaerys.ClinSignificance` enum has 19 members corresponding to
`ClinVar clinical significance categories
<https://www.ncbi.nlm.nih.gov/clinvar/docs/clinsig/>`_.  Common values:

- ``PATHOGENIC``
- ``LIKELY_PATHOGENIC``
- ``UNCERTAIN_SIGNIFICANCE``
- ``LIKELY_BENIGN``
- ``CLNSIG_BENIGN``
- ``CONFLICTING_INTERPRETATIONS``

Other values include ``DRUG_RESPONSE``, ``RISK_FACTOR``, ``PROTECTIVE``,
``PATHOGENIC_LOW_PENETRANCE``, ``LIKELY_RISK_ALLELE``, and more.

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, ClinSignificance

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(clin_significance=[
           ClinSignificance.PATHOGENIC,
           ClinSignificance.LIKELY_PATHOGENIC,
       ])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} {v.ref}>{v.alt}")

String aliases work the same way:

.. code-block:: python

   ann = AnnotationFilter(clin_significance=["PATHOGENIC", "LIKELY_PATHOGENIC"])


Predictive scores
-----------------

AlphaMissense
^^^^^^^^^^^^^^

`AlphaMissense <https://www.science.org/doi/10.1126/science.adg7492>`_
predicts pathogenicity of missense variants.  You can filter by either
categorical class or numeric score, but **not both** — combining them raises
``ValueError`` because the server silently ignores ``am_class`` when score
bounds are present.

The :class:`~dnaerys.AlphaMissense` enum has three members:

- ``AM_LIKELY_BENIGN`` — score < 0.34
- ``AM_AMBIGUOUS`` — score 0.34–0.564
- ``AM_LIKELY_PATHOGENIC`` — score > 0.564

**Filtering by class:**

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, AlphaMissense

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(am_class=[AlphaMissense.AM_LIKELY_PATHOGENIC])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} {v.ref}>{v.alt} AM={v.am_score}")

**Filtering by score range:**

.. code-block:: python

   # Variants with AlphaMissense score > 0.8
   ann = AnnotationFilter(am_score_gt=0.8)

**Mutual exclusivity — this raises ValueError:**

.. code-block:: python

   # ValueError: am_score_lt/am_score_gt and am_class are mutually exclusive
   ann = AnnotationFilter(
       am_score_gt=0.5,
       am_class=[AlphaMissense.AM_LIKELY_PATHOGENIC],
   )

.. note::

   The examples below using CADD, PolyPhen, and SIFT will not yield variants
   against ``db.dnaerys.org:443`` because the KGP dataset is not annotated
   with these scores due to license restrictions.

CADD
^^^^^

`CADD <https://cadd.gs.washington.edu>`_ (Combined Annotation Dependent
Depletion) scores are available in two forms:

- **Raw score** (``cadd_raw_lt`` / ``cadd_raw_gt``) — the untransformed
  score.
- **Phred-scaled score** (``cadd_phred_lt`` / ``cadd_phred_gt``) — a
  rank-based score that is more interpretable:

  - Phred > 10 → top 10% most deleterious
  - Phred > 20 → top 1% most deleterious
  - Phred > 30 → top 0.1% most deleterious

In practice, a CADD phred threshold of 20 or higher is a common filter for
potentially deleterious variants.

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Variants in the top 1% most deleterious by CADD
       ann = AnnotationFilter(cadd_phred_gt=20)
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} {v.ref}>{v.alt} CADD={v.cadd_phred}")

.. code-block:: python

   # Using both bounds to define a range
   ann = AnnotationFilter(cadd_phred_gt=20, cadd_phred_lt=30)

PolyPhen
^^^^^^^^^

The :class:`~dnaerys.PolyPhen` enum predicts the impact of amino acid
substitutions:

- ``PROBABLY_DAMAGING``
- ``POSSIBLY_DAMAGING``
- ``BENIGN``
- ``UNKNOWN``

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, PolyPhen

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(polyphen=[PolyPhen.PROBABLY_DAMAGING])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} {v.ref}>{v.alt}")

SIFT
^^^^^

The :class:`~dnaerys.SIFT` enum predicts whether an amino acid substitution
affects protein function:

- ``DELETERIOUS``
- ``TOLERATED``

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, SIFT

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(sift=[SIFT.DELETERIOUS])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} {v.ref}>{v.alt}")


Population frequency filters
-----------------------------

All frequency filters use strict inequality: ``af_lt`` means "AF < value"
and ``af_gt`` means "AF > value".  Setting a filter to ``None`` (the default)
disables it.

Dataset allele frequency
^^^^^^^^^^^^^^^^^^^^^^^^^

``af_lt`` and ``af_gt`` filter by the allele frequency within the loaded
dataset itself:

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Rare variants: dataset AF < 1%
       ann = AnnotationFilter(af_lt=0.01)
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
           limit=100
       ):
           print(f"{v.start} AF={v.af}")

gnomAD exomes
^^^^^^^^^^^^^^

``gnomad_exomes_af_lt`` and ``gnomad_exomes_af_gt`` filter by the allele
frequency in gnomAD exomes (proto field ``gnomADe``):

.. code-block:: python

   # Variants with gnomAD exomes AF < 0.001 (very rare in gnomAD)
   ann = AnnotationFilter(gnomad_exomes_af_lt=0.001)

gnomAD genomes
^^^^^^^^^^^^^^^

``gnomad_genomes_af_lt`` and ``gnomad_genomes_af_gt`` filter by the allele
frequency in gnomAD genomes (proto field ``gnomADg``):

.. code-block:: python

   # Variants absent from or very rare in gnomAD genomes
   ann = AnnotationFilter(gnomad_genomes_af_lt=0.0001)

The 0.0 sentinel and gnomAD presence
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Variants not annotated in gnomAD have an AF of ``0.0``.  This means
``gnomad_exomes_af_gt=0`` selects only variants that **are** present in
gnomAD exomes (i.e. AF > 0.0):

.. code-block:: python

   # Only variants that exist in gnomAD exomes
   ann = AnnotationFilter(gnomad_exomes_af_gt=0)

Conversely, there is no direct way to select variants *absent* from gnomAD
using frequency filters alone.

**Important: ``gnomad_exomes_af_lt`` with any positive threshold will NOT include
unannotated variants (AF = 0.0).**


Feature and biotype filters (VEP)
-----------------------------------

FeatureType
^^^^^^^^^^^^

The :class:`~dnaerys.FeatureType` enum controls which VEP feature types are
included:

- ``TRANSCRIPT`` — gene transcripts
- ``REGULATORYFEATURE`` — regulatory elements from the Ensembl Regulatory Build
- ``MOTIFFEATURE`` — transcription factor binding motifs

BioType
^^^^^^^^

The :class:`~dnaerys.BioType` enum has 47 members covering transcript biotypes
and regulatory biotypes.

Common **transcript biotypes**:

- ``PROTEIN_CODING``
- ``LNCRNA``, ``LINCRNA``, ``ANTISENSE``
- ``NONSENSE_MEDIATED_DECAY``
- ``PSEUDOGENE``, ``PROCESSED_PSEUDOGENE``
- ``MIRNA``, ``SNRNA``, ``SNORNA``, ``RRNA``

**Regulatory biotypes**:

- ``PROMOTER``, ``PROMOTER_FLANKING_REGION``
- ``ENHANCER``
- ``CTCF_BINDING_SITE``
- ``OPEN_CHROMATIN_REGION``

See `Ensembl biotypes <https://asia.ensembl.org/info/genome/genebuild/biotypes.html>`_
for the full list.

Filtering to protein-coding transcripts
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, BioType

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(bio_type=[BioType.PROTEIN_CODING])
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
           limit=100
       ):
           print(f"{v.start} {v.ref}>{v.alt}")

Combining feature type and biotype
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import AnnotationFilter, FeatureType, BioType

   # Only variants affecting regulatory enhancers
   ann = AnnotationFilter(
       feature_type=[FeatureType.REGULATORYFEATURE],
       bio_type=[BioType.ENHANCER],
   )


Exclusion flags
---------------

biallelic_only / multiallelic_only
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These boolean flags control whether to include only biallelic or only
multiallelic variant sites.  They are **mutually exclusive** — setting both
to ``True`` raises ``ValueError``.

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Only biallelic sites
       ann = AnnotationFilter(biallelic_only=True)
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       ):
           print(f"{v.start} biallelic={v.biallelic}")

.. code-block:: python

   # Only multiallelic sites
   ann = AnnotationFilter(multiallelic_only=True)

exclude_males / exclude_females
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

These flags exclude samples by sex.  They are **mutually exclusive** —
setting both to ``True`` raises ``ValueError`` (the result set would be
empty).

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter

   with DnaerysClient("db.dnaerys.org:443") as client:
       # Exclude male samples
       ann = AnnotationFilter(exclude_males=True)
       count = client.count_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
       )
       print(f"Variants in females only: {count.count}")


Combining filters
-----------------

Since different fields are AND'd, you can build complex queries that
combine multiple filter categories.  Here is an example that selects
high impact heterozygous variants in transcripts in TP53:

.. code-block:: python

   from dnaerys import DnaerysClient, Region, AnnotationFilter, FeatureType, Impact

   with DnaerysClient("db.dnaerys.org:443") as client:
       ann = AnnotationFilter(
           impact=[Impact.HIGH],
           feature_type=[FeatureType.TRANSCRIPT],
       )
       for v in client.select_variants(
           region=Region("chr17", 7661779, 7687546),
           annotations=ann,
           hom=False,
           het=True,
       ):
           print(v)

The same :class:`~dnaerys.AnnotationFilter` instance can be reused across
multiple queries or combined with sample-level parameters on methods like
:meth:`~dnaerys.DnaerysClient.select_variants_with_stats` and the
inheritance methods.


Validation rules summary
-------------------------

:class:`~dnaerys.AnnotationFilter` validates its fields at construction time.
The following table summarises which combinations raise ``ValueError`` versus
emit a warning:

.. list-table::
   :header-rows: 1
   :widths: 50 20 30

   * - Condition
     - Result
     - Reason
   * - ``biallelic_only=True`` and ``multiallelic_only=True``
     - ``ValueError``
     - Mutually exclusive
   * - ``exclude_males=True`` and ``exclude_females=True``
     - ``ValueError``
     - Would produce an empty result set
   * - ``am_score_lt`` or ``am_score_gt`` set with non-empty ``am_class``
     - ``ValueError``
     - Server silently ignores ``am_class`` when score bounds are present
   * - ``af_gt >= af_lt`` (both set)
     - ``warnings.warn``
     - Empty range — no value can satisfy both bounds
   * - ``gnomad_exomes_af_gt >= gnomad_exomes_af_lt`` (both set)
     - ``warnings.warn``
     - Empty range
   * - ``gnomad_genomes_af_gt >= gnomad_genomes_af_lt`` (both set)
     - ``warnings.warn``
     - Empty range
   * - ``cadd_raw_gt >= cadd_raw_lt`` (both set)
     - ``warnings.warn``
     - Empty range
   * - ``cadd_phred_gt >= cadd_phred_lt`` (both set)
     - ``warnings.warn``
     - Empty range
   * - ``am_score_gt >= am_score_lt`` (both set)
     - ``warnings.warn``
     - Empty range
   * - Unrecognised enum string value
     - ``ValueError``
     - Raised by enum resolution during construction
