# Author(s): Sepehr Vahedi, Helia Akhtarkavian
# Student ID(s): 99170615, 98170657

from grammar import FOLLOW, PREDICT

class Node:
    """Represents a node in the parse tree."""
    def __init__(self, name, is_terminal=False, lexeme=None):
        self.name = name
        self.is_terminal = is_terminal
        self.lexeme = lexeme
        self.children = []

    def add_child(self, node):
        """Add a child node to this node."""
        self.children.append(node)

    def __str__(self):
        """String representation for a node in the parse tree."""
        if self.is_terminal:
            if self.name == 'EPSILON':
                return 'epsilon'
            if self.name == '$':
                return '$'
            if self.lexeme:
                return f"({self.name}, {self.lexeme})"
            return self.name
        return self.name


class Parser:
    def __init__(self, tokens):
        """
        Initialize the parser with tokens.

        Args:
            tokens: A list of Token objects from the scanner.
        """
        self.tokens = tokens
        self.token_index = 0
        self.current_token = None
        self.current_token_type = None
        self.current_lexeme = None
        self.tokens_processed = 0
        self.errors = []
        self.parse_tree = None
        self.get_next_token()  # Initialize with the first token

    def get_next_token(self):
        """Get the next token from the token list."""
        if self.token_index < len(self.tokens):
            token = self.tokens[self.token_index]
            self.token_index += 1

            # Skip comment and whitespace tokens
            while (self.token_index < len(self.tokens) and
                   (token.token_type == 'COMMENT' or token.token_type == 'WHITESPACE' or token.token_type == 'ERROR')):
                token = self.tokens[self.token_index]
                self.token_index += 1

            self.current_token_type = token.token_type
            self.current_lexeme = token.lexeme

            # Determine the current token based on its type
            if self.current_token_type in ['KEYWORD', 'SYMBOL']:
                self.current_token = self.current_lexeme
            else:
                self.current_token = self.current_token_type

            self.tokens_processed += 1
            return self.current_token, self.current_lexeme
        else:
            # End of tokens
            self.current_token = 'EOF'
            self.current_lexeme = ''
            self.current_token_type = 'EOF'
            return 'EOF', ''

    def match(self, expected_token):
        """
        Match the current token with the expected token.

        Args:
            expected_token: The expected token type or value.

        Returns:
            A Node representing the matched token, or None if there was an error.
        """
        if self.current_token == expected_token:
            matched_node = Node(self.current_token_type, is_terminal=True, lexeme=self.current_lexeme)
            self.get_next_token()
            return matched_node
        else:
            # Error handling: unexpected token
            self.handle_error(expected_token)
            return None

    def handle_error(self, expected_token=None):
        """
        Handle a syntax error using Panic Mode recovery.

        Args:
            expected_token: The expected token if available.
        """
        # Use the line number from the token if available
        if self.token_index > 0 and self.token_index <= len(self.tokens):
            lineno = self.tokens[self.token_index-1].lineno
        else:
            lineno = 0

        column = 0  # We don't have column information in the token

        if self.current_token == 'EOF':
            error_message = f"Unexpected EOF"
        elif expected_token:
            error_message = f"Missing '{expected_token}'"
        else:
            error_message = f"Unexpected '{self.current_lexeme}'"

        self.errors.append((lineno, column, error_message))

    def skip_to_synchronizing_set(self, sync_set):
        """
        Skip tokens until a token in the synchronizing set is encountered.

        Args:
            sync_set: A set of tokens to synchronize on.
        """
        while self.current_token != 'EOF' and self.current_token not in sync_set:
            self.get_next_token()

    def write_parse_tree(self, filename):
        """Write the parse tree to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self._print_node(self.parse_tree))
        except IOError as e:
            print(f"Error: Could not write parse tree to file '{filename}'. Reason: {e}")

    def write_syntax_errors(self, filename):
        """Write syntax errors to a file."""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                if not self.errors:
                    f.write("There is no syntax error.")
                else:
                    for line, column, message in self.errors:
                        f.write(f"{line}: {message}\n")
        except IOError as e:
            print(f"Error: Could not write syntax errors to file '{filename}'. Reason: {e}")

    def _print_node(self, node, prefix="", is_last=True):
        """
        Helper method to recursively print a parse tree node and its children,
        using ├── and └── with proper vertical lines and indentation.
        """
        if not node:
            return ""
        connector = "└── " if is_last else "├── "
        result = f"{prefix}{connector}{node}\n"

        # Prepare prefix for children:
        # If this node is last child, add spaces; else add vertical bar
        if is_last:
            new_prefix = prefix + "    "
        else:
            new_prefix = prefix + "│   "

        child_count = len(node.children)
        for i, child in enumerate(node.children):
            last_child = (i == child_count - 1)
            result += self._print_node(child, new_prefix, last_child)

        return result

    def parse(self):
        """
        Start the parsing process.

        Returns:
            The root node of the parse tree.
        """
        self.parse_tree = self.program()
        return self.parse_tree

    def check_predict_set(self, non_terminal, rule_index):
        """
        Check if the current token is in the predict set for a given rule.

        Args:
            non_terminal: The non-terminal symbol.
            rule_index: The index of the rule for the non-terminal.

        Returns:
            True if the current token is in the predict set, False otherwise.
        """
        if non_terminal in PREDICT and rule_index in PREDICT[non_terminal]:
            return self.current_token in PREDICT[non_terminal][rule_index]
        return False

    # Transition diagram methods for each non-terminal in the grammar

    def program(self):
        """Program -> DeclarationList $"""
        node = Node('Program')

        declaration_list_node = self.declaration_list()
        if declaration_list_node:
            node.add_child(declaration_list_node)

        # Check for end of input marker
        if self.current_token == 'EOF':
            endmarker_node = Node('$', is_terminal=True, lexeme='$')
            node.add_child(endmarker_node)
        else:
            self.handle_error("Expected end of input")

        return node


    def declaration_list(self):
        """DeclarationList -> Declaration DeclarationList | EPSILON"""
        node = Node('DeclarationList')

        if self.check_predict_set('DeclarationList', 1):  # First rule
            declaration_node = self.declaration()
            if declaration_node:
                node.add_child(declaration_node)

                declaration_list_node = self.declaration_list()
                if declaration_list_node:
                    node.add_child(declaration_list_node)

        elif self.check_predict_set('DeclarationList', 2):  # EPSILON rule
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['DeclarationList'])

        return node

    def declaration(self):
        """Declaration -> DeclarationInitial DeclarationPrime"""
        node = Node('Declaration')

        declaration_initial_node = self.declaration_initial()
        if declaration_initial_node:
            node.add_child(declaration_initial_node)

            declaration_prime_node = self.declaration_prime()
            if declaration_prime_node:
                node.add_child(declaration_prime_node)

        return node

    def declaration_initial(self):
        """DeclarationInitial -> TypeSpecifier ID"""
        node = Node('DeclarationInitial')

        type_specifier_node = self.type_specifier()
        if type_specifier_node:
            node.add_child(type_specifier_node)

            id_node = self.match('ID')
            if id_node:
                node.add_child(id_node)

        return node

    def declaration_prime(self):
        """DeclarationPrime -> FunDeclarationPrime | VarDeclarationPrime"""
        node = Node('DeclarationPrime')

        if self.check_predict_set('DeclarationPrime', 1):  # FunDeclarationPrime
            fun_declaration_prime_node = self.fun_declaration_prime()
            if fun_declaration_prime_node:
                node.add_child(fun_declaration_prime_node)

        elif self.check_predict_set('DeclarationPrime', 2):  # VarDeclarationPrime
            var_declaration_prime_node = self.var_declaration_prime()
            if var_declaration_prime_node:
                node.add_child(var_declaration_prime_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['DeclarationPrime'])

        return node


    def var_declaration_prime(self):
        """VarDeclarationPrime -> ; | [ NUM ] ;"""
        node = Node('VarDeclarationPrime')

        if self.check_predict_set('VarDeclarationPrime', 1):  # ;
            semicolon_node = self.match(';')
            if semicolon_node:
                node.add_child(semicolon_node)

        elif self.check_predict_set('VarDeclarationPrime', 2):  # [ NUM ] ;
            left_bracket_node = self.match('[')
            if left_bracket_node:
                node.add_child(left_bracket_node)

                num_node = self.match('NUM')
                if num_node:
                    node.add_child(num_node)

                    right_bracket_node = self.match(']')
                    if right_bracket_node:
                        node.add_child(right_bracket_node)

                        semicolon_node = self.match(';')
                        if semicolon_node:
                            node.add_child(semicolon_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['VarDeclarationPrime'])

        return node

    def fun_declaration_prime(self):
        """FunDeclarationPrime -> ( Params ) CompoundStmt"""
        node = Node('FunDeclarationPrime')

        left_paren_node = self.match('(')
        if left_paren_node:
            node.add_child(left_paren_node)

            params_node = self.params()
            if params_node:
                node.add_child(params_node)

                right_paren_node = self.match(')')
                if right_paren_node:
                    node.add_child(right_paren_node)

                    compound_stmt_node = self.compound_stmt()
                    if compound_stmt_node:
                        node.add_child(compound_stmt_node)

        return node

    def type_specifier(self):
        """TypeSpecifier -> int | void"""
        node = Node('TypeSpecifier')

        if self.check_predict_set('TypeSpecifier', 1):  # int
            int_node = self.match('int')
            if int_node:
                node.add_child(int_node)

        elif self.check_predict_set('TypeSpecifier', 2):  # void
            void_node = self.match('void')
            if void_node:
                node.add_child(void_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['TypeSpecifier'])

        return node

    def params(self):
        """Params -> int ID ParamPrime ParamList | void"""
        node = Node('Params')

        if self.check_predict_set('Params', 1):  # int ID ParamPrime ParamList
            int_node = self.match('int')
            if int_node:
                node.add_child(int_node)

                id_node = self.match('ID')
                if id_node:
                    node.add_child(id_node)

                    param_prime_node = self.param_prime()
                    if param_prime_node:
                        node.add_child(param_prime_node)

                        param_list_node = self.param_list()
                        if param_list_node:
                            node.add_child(param_list_node)

        elif self.check_predict_set('Params', 2):  # void
            void_node = self.match('void')
            if void_node:
                node.add_child(void_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Params'])

        return node

    def param_list(self):
        """ParamList -> , Param ParamList | EPSILON"""
        node = Node('ParamList')

        if self.check_predict_set('ParamList', 1):  # , Param ParamList
            comma_node = self.match(',')
            if comma_node:
                node.add_child(comma_node)

                param_node = self.param()
                if param_node:
                    node.add_child(param_node)

                    param_list_node = self.param_list()
                    if param_list_node:
                        node.add_child(param_list_node)

        elif self.check_predict_set('ParamList', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['ParamList'])

        return node

    def param(self):
        """Param -> DeclarationInitial ParamPrime"""
        node = Node('Param')

        declaration_initial_node = self.declaration_initial()
        if declaration_initial_node:
            node.add_child(declaration_initial_node)

            param_prime_node = self.param_prime()
            if param_prime_node:
                node.add_child(param_prime_node)

        return node

    def param_prime(self):
        """ParamPrime -> [ ] | EPSILON"""
        node = Node('ParamPrime')

        if self.check_predict_set('ParamPrime', 1):  # [ ]
            left_bracket_node = self.match('[')
            if left_bracket_node:
                node.add_child(left_bracket_node)

                right_bracket_node = self.match(']')
                if right_bracket_node:
                    node.add_child(right_bracket_node)

        elif self.check_predict_set('ParamPrime', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['ParamPrime'])

        return node

    def compound_stmt(self):
        """CompoundStmt -> { DeclarationList StatementList }"""
        node = Node('CompoundStmt')

        left_brace_node = self.match('{')
        if left_brace_node:
            node.add_child(left_brace_node)

            declaration_list_node = self.declaration_list()
            if declaration_list_node:
                node.add_child(declaration_list_node)

                statement_list_node = self.statement_list()
                if statement_list_node:
                    node.add_child(statement_list_node)

                    right_brace_node = self.match('}')
                    if right_brace_node:
                        node.add_child(right_brace_node)

        return node

    def statement_list(self):
        """StatementList -> Statement StatementList | EPSILON"""
        node = Node('StatementList')

        if self.check_predict_set('StatementList', 1):  # Statement StatementList
            statement_node = self.statement()
            if statement_node:
                node.add_child(statement_node)

                statement_list_node = self.statement_list()
                if statement_list_node:
                    node.add_child(statement_list_node)

        elif self.check_predict_set('StatementList', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['StatementList'])

        return node

    def statement(self):
        """Statement -> ExpressionStmt | CompoundStmt | SelectionStmt | IterationStmt | ReturnStmt"""
        node = Node('Statement')

        if self.check_predict_set('Statement', 1):  # ExpressionStmt
            expression_stmt_node = self.expression_stmt()
            if expression_stmt_node:
                node.add_child(expression_stmt_node)

        elif self.check_predict_set('Statement', 2):  # CompoundStmt
            compound_stmt_node = self.compound_stmt()
            if compound_stmt_node:
                node.add_child(compound_stmt_node)

        elif self.check_predict_set('Statement', 3):  # SelectionStmt
            selection_stmt_node = self.selection_stmt()
            if selection_stmt_node:
                node.add_child(selection_stmt_node)

        elif self.check_predict_set('Statement', 4):  # IterationStmt
            iteration_stmt_node = self.iteration_stmt()
            if iteration_stmt_node:
                node.add_child(iteration_stmt_node)

        elif self.check_predict_set('Statement', 5):  # ReturnStmt
            return_stmt_node = self.return_stmt()
            if return_stmt_node:
                node.add_child(return_stmt_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Statement'])

        return node

    def expression_stmt(self):
        """ExpressionStmt -> Expression ; | break ; | ;"""
        node = Node('ExpressionStmt')

        if self.check_predict_set('ExpressionStmt', 1):  # Expression ;
            expression_node = self.expression()
            if expression_node:
                node.add_child(expression_node)

                semicolon_node = self.match(';')
                if semicolon_node:
                    node.add_child(semicolon_node)

        elif self.check_predict_set('ExpressionStmt', 2):  # break ;
            break_node = self.match('break')
            if break_node:
                node.add_child(break_node)

                semicolon_node = self.match(';')
                if semicolon_node:
                    node.add_child(semicolon_node)

        elif self.check_predict_set('ExpressionStmt', 3):  # ;
            semicolon_node = self.match(';')
            if semicolon_node:
                node.add_child(semicolon_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['ExpressionStmt'])

        return node

    def selection_stmt(self):
        """SelectionStmt -> if ( Expression ) Statement else Statement"""
        node = Node('SelectionStmt')

        if_node = self.match('if')
        if if_node:
            node.add_child(if_node)

            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

                        statement_node = self.statement()
                        if statement_node:
                            node.add_child(statement_node)

                            else_node = self.match('else')
                            if else_node:
                                node.add_child(else_node)

                                statement_node2 = self.statement()
                                if statement_node2:
                                    node.add_child(statement_node2)

        return node

    def iteration_stmt(self):
        """IterationStmt -> while ( Expression ) Statement"""
        node = Node('IterationStmt')

        while_node = self.match('while')
        if while_node:
            node.add_child(while_node)

            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

                        statement_node = self.statement()
                        if statement_node:
                            node.add_child(statement_node)

        return node

    def return_stmt(self):
        """ReturnStmt -> return ReturnStmtPrime"""
        node = Node('ReturnStmt')

        return_node = self.match('return')
        if return_node:
            node.add_child(return_node)

            return_stmt_prime_node = self.return_stmt_prime()
            if return_stmt_prime_node:
                node.add_child(return_stmt_prime_node)

        return node

    def return_stmt_prime(self):
        """ReturnStmtPrime -> ; | Expression ;"""
        node = Node('ReturnStmtPrime')

        if self.check_predict_set('ReturnStmtPrime', 1):  # ;
            semicolon_node = self.match(';')
            if semicolon_node:
                node.add_child(semicolon_node)

        elif self.check_predict_set('ReturnStmtPrime', 2):  # Expression ;
            expression_node = self.expression()
            if expression_node:
                node.add_child(expression_node)

                semicolon_node = self.match(';')
                if semicolon_node:
                    node.add_child(semicolon_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['ReturnStmtPrime'])

        return node

    def expression(self):
        """Expression -> SimpleExpressionZegond | ID B"""
        node = Node('Expression')

        if self.check_predict_set('Expression', 1):  # SimpleExpressionZegond
            simple_expression_zegond_node = self.simple_expression_zegond()
            if simple_expression_zegond_node:
                node.add_child(simple_expression_zegond_node)

        elif self.check_predict_set('Expression', 2):  # ID B
            id_node = self.match('ID')
            if id_node:
                node.add_child(id_node)

                b_node = self.b()
                if b_node:
                    node.add_child(b_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Expression'])

        return node

    def b(self):
        """B -> = Expression | [ Expression ] H | SimpleExpressionPrime"""
        node = Node('B')

        if self.check_predict_set('B', 1):  # = Expression
            assign_node = self.match('=')
            if assign_node:
                node.add_child(assign_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

        elif self.check_predict_set('B', 2):  # [ Expression ] H
            left_bracket_node = self.match('[')
            if left_bracket_node:
                node.add_child(left_bracket_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    right_bracket_node = self.match(']')
                    if right_bracket_node:
                        node.add_child(right_bracket_node)

                        h_node = self.h()
                        if h_node:
                            node.add_child(h_node)

        elif self.check_predict_set('B', 3):  # SimpleExpressionPrime
            simple_expression_prime_node = self.simple_expression_prime()
            if simple_expression_prime_node:
                node.add_child(simple_expression_prime_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['B'])

        return node

    def h(self):
        """H -> = Expression | G D C"""
        node = Node('H')

        if self.check_predict_set('H', 1):  # = Expression
            assign_node = self.match('=')
            if assign_node:
                node.add_child(assign_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

        elif self.check_predict_set('H', 2):  # G D C
            g_node = self.g()
            if g_node:
                node.add_child(g_node)

                d_node = self.d()
                if d_node:
                    node.add_child(d_node)

                    c_node = self.c()
                    if c_node:
                        node.add_child(c_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['H'])

        return node

    def simple_expression_zegond(self):
        """SimpleExpressionZegond -> AdditiveExpressionZegond C"""
        node = Node('SimpleExpressionZegond')

        additive_expression_zegond_node = self.additive_expression_zegond()
        if additive_expression_zegond_node:
            node.add_child(additive_expression_zegond_node)

            c_node = self.c()
            if c_node:
                node.add_child(c_node)

        return node

    def simple_expression_prime(self):
        """SimpleExpressionPrime -> AdditiveExpressionPrime C"""
        node = Node('SimpleExpressionPrime')

        additive_expression_prime_node = self.additive_expression_prime()
        if additive_expression_prime_node:
            node.add_child(additive_expression_prime_node)

            c_node = self.c()
            if c_node:
                node.add_child(c_node)

        return node

    def c(self):
        """C -> Relop AdditiveExpression | EPSILON"""
        node = Node('C')

        if self.check_predict_set('C', 1):  # Relop AdditiveExpression
            relop_node = self.relop()
            if relop_node:
                node.add_child(relop_node)

                additive_expression_node = self.additive_expression()
                if additive_expression_node:
                    node.add_child(additive_expression_node)

        elif self.check_predict_set('C', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['C'])

        return node

    def relop(self):
        """Relop -> < | =="""
        node = Node('Relop')

        if self.check_predict_set('Relop', 1):  # <
            lt_node = self.match('<')
            if lt_node:
                node.add_child(lt_node)

        elif self.check_predict_set('Relop', 2):  # ==
            eq_node = self.match('==')
            if eq_node:
                node.add_child(eq_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Relop'])

        return node

    def additive_expression(self):
        """AdditiveExpression -> Term D"""
        node = Node('AdditiveExpression')

        term_node = self.term()
        if term_node:
            node.add_child(term_node)

            d_node = self.d()
            if d_node:
                node.add_child(d_node)

        return node

    def additive_expression_prime(self):
        """AdditiveExpressionPrime -> TermPrime D"""
        node = Node('AdditiveExpressionPrime')

        term_prime_node = self.term_prime()
        if term_prime_node:
            node.add_child(term_prime_node)

            d_node = self.d()
            if d_node:
                node.add_child(d_node)

        return node

    def additive_expression_zegond(self):
        """AdditiveExpressionZegond -> TermZegond D"""
        node = Node('AdditiveExpressionZegond')

        term_zegond_node = self.term_zegond()
        if term_zegond_node:
            node.add_child(term_zegond_node)

            d_node = self.d()
            if d_node:
                node.add_child(d_node)

        return node

    def d(self):
        """D -> Addop Term D | EPSILON"""
        node = Node('D')

        if self.check_predict_set('D', 1):  # Addop Term D
            addop_node = self.addop()
            if addop_node:
                node.add_child(addop_node)

                term_node = self.term()
                if term_node:
                    node.add_child(term_node)

                    d_node = self.d()
                    if d_node:
                        node.add_child(d_node)

        elif self.check_predict_set('D', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['D'])

        return node

    def addop(self):
        """Addop -> + | -"""
        node = Node('Addop')

        if self.check_predict_set('Addop', 1):  # +
            plus_node = self.match('+')
            if plus_node:
                node.add_child(plus_node)

        elif self.check_predict_set('Addop', 2):  # -
            minus_node = self.match('-')
            if minus_node:
                node.add_child(minus_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Addop'])

        return node

    def term(self):
        """Term -> SignedFactor G"""
        node = Node('Term')

        signed_factor_node = self.signed_factor()
        if signed_factor_node:
            node.add_child(signed_factor_node)

            g_node = self.g()
            if g_node:
                node.add_child(g_node)

        return node

    def term_prime(self):
        """TermPrime -> SignedFactorPrime G"""
        node = Node('TermPrime')

        signed_factor_prime_node = self.signed_factor_prime()
        if signed_factor_prime_node:
            node.add_child(signed_factor_prime_node)

            g_node = self.g()
            if g_node:
                node.add_child(g_node)

        return node

    def term_zegond(self):
        """TermZegond -> SignedFactorZegond G"""
        node = Node('TermZegond')

        signed_factor_zegond_node = self.signed_factor_zegond()
        if signed_factor_zegond_node:
            node.add_child(signed_factor_zegond_node)

            g_node = self.g()
            if g_node:
                node.add_child(g_node)

        return node

    def g(self):
        """G -> * SignedFactor G | EPSILON"""
        node = Node('G')

        if self.check_predict_set('G', 1):  # * SignedFactor G
            multiply_node = self.match('*')
            if multiply_node:
                node.add_child(multiply_node)

                signed_factor_node = self.signed_factor()
                if signed_factor_node:
                    node.add_child(signed_factor_node)

                    g_node = self.g()
                    if g_node:
                        node.add_child(g_node)

        elif self.check_predict_set('G', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['G'])

        return node

    def signed_factor(self):
        """SignedFactor -> + Factor | - Factor | Factor"""
        node = Node('SignedFactor')

        if self.check_predict_set('SignedFactor', 1):  # + Factor
            plus_node = self.match('+')
            if plus_node:
                node.add_child(plus_node)

                factor_node = self.factor()
                if factor_node:
                    node.add_child(factor_node)

        elif self.check_predict_set('SignedFactor', 2):  # - Factor
            minus_node = self.match('-')
            if minus_node:
                node.add_child(minus_node)

                factor_node = self.factor()
                if factor_node:
                    node.add_child(factor_node)

        elif self.check_predict_set('SignedFactor', 3):  # Factor
            factor_node = self.factor()
            if factor_node:
                node.add_child(factor_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['SignedFactor'])

        return node

    def signed_factor_prime(self):
        """SignedFactorPrime -> FactorPrime"""
        node = Node('SignedFactorPrime')

        factor_prime_node = self.factor_prime()
        if factor_prime_node:
            node.add_child(factor_prime_node)

        return node

    def signed_factor_zegond(self):
        """SignedFactorZegond -> + Factor | - Factor | FactorZegond"""
        node = Node('SignedFactorZegond')

        if self.check_predict_set('SignedFactorZegond', 1):  # + Factor
            plus_node = self.match('+')
            if plus_node:
                node.add_child(plus_node)

                factor_node = self.factor()
                if factor_node:
                    node.add_child(factor_node)

        elif self.check_predict_set('SignedFactorZegond', 2):  # - Factor
            minus_node = self.match('-')
            if minus_node:
                node.add_child(minus_node)

                factor_node = self.factor()
                if factor_node:
                    node.add_child(factor_node)

        elif self.check_predict_set('SignedFactorZegond', 3):  # FactorZegond
            factor_zegond_node = self.factor_zegond()
            if factor_zegond_node:
                node.add_child(factor_zegond_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['SignedFactorZegond'])

        return node

    def factor(self):
        """Factor -> ( Expression ) | ID VarCallPrime | NUM"""
        node = Node('Factor')

        if self.check_predict_set('Factor', 1):  # ( Expression )
            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

        elif self.check_predict_set('Factor', 2):  # ID VarCallPrime
            id_node = self.match('ID')
            if id_node:
                node.add_child(id_node)

                var_call_prime_node = self.var_call_prime()
                if var_call_prime_node:
                    node.add_child(var_call_prime_node)

        elif self.check_predict_set('Factor', 3):  # NUM
            num_node = self.match('NUM')
            if num_node:
                node.add_child(num_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Factor'])

        return node

    def var_call_prime(self):
        """VarCallPrime -> ( Args ) | VarPrime"""
        node = Node('VarCallPrime')

        if self.check_predict_set('VarCallPrime', 1):  # ( Args )
            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                args_node = self.args()
                if args_node:
                    node.add_child(args_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

        elif self.check_predict_set('VarCallPrime', 2):  # VarPrime
            var_prime_node = self.var_prime()
            if var_prime_node:
                node.add_child(var_prime_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['VarCallPrime'])

        return node

    def var_prime(self):
        node = Node('VarPrime')

        if self.check_predict_set('VarPrime', 1):  # [ Expression ]
            left_bracket_node = self.match('[')
            node.add_child(left_bracket_node)

            expression_node = self.expression()
            node.add_child(expression_node)

            right_bracket_node = self.match(']')
            node.add_child(right_bracket_node)

        elif self.current_lexeme in FOLLOW['VarPrime']:  # epsilon production
            node.add_child(Node('epsilon', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['VarPrime'])

        return node

    def factor_prime(self):
        """FactorPrime -> ( Args ) | VarPrime"""
        node = Node('FactorPrime')

        if self.check_predict_set('FactorPrime', 1):  # ( Args )
            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                args_node = self.args()
                if args_node:
                    node.add_child(args_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

        elif self.check_predict_set('FactorPrime', 2):  # VarPrime
            var_prime_node = self.var_prime()
            if var_prime_node:
                node.add_child(var_prime_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['FactorPrime'])

        return node

    def factor_zegond(self):
        """FactorZegond -> ( Expression ) | NUM"""
        node = Node('FactorZegond')

        if self.check_predict_set('FactorZegond', 1):  # ( Expression )
            left_paren_node = self.match('(')
            if left_paren_node:
                node.add_child(left_paren_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    right_paren_node = self.match(')')
                    if right_paren_node:
                        node.add_child(right_paren_node)

        elif self.check_predict_set('FactorZegond', 2):  # NUM
            num_node = self.match('NUM')
            if num_node:
                node.add_child(num_node)

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['FactorZegond'])

        return node

    def args(self):
        """Args -> ArgList | EPSILON"""
        node = Node('Args')

        if self.check_predict_set('Args', 1):  # ArgList
            arg_list_node = self.arg_list()
            if arg_list_node:
                node.add_child(arg_list_node)

        elif self.check_predict_set('Args', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['Args'])

        return node

    def arg_list(self):
        """ArgList -> Expression ArgListPrime"""
        node = Node('ArgList')

        expression_node = self.expression()
        if expression_node:
            node.add_child(expression_node)

            arg_list_prime_node = self.arg_list_prime()
            if arg_list_prime_node:
                node.add_child(arg_list_prime_node)

        return node

    def arg_list_prime(self):
        """ArgListPrime -> , Expression ArgListPrime | EPSILON"""
        node = Node('ArgListPrime')

        if self.check_predict_set('ArgListPrime', 1):  # , Expression ArgListPrime
            comma_node = self.match(',')
            if comma_node:
                node.add_child(comma_node)

                expression_node = self.expression()
                if expression_node:
                    node.add_child(expression_node)

                    arg_list_prime_node = self.arg_list_prime()
                    if arg_list_prime_node:
                        node.add_child(arg_list_prime_node)

        elif self.check_predict_set('ArgListPrime', 2):  # EPSILON
            node.add_child(Node('EPSILON', is_terminal=True))

        else:
            self.handle_error()
            self.skip_to_synchronizing_set(FOLLOW['ArgListPrime'])

        return node

    def generate_parse_tree_text(self, node=None, depth=0):
        """
        Generate a textual representation of the parse tree.

        Args:
            node: The current node being processed.
            depth: The current depth in the tree.

        Returns:
            A list of strings representing the parse tree.
        """
        if node is None:
            node = self.parse_tree

        result = []
        indent = '│  ' * depth

        if node.is_terminal:
            if node.lexeme and node.name != 'EPSILON':
                result.append(f"{indent}├─ {node.name}: {node.lexeme}")
            else:
                result.append(f"{indent}├─ {node.name}")
        else:
            result.append(f"{indent}├─ {node.name}")

            for child in node.children:
                result.extend(self.generate_parse_tree_text(child, depth + 1))

        return result
