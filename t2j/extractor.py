import copy

from t2j.prem_sdk import PremSDK
from t2j.prompts import Prompts


class FieldExtractor:
    def __init__(self, model: PremSDK, prompt: Prompts):
        self.model = model
        self.prompt = prompt
        
    def remove_content(self, data):
        counter = {"value": 1}
        mapping = {}

        def recurse(obj):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if key == "content":
                        mapping[counter["value"]] = value
                        obj[key] = counter["value"]
                        counter["value"] += 1
                    else:
                        recurse(value)

                if "sub-headings" in obj and isinstance(obj["sub-headings"], list):
                    for item in obj["sub-headings"]:
                        for sub_key, sub_value in item.items():
                            recurse(sub_value)

            elif isinstance(obj, list):
                for item in obj:
                    recurse(item)

        recurse(data)
        return data, mapping
    
    def max_child_depth(self, schema_list, trunk_path):
        def get_depth(path):
            return path.count("[]") + path.count(".")

        trunk_path = trunk_path.rstrip('.')

        max_depth = 0
        for field in schema_list:
            path = field['path']
            if path == trunk_path:
                continue
            if path.startswith(trunk_path + ".") or path.startswith(trunk_path + "[]"):
                relative_path = path[len(trunk_path):].lstrip('.').lstrip('[]')
                depth = get_depth(relative_path)
                max_depth = max(max_depth, depth)

        return max_depth
    
    def get_from_json_path(self, data, path):
        sub_paths = [x for x in path.split (" -> ") if x!= ""]
        self.output = data
        for sp in sub_paths:
            try:
                if not sp.endswith("]"):
                    self.output = self.output[sp]
                else:
                    new_path = sp.split("[")[0]
                    self.output = self.output[new_path]
                    array_pos = int(sp.split("[")[1].split("]")[0])
                    self.output = self.output[array_pos]
            except Exception as e:
                print("Error", e)
                
        return self.output
    
    def extract_all_content(self, json_data):
        contents = []

        def recursive_extract(data):
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "content" and isinstance(value, str):
                        contents.append(value)
                    else:
                        recursive_extract(value)
            elif isinstance(data, list):
                for item in data:
                    recursive_extract(item)

        recursive_extract(json_data)
        return " ".join(contents)
    
    def create_empty_json_from_skeleton(self, skeleton):
        result = {}
        
        for item in skeleton:
            path = item['path']
            parts = path.split('.')
            current = result
            
            for i, part in enumerate(parts):
                if part.endswith('[]'):
                    key = part[:-2]
                    if key not in current:
                        current[key] = []
                        if i == len(parts) - 1 and item['type'] == 'array<object>':
                            current[key].append({})
                    if i < len(parts) - 1:
                        if not current[key]:
                            current[key].append({})
                        current = current[key][0]
                    else:
                        pass
                else:
                    if part not in current:
                        if i == len(parts) - 1:
                            if item['type'] == 'string':
                                current[part] = ""
                            elif item['type'] == 'object':
                                current[part] = {}
                            elif item['type'].startswith('array'):
                                current[part] = []
                        else:
                            current[part] = {}
                    current = current[part]
        return result
        
    def extract(self, chunks, decomposed_schema):
        copy_chunks = copy.deepcopy(chunks)
        no_content_chunks, content_mapping =  self.remove_content(copy_chunks)
        
        final_output = []
        
        for schema_field in decomposed_schema:
            if schema_field['node_type'] == "trunk":
                if self.max_child_depth(decomposed_schema, schema_field['path']) == 0:
                    prompt = self.prompt.extract_path_for_trunk(schema_field, no_content_chunks)
                    output = self.model.generate(prompt)
                    output = self.model.extract_json(output)
                    
                    path = output['output']
                    req_json = self.get_from_json_path(chunks, path)
                    content = self.extract_all_content(req_json)
                    
                    prompt = self.prompt.extract_trunk_field_simple(schema_field, content)
                    output = self.model.generate(prompt)
                    output = self.model.extract_json(output)
                    final_output.append({'schema_field': schema_field, 'data': output['output']})
                else:
                    prompt = self.prompt.extract_path_for_trunk_child_list(schema_field, no_content_chunks)
                    output = self.model.generate(prompt)
                    output = self.model.extract_json(output)
                    
                    content = ""
                    for o in output['output']:
                        req_json = self.get_from_json_path(chunks, o)
                        content += self.extract_all_content(req_json)
                        
                    sub_json_w_meta = [r for r in decomposed_schema if r['path'].startswith(schema_field['path'])]
                    skeleton_json = self.create_empty_json_from_skeleton(sub_json_w_meta)
                    
                    prompt = self.prompt.extract_trunk_field_children(sub_json_w_meta, skeleton_json, content)
                    output = self.model.generate(prompt)
                    output = self.model.extract_json(output)
                    final_output.append({'schema_field': schema_field, 'data': output['output']})
            
        return final_output