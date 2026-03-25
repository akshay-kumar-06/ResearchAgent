"""
Benchmark tests for measuring research performance
"""

import pytest
import time
import asyncio
from app.agents.graph import run_research


@pytest.mark.benchmark
async def test_research_performance_benchmark():
    """Benchmark test to measure research performance"""
    # Test query that should generate multiple sources
    query = "What are the latest developments in renewable energy technology?"

    start_time = time.time()
    result = await run_research(query)
    execution_time = time.time() - start_time

    # Assertions for performance
    assert execution_time < 120  # Should complete within 2 minutes (120 seconds)
    assert isinstance(result, dict) and result.get("status") in [
        "complete",
        "error",
    ]  # Should have a final status

    # Log performance metrics
    sources_count = result.get("total_sources", 0)
    print(f"Benchmark Results:")
    print(f"  Query: {query}")
    print(f"  Execution Time: {execution_time:.2f} seconds")
    print(f"  Sources Found: {sources_count}")
    print(f"  Status: {result.get('status')}")

    # If we got sources, check if we met the 25+ sources target
    if sources_count > 0:
        sources_per_second = sources_count / execution_time if execution_time > 0 else 0
        print(f"  Sources per Second: {sources_per_second:.2f}")

        # For 25+ sources in under 2 minutes, we need >0.2 sources/second
        assert sources_per_second > 0.2, (
            f"Too slow: {sources_per_second:.2f} sources/second"
        )


@pytest.mark.benchmark
async def test_multiple_researches_performance():
    """Test performance of multiple concurrent researches"""
    queries = [
        "Artificial intelligence trends 2024",
        "Climate change solutions",
        "Space exploration latest missions",
        "Quantum computing breakthroughs",
        "Biotechnology advances",
    ]

    start_time = time.time()

    # Run researches concurrently
    tasks = [run_research(query) for query in queries]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    execution_time = time.time() - start_time

    # Process results
    successful = 0
    total_sources = 0

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Query {i} failed: {result}")
        elif isinstance(result, dict) and result.get("status") == "complete":
            successful += 1
            total_sources += result.get("total_sources", 0)
        else:
            print(
                f"Query {i} ended with status: {result.get('status') if isinstance(result, dict) else 'unknown'}"
            )

    print(f"Multiple Researches Benchmark:")
    print(f"  Total Queries: {len(queries)}")
    print(f"  Successful: {successful}")
    print(f"  Total Execution Time: {execution_time:.2f} seconds")
    print(f"  Average Time per Research: {execution_time / len(queries):.2f} seconds")
    print(f"  Total Sources Found: {total_sources}")
    print(f"  Average Sources per Research: {total_sources / max(successful, 1):.2f}")

    # Performance assertions
    assert execution_time < 300  # All 5 researches should complete within 5 minutes
    assert successful >= 3  # At least 60% success rate
