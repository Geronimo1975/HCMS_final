import re
from .models import DocumentChunk

class ChatbotService:
    def __init__(self):
        pass

    def get_relevant_chunk(self, question, k=1):
        """
        Retrieve the most relevant document chunk(s) for the given question.
        For now, use simple keyword overlap. Returns a list of chunks.
        """
        question = question.lower()
        best_chunks = []
        best_score = 0
        for chunk in DocumentChunk.objects.all():
            score = sum(1 for word in question.split() if word in chunk.chunk.lower())
            if score > best_score:
                best_score = score
                best_chunks = [chunk.chunk]
            elif score == best_score and score > 0:
                best_chunks.append(chunk.chunk)
        return best_chunks if best_chunks else [None]

    def generate_answer(self, question):
        """
        Generate an answer for the question using RAG (and later, OpenAI).
        For now, return the best matching chunk or a fallback message.
        """
        chunks = self.get_relevant_chunk(question)
        if chunks and chunks[0]:
            return chunks[0]
        return "No relevant information found in the document." 