from tqdm import tqdm
import re

from t2j.prem_sdk import PremSDK
from t2j.prompts import Prompts
from t2j.utils import *


class DocumentChunker:
    """Logically chunks a given document in a format which can be utilized for other modules
    """
    def __init__(self, prompts: Prompts, model: PremSDK):
        self.prompts = prompts
        self.model = model
        self.banned_headings = ["Appendix"]
        
    def smart_chunk(self, file_path: str, chunk_size_lines: int):
        lines = extract_text(file_path)
        chunks = chunk(lines, chunk_size_lines)
        prompts = [self.prompts.extract_headings_prompt(chunk) for chunk in chunks]
        responses = self.model.generate_parallel(prompts)

        all_headings = []
        for i, response in enumerate(responses):
            headings = []
            if response:
                try:
                    headings = self.model.extract_json(response)
                except Exception as parse_error:
                    print(f"Parse error in chunk {i+1}: {parse_error}")
            all_headings.append({
                "chunk_id": i,
                "headings": headings
            })
        headings = self.filter_headings(all_headings)
        logical_chunks = self.extract_logical_chunks(headings, chunks)
        output = self.create_raw_json(logical_chunks)
        return output
        
    def extract_logical_chunks(self, headings, chunks):
        final_headings = []

        for i, head in tqdm(enumerate(headings), total=len(headings)):
            text_chunk = ""
            for c in head['chunk_id']:
                text_chunk += (" " + chunks[c])
            text_chunk = text_chunk.replace("\n", " ")
            if i+1 != len(headings):
                if headings[i+1]['chunk_id'][-1] != head['chunk_id'][0]:
                    for c_i in headings[i+1]['chunk_id']:
                        text_chunk += (" " + chunks[c_i])
                text_chunk = text_chunk.replace("\n", " ")
                content = text_chunk.split(head['heading'], maxsplit=1)[1].split(headings[i+1]['heading'], maxsplit=1)[0]
                final_headings.append({
                    'heading': head['heading'],
                    'content': content
                })
            else:
                content = text_chunk.split(head['heading'], maxsplit=1)[1]
                final_headings.append({
                    'heading': head['heading'],
                    'content': content
                })
        return final_headings
    
    def filter_headings(self, headings):
        filtered_heading = []
        stop = False

        ignore_pattern = re.compile(r'^(figure|table|algorithm)\s+\d+', re.IGNORECASE)
        current_heading_entry = None

        for h in headings:
            for head in h['headings']:
                if any(word.lower() in [b.lower() for b in self.banned_headings] for word in head.split()):
                    stop = True
                    break

                if ignore_pattern.match(head.strip()):
                    if current_heading_entry:
                        current_heading_entry["chunk_id"].append(h['chunk_id'])
                    continue

                current_heading_entry = {
                    "heading": head,
                    "chunk_id": [h['chunk_id']]
                }
                filtered_heading.append(current_heading_entry)

            if stop:
                break

        return filtered_heading
    
    def extract_other_info(self, file_path: str):
        page = extract_first_page(file_path)
        prompt = self.prompts.extract_meta_data(page)
        output = self.model.generate(prompt)
        output = self.model.extract_json(output)
        simplified = [{
            'heading': k,
            'content': v,
        } for k, v in output.items()]
        return simplified
    
    def create_content_mapping(self, headings):
        mappings = {}
        
        for i, heading in enumerate(headings):
            mappings[str(i)] = heading['content']
            headings[i]['content'] = str(i)
        return mappings, headings
    
    def create_raw_json(self, headings):
        content_mapping, mapped_headings = self.create_content_mapping(headings)
        output = self.model.generate(self.prompts.create_rough_json(mapped_headings))
        result =  self.model.extract_json(output)
        self.replace_content(result, content_mapping)
        
        return result
    
    def replace_content(self, data, content_map):
        for key, value in data.items():
            if 'content' in value:
                content_id = value['content']
                if content_id in content_map:
                    value['content'] = content_map[content_id]

            if 'sub-headings' in value and isinstance(value['sub-headings'], list):
                for sub_item in value['sub-headings']:
                    for sub_key, sub_value in sub_item.items():
                        self.replace_content({sub_key: sub_value}, content_map)