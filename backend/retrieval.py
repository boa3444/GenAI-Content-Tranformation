import os
import re
import gc
import numpy as np
import logging
from typing import List, Dict, Any, Optional
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

# Import FAISS
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    logger.warning("FAISS vector library not installed. Defaulting to BM25-only retrieval.")

# Import Google GenAI SDK
try:
    from google import genai
    HAS_GENAI_SDK = True
except ImportError:
    HAS_GENAI_SDK = False
    logger.warning("google-genai SDK not found. Defaulting to BM25-only retrieval.")

# Explicit global in-memory retrieval database state references
global_vector_db = None
global_chunks = []

def reset_global_retrieval_state():
    """
    Explicitly resets and clears all in-memory vector database and document chunks state,
    forcing immediate Python garbage collection to guarantee zero context persistence across uploads.
    """
    global global_vector_db, global_chunks
    global_vector_db = None
    global_chunks = []
    gc.collect()
    logger.info("Global retrieval database and chunks state explicitly reset; garbage collection executed.")

class HybridRetriever:
    """
    BM25 + FAISS Hybrid Retrieval Engine using Google Gemini Embedding API (text-embedding-004).
    Instantiated per-request for strict context isolation without state persistence.
    """
    def __init__(self, chunk_size: int = 2000, chunk_overlap: int = 400):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Strict context isolation: clear all instance data per request
        self.chunks: List[str] = []
        self.bm25: Optional[BM25Okapi] = None
        self.faiss_index = None

        self.api_key = os.environ.get("GEMINI_API_KEY")
        self.client = None
        if HAS_GENAI_SDK and self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to initialize GenAI client for embeddings: {e}")

    def _chunk_text(self, text: str) -> List[str]:
        """Splits text into character chunks with overlap."""
        if not text or len(text) <= self.chunk_size:
            return [text] if text else []

        sentences = re.split(r'(?<=[.?!])\s+', text)
        chunks = []
        current_chunk_sentences = []
        current_char_len = 0

        for sentence in sentences:
            sentence_len = len(sentence)
            if current_char_len + sentence_len > self.chunk_size and current_chunk_sentences:
                chunk_str = " ".join(current_chunk_sentences)
                chunks.append(chunk_str)

                overlap_sentences = []
                overlap_char_len = 0
                for s in reversed(current_chunk_sentences):
                    if overlap_char_len + len(s) <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_char_len += len(s)
                    else:
                        break

                current_chunk_sentences = overlap_sentences
                current_char_len = overlap_char_len

            current_chunk_sentences.append(sentence)
            current_char_len += sentence_len

        if current_chunk_sentences:
            chunks.append(" ".join(current_chunk_sentences))

        return [c.strip() for c in chunks if c.strip()]

    def _embed_texts(self, texts: List[str]) -> Optional[np.ndarray]:
        """Fetches vector embeddings from Gemini text-embedding-004 API."""
        if not self.client or not texts:
            return None

        try:
            res = self.client.models.embed_content(
                model="text-embedding-004",
                contents=texts
            )

            if hasattr(res, "embeddings") and res.embeddings:
                vecs = [e.values for e in res.embeddings]
                return np.array(vecs, dtype=np.float32)
            elif hasattr(res, "embedding") and hasattr(res.embedding, "values"):
                return np.array([res.embedding.values], dtype=np.float32)
        except Exception as e:
            logger.error(f"Gemini text-embedding-004 API error: {e}")

        return None

    def index_document(self, text: str):
        """Strictly resets global state and indexes raw text for a single user document."""
        global global_vector_db, global_chunks
        reset_global_retrieval_state()

        self.chunks = self._chunk_text(text)
        if not self.chunks:
            self.chunks = [text]

        global_chunks = self.chunks

        # 1. BM25 Index
        tokenized_corpus = [doc.lower().split() for doc in self.chunks]
        self.bm25 = BM25Okapi(tokenized_corpus)

        # 2. FAISS Index with Gemini Embeddings
        if HAS_FAISS and self.client:
            try:
                embeddings = self._embed_texts(self.chunks)
                if embeddings is not None and len(embeddings) > 0:
                    faiss.normalize_L2(embeddings)
                    dimension = embeddings.shape[1]
                    self.faiss_index = faiss.IndexFlatIP(dimension)
                    self.faiss_index.add(embeddings)
                    global_vector_db = self.faiss_index
            except Exception as e:
                logger.error(f"FAISS indexing error: {e}")
                self.faiss_index = None

    def retrieve(self, query: str, top_k: int = 5) -> str:
        """Executes BM25 + FAISS rank fusion retrieval on the isolated document index."""
        if not self.chunks:
            return ""

        num_chunks = len(self.chunks)
        effective_k = min(top_k, num_chunks)

        # 1. BM25 Scores
        bm25_scores = np.zeros(num_chunks)
        if self.bm25:
            tokenized_query = query.lower().split()
            bm25_scores = np.array(self.bm25.get_scores(tokenized_query))
            if bm25_scores.max() > 0:
                bm25_scores = bm25_scores / bm25_scores.max()

        # 2. FAISS Vector Scores using Gemini Query Embedding
        vector_scores = np.zeros(num_chunks)
        if HAS_FAISS and self.faiss_index and self.client:
            try:
                query_vec = self._embed_texts([query])
                if query_vec is not None and len(query_vec) > 0:
                    faiss.normalize_L2(query_vec)
                    scores, indices = self.faiss_index.search(query_vec, num_chunks)
                    for rank, idx in enumerate(indices[0]):
                        if idx >= 0 and idx < num_chunks:
                            vector_scores[idx] = max(0, scores[0][rank])
            except Exception as e:
                logger.error(f"FAISS vector search error: {e}")

        # 3. Hybrid Score Fusion
        hybrid_scores = (0.5 * bm25_scores) + (0.5 * vector_scores)
        top_indices = np.argsort(hybrid_scores)[::-1][:effective_k]

        # Preserve original document order for top retrieved chunks
        sorted_top_indices = sorted(top_indices)

        # Deduplicate retrieved chunks while preserving order
        seen = set()
        unique_chunks = []
        for idx in sorted_top_indices:
            chunk = self.chunks[idx]
            if chunk not in seen:
                seen.add(chunk)
                unique_chunks.append(chunk)

        return "\n\n---\n\n".join(unique_chunks)

def get_hybrid_context(source_text: str, objective_query: str, top_k: int = 5, page_count: Optional[int] = None) -> str:
    """
    Utility wrapper to retrieve relevant context.
    If the document is under 40,000 characters or <= 10 pages, BM25/FAISS retrieval is bypassed
    and the ENTIRE raw text is passed directly to the Gemini prompt context.
    """
    reset_global_retrieval_state()
    is_under_bypass_limit = (page_count is not None and page_count <= 10) or (len(source_text) <= 40000)
    
    if is_under_bypass_limit:
        logger.info(f"Document under bypass limit (len: {len(source_text)} chars <= 40000, pages: {page_count}). Bypassing BM25/FAISS retrieval.")
        return source_text

    logger.info(f"Document over 40,000 chars (len: {len(source_text)} chars). Performing isolated BM25 + Gemini FAISS retrieval.")
    retriever = HybridRetriever(chunk_size=2000, chunk_overlap=400)
    retriever.index_document(source_text)
    return retriever.retrieve(objective_query, top_k=top_k)
