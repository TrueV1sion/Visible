from typing import Dict, Any, List
import spacy
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import nltk
from datetime import datetime
from .base_agent import BaseAgent


# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')


class NLPSummarizationAgent(BaseAgent):
    """Agent for summarizing and extracting key information from text data."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the NLP summarization agent.
        
        Args:
            config: Configuration dictionary containing model parameters
        """
        super().__init__(config)
        self.config = config or {}
        
        # Load spaCy model for NER and dependency parsing
        self.nlp = spacy.load(self.config.get('spacy_model', 'en_core_web_sm'))
        
        # Initialize summarization pipeline
        self.summarizer = pipeline(
            "summarization",
            model=self.config.get('model', 'facebook/bart-large-cnn'),
            device=self.config.get('device', -1)  # -1 for CPU, >= 0 for GPU
        )
        
        # Configure summarization parameters
        self.max_length = self.config.get('max_length', 130)
        self.min_length = self.config.get('min_length', 30)
        self.chunk_size = self.config.get('chunk_size', 1000)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing data to process
            
        Returns:
            Boolean indicating if input is valid
        """
        return (isinstance(input_data.get('data'), list) and 
                len(input_data.get('data', [])) > 0)

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks for processing.
        
        Args:
            text: Text to split
            
        Returns:
            List of text chunks
        """
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            if current_length + sentence_length <= self.chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return chunks

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        Extract named entities from text.
        
        Args:
            text: Text to process
            
        Returns:
            Dictionary of entity types and their values
        """
        doc = self.nlp(text)
        entities = {}
        
        for ent in doc.ents:
            if ent.label_ not in entities:
                entities[ent.label_] = []
            if ent.text not in entities[ent.label_]:
                entities[ent.label_].append(ent.text)
        
        return entities

    def extract_key_phrases(self, text: str) -> List[str]:
        """
        Extract key phrases using dependency parsing.
        
        Args:
            text: Text to process
            
        Returns:
            List of key phrases
        """
        doc = self.nlp(text)
        phrases = []
        
        for chunk in doc.noun_chunks:
            # Get the chunk and its root head
            if chunk.root.dep_ in ['nsubj', 'dobj', 'pobj']:
                phrase = chunk.text.strip()
                if len(phrase.split()) > 1:  # Only phrases with 2+ words
                    phrases.append(phrase)
        
        return list(set(phrases))

    def summarize_text(self, text: str) -> str:
        """
        Generate a summary of the text.
        
        Args:
            text: Text to summarize
            
        Returns:
            Summarized text
        """
        chunks = self.chunk_text(text)
        summaries = []
        
        for chunk in chunks:
            if len(chunk.split()) < self.min_length:
                continue
                
            try:
                summary = self.summarizer(
                    chunk,
                    max_length=self.max_length,
                    min_length=self.min_length,
                    do_sample=False
                )[0]['summary_text']
                summaries.append(summary)
            except Exception as e:
                self.logger.error(f"Error summarizing chunk: {str(e)}")
        
        return ' '.join(summaries)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and summarize the input data.
        
        Args:
            input_data: Dictionary containing data to process
            
        Returns:
            Dictionary containing processed data
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            processed_data = []
            
            for item in input_data['data']:
                if 'content' not in item:
                    continue
                    
                text = item['content']
                processed_item = {
                    'original_content': text,
                    'summary': self.summarize_text(text),
                    'entities': self.extract_entities(text),
                    'key_phrases': self.extract_key_phrases(text)
                }
                processed_data.append(processed_item)
            
            return {
                'status': 'success',
                'data': processed_data,
                'metadata': {
                    'processed_count': len(processed_data),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error in NLP processing: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the NLP summarization agent
    agent = NLPSummarizationAgent({
        'spacy_model': 'en_core_web_sm',
        'model': 'facebook/bart-large-cnn',
        'max_length': 130,
        'min_length': 30
    })
    
    test_data = {
        'data': [{
            'content': """
            Artificial Intelligence has transformed various industries.
            Machine learning algorithms can now process vast amounts of data
            and make predictions with high accuracy. Deep learning models
            have achieved remarkable results in computer vision and natural
            language processing tasks. Companies are increasingly adopting
            AI solutions to automate processes and gain insights from their data.
            """
        }]
    }
    
    results = agent.process(test_data)
    print("Summary:", results['data'][0]['summary'])
    print("Entities:", results['data'][0]['entities'])
    print("Key Phrases:", results['data'][0]['key_phrases']) 