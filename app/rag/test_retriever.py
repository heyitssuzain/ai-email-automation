from app.rag.retriever import retrieve_relevant_knowledge


query = """
I purchased a product 3 days ago and want to know
whether I can get a refund.
"""

results = retrieve_relevant_knowledge(query, top_k=3)

print("=" * 70)
print("RAG RETRIEVER TEST")
print("=" * 70)

for result in results:
    print(f"Title : {result['title']}")
    print(f"Score : {result['score']:.4f}")
    print(f"Content: {result['content']}")
    print("-" * 70)