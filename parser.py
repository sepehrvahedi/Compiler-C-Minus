# Sepehr Vahedi
# 99170615

from enum import Enum
from types import DynamicClassAttribute

from anytree import Node

from symbols import ActionSymbols, CheckSymbols
from lexer import Lexer
from intermediate_code_generator.expression_processor import CodeGenerator



class Parser:
    def __init__(self, lexer: Lexer, code_generator: CodeGenerator):
        self.lexer = lexer
        self.code_generator = code_generator
        self.__current_token = None
        self.__lookahead = None
        self.node = Node(start_symbol.name)
        self.stack = [start_symbol]
        create_parsing_table()

    def __get_token(self):
        self.__current_token = self.lexer.get_next_token()
        if self.__current_token.type in ['KEYWORD', 'SYMBOL', 'END']:
            la = self.__current_token.lexeme
        else:
            la = self.__current_token.type
        self.__lookahead = Terminals.get_enum_by_content(la)

    def parse(self):
        is_running = True
        nodes = [self.node]
        self.__get_token()
        while self.stack and is_running:
            top = self.stack[-1]
            if type(top) is ActionSymbols:
                self.code_generator.code_gen(top, self.__current_token)
                self.stack.pop()
            elif type(top) is CheckSymbols:
                self.code_generator.semantic_check(top, self.__current_token)
                self.stack.pop()
            elif type(top) is Terminals:
                if top == Terminals.EPSILON:
                    self.stack.pop()
                    node = nodes.pop(0)
                    node.name = Terminals.EPSILON.content
                elif top == self.__lookahead:
                    self.stack.pop()
                    node = nodes.pop(0)
                    node.name = '(' + self.__current_token.type + ', ' + self.__current_token.lexeme + ')'
                    self.__get_token()
                else:
                    report_syntax_error(self.__current_token.line_number, f'missing {top.content}')
                    self.stack.pop()
                    node = nodes.pop(0)
                    node.parent = None
            else:
                action = ll1_table[top.name][self.__lookahead.name]
                if action is None:
                    if self.__lookahead == Terminals.DOLLAR:
                        report_syntax_error(self.__current_token.line_number, f'Unexpected EOF')
                        is_running = False
                        for node in nodes:
                            node.parent = None
                    else:
                        report_syntax_error(self.__current_token.line_number, f'illegal {self.__lookahead.content}')
                        self.__get_token()
                elif type(action) is str:
                    report_syntax_error(self.__current_token.line_number, f'missing {top.name}')
                    self.stack.pop()
                    node = nodes.pop(0)
                    node.parent = None
                else:
                    new_node = nodes.pop(0)
                    new_nodes = []
                    for variable in action:
                        if type(variable) is not Terminals and type(variable) is not NonTerminals:
                            continue
                        new_nodes.append(Node(variable.name, parent=new_node))
                    nodes = new_nodes + nodes
                    self.stack.pop()
                    self.stack += action[::-1]
        if is_running:
            Node(Terminals.DOLLAR.content, self.node)
        if self.code_generator.is_erroneous:
            self.code_generator.program_block = []


class Terminals(Enum):
    NUM = 'NUM'
    ID = 'ID'
    IF = 'if'
    ELSE = 'else'
    ENDIF = 'endif'
    VOID = 'void'
    INT = 'int'
    WHILE = 'while'
    BREAK = 'break'
    RETURN = 'return'
    SEMICOLON = ';'
    COLON = ':'
    COMMA = ','
    BRACKET_OPEN = '['
    BRACKET_CLOSE = ']'
    PARENTHESIS_OPEN = '('
    PARENTHESIS_CLOSE = ')'
    BRACE_OPEN = '{'
    BRACE_CLOSE = '}'
    PLUS = '+'
    MINUS = '-'
    STAR = '*'
    ASSIGN = '='
    LESS_THAN = '<'
    EQUAL = '=='
    SLASH = '/'
    EPSILON = 'epsilon'
    DOLLAR = '$'

    def __init__(self, value):
        self.content = value

    @classmethod
    def get_enum_by_content(cls, content):
        for t in Terminals:
            if t.content == content:
                return t


class NonTerminals(Enum):
    PROGRAM = (0, [Terminals.INT, Terminals.VOID, Terminals.EPSILON],
               [Terminals.DOLLAR])
    DECLARATION_LIST = (1, [Terminals.INT, Terminals.VOID, Terminals.EPSILON],
                        [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                         Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.WHILE,
                         Terminals.RETURN, Terminals.PLUS, Terminals.MINUS, Terminals.DOLLAR])
    DECLARATION = (2, [Terminals.INT, Terminals.VOID],
                   [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.INT,
                    Terminals.VOID, Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF,
                    Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS, Terminals.DOLLAR])
    DECLARATION_INITIAL = (3, [Terminals.INT, Terminals.VOID],
                           [Terminals.SEMICOLON, Terminals.BRACKET_OPEN, Terminals.PARENTHESIS_OPEN,
                            Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    DECLARATION_PRIME = (4, [Terminals.SEMICOLON, Terminals.BRACKET_OPEN, Terminals.PARENTHESIS_OPEN],
                         [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.INT,
                          Terminals.VOID, Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF,
                          Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS, Terminals.DOLLAR])
    VAR_DECLARATION_PRIME = (5, [Terminals.SEMICOLON, Terminals.BRACKET_OPEN],
                             [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                              Terminals.INT, Terminals.VOID, Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE,
                              Terminals.BREAK, Terminals.IF, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS,
                              Terminals.MINUS, Terminals.DOLLAR])
    FUN_DECLARATION_PRIME = (6, [Terminals.PARENTHESIS_OPEN],
                             [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                              Terminals.INT, Terminals.VOID, Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE,
                              Terminals.BREAK, Terminals.IF, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS,
                              Terminals.MINUS, Terminals.DOLLAR])
    TYPE_SPECIFIER = (7, [Terminals.INT, Terminals.VOID],
                      [Terminals.ID])
    PARAMS = (8, [Terminals.INT, Terminals.VOID],
              [Terminals.PARENTHESIS_CLOSE])
    PARAM_LIST = (9, [Terminals.COMMA, Terminals.EPSILON],
                  [Terminals.PARENTHESIS_CLOSE])
    PARAM = (10, [Terminals.INT, Terminals.VOID],
             [Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    PARAM_PRIME = (11, [Terminals.BRACKET_OPEN, Terminals.EPSILON],
                   [Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    COMPOUND_STMT = (12, [Terminals.BRACE_OPEN],
                     [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.INT,
                      Terminals.VOID, Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF,
                      Terminals.ENDIF, Terminals.ELSE, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS,
                      Terminals.MINUS, Terminals.DOLLAR])
    STATEMENT_LIST = (13, [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                           Terminals.BRACE_OPEN, Terminals.BREAK, Terminals.IF, Terminals.WHILE, Terminals.RETURN,
                           Terminals.PLUS, Terminals.MINUS, Terminals.EPSILON],
                      [Terminals.BRACE_CLOSE])
    STATEMENT = (14,
                 [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.BRACE_OPEN,
                  Terminals.BREAK, Terminals.IF, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS],
                 [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.BRACE_OPEN,
                  Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF, Terminals.ELSE,
                  Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    EXPRESSION_STMT = (15,
                       [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.BREAK,
                        Terminals.PLUS, Terminals.MINUS],
                       [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                        Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF,
                        Terminals.ELSE, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    SELECTION_STMT = (16, [Terminals.IF],
                      [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                       Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF,
                       Terminals.ELSE, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    ELSE_STMT = (17, [Terminals.ENDIF, Terminals.ELSE],
                 [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.BRACE_OPEN,
                  Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF, Terminals.ELSE,
                  Terminals.WHILE,
                  Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    ITERATION_STMT = (18, [Terminals.WHILE],
                      [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                       Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF,
                       Terminals.ELSE, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    RETURN_STMT = (19, [Terminals.RETURN],
                   [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.BRACE_OPEN,
                    Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF, Terminals.ELSE,
                    Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    RETURN_STMT_PRIME = (20,
                         [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS,
                          Terminals.MINUS],
                         [Terminals.ID, Terminals.SEMICOLON, Terminals.NUM, Terminals.PARENTHESIS_OPEN,
                          Terminals.BRACE_OPEN, Terminals.BRACE_CLOSE, Terminals.BREAK, Terminals.IF, Terminals.ENDIF,
                          Terminals.ELSE, Terminals.WHILE, Terminals.RETURN, Terminals.PLUS, Terminals.MINUS])
    EXPRESSION = (21, [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                  [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    B = (22,
         [Terminals.BRACKET_OPEN, Terminals.PARENTHESIS_OPEN, Terminals.ASSIGN, Terminals.LESS_THAN, Terminals.EQUAL,
          Terminals.PLUS, Terminals.MINUS, Terminals.STAR, Terminals.SLASH, Terminals.EPSILON],
         [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    H = (23, [Terminals.ASSIGN, Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
              Terminals.SLASH, Terminals.EPSILON],
         [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    SIMPLE_EXPRESSION_ZEGOND = (24, [Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                                [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE,
                                 Terminals.COMMA])
    SIMPLE_EXPRESSION_PRIME = (25, [Terminals.PARENTHESIS_OPEN, Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS,
                                    Terminals.MINUS, Terminals.STAR, Terminals.SLASH, Terminals.EPSILON],
                               [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE,
                                Terminals.COMMA])
    C = (26, [Terminals.LESS_THAN, Terminals.EQUAL, Terminals.EPSILON],
         [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    RELOP = (27, [Terminals.LESS_THAN, Terminals.EQUAL],
             [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS])
    ADDITIVE_EXPRESSION = (28,
                           [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                           [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA])
    ADDITIVE_EXPRESSION_PRIME = (29,
                                 [Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                                  Terminals.SLASH, Terminals.EPSILON],
                                 [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE,
                                  Terminals.COMMA, Terminals.LESS_THAN, Terminals.EQUAL])
    ADDITIVE_EXPRESSION_ZEGOND = (30, [Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                                  [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE,
                                   Terminals.COMMA, Terminals.LESS_THAN, Terminals.EQUAL])
    D = (31, [Terminals.PLUS, Terminals.MINUS, Terminals.EPSILON],
         [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
          Terminals.LESS_THAN, Terminals.EQUAL])
    ADDOP = (32, [Terminals.PLUS, Terminals.MINUS],
             [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS])
    TERM = (33, [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
            [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
             Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS])
    TERM_PRIME = (34, [Terminals.PARENTHESIS_OPEN, Terminals.STAR, Terminals.SLASH, Terminals.EPSILON],
                  [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                   Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS])
    TERM_ZEGOND = (35, [Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                   [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                    Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS])
    G = (36, [Terminals.STAR, Terminals.SLASH, Terminals.EPSILON],
         [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
          Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS])
    MULOP = (37, [Terminals.STAR, Terminals.SLASH],
             [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS])
    SIGNED_FACTOR = (38, [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                     [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                      Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                      Terminals.SLASH])
    SIGNED_FACTOR_PRIME = (39, [Terminals.PARENTHESIS_OPEN, Terminals.EPSILON],
                           [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                            Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                            Terminals.SLASH])
    SIGNED_FACTOR_ZEGOND = (40, [Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                            [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                             Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                             Terminals.SLASH])
    FACTOR = (41, [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN],
              [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
               Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR, Terminals.SLASH])
    VAR_CALL_PRIME = (42, [Terminals.BRACKET_OPEN, Terminals.PARENTHESIS_OPEN, Terminals.EPSILON],
                      [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                       Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                       Terminals.SLASH])
    VAR_PRIME = (43, [Terminals.BRACKET_OPEN, Terminals.EPSILON],
                 [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                  Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                  Terminals.SLASH])
    FACTOR_PRIME = (44, [Terminals.PARENTHESIS_OPEN, Terminals.EPSILON],
                    [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                     Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                     Terminals.SLASH])
    FACTOR_ZEGOND = (45, [Terminals.NUM, Terminals.PARENTHESIS_OPEN],
                     [Terminals.SEMICOLON, Terminals.BRACKET_CLOSE, Terminals.PARENTHESIS_CLOSE, Terminals.COMMA,
                      Terminals.LESS_THAN, Terminals.EQUAL, Terminals.PLUS, Terminals.MINUS, Terminals.STAR,
                      Terminals.SLASH])
    ARGS = (46,
            [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS,
             Terminals.EPSILON],
            [Terminals.PARENTHESIS_CLOSE])
    ARG_LIST = (47, [Terminals.ID, Terminals.NUM, Terminals.PARENTHESIS_OPEN, Terminals.PLUS, Terminals.MINUS],
                [Terminals.PARENTHESIS_CLOSE])
    ARG_LIST_PRIME = (48, [Terminals.COMMA, Terminals.EPSILON],
                      [Terminals.PARENTHESIS_CLOSE])

    def __init__(self, idx, first, follow):
        self.index = idx
        self.first = first
        self.follow = follow

    @DynamicClassAttribute
    def name(self):
        parts = super(NonTerminals, self).name.lower().split('_')
        return ''.join([part.capitalize() for part in parts])


start_symbol = NonTerminals.PROGRAM


productions = {
    NonTerminals.PROGRAM: [
        [NonTerminals.DECLARATION_LIST, ActionSymbols.END_OF_PROGRAM]],
    NonTerminals.DECLARATION_LIST: [
        [NonTerminals.DECLARATION, NonTerminals.DECLARATION_LIST],
        [Terminals.EPSILON]],
    NonTerminals.DECLARATION: [
        [NonTerminals.DECLARATION_INITIAL, NonTerminals.DECLARATION_PRIME]],
    NonTerminals.DECLARATION_INITIAL: [
        [ActionSymbols.SET_DECLARING, ActionSymbols.PUSH, NonTerminals.TYPE_SPECIFIER, ActionSymbols.UPDATE_TYPE,
         Terminals.ID]],
    NonTerminals.DECLARATION_PRIME: [
        [NonTerminals.FUN_DECLARATION_PRIME],
        [NonTerminals.VAR_DECLARATION_PRIME]],
    NonTerminals.VAR_DECLARATION_PRIME: [
        [ActionSymbols.UPDATE_VAR_ATTRIBUTES, CheckSymbols.VAR_ARR_IS_INT, Terminals.SEMICOLON],
        [Terminals.BRACKET_OPEN, ActionSymbols.UPDATE_ARR_ATTRIBUTES, CheckSymbols.VAR_ARR_IS_INT, Terminals.NUM,
         Terminals.BRACKET_CLOSE, Terminals.SEMICOLON]],
    NonTerminals.FUN_DECLARATION_PRIME: [
        [ActionSymbols.START_FUNCTION, Terminals.PARENTHESIS_OPEN, NonTerminals.PARAMS, Terminals.PARENTHESIS_CLOSE,
         ActionSymbols.UPDATE_FUNC_ATTRIBUTES, NonTerminals.COMPOUND_STMT, ActionSymbols.RETURN_AT_THE_END_OF_FUNCTION,
         ActionSymbols.END_SCOPE]],
    NonTerminals.TYPE_SPECIFIER: [
        [Terminals.INT],
        [Terminals.VOID]],
    NonTerminals.PARAMS: [
        [ActionSymbols.SET_DECLARING, ActionSymbols.PUSH, Terminals.INT, ActionSymbols.UPDATE_TYPE, Terminals.ID,
         NonTerminals.PARAM_PRIME, NonTerminals.PARAM_LIST],
        [Terminals.VOID]],
    NonTerminals.PARAM_LIST: [
        [Terminals.COMMA, NonTerminals.PARAM, NonTerminals.PARAM_LIST],
        [Terminals.EPSILON]],
    NonTerminals.PARAM: [
        [NonTerminals.DECLARATION_INITIAL, NonTerminals.PARAM_PRIME]],
    NonTerminals.PARAM_PRIME: [
        [ActionSymbols.UPDATE_ARR_ATTRIBUTES, CheckSymbols.VAR_ARR_IS_INT, Terminals.BRACKET_OPEN,
         Terminals.BRACKET_CLOSE],
        [ActionSymbols.UPDATE_VAR_ATTRIBUTES, CheckSymbols.VAR_ARR_IS_INT, Terminals.EPSILON]],
    NonTerminals.COMPOUND_STMT: [
        [ActionSymbols.START_SCOPE, Terminals.BRACE_OPEN, NonTerminals.DECLARATION_LIST, NonTerminals.STATEMENT_LIST,
         Terminals.BRACE_CLOSE, ActionSymbols.END_SCOPE]],
    NonTerminals.STATEMENT_LIST: [
        [NonTerminals.STATEMENT, NonTerminals.STATEMENT_LIST],
        [Terminals.EPSILON]],
    NonTerminals.STATEMENT: [
        [NonTerminals.EXPRESSION_STMT],
        [NonTerminals.COMPOUND_STMT],
        [NonTerminals.SELECTION_STMT],
        [NonTerminals.ITERATION_STMT],
        [NonTerminals.RETURN_STMT]],
    NonTerminals.EXPRESSION_STMT: [
        [NonTerminals.EXPRESSION, ActionSymbols.TYPE_POP, ActionSymbols.POP, Terminals.SEMICOLON],
        [CheckSymbols.BREAK_IS_IN_LOOP, Terminals.BREAK, ActionSymbols.BREAK, Terminals.SEMICOLON],
        [Terminals.SEMICOLON]],
    NonTerminals.SELECTION_STMT: [
        [Terminals.IF, Terminals.PARENTHESIS_OPEN, NonTerminals.EXPRESSION, ActionSymbols.TYPE_POP,
         Terminals.PARENTHESIS_CLOSE,
         ActionSymbols.SAVE, NonTerminals.STATEMENT, NonTerminals.ELSE_STMT]],
    NonTerminals.ELSE_STMT: [
        [ActionSymbols.JPF, Terminals.ENDIF],
        [Terminals.ELSE, ActionSymbols.JPF_SAVE, NonTerminals.STATEMENT, ActionSymbols.JP, Terminals.ENDIF]],
    NonTerminals.ITERATION_STMT: [
        [Terminals.WHILE, ActionSymbols.SAVE, ActionSymbols.LABEL, Terminals.PARENTHESIS_OPEN, NonTerminals.EXPRESSION,
         ActionSymbols.TYPE_POP, Terminals.PARENTHESIS_CLOSE, ActionSymbols.WHILE_SAVE, NonTerminals.STATEMENT,
         ActionSymbols.WHILE]],
    NonTerminals.RETURN_STMT: [
        [Terminals.RETURN, NonTerminals.RETURN_STMT_PRIME]],
    NonTerminals.RETURN_STMT_PRIME: [
        [ActionSymbols.RETURN, Terminals.SEMICOLON],
        [NonTerminals.EXPRESSION, ActionSymbols.RETURN_VALUE, ActionSymbols.TYPE_POP, Terminals.SEMICOLON]],
    NonTerminals.EXPRESSION: [
        [NonTerminals.SIMPLE_EXPRESSION_ZEGOND],
        [CheckSymbols.ID_IS_DEFINED, ActionSymbols.PUSH_ID, Terminals.ID, NonTerminals.B]],
    NonTerminals.B: [
        [Terminals.ASSIGN, NonTerminals.EXPRESSION, CheckSymbols.TYPE_MATCH, ActionSymbols.ASSIGN],
        [Terminals.BRACKET_OPEN, NonTerminals.EXPRESSION, Terminals.BRACKET_CLOSE, ActionSymbols.UPDATE_ID,
         NonTerminals.H],
        [NonTerminals.SIMPLE_EXPRESSION_PRIME]],
    NonTerminals.H: [
        [Terminals.ASSIGN, NonTerminals.EXPRESSION, CheckSymbols.TYPE_MATCH, ActionSymbols.ASSIGN],
        [NonTerminals.G, NonTerminals.D, NonTerminals.C]],
    NonTerminals.SIMPLE_EXPRESSION_ZEGOND: [
        [NonTerminals.ADDITIVE_EXPRESSION_ZEGOND, NonTerminals.C]],
    NonTerminals.SIMPLE_EXPRESSION_PRIME: [
        [NonTerminals.ADDITIVE_EXPRESSION_PRIME, NonTerminals.C]],
    NonTerminals.C: [
        [ActionSymbols.PUSH, NonTerminals.RELOP, NonTerminals.ADDITIVE_EXPRESSION, CheckSymbols.TYPE_MATCH,
         ActionSymbols.OPERATION],
        [Terminals.EPSILON]],
    NonTerminals.RELOP: [
        [Terminals.LESS_THAN],
        [Terminals.EQUAL]],
    NonTerminals.ADDITIVE_EXPRESSION: [
        [NonTerminals.TERM, NonTerminals.D]],
    NonTerminals.ADDITIVE_EXPRESSION_PRIME: [
        [NonTerminals.TERM_PRIME, NonTerminals.D]],
    NonTerminals.ADDITIVE_EXPRESSION_ZEGOND: [
        [NonTerminals.TERM_ZEGOND, NonTerminals.D]],
    NonTerminals.D: [
        [ActionSymbols.PUSH, NonTerminals.ADDOP, NonTerminals.TERM, CheckSymbols.TYPE_MATCH, ActionSymbols.OPERATION,
         NonTerminals.D],
        [Terminals.EPSILON]],
    NonTerminals.ADDOP: [
        [Terminals.PLUS],
        [Terminals.MINUS]],
    NonTerminals.TERM: [
        [NonTerminals.SIGNED_FACTOR, NonTerminals.G]],
    NonTerminals.TERM_PRIME: [
        [NonTerminals.SIGNED_FACTOR_PRIME, NonTerminals.G]],
    NonTerminals.TERM_ZEGOND: [
        [NonTerminals.SIGNED_FACTOR_ZEGOND, NonTerminals.G]],
    NonTerminals.G: [
        [ActionSymbols.PUSH, NonTerminals.MULOP, NonTerminals.SIGNED_FACTOR, CheckSymbols.TYPE_MATCH,
         ActionSymbols.OPERATION, NonTerminals.G],
        [Terminals.EPSILON]],
    NonTerminals.MULOP: [
        [Terminals.STAR],
        [Terminals.SLASH]],
    NonTerminals.SIGNED_FACTOR: [
        [Terminals.PLUS, NonTerminals.FACTOR],
        [Terminals.MINUS, NonTerminals.FACTOR, ActionSymbols.NEG],
        [NonTerminals.FACTOR]],
    NonTerminals.SIGNED_FACTOR_PRIME: [
        [NonTerminals.FACTOR_PRIME]],
    NonTerminals.SIGNED_FACTOR_ZEGOND: [
        [Terminals.PLUS, NonTerminals.FACTOR],
        [Terminals.MINUS, NonTerminals.FACTOR, ActionSymbols.NEG],
        [NonTerminals.FACTOR_ZEGOND]],
    NonTerminals.FACTOR: [
        [Terminals.PARENTHESIS_OPEN, NonTerminals.EXPRESSION, Terminals.PARENTHESIS_CLOSE],
        [CheckSymbols.ID_IS_DEFINED, ActionSymbols.PUSH_ID, Terminals.ID, NonTerminals.VAR_CALL_PRIME],
        [ActionSymbols.SAVE_NUM, Terminals.NUM]],
    NonTerminals.VAR_CALL_PRIME: [
        [Terminals.PARENTHESIS_OPEN, NonTerminals.ARGS, Terminals.PARENTHESIS_CLOSE, ActionSymbols.CALL],
        [NonTerminals.VAR_PRIME]],
    NonTerminals.VAR_PRIME: [
        [Terminals.BRACKET_OPEN, NonTerminals.EXPRESSION, ActionSymbols.UPDATE_ID, Terminals.BRACKET_CLOSE],
        [Terminals.EPSILON]],
    NonTerminals.FACTOR_PRIME: [
        [Terminals.PARENTHESIS_OPEN, NonTerminals.ARGS, Terminals.PARENTHESIS_CLOSE, ActionSymbols.CALL],
        [Terminals.EPSILON]],
    NonTerminals.FACTOR_ZEGOND: [
        [Terminals.PARENTHESIS_OPEN, NonTerminals.EXPRESSION, Terminals.PARENTHESIS_CLOSE],
        [ActionSymbols.SAVE_NUM, Terminals.NUM]],
    NonTerminals.ARGS: [
        [ActionSymbols.PUSH_ZERO, NonTerminals.ARG_LIST],
        [Terminals.EPSILON]],
    NonTerminals.ARG_LIST: [
        [CheckSymbols.PARAMETER_NUMBER, NonTerminals.EXPRESSION, CheckSymbols.ARG_TYPE, ActionSymbols.NEW_ARG,
         NonTerminals.ARG_LIST_PRIME]],
    NonTerminals.ARG_LIST_PRIME: [
        [Terminals.COMMA, CheckSymbols.PARAMETER_NUMBER, NonTerminals.EXPRESSION, CheckSymbols.ARG_TYPE,
         ActionSymbols.NEW_ARG,
         NonTerminals.ARG_LIST_PRIME],
        [ActionSymbols.POP, Terminals.EPSILON]]}


def first(statement):
    first_set = set()
    for i, state in enumerate(statement):
        if type(state) is not Terminals and type(state) is not NonTerminals:
            continue
        if type(state) is NonTerminals:
            s = set(state.first)

            if Terminals.EPSILON in s:
                if i < (len(statement) - 1):
                    s.remove(Terminals.EPSILON)
                first_set.update(s)
            else:
                first_set.update(s)
                break
        else:
            first_set.add(state)
            break
    return list(first_set)




ll1_table = {}
for nonterminal in NonTerminals:
    ll1_table[nonterminal.name] = {}
    row = {}
    for terminal in Terminals:
        row[terminal.name] = None
    ll1_table[nonterminal.name] = row


def create_parsing_table():
    for nonterminal in NonTerminals:
        action_leading_to_epsilon = None
        for production in productions[nonterminal]:
            for terminal in first(production):
                if terminal != Terminals.EPSILON:
                    ll1_table[nonterminal.name][terminal.name] = production
                else:
                    action_leading_to_epsilon = production
        default_value = action_leading_to_epsilon if action_leading_to_epsilon else 'synch'
        for terminal in nonterminal.follow:
            if ll1_table[nonterminal.name][terminal.name] is None:
                ll1_table[nonterminal.name][terminal.name] = default_value



def report_syntax_error(error_line, error_message):
    print("error_line")
    print(error_line)
    print("error_message")
    print(error_message)
