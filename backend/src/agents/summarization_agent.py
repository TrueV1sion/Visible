from ..core.utils import anthropic_llm_summarize

class SummarizationAgent:
    def __init__(self, context_protocol=True):
        self.context_protocol = context_protocol

    def summarize_text(self, text_chunks):
        """
        Summarizes large amounts of text by chunking and using
        Anthropic's model context protocol or a similar approach.
        """
        summaries = []
        for chunk in text_chunks:
            summary = anthropic_llm_summarize(chunk)
            summaries.append(summary)
        return " ".join(summaries)

    def run(self, raw_data):
        text_chunks = self.partition(raw_data)
        return self.summarize_text(text_chunks)

    @staticmethod
    def partition(raw_data):
        # Example partitioning into chunks
        chunks = [raw_data[i:i+500] for i in range(0, len(raw_data), 500)]
        return chunks 