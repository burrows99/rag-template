from langchain_core.tools import BaseTool
from langchain.embeddings import HuggingFaceEmbeddings
import logging
import os
from typing import Dict, List, Optional, Any, Union
from dotenv import load_dotenv
from rag_agent.retrieval.types import SearchResult
load_dotenv()
# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
from rag_agent.vector_store import AZURE_VECTOR_STORE

class VectorSearchAgent(BaseTool):
    name: str = "vector_search"
    description: str = (
        "Perform a similarity search over a collection of data stored in the Vector Database from the documents. " \
        "This tool is useful if the data is present in documents."
    )
    def __init__(self,tool_name):
        super().__init__()
        """Initialize summary vector stores - one for summaries """
        self.name = tool_name
    
        
    def _run(self, query: str, limit: int = 5, urls: Optional[List[str]] = None):
        """Search in the vector database"""
        filter_dict = {"url": {"$in": urls}} if urls else None
        docs_with_scores = AZURE_VECTOR_STORE.asimilarity_search_with_score(
            query=query,
            k=limit,
            # filter=filter_dict
        )
        
        results = []
        for doc, score in docs_with_scores:
            results.append(SearchResult(
                content=doc.page_content,
                # url=doc.metadata["url"],
                score=float(score),
                metadata=doc.metadata
            ).model_dump())
        
        return results
    async def _arun(self, query: str, limit: int = 5, urls: Optional[List[str]] = None):
        """Search in the vector database"""
        filter_dict = {"url": {"$in": urls}} if urls else None
        docs_with_scores = await AZURE_VECTOR_STORE.asimilarity_search_with_score(
            query=query,
            k=limit,
            # filter=filter_dict
        )
        
        results = []
        for doc, score in docs_with_scores:
            results.append(SearchResult(
                content=doc.page_content,
                # url=doc.metadata["url"],
                score=float(score),
                metadata=doc.metadata
            ).model_dump())
        
        return results
    