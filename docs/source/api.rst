API Reference
=============

.. module:: dnaerys

Client
------

.. autoclass:: dnaerys.DnaerysClient
   :members:
   :exclude-members: close

   .. automethod:: close

Input types
-----------

.. autoclass:: dnaerys.Region
   :members:

.. autoclass:: dnaerys.Bracket
   :members:

.. autoclass:: dnaerys.AnnotationFilter
   :members:

Core result types
-----------------

.. autoclass:: dnaerys.Variant
   :members:

.. autoclass:: dnaerys.VariantWithStats
   :members:

Stream wrappers
---------------

.. autoclass:: dnaerys.VariantStream
   :members:

.. autoclass:: dnaerys.VariantWithStatsStream
   :members:

Pagination
----------

.. autoclass:: dnaerys.Page
   :members:

.. autoclass:: dnaerys.PaginatedQuery
   :members:

Response types
--------------

.. autoclass:: dnaerys.ResponseMetadata
   :members:

.. autoclass:: dnaerys.CountResult
   :members:

.. autoclass:: dnaerys.SamplesResult
   :members:

.. autoclass:: dnaerys.HealthResult
   :members:

.. autoclass:: dnaerys.ClusterNodesResult
   :members:

.. autoclass:: dnaerys.DatasetInfo
   :members:

.. autoclass:: dnaerys.Cohort
   :members:

.. autoclass:: dnaerys.PrsInfo
   :members:

.. autoclass:: dnaerys.PrsResult
   :members:

.. autoclass:: dnaerys.SampleScore
   :members:

.. autoclass:: dnaerys.SexMismatchResult
   :members:

.. autoclass:: dnaerys.SampleStat
   :members:

.. autoclass:: dnaerys.FstatXResult
   :members:

.. autoclass:: dnaerys.KinshipResult
   :members:

.. autoclass:: dnaerys.Relatedness
   :members:

.. autoclass:: dnaerys.SampleKinshipResult
   :members:

.. autoclass:: dnaerys.SampleRelatedness
   :members:

.. autoclass:: dnaerys.TopHweResult
   :members:

.. autoclass:: dnaerys.TopChi2Result
   :members:

Enums
-----

.. autoclass:: dnaerys.Chromosome
   :members:
   :undoc-members:

.. autoclass:: dnaerys.RefAssembly
   :members:
   :undoc-members:

.. autoclass:: dnaerys.VariantType
   :members:
   :undoc-members:

.. autoclass:: dnaerys.FeatureType
   :members:
   :undoc-members:

.. autoclass:: dnaerys.BioType
   :members:
   :undoc-members:

.. autoclass:: dnaerys.Consequence
   :members:
   :undoc-members:

.. autoclass:: dnaerys.Impact
   :members:
   :undoc-members:

.. autoclass:: dnaerys.SIFT
   :members:
   :undoc-members:

.. autoclass:: dnaerys.PolyPhen
   :members:
   :undoc-members:

.. autoclass:: dnaerys.ClinSignificance
   :members:
   :undoc-members:

.. autoclass:: dnaerys.AlphaMissense
   :members:
   :undoc-members:

.. autoclass:: dnaerys.KinshipDegree
   :members:
   :undoc-members:

Enum resolution helpers
^^^^^^^^^^^^^^^^^^^^^^^

.. autofunction:: dnaerys.resolve_chromosome

.. autofunction:: dnaerys.resolve_enum

.. autofunction:: dnaerys.resolve_assembly

Exceptions
----------

.. autoclass:: dnaerys.DnaerysError
   :members:

.. autoclass:: dnaerys.DnaerysConnectionError
   :members:

.. autoclass:: dnaerys.DnaerysAuthenticationError
   :members:

.. autoclass:: dnaerys.DnaerysNotFoundError
   :members:

.. autoclass:: dnaerys.DnaerysInvalidRequestError
   :members:

.. autoclass:: dnaerys.DnaerysServerError
   :members:

.. autoclass:: dnaerys.DnaerysResourceExhausted
   :members:

.. autoclass:: dnaerys.DnaerysIncompleteResultWarning
   :members:

Constants
---------

.. data:: dnaerys.PROTO_VERSION
   :type: str
   :value: "R1.17.8"

   Protocol buffer schema version that this library targets.
