from symbols import ActionSymbols
from lexer import Token

from symbols import CheckSymbols
from intermediate_code_generator.intermediate_code_builder import IntermediateCodeBuilder
from symbols import SymbolTable


class ExpressionProcessor:
    def __init__(self, builder):
        self.builder = builder

    def process_identifiers(self, action: ActionSymbols, token: Token):
        if action == ActionSymbols.PUSH_ID:
            symbol = self.builder.symbol_registry.find_symbol_by_lexeme(token.lexeme)
            if not symbol:
                if token.lexeme == 'output':
                    self.builder.function_stack.append('output')
                    self.builder.data_type_stack.append('void')
            elif symbol.is_function:
                self.builder.function_stack.append(symbol)
                current_addr = symbol.first_address
                for _ in range(symbol.size):
                    self.builder.instruction_list.append(f'(ADD, 1000, #4, 1000)')
                    self.builder.instruction_list.append(f'(ASSIGN, {current_addr}, @1000, )')
                    current_addr += 4
                self.builder.instruction_list.append(f'(ADD, 1000, #4, 1000)')
                self.builder.instruction_list.append(f'(ASSIGN, 500, @1000, )')

                for stack_item in reversed(self.builder.operand_stack):
                    if type(stack_item) is int and stack_item >= 500:
                        self.builder.instruction_list.append(f'(ADD, 1000, #4, 1000)')
                        self.builder.instruction_list.append(f'(ASSIGN, {stack_item}, @1000, )')
                    if type(stack_item) is str and stack_item[0] == '@' and int(stack_item[1:]) >= 500:
                        self.builder.instruction_list.append(f'(ADD, 1000, #4, 1000)')
                        self.builder.instruction_list.append(f'(ASSIGN, {stack_item[1:]}, @1000, )')
                self.builder.data_type_stack.append(symbol.type)
            else:
                self.builder.operand_stack.append(symbol.address)
                if symbol.is_array:
                    self.builder.data_type_stack.append('array')
                else:
                    self.builder.data_type_stack.append(symbol.type)

    def process_operations(self, action: ActionSymbols):
        if action == ActionSymbols.ASSIGN:
            self.builder.handle_function_result(-2)
            self.builder.handle_function_result(-1)
            self.builder.instruction_list.append(f'(ASSIGN, {self.builder.operand_stack[-1]}, {self.builder.operand_stack[-2]}, )')
            self.builder.operand_stack.pop(-2)
            self.builder.data_type_stack.pop()
        elif action == ActionSymbols.OPERATION:
            operator = self.builder.operand_stack.pop(-2)
            operation_map = {'*': 'MULT', '/': 'DIV', '+': 'ADD', '-': 'SUB', '<': 'LT', '==': 'EQ'}
            command = operation_map[operator]
            self.builder.handle_function_result(-1)
            self.builder.handle_function_result(-2)
            temp_location = self.builder.allocate_temporary()
            self.builder.instruction_list.append(f'({command}, {self.builder.operand_stack[-2]}, {self.builder.operand_stack[-1]}, {temp_location})')
            self.builder.pop_operands(2)
            self.builder.operand_stack.append(temp_location)
            self.builder.data_type_stack.pop()
        elif action == ActionSymbols.NEG:
            self.builder.handle_function_result(-1)
            self.builder.instruction_list.append(f'(MULT, {self.builder.operand_stack[-1]}, #-1, {self.builder.operand_stack[-1]})')
        elif action == ActionSymbols.UPDATE_ID:
            temp_location = self.builder.allocate_temporary()
            self.builder.instruction_list.append(f'(MULT, {self.builder.operand_stack[-1]}, #4, {temp_location})')
            if self.builder.operand_stack[-2] in self.builder.function_stack[0].parameters:
                self.builder.instruction_list.append(f'(ADD, {self.builder.operand_stack[-2]}, {temp_location}, {temp_location})')
            else:
                self.builder.instruction_list.append(f'(ADD, #{self.builder.operand_stack[-2]}, {temp_location}, {temp_location})')
            self.builder.pop_operands(2)
            self.builder.operand_stack.append(f'@{temp_location}')
            self.builder.data_type_stack.pop()
            self.builder.data_type_stack.pop()
            self.builder.data_type_stack.append('int')

    def process_literals_and_cleanup(self, action: ActionSymbols, token: Token):
        if action == ActionSymbols.SAVE_NUM:
            self.builder.operand_stack.append(f'#{token.lexeme}')
            self.builder.data_type_stack.append('int')
        elif action == ActionSymbols.POP:
            if self.builder.operand_stack[-1] == '@1000':
                self.builder.instruction_list.append(f'(SUB, 1000, #4, 1000)')
            self.builder.pop_operands()
        elif action == ActionSymbols.PUSH_ZERO:
            self.builder.operand_stack.append(0)
        elif action == ActionSymbols.TYPE_POP:
            self.builder.data_type_stack.pop()

    def process_function_calls(self, action: ActionSymbols):
        if action == ActionSymbols.NEW_ARG:
            if self.builder.function_stack[-1] == 'output':
                self.builder.operand_stack.pop(-2)
                self.builder.operand_stack.append(0)
            else:
                arg_value = self.builder.operand_stack.pop()
                arg_position = self.builder.operand_stack.pop()
                if arg_position < len(self.builder.function_stack[-1].parameters):
                    param_addr = self.builder.function_stack[-1].parameters[arg_position]
                    if self.builder.symbol_registry.find_symbol_by_address(param_addr).is_array:
                        if self.builder.symbol_registry.find_symbol_by_address(arg_value) \
                                and self.builder.symbol_registry.find_symbol_by_address(arg_value).is_array \
                                and arg_value in self.builder.function_stack[-1].parameters:
                            self.builder.instruction_list.append(f'(ASSIGN, {arg_value}, {param_addr}, )')
                        else:
                            self.builder.instruction_list.append(f'(ASSIGN, #{arg_value}, {param_addr}, )')
                    else:
                        self.builder.instruction_list.append(f'(ASSIGN, {arg_value}, {param_addr}, )')
                self.builder.operand_stack.append(arg_position + 1)
        elif action == ActionSymbols.CALL:
            function_called = self.builder.function_stack.pop()
            if function_called == 'output':
                output_value = self.builder.operand_stack.pop()
                self.builder.instruction_list.append(f'(PRINT, {output_value}, , )')
                self.builder.operand_stack.append(0)
            else:
                current_index = len(self.builder.instruction_list)
                self.builder.instruction_list.append(f'(ASSIGN, #{current_index + 2}, 500, )')
                self.builder.instruction_list.append(f'(JP, {function_called.code_beginning}, , )')

                for stack_item in self.builder.operand_stack:
                    if type(stack_item) is int and stack_item >= 500:
                        self.builder.instruction_list.append(f'(ASSIGN, @1000, {stack_item}, )')
                        self.builder.instruction_list.append(f'(SUB, 1000, #4, 1000)')
                    if type(stack_item) is str and stack_item[0] == '@' and int(stack_item[1:]) >= 500:
                        self.builder.instruction_list.append(f'(ASSIGN, @1000, {stack_item[1:]}, )')
                        self.builder.instruction_list.append(f'(SUB, 1000, #4, 1000)')

                self.builder.instruction_list.append(f'(ASSIGN, @1000, 500, )')
                self.builder.instruction_list.append(f'(SUB, 1000, #4, 1000)')
                final_address = function_called.first_address + (function_called.size - 1) * 4
                current_addr = final_address
                for _ in range(function_called.size):
                    self.builder.instruction_list.append(f'(ASSIGN, @1000, {current_addr}, )')
                    self.builder.instruction_list.append(f'(SUB, 1000, #4, 1000)')
                    current_addr -= 4
                self.builder.instruction_list.append(f'(ADD, 1000, #4, 1000)')
                self.builder.instruction_list.append(f'(ASSIGN, 504, @1000, )')
                self.builder.operand_stack.append('@1000')

    def process_return_statements(self, action: ActionSymbols):
        if action == ActionSymbols.END_OF_PROGRAM:
            program_address = self.builder.operand_stack.pop()
            final_index = len(self.builder.instruction_list)
            self.builder.instruction_list[program_address] = f'(ASSIGN, #{final_index}, 500, )'
        elif action == ActionSymbols.RETURN:
            self.builder.instruction_list.append(f'(ASSIGN, #0, 504, )')
            self.builder.instruction_list.append(f'(JP, @500, , )')
        elif action == ActionSymbols.RETURN_VALUE:
            return_value = self.builder.operand_stack.pop()
            self.builder.instruction_list.append(f'(ASSIGN, {return_value}, 504, )')
            self.builder.instruction_list.append(f'(JP, @500, , )')

    def execute_code_generation(self, action_type: ActionSymbols, current_token: Token):
        action_processor = CodeGenerationActions(self.builder)

        # Declaration actions
        if action_type in [ActionSymbols.SET_DECLARING, ActionSymbols.PUSH, ActionSymbols.UPDATE_TYPE,
                           ActionSymbols.UPDATE_VAR_ATTRIBUTES, ActionSymbols.UPDATE_ARR_ATTRIBUTES]:
            action_processor.execute_declaration_actions(action_type, current_token)

        # Scope actions
        elif action_type in [ActionSymbols.START_SCOPE, ActionSymbols.START_FUNCTION, ActionSymbols.END_SCOPE]:
            action_processor.execute_scope_actions(action_type)

        # Function actions
        elif action_type in [ActionSymbols.UPDATE_FUNC_ATTRIBUTES, ActionSymbols.RETURN_AT_THE_END_OF_FUNCTION]:
            action_processor.execute_function_actions(action_type)

        # Control flow actions
        elif action_type in [ActionSymbols.LABEL, ActionSymbols.SAVE, ActionSymbols.WHILE_SAVE, ActionSymbols.WHILE,
                             ActionSymbols.JPF_SAVE, ActionSymbols.JP, ActionSymbols.JPF, ActionSymbols.BREAK]:
            action_processor.execute_control_flow_actions(action_type)

        # Expression and operation actions
        elif action_type in [ActionSymbols.PUSH_ID]:
            self.process_identifiers(action_type, current_token)
        elif action_type in [ActionSymbols.ASSIGN, ActionSymbols.OPERATION, ActionSymbols.NEG, ActionSymbols.UPDATE_ID]:
            self.process_operations(action_type)
        elif action_type in [ActionSymbols.SAVE_NUM, ActionSymbols.POP, ActionSymbols.PUSH_ZERO, ActionSymbols.TYPE_POP]:
            self.process_literals_and_cleanup(action_type, current_token)
        elif action_type in [ActionSymbols.NEW_ARG, ActionSymbols.CALL]:
            self.process_function_calls(action_type)
        elif action_type in [ActionSymbols.END_OF_PROGRAM, ActionSymbols.RETURN, ActionSymbols.RETURN_VALUE]:
            self.process_return_statements(action_type)


from intermediate_code_generator.code_generation_actions import CodeGenerationActions


class CodeGenerator:
    def __init__(self, symbol_table: SymbolTable):
        self.builder = IntermediateCodeBuilder(symbol_table)
        self.processor = ExpressionProcessor(self.builder)

    def print_pb(self):
        self.builder.display_instructions()

    def semantic_check(self, check_symbol: CheckSymbols, current_token: Token):
        self.builder.validate_semantics(check_symbol, current_token)

    def code_gen(self, action_symbol: ActionSymbols, current_token: Token):
        self.processor.execute_code_generation(action_symbol, current_token)

    @property
    def semantic_stack(self):
        return self.builder.operand_stack

    @property
    def program_block(self):
        return self.builder.instruction_list

    @property
    def symbol_table(self):
        return self.builder.symbol_registry

    @property
    def is_erroneous(self):
        return self.builder.error_state
