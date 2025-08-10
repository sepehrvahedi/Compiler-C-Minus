# Sepehr Vahedi
# 99170615

from symbols import SymbolTable
from lexer import Lexer
from parser import Parser
from intermediate_code_generator.expression_processor import CodeGenerator

def read_code(address):
    with open(address) as file:
        input_text = file.read()
    return input_text


def write_intermediate(codes):
    text = ''
    for i, code in enumerate(codes):
        text += f'{i}\t{code}\n'
    if not text:
        text = 'The output code has not been generated.\n'

    with open('output.txt', 'w') as file:
        file.write(text)


input_text = read_code('input.txt')

symbol_table = SymbolTable()
lexer = Lexer(input_text, symbol_table)
code_generator = CodeGenerator(symbol_table)
parser = Parser(lexer, code_generator)

parser.parse()

write_intermediate(parser.code_generator.program_block)
