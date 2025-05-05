import jsonschema

class JsonValidator:
    def __init__(self, schema: dict):
        self.schema = schema
        
    def validate(self, data: dict) -> bool:
        """Validate against the schema"""
        try:
            jsonschema.validate(data, self.schema)
            return True
        except jsonschema.ValidationError:
            return False