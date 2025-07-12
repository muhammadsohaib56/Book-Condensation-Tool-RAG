import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import logging

logger = logging.getLogger(__name__)
embedder = SentenceTransformer("all-MiniLM-L6-v2")

def build_vector_store(sections):
    """Build a vector store from book sections."""
    try:
        # Extract content from sections
        texts = [section["content"][:5000] for section in sections]  # Limit text size
        if not texts:
            raise ValueError("No valid sections for vector store")
        embeddings = embedder.encode(texts, show_progress_bar=True)
        index = faiss.IndexFlatL2(embeddings.shape[1])
        index.add(np.array(embeddings))
        logger.info(f"Built vector store with {len(texts)} sections")
        return index, embeddings, sections
    except Exception as e:
        logger.error(f"Error building vector store: {e}")
        raise

def retrieve_relevant_chunks(index, embeddings, sections, query_section, top_k=2):
    """Retrieve relevant sections for context."""
    try:
        query_text = query_section["content"][:5000]  # Limit query size
        query_vec = embedder.encode([query_text])
        D, I = index.search(np.array(query_vec), top_k + 1)  # +1 to skip self
        relevant_sections = [sections[i]["content"][:2000] for i in I[0] if sections[i]["content"] != query_text][:top_k]
        logger.debug(f"Retrieved {len(relevant_sections)} relevant sections")
        return relevant_sections
    except Exception as e:
        logger.error(f"Error retrieving relevant chunks: {e}")
        return []