from typing import List

class JsonMerger:
    @staticmethod
    def merge_results(extractions: List[dict]) -> dict:
        """Merge multiple extraction results into single JSON"""
        result = {}
        for extraction in extractions:
            path = extraction["field"].split('.')
            current = result
            for part in path[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[path[-1]] = extraction["value"]
        return result