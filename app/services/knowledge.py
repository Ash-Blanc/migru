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
        db.redis.hset(key, mapping=attributes)
    
    def add_edge(self, subject_id: str, relation: str, object_id: str):
        """Adds a directed edge between two nodes."""
        key = f"edge:{subject_id}:{relation}"
        db.redis.sadd(key, object_id)
        
    def get_related(self, subject_id: str, relation: str) -> List[str]:
        """Gets all entities related to a subject by a relation."""
        key = f"edge:{subject_id}:{relation}"
        return [x.decode('utf-8') for x in db.redis.smembers(key)]

    def get_node(self, node_id: str, label: str) -> Dict:
        """Retrieves node attributes."""
        key = f"node:{label}:{node_id}"
        raw = db.redis.hgetall(key)
        return {k.decode('utf-8'): v.decode('utf-8') for k, v in raw.items()}

knowledge_service = KnowledgeGraphService()
