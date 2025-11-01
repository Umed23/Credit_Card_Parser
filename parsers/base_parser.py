"""
Base parser class with common functionality for all credit card statement parsers
"""

import re
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pdfplumber


class BaseParser(ABC):
        
    def __init__(self):
        pass
    
    @abstractmethod
    def parse(self, pdf_path: str, verbose: bool = False) -> Optional[Dict]:
        pass
    
    def extract_text(self, pdf_path: str, max_pages: int = 10) -> str:
        
        full_text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for i, page in enumerate(pdf.pages[:max_pages]):
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"
        except Exception as e:
            print(f"Error extracting text: {e}")
        return full_text
    
    def extract_tables(self, pdf_path: str) -> List:
        
        tables = []
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
        except Exception as e:
            print(f"Error extracting tables: {e}")
        return tables
    
    def find_date_pattern(self, text: str) -> Optional[str]:
        
        patterns = [
            r'\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}',  # MM/DD/YYYY or MM-DD-YYYY
            r'\d{4}[\/\-]\d{1,2}[\/\-]\d{1,2}',    # YYYY/MM/DD
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)
        return None
    
    def find_amount_pattern(self, text: str, field_name: str = None) -> Optional[float]:
        """
        Find amount patterns in text
        
        Args:
            text: Text to search
            field_name: Optional field name to search for
            
        Returns:
            First matched amount or None
        """
        if field_name:
            pattern = rf'{field_name}[:\s]+\$?([\d,]+\.?\d*)'
        else:
            pattern = r'\$?([\d,]+\.?\d{2})'
        
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                return float(match.replace(',', ''))
            except ValueError:
                continue
        return None
    
    def find_card_last_4(self, text: str) -> Optional[str]:
       
        patterns = [
            r'(?:card ending in|account ending in|ending in)[:\s#]*(\d{4})',
            r'(\d{4})(?:\s+ending|\s+xxxx)',
            r'xxxx[-\s]*xxxx[-\s]*xxxx[-\s]*(\d{4})',
            r'ending[:\s]+(\d{4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def find_billing_cycle(self, text: str) -> Optional[Dict]:
        
        patterns = [
            r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s*[\-–—]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'billing period[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+to\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'start_date': match.group(1),
                    'end_date': match.group(2)
                }
        return None
    
    def find_due_date(self, text: str) -> Optional[str]:
        
        patterns = [
            r'payment due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'pay by[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None


