class FieldExtractor:
    def __init__(self, schema: dict):
        self.schema = schema
        
    def extract_field(self, field_name: str, text: str) -> dict:
        """Extract a single field from text"""
        # TODO:
        # 1. add LLM
        return {
            "field": field_name,
            "value": text[:50],  # dummy extraction
            "confidence": 0.9
        }