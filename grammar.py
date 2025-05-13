# Author(s): Sepehr Vahedi, Helia Akhtarkavian
# Student ID(s): 99170615, 98170657

# Terminal symbols
TERMINALS = [
    'ID', 'NUM', 'int', 'void', 'if', 'else', 'while', 'return', 'break',
    '{', '}', '[', ']', '(', ')', ';', ':', ',', '=', '<', '+', '-', '*',
    '==', '!=', '>=', '<=', 'EPSILON', 'ENDMARKER'
]

# Non-terminal symbols
NON_TERMINALS = [
    'Program', 'DeclarationList', 'Declaration', 'DeclarationInitial', 'DeclarationPrime',
    'VarDeclarationPrime', 'TypeSpecifier', 'FunDeclarationPrime',
    'Params', 'ParamList', 'Param', 'ParamPrime', 'CompoundStmt',
    'StatementList', 'Statement', 'ExpressionStmt', 'SelectionStmt',
    'IterationStmt', 'ReturnStmt', 'ReturnStmtPrime', 'Expression',
    'B', 'H', 'SimpleExpression', 'SimpleExpressionPrime', 'SimpleExpressionZegond', 'C',
    'Relop', 'AdditiveExpression', 'AdditiveExpressionPrime', 'AdditiveExpressionZegond', 'D',
    'Addop', 'Term', 'TermPrime', 'TermZegond', 'G', 'SignedFactor', 'SignedFactorPrime',
    'SignedFactorZegond', 'Factor', 'VarCallPrime', 'VarPrime', 'FactorPrime', 'FactorZegond',
    'Args', 'ArgList', 'ArgListPrime'
]

# Grammar rules
GRAMMAR = {
    'Program': [
        ['DeclarationList']
    ],
    'DeclarationList': [
        ['Declaration', 'DeclarationList'],
        ['EPSILON']
    ],
    'Declaration': [
        ['DeclarationInitial', 'DeclarationPrime']
    ],
    'DeclarationInitial': [
        ['TypeSpecifier', 'ID']
    ],
    'DeclarationPrime': [
        ['FunDeclarationPrime'],
        ['VarDeclarationPrime']
    ],
    'VarDeclarationPrime': [
        [';'],
        ['[', 'NUM', ']', ';']
    ],
    'TypeSpecifier': [
        ['int'],
        ['void']
    ],
    'FunDeclarationPrime': [
        ['(', 'Params', ')', 'CompoundStmt']
    ],
    'Params': [
        ['int', 'ID', 'ParamPrime', 'ParamList'],
        ['void']
    ],
    'ParamList': [
        [',', 'Param', 'ParamList'],
        ['EPSILON']
    ],
    'Param': [
        ['DeclarationInitial', 'ParamPrime']
    ],
    'ParamPrime': [
        ['[', ']'],
        ['EPSILON']
    ],
    'CompoundStmt': [
        ['{', 'DeclarationList', 'StatementList', '}']
    ],
    'StatementList': [
        ['Statement', 'StatementList'],
        ['EPSILON']
    ],
    'Statement': [
        ['ExpressionStmt'],
        ['CompoundStmt'],
        ['SelectionStmt'],
        ['IterationStmt'],
        ['ReturnStmt']
    ],
    'ExpressionStmt': [
        ['Expression', ';'],
        ['break', ';'],
        [';']
    ],
    'SelectionStmt': [
        ['if', '(', 'Expression', ')', 'Statement', 'else', 'Statement']
    ],
    'IterationStmt': [
        ['while', '(', 'Expression', ')', 'Statement']
    ],
    'ReturnStmt': [
        ['return', 'ReturnStmtPrime']
    ],
    'ReturnStmtPrime': [
        [';'],
        ['Expression', ';']
    ],
    'Expression': [
        ['SimpleExpressionZegond'],
        ['ID', 'B']
    ],
    'B': [
        ['=', 'Expression'],
        ['[', 'Expression', ']', 'H'],
        ['SimpleExpressionPrime']
    ],
    'H': [
        ['=', 'Expression'],
        ['G', 'D', 'C']
    ],
    'SimpleExpressionZegond': [
        ['AdditiveExpressionZegond', 'C']
    ],
    'SimpleExpressionPrime': [
        ['AdditiveExpressionPrime', 'C']
    ],
    'C': [
        ['Relop', 'AdditiveExpression'],
        ['EPSILON']
    ],
    'Relop': [
        ['<'],
        ['=='],
        ['>='],
        ['<='],
        ['!=']
    ],
    'AdditiveExpression': [
        ['Term', 'D']
    ],
    'AdditiveExpressionPrime': [
        ['TermPrime', 'D']
    ],
    'AdditiveExpressionZegond': [
        ['TermZegond', 'D']
    ],
    'D': [
        ['Addop', 'Term', 'D'],
        ['EPSILON']
    ],
    'Addop': [
        ['+'],
        ['-']
    ],
    'Term': [
        ['SignedFactor', 'G']
    ],
    'TermPrime': [
        ['SignedFactorPrime', 'G']
    ],
    'TermZegond': [
        ['SignedFactorZegond', 'G']
    ],
    'G': [
        ['*', 'SignedFactor', 'G'],
        ['EPSILON']
    ],
    'SignedFactor': [
        ['+', 'Factor'],
        ['-', 'Factor'],
        ['Factor']
    ],
    'SignedFactorPrime': [
        ['FactorPrime']
    ],
    'SignedFactorZegond': [
        ['+', 'Factor'],
        ['-', 'Factor'],
        ['FactorZegond']
    ],
    'Factor': [
        ['(', 'Expression', ')'],
        ['ID', 'VarCallPrime'],
        ['NUM']
    ],
    'VarCallPrime': [
        ['(', 'Args', ')'],
        ['VarPrime']
    ],
    'VarPrime': [
        ['[', 'Expression', ']'],
        ['EPSILON']
    ],
    'FactorPrime': [
        ['(', 'Args', ')'],
        ['EPSILON']
    ],
    'FactorZegond': [
        ['(', 'Expression', ')'],
        ['NUM']
    ],
    'Args': [
        ['ArgList'],
        ['EPSILON']
    ],
    'ArgList': [
        ['Expression', 'ArgListPrime']
    ],
    'ArgListPrime': [
        [',', 'Expression', 'ArgListPrime'],
        ['EPSILON']
    ]
}

# FIRST sets for each non-terminal
FIRST = {
    'Program': ['int', 'void', 'EPSILON'],
    'DeclarationList': ['int', 'void', 'EPSILON'],
    'Declaration': ['int', 'void'],
    'DeclarationInitial': ['int', 'void'],
    'DeclarationPrime': ['(', ';', '['],
    'VarDeclarationPrime': [';', '['],
    'TypeSpecifier': ['int', 'void'],
    'FunDeclarationPrime': ['('],
    'Params': ['int', 'void'],
    'ParamList': [',', 'EPSILON'],
    'Param': ['int', 'void'],
    'ParamPrime': ['[', 'EPSILON'],
    'CompoundStmt': ['{'],
    'StatementList': ['ID', ';', '{', 'if', 'while', 'return', 'break', 'EPSILON', '(', 'NUM'],
    'Statement': ['ID', ';', '{', 'if', 'while', 'return', 'break', '(', 'NUM'],
    'ExpressionStmt': ['ID', ';', 'break', '(', 'NUM'],
    'SelectionStmt': ['if'],
    'IterationStmt': ['while'],
    'ReturnStmt': ['return'],
    'ReturnStmtPrime': [';', 'ID', '(', 'NUM'],
    'Expression': ['ID', '(', 'NUM', '+', '-'],
    'B': ['=', '[', '(', '*', '+', '-', '<', '==', '>=', '<=', '!=', 'EPSILON'],
    'H': ['=', '*', '+', '-', '<', '==', '>=', '<=', '!=', 'EPSILON'],
    'SimpleExpressionZegond': ['(', 'NUM', '+', '-'],
    'SimpleExpressionPrime': ['*', '+', '-', '<', '==', '>=', '<=', '!=', 'EPSILON'],
    'C': ['<', '==', '>=', '<=', '!=', 'EPSILON'],
    'Relop': ['<', '==', '>=', '<=', '!='],
    'AdditiveExpression': ['(', 'ID', 'NUM', '+', '-'],
    'AdditiveExpressionPrime': ['*', '+', '-', 'EPSILON'],
    'AdditiveExpressionZegond': ['(', 'NUM', '+', '-'],
    'D': ['+', '-', 'EPSILON'],
    'Addop': ['+', '-'],
    'Term': ['(', 'ID', 'NUM', '+', '-'],
    'TermPrime': ['*', 'EPSILON'],
    'TermZegond': ['(', 'NUM', '+', '-'],
    'G': ['*', 'EPSILON'],
    'SignedFactor': ['+', '-', '(', 'ID', 'NUM'],
    'SignedFactorPrime': ['(', '[', 'EPSILON'],
    'SignedFactorZegond': ['+', '-', '(', 'NUM'],
    'Factor': ['(', 'ID', 'NUM'],
    'VarCallPrime': ['(', '[', 'EPSILON'],
    'VarPrime': ['[', 'EPSILON'],
    'FactorPrime': ['(', 'EPSILON'],
    'FactorZegond': ['(', 'NUM'],
    'Args': ['ID', '(', 'NUM', '+', '-', 'EPSILON'],
    'ArgList': ['ID', '(', 'NUM', '+', '-'],
    'ArgListPrime': [',', 'EPSILON']
}

# FOLLOW sets for each non-terminal
FOLLOW = {
    'Program': ['ENDMARKER'],
    'DeclarationList': ['{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}'],
    'Declaration': ['int', 'void', '{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}'],
    'DeclarationInitial': ['(', ';', '[', ',', ')'],
    'DeclarationPrime': ['int', 'void', '{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}'],
    'VarDeclarationPrime': ['int', 'void', '{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}'],
    'TypeSpecifier': ['ID'],
    'FunDeclarationPrime': ['int', 'void', '{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}'],
    'Params': [')'],
    'ParamList': [')'],
    'Param': [',', ')'],
    'ParamPrime': [',', ')'],
    'CompoundStmt': ['int', 'void', '{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'StatementList': ['}'],
    'Statement': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'ExpressionStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'SelectionStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'IterationStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'ReturnStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'ReturnStmtPrime': ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM', '}', 'else'],
    'Expression': [';', ']', ')', ','],
    'B': [';', ']', ')', ','],
    'H': [';', ']', ')', ','],
    'SimpleExpressionZegond': [';', ']', ')', ','],
    'SimpleExpressionPrime': [';', ']', ')', ','],
    'C': [';', ']', ')', ','],
    'Relop': ['(', 'ID', 'NUM', '+', '-'],
    'AdditiveExpression': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'AdditiveExpressionPrime': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'AdditiveExpressionZegond': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'D': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Addop': ['(', 'ID', 'NUM', '+', '-'],
    'Term': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'TermPrime': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'TermZegond': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'G': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactor': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactorPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactorZegond': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Factor': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'VarCallPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'VarPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'FactorPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'FactorZegond': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Args': [')'],
    'ArgList': [')'],
    'ArgListPrime': [')']
}

# PREDICT sets for each production rule
PREDICT = {
    'Program': {
        1: ['int', 'void', 'EPSILON']  # DeclarationList
    },
    'DeclarationList': {
        1: ['int', 'void'],           # Declaration DeclarationList
        2: ['{', 'ID', ';', 'break', 'if', 'while', 'return', '(', 'NUM', '}', 'EOF']  # EPSILON
    },
    'Declaration': {
        1: ['int', 'void']            # DeclarationInitial DeclarationPrime
    },
    'DeclarationInitial': {
        1: ['int', 'void']            # TypeSpecifier ID
    },
    'DeclarationPrime': {
        1: ['('],                     # FunDeclarationPrime
        2: [';', '[']                 # VarDeclarationPrime
    },
    'VarDeclarationPrime': {
        1: [';'],                     # ;
        2: ['[']                      # [ NUM ] ;
    },
    'TypeSpecifier': {
        1: ['int'],                   # int
        2: ['void']                   # void
    },
    'FunDeclarationPrime': {
        1: ['(']                      # ( Params ) CompoundStmt
    },
    'Params': {
        1: ['int'],                   # int ID ParamPrime ParamList
        2: ['void']                   # void
    },
    'ParamList': {
        1: [','],                     # , Param ParamList
        2: [')']                      # EPSILON
    },
    'Param': {
        1: ['int', 'void']            # DeclarationInitial ParamPrime
    },
    'ParamPrime': {
        1: ['['],                     # [ ]
        2: [',', ')']                 # EPSILON
    },
    'CompoundStmt': {
        1: ['{']                      # { DeclarationList StatementList }
    },
    'StatementList': {
        1: ['ID', ';', 'break', '{', 'if', 'while', 'return', '(', 'NUM'],  # Statement StatementList
        2: ['}']                      # EPSILON
    },
    'Statement': {
        1: ['ID', ';', 'break', '(', 'NUM'],   # ExpressionStmt
        2: ['{'],                     # CompoundStmt
        3: ['if'],                    # SelectionStmt
        4: ['while'],                 # IterationStmt
        5: ['return']                 # ReturnStmt
    },
    'ExpressionStmt': {
        1: ['ID', '(', 'NUM', '+', '-'],        # Expression ;
        2: ['break'],                 # break ;
        3: [';']                      # ;
    },
    'SelectionStmt': {
        1: ['if']                     # if ( Expression ) Statement else Statement
    },
    'IterationStmt': {
        1: ['while']                  # while ( Expression ) Statement
    },
    'ReturnStmt': {
        1: ['return']                 # return ReturnStmtPrime
    },
    'ReturnStmtPrime': {
        1: [';'],                     # ;
        2: ['ID', '(', 'NUM', '+', '-']         # Expression ;
    },
    'Expression': {
        1: ['(', 'NUM', '+', '-'],               # SimpleExpressionZegond
        2: ['ID']                    # ID B
    },
    'B': {
        1: ['='],                     # = Expression
        2: ['['],                     # [ Expression ] H
        3: ['(', '*', '+', '-', '<', '==', '>=', '<=', '!=', ';', ']', ')', ',']  # SimpleExpressionPrime
    },
    'H': {
        1: ['='],                     # = Expression
        2: ['*', '+', '-', '<', '==', '>=', '<=', '!='],  # G D C
    },
    'SimpleExpressionZegond': {
        1: ['(', 'NUM', '+', '-']               # AdditiveExpressionZegond C
    },
    'SimpleExpressionPrime': {
        1: ['*', '+', '-', '<', '==', '>=', '<=', '!=', ';', ']', ')', ',']  # AdditiveExpressionPrime C
    },
    'C': {
        1: ['<', '==', '>=', '<=', '!='],  # Relop AdditiveExpression
        2: [';', ']', ')', ',']       # EPSILON
    },
    'Relop': {
        1: ['<'],                     # <
        2: ['=='],                    # ==
        3: ['>='],                    # >=
        4: ['<='],                    # <=
        5: ['!=']                     # !=
    },
    'AdditiveExpression': {
        1: ['(', 'ID', 'NUM', '+', '-']         # Term D
    },
    'AdditiveExpressionPrime': {
        1: ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # TermPrime D
    },
    'AdditiveExpressionZegond': {
        1: ['(', 'NUM', '+', '-']               # TermZegond D
    },
    'D': {
        1: ['+', '-'],                # Addop Term D
        2: [';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # EPSILON
    },
    'Addop': {
        1: ['+'],                     # +
        2: ['-']                      # -
    },
    'Term': {
        1: ['(', 'ID', 'NUM', '+', '-']         # SignedFactor G
    },
    'TermPrime': {
        1: ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # SignedFactorPrime G
    },
    'TermZegond': {
        1: ['(', 'NUM', '+', '-']               # SignedFactorZegond G
    },
    'G': {
        1: ['*'],                     # * SignedFactor G
        2: ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # EPSILON
    },
    'SignedFactor': {
        1: ['+'],                     # + Factor
        2: ['-'],                     # - Factor
        3: ['(', 'ID', 'NUM']         # Factor
    },
    'SignedFactorPrime': {
        1: ['(', '[', 'EPSILON']      # FactorPrime
    },
    'SignedFactorZegond': {
        1: ['+'],                     # + Factor
        2: ['-'],                     # - Factor
        3: ['(', 'NUM']               # FactorZegond
    },
    'Factor': {
        1: ['('],                     # ( Expression )
        2: ['ID'],                    # ID VarCallPrime
        3: ['NUM']                    # NUM
    },
    'VarCallPrime': {
        1: ['('],                     # ( Args )
        2: ['[', '*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # VarPrime
    },
    'VarPrime': {
        1: ['['],                     # [ Expression ]
        2: ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # EPSILON
    },
    'FactorPrime': {
        1: ['('],                     # ( Args )
        2: ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!=']  # EPSILON
    },
    'FactorZegond': {
        1: ['('],                     # ( Expression )
        2: ['NUM']                    # NUM
    },
    'Args': {
        1: ['ID', '(', 'NUM', '+', '-'],        # ArgList
        2: [')']                      # EPSILON
    },
    'ArgList': {
        1: ['ID', '(', 'NUM', '+', '-']         # Expression ArgListPrime
    },
    'ArgListPrime': {
        1: [','],                     # , Expression ArgListPrime
        2: [')']                      # EPSILON
    }
}

# Synchronizing sets for error recovery
SYNCHRONIZING_SETS = {
    'Program': ['ENDMARKER'],
    'DeclarationList': ['int', 'void', '}'],
    'Declaration': ['int', 'void', 'ID', ';', 'break', '{', 'if', 'while', 'return', '}'],
    'DeclarationInitial': ['(', ';', '[', ',', ')'],
    'DeclarationPrime': ['int', 'void', 'ID', ';', 'break', '{', 'if', 'while', 'return', '}'],
    'VarDeclarationPrime': ['int', 'void', 'ID', ';', 'break', '{', 'if', 'while', 'return', '}'],
    'TypeSpecifier': ['ID'],
    'FunDeclarationPrime': ['int', 'void', 'ID', ';', 'break', '{', 'if', 'while', 'return', '}'],
    'Params': [')'],
    'ParamList': [')'],
    'Param': [',', ')'],
    'ParamPrime': [',', ')'],
    'CompoundStmt': ['int', 'void', 'ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'StatementList': ['}'],
    'Statement': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'ExpressionStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'SelectionStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'IterationStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'ReturnStmt': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'ReturnStmtPrime': ['ID', ';', 'break', '{', 'if', 'while', 'return', '}', 'else'],
    'Expression': [';', ']', ')', ','],
    'B': [';', ']', ')', ','],
    'H': [';', ']', ')', ','],
    'SimpleExpressionZegond': [';', ']', ')', ','],
    'SimpleExpressionPrime': [';', ']', ')', ','],
    'C': [';', ']', ')', ','],
    'Relop': ['ID', '(', 'NUM', '+', '-'],
    'AdditiveExpression': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'AdditiveExpressionPrime': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'AdditiveExpressionZegond': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'D': [';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Addop': ['ID', '(', 'NUM', '+', '-'],
    'Term': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'TermPrime': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'TermZegond': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'G': ['+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactor': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactorPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'SignedFactorZegond': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Factor': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'VarCallPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'VarPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'FactorPrime': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'FactorZegond': ['*', '+', '-', ';', ']', ')', ',', '<', '==', '>=', '<=', '!='],
    'Args': [')'],
    'ArgList': [')'],
    'ArgListPrime': [')']
}
