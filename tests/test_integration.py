from app.rag.retriever import retrieve_relevant_knowledge
from app.ai.schemas import EmailAnalysis


def test_email_analysis_and_rag_flow():
    # Simulate the structured result that the AI analyzer produces.
    analysis = EmailAnalysis(
        category="Customer Support",
        priority="HIGH",
        intent="Customer wants a refund",
        summary="Customer is requesting a refund for a purchase.",
        requires_reply=True,
    )

    assert analysis.category == "Customer Support"
    assert analysis.priority == "HIGH"
    assert analysis.requires_reply is True

    # Verify that the RAG layer can find relevant knowledge.
    results = retrieve_relevant_knowledge(
        analysis.intent,
        top_k=3,
    )

    assert len(results) > 0
    assert results[0]["id"] == "refund_policy"