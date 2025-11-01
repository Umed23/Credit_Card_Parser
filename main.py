"""
Main entry point for the Credit Card Statement Parser
Command-line interface for parsing credit card statements
"""

import argparse
import json
import sys
import os
from pathlib import Path
from termcolor import colored
from parser import CreditCardStatementParser

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul')


def print_header():
    """Print application header"""
    print(colored("=" * 70, "cyan"))
    print(colored("Credit Card Statement Parser", "cyan", attrs=['bold']))
    print(colored("Supporting: Chase, Capital One, Citibank, Amex, Discover", "cyan"))
    print(colored("=" * 70, "cyan"))
    print()


def print_result(result: dict, verbose: bool = False):
    """
    Print parsed results in a formatted way
    
    Args:
        result: Dictionary containing parsed data
        verbose: Enable verbose output
    """
    if not result:
        print(colored("[X] Failed to parse statement", "red"))
        return
    
    print(colored("[SUCCESS] Successfully parsed statement", "green"))
    print()
    
    # Print issuer
    if 'issuer' in result:
        print(colored(f"Issuer: {result['issuer']}", "yellow", attrs=['bold']))
    
    # Print billing cycle
    if 'billing_cycle' in result and result['billing_cycle']:
        bc = result['billing_cycle']
        if bc.get('start_date') and bc.get('end_date'):
            print(colored("Billing Cycle:", "white", attrs=['bold']), 
                  f"{bc['start_date']} - {bc['end_date']}")
        elif bc.get('start_date'):
            print(colored("Statement Date:", "white", attrs=['bold']), bc['start_date'])
    
    # Print payment due date
    if 'payment_due_date' in result and result['payment_due_date']:
        print(colored("Payment Due Date:", "white", attrs=['bold']), 
              result['payment_due_date'])
    
    # Print card last 4 digits
    if 'card_last_4' in result and result['card_last_4']:
        print(colored("Card Last 4 Digits:", "white", attrs=['bold']), 
              f"**** **** **** {result['card_last_4']}")
    
    # Print total balance
    if 'total_balance' in result and result['total_balance'] is not None:
        print(colored("Total Balance:", "white", attrs=['bold']), 
              f"${result['total_balance']:,.2f}")
    
    # Print transactions summary
    if 'transactions' in result and result['transactions']:
        print(colored(f"Transactions Found: {len(result['transactions'])}", 
                      "white", attrs=['bold']))
        
        if verbose and result['transactions']:
            print()
            print(colored("Recent Transactions:", "yellow", attrs=['bold']))
            print("-" * 70)
            for i, tx in enumerate(result['transactions'][:10], 1):
                amount = tx.get('amount', 0)
                color = "red" if amount < 0 else "green"
                print(f"{i}. {tx.get('date', 'N/A')} - {tx.get('description', 'N/A')[:40]}")
                print(f"   {colored(f'${abs(amount):,.2f}', color)}")
            if len(result['transactions']) > 10:
                print(f"\n... and {len(result['transactions']) - 10} more transactions")
    
    print()


def export_json(result: dict, output_path: str):
    """
    Export parsed results to JSON file
    
    Args:
        result: Dictionary containing parsed data
        output_path: Path to output JSON file
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        print(colored(f"[SUCCESS] Results exported to: {output_path}", "green"))
    except Exception as e:
        print(colored(f"[X] Failed to export JSON: {e}", "red"))


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Parse credit card statements from multiple issuers',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --file statement.pdf
  %(prog)s --file statement1.pdf statement2.pdf
  %(prog)s --file statement.pdf --verbose
  %(prog)s --file statement.pdf --output results.json
        """
    )
    
    parser.add_argument(
        '--file', '-f',
        nargs='+',
        required=True,
        help='Path(s) to credit card statement PDF file(s)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output with detailed information'
    )
    
    parser.add_argument(
        '--output', '-o',
        help='Export results to JSON file'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    args = parser.parse_args()
    
    # Initialize parser
    statement_parser = CreditCardStatementParser()
    
    # Process each file
    results = []
    for file_path in args.file:
        if not Path(file_path).exists():
            print(colored(f"[X] File not found: {file_path}", "red"))
            continue
        
        print_header()
        print(colored(f"Processing: {file_path}", "cyan"))
        print()
        
        # Parse statement
        result = statement_parser.parse(file_path, verbose=args.verbose)
        results.append(result)
        
        # Print results
        print_result(result, verbose=args.verbose)
        
        # Export if requested
        if args.output and result:
            output_path = args.output if len(args.file) == 1 else f"{args.output}.{Path(file_path).stem}.json"
            export_json(result, output_path)
    
    # Summary
    if len(results) > 1:
        successful = sum(1 for r in results if r)
        print(colored("=" * 70, "cyan"))
        print(colored(f"Summary: {successful}/{len(results)} statements parsed successfully", 
                      "cyan" if successful == len(results) else "yellow"))
        print(colored("=" * 70, "cyan"))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(colored("\n\nInterrupted by user", "yellow"))
        sys.exit(0)
    except Exception as e:
        print(colored(f"\n\nUnexpected error: {e}", "red"))
        sys.exit(1)

