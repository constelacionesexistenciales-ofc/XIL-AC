import pytest

from core.research_eval import ResearchCase, aggregate_metrics, evaluate_case


def test_evaluator_scores_relevant_forbidden_and_invalid_urls():
    case = ResearchCase(
        case_id="science-001",
        relevant_domains=frozenset({"example.org", "university.edu"}),
        forbidden_domains=frozenset({"misinfo.example"}),
    )
    metrics = evaluate_case(
        case,
        [
            {"url": "https://example.org/paper"},
            {"url": "https://misinfo.example/post"},
            {"url": "http://university.edu/paper"},
            {"url": "https://other.example/page"},
        ],
        k=4,
    )
    assert metrics.retrieved == 4
    assert metrics.relevant == 1
    assert metrics.precision_at_k == pytest.approx(0.25)
    assert metrics.recall_at_k == pytest.approx(0.5)
    assert metrics.forbidden_results == 1
    assert metrics.invalid_urls == 1


def test_evaluator_rejects_non_positive_k():
    with pytest.raises(ValueError):
        evaluate_case(ResearchCase("x", frozenset()), [], k=0)


def test_aggregate_metrics_is_empty_safe():
    assert aggregate_metrics([])["cases"] == 0


def test_aggregate_metrics_uses_macro_average():
    cases = [
        ResearchCase("a", frozenset({"a.example"})),
        ResearchCase("b", frozenset({"b.example"})),
    ]
    metrics = [
        evaluate_case(cases[0], [{"url": "https://a.example/x"}]),
        evaluate_case(cases[1], [{"url": "https://other.example/x"}]),
    ]
    aggregate = aggregate_metrics(metrics)
    assert aggregate["cases"] == 2
    assert aggregate["mean_precision_at_k"] == pytest.approx(0.5)
