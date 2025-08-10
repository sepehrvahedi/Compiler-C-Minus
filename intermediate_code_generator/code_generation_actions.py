# Sepehr Vahedi
# 99170615

from symbols import ActionSymbols
from lexer import Token


class CodeGenerationActions:
    def __init__(self, builder):
        self.builder = builder

    def execute_declaration_actions(self, action: ActionSymbols, token: Token):
        if action == ActionSymbols.SET_DECLARING:
            self.builder.symbol_registry.is_declaring = True
        elif action == ActionSymbols.PUSH:
            self.builder.operand_stack.append(token.lexeme)
        elif action == ActionSymbols.UPDATE_TYPE:
            stored_type = self.builder.operand_stack.pop()
            self.builder.symbol_registry.update_type(stored_type)
        elif action == ActionSymbols.UPDATE_VAR_ATTRIBUTES:
            symbol = self.builder.symbol_registry.update_last_symbol()
            if self.builder.function_stack:
                self.builder.function_stack[-1].size += 1
            if not self.builder.parameter_declaration_mode:
                self.builder.instruction_list.append(f'(ASSIGN, #0, {symbol.address}, )')
        elif action == ActionSymbols.UPDATE_ARR_ATTRIBUTES:
            array_size = int(token.lexeme) if token.type == 'NUM' else 0
            symbol = self.builder.symbol_registry.update_last_symbol(is_array=True, size=array_size)
            if self.builder.function_stack:
                self.builder.function_stack[-1].size += symbol.size
            if not self.builder.parameter_declaration_mode:
                current_address = symbol.address
                for _ in range(symbol.size):
                    self.builder.instruction_list.append(f'(ASSIGN, #0, {current_address}, )')
                    current_address += 4

    def execute_scope_actions(self, action: ActionSymbols):
        if action == ActionSymbols.START_SCOPE:
            self.builder.symbol_registry.add_scope()
        elif action == ActionSymbols.START_FUNCTION:
            self.builder.symbol_registry.add_scope()
            self.builder.parameter_declaration_mode = True
        elif action == ActionSymbols.END_SCOPE:
            self.builder.symbol_registry.del_scope()

    def execute_function_actions(self, action: ActionSymbols):
        if action == ActionSymbols.UPDATE_FUNC_ATTRIBUTES:
            self.builder.parameter_declaration_mode = False
            func_symbol = self.builder.symbol_registry.update_last_function()
            func_symbol.code_beginning = len(self.builder.instruction_list)
            self.builder.function_stack.append(func_symbol)
            if func_symbol.lexeme == 'main':
                self.builder.instruction_list.append(f'(ASSIGN, #1000, 1000, )')
                for address in range(100, self.builder.symbol_registry.last_used_address() + 4, 4):
                    self.builder.instruction_list.append(f'(ASSIGN, #0, {address}, )')
                self.builder.operand_stack.append(len(self.builder.instruction_list))
                func_symbol.code_beginning = len(self.builder.instruction_list)
                self.builder.instruction_list.append('')
        elif action == ActionSymbols.RETURN_AT_THE_END_OF_FUNCTION:
            symbol = self.builder.function_stack.pop()
            self.builder.instruction_list.append(f'(ASSIGN, #0, 504, )')
            self.builder.instruction_list.append(f'(JP, @500, , )')
            if symbol.lexeme == 'main':
                param_count = int((symbol.first_address - 100) / 4) + 1
                self.builder.instruction_list[0] = f'(JP, {symbol.code_beginning - param_count}, , )'

    def execute_control_flow_actions(self, action: ActionSymbols):
        if action == ActionSymbols.LABEL:
            self.builder.operand_stack.append(len(self.builder.instruction_list))
        elif action == ActionSymbols.SAVE:
            self.builder.operand_stack.append(len(self.builder.instruction_list))
            self.builder.instruction_list.append('')
        elif action == ActionSymbols.WHILE_SAVE:
            self.builder.handle_function_result(-1)
            temp_address = self.builder.allocate_temporary()
            self.builder.loop_stack.append(temp_address)
            self.builder.instruction_list.append(f'(JPF, {self.builder.operand_stack[-1]}, @{temp_address},)')
            self.builder.pop_operands(1)
        elif action == ActionSymbols.WHILE:
            current_index = len(self.builder.instruction_list)
            self.builder.instruction_list[self.builder.operand_stack[-2]] = f'(ASSIGN, #{current_index + 1}, {self.builder.loop_stack[-1]},)'
            self.builder.instruction_list.append(f'(JP, {self.builder.operand_stack[-1]}, ,)')
            self.builder.loop_stack.pop()
            self.builder.pop_operands(2)
        elif action == ActionSymbols.JPF_SAVE:
            current_index = len(self.builder.instruction_list)
            if self.builder.handle_function_result(-2, self.builder.operand_stack[-1]):
                self.builder.instruction_list[self.builder.operand_stack[-1] + 2] = f'(JPF, {self.builder.operand_stack[-2]}, {current_index + 3},)'
            else:
                self.builder.instruction_list[self.builder.operand_stack[-1]] = f'(JPF, {self.builder.operand_stack[-2]}, {current_index + 1},)'
            self.builder.pop_operands(2)
            self.builder.operand_stack.append(len(self.builder.instruction_list))
            self.builder.instruction_list.append('')
        elif action == ActionSymbols.JP:
            current_index = len(self.builder.instruction_list)
            self.builder.instruction_list[self.builder.operand_stack[-1]] = f'(JP, {current_index}, ,)'
            self.builder.pop_operands(1)
        elif action == ActionSymbols.JPF:
            current_index = len(self.builder.instruction_list)
            if self.builder.handle_function_result(-2, self.builder.operand_stack[-1]):
                self.builder.instruction_list[self.builder.operand_stack[-1] + 2] = f'(JPF, {self.builder.operand_stack[-2]}, {current_index + 2},)'
            else:
                self.builder.instruction_list[self.builder.operand_stack[-1]] = f'(JPF, {self.builder.operand_stack[-2]}, {current_index},)'
            self.builder.pop_operands(2)
        elif action == ActionSymbols.BREAK:
            if self.builder.loop_stack:
                self.builder.instruction_list.append(f'(JP, @{self.builder.loop_stack[-1]}, , )')
