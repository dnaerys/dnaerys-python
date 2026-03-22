Error Handling
==============

The library translates gRPC status codes into a clean exception hierarchy
rooted at :class:`~dnaerys.DnaerysError`. All exceptions expose an
:attr:`~dnaerys.DnaerysError.is_retryable` property to help with retry logic.

Exception hierarchy
-------------------

.. code-block:: text

   DnaerysError (base)                       is_retryable = False
   +-- DnaerysConnectionError                is_retryable = True
   |       UNAVAILABLE, DEADLINE_EXCEEDED
   +-- DnaerysAuthenticationError             is_retryable = False
   |       UNAUTHENTICATED, PERMISSION_DENIED
   +-- DnaerysNotFoundError                   is_retryable = False
   |       NOT_FOUND
   +-- DnaerysInvalidRequestError             is_retryable = False
   |       INVALID_ARGUMENT, FAILED_PRECONDITION, OUT_OF_RANGE
   +-- DnaerysServerError                     is_retryable = False
   |       INTERNAL, UNKNOWN, DATA_LOSS, UNIMPLEMENTED
   +-- DnaerysResourceExhausted               is_retryable = True
           RESOURCE_EXHAUSTED

   DnaerysIncompleteResultWarning (UserWarning — not part of error hierarchy)
       Emitted when affected=True in a server response.

Catching errors
---------------

Catch the base class to handle any Dnaerys error:

.. code-block:: python

   from dnaerys import DnaerysClient, DnaerysError

   try:
       with DnaerysClient("db.dnaerys.org:443") as client:
           result = client.health()
   except DnaerysError as e:
       print(f"Error: {e}")
       print(f"Retryable: {e.is_retryable}")

Or catch specific subclasses for targeted handling:

.. code-block:: python

   from dnaerys import (
       DnaerysClient, Region,
       DnaerysConnectionError,
       DnaerysInvalidRequestError,
       DnaerysError,
   )

   try:
       with DnaerysClient("db.dnaerys.org:443") as client:
           for v in client.select_variants():
               print(v)
   except DnaerysInvalidRequestError as e:
       print(f"Bad request (retryable={e.is_retryable}): {e}")
   except DnaerysConnectionError as e:
       print(f"Connection failed (retryable={e.is_retryable}): {e}")
   except DnaerysError as e:
       print(f"Other error: {e}")

Client-side validation
----------------------

Input types validate their parameters at construction time. These raise
standard :exc:`ValueError` or :exc:`TypeError`, **not** :class:`~dnaerys.DnaerysError`:

.. code-block:: python

   from dnaerys import Region

   try:
       region = Region("chr17", -1, 7687546)
   except ValueError as e:
       print(f"ValueError: {e}")
       # "start must be >= 1, got -1"

Retry logic
-----------

Use the :attr:`~dnaerys.DnaerysError.is_retryable` property to implement
retry logic:

.. code-block:: python

   import time
   from dnaerys import DnaerysClient, Region, DnaerysError

   def query_with_retry(client, region, max_retries=3):
       for attempt in range(max_retries):
           try:
               return client.count_variants(region=region)
           except DnaerysError as e:
               if not e.is_retryable or attempt == max_retries - 1:
                   raise
               time.sleep(2 ** attempt)  # Exponential backoff

Currently retryable exceptions:

- :class:`~dnaerys.DnaerysConnectionError` — server unreachable or timeout
- :class:`~dnaerys.DnaerysResourceExhausted` — rate limit or quota exceeded

Incomplete result warning
-------------------------

:class:`~dnaerys.DnaerysIncompleteResultWarning` is a :class:`UserWarning`
(not part of the error hierarchy) emitted when results may be incomplete due
to unreachable cluster nodes. It fires when a server response has
``affected=True``.

Suppress it if needed:

.. code-block:: python

   import warnings
   from dnaerys import DnaerysIncompleteResultWarning

   warnings.filterwarnings(
       "ignore", category=DnaerysIncompleteResultWarning,
   )

Accessing the original gRPC error
----------------------------------

The original gRPC error is chained via ``raise ... from``, so you can inspect
the raw status code and details:

.. code-block:: python

   from dnaerys import DnaerysClient, DnaerysError

   try:
       with DnaerysClient("db.dnaerys.org:443") as client:
           client.health()
   except DnaerysError as e:
       if e.__cause__:
           grpc_error = e.__cause__
           print(f"gRPC code: {grpc_error.code()}")
           print(f"gRPC details: {grpc_error.details()}")
