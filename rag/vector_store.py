import logging
import numpy as np
import faiss
from typing import List, Tuple
try:
    from langchain.text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from utils.config import CHUNK_SIZE, CHUNK_OVERLAP, SIMILARITY_THRESHOLD

logger = logging.getLogger(__name__)


class VectorStore:
    """Manages vector embeddings and similarity search using FAISS."""
    
    def __init__(self):
        """Initialize vector store with embeddings model."""
        try:
            logger.info("Initializing embeddings model...")
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2"
            )
            self.index = None
            self.documents = []
            logger.info("VectorStore initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStore: {str(e)}")
            raise
    
    def chunk_data(self, texts: List[str]) -> List[str]:
        """
        Split texts into chunks for embedding.
        
        Args:
            texts (List[str]): List of documents/tweets
            
        Returns:
            List[str]: List of text chunks
        """
        try:
            if not texts:
                logger.warning("No texts provided for chunking")
                return []
            
            logger.info(f"Chunking {len(texts)} texts")
            
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
                separators=["\n\n", "\n", " ", ""]
            )
            
            chunks = []
            for text in texts:
                if isinstance(text, dict):
                    # If text is dict (from tweets), extract text field
                    text_content = text.get("text", "")
                else:
                    text_content = str(text)
                
                if text_content.strip():
                    split_texts = splitter.split_text(text_content)
                    chunks.extend(split_texts)
            
            logger.info(f"Created {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to chunk data: {str(e)}")
            raise
    
    def create_index(self, chunks: List[str]) -> None:
        """
        Create FAISS index from text chunks.
        
        Args:
            chunks (List[str]): List of text chunks
            
        Raises:
            ValueError: If chunks list is empty
        """
        try:
            if not chunks:
                logger.warning("No chunks provided to create index")
                raise ValueError("Chunks list cannot be empty")
            
            logger.info(f"Creating FAISS index for {len(chunks)} chunks...")
            
            # Embed all chunks
            embeddings_list = self.embeddings.embed_documents(chunks)
            embeddings_array = np.array(embeddings_list).astype("float32")
            
            # Create FAISS index
            dimension = embeddings_array.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(embeddings_array)
            self.documents = chunks
            
            logger.info(f"FAISS index created with {len(chunks)} documents, dimension {dimension}")
            
        except Exception as e:
            logger.error(f"Failed to create FAISS index: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 5) -> List[Tuple[str, float]]:
        """
        Search for similar documents using FAISS.
        
        Args:
            query (str): Query text
            k (int): Number of results to return
            
        Returns:
            List[Tuple[str, float]]: List of (document, score) tuples
            
        Raises:
            ValueError: If index is not initialized
        """
        try:
            if self.index is None or not self.documents:
                logger.warning("Vector index not initialized")
                raise ValueError("Index must be created before searching")
            
            if not query or not isinstance(query, str):
                logger.error("Invalid query")
                raise ValueError("Query must be a non-empty string")
            
            logger.info(f"Searching for: {query}")
            
            # Embed query
            query_embedding = np.array([self.embeddings.embed_query(query)]).astype("float32")
            
            # Search
            distances, indices = self.index.search(query_embedding, min(k, len(self.documents)))
            
            results = []
            for distance, idx in zip(distances[0], indices[0]):
                if idx < len(self.documents):
                    # Convert L2 distance to similarity score (0-1)
                    similarity = 1 / (1 + distance)
                    
                    if similarity >= SIMILARITY_THRESHOLD:
                        results.append((self.documents[idx], similarity))
            
            logger.info(f"Found {len(results)} similar documents")
            return results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            raise
    
    def get_context(self, query: str, k: int = 5) -> str:
        """
        Get context for RAG from similar documents.
        
        Args:
            query (str): Query text
            k (int): Number of documents to retrieve
            
        Returns:
            str: Concatenated context from similar documents
        """
        try:
            results = self.similarity_search(query, k)
            
            if not results:
                logger.info("No similar documents found")
                return "No relevant context found."
            
            context = "\n---\n".join([doc for doc, score in results])
            logger.info(f"Generated context from {len(results)} documents")
            return context
            
        except Exception as e:
            logger.error(f"Failed to get context: {str(e)}")
            raise


# Singleton instance
_vector_store = None


def get_vector_store() -> VectorStore:
    """Get or create vector store singleton."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store


def chunk_data(texts: List[str]) -> List[str]:
    """Convenience function to chunk data."""
    store = get_vector_store()
    return store.chunk_data(texts)


def create_vector_store(chunks: List[str]) -> VectorStore:
    """
    Create and initialize vector store from chunks.
    
    Args:
        chunks (List[str]): List of text chunks
        
    Returns:
        VectorStore: Initialized vector store
    """
    store = get_vector_store()
    store.create_index(chunks)
    return store


def similarity_search(query: str, k: int = 5) -> List[Tuple[str, float]]:
    """Convenience function for similarity search."""
    store = get_vector_store()
    return store.similarity_search(query, k)


def get_context(query: str, k: int = 5) -> str:
    """Convenience function to get RAG context."""
    store = get_vector_store()
    return store.get_context(query, k)    