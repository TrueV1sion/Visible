from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator, HttpUrl
from enum import Enum
import re


class CompetitorInfoSchema(BaseModel):
    """Schema for competitor information validation."""
    name: str = Field(..., min_length=1, max_length=100)
    website: Optional[HttpUrl] = None
    description: Optional[str] = Field(None, max_length=1000)
    primary_offering: Optional[str] = Field(None, max_length=200)
    target_market: Optional[str] = Field(None, max_length=200)
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Competitor name cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        if v:
            return v.strip()
        return v


class ProductSegmentSchema(BaseModel):
    """Schema for product segment validation."""
    id: str = Field(..., regex=r'^[a-zA-Z0-9_-]+$')
    name: str = Field(..., min_length=1, max_length=50)
    
    @validator('id')
    def validate_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError('Product segment ID must contain only alphanumeric characters, hyphens, and underscores')
        return v


class FocusAreaSchema(BaseModel):
    """Schema for focus area validation."""
    value: str = Field(..., min_length=1, max_length=100)
    
    @validator('value')
    def validate_value(cls, v):
        if not v or not v.strip():
            raise ValueError('Focus area cannot be empty')
        return v.strip()


class BattlecardGenerationRequestSchema(BaseModel):
    """Schema for battlecard generation request validation."""
    competitor_info: CompetitorInfoSchema
    product_segment: str = Field(..., min_length=1)
    focus_areas: List[str] = Field(default_factory=list, max_items=10)
    include_sections: Optional[List[str]] = Field(default_factory=lambda: [
        'overview', 'strengths_weaknesses', 'objection_handling', 'winning_strategies'
    ])
    
    @validator('focus_areas')
    def validate_focus_areas(cls, v):
        if not v:
            return []
        
        validated_areas = []
        for area in v:
            if isinstance(area, str) and area.strip():
                validated_areas.append(area.strip())
        
        return validated_areas[:10]  # Limit to 10 items
    
    @validator('include_sections')
    def validate_sections(cls, v):
        allowed_sections = [
            'overview', 'competitive_analysis', 'strengths_weaknesses',
            'pricing_comparison', 'objection_handling', 'winning_strategies'
        ]
        if v:
            return [section for section in v if section in allowed_sections]
        return allowed_sections


class AIProcessingOptionsSchema(BaseModel):
    """Schema for AI processing options."""
    model_preference: Optional[str] = Field(None, regex=r'^(claude|gpt|auto)$')
    complexity_level: Optional[str] = Field('medium', regex=r'^(low|medium|high)$')
    max_tokens: Optional[int] = Field(2000, ge=100, le=4000)
    temperature: Optional[float] = Field(0.7, ge=0.0, le=2.0)
    include_sources: bool = Field(True)
    
    @validator('model_preference')
    def validate_model(cls, v):
        if v and v not in ['claude', 'gpt', 'auto']:
            raise ValueError('Model preference must be claude, gpt, or auto')
        return v


class SearchQuerySchema(BaseModel):
    """Schema for search query validation."""
    query: str = Field(..., min_length=1, max_length=500)
    filters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    max_results: Optional[int] = Field(20, ge=1, le=100)
    
    @validator('query')
    def validate_query(cls, v):
        # Basic XSS prevention
        dangerous_chars = ['<', '>', '"', "'", '&']
        if any(char in v for char in dangerous_chars):
            raise ValueError('Query contains invalid characters')
        return v.strip()


class ObjectionRequestSchema(BaseModel):
    """Schema for objection handling request."""
    objection: str = Field(..., min_length=1, max_length=500)
    context: Dict[str, Any] = Field(default_factory=dict)
    competitor_name: Optional[str] = Field(None, max_length=100)
    product_context: Optional[str] = Field(None, max_length=1000)
    
    @validator('objection')
    def validate_objection(cls, v):
        if not v or not v.strip():
            raise ValueError('Objection cannot be empty')
        return v.strip()


class InsightContextSchema(BaseModel):
    """Schema for insight generation context."""
    battlecard_id: Optional[str] = None
    competitor_id: Optional[str] = None
    section: Optional[str] = None
    focus_area: Optional[str] = None
    
    @validator('section')
    def validate_section(cls, v):
        if v:
            allowed_sections = [
                'overview', 'competitive_analysis', 'strengths_weaknesses',
                'pricing_comparison', 'objection_handling', 'winning_strategies'
            ]
            if v not in allowed_sections:
                raise ValueError(f'Invalid section. Must be one of: {allowed_sections}')
        return v


class DataCollectionConfigSchema(BaseModel):
    """Schema for data collection configuration."""
    search_terms: List[str] = Field(..., min_items=1, max_items=20)
    max_pages: int = Field(5, ge=1, le=20)
    include_social_media: bool = Field(True)
    include_news: bool = Field(True)
    include_company_data: bool = Field(True)
    date_range_days: Optional[int] = Field(30, ge=1, le=365)
    
    @validator('search_terms')
    def validate_search_terms(cls, v):
        validated_terms = []
        for term in v:
            if isinstance(term, str) and term.strip():
                # Basic validation for search terms
                if len(term.strip()) >= 2:
                    validated_terms.append(term.strip())
        
        if not validated_terms:
            raise ValueError('At least one valid search term is required')
        
        return validated_terms[:20]  # Limit to 20 terms


# URL validation helper
def validate_external_url(url: str, allowed_domains: List[str]) -> bool:
    """Validate that URL is from an allowed domain."""
    try:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix for comparison
        if domain.startswith('www.'):
            domain = domain[4:]
        
        return any(
            domain == allowed_domain.lower() or 
            domain.endswith(f'.{allowed_domain.lower()}')
            for allowed_domain in allowed_domains
        )
    except Exception:
        return False


# Content validation helpers
def sanitize_html_content(content: str) -> str:
    """Remove potentially dangerous HTML tags from content."""
    import html
    from bs4 import BeautifulSoup
    
    # Parse with BeautifulSoup and extract text only
    soup = BeautifulSoup(content, 'html.parser')
    text = soup.get_text()
    
    # HTML escape the result
    return html.escape(text.strip())


def validate_json_size(data: Dict[str, Any], max_size_mb: int = 1) -> bool:
    """Validate that JSON data size doesn't exceed limit."""
    import json
    import sys
    
    json_str = json.dumps(data)
    size_bytes = sys.getsizeof(json_str)
    size_mb = size_bytes / (1024 * 1024)
    
    return size_mb <= max_size_mb