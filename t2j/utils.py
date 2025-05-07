import pymupdf
import re


def extract_text(file_path: str):
    doc = pymupdf.open(file_path)
    full_text = ""
    for page in doc:        
        text = page.get_text()
        text = text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        text = re.sub(r'[^\x20-\x7E\n\t]', '', text) 
        full_text += text
    doc.close()

    return full_text.splitlines()

def extract_first_page(file_path: str):
    doc = pymupdf.open(file_path)
    full_text = doc[0].get_text()
    full_text = full_text.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
    full_text = re.sub(r'[^\x20-\x7E\n\t]', '', full_text) 
    doc.close()
    return full_text

def chunk(lines, lines_per_chunk=100):
    chunks = [
        "\n".join(lines[i:i + lines_per_chunk])
        for i in range(0, len(lines), lines_per_chunk)
    ]
    return chunks

def merge(extracted_data):
    result = {}
    for data in extracted_data:
        result[data['schema_field']['path'].replace("[", "").replace("]", "")] = data['data']
    return result