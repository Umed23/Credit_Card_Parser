"""
Main Credit Card Statement Parser
Orchestrates parsing across multiple credit card issuers
"""

import re
import os
from typing import Dict, List, Optional
from datetime import datetime
import pdfplumber
import pypdf

# Import issuer-specific parsers
from parsers.chase_parser import ChaseParser
from parsers.capital_one_parser import CapitalOneParser
from parsers.citi_parser import CitiParser
from parsers.amex_parser import AmexParser
from parsers.discover_parser import DiscoverParser


class CreditCardStatementParser:
    """Main parser class that routes to issuer-specific parsers"""
    
    def __init__(self):
        """Initialize the parser with issuer-specific handlers"""
        self.parsers = {
            'chase': ChaseParser(),
            'capital_one': CapitalOneParser(),
            'citi': CitiParser(),
            'amex': AmexParser(),
            'discover': DiscoverParser()
        }
    
    def identify_issuer(self, pdf_path: str) -> Optional[str]:
        """
        Identify the credit card issuer from the PDF content
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Issuer identifier string or None if cannot identify
        """
        try:
            # Read first few pages to identify issuer
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                # Check first 3 pages
                for i, page in enumerate(pdf.pages[:3]):
                    text += page.extract_text() or ""
                
                text_lower = text.lower()
                
                # Check for issuer keywords (order matters!)
                if 'capital one' in text_lower:
                    return 'capital_one'
                elif 'citibank' in text_lower or 'citi bank' in text_lower or 'citi double cash' in text_lower or 'citi®' in text_lower:
                    return 'citi'
                elif 'discover' in text_lower:
                    return 'discover'
                elif re.search(r'\bamerican express\b', text_lower):
                    return 'amex'
                elif 'chase' in text_lower:
                    return 'chase'
                
                return None
        except Exception as e:
            print(f"Error identifying issuer: {e}")
            return None
    
    def parse(self, pdf_path: str, verbose: bool = False) -> Optional[Dict]:
        """
        Parse a credit card statement PDF
        
        Args:
            pdf_path: Path to the PDF file
            verbose: Enable verbose output
            
        Returns:
            Dictionary containing extracted data or None if parsing fails
        """
        if not os.path.exists(pdf_path):
            print(f"Error: File not found: {pdf_path}")
            return None
        
        # Identify issuer
        if verbose:
            print(f"Processing: {pdf_path}")
        
        issuer = self.identify_issuer(pdf_path)
        
        if not issuer:
            print("Warning: Could not identify credit card issuer. Attempting generic parsing...")
            # Try to parse generically
            return self._generic_parse(pdf_path, verbose)
        
        if verbose:
            print(f"Identified issuer: {issuer.replace('_', ' ').title()}")
        
        # Get appropriate parser
        parser = self.parsers.get(issuer)
        if not parser:
            print(f"Error: No parser available for issuer: {issuer}")
            return None
        
        # Parse with issuer-specific parser
        try:
            result = parser.parse(pdf_path, verbose)
            if result:
                result['issuer'] = issuer.replace('_', ' ').title()
            return result
        except Exception as e:
            print(f"Error parsing statement: {e}")
            if verbose:
                import traceback
                traceback.print_exc()
            return None
    
    def _generic_parse(self, pdf_path: str, verbose: bool = False) -> Optional[Dict]:
        """
        Generic fallback parser when issuer cannot be identified
        
        Args:
            pdf_path: Path to the PDF file
            verbose: Enable verbose output
            
        Returns:
            Dictionary containing extracted data or None if parsing fails
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    full_text += page.extract_text() or ""
                
                # Try to extract basic information
                result = {
                    'issuer': 'Unknown',
                    'billing_cycle': self._extract_billing_cycle_generic(full_text),
                    'payment_due_date': self._extract_due_date_generic(full_text),
                    'card_last_4': self._extract_card_last_4_generic(full_text),
                    'total_balance': self._extract_balance_generic(full_text),
                    'transactions': self._extract_transactions_generic(full_text)
                }
                
                return result
        except Exception as e:
            print(f"Error in generic parsing: {e}")
            return None
    
    def _extract_billing_cycle_generic(self, text: str) -> Optional[Dict]:
        """Extract billing cycle from generic text"""
        # Look for date ranges
        pattern = r'(\d{1,2}[\/\-])\d{1,2}[\/\-]\d{2,4}\s*[\-–—]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        match = re.search(pattern, text)
        if match:
            return {'start_date': match.group(1), 'end_date': match.group(2)}
        return None
    
    def _extract_due_date_generic(self, text: str) -> Optional[str]:
        """Extract payment due date from generic text"""
        patterns = [
            r'payment due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'minimum payment due[:\s]+\$[^:]+:[\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_card_last_4_generic(self, text: str) -> Optional[str]:
        """Extract last 4 digits of card from generic text"""
        patterns = [
            r'(?:card ending in|card number|account ending)[:\s#]*(\d{4})',
            r'(?:ending[:\s]*)?(\d{4})\s*(?:ending|xxxx|xxxx)',
            r'xxxx[-\s]*xxxx[-\s]*xxxx[-\s]*(\d{4})'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def _extract_balance_generic(self, text: str) -> Optional[float]:
        """Extract total balance from generic text"""
        patterns = [
            r'new balance[:\s]+\$?([\d,]+\.?\d*)',
            r'total balance[:\s]+\$?([\d,]+\.?\d*)',
            r'current balance[:\s]+\$?([\d,]+\.?\d*)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None
    
    def _extract_transactions_generic(self, text: str) -> List[Dict]:
        """Extract transactions from generic text"""
        transactions = []
        # Look for date patterns followed by amounts
        pattern = r'(\d{1,2}[\/\-]\d{1,2})[^$]+\$?([\d,]+\.?\d*)'
        matches = re.findall(pattern, text)
        # This is a very basic extraction - issuer-specific parsers will do better
        return transactions

