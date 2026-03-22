"""Thread safety tests for DnaerysClient."""

from __future__ import annotations

from concurrent import futures

import pytest

from dnaerys import DnaerysClient, Region
from tests.conftest import make_alleles_response


class TestThreadSafety:
    def test_concurrent_unary_calls(self, client, fake_servicer):
        """10 threads each calling count_variants, all return correct result."""
        def call_count(_):
            return client.count_variants(region=Region("chr1", 100, 200))

        with futures.ThreadPoolExecutor(max_workers=10) as pool:
            results = list(pool.map(call_count, range(10)))
        assert all(r.count == 42 for r in results)

    def test_concurrent_streaming_calls(self, client, fake_servicer):
        """5 threads each iterating select_variants, no cross-contamination."""
        fake_servicer.variant_chunks = [make_alleles_response(n_variants=3)]

        def call_select(_):
            stream = client.select_variants(region=Region("chr1", 100, 200))
            return stream.to_list()

        with futures.ThreadPoolExecutor(max_workers=5) as pool:
            results = list(pool.map(call_select, range(5)))
        assert all(len(variants) == 3 for variants in results)

    def test_concurrent_mixed_calls(self, client, fake_servicer):
        """Mix of count_variants and select_variants from thread pool."""
        fake_servicer.variant_chunks = [make_alleles_response(n_variants=2)]

        def mixed_call(i):
            if i % 2 == 0:
                return client.count_variants(region=Region("chr1", 100, 200))
            else:
                stream = client.select_variants(region=Region("chr1", 100, 200))
                return stream.to_list()

        with futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(mixed_call, range(8)))
        for i, r in enumerate(results):
            if i % 2 == 0:
                assert r.count == 42
            else:
                assert len(r) == 2

    def test_client_used_after_close(self, grpc_server):
        """Call method after client.close() raises appropriate error."""
        _, port, _ = grpc_server
        c = DnaerysClient(f"localhost:{port}", tls=False)
        c.close()
        with pytest.raises(Exception):
            c.health()
