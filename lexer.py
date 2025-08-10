# Sepehr Vahedi
# 99170615

from enum import Enum
from symbols import SymbolTable


class Token:
    def __init__(self, value, token_type, line_number):
        self.lexeme = value
        self.type = token_type
        self.line_number = line_number


class Lexer:
    def __init__(self, text, symbol_table: SymbolTable):
        self.text = text
        self.line_number = 1
        self.tokens = []
        self.symbol_table = symbol_table

    def __get_next_state(self, current_state, char):
        transition_type = TransitionTypes.get_transition_type(char)
        return current_state.read(transition_type)

    def get_next_token(self):
        token_value = ''
        index = 0
        state = States.Q0.value

        while True:
            if index >= len(self.text):
                if state in [States.Q6.value, States.Q7.value]:
                    report_lexical_error(self.line_number, token_value, ErrorMessages.UNCLOSED_COMMENT.value)
                break

            char = self.text[index]
            state = self.__get_next_state(state, char)

            if state.error_message:
                token_value = token_value + char
                report_lexical_error(self.line_number, token_value, state.error_message)

                token_value = ''
                index += 1
                state = States.Q0.value
            elif state.is_finished:
                if not state.does_need_reversion:
                    index += 1
                    token_value = token_value + char
                break
            elif state.does_reset:
                token_value = ''
                state = States.Q0.value
                index += 1
                if char == '\n':
                    self.line_number += 1
            else:
                token_value = token_value + char
                index += 1

        token_type = state.token_type
        if token_type and token_type == TokenTypes.ID_KEY.value:
            if token_value in keywords:
                token_type = TokenTypes.KEY.value
            else:
                token_type = TokenTypes.ID.value

        if not token_type or not token_value:
            # token_type = token_value = None
            token_type = 'END'
            token_value = '$'

        token = Token(token_value, token_type, self.line_number)

        self.text = self.text[index:]
        # add_to_symbol_table(token.type, token.lexeme)
        self.symbol_table.add_to_symbol_table(token.type, token.lexeme)
        self.tokens.append(token)

        # return Token(token_value, token_type, self.line_number)
        return token

digits = [chr(i) for i in range(48, 58)]
letters = [chr(i) for i in range(65, 91)] + [chr(i) for i in range(97, 123)]
symbols = [';', ':', ',', '[', ']', '(', ')', '{', '}', '+', '-', '*', '/', '=', '<']
whitespace = [' ', '\n', '\r', '\t', '\v', '\f']
keywords = ['if', 'else', 'void', 'int', 'while', 'break', 'return', 'endif']


class TokenTypes(Enum):
    NUM = 'NUM'
    ID_KEY = 'ID_KEYWORD'
    ID = 'ID'
    KEY = 'KEYWORD'
    SYMBOL = 'SYMBOL'


class TransitionTypes(Enum):
    DIGIT = digits
    LETTER = letters
    SYMBOL = symbols
    WHITESPACE = whitespace
    NEWLINE = ['\n']
    SLASH = ['/']
    EQUAL = ['=']
    STAR = ['*']
    INVALID = []

    @classmethod
    def get_transition_type(cls, character: chr):
        transition_type = None
        for tr_type in TransitionTypes:
            if character in tr_type.value:
                transition_type = tr_type
        if not transition_type:
            transition_type = TransitionTypes.INVALID
        return transition_type


class ErrorMessages(Enum):
    INVALID_INPUT = 'Invalid input'
    INVALID_NUMBER = 'Invalid number'
    UNMATCHED_COMMENT = 'Unmatched comment'
    UNCLOSED_COMMENT = 'Unclosed comment'

class StateNames(Enum):
    Q0 = 'start'
    Q1 = 'digit'
    Q2 = 'identifier'
    Q3 = '='
    Q4 = '*'
    Q5 = '/'
    Q6 = '/*'
    Q7 = '/**'
    Q8 = '//'
    F0 = 'finished_num'
    F1 = 'finished_id'
    F2 = 'finished_symbol'
    FR0 = 'finished_reverse_num'
    FR1 = 'finished_reverse_id'
    FR2 = 'finished_reverse_symbol'
    R = 'reset'
    ER1 = 'error_invalid_number'
    ER2 = 'error_unmatched_comment'
    ER3 = 'error_invalid_input'


class Transition(Enum):
    # start
    Q0 = {TransitionTypes.DIGIT: StateNames.Q1, TransitionTypes.LETTER: StateNames.Q2,
          TransitionTypes.EQUAL: StateNames.Q3, TransitionTypes.STAR: StateNames.Q4,
          TransitionTypes.SYMBOL: StateNames.F2, TransitionTypes.SLASH: StateNames.Q5,
          TransitionTypes.WHITESPACE: StateNames.R, TransitionTypes.NEWLINE: StateNames.R}
    # digit
    Q1 = {TransitionTypes.DIGIT: StateNames.Q1, TransitionTypes.LETTER: StateNames.ER1,
          TransitionTypes.EQUAL: StateNames.FR0, TransitionTypes.STAR: StateNames.FR0,
          TransitionTypes.SYMBOL: StateNames.FR0, TransitionTypes.SLASH: StateNames.FR0,
          TransitionTypes.WHITESPACE: StateNames.FR0, TransitionTypes.NEWLINE: StateNames.FR0}
    # identifier
    Q2 = {TransitionTypes.DIGIT: StateNames.Q2, TransitionTypes.LETTER: StateNames.Q2,
          TransitionTypes.EQUAL: StateNames.FR1, TransitionTypes.STAR: StateNames.FR1,
          TransitionTypes.SYMBOL: StateNames.FR1, TransitionTypes.SLASH: StateNames.FR1,
          TransitionTypes.WHITESPACE: StateNames.FR1, TransitionTypes.NEWLINE: StateNames.FR1}
    # =
    Q3 = {TransitionTypes.DIGIT: StateNames.FR2, TransitionTypes.LETTER: StateNames.FR2,
          TransitionTypes.EQUAL: StateNames.F2, TransitionTypes.STAR: StateNames.FR2,
          TransitionTypes.SYMBOL: StateNames.FR2, TransitionTypes.SLASH: StateNames.FR2,
          TransitionTypes.WHITESPACE: StateNames.FR2, TransitionTypes.NEWLINE: StateNames.FR2}
    # # *
    # Q4 = {TransitionTypes.DIGIT: StateNames.FR2, TransitionTypes.LETTER: StateNames.FR2,
    #       TransitionTypes.EQUAL: StateNames.FR2, TransitionTypes.STAR: StateNames.FR2,
    #       TransitionTypes.SYMBOL: StateNames.FR2, TransitionTypes.SLASH: StateNames.ERROR2,
    #       TransitionTypes.WHITESPACE: StateNames.FR2, TransitionTypes.NEWLINE: StateNames.FR2,
    #       TransitionTypes.INVALID: StateNames.FR2}
    # *
    Q4 = {TransitionTypes.DIGIT: StateNames.FR2, TransitionTypes.LETTER: StateNames.FR2,
          TransitionTypes.EQUAL: StateNames.FR2, TransitionTypes.STAR: StateNames.FR2,
          TransitionTypes.SYMBOL: StateNames.FR2, TransitionTypes.SLASH: StateNames.ER2,
          TransitionTypes.WHITESPACE: StateNames.FR2, TransitionTypes.NEWLINE: StateNames.FR2}
    # # /
    # Q5 = {TransitionTypes.DIGIT: StateNames.FR2, TransitionTypes.LETTER: StateNames.FR2,
    #       TransitionTypes.EQUAL: StateNames.FR2, TransitionTypes.STAR: StateNames.Q6,
    #       TransitionTypes.SYMBOL: StateNames.FR2, TransitionTypes.SLASH: StateNames.Q8,
    #       TransitionTypes.WHITESPACE: StateNames.FR2, TransitionTypes.NEWLINE: StateNames.FR2,
    #       TransitionTypes.INVALID: StateNames.FR2}
    # /
    Q5 = {TransitionTypes.DIGIT: StateNames.FR2, TransitionTypes.LETTER: StateNames.FR2,
          TransitionTypes.EQUAL: StateNames.FR2, TransitionTypes.STAR: StateNames.Q6,
          TransitionTypes.SYMBOL: StateNames.FR2, TransitionTypes.SLASH: StateNames.Q8,
          TransitionTypes.WHITESPACE: StateNames.FR2, TransitionTypes.NEWLINE: StateNames.FR2}
    # /*
    Q6 = {TransitionTypes.DIGIT: StateNames.Q6, TransitionTypes.LETTER: StateNames.Q6,
          TransitionTypes.EQUAL: StateNames.Q6, TransitionTypes.STAR: StateNames.Q7,
          TransitionTypes.SYMBOL: StateNames.Q6, TransitionTypes.SLASH: StateNames.Q6,
          TransitionTypes.WHITESPACE: StateNames.Q6, TransitionTypes.NEWLINE: StateNames.Q6,
          TransitionTypes.INVALID: StateNames.Q6}
    # /*...*
    Q7 = {TransitionTypes.DIGIT: StateNames.Q6, TransitionTypes.LETTER: StateNames.Q6,
          TransitionTypes.EQUAL: StateNames.Q6, TransitionTypes.STAR: StateNames.Q7,
          TransitionTypes.SYMBOL: StateNames.Q6, TransitionTypes.SLASH: StateNames.R,
          TransitionTypes.WHITESPACE: StateNames.Q6, TransitionTypes.NEWLINE: StateNames.Q6,
          TransitionTypes.INVALID: StateNames.Q6}
    # //
    Q8 = {TransitionTypes.DIGIT: StateNames.Q8, TransitionTypes.LETTER: StateNames.Q8,
          TransitionTypes.EQUAL: StateNames.Q8, TransitionTypes.STAR: StateNames.Q8,
          TransitionTypes.SYMBOL: StateNames.Q8, TransitionTypes.SLASH: StateNames.Q8,
          TransitionTypes.WHITESPACE: StateNames.Q8, TransitionTypes.NEWLINE: StateNames.R,
          TransitionTypes.INVALID: StateNames.Q8}
    F0 = F1 = F2 = {}
    FR0 = FR1 = FR2 = {}
    RESET = {}
    ERROR1 = ERROR2 = ERROR3 = {}


class State:
    state_name = None
    transition = {}
    is_finished = False
    does_need_reversion = False
    does_reset = False
    token_type = None
    error_message = None

    def __init__(self, name: StateNames, transition: Transition, token_type: str = None, is_finished: bool = False,
                 does_need_reversion: bool = False, does_reset: bool = False, error_message: str = None):
        self.state_name = name.value
        self.transition = transition.value
        self.is_finished = is_finished
        self.does_need_reversion = does_need_reversion
        self.does_reset = does_reset
        self.token_type = token_type
        self.error_message = error_message

    def read(self, transition_type: str):
        next_state_name = self.transition.get(transition_type, StateNames.ER3).value
        return States.get_state_by_name(next_state_name)


class States(Enum):
    Q0 = State(StateNames.Q0, Transition.Q0)
    Q1 = State(StateNames.Q1, Transition.Q1, token_type=TokenTypes.NUM.value)
    Q2 = State(StateNames.Q2, Transition.Q2, token_type=TokenTypes.ID_KEY.value)
    Q3 = State(StateNames.Q3, Transition.Q3, token_type=TokenTypes.SYMBOL.value)
    Q4 = State(StateNames.Q4, Transition.Q4, token_type=TokenTypes.SYMBOL.value)
    Q5 = State(StateNames.Q5, Transition.Q5, token_type=TokenTypes.SYMBOL.value)
    Q6 = State(StateNames.Q6, Transition.Q6)
    Q7 = State(StateNames.Q7, Transition.Q7)
    Q8 = State(StateNames.Q8, Transition.Q8)
    F0 = State(StateNames.F0, Transition.F0, is_finished=True, token_type=TokenTypes.NUM.value)
    F1 = State(StateNames.F1, Transition.F1, is_finished=True, token_type=TokenTypes.ID_KEY.value)
    F2 = State(StateNames.F2, Transition.F2, is_finished=True, token_type=TokenTypes.SYMBOL.value)
    FR0 = State(StateNames.FR0, Transition.FR0, is_finished=True, does_need_reversion=True,
                token_type=TokenTypes.NUM.value)
    FR1 = State(StateNames.FR1, Transition.FR1, is_finished=True, does_need_reversion=True,
                token_type=TokenTypes.ID_KEY.value)
    FR2 = State(StateNames.FR2, Transition.FR2, is_finished=True, does_need_reversion=True,
                token_type=TokenTypes.SYMBOL.value)
    RESET = State(StateNames.R, Transition.RESET, does_reset=True)
    ERROR1 = State(StateNames.ER1, Transition.ERROR1, does_reset=True, error_message=ErrorMessages.INVALID_NUMBER.value)
    ERROR2 = State(StateNames.ER2, Transition.ERROR2, does_reset=True,
                   error_message=ErrorMessages.UNMATCHED_COMMENT.value)
    ERROR3 = State(StateNames.ER3, Transition.ERROR3, does_reset=True, error_message=ErrorMessages.INVALID_INPUT.value)

    @classmethod
    def get_state_by_name(cls, name: str):
        for state in States:
            if state.value.state_name == name:
                return state.value
        return None


def report_lexical_error(error_line, dumped_text, error_message):
    print("error_line")
    print(error_line)
    print("dumped_text")
    print(dumped_text)
    print("error_message")
    print(error_message)
