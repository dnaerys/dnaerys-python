Pagination
==========

Why pagination matters
----------------------

Dnaerys is a distributed database. Its data is range-partitioned across *rings*
(nodes) with no duplication, and each ring **hard-caps** the number of variants
it returns per request (``DatasetInfo.max_variants_per_ring``, default 5000). ``skip`` and ``limit`` are applied **per ring**, not globally.

When you set ``limit=100`` on
:meth:`~dnaerys.DnaerysClient.select_variants`, that limit is a **hard global
cap** — you receive at most 100 results regardless of cluster topology. Because
the client fetches in internal, constant-window ``skip`` batches and trims the
result to exactly ``limit``, the cap may safely **exceed** a ring's per-request
limit and is still honoured (e.g. ``limit=50000`` works even though each ring
returns at most 5000 per request).

When you set ``limit=None`` a single request is issued and each ring returns up
to its cap, so results for very large regions may be **truncated**. To retrieve
*everything*, either pass a ``limit`` large enough, or paginate.

``skip`` is **not** exposed on the public ``select_*`` methods because its
per-ring semantics do not provide global offset-based pagination: ``skip=100`` makes each ring independently skip 100 rows.

How PaginatedQuery solves this
------------------------------

The ``paginate_*`` factory methods on :class:`~dnaerys.DnaerysClient` return a
:class:`~dnaerys.PaginatedQuery` that manages ``skip``/``limit`` internally:

1. It requests a per-ring window of ``buffer_size`` variants from every owner
   ring (``buffer_size`` defaults to, and is capped at, the server per-ring
   limit so no ring is left with a gap).
2. It keeps **every** ring's window (a round-trip can therefore yield up to
   ``buffer_size × owner_rings`` variants) in an internal ``collections.deque``.
3. When you call :meth:`~dnaerys.PaginatedQuery.next_page` (or iterate with
   ``for page in query``), it pops ``page_size`` variants from the buffer,
   refilling as many times as needed.
4. Each refill advances ``skip`` by a **constant** ``buffer_size``; because the
   window is ``≤`` the per-ring cap, this walks every ring's partition with no
   gaps and no duplicates.
5. Exhaustion is detected when a refill returns an empty batch.

This gives you clean, fixed-size pages — complete across the whole cluster —
without needing to know about topology or per-ring skip semantics.

Available paginate methods
--------------------------

.. list-table::
   :header-rows: 1
   :widths: 40 60

   * - Method
     - Description
   * - :meth:`~dnaerys.DnaerysClient.paginate_variants`
     - Paginate variant selection queries
   * - :meth:`~dnaerys.DnaerysClient.paginate_variants_with_stats`
     - Paginate variants with population statistics
   * - :meth:`~dnaerys.DnaerysClient.paginate_de_novo`
     - Paginate de novo candidate variants
   * - :meth:`~dnaerys.DnaerysClient.paginate_het_dominant`
     - Paginate heterozygous dominant candidates
   * - :meth:`~dnaerys.DnaerysClient.paginate_hom_recessive`
     - Paginate homozygous recessive candidates

Examples
--------

Basic pagination
^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       for page in client.paginate_variants(
           region=Region("chr17", 7661779, 7687546),
           page_size=100,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

Pagination with statistics
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       for page in client.paginate_variants_with_stats(
           regions=[Region("chr17", 7661779, 7687546)],
           samples=["NA10842", "HG00418"],
           page_size=50,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

Inheritance pagination
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from dnaerys import DnaerysClient, Region

   with DnaerysClient("db.dnaerys.org:443") as client:
       for page in client.paginate_de_novo(
           parent1="HG00418",
           parent2="HG00419",
           proband="HG00420",
           region=Region("chr17", 10000000, 15000000),
           page_size=50,
       ):
           print(f"Page {page.page_number}: {len(page.variants)} variants")

       # Also available:
       # client.paginate_het_dominant(...)
       # client.paginate_hom_recessive(...)

Controlling buffer size
^^^^^^^^^^^^^^^^^^^^^^^

``buffer_size`` is the **per-ring window** requested each round-trip. It
defaults to the server per-ring cap (discovered from ``dataset_info``, falling
back to 5000). It **must not exceed** that cap — a larger value is silently
clamped down (with a warning), because a window bigger than the cap would leave
gaps between pages. You may set a *smaller* value to reduce memory use:

.. code-block:: python

   query = client.paginate_variants(
       region=Region("chr17", 7661779, 7687546),
       page_size=100,
       buffer_size=1000,  # smaller per-ring window, more round-trips
   )

``page_size`` may be larger than ``buffer_size``; a page is simply assembled
from as many round-trips as needed.

Using as a context manager
^^^^^^^^^^^^^^^^^^^^^^^^^^

:class:`~dnaerys.PaginatedQuery` supports the context manager protocol. On
exit, the buffer is cleared and the query is marked as exhausted:

.. code-block:: python

   with client.paginate_variants(
       region=Region("chr17", 7661779, 7687546),
       page_size=100,
   ) as query:
       for page in query:
           if some_condition(page):
               break  # Buffer cleared on exit

Accessing metadata
^^^^^^^^^^^^^^^^^^

Accumulated server metadata is available via the
:attr:`~dnaerys.PaginatedQuery.metadata` property at any time:

.. code-block:: python

   query = client.paginate_variants(
       region=Region("chr17", 7661779, 7687546),
       page_size=100,
   )
   for page in query:
       pass
   print(f"Total elapsed: {query.metadata.elapsed_ms}ms")
   print(f"Total fetched: {query.total_fetched}")
