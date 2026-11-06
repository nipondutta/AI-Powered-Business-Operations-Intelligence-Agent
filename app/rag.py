
from pathlib import Path
import json
import re

import numpy as np
import faiss

from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

from app.config import settings


class HybridRAG:

    def __init__(self):
        self.folder = Path(settings.index_dir)
        self.folder.mkdir(parents=True, exist_ok=True)

        self.docs_file = self.folder / "documents.json"
        self.faiss_file = self.folder / "vectors.faiss"

        self.docs = (
            json.loads(self.docs_file.read_text(encoding="utf-8"))
            if self.docs_file.exists()
            else []
        )

        self.model = None

        self.index = (
            faiss.read_index(str(self.faiss_file))
            if self.faiss_file.exists()
            else None
        )

        self.bm25 = None
        self._build_bm25()

        print(f"RAG initialized with {len(self.docs)} documents.")

    # --------------------------------------------------
    # Embedding Model
    # --------------------------------------------------

    def embedder(self):
        if self.model is None:
            self.model = SentenceTransformer(
                settings.embedding_model
            )

        return self.model

    # --------------------------------------------------
    # Text Chunking
    # --------------------------------------------------

    @staticmethod
    def split(text, size=700, overlap=120):

        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            return []

        chunks = []
        start = 0

        while start < len(text):

            end = min(start + size, len(text))

            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(text):
                break

            start = max(end - overlap, start + 1)

        return chunks

    # --------------------------------------------------
    # Tokenization
    # --------------------------------------------------

    @staticmethod
    def tokenize(text):
        return re.findall(r"\w+", text.lower())

    # --------------------------------------------------
    # BM25 Initialization
    # --------------------------------------------------

    def _build_bm25(self):

        if not self.docs:
            self.bm25 = None
            print("BM25 skipped: No documents available.")
            return

        tokens = [
            self.tokenize(doc.get("text", ""))
            for doc in self.docs
        ]

        # Check whether at least one document has valid tokens
        if not any(tokens):
            self.bm25 = None
            print("BM25 skipped: No valid vocabulary found.")
            return

        try:
            self.bm25 = BM25Okapi(tokens)
            print("BM25 initialized successfully.")

        except ZeroDivisionError:
            self.bm25 = None
            print("BM25 skipped: Empty IDF vocabulary.")

    # --------------------------------------------------
    # Add and Index Documents
    # --------------------------------------------------

    def add_text(self, text, source):

        if not isinstance(text, str) or not text.strip():
            return 0

        chunks = self.split(text)

        if not chunks:
            return 0

        new_docs = [
            {
                "source": source,
                "text": chunk
            }
            for chunk in chunks
        ]

        vectors = np.asarray(
            self.embedder().encode(
                [doc["text"] for doc in new_docs],
                normalize_embeddings=True
            ),
            dtype="float32"
        )

        # Check existing FAISS index consistency
        if self.index is not None:
            if self.index.ntotal != len(self.docs):
                raise RuntimeError(
                    "FAISS index and document count do not match. "
                    "Inspect the existing index before adding documents."
                )

        if self.index is None:
            self.index = faiss.IndexFlatIP(
                vectors.shape[1]
            )

        self.index.add(vectors)

        self.docs.extend(new_docs)

        self.docs_file.write_text(
            json.dumps(
                self.docs,
                ensure_ascii=False,
                indent=2
            ),
            encoding="utf-8"
        )

        faiss.write_index(
            self.index,
            str(self.faiss_file)
        )

        self._build_bm25()

        print(f"Successfully indexed {len(new_docs)} chunks.")

        return len(new_docs)

    # --------------------------------------------------
    # Score Normalization
    # --------------------------------------------------

    @staticmethod
    def normalize(scores):

        if not scores:
            return {}

        maximum = max(scores.values())

        if maximum <= 0:
            return {
                key: 0.0
                for key in scores
            }

        return {
            key: value / maximum
            for key, value in scores.items()
        }

    # --------------------------------------------------
    # Hybrid Search
    # --------------------------------------------------

    def search(self, query, top_k=None):

        if not self.docs or not query.strip():
            return []

        k = top_k or settings.rag_top_k

        dense_scores = {}
        lexical_scores = {}

        # Dense Retrieval using FAISS
        if self.index is not None:

            if self.index.ntotal != len(self.docs):
                raise RuntimeError(
                    "FAISS index size does not match document count."
                )

            query_vector = np.asarray(
                self.embedder().encode(
                    [query],
                    normalize_embeddings=True
                ),
                dtype="float32"
            )

            scores, ids = self.index.search(
                query_vector,
                min(k * 3, len(self.docs))
            )

            dense_scores = {
                int(doc_id): float(score)
                for score, doc_id in zip(scores[0], ids[0])
                if doc_id >= 0
            }

        # Keyword Retrieval using BM25
        if self.bm25 is not None:

            query_tokens = self.tokenize(query)

            if query_tokens:
                scores = self.bm25.get_scores(query_tokens)

                lexical_scores = {
                    i: float(score)
                    for i, score in enumerate(scores)
                }

        # Normalize scores
        dense = self.normalize(dense_scores)
        lexical = self.normalize(lexical_scores)

        # Combine retrieval scores
        if dense and lexical:
            combined = {
                i: (
                    0.55 * dense.get(i, 0)
                    + 0.45 * lexical.get(i, 0)
                )
                for i in set(dense) | set(lexical)
            }

        elif dense:
            combined = dense

        elif lexical:
            combined = lexical

        else:
            return []

        ranked = sorted(
            combined,
            key=combined.get,
            reverse=True
        )[:k]

        return [
            {
                "source": self.docs[i]["source"],
                "text": self.docs[i]["text"],
                "score": round(combined[i], 4)
            }
            for i in ranked
        ]


# Global RAG instance
rag = HybridRAG()
