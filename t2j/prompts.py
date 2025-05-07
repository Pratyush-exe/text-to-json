import json
from typing import List

class Prompts:
    @staticmethod
    def extract_headings_prompt(text_chunk: str) -> str:
        return f"""
## TASK: You are an assistant that extracts section headings, subheadings, and other headings from academic or technical papers.
Follow the guidelines strictly.

## GUIDELINES:
1. Identify and extract **section headings, subheadings, and other headings** from the "TEXT".
2. Prefer numbered headings if present (e.g., "1. Introduction", "2.1 Previous Work").
3. Only return **phrases that clearly represent headings/subheadings**.
4. Return the output as a JSON list of phrases in the order they appear. Refer "OUTPUT FORMAT".

## Text:
\"\"\"
{text_chunk}
\"\"\"

## OUTPUT FORMAT:
```json
// required json
```
"""

    @staticmethod
    def create_rough_json(headings: List[str]) -> str:
        return """
## TASK: Given a list of section and subsection titles from a research paper or technical document. Your task is to organize these items into a clean, nested JSON format that clearly reflects the hierarchy of sections and their corresponding subsections.
Follow the guidelines strictly.

## GUIDELINES:
1. Identify top-level sections by numbering (e.g., 1 Introduction, 2 Related Work, 3 Methods, etc.). Each of these becomes a top-level key in the JSON.
2. Group subsections under the correct top-level section. Subsections are typically numbered in the format X.Y, such as 3.1, 3.2, etc.
3. Unnumbered items:
3.1 The given order of Items is correct and needs to be followed at all times.
3.2 If an item is unnumbered but logically follows or relates to a subsection, include it as a subsection under the closest preceding numbered section or subsection.
3.3 Use your judgment to associate unnumbered items with the most relevant parent section or subsection.
4. Algorithms should be placed under the section or subsection they describe or are closest to.
5. If a section has no subsections, it should still appear with an empty array ([]).
6. Preserve the original casing and wording of each title.
7. Avoid duplicate entries unless they appear distinctly in the list.
8. Look at the "EXAMPLE" for a little idea. on output

## EXAMPLE:
{
    "Section Title": {
        "content": str,
        "sub-headings": [
            {
                "Subsection Title": {
                    "content": str, 
                    "sub-heading": []
                }
            },
            {
                "Subsection Title": {
                    "content": str, 
                    "sub-heading": []
                }
            },
            ...
        ]
    },
    ...
}

""" + f"""
## INPUT:
{str(headings)}

## OUTPUT FORMAT:
```json
// required json
```
"""

    @staticmethod
    def extract_meta_data(text_chunk: str) -> str:
        return f"""
## TASK: Given this document in "TEXT", your job is to extract json fields. Follow "GUIDELINES'. Follow "OUTPUT FORMAT" strictly.

## GUIDELINES:
These are the JSON fields to be extracted:
1. 'abstract' with the exact content of 'abstract' given in the document
2. 'authors' as a list of strings, and string containing all the info given about that particular author.
3. 'date_written': str, date when the paper was written. give output only if the info is here, else empty string,
4. 'title': str, title of the paper

## TEXT:
\"\"\"
{text_chunk}
\"\"\"

""" + """
## OUTPUT FORMAT:
```json
{
    'abstract': str,
    'authors': List[str],
    'date_written': str,
    'title': str
}
```
"""

    @staticmethod
    def extract_path_for_trunk(schema_field_details, simplified_data_json) -> str:
        return f"""
## TASK: Given a field from a schema-json, and another data-json, your job is to fetch the JSON path from data-json that will have the values required in the field of schema-json.

## GUIDELINES:
1. path of the schema-json is given in 'PATH OF SCHEMA JSON', this is the field for which we are fetching the data.
2. 'DESCRIPTION' stores the description of the field from schema-json and what sort of data it stores
3. 'DATA JSON' stores the data-json, so we need to fetch path from here for the field in schema-json
4. Refer the 'EXAMPLE' for which type of output format we are looking for.
5. 'OUTPUT FORMAT' explain the output format. We are basically looking for a string, string containing the JSON path from data-json
7. ONLY RETURN THE JSON, NO OTHER INFO
AS SHOWN IN EXAMPLES, SEPARATE THE PATH by ' -> '

## PATH OF SCHEMA JSON:
{schema_field_details['path']}

## DESCRIPTION:
{schema_field_details.get('description', '')}

## DATA JSON:
{json.dumps(simplified_data_json, indent=2)}
""" + """

## EXAMPLE:
{
    "output": "heading -> sub-headings4[1] -> sub-heads0"
}

## OUTPUT FORMAT:
```json
{
    "output": "path1"
}
```
"""

    @staticmethod
    def extract_path_for_trunk_child_list(schema_field_details, simplified_data_json) -> str:
        return f"""
## TASK: Given a field from a schema-json, and another data-json, your job is to fetch the JSON paths from data-json that will have the values required in the field of schema-json based on description.

## GUIDELINES:
1. path of the schema-json is given in 'PATH OF SCHEMA JSON', this is the field for which we are fetching the data.
2. 'DESCRIPTION' stores the description of the field from schema-json and what sort of data it stores
3. 'DATA JSON' stores the data-json, so we need to fetch paths from here for the field in schema-json
4. Refer the 'EXAMPLE' for which type of output format we are looking for.
5. 'OUTPUT FORMAT' explain the output format. We are basically looking for List of strings, string containing the JSON path from data-json
6. Resulted field should have the required data, no other information.
7. ONLY RETURN THE JSON, NO OTHER INFO
AS SHOWN IN EXAMPLES, SEPARATE THE PATH by ' -> '

## PATH OF SCHEMA JSON:
{schema_field_details['path']}

## DESCRIPTION:
{schema_field_details.get('description', '')}

## DATA JSON:
{json.dumps(simplified_data_json, indent=2)}
""" + """

## EXAMPLE:
{
    "output": [
        "heading -> sub-headings4[1] -> sub-heads0",
        "heading -> sub-headings2[0]",
        ...
    ]
}

## OUTPUT FORMAT:
```json
{
    "output": [
        "path1",
        "path2",
        ...
    ]
}
```
"""

    @staticmethod
    def extract_trunk_field_simple(schema_field_details, content) -> str:
        return f"""
## TASK: Given a field from a schema-json with it's metadata, based on output format, fetch the value from a given content.
Follow the 'GUIDELINES' strictly

## GUIDELINES:
1. path of the json is given in 'PATH OF SCHEMA JSON', this is the field for which we are fetching the value.
2. 'DESCRIPTION' stores the description of the 'PATH OF SCHEMA JSON' and what sort of data it will have 
3. 'OUTPUT DATATYPE', this tells which datatype is expected as a value for the given field
4. 'OUTPUT FORMAT', this tells which format should be of the output.
5. 'CONTENT' contains all the content, from where you will be extracting information. Output cannot be empty as 'CONTENT' exists
6. ONLY RETURN THE JSON, NO OTHER INFO

## CONTENT:
{content}

## PATH OF SCHEMA JSON:
{schema_field_details['path']}

## DESCRIPTION:
{schema_field_details.get('description', '')}

## OUTPUT DATATYPE:
{schema_field_details.get('type', '')}
""" + """

## OUTPUT FORMAT:
```json
{
    'output': // required data from 'OUTPUT DATATYPE'
}
```
"""

    @staticmethod
    def extract_trunk_field_children(sub_json_w_meta, sub_json, content) -> str:
        return f"""
## TASK: Given a sub-json from a schema-json with it's metadata, based on format, fetch the value from given content.
Follow the 'GUIDELINES' strictly

## GUIDELINES:
1. sub-json is given in 'SUB JSON', this is the sub-json for which we are fetching the value.
2. Return list of these sub-json based on guidelines
5. 'OUTPUT FORMAT', this tells which format should be of the output.
6. 'CONTENT' contains all the content, from where you will be extracting information. Output cannot be empty as 'CONTENT' exists
7. ONLY RETURN THE JSON, NO OTHER INFO

## CONTENT:
{content}

## SUB JSON:
{sub_json_w_meta}

## OUTPUT FORMAT:
```json
{{
    'output': [
        {sub_json}
    ]
}}
```
"""

    @staticmethod
    def fix_json(input_json) -> str:
        return f"""
## TASK: Given a JSON, fix the formatting so that it does not fail during JSONDecoder

## GUIDELINES:
1. 'JSON' has the input JSON
2. remember py's json lib is used, so create the final JSON accordingly
3. 'OUTPUT FORMAT', this tells which format should be of the output.
4. ONLY RETURN THE JSON, NO OTHER INFO

## JSON:
{input_json}

## OUTPUT FORMAT:
```json
// output json
```
"""