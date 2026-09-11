import json
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


KNOWLEDGE_BASE_PATH = Path(__file__).parent / "knowledge_base.json"

DEFAULT_SCORE_THRESHOLD = 0.20


def load_knowledge_base():
    with open(KNOWLEDGE_BASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def retrieve_relevant_knowledge(
    query: str,
    top_k: int = 3,
    score_threshold: float = DEFAULT_SCORE_THRESHOLD,
):
    knowledge_base = load_knowledge_base()

    if not knowledge_base:
        return []

    documents = [
        f"{item['title']}\n{item['content']}"
        for item in knowledge_base
    ]

    vectorizer = TfidfVectorizer(
        lowercase=True,
        stop_words="english",
    )

    document_vectors = vectorizer.fit_transform(documents)
    query_vector = vectorizer.transform([query])

    similarities = cosine_similarity(
        query_vector,
        document_vectors,
    )[0]

    ranked_indexes = similarities.argsort()[::-1]

    results = []

    for index in ranked_indexes[:top_k]:
        score = float(similarities[index])

        # Ignore weak/irrelevant matches.
        if score < score_threshold:
            continue

        results.append(
            {
                "id": knowledge_base[index]["id"],
                "title": knowledge_base[index]["title"],
                "content": knowledge_base[index]["content"],
                "score": score,
            }
        )

    return results