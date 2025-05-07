from typing import Dict, List, Union


class SchemaDecomposer:
    def __init__(self, schema: Dict, traversal_limit: int = 1):
        # trunk nodes are including the 'traversal_limit' number
        self.traversal_limit = traversal_limit
        self.schema = schema
        self.field_metadata = []
        
    def print_schema_tree(self, decomposed_path, indent=4):
        for field in decomposed_path:
            f = field['path'].split(".")
            print(" trunk" if len(f) <= self.traversal_limit else "branch" ,(len(f) - 1), "─"*(len(f) - 1)*indent, f[-1])
            
    def decompose(self) -> List[Dict]:
        if "properties" not in self.schema:
            raise ValueError("Schema does not contain 'properties' field.")
        self.traverse_schema(self.schema["properties"])
        
        for i, field_path in enumerate(self.field_metadata):
            self.field_metadata[i]['node_type'] = "trunk" \
            if (len(field_path['path'].split(".")) <= self.traversal_limit) \
            else "branch"
        return self.field_metadata

    def traverse_schema(self, node: Union[Dict, List], path: str = ""):
        if isinstance(node, dict):
            for key, value in node.items():
                current_path = f"{path}.{key}" if path else key
                node_type = value.get("type", "unknown")
                desc = value.get("description", "")

                if node_type == "object" and "properties" in value:
                    self.field_metadata.append({
                        "path": current_path,
                        "type": "object",
                        "description": desc
                    })
                    self.traverse_schema(value["properties"], current_path)

                elif node_type == "array":
                    item_type = value.get("items", {}).get("type", "unknown")
                    self.field_metadata.append({
                        "path": f"{current_path}[]",
                        "type": f"array<{item_type}>",
                        "description": desc
                    })

                    if item_type == "object" and "properties" in value["items"]:
                        self.traverse_schema(value["items"]["properties"], f"{current_path}[]")

                else:
                    self.field_metadata.append({
                        "path": current_path,
                        "type": node_type,
                        "description": desc
                    })
