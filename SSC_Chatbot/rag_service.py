import pickle

import faiss
import numpy as np

from embedding_service import embed_query
from llm_service import generate_answer


FAISS_INDEX_PATH = "faiss_index/index.faiss"
DOCUMENTS_PATH = "faiss_index/documents.pkl"

TOP_K = 3

# Because we normalize vectors and use IndexFlatIP,
# higher scores mean greater similarity.
#
# Start here and tune using real SSC questions.
RELEVANCE_THRESHOLD = 0.40


# ------------------------------------------
# LOAD FAISS
# ------------------------------------------

vector_db = faiss.read_index(
    FAISS_INDEX_PATH
)


# ------------------------------------------
# LOAD DOCUMENTS
# ------------------------------------------

with open(
    DOCUMENTS_PATH,
    "rb"
) as file:

    documents = pickle.load(file)


print(
    f"FAISS database loaded successfully. "
    f"Total documents: {len(documents)}"
)


# ------------------------------------------
# RETRIEVE CONTEXT
# ------------------------------------------

def retrieve_context(question):

    query_vector = embed_query(
        question
    )

    query_vector = np.array(
        [query_vector],
        dtype="float32"
    )

    faiss.normalize_L2(
        query_vector
    )


    scores, indices = vector_db.search(
        query_vector,
        TOP_K
    )


    best_score = float(
        scores[0][0]
    )


    print(
        f"Best similarity score: "
        f"{best_score}"
    )


    # Higher = more similar because
    # we're using normalized vectors
    # with inner-product search.

    if best_score < RELEVANCE_THRESHOLD:
        return None


    context_parts = []


    for index in indices[0]:

        if index == -1:
            continue

        document = documents[index]

        context_parts.append(
            document["content"]
        )


    if not context_parts:
        return None


    context = "\n\n---\n\n".join(
        context_parts
    )

    return context


# ------------------------------------------
# CHATBOT
# ------------------------------------------

def ask_chatbot(question):

    question = question.strip()


    if not question:

        return (
            "Please enter a question "
            "related to SSC examinations."
        )


    try:

        context = retrieve_context(
            question
        )


        if context is None:

            return (
                "I could not find relevant information "
                "in the available SSC FAQs. "
                "Please ask a question related to "
                "SSC examinations."
            )


        answer = generate_answer(
            question=question,
            context=context
        )


        return answer


    except Exception as error:

        print(
            f"RAG Error: {error}"
        )

        return (
            "The chatbot service is temporarily "
            "unavailable. Please try again later."
        )