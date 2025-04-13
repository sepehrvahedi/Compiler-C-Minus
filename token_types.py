EOF = 'EOF'

# Reserved Keywords
KEYWORD = 'KEYWORD'
KEYWORDS = ['if', 'else', 'void', 'int', 'while', 'break', 'return']

# Identifiers: sequences of letters and digits, starting with a letter
ID = 'ID'

# Numbers: sequences of digits
NUM = 'NUM'

# Symbols: Punctuation and operators
SYMBOL = 'SYMBOL'
SYMBOLS = {
    ';': 'SEMICOLON', ',': 'COMMA', ':': 'COLON',
    '(': 'LPAREN', ')': 'RPAREN', '[': 'LBRACKET', ']': 'RBRACKET',
    '{': 'LBRACE', '}': 'RBRACE',
    '+': 'PLUS', '-': 'MINUS', '*': 'MULTIPLY', '/': 'DIVIDE',
    '=': 'ASSIGN', '==': 'EQ', '<': 'LT'
}

COMMENT = 'COMMENT'

WHITESPACE = 'WHITESPACE'

ERROR = 'ERROR'

TOKEN_TYPE_MAP = {
    **{kw: KEYWORD for kw in KEYWORDS},
    **{sym: SYMBOL for sym in SYMBOLS.keys()},
}

LOOKAHEAD_CHARS = {'=', '/', '*'}

WHITESPACE_CHARS = {' ', '\n', '\r', '\t', '\v', '\f'}
