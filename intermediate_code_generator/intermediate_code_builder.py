from symbols import CheckSymbols
from lexer import Token
from symbols import SymbolTable


class IntermediateCodeBuilder:
    def __init__(self, symbol_registry: SymbolTable):
        self.operand_stack = []
        self.instruction_list = ['']
        self.symbol_registry = symbol_registry
        self.temporary_counter = 508
        self.loop_stack = []
        self.function_stack = []
        self.parameter_declaration_mode = True
        self.error_state = False
        self.data_type_stack = []

    def display_instructions(self):
        for index, instruction in enumerate(self.instruction_list):
            print(f'{index}	{instruction}')

    def allocate_temporary(self):
        current_address = self.temporary_counter
        self.temporary_counter += 4
        return current_address

    def pop_operands(self, count: int = 1):
        for _ in range(count):
            self.operand_stack.pop()

    def handle_function_result(self, stack_position, instruction_position=None):
        if self.operand_stack[stack_position] != '@1000':
            return False
        else:
            temp_location = self.allocate_temporary()
            if not instruction_position:
                self.instruction_list.append(f'(ASSIGN, @1000, {temp_location}, )')
                self.instruction_list.append(f'(SUB, 1000, #4, 1000)')
            else:
                self.instruction_list.insert(instruction_position, f'(ASSIGN, @1000, {temp_location}, )')
                self.instruction_list.insert(instruction_position + 1, f'(SUB, 1000, #4, 1000)')
            self.operand_stack[stack_position] = temp_location
            return True

    def validate_semantics(self, validation_type: CheckSymbols, token: Token):
        if validation_type == CheckSymbols.ID_IS_DEFINED:
            symbol = self.symbol_registry.find_symbol_by_lexeme(token.lexeme)
            if symbol is None and token.lexeme != 'output':
                report_semantic_error(token.line_number, f'{token.lexeme} is not defined.')
                self.operand_stack.append(0)
                self.data_type_stack.append('int')
                self.error_state = True
        elif validation_type == CheckSymbols.VAR_ARR_IS_INT:
            symbol = self.symbol_registry.get_last_symbol()
            if not symbol.is_function and symbol.type == 'void':
                report_semantic_error(token.line_number, f'Illegal type of void for {symbol.lexeme}.')
                self.error_state = True
        elif validation_type == CheckSymbols.PARAMETER_NUMBER:
            function_called = self.function_stack[-1]
            arguments_provided = self.operand_stack[-1]
            if (function_called == 'output' and arguments_provided == 1) or \
                    (function_called != 'output' and arguments_provided == len(function_called.parameters)):
                report_semantic_error(token.line_number,
                                      f'Mismatch in numbers of arguments of {function_called.lexeme}.')
                self.error_state = True
        elif validation_type == CheckSymbols.BREAK_IS_IN_LOOP:
            if not self.loop_stack:
                report_semantic_error(token.line_number, f'No while found for break.')
                self.error_state = True
        elif validation_type == CheckSymbols.TYPE_MATCH:
            if self.data_type_stack[-1] != self.data_type_stack[-2]:
                report_semantic_error(
                    token.line_number,
                    f'Type mismatch in operands, Got {self.data_type_stack[-2]} instead of {self.data_type_stack[-1]}.')
                self.error_state = True
        elif validation_type == CheckSymbols.ARG_TYPE:
            arg_index = self.operand_stack[-2]
            function_called = self.function_stack[-1]
            if function_called == 'output':
                expected_type = 'int'
            else:
                if arg_index >= len(function_called.parameters):
                    self.data_type_stack.pop()
                    return
                param_address = function_called.parameters[arg_index]
                param_symbol = self.symbol_registry.find_symbol_by_address(param_address)
                expected_type = 'array' if param_symbol.is_array else param_symbol.type
            actual_type = self.data_type_stack.pop()
            if expected_type != actual_type:
                report_semantic_error(
                    token.line_number,
                    f'Mismatch in type of argument {arg_index + 1} of {function_called.lexeme}. Expected {expected_type} but got {actual_type} instead.')
                self.error_state = True

def report_semantic_error(error_line, error_message):
    print("error_line")
    print(error_line)
    print("error_message")
    print(error_message)