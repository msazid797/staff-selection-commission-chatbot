import os
import pickle
import time

import faiss
import numpy as np
import pandas as pd

from embedding_service import embed_documents


# -------------------------------------------------
# CONFIGURATION
# -------------------------------------------------

EXCEL_FILE = "data/ssc_faqs.xlsx"

FAISS_INDEX_DIRECTORY = "faiss_index"

BATCH_SIZE = 20

DELAY_BETWEEN_BATCHES = 2


# -------------------------------------------------
# READ EXCEL FILE
# -------------------------------------------------

print("\nReading SSC FAQ Excel file...")


all_sheets = pd.read_excel(
    EXCEL_FILE,
    sheet_name=None,
    header=None
)


print(
    f"Total examination sheets found: "
    f"{len(all_sheets)}"
)


# -------------------------------------------------
# CREATE FAQ DOCUMENTS
# -------------------------------------------------

documents = []


for sheet_name, df in all_sheets.items():

    current_question = None


    for _, row in df.iterrows():

        values = [
            str(value).strip()
            for value in row
            if pd.notna(value)
        ]


        if not values:
            continue


        # -----------------------------------------
        # FIND QUESTION
        # -----------------------------------------

        question_label_index = next(
            (
                i
                for i, value in enumerate(values)
                if value.upper().startswith(
                    "QUESTION-"
                )
            ),
            None
        )


        if question_label_index is not None:

            question_parts = values[
                question_label_index + 1:
            ]


            if question_parts:

                current_question = " ".join(
                    question_parts
                )


            continue


        # -----------------------------------------
        # FIND ANSWER
        # -----------------------------------------

        answer_label_index = next(
            (
                i
                for i, value in enumerate(values)
                if value.upper().startswith(
                    "ANSWER-"
                )
            ),
            None
        )


        if (
            answer_label_index is not None
            and current_question
        ):

            answer_parts = values[
                answer_label_index + 1:
            ]


            if answer_parts:

                answer = " ".join(
                    answer_parts
                )


                content = (
                    f"Exam: {sheet_name.strip()}\n\n"
                    f"Question: {current_question}\n\n"
                    f"Answer: {answer}"
                )


                documents.append(
                    {
                        "content": content,
                        "exam": sheet_name.strip(),
                        "question": current_question
                    }
                )


                current_question = None


# -------------------------------------------------
# DOCUMENT COUNT
# -------------------------------------------------

total_documents = len(documents)


print(
    f"Total FAQ documents created: "
    f"{total_documents}"
)


if total_documents == 0:

    raise ValueError(
        "No FAQ documents were found."
    )


# -------------------------------------------------
# CREATE EMBEDDINGS IN BATCHES
# -------------------------------------------------

print(
    "\nStarting Gemini embedding generation..."
)

print(
    f"Batch size: {BATCH_SIZE}"
)


all_vectors = []


for start_index in range(
    0,
    total_documents,
    BATCH_SIZE
):

    end_index = min(
        start_index + BATCH_SIZE,
        total_documents
    )


    batch_documents = documents[
        start_index:end_index
    ]


    batch_texts = [
        document["content"]
        for document in batch_documents
    ]


    batch_number = (
        start_index // BATCH_SIZE
    ) + 1


    total_batches = (
        total_documents
        + BATCH_SIZE
        - 1
    ) // BATCH_SIZE


    print(
        f"\nBatch "
        f"{batch_number}/{total_batches}"
    )


    print(
        f"Processing FAQs "
        f"{start_index + 1}-{end_index}"
        f" of {total_documents}"
    )


    batch_vectors = embed_documents(
        batch_texts
    )


    # -----------------------------------------
    # VALIDATE RESPONSE
    # -----------------------------------------

    if len(batch_vectors) != len(
        batch_documents
    ):

        raise ValueError(
            "Embedding count does not match "
            "document count."
        )


    all_vectors.extend(
        batch_vectors
    )


    print(
        f"Batch {batch_number} completed."
    )


    # Don't sleep after final batch.

    if end_index < total_documents:

        print(
            f"Waiting "
            f"{DELAY_BETWEEN_BATCHES} "
            f"seconds..."
        )

        time.sleep(
            DELAY_BETWEEN_BATCHES
        )


# -------------------------------------------------
# CONVERT TO NUMPY
# -------------------------------------------------

vectors = np.array(
    all_vectors,
    dtype="float32"
)


print(
    "\nEmbedding matrix shape:",
    vectors.shape
)


# -------------------------------------------------
# VALIDATE DIMENSIONS
# -------------------------------------------------

if len(vectors) != total_documents:

    raise ValueError(
        "Final embedding count does not "
        "match document count."
    )


# -------------------------------------------------
# NORMALIZE EMBEDDINGS
# -------------------------------------------------

faiss.normalize_L2(
    vectors
)


# -------------------------------------------------
# CREATE FAISS INDEX
# -------------------------------------------------

dimension = vectors.shape[1]


print(
    f"Embedding dimensions: "
    f"{dimension}"
)


index = faiss.IndexFlatIP(
    dimension
)


index.add(
    vectors
)


print(
    f"FAISS index contains "
    f"{index.ntotal} vectors."
)


# -------------------------------------------------
# CREATE DIRECTORY
# -------------------------------------------------

os.makedirs(
    FAISS_INDEX_DIRECTORY,
    exist_ok=True
)


# -------------------------------------------------
# SAVE FAISS INDEX
# -------------------------------------------------

faiss.write_index(
    index,
    os.path.join(
        FAISS_INDEX_DIRECTORY,
        "index.faiss"
    )
)


# -------------------------------------------------
# SAVE DOCUMENT METADATA
# -------------------------------------------------

with open(
    os.path.join(
        FAISS_INDEX_DIRECTORY,
        "documents.pkl"
    ),
    "wb"
) as file:

    pickle.dump(
        documents,
        file
    )


# -------------------------------------------------
# COMPLETE
# -------------------------------------------------

print(
    "\n--------------------------------"
)

print(
    "FAISS vector database "
    "created successfully."
)

print(
    "--------------------------------"
)

print(
    f"Documents: {total_documents}"
)

print(
    f"Vectors: {index.ntotal}"
)

print(
    f"Dimensions: {dimension}"
)

print(
    "Files:"
)

print(
    "faiss_index/index.faiss"
)

print(
    "faiss_index/documents.pkl"
)