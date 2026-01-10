from typing import List, Dict
from app.db import db
import json

class KnowledgeGraphService:
    """
    A simplified Knowledge Graph using Redis Sets and Hashes.
    Structure:
    - Nodes: Stored as hashes with attributes.
    - Edges: Stored as sets (Subject:Relation -> Object).
    """
    
    def add_node(self, node_id: str, label: str, attributes: Dict):
        """Adds or updates a node (entity)."""
        key = f"node:{label}:{node_id}"
        db.redis_client.hset(key, mapping=attributes)
    
    def add_edge(self, subject_id: str, relation: str, object_id: str):
        """Adds a directed edge between two nodes."""
        key = f"edge:{subject_id}:{relation}"
        db.redis_client.sadd(key, object_id)
        
    def get_related(self, subject_id: str, relation: str) -> List[str]:
        """Gets all entities related to a subject by a relation."""
        key = f"edge:{subject_id}:{relation}"
        # smembers returns set of bytes if decode_responses is False, 
        # but RedisDb initializes it with decode_responses=True by default for db_url
        members = db.redis_client.smembers(key)
        return [x if isinstance(x, str) else x.decode('utf-8') for x in members]

    def get_node(self, node_id: str, label: str) -> Dict:
        """Retrieves node attributes."""
        key = f"node:{label}:{node_id}"
        raw = db.redis_client.hgetall(key)
        return {k if isinstance(k, str) else k.decode('utf-8'): v if isinstance(v, str) else v.decode('utf-8') for k, v in raw.items()}

knowledge_service = KnowledgeGraphService()