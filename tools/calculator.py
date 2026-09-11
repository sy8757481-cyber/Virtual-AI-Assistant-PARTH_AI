"""
==========================================
PARTH AI
Calculator Tool — bounded AST evaluation
==========================================
"""

import ast
import math
import operator

from utils.logger import log_info, log_error


class Calculator:
    # Bounds keep voice requests inexpensive on an 8 GB CPU-only machine.
    MAX_EXPRESSION_LENGTH = 512
    MAX_AST_NODES = 128
    MAX_DEPTH = 32
    MAX_INTEGER_BITS = 4096
    MAX_EXPONENT = 1000

    def __init__(self):
        self.operators = {
            ast.Add: operator.add,
            ast.Sub: operator.sub,
            ast.Mult: operator.mul,
            ast.Div: operator.truediv,
            ast.FloorDiv: operator.floordiv,
            ast.Mod: operator.mod,
            ast.Pow: operator.pow,
            ast.USub: operator.neg,
            ast.UAdd: operator.pos,
        }
        log_info("Calculator Initialized Successfully.")

    def calculate(self, expression: str):
        try:
            if expression is None:
                raise ValueError("Empty expression")
            expression = str(expression).strip()
            if not expression:
                raise ValueError("Empty expression")
            if len(expression) > self.MAX_EXPRESSION_LENGTH:
                raise ValueError("Expression is too long")
            expression = self._normalize(expression)
            if len(expression) > self.MAX_EXPRESSION_LENGTH:
                raise ValueError("Expression is too long")
            tree = ast.parse(expression, mode="eval")
            if sum(1 for _ in ast.walk(tree)) > self.MAX_AST_NODES:
                raise ValueError("Expression is too complex")
            result = self._format_result(self._evaluate(tree.body))
            log_info(f"Calculation: {expression} = {result}")
            return result
        except Exception as e:
            log_error(f"Calculator Error : {e}")
            raise ValueError("Invalid calculation") from e

    def _normalize(self, expression: str):
        return (expression.replace("×", "*").replace("÷", "/")
                .replace("^", "**").replace("−", "-"))

    def _check_number(self, value):
        # bool is a subclass of int, but is not a supported calculator input.
        if type(value) not in (int, float):
            raise ValueError("Only real numbers are supported")
        if isinstance(value, int):
            if value.bit_length() > self.MAX_INTEGER_BITS:
                raise ValueError("Integer result is too large")
        elif not math.isfinite(value):
            raise ValueError("Result must be finite")
        return value

    def _evaluate(self, node, depth=0):
        if depth > self.MAX_DEPTH:
            raise ValueError("Expression nesting is too deep")

        if isinstance(node, ast.Constant):
            return self._check_number(node.value)

        if isinstance(node, ast.BinOp):
            left = self._evaluate(node.left, depth + 1)
            right = self._evaluate(node.right, depth + 1)
            operation = self.operators.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator")

            if isinstance(node.op, ast.Pow):
                if abs(right) > self.MAX_EXPONENT:
                    raise ValueError("Exponent is too large")
                if left < 0 and isinstance(right, float) and not right.is_integer():
                    raise ValueError("Complex results are not supported")
                # Check growth BEFORE integer exponentiation allocates a result.
                if (isinstance(left, int) and isinstance(right, int)
                        and right > 0 and abs(left) > 1
                        and abs(left).bit_length() * right > self.MAX_INTEGER_BITS):
                    raise ValueError("Power result is too large")

            if (isinstance(node.op, ast.Mult)
                    and isinstance(left, int) and isinstance(right, int)
                    and left and right
                    and left.bit_length() + right.bit_length() > self.MAX_INTEGER_BITS + 1):
                raise ValueError("Product result is too large")

            return self._check_number(operation(left, right))

        if isinstance(node, ast.UnaryOp):
            operand = self._evaluate(node.operand, depth + 1)
            operation = self.operators.get(type(node.op))
            if operation is None:
                raise ValueError("Unsupported operator")
            return self._check_number(operation(operand))

        raise ValueError("Invalid expression")

    def _format_result(self, result):
        result = self._check_number(result)
        if isinstance(result, float):
            if result.is_integer():
                return int(result)
            return round(result, 10)
        return result


