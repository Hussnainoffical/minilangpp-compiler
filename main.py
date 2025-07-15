from lexer import Lexer
from parser import Parser
from semantic import SemanticAnalyzer
from tac import TACGenerator
import traceback
import sys
import time

def main():
    try:
        # Read source code
        with open("sample_input.minipp") as f:
            code = f.read()
        print("==== MiniLang++ Compiler Front-End ====")

        # Lexical Analysis
        print("\n--- Lexical Analysis: Tokens ---")
        lexer = Lexer(code)
        start_time = time.time()
        tokens = lexer.tokenize()
        elapsed = time.time() - start_time
        print(f"[Lexer] Tokenization complete. {len(tokens)} tokens generated in {elapsed:.4f} seconds.")
        for token in tokens:
            print(token)
        if lexer.errors:
            print("\nLexical Errors:")
            for err in lexer.errors:
                print(err)
        print("[Lexer] Phase complete.\n")

        # Syntax Analysis
        print("--- Syntax Analysis: AST ---")
        parser = Parser(tokens)
        start_time = time.time()
        ast = parser.parse()
        elapsed = time.time() - start_time
        print(f"[Parser] AST construction complete in {elapsed:.4f} seconds.")
        if hasattr(ast, 'pretty_print'):
            ast.pretty_print()
        else:
            print("[Parser] AST has no pretty_print method.")
        if parser.errors:
            print("\nSyntax Errors:")
            for err in parser.errors:
                print(err)
        print("[Parser] Phase complete.\n")

        # Semantic Analysis
        print("--- Semantic Analysis: Symbol Tables & Errors ---")
        analyzer = SemanticAnalyzer()
        start_time = time.time()
        analyzer.analyze(ast)
        elapsed = time.time() - start_time
        print(f"[Semantic] Analysis complete in {elapsed:.4f} seconds.")
        print(analyzer.symbol_stack)
        if analyzer.errors:
            print("\nSemantic Errors:")
            for err in analyzer.errors:
                print(err)
        else:
            print("No semantic errors detected.")
        print("[Semantic] Phase complete.\n")

        # Intermediate Code Generation
        print("--- Intermediate Code Generation: Three Address Code (TAC) ---")
        tacgen = TACGenerator()
        start_time = time.time()
        tac = tacgen.generate(ast)
        elapsed = time.time() - start_time
        print(f"[TAC] Generation complete in {elapsed:.4f} seconds. {len(tac)} instructions generated.")
        for instr in tac:
            print(instr)
        print("[TAC] Phase complete.\n")

        print("==== Compilation pipeline completed successfully ====")
    except Exception as e:
        print("\n[ERROR] An exception occurred during compilation:")
        traceback.print_exc(file=sys.stdout)
        print("\n[FAIL] Compilation pipeline terminated with errors.")

if __name__ == "__main__":
    print(">>> Running compiler pipeline")
    main() 