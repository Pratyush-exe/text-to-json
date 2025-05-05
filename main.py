import streamlit as st
import json
from t2j import SchemaDecomposer, FieldExtractor, JsonMerger

st.title("Text to JSON Converter")

uploaded_schema = st.file_uploader("Upload JSON Schema", type=["json"])
uploaded_text = st.file_uploader("Upload Text Document", type=["txt"])

if st.button("Convert") and uploaded_schema and uploaded_text:
    try:
        schema = json.load(uploaded_schema)
        text = uploaded_text.read().decode("utf-8")
        
        with st.spinner("Processing..."):
            # Pipeline
            decomposer = SchemaDecomposer(schema)
            fields = decomposer.decompose()
            
            extractor = FieldExtractor(schema)
            extractions = [extractor.extract_field(f["path"], text) for f in fields]
            
            merger = JsonMerger()
            result = merger.merge_results(extractions)
            
            st.success("Conversion successful!")
            st.json(result)
            
    except Exception as e:
        st.error(f"Error: {str(e)}")