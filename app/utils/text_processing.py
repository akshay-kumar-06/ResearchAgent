"""
Text Processing Utilities

Functions for cleaning, chunking, and processing text content
"""

import re
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize text content
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters but keep punctuation
    text = re.sub(r'[^\w\s.,!?;:\-\'"()[\]{}]', '', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 100) -> List[str]:
    """
    Split text into overlapping chunks
    
    Args:
        text: Text to chunk
        chunk_size: Maximum size of each chunk
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if not text or chunk_size <= 0:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at a sentence boundary
        if end < len(text):
            # Look for sentence endings
            for delimiter in ['. ', '! ', '? ', '\n']:
                last_break = text.rfind(delimiter, start, end)
                if last_break > start:
                    end = last_break + len(delimiter)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start position with overlap
        start = end - overlap if end < len(text) else len(text)
    
    return chunks


def extract_keywords(text: str, max_keywords: int = 10) -> List[str]:
    """
    Extract potential keywords from text
    
    Args:
        text: Text to extract keywords from
        max_keywords: Maximum number of keywords to return
        
    Returns:
        List of keywords
    """
    # Simple keyword extraction based on word frequency
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    
    # Count frequency
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    
    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    
    return [word for word, _ in sorted_words[:max_keywords]]


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    # Try to break at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.7:
        truncated = truncated[:last_space]
    
    return truncated + suffix
