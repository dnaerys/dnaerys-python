Changelog
=========

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
