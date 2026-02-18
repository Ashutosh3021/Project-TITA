"""ChromaDB vector memory storage for JARVIS."""

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    HuggingFaceEmbeddings = None

from ..core.config import CHROMA_PATH
from ..core.logger import get_logger

logger = get_logger(__name__)


class ChromaMemory:
    """ChromaDB-based vector memory for conversations and facts."""
    
    def __init__(self, persist_directory: Path = CHROMA_PATH) -> None:
        """Initialize ChromaDB with persistent storage.
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        # Check if dependencies are available
        if not LANGCHAIN_AVAILABLE or HuggingFaceEmbeddings is None:
            raise RuntimeError(
                "langchain_community not installed. "
                "Install with: pip install langchain-community sentence-transformers"
            )
        
        # Initialize embeddings
        try:
            self.embeddings = HuggingFaceEmbeddings(
                model_name="sentence-transformers/all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'}
            )
            logger.info("Embeddings model loaded")
        except Exception as e:
            logger.error(f"Failed to load embeddings: {e}")
            raise RuntimeError(f"Failed to initialize embeddings: {e}") from e
        
        # Initialize ChromaDB client
        try:
            import chromadb
            self.client = chromadb.PersistentClient(path=str(self.persist_directory))
            logger.info(f"ChromaDB initialized at {self.persist_directory}")
        except ImportError:
            raise RuntimeError(
                "chromadb not installed. Install with: pip install chromadb"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {e}")
            raise RuntimeError(f"Failed to initialize ChromaDB: {e}") from e
        
        # Create or get collections
        self.conversations_collection = self._get_or_create_collection("conversations")
        self.facts_collection = self._get_or_create_collection("facts")
        
        logger.info("ChromaMemory initialized with conversations and facts collections")
    
    def _get_or_create_collection(self, name: str) -> Any:
        """Get existing collection or create new one.
        
        Args:
            name: Collection name
            
        Returns:
            ChromaDB collection
        """
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=name)
            logger.debug(f"Retrieved existing collection: {name}")
            return collection
        except Exception:
            # Create new collection if it doesn't exist
            try:
                collection = self.client.create_collection(
                    name=name,
                    metadata={"hnsw:space": "cosine"}
                )
                logger.info(f"Created new collection: {name}")
                return collection
            except Exception as e:
                logger.error(f"Failed to create collection {name}: {e}")
                raise RuntimeError(f"Failed to create collection {name}: {e}") from e
    
    def add_conversation(
        self,
        user_input: str,
        assistant_response: str,
        metadata: dict[str, Any] | None = None
    ) -> str:
        """Add a conversation exchange to ChromaDB.
        
        Args:
            user_input: User's input text
            assistant_response: Assistant's response text
            metadata: Optional metadata dict
            
        Returns:
            Document ID
        """
        try:
            # Combine for embedding
            combined_text = f"User: {user_input}\nAssistant: {assistant_response}"
            
            # Generate unique ID
            doc_id = hashlib.md5(
                f"{user_input}{assistant_response}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Build metadata
            doc_metadata = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "assistant_response": assistant_response
            }
            if metadata:
                doc_metadata.update(metadata)
            
            # Generate embedding
            embedding = self.embeddings.embed_query(combined_text)
            
            # Add to collection
            self.conversations_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[combined_text],
                metadatas=[doc_metadata]
            )
            
            logger.debug(f"Added conversation with ID: {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add conversation: {e}")
            raise RuntimeError(f"Failed to add conversation: {e}") from e
    
    def add_fact(self, fact: str, category: str = "general") -> str:
        """Add an important fact to ChromaDB.
        
        Args:
            fact: The fact text
            category: Category of the fact
            
        Returns:
            Document ID
        """
        try:
            # Generate unique ID
            doc_id = hashlib.md5(
                f"{fact}{category}{datetime.now().isoformat()}".encode()
            ).hexdigest()
            
            # Build metadata
            metadata = {
                "category": category,
                "timestamp": datetime.now().isoformat(),
                "type": "fact"
            }
            
            # Generate embedding
            embedding = self.embeddings.embed_query(fact)
            
            # Add to collection
            self.facts_collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[fact],
                metadatas=[metadata]
            )
            
            logger.debug(f"Added fact with ID: {doc_id} (category: {category})")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add fact: {e}")
            raise RuntimeError(f"Failed to add fact: {e}") from e
    
    def retrieve_relevant(self, query: str, n_results: int = 5) -> list[str]:
        """Retrieve relevant memories based on query.
        
        Searches both conversations and facts collections.
        
        Args:
            query: Search query
            n_results: Number of results per collection
            
        Returns:
            List of relevant text chunks
        """
        try:
            # Generate query embedding
            query_embedding = self.embeddings.embed_query(query)
            
            results = []
            
            # Search conversations
            try:
                conv_results = self.conversations_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, 5)
                )
                if conv_results['documents'] and conv_results['documents'][0]:
                    results.extend(conv_results['documents'][0])
                    logger.debug(f"Retrieved {len(conv_results['documents'][0])} conversations")
            except Exception as e:
                logger.warning(f"Failed to query conversations: {e}")
            
            # Search facts
            try:
                fact_results = self.facts_collection.query(
                    query_embeddings=[query_embedding],
                    n_results=min(n_results, 5)
                )
                if fact_results['documents'] and fact_results['documents'][0]:
                    results.extend(fact_results['documents'][0])
                    logger.debug(f"Retrieved {len(fact_results['documents'][0])} facts")
            except Exception as e:
                logger.warning(f"Failed to query facts: {e}")
            
            logger.info(f"Retrieved {len(results)} total relevant memories")
            return results
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant memories: {e}")
            return []
    
    def clear_old_conversations(self, days: int = 30) -> int:
        """Remove conversations older than specified days.
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of deleted items
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            # Get all conversations
            all_convos = self.conversations_collection.get()
            
            if not all_convos['ids']:
                logger.info("No conversations to clean up")
                return 0
            
            # Find old conversations
            ids_to_delete = []
            for i, metadata in enumerate(all_convos['metadatas']):
                if metadata and 'timestamp' in metadata:
                    try:
                        convo_date = datetime.fromisoformat(metadata['timestamp'])
                        if convo_date < cutoff_date:
                            ids_to_delete.append(all_convos['ids'][i])
                    except (ValueError, TypeError):
                        # If timestamp is invalid, delete it
                        ids_to_delete.append(all_convos['ids'][i])
            
            # Delete old conversations
            if ids_to_delete:
                self.conversations_collection.delete(ids=ids_to_delete)
                logger.info(f"Cleared {len(ids_to_delete)} old conversations (older than {days} days)")
                return len(ids_to_delete)
            else:
                logger.info("No old conversations to clear")
                return 0
                
        except Exception as e:
            logger.error(f"Failed to clear old conversations: {e}")
            return 0
    
    def get_stats(self) -> dict[str, int]:
        """Get memory statistics.
        
        Returns:
            Dictionary with collection counts
        """
        try:
            convo_count = self.conversations_collection.count()
            facts_count = self.facts_collection.count()
            
            return {
                "conversations": convo_count,
                "facts": facts_count,
                "total": convo_count + facts_count
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"conversations": 0, "facts": 0, "total": 0}
