import json
from typing import Dict, List

class SchemaDecomposer:
    def __init__(self, schema: Dict):
        self.schema = schema
        self.field_metadata = []
        
    def decompose(self) -> List[Dict]:
        """Break down schema into field metadata"""
        self._traverse_schema(self.schema)
        return self.field_metadata
    
    def _traverse_schema(self, node: Dict, path: str = ""):
        """Recursively traverse schema to extract field info"""
        if "properties" in node:
            for field, props in node["properties"].items():
                new_path = f"{path}.{field}" if path else field
                self.field_metadata.append({
                    "path": new_path,
                    "type": props.get("type", "unknown"),
                    "description": props.get("description", "")
                })
                self._traverse_schema(props, new_path)