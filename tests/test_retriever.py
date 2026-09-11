from app.rag.retriever import (
    DEFAULT_SCORE_THRESHOLD,
    load_knowledge_base,
    retrieve_relevant_knowledge,
)


def test_knowledge_base_loads():
    knowledge_base = load_knowledge_base()

    assert isinstance(knowledge_base, list)
    assert len(knowledge_base) > 0


def test_refund_query_returns_refund_policy():
    results = retrieve_relevant_knowledge(
        "I want a refund for my purchase",
        top_k=3,
    )

    assert len(results) > 0
    assert results[0]["id"] == "refund_policy"
    assert results[0]["title"] == "Refund Policy"


def test_results_are_sorted_by_score():
    results = retrieve_relevant_knowledge(
        "refund purchase",
        top_k=3,
    )

    scores = [result["score"] for result in results]

    assert scores == sorted(scores, reverse=True)


def test_top_k_limits_results():
    results = retrieve_relevant_knowledge(
        "customer support refund invoice shipping",
        top_k=2,
    )

    assert len(results) <= 2


def test_score_threshold_filters_weak_matches():
    results = retrieve_relevant_knowledge(
        "completely unrelated xyz abc",
        top_k=3,
        score_threshold=DEFAULT_SCORE_THRESHOLD,
    )

    assert all(
        result["score"] >= DEFAULT_SCORE_THRESHOLD
        for result in results
    )


def test_result_contains_expected_fields():
    results = retrieve_relevant_knowledge(
        "How can I request a refund?",
        top_k=1,
    )

    assert len(results) > 0

    result = results[0]

    assert "id" in result
    assert "title" in result
    assert "content" in result
    assert "score" in result