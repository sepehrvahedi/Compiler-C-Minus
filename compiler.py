# Author(s): Sepehr Vahedi, Helia Akhtarkavian
# Student ID(s): 99170615, 98170657

import sys

import token_types as tt
from scanner import Scanner


def write_tokens(tokens_by_line, filename="tokens.txt"):
    """
    Writes the recognized tokens to the specified file, grouped by line number.

    Args:
        tokens_by_line (dict): A dictionary mapping line numbers to lists of (Type, Lexeme) tuples.
        filename (str): The name of the output file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if not tokens_by_line:
                f.write("")
                return

            sorted_lines = sorted(tokens_by_line.keys())

            first_line_written = False
            for lineno in sorted_lines:
                token_pairs = tokens_by_line[lineno]
                token_strings = [f"({token[0]}, {token[1]})" for token in token_pairs]

                if first_line_written:
                    f.write("\n")
                else:
                    first_line_written = True

                f.write(f"{lineno}.\t{' '.join(token_strings)}")
            if first_line_written:
                f.write("\n")

    except IOError as e:
        print(f"Error: Could not write tokens file '{filename}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)


def write_errors(errors, filename="lexical_errors.txt"):
    """
    Writes the lexical errors to the specified file, grouping multiple errors
    on the same line into one output line of the form:
      <lineno>.\t(<lex1>, <msg1>) (<lex2>, <msg2>) …
    and ensures there is no trailing newline after the last line.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            if not errors:
                f.write("There is no lexical error.")
                return

            # sort and group
            errors.sort(key=lambda x: x[0])
            grouped = {}
            for lineno, lexeme, msg in errors:
                grouped.setdefault(lineno, []).append((lexeme, msg))

            lines = sorted(grouped.keys())
            for idx, lineno in enumerate(lines):
                f.write(f"{lineno}.\t")
                pairs = grouped[lineno]
                for lex, msg in pairs:
                    f.write(f"({lex}, {msg}) ")
                if idx < len(lines) - 1:
                    f.write("\n")

    except IOError as e:
        print(f"Error: Could not write errors file '{filename}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)


def write_symbol_table(symbol_table, filename="symbol_table.txt"):
    """
    Writes the symbol table (keywords and identifiers) to the specified file.

    Args:
        symbol_table (list): A list of lexemes (keywords and identifiers).
        filename (str): The name of the output file.
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            first_entry_written = False
            for i, lexeme in enumerate(symbol_table):
                if first_entry_written:
                    f.write("\n")
                else:
                    first_entry_written = True
                f.write(f"{i + 1}.\t{lexeme}")
            if first_entry_written:
                f.write("\n")

    except IOError as e:
        print(f"Error: Could not write symbol table file '{filename}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    input_filename = "input.txt"
    tokens_filename = "tokens.txt"
    errors_filename = "lexical_errors.txt"
    symbol_table_filename = "symbol_table.txt"

    try:
        with open(input_filename, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file '{input_filename}' not found.", file=sys.stderr)
        open(tokens_filename, 'w').close()
        open(errors_filename, 'w').write("There is no lexical error.")
        open(symbol_table_filename, 'w').close()
        sys.exit(1)
    except IOError as e:
        print(f"Error: Could not read input file '{input_filename}'. Reason: {e}", file=sys.stderr)
        sys.exit(1)

    scanner = Scanner(input_text)

    tokens_by_line = {}
    current_line_tokens = []
    last_token_line = 0

    while True:
        token_type, token_lexeme = scanner.get_next_token()
        token_start_line = scanner.lineno

        if token_type == tt.COMMENT or token_type == tt.WHITESPACE or token_type == tt.ERROR:
            continue

        if token_type == tt.EOF:
            if current_line_tokens:
                tokens_by_line.setdefault(last_token_line, []).extend(current_line_tokens)
            break

        # Process valid tokens
        # When we hit a new line, flush previous line's tokens
        if token_start_line != last_token_line:
            if current_line_tokens:
                tokens_by_line.setdefault(last_token_line, []).extend(current_line_tokens)
            current_line_tokens = []
            last_token_line = token_start_line

        current_line_tokens.append((token_type, token_lexeme))

    write_tokens(tokens_by_line, tokens_filename)
    write_errors(scanner.get_errors(), errors_filename)
    write_symbol_table(scanner.get_symbol_table(), symbol_table_filename)


if __name__ == "__main__":
    main()
