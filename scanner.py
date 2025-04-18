# Author(s): Sepehr Vahedi, Helia Akhtarkavian
# Student ID(s): 99170615, 98170657

import token_types as tt


class Scanner:
    """
    A lexical analyzer (scanner) for the C-minus language.

    Reads an input string (C-minus program) and breaks it down into a sequence
    of tokens, handling whitespace, comments, and basic lexical errors.
    """

    def __init__(self, input_text):
        """
        Initializes the Scanner.

        Args:
            input_text (str): The source code of the C-minus program.
        """
        self.buffer = input_text
        self.current_pos = 0
        self.lineno = 1
        self.symbol_table = tt.KEYWORDS[:]
        self.errors = []
        self._last_token_start_pos = 0

    def _peek(self):
        """Returns the next character without consuming it, or None if EOF."""
        if self.current_pos < len(self.buffer):
            return self.buffer[self.current_pos]
        return None

    def _advance(self):
        """Consumes the next character and advances the position."""
        char = self.buffer[self.current_pos]
        self.current_pos += 1
        if char == '\n':
            self.lineno += 1
        return char

    def _skip_whitespace(self):
        """Skips over any whitespace characters."""
        while True:
            char = self._peek()
            if char is None or char not in tt.WHITESPACE_CHARS:
                break
            self._advance()

    def _skip_comment(self):
        """
        Skips over a block comment (/* ... */).
        Handles unclosed comments at EOF and unmatched '*/'.
        Returns True if a comment was skipped, False otherwise.
        """
        start_char = self._peek()
        if start_char != '/':
            return False

        # Lookahead one character
        if self.current_pos + 1 < len(self.buffer) and self.buffer[self.current_pos + 1] == '*':
            start_line = self.lineno
            start_pos = self.current_pos
            self._advance()
            self._advance()

            comment_content = ""
            while True:
                char = self._peek()
                if char is None:
                    # Unclosed comment at EOF
                    error_str = self.buffer[start_pos:start_pos + 10]
                    if len(error_str) > 9:
                        error_str = error_str[:7] + "..."
                    self._record_error(error_str, "Unclosed comment", start_line)
                    self.current_pos = len(self.buffer)
                    return True

                if char == '*':
                    self._advance()  # Consume '*'
                    next_char = self._peek()
                    if next_char == '/':
                        self._advance()  # Consume '/' - comment successfully closed
                        return True
                    else:
                        if len(comment_content) < 7: comment_content += '*'
                        continue
                else:
                    if len(comment_content) < 7: comment_content += char
                    self._advance()

        return False

    def _handle_number(self):
        """Recognizes and returns a NUM token."""
        start_pos = self.current_pos
        while True:
            char = self._peek()
            # Keep consuming digits
            if char is not None and char.isdigit():
                self._advance()
            else:
                break

        lexeme = self.buffer[start_pos:self.current_pos]

        next_char = self._peek()
        if next_char is not None and next_char.isalpha():
            invalid_char = self._advance()
            error_lexeme = lexeme + invalid_char
            self._record_error(error_lexeme, "Invalid number", self.lineno)
            return (tt.ERROR, error_lexeme)

        return (tt.NUM, lexeme)

    def _handle_identifier_or_keyword(self):
        """
        Recognizes an ID or KEYWORD token, or treats an identifier
        followed immediately by a bad char as one INVALID‐INPUT lexeme.
        """
        start_pos = self.current_pos
        # consume first letter
        self._advance()
        # consume letters/digits
        while True:
            char = self._peek()
            if char is not None and char.isalnum():
                self._advance()
            else:
                break

        lexeme = self.buffer[start_pos:self.current_pos]

        # If next char is neither whitespace nor a known symbol, it's an invalid suffix.
        next_char = self._peek()
        if next_char is not None and \
                next_char not in tt.WHITESPACE_CHARS and \
                next_char not in tt.SYMBOLS:
            # grab that bad char too
            invalid_char = self._advance()
            error_lexeme = lexeme + invalid_char
            self._record_error(error_lexeme, "Invalid input", self.lineno)
            return (tt.ERROR, error_lexeme)

        # Otherwise it's a normal identifier or keyword
        if lexeme in tt.KEYWORDS:
            return (tt.KEYWORD, lexeme)
        else:
            if lexeme not in self.symbol_table:
                self.symbol_table.append(lexeme)
            return (tt.ID, lexeme)

    def _handle_symbol(self):
        """Recognizes SYMBOL tokens, handling lookahead for ==, /*, */."""
        start_pos = self.current_pos
        first_char = self._advance()

        if first_char == '=':
            if self._peek() == '=':
                self._advance()
                return (tt.SYMBOL, '==')
            else:
                return (tt.SYMBOL, '=')
        elif first_char == '*':
            next_char = self._peek()
            # 1) Closing comment “*/”
            if next_char == '/':
                self._advance()
                self._record_error("*/", "Unmatched comment", self.lineno)
                return (tt.ERROR, "*/")
            # 2) The *# case: consume both and emit one error token "*#"
            elif next_char == '#':
                self._advance()                  # consume the '#'
                lexeme = "*#"
                self._record_error(lexeme, "Invalid input", self.lineno)
                return (tt.ERROR, lexeme)
            # 3) Otherwise, it’s just the '*' symbol
            else:
                return (tt.SYMBOL, '*')
        elif first_char == '/':
            return (tt.SYMBOL, '/')

        elif first_char in tt.SYMBOLS:
            if first_char in [';', ':', ',', '(', ')', '[', ']', '{', '}', '+', '-', '<']:
                return (tt.SYMBOL, first_char)
            else:
                self._record_error(first_char, "Invalid input", self.lineno)
                return (tt.ERROR, first_char)  # Discard invalid symbol

        else:
            # If the character consumed wasn't a recognized symbol start
            # This handles characters like '@', '#', etc.
            self._record_error(first_char, "Invalid input", self.lineno)
            return (tt.ERROR, first_char)

    def _record_error(self, error_string, message, lineno):
        """Records a lexical error."""
        if len(error_string) > 7 and message == "Unclosed comment":
            display_string = error_string[:7] + "..."
        else:
            display_string = error_string

        if message == "Unmatched comment" or not self.errors or self.errors[-1] != (lineno, display_string, message):
            self.errors.append((lineno, display_string, message))

    def get_next_token(self):
        """
        Recognizes and returns the next token from the input buffer.

        Skips whitespace and comments. Handles lexical errors using panic mode.

        Returns:
            tuple: A pair (TokenType, TokenString) or (EOF, '$') at end of file.
                   Returns (ERROR, ErrorString) if an error is handled via panic mode,
                   which should typically be skipped by the caller loop in this phase.
        """
        while True:
            self._skip_whitespace()

            if self._skip_comment():
                continue

            self._last_token_start_pos = self.current_pos
            current_char = self._peek()

            if current_char is None:
                return (tt.EOF, '$')

            if current_char.isalpha():
                return self._handle_identifier_or_keyword()

            elif current_char.isdigit():
                token = self._handle_number()
                if token[0] == tt.ERROR:
                    continue
                return token

            # Symbols or potential errors
            elif current_char in tt.SYMBOLS or current_char in ['/', '*']:
                token = self._handle_symbol()
                if token[0] == tt.ERROR:
                    # Error handled (Invalid input, Unmatched comment), loop to continue
                    continue
                return token

            # --- Error Handling for Invalid Input ---
            else:
                # Capture any contiguous alphanumeric chars before the bad char
                start = self.current_pos
                invalid_char = self._advance()
                i = start - 1
                while i >= 0 and (self.buffer[i].isalnum() or self.buffer[i] == '*'):
                    i -= 1
                lexeme = self.buffer[i + 1:self.current_pos]
                self._record_error(lexeme, "Invalid input", self.lineno)
                continue

    def get_errors(self):
        """Returns the list of recorded lexical errors."""
        return self.errors

    def get_symbol_table(self):
        """Returns the final symbol table."""
        return self.symbol_table
