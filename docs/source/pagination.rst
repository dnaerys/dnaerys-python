Pagination
==========

Why pagination matters
----------------------

Dnaerys is a distributed database. When you set ``limit=100`` on
:meth:`~dnaerys.DnaerysClient.select_variants`, that limit is a **hard global
cap** enforced client-side by the stream wrapper — you will receive at most 100
results regardless of how many nodes serve the query. The value is also forwarded
to the server as a performance hint.

However, ``skip`` is **not** exposed on the public ``select_*`` methods because
its per-node semantics do not provide true global offset-based pagination. If
a cluster has 8 nodes and you set ``skip=100`` in the underlying gRPC call,
each node independently skips 100 rows.

How PaginatedQuery solves this
------------------------------

The ``paginate_*`` factory methods on :class:`~dnaerys.DnaerysClient` return a
:class:`~dnaerys.PaginatedQuery` that manages ``skip``/``limit`` internally:

1. It fetches a batch of ``buffer_size`` variants from the server (default 5000).
2. It stores them in an internal ``collections.deque`` buffer.
3. When you call :meth:`~dnaerys.PaginatedQuery.next_page` (or iterate with
   ``for page in query``), it pops ``page_size`` variants from the buffer.
4. When the buffer runs low, it transparently fetches the next batch from the
   server with an incremented ``skip``.
5. Exhaustion is detected when the server returns an empty batch.

This gives you clean, fixed-size pages without needing to know about cluster
topology or per-node skip semantics.

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

The ``buffer_size`` parameter (default 5000) controls how many variants are
fetched per server round-trip. Increase it to reduce round-trips for large
result sets, or decrease it to limit memory usage:

.. code-block:: python

   query = client.paginate_variants(
       region=Region("chr17", 7661779, 7687546),
       page_size=100,
       buffer_size=10000,  # Fetch 10k variants per round-trip
   )

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
