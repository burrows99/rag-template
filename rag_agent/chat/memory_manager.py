# src/chat/memory_manager.py
from typing import Dict, Any, List
from datetime import datetime
import json

class MemoryManager:
    def __init__(self, config: Dict[str, Any]):
        self.opensearch_client = self._init_opensearch(config)
        self.memory_index = config['memory_index_name']
        self.ttl_short_term = config.get('ttl_short_term', 3600)  # 1 hour
        self.ttl_long_term = config.get('ttl_long_term', 2592000)  # 30 days
    
    async def get_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Retrieve relevant memory context"""
        # Get short-term memory (current session)
        short_term = await self._get_short_term_memory(session_id)
        
        # Get long-term memory (user history)
        long_term = await self._get_long_term_memory(user_id)
        
        return {
            'short_term': short_term,
            'long_term': long_term,
            'user_preferences': long_term.get('preferences', {}),
            'recent_topics': self._extract_topics(short_term)
        }
    
    async def update_memory(self, user_id: str, session_id: str, 
                           query: str, response: str) -> None:
        """Update both short and long-term memory"""
        timestamp = datetime.utcnow().isoformat()
        
        # Update short-term memory
        short_term_doc = {
            'session_id': session_id,
            'user_id': user_id,
            'timestamp': timestamp,
            'query': query,
            'response': response,
            'type': 'short_term',
            'ttl': self.ttl_short_term
        }
        
        await self._index_memory(short_term_doc)
        
        # Update long-term memory with summary
        if self._should_update_long_term(session_id):
            summary = await self._generate_session_summary(session_id)
            long_term_doc = {
                'user_id': user_id,
                'timestamp': timestamp,
                'summary': summary,
                'topics': self._extract_topics_from_summary(summary),
                'type': 'long_term',
                'ttl': self.ttl_long_term
            }
            await self._index_memory(long_term_doc)
    
    async def _get_short_term_memory(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieve short-term memory for current session"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"session_id": session_id}},
                        {"term": {"type": "short_term"}}
                    ]
                }
            },
            "sort": [{"timestamp": "desc"}],
            "size": 10
        }
        
        response = self.opensearch_client.search(
            index=self.memory_index,
            body=query
        )
        
        return [hit['_source'] for hit in response['hits']['hits']]
    
    async def _get_long_term_memory(self, user_id: str) -> Dict[str, Any]:
        """Retrieve long-term memory for user"""
        query = {
            "query": {
                "bool": {
                    "must": [
                        {"term": {"user_id": user_id}},
                        {"term": {"type": "long_term"}}
                    ]
                }
            },
            "sort": [{"timestamp": "desc"}],
            "size": 5
        }
        
        response = self.opensearch_client.search(
            index=self.memory_index,
            body=query
        )
        
        memories = [hit['_source'] for hit in response['hits']['hits']]
        
        # Aggregate user preferences and topics
        return self._aggregate_long_term_memories(memories)