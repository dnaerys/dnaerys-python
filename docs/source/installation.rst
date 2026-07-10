Installation
============

Requirements
------------

- Python 3.11 or later

Install from PyPI
-----------------

.. code-block:: bash

   pip install dnaerys

With DataFrame support
----------------------

To use the ``to_dataframe()`` method on streaming results, install with the
``pandas`` extra:

.. code-block:: bash

   pip install dnaerys[pandas]

This pulls in `pandas <https://pandas.pydata.org/>`_ >= 2.0.

Development install
-------------------

Clone the repository and install in editable mode with development dependencies:

.. code-block:: bash

   git clone https://github.com/dnaerys/dnaerys-python.git
   cd dnaerys-python
   pip install -e ".[dev]"

This installs ``pytest``, ``grpcio-tools``, ``build``, and ``twine`` in addition
to the runtime dependencies.

Verify the installation
-----------------------

.. code-block:: python

   from dnaerys import DnaerysClient, PROTO_VERSION
   print(f'dnaerys installed, proto version: {PROTO_VERSION}')
