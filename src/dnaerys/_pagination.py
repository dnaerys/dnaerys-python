"""Paginated variant query API for the Dnaerys client library.

``PaginatedQuery`` manages an internal buffer via ``collections.deque``,
refills transparently from the server, and serves fixed-size pages to the
caller.  ``skip`` and ``limit`` become invisible implementation details.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from types import TracebackType

from dnaerys._stream import VariantStream
from dnaerys._types import ResponseMetadata, Variant


@dataclass(frozen=True, slots=True)
class Page:
    """A single page of variant results from a paginated query.

    Parameters
    ----------
    variants : tuple[Variant, ...]
        The variants in this page.
    page_number : int
        1-based page number.
    """

    variants: tuple[Variant, ...]
    page_number: int


class PaginatedQuery:
    """Iterator that serves fixed-size pages of variants from a Dnaerys query.

    Manages an internal ``collections.deque`` buffer, refilling it
    transparently from the server via the provided *fetch* callable.
    Callers see clean, fixed-size pages without needing to know about
    ``skip``/``limit`` or cluster topology.

    Parameters
    ----------
    fetch : Callable[[int, int], VariantStream]
        A callable that takes ``(skip, limit)`` and returns a
        ``VariantStream``.
    page_size : int
        Number of variants per page (last page may be shorter).
    buffer_size : int
        Number of variants to request per server round-trip.

    Raises
    ------
    ValueError
        If *page_size* < 1 or *buffer_size* < *page_size*.
    """

    def __init__(
        self,
        fetch: Callable[[int, int], VariantStream],
        *,
        page_size: int,
        buffer_size: int = 5000,
    ) -> None:
        if page_size < 1:
            raise ValueError("page_size must be >= 1")
        if buffer_size < page_size:
            raise ValueError("buffer_size must be >= page_size")

        self._fetch = fetch
        self._page_size = page_size
        self._buffer_size = buffer_size
        self._buffer: deque[Variant] = deque()
        self._offset: int = 0
        self._page_number: int = 0
        self._exhausted: bool = False
        self._total_fetched: int = 0

        # Metadata accumulators (same pattern as VariantStream)
        self._incomplete_cluster: bool = False
        self._affected: bool = False
        self._elapsed_ms: int = 0
        self._elapsed_db_ms: int = 0
        self._node_ids: set[str] = set()

    @property
    def page_size(self) -> int:
        """Number of variants per page."""
        return self._page_size

    @property
    def buffer_size(self) -> int:
        """Number of variants requested per server round-trip."""
        return self._buffer_size

    @property
    def total_fetched(self) -> int:
        """Total number of variants served across all pages so far."""
        return self._total_fetched

    @property
    def has_more(self) -> bool:
        """Whether more pages may be available.

        Returns ``True`` if the buffer contains variants or the server has
        not yet been confirmed exhausted.  Returns ``False`` only after
        iteration is complete and the buffer is empty.

        .. note::
            Before the first :meth:`next_page` call, this property returns
            ``True`` even if the query matches zero variants — no server
            call has been made yet, so exhaustion is unknown.  The first
            :meth:`next_page` call triggers the first server round-trip;
            if it returns no variants, :exc:`StopIteration` is raised
            immediately and ``has_more`` becomes ``False``.
        """
        return not (self._exhausted and len(self._buffer) == 0)

    @property
    def metadata(self) -> ResponseMetadata:
        """Accumulated metadata from all server round-trips so far."""
        return ResponseMetadata(
            elapsed_ms=self._elapsed_ms,
            elapsed_db_ms=self._elapsed_db_ms,
            node_id=",".join(sorted(self._node_ids)) if self._node_ids else "",
            incomplete_cluster=self._incomplete_cluster,
            affected=self._affected,
        )

    def _accumulate_metadata(self, stream_metadata: ResponseMetadata) -> None:
        self._incomplete_cluster = self._incomplete_cluster or stream_metadata.incomplete_cluster
        self._affected = self._affected or stream_metadata.affected
        self._elapsed_ms = max(self._elapsed_ms, stream_metadata.elapsed_ms)
        self._elapsed_db_ms = max(self._elapsed_db_ms, stream_metadata.elapsed_db_ms)
        if stream_metadata.node_id:
            for part in stream_metadata.node_id.split(","):
                part = part.strip()
                if part:
                    self._node_ids.add(part)

    def _refill(self) -> None:
        stream = self._fetch(self._offset, self._buffer_size)
        new_variants = stream.to_list()
        self._accumulate_metadata(stream.metadata)
        if not new_variants:
            self._exhausted = True
            return
        self._buffer.extend(new_variants)
        self._offset += self._buffer_size

    def next_page(self) -> Page:
        """Return the next page of variants.

        Raises
        ------
        StopIteration
            When no more variants are available.
        """
        while len(self._buffer) < self._page_size and not self._exhausted:
            self._refill()

        if not self._buffer:
            raise StopIteration

        count = min(self._page_size, len(self._buffer))
        page_variants = [self._buffer.popleft() for _ in range(count)]
        self._page_number += 1
        self._total_fetched += count
        return Page(variants=tuple(page_variants), page_number=self._page_number)

    def __iter__(self) -> Iterator[Page]:
        return self

    def __next__(self) -> Page:
        return self.next_page()

    def __enter__(self) -> PaginatedQuery:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._buffer.clear()
        self._exhausted = True
