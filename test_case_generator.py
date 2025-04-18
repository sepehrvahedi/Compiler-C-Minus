import os
import random

# Define the target directory for test cases
TEST_CASE_DIR = "test_cases"

# Define C-minus keywords and symbols (should match token_types.py)
KEYWORDS = ["else", "if", "int", "return", "void", "while"]
SYMBOLS = [
    "+", "-", "*", "/", "<", "<=", ">", ">=", "==", "!=", "=", ";", ",",
    "(", ")", "[", "]", "{", "}"
]
# Note: Assuming C-minus does NOT support single quotes for chars,
# C-style line comments //, or other advanced C features.

def write_test_case(filename, content, description=""):
    """Helper function to write content to a test file."""
    filepath = os.path.join(TEST_CASE_DIR, filename)
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            # Add description as a comment at the top of the test file itself
            if description:
                f.write(f"/*\n * Test Case Description:\n * {description}\n */\n")
            f.write(content)
        print(f"Generated: {filepath} ({description or 'No description'})")
    except IOError as e:
        print(f"Error writing {filepath}: {e}", file=sys.stderr)

def generate_test_suite():
    """Generates a suite of test case files."""
    if not os.path.exists(TEST_CASE_DIR):
        os.makedirs(TEST_CASE_DIR)
        print(f"Created directory: {TEST_CASE_DIR}")

    test_cases = [] # List to hold (filename, content, description) tuples

    # --- Test Case Definitions ---

    # 01: Basic Valid Program Snippet
    test_cases.append((
        "01_basic_valid.txt",
        """
int main(void) {
    int count = 0;
    int threshold = 10;
    /* Check if count is less than threshold */
    if (count < threshold) {
        count = count + 1;
    } else {
        // C-style comment (might be invalid depending on spec)
        // Let's assume /* */ only for C-minus
        count = 0; /* Reset count */
    }
    return count;
}
        """,
        "Basic valid C-minus snippet with keywords, IDs, numbers, symbols, comments, and whitespace."
    ))

    # 02: All Keywords
    test_cases.append((
        "02_all_keywords.txt",
        f"{' '.join(KEYWORDS)}\n" + \
        f"int check_{KEYWORDS[0]}(void);\n" + \
        f"void setup_{KEYWORDS[1]}(int val);\n" + \
        f"{KEYWORDS[2]} process_{KEYWORDS[3]}(int x);\n" + \
        f"while(a < 5) return; \n", # Using some keywords in context
        "Tests recognition of all defined keywords, used individually and within simple constructs."
    ))

    # 03: All Symbols
    test_cases.append((
        "03_all_symbols.txt",
        f"{' '.join(SYMBOLS)}\n" + \
        "a = b + c - d * e / f;\n" + \
        "g = (h[1] == i[2]);\n" + \
        "if(j < k <= l > m >= n != o)\n {p, q};",
        "Tests recognition of all defined single and double character symbols."
    ))

    # 04: Whitespace Variations
    test_cases.append((
        "04_whitespace.txt",
        "int\t   main ( void )\n{\nreturn\t0 ; }",
        "Tests handling of various whitespace (spaces, tabs, newlines) between tokens."
    ))

    # 05: Comment Variations
    test_cases.append((
        "05_comments.txt",
        """
int main(void) { /* Start comment */
    int x = 5; /* Mid-line comment */
    /* Multi-line
       comment test */
    int y = 10;/**/ /*Empty comment*/
    return x /* Comment before symbol */ + /* Comment between symbols */ y;
}/* Comment at EOF */
        """,
        "Tests various comment placements: start/mid/end of line, multi-line, empty, adjacent to tokens."
    ))

    # 06: Identifier Variations
    test_cases.append((
        "06_identifiers.txt",
        "int a;\nint A;\nint a1;\nint longIdentifierName123;\nint _underscoreStart; /* Assuming IDs can start with _ */\nint main;",
        "Tests different valid identifiers: short, long, mixed case, with numbers. Assumes '_' allowed.",
        # Note: Adjust if C-minus spec restricts ID format (e.g., no leading underscore)
    ))
    # If leading underscore is NOT allowed by your spec, remove/comment out that line/test case.

    # 07: Number Variations
    test_cases.append((
        "07_numbers.txt",
        "int x = 0;\nint y = 1;\nint z = 12345;\nint w = 007; /* Octal usually not distinct lexically */",
        "Tests valid integer numbers: zero, single digit, multiple digits."
        # Note: C-minus usually doesn't support float, hex, octal distinctly at lexer level.
    ))

    # 08: Empty File
    test_cases.append((
        "08_empty.txt",
        "",
        "Tests handling of an completely empty input file."
    ))

    # 09: Whitespace Only File
    test_cases.append((
        "09_whitespace_only.txt",
        "  \n\t  \n \n\t",
        "Tests handling of a file containing only whitespace characters."
    ))

    # 10: Comment Only File
    test_cases.append((
        "10_comment_only.txt",
        "/* This is the only content in the file. */",
        "Tests handling of a file containing only a valid comment."
    ))

    # --- Error Cases ---

    # 11: Invalid Character Error
    test_cases.append((
        "11_error_invalid_char.txt",
        """
int main(void) {
    int val = 5;
    val = val + @; /* Invalid character @ */
    int result#;    /* Invalid character # */
    return $;     /* Invalid character $ */
}
        """,
        "Tests detection of invalid characters that cannot start or be part of any valid token."
    ))

    # 12: Unterminated Comment Error (at EOF)
    test_cases.append((
        "12_error_unterminated_comment_eof.txt",
        """
int main(void) {
    int x = 1; /* This comment starts but never ends...
        """,
        "Tests detection of a comment block that is not closed before the end of the file."
    ))

    # 13: Unterminated Comment Error (mid-file)
    test_cases.append((
        "input.txt",
        """
int main(void) {
    /* Start of an unclosed comment.
    int x = 5;
    return x;
    /* This code should ideally be reachable if error recovery works well */
    int y = 10;
    return y;
}
        """,
        "Tests detection of an unterminated comment followed by more code (tests error recovery)."
    ))

    # 14: Invalid Number Formation (if applicable) - Often caught as NUM then ID or Error
    # C-minus usually just has INTs. An invalid sequence like `12a` might be tokenized
    # as NUM(12) then ID(a), which is syntactically wrong but lexically potentially okay.
    # Let's focus on characters that are simply invalid.
    # If your scanner specifically flags things like `a1` as an invalid ID, add that test.
    test_cases.append((
        "input.txt",
        """
int main(void) {
    int a = 1a; /* Should be NUM(1) ID(a) or error depending on spec */
    int b = ==; /* Should be SYMBOL(==) SYMBOL(=) or maybe just SYMBOL(==)? */
    b = !=!;    /* Should be SYMBOL(!=) followed by error(!) or SYMBOL(!=) SYMBOL(!) ? */
    a = / *b;   /* SYMBOL(/) SYMBOL(*) ID(b) - space matters! */
    a = /*b;    /* Comment start then ID */
    return 0;
}
        """,
        "Tests potentially ambiguous sequences or adjacent operators/errors."
    ))

    # 15: Complex Mix
    test_cases.append((
        "input.txt",
        """
void process(int data[], int size) {
    int i = 0; /* counter */
    int sum = 0;
    while (i < size /* && data[i] != 0 - this part commented out */) {
        if (data[i] > 0) { /* process positive */
            sum = sum + data[i];
        } /* else { ignore negative/zero } */
        i = i + 1;
    }
    /* Error test: $ */
    if (sum > @100) return; /* Invalid char + number */
    /* Unterminated comment test:
} """,
        "A more complex mix of valid code, comments, and embedded lexical errors (invalid char, unterminated comment)."
    ))

    # --- Generate the files ---
    for filename, content, description in test_cases:
        write_test_case(filename, content.strip(), description) # strip() removes leading/trailing whitespace from multiline strings

    print(f"\nSuccessfully generated {len(test_cases)} test case files in '{TEST_CASE_DIR}'.")

if __name__ == "__main__":
    generate_test_suite()
