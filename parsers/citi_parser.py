"""
Citibank Credit Card Statement Parser
"""

import re
from typing import Dict, Optional
from .base_parser import BaseParser


class CitiParser(BaseParser):
    """Parser for Citibank credit card statements"""
    
    def parse(self, pdf_path: str, verbose: bool = False) -> Optional[Dict]:
        """
        Parse Citibank credit card statement
        
        Args:
            pdf_path: Path to the PDF file
            verbose: Enable verbose output
            
        Returns:
            Dictionary containing extracted data
        """
        try:
            text = self.extract_text(pdf_path)
            
            if verbose:
                print("Extracting data from Citibank statement...")
            
            # Extract billing cycle
            billing_cycle = self.extract_billing_cycle_citi(text)
            
            # Extract payment due date
            payment_due_date = self.extract_due_date_citi(text)
            
            # Extract card last 4 digits
            card_last_4 = self.extract_card_last_4_citi(text)
            
            # Extract total balance
            total_balance = self.extract_total_balance_citi(text)
            
            # Extract transactions
            transactions = self.extract_transactions_citi(pdf_path, verbose)
            
            return {
                'billing_cycle': billing_cycle,
                'payment_due_date': payment_due_date,
                'card_last_4': card_last_4,
                'total_balance': total_balance,
                'transactions': transactions
            }
        except Exception as e:
            print(f"Error parsing Citibank statement: {e}")
            return None
    
    def extract_billing_cycle_citi(self, text: str) -> Optional[Dict]:
        """Extract billing cycle from Citibank statement"""
        # Citi format: "Statement Period: 01/01/24 - 01/31/24"
        patterns = [
            r'statement period[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s*[\-–—]\s*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'billing period[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\s+to\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'statement date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    'start_date': match.group(1),
                    'end_date': match.group(2) if len(match.groups()) > 1 else match.group(1)
                }
        return {'start_date': None, 'end_date': None}
    
    def extract_due_date_citi(self, text: str) -> Optional[str]:
        """Extract payment due date from Citibank statement"""
        # Citi format: "Payment Due Date: 02/25/24"
        patterns = [
            r'payment due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'due date[:\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
            r'minimum payment due[:\s]+\$[^:]+:[\s]+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_card_last_4_citi(self, text: str) -> Optional[str]:
        """Extract card last 4 digits from Citibank statement"""
        # Citi format: "xxxx xxxx xxxx 1234" or "Account ending 1234"
        patterns = [
            r'(?:card ending|account ending)[:\s#]*(\d{4})',
            r'xxxx[-\s]*xxxx[-\s]*xxxx[-\s]*(\d{4})',
            r'\*{4}\s*\*{4}\s*\*{4}\s*(\d{4})',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None
    
    def extract_total_balance_citi(self, text: str) -> Optional[float]:
        """Extract total balance from Citibank statement"""
        # Citi format: "NEW BALANCE $1,234.56"
        patterns = [
            r'new balance[:\s]+\$?([\d,]+\.?\d*)',
            r'total balance[:\s]+\$?([\d,]+\.?\d*)',
            r'current balance[:\s]+\$?([\d,]+\.?\d*)',
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None
    
    def extract_transactions_citi(self, pdf_path: str, verbose: bool = False) -> list:
        """Extract transactions from Citibank statement"""
        transactions = []
        try:
            tables = self.extract_tables(pdf_path)
            
            for table in tables:
                if not table or len(table) < 2:
                    continue
                
                header_row = None
                for i, row in enumerate(table[:3]):
                    if row and any(keyword in ' '.join([str(cell) for cell in row if cell]).lower() 
                                   for keyword in ['date', 'description', 'amount']):
                        header_row = i
                        break
                
                if header_row is not None:
                    for row in table[header_row + 1:]:
                        if row and len(row) >= 3:
                            try:
                                date_str = str(row[0]).strip() if row[0] else None
                                desc = ' '.join([str(cell).strip() for cell in row[1:-1] if cell]) if len(row) > 2 else None
                                amount_str = str(row[-1]).strip() if row[-1] else None
                                
                                if date_str and desc and amount_str:
                                    amount = self._clean_amount(amount_str)
                                    if amount and amount != 0:
                                        transactions.append({
                                            'date': date_str,
                                            'description': desc,
                                            'amount': amount
                                        })
                            except Exception:
                                continue
                    if transactions:
                        break
            
            if not transactions:
                text = self.extract_text(pdf_path)
                lines = text.split('\n')
                for line in lines:
                    match = re.search(r'(\d{1,2}[\/\-]\d{1,2})', line)
                    if match:
                        amount_match = re.search(r'\$\s*([\d,]+\.?\d{2})', line)
                        if amount_match:
                            transactions.append({
                                'date': match.group(1),
                                'description': line[:100],
                                'amount': float(amount_match.group(1).replace(',', ''))
                            })
        except Exception as e:
            if verbose:
                print(f"Error extracting transactions: {e}")
        
        return transactions[:50]
    
    def _clean_amount(self, amount_str: str) -> Optional[float]:
        """Clean and parse amount string"""
        try:
            amount_str = amount_str.replace('$', '').replace(',', '').strip()
            if amount_str.startswith('(') and amount_str.endswith(')'):
                amount_str = '-' + amount_str[1:-1]
            return float(amount_str)
        except ValueError:
            return None

