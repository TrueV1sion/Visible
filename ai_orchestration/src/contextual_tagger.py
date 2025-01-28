from typing import Dict, Any, List, Set
import spacy
from collections import defaultdict
from datetime import datetime
from .base_agent import BaseAgent


class ContextualTaggerAgent(BaseAgent):
    """Agent for contextual tagging of content."""

    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the contextual tagger agent."""
        super().__init__(config)
        self.config = config or {}
        
        # Load spaCy model
        self.nlp = spacy.load(self.config.get('spacy_model', 'en_core_web_sm'))
        
        # Define tag categories and their keywords
        self.tag_categories = {
            'event_type': {
                'product_launch': {'launch', 'release', 'announce', 'introduce', 'unveil'},
                'pricing_change': {'price', 'pricing', 'cost', 'subscription', 'fee'},
                'partnership': {'partner', 'partnership', 'collaborate', 'alliance'},
                'acquisition': {'acquire', 'acquisition', 'merge', 'purchase'},
                'leadership_change': {'ceo', 'executive', 'appoint', 'hire', 'leadership'}
            },
            'market_focus': {
                'enterprise': {'enterprise', 'corporate', 'large-scale', 'organization'},
                'smb': {'small business', 'medium business', 'smb', 'startup'},
                'consumer': {'consumer', 'individual', 'personal', 'retail'}
            },
            'technology': {
                'ai_ml': {'ai', 'machine learning', 'artificial intelligence', 'neural'},
                'cloud': {'cloud', 'saas', 'aws', 'azure', 'hosted'},
                'security': {'security', 'encryption', 'firewall', 'protection'},
                'integration': {'api', 'integration', 'connector', 'webhook'}
            }
        }

    def validate_input(self, input_data: Dict[str, Any]) -> bool:
        """Validate input data contains required fields."""
        return isinstance(input_data.get('data'), list) and len(input_data.get('data', [])) > 0

    def extract_entities(self, text: str) -> Dict[str, Set[str]]:
        """Extract named entities from text."""
        doc = self.nlp(text)
        entities = defaultdict(set)
        
        for ent in doc.ents:
            entities[ent.label_].add(ent.text)
        
        return dict(entities)

    def find_category_matches(self, text: str) -> Dict[str, List[str]]:
        """Find matches for predefined tag categories."""
        text_lower = text.lower()
        matches = defaultdict(list)
        
        for category, subcategories in self.tag_categories.items():
            for subcategory, keywords in subcategories.items():
                if any(keyword.lower() in text_lower for keyword in keywords):
                    matches[category].append(subcategory)
        
        return dict(matches)

    def extract_custom_tags(self, text: str) -> List[str]:
        """Extract custom tags based on noun phrases and key terms."""
        doc = self.nlp(text)
        custom_tags = set()
        
        # Extract noun phrases
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 3:  # Limit to phrases of 3 words or less
                custom_tags.add(chunk.text.lower())
        
        # Extract key terms based on part-of-speech
        for token in doc:
            if token.pos_ in {'NOUN', 'PROPN'} and not token.is_stop:
                custom_tags.add(token.text.lower())
        
        return list(custom_tags)

    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of the text."""
        doc = self.nlp(text)
        
        # Simple rule-based sentiment analysis
        positive_words = {'increase', 'growth', 'improve', 'success', 'innovative'}
        negative_words = {'decrease', 'decline', 'fail', 'problem', 'issue'}
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total = positive_count + negative_count
        if total == 0:
            sentiment_score = 0.0
        else:
            sentiment_score = (positive_count - negative_count) / total
        
        return {
            'score': sentiment_score,
            'label': (
                'positive' if sentiment_score > 0.1
                else 'negative' if sentiment_score < -0.1
                else 'neutral'
            )
        }

    async def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process and tag the input data."""
        if not self.validate_input(input_data):
            raise ValueError("Invalid input data format")

        try:
            tagged_items = []
            
            for item in input_data['data']:
                if 'content' not in item:
                    continue
                    
                content = item['content']
                
                # Process the content
                entities = self.extract_entities(content)
                category_matches = self.find_category_matches(content)
                custom_tags = self.extract_custom_tags(content)
                sentiment = self.analyze_sentiment(content)
                
                tagged_item = {
                    **item,
                    'metadata': {
                        'entities': entities,
                        'categories': category_matches,
                        'custom_tags': custom_tags,
                        'sentiment': sentiment,
                        'processed_at': datetime.now().isoformat()
                    }
                }
                
                tagged_items.append(tagged_item)
            
            return {
                'status': 'success',
                'data': tagged_items,
                'metadata': {
                    'items_processed': len(tagged_items),
                    'timestamp': datetime.now().isoformat()
                }
            }
        except Exception as e:
            self.logger.error(f"Error in contextual tagging: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'metadata': {
                    'timestamp': datetime.now().isoformat()
                }
            }


if __name__ == "__main__":
    # Test the contextual tagger agent
    agent = ContextualTaggerAgent({
        'spacy_model': 'en_core_web_sm'
    })
    
    test_data = {
        'data': [
            {
                'content': """
                Microsoft announces new AI-powered cloud services for enterprise customers.
                The launch includes advanced security features and seamless integration
                with existing systems. Pricing starts at $99 per month.
                """,
                'source': 'test'
            },
            {
                'content': """
                Startup XYZ raises Series B funding to expand their innovative
                machine learning platform for small businesses. The company plans
                to enhance their API capabilities and partner ecosystem.
                """,
                'source': 'test'
            }
        ]
    }
    
    import asyncio
    results = asyncio.run(agent.process(test_data))
    print("Tagged Results:", results['data']) 