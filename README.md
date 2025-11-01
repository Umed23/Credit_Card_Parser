# Credit Card Statement Parser

A comprehensive PDF parser that extracts key data points from credit card statements across 5 major credit card issuers.

## Supported Credit Card Issuers

1. **Chase Bank**
2. **Capital One**
3. **Citibank (Citi)**
4. **American Express (Amex)**
5. **Discover Financial Services**

## Extracted Data Points

For each credit card statement, the parser extracts the following 5 key data points:

1. **Billing Cycle** - Start and end dates of the billing period
2. **Payment Due Date** - Date by which payment must be received
3. **Card Last 4 Digits** - Last four digits of the credit card number
4. **Total Balance** - Current outstanding balance on the account
5. **Transactions** - List of all transactions with date, description, and amount

## Installation

1. Clone this repository:
```bash
git clone https://github.com/Umed23/Credit_Card_Parser.git
cd Credit_Card_Parser
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Parse a single credit card statement:
```bash
python main.py --file path/to/statement.pdf
```

Parse multiple statements:
```bash
python main.py --file statement1.pdf statement2.pdf statement3.pdf
```

View detailed output:
```bash
python main.py --file statement.pdf --verbose
```

Export results to JSON:
```bash
python main.py --file statement.pdf --output results.json
```

### Programmatic Usage

```python
from parser import CreditCardStatementParser

# Initialize parser
parser = CreditCardStatementParser()

# Parse a statement
result = parser.parse('path/to/statement.pdf')

# Access extracted data
print(f"Billing Cycle: {result['billing_cycle']}")
print(f"Due Date: {result['payment_due_date']}")
print(f"Card Number: **** **** **** {result['card_last_4']}")
print(f"Total Balance: {result['total_balance']}")
print(f"Number of Transactions: {len(result['transactions'])}")
```

## Architecture

The parser is built using a modular architecture:

- **`main.py`** - Entry point and CLI interface
- **`parser.py`** - Main orchestrator that identifies issuer and routes to appropriate parser
- **`parsers/`** - Directory containing issuer-specific parsers
  - `chase_parser.py` - Chase Bank statement parser
  - `capital_one_parser.py` - Capital One statement parser
  - `citi_parser.py` - Citibank statement parser
  - `amex_parser.py` - American Express statement parser
  - `discover_parser.py` - Discover statement parser

## Technical Approach

The parser uses multiple techniques to ensure robust extraction:

1. **PDF Text Extraction** - Using `pdfplumber` and `pypdf` libraries
2. **Pattern Matching** - Regular expressions for identifying key fields
3. **Table Extraction** - Using `tabula-py` for transaction tables
4. **Layout Analysis** - Intelligent text positioning and section detection
5. **Multiple Fallback Methods** - If one extraction method fails, others are attempted

## Features

- ✅ Support for 5 major credit card issuers
- ✅ Robust extraction of 5 key data points
- ✅ Error handling and validation
- ✅ Multiple PDF parsing strategies
- ✅ Detailed logging and verbose output
- ✅ Clean, structured output (JSON-ready)
- ✅ Command-line and programmatic interfaces

## Output Format

The parser returns structured data in the following format:

```json
{
  "issuer": "Chase",
  "billing_cycle": {
    "start_date": "2024-01-01",
    "end_date": "2024-01-31"
  },
  "payment_due_date": "2024-02-25",
  "card_last_4": "1234",
  "total_balance": 1250.75,
  "transactions": [
    {
      "date": "2024-01-15",
      "description": "Purchase at AMAZON.COM",
      "amount": 49.99
    }
  ]
}
```

## Limitations

- Requires text-based PDFs (not scanned images)
- Statement formats may vary between issuers over time
- Some edge cases in formatting may require manual verification

## Future Enhancements

- Support for additional credit card issuers
- OCR capabilities for scanned PDFs
- Export to CSV/Excel formats
- Web interface for statement upload
- Batch processing capabilities

## License

This project is provided for educational purposes.

## Author

Credit Card Statement Parser - Assignment Submission
