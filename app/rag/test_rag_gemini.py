from app.rag.retriever import retrieve_relevant_knowledge
from app.ai.reply_generator import generate_reply


email_subject = "Refund Request"

email_body = """
Hi,

I purchased the product 3 days ago and I would like
to request a refund.

Please let me know if I am eligible.

Thanks.
"""


query = f"{email_subject}\n{email_body}"

results = retrieve_relevant_knowledge(query, top_k=3)

knowledge_context = "\n\n".join(
    f"Knowledge: {result['title']}\n"
    f"{result['content']}"
    for result in results
)

print("=" * 70)
print("RETRIEVED KNOWLEDGE")
print("=" * 70)
print(knowledge_context)

print("\n" + "=" * 70)
print("GENERATING RAG-BASED REPLY")
print("=" * 70)

reply = generate_reply(
    sender="customer@example.com",
    subject=email_subject,
    body=email_body,
    category="Customer Support",
    priority="MEDIUM",
    intent="Request a refund for a recent purchase.",
    summary="Customer purchased a product 3 days ago and wants to know if they are eligible for a refund.",
    attachment_text="",
    knowledge_context=knowledge_context,
)

print("\n" + "=" * 70)
print("GENERATED REPLY")
print("=" * 70)
print(reply)