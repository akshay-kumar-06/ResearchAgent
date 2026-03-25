"""
Evaluation framework for measuring research accuracy
"""

import structlog
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.core.metrics import metrics_collector

logger = structlog.get_logger()


@dataclass
class EvaluationResult:
    """Result of an evaluation"""

    query: str
    expected_keywords: List[str]
    actual_report: str
    accuracy_score: float
    missing_keywords: List[str]
    found_keywords: List[str]


class AccuracyEvaluator:
    """Evaluates research accuracy based on keyword matching"""

    def __init__(self):
        # Predefined evaluation datasets for common topics
        self.evaluation_datasets = {
            "AI regulations": {
                "expected_keywords": ["EU", "US", "regulation", "AI Act", "framework"],
                "weight": 1.0,
            },
            "climate change": {
                "expected_keywords": [
                    "temperature",
                    "emissions",
                    "carbon",
                    "warming",
                    "mitigation",
                ],
                "weight": 1.0,
            },
            "renewable energy": {
                "expected_keywords": [
                    "solar",
                    "wind",
                    "hydroelectric",
                    "geothermal",
                    "biomass",
                ],
                "weight": 1.0,
            },
        }

    def evaluate_research(self, query: str, report: str) -> EvaluationResult:
        """
        Evaluate research accuracy by checking for expected keywords

        Args:
            query: Original research query
            report: Generated research report

        Returns:
            EvaluationResult with accuracy score and details
        """
        # Normalize inputs for comparison
        query_lower = query.lower()
        report_lower = report.lower()

        # Find matching evaluation dataset
        dataset_key = None
        for key in self.evaluation_datasets.keys():
            if key.lower() in query_lower:
                dataset_key = key
                break

        # If no specific dataset found, use generic evaluation
        if dataset_key is None:
            # Extract key nouns from query as expected keywords
            expected_keywords = self._extract_keywords_from_query(query)
            weight = 0.5  # Lower weight for generic evaluation
        else:
            expected_keywords = self.evaluation_datasets[dataset_key][
                "expected_keywords"
            ]
            weight = self.evaluation_datasets[dataset_key]["weight"]

        # Check for keyword presence
        found_keywords = []
        missing_keywords = []

        for keyword in expected_keywords:
            if keyword.lower() in report_lower:
                found_keywords.append(keyword)
            else:
                missing_keywords.append(keyword)

        # Calculate accuracy score (percentage of expected keywords found)
        if len(expected_keywords) > 0:
            accuracy_score = len(found_keywords) / len(expected_keywords)
        else:
            accuracy_score = 0.0

        # Apply weight to score
        weighted_score = accuracy_score * weight

        # Record metrics
        metrics_collector.record_accuracy_score(weighted_score)

        result = EvaluationResult(
            query=query,
            expected_keywords=expected_keywords,
            actual_report=report,
            accuracy_score=weighted_score,
            missing_keywords=missing_keywords,
            found_keywords=found_keywords,
        )

        logger.info(
            "research_evaluated",
            query=query,
            accuracy_score=weighted_score,
            found_keywords=len(found_keywords),
            expected_keywords=len(expected_keywords),
        )

        return result

    def _extract_keywords_from_query(self, query: str) -> List[str]:
        """
        Extract potential keywords from a query for generic evaluation

        Simple implementation - in practice, you'd use NLP techniques
        """
        # Remove common question words and extract meaningful terms
        stop_words = {
            "what",
            "is",
            "are",
            "the",
            "of",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "by",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "this",
            "that",
            "these",
            "those",
            "a",
            "an",
        }

        # Simple word extraction (would be improved with proper NLP)
        words = query.lower().split()
        keywords = [
            word.strip(".,!?;:")
            for word in words
            if word.strip(".,!?;:") not in stop_words and len(word) > 2
        ]

        # Return top keywords (limit to reasonable number)
        return keywords[:5] if keywords else ["topic"]


# Global evaluator instance
accuracy_evaluator = AccuracyEvaluator()


def evaluate_research_accuracy(query: str, report: str) -> EvaluationResult:
    """
    Convenience function to evaluate research accuracy

    Args:
        query: Original research query
        report: Generated research report

    Returns:
        EvaluationResult with accuracy assessment
    """
    return accuracy_evaluator.evaluate_research(query, report)
