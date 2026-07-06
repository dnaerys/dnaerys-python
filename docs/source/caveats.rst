Important Caveats
=================

This page documents behaviours and conventions that may surprise new users
of the library.

hom/het defaults
----------------

By default, :meth:`~dnaerys.DnaerysClient.select_variants`,
:meth:`~dnaerys.DnaerysClient.count_variants`,
:meth:`~dnaerys.DnaerysClient.select_samples`, and
:meth:`~dnaerys.DnaerysClient.count_samples` set both ``hom=True`` and
``het=True``. This means queries include **both** homozygous and heterozygous
variants.

This diverges from the proto default (where ``hom`` and ``het`` are ``false``
by default). The Python client defaults are chosen for the most common use
case — querying all variant genotypes.

To query only homozygous or only heterozygous variants, set one to ``False``:

.. code-block:: python

   # Only heterozygous variants
   for v in client.select_variants(
       region=Region("chr17", 7661779, 7687546),
       hom=False,
       het=True,
   ):
       print(v)

limit semantics
---------------

On :meth:`~dnaerys.DnaerysClient.select_variants`,
:meth:`~dnaerys.DnaerysClient.select_variants_with_stats`, and the inheritance
methods (:meth:`~dnaerys.DnaerysClient.select_de_novo`,
:meth:`~dnaerys.DnaerysClient.select_het_dominant`,
:meth:`~dnaerys.DnaerysClient.select_hom_recessive`), ``limit`` is a
**hard global cap**. You receive at most ``limit`` results regardless of cluster
topology. Each ring hard-caps its own per-request response, so the
client fetches in internal constant-window batches and trims to exactly
``limit`` — meaning ``limit`` may **exceed** a ring's per-request cap and is
still honoured (e.g. ``limit=50000`` works even where each ring returns at most
5000 per request).

When ``limit=None`` a single request is issued and **each ring returns up to its
per-ring cap** (``DatasetInfo.max_variants_per_ring``, default 5000).
Results for large regions are therefore **truncated** — pass a ``limit`` or use
``paginate_*`` to retrieve everything.

On :meth:`~dnaerys.DnaerysClient.select_samples` (and
:meth:`~dnaerys.DnaerysClient.select_samples_hom_ref`), ``skip`` and ``limit``
have standard global semantics — the server aggregates sample results across
nodes before applying skip/limit, so ``limit=10`` returns exactly 10 (or fewer
if exhausted) regardless of cluster topology.

Use paginate_* for full result sets
------------------------------------

If you need offset-based pagination through large result sets, use the
``paginate_*`` methods instead of manually managing ``limit``. See
:doc:`pagination` for details.

to_dataframe() memory warning
------------------------------

:meth:`~dnaerys.VariantStream.to_list` and
:meth:`~dnaerys.VariantStream.to_dataframe` are **terminal operations** that
materialise the entire stream into memory. For genome-wide queries, this may
require substantial memory.

Consider iterating with a ``for`` loop for large result sets:

.. code-block:: python

   # Memory-safe: processes one variant at a time
   for v in client.select_variants(region=region):
       process(v)

   # Memory-intensive: loads everything into RAM
   df = client.select_variants(region=region).to_dataframe()

0.0 sentinel for unannotated float fields
------------------------------------------

Annotation float fields on :class:`~dnaerys.Variant` and
:class:`~dnaerys.VariantWithStats` use ``0.0`` as a sentinel meaning
"not annotated":

- ``gnomad_exomes_af``
- ``gnomad_genomes_af``
- ``cadd_raw``
- ``cadd_phred``
- ``am_score``

This mirrors the proto convention where the default float value (0.0) indicates
absence of annotation data. When processing these fields, check for ``0.0``
to distinguish between "annotated as zero" and "not annotated":

.. code-block:: python

   for v in client.select_variants(region=region):
       if v.gnomad_exomes_af != 0.0:
           print(f"gnomAD exomes AF: {v.gnomad_exomes_af}")
       else:
           print("Not annotated in gnomAD exomes")

