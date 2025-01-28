import pandas as pd
from typing import Dict, Any
import re
from datetime import datetime
from nltk.tokenize import sent_tokenize
import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from .base_agent import BaseAgent

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class DataCleaningAgent(BaseAgent):
    """Agent for cleaning and preprocessing collected data."""

    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the data cleaning agent.
        
        Args:
            config: Configuration dictionary containing cleaning parameters
        """
        super().__init__(config)
        self.config = config or {}
        self.min_text_length = self.config.get('min_text_length', 50)
        self.max_text_length = self.config.get('max_text_length', 10000)
        self.min_sentences = self.config.get('min_sentences', 2)

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """
        Validate input data contains required fields.
        
        Args:
            input_data: Dictionary containing data to clean
            
        Returns:
            Boolean indicating if input is valid
        """
        return (isinstance(input_data.get('data'), list) and 
                len(input_data.get('data', [])) > 0)

    def clean_text(self, text: str) -> str:
        """
        Clean text by removing special characters and normalizing whitespace.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        if not isinstance(text, str):
            return ""
            
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove special characters and normalize whitespace
        text = re.sub(r'[^\w\s.,!?-]', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove duplicate entries based on content similarity.
        
        Args:
            df: DataFrame containing the data
            
        Returns:
            DataFrame with duplicates removed
        """
        if df.empty:
            return df
            
        # Create TF-IDF matrix
        tfidf = TfidfVectorizer(max_features=1000)
        try:
            tfidf_matrix = tfidf.fit_transform(df['content'].fillna(''))
            
            # Calculate similarity matrix
            similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
            
            # Find duplicates
            duplicate_indices = []
            for i in range(len(similarity_matrix)):
                for j in range(i + 1, len(similarity_matrix)):
                    if similarity_matrix[i][j] > 0.8:  # Similarity threshold
                        duplicate_indices.append(j)
            
            # Keep first occurrence, remove duplicates
            return df.drop(index=list(set(duplicate_indices)))
        except Exception as e:
            self.logger.error(f"Error removing duplicates: {str(e)}")
            return df

    def filter_content(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter content based on quality criteria.
        
        Args:
            df: DataFrame containing the data
            
        Returns:
            Filtered DataFrame
        """
        if df.empty:
            return df
            
        # Convert to DataFrame if input is a list of dictionaries
        if isinstance(df, list):
            df = pd.DataFrame(df)

        # Apply text length filters
        df['content_length'] = df['content'].str.len()
        df['sentence_count'] = df['content'].apply(
            lambda x: len(sent_tokenize(str(x)))
        )
        
        # Filter based on criteria
        mask = (
            (df['content_length'] >= self.min_text_length) &
            (df['content_length'] <= self.max_text_length) &
            (df['sentence_count'] >= self.min_sentences)
        )
        
        return df[mask].drop(['content_length', 'sentence_count'], axis=1)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process and clean the input data.
        
        Args:
            input_data: Dictionary containing data to clean
            
        Returns:
            Dictionary containing cleaned data
        """
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            # Convert input data to DataFrame
            df = pd.DataFrame(input_data['data'])
            
            # Clean text content
            if 'content' in df.columns:
                df['content'] = df['content'].apply(self.clean_text)
            
            # Remove duplicates
            df = self.remove_duplicates(df)
            
            # Filter content
            df = self.filter_content(df)
            
            return {
                'status': 'success',
                'data': df.to_dict('records'),
                'metadata': {
                    'initial_count': len(input_data['data']),
                    'final_count': len(df),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error in data cleaning: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the data cleaning agent
    agent = DataCleaningAgent({
        'min_text_length': 100,
        'max_text_length': 5000,
        'min_sentences': 3
    })
    
    test_data = {
        'data': [
            {'content': 'Short text.'},
            {'content': 'This is a longer text with multiple sentences. '
             'It should pass the filters. The content is unique.'},
            {'content': '<p>HTML content</p> with special characters & symbols!'}
        ]
    }
    
    results = agent.process(test_data)
    print(f"Cleaned {len(results['data'])} records") 