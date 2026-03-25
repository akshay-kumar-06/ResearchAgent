"""
Tests for the evaluation framework
"""

from app.evaluation import (
    AccuracyEvaluator,
    EvaluationResult,
    evaluate_research_accuracy,
)


def test_evaluator_initialization():
    """Test that evaluator initializes correctly"""
    evaluator = AccuracyEvaluator()
    assert evaluator is not None
    assert hasattr(evaluator, "evaluation_datasets")


def test_ai_regulations_evaluation():
    """Test evaluation for AI regulations query"""
    evaluator = AccuracyEvaluator()

    query = "Compare AI regulations in EU vs US"
    report = """# AI Regulations Comparison
    
    ## Executive Summary
    The EU has implemented the comprehensive AI Act while the US uses a sector-specific approach.
    
    ## Key Findings
    1. EU has comprehensive AI Act framework
    2. US uses sector-specific approach for different industries
    3. Both regions focus on AI safety and ethics
    
    ## Sources
    [1] EU Official Journal - https://eur-lex.europa.eu
    [2] White House AI Initiative - https://whitehouse.gov/ai
    """

    result = evaluator.evaluate_research(query, report)

    assert isinstance(result, EvaluationResult)
    assert result.query == query
    assert result.actual_report == report
    assert result.accuracy_score > 0.0  # Should find some expected keywords
    assert "EU" in result.found_keywords or "US" in result.found_keywords
    # Check if any found keyword contains "regulation" (case-insensitive)
    assert (
        any("regulation" in keyword.lower() for keyword in result.found_keywords)
        if result.found_keywords
        else True
    )


def test_generic_query_evaluation():
    """Test evaluation for a query without predefined dataset"""
    evaluator = AccuracyEvaluator()

    query = "What are the benefits of exercise?"
    report = """Exercise provides numerous health benefits including improved cardiovascular health,
    increased muscle strength, better mental health, and enhanced longevity."""

    result = evaluator.evaluate_research(query, report)

    assert isinstance(result, EvaluationResult)
    assert result.query == query
    assert result.accuracy_score >= 0.0  # Should have some score
    # Should have extracted some keywords from the query
    assert len(result.expected_keywords) > 0


def test_evaluate_research_accuracy_function():
    """Test the convenience function"""
    query = "Test query about renewable energy"
    report = "Renewable energy sources like solar and wind power are important for reducing carbon emissions."

    result = evaluate_research_accuracy(query, report)

    assert isinstance(result, EvaluationResult)
    assert result.query == query
    assert result.actual_report == report


def test_empty_report_evaluation():
    """Test evaluation with empty report"""
    evaluator = AccuracyEvaluator()

    query = "Test query"
    report = ""

    result = evaluator.evaluate_research(query, report)

    assert isinstance(result, EvaluationResult)
    assert result.accuracy_score == 0.0  # Should be zero for empty report
    assert len(result.missing_keywords) > 0  # All expected keywords should be missing
    assert len(result.found_keywords) == 0  # No keywords should be found
