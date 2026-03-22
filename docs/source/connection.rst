Connection Options
==================

The :class:`~dnaerys.DnaerysClient` constructor accepts several parameters
to control connection behaviour.

TLS (default)
-------------

By default, the client creates a secure TLS channel using default SSL
credentials:

.. code-block:: python

   from dnaerys import DnaerysClient

   # Uses default SSL credentials
   client = DnaerysClient("db.dnaerys.org:443")

Custom TLS credentials
^^^^^^^^^^^^^^^^^^^^^^

Pass your own :class:`grpc.ChannelCredentials` for custom certificate authority
chains or mutual TLS:

.. code-block:: python

   import grpc
   from dnaerys import DnaerysClient

   creds = grpc.ssl_channel_credentials(
       root_certificates=open("ca.pem", "rb").read(),
   )
   client = DnaerysClient("db.dnaerys.org:443", credentials=creds)

Plain HTTP (no TLS)
-------------------

For local development or testing without TLS:

.. code-block:: python

   from dnaerys import DnaerysClient

   client = DnaerysClient("localhost:50051", tls=False)

.. note::

   Providing ``credentials`` with ``tls=False`` raises :exc:`ValueError`.

Timeouts
--------

Default timeout
^^^^^^^^^^^^^^^

Set a default timeout (in seconds) for all RPC calls:

.. code-block:: python

   from dnaerys import DnaerysClient

   client = DnaerysClient("db.dnaerys.org:443", default_timeout=30.0)

Per-call override
^^^^^^^^^^^^^^^^^

Every method accepts a ``timeout`` keyword argument that overrides the default:

.. code-block:: python

   result = client.health(timeout=5.0)

If neither the per-call nor default timeout is set, calls have no timeout
(they will block until the server responds or the connection drops).

Reference assembly
------------------

The default reference assembly for all queries is ``GRCh38``. Set a different
default at construction time:

.. code-block:: python

   from dnaerys import DnaerysClient, RefAssembly

   client = DnaerysClient(
       "db.dnaerys.org:443",
       assembly=RefAssembly.GRCh37,
   )

Or override per-call:

.. code-block:: python

   from dnaerys import Region

   result = client.count_variants(
       region=Region("chr17", 7661779, 7687546),
       assembly="GRCh38",
   )

Assembly values can be passed as :class:`~dnaerys.RefAssembly` enum members or
case-insensitive strings (``"GRCh37"``, ``"grch38"``).

Context manager
---------------

:class:`~dnaerys.DnaerysClient` implements the context manager protocol.
Using ``with`` ensures the underlying gRPC channel is closed on exit:

.. code-block:: python

   from dnaerys import DnaerysClient

   with DnaerysClient("db.dnaerys.org:443") as client:
       result = client.health()
       print(result.status)
   # Channel is closed here

You can also close manually:

.. code-block:: python

   client = DnaerysClient("db.dnaerys.org:443")
   # ... use client ...
   client.close()

Constructor reference
---------------------

.. autoclass:: dnaerys.DnaerysClient
   :noindex:
   :no-members:
