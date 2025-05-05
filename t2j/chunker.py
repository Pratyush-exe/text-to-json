from typing import List

class DocumentChunker:
    @staticmethod
    def chunk_by_paragraphs(text: str) -> List[str]:
        """Basic chunking by paragraphs"""
        return [p.strip() for p in text.split('\n\n') if p.strip()]
    
    @staticmethod
    def chunk_by_sentences(text: str, sentences_per_chunk: int = 3) -> List[str]:
        """Chunk by grouping sentences together"""
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        chunks = []
        for i in range(0, len(sentences), sentences_per_chunk):
            chunks.append('. '.join(sentences[i:i+sentences_per_chunk]))
        return chunks