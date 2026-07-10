Changelog
=========

v0.2.1 (July 2026)
------------------

- **Lower the minimum supported Python to 3.11** (previously 3.12). The library
  is fully source-compatible with Python 3.11 — there are no API changes.
  ``requires-python`` is now ``>=3.11`` and a ``Python :: 3.11`` classifier was
  added. Python 3.12 and 3.13 remain supported.

v0.2.0 (July 2026)
------------------

- **Breaking changes**: Retargets the Dnaerys proto schema to **R1.20.0**.
- **Per-ring cap awareness**: R1.20.0 hard-caps each ring's streaming response
  at ``DatasetInfo.max_variants_per_ring`` (new field). The client now discovers
  this cap (cached; fallback 5000) and uses it to keep results complete:

  - **Strong** ``limit``: :meth:`~dnaerys.DnaerysClient.select_variants`,
    :meth:`~dnaerys.DnaerysClient.select_variants_with_stats` and the inheritance
    selectors now fetch in internal constant-window ``skip`` batches and trim to
    exactly ``limit``. ``limit`` may now **exceed** the per-ring cap (and
    ``cap × rings``) and is still honoured exactly. With ``limit=None`` a single
    request is made and each ring returns up to its cap, so large regions may be
    truncated — pass a ``limit`` or paginate for complete results.
  - **Pagination**: ``paginate_*`` now keeps every ring's full window each
    round-trip. ``buffer_size`` defaults to the server per-ring cap and is clamped to it
    (values above the cap warn); ``page_size`` may now exceed ``buffer_size``.
- :class:`~dnaerys.Chromosome` enum members renamed to drop the underscore:
  ``CHR_1`` → ``CHR1`` … ``CHR_X`` → ``CHRX``, ``CHR_Y`` → ``CHRY``,
  ``CHR_MT`` → ``CHRMT``.  Integer values are unchanged, and
  :func:`~dnaerys.resolve_chromosome` still accepts the old string forms
  (``"chr_1"``, ``"chr1"``, ``"1"``, ``"chrX"``, …).
- :class:`~dnaerys.Variant`: the per-variant samples counters: all samples ``homc``/``hetc``/``misc``
  → ``hom_samples``/``het_samples``/``mis_samples``; the female sample counters
  ``homfc``/``hetfc``/``misfc`` → ``hom_samples_fx``/``het_samples_fx``/``mis_samples_fx``
  (X-chromosome only). New male samples counters (X and Y only): ``hom_samples_mxy``, ``het_samples_mxy``, ``mis_samples_mxy``.
- :class:`~dnaerys.VariantWithStats`: virtual-cohort counters
  ``vhomc``/``vhetc``/``vhomfc``/``vhetfc`` →
  ``v_hom_samples``/``v_het_samples``/``v_hom_samples_fx``/``v_het_samples_fx``,
  plus two new male X&Y counters ``v_hom_samples_mxy`` and ``v_het_samples_mxy``.
- ``to_dataframe()`` column schemas updated accordingly
  (:class:`~dnaerys.Variant` 24 columns, :class:`~dnaerys.VariantWithStats`
  37 columns).
- Documented that the ``gnomad_exomes_af_lt`` / ``gnomad_genomes_af_lt``
  filters include unannotated variants (gnomAD AF = 0).

v0.1.0 (March 2026)
-------------------

- Initial release targeting Dnaerys proto schema **R1.17.8**.
- 27 public methods on :class:`~dnaerys.DnaerysClient` covering variant
  selection, sample queries, inheritance analysis, kinship, and statistics.
- Streaming iteration with :class:`~dnaerys.VariantStream` and
  :class:`~dnaerys.VariantWithStatsStream`.
- Paginated queries via :class:`~dnaerys.PaginatedQuery`.
- 12 :class:`~enum.IntEnum` classes mirroring all proto enums.
- Clean exception hierarchy mapping gRPC status codes.
- Optional pandas DataFrame export via ``to_dataframe()``.
