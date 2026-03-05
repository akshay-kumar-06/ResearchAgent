"""
Markdown Generator Utilities

Helper class for generating structured markdown reports
"""

from typing import List, Dict, Any
from datetime import datetime


class MarkdownGenerator:
    """Helper class for generating markdown content"""
    
    def __init__(self):
        self.content: List[str] = []
    
    def add_heading(self, text: str, level: int = 1) -> 'MarkdownGenerator':
        """
        Add a heading
        
        Args:
            text: Heading text
            level: Heading level (1-6)
            
        Returns:
            Self for chaining
        """
        prefix = '#' * min(max(level, 1), 6)
        self.content.append(f"\n{prefix} {text}\n")
        return self
    
    def add_paragraph(self, text: str) -> 'MarkdownGenerator':
        """Add a paragraph"""
        self.content.append(f"\n{text}\n")
        return self
    
    def add_bullet_list(self, items: List[str]) -> 'MarkdownGenerator':
        """Add a bullet list"""
        for item in items:
            self.content.append(f"- {item}")
        self.content.append("")
        return self
    
    def add_numbered_list(self, items: List[str]) -> 'MarkdownGenerator':
        """Add a numbered list"""
        for idx, item in enumerate(items, 1):
            self.content.append(f"{idx}. {item}")
        self.content.append("")
        return self
    
    def add_blockquote(self, text: str) -> 'MarkdownGenerator':
        """Add a blockquote"""
        lines = text.split('\n')
        for line in lines:
            self.content.append(f"> {line}")
        self.content.append("")
        return self
    
    def add_code_block(self, code: str, language: str = "") -> 'MarkdownGenerator':
        """Add a code block"""
        self.content.append(f"```{language}")
        self.content.append(code)
        self.content.append("```")
        return self
    
    def add_table(self, headers: List[str], rows: List[List[str]]) -> 'MarkdownGenerator':
        """
        Add a markdown table
        
        Args:
            headers: Column headers
            rows: Table rows
        """
        # Header row
        self.content.append("| " + " | ".join(headers) + " |")
        # Separator
        self.content.append("| " + " | ".join(["---"] * len(headers)) + " |")
        # Data rows
        for row in rows:
            self.content.append("| " + " | ".join(row) + " |")
        self.content.append("")
        return self
    
    def add_horizontal_rule(self) -> 'MarkdownGenerator':
        """Add a horizontal rule"""
        self.content.append("\n---\n")
        return self
    
    def add_link(self, text: str, url: str) -> 'MarkdownGenerator':
        """Add a link inline"""
        self.content.append(f"[{text}]({url})")
        return self
    
    def add_metadata(self, metadata: Dict[str, Any]) -> 'MarkdownGenerator':
        """Add metadata as key-value pairs"""
        for key, value in metadata.items():
            self.content.append(f"**{key}:** {value}")
        self.content.append("")
        return self
    
    def add_timestamp(self) -> 'MarkdownGenerator':
        """Add current timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.content.append(f"\n*Generated on {timestamp}*\n")
        return self
    
    def build(self) -> str:
        """
        Build the final markdown string
        
        Returns:
            Complete markdown content
        """
        return "\n".join(self.content)
    
    def clear(self) -> 'MarkdownGenerator':
        """Clear all content"""
        self.content = []
        return self
