# Author(s): Sepehr Vahedi, Helia Akhtarkavian
# Student ID(s): 99170615, 98170657

import sys
import os
import argparse
from scanner import Scanner
from parser import Parser

class Token:
    """Simple token class to store token information."""
    def __init__(self, token_type, lexeme, lineno):
        self.token_type = token_type
        self.lexeme = lexeme
        self.lineno = lineno

def main():
    """Main entry point for the compiler."""
    # Parse command-line arguments
    arg_parser = argparse.ArgumentParser(description='C-minus Compiler')
    arg_parser.add_argument('input_file', type=str, help='Path to the input source file')
    arg_parser.add_argument('--output-dir', type=str, default='.', help='Directory for output files')
    arg_parser.add_argument('--verbose', action='store_true', help='Enable verbose output')
    args = arg_parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist.")
        return 1

    # Create output directory if it doesn't exist
    if not os.path.exists(args.output_dir):
        try:
            os.makedirs(args.output_dir)
        except OSError as e:
            print(f"Error: Could not create output directory '{args.output_dir}'. Reason: {e}")
            return 1

    # Read input file
    try:
        with open(args.input_file, 'r', encoding='utf-8') as f:
            source_code = f.read()
    except IOError as e:
        print(f"Error: Could not read input file '{args.input_file}'. Reason: {e}")
        return 1

    # Get base filename (without extension)
    base_filename = os.path.splitext(os.path.basename(args.input_file))[0]

    # Step 1: Lexical Analysis
    if args.verbose:
        print("Starting lexical analysis...")

    scanner = Scanner(source_code)
    tokens = []

    # Collect all tokens from the scanner
    while True:
        token_type, lexeme = scanner.get_next_token()
        tokens.append(Token(token_type, lexeme, scanner.lineno))
        if token_type == 'EOF':
            break

    # Write tokens to file
    tokens_filename = os.path.join(args.output_dir, f"{base_filename}_tokens.txt")
    try:
        with open(tokens_filename, 'w', encoding='utf-8') as f:
            for token in tokens:
                if token.token_type == 'EOF':
                    continue
                f.write(f"{token.lineno}:\t({token.token_type}, {token.lexeme})\n")
    except IOError as e:
        print(f"Error: Could not write tokens to file '{tokens_filename}'. Reason: {e}")

    # Write lexical errors to file
    lexical_errors_filename = os.path.join(args.output_dir, f"{base_filename}_lexical_errors.txt")
    try:
        with open(lexical_errors_filename, 'w', encoding='utf-8') as f:
            if not scanner.errors:
                f.write("There is no lexical error.\n")
            else:
                for error in scanner.errors:
                    lineno, lexeme, message = error
                    f.write(f"{lineno}:\t({lexeme}, {message})\n")
    except IOError as e:
        print(f"Error: Could not write lexical errors to file '{lexical_errors_filename}'. Reason: {e}")

    if args.verbose:
        print(f"Lexical analysis completed. Found {len(tokens)} tokens and {len(scanner.errors)} errors.")
        print(f"Tokens written to '{tokens_filename}'")
        print(f"Lexical errors written to '{lexical_errors_filename}'")

    # Step 2: Syntax Analysis
    if args.verbose:
        print("Starting syntax analysis...")

    parser = Parser(tokens)
    parser.parse()

    # Write parse tree to file
    parse_tree_filename = os.path.join(args.output_dir, f"{base_filename}_parse_tree.txt")
    parser.write_parse_tree(parse_tree_filename)

    # Write syntax errors to file
    syntax_errors_filename = os.path.join(args.output_dir, f"{base_filename}_syntax_errors.txt")
    parser.write_syntax_errors(syntax_errors_filename)

    if args.verbose:
        print(f"Syntax analysis completed. Found {len(parser.errors)} errors.")
        print(f"Parse tree written to '{parse_tree_filename}'")
        print(f"Syntax errors written to '{syntax_errors_filename}'")

    return 0

if __name__ == "__main__":
    sys.exit(main())
