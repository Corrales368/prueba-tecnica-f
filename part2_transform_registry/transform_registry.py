"""
Platform transformation catalog.

From the web, the user picks which operation to apply to the data before it is sent
to the ERP. The team adds new operations every week.

Hotfix of transform_registry_2.py (the original as delivered): no eval, no getattr.
"""
import ast
import inspect
import sys

# Only registered operations can be called from the web. A new operation is a new
# function decorated with @operation: no existing code has to change.
REGISTRY = {}
MAX_EXPRESSION_LENGTH = 200


class OperationNotAllowed(ValueError):
    pass


def operation(func):
    try:
        inspect.signature(func).bind("var1", "var2")
    except TypeError:
        raise TypeError(f"operation {func.__name__!r} must accept (var1, var2)") from None
    if func.__name__ in REGISTRY:
        raise ValueError(f"operation {func.__name__!r} is already registered")
    REGISTRY[func.__name__] = func
    return func


@operation
def suma(var1, var2):
    return float(var1) + float(var2)


@operation
def resta(var1, var2):
    return float(var1) - float(var2)


@operation
def mayuscula_a_minuscula(var1, var2):
    return var1.lower()


def _formatear_salida(valor):
    """Internal helper. Not a catalog operation."""
    return str(valor).strip()


def main(nombre_funcion, var1, var2):
    """Runs the operation the user picked on the web."""
    # Composite operations: a client asked to chain two functions in a single
    # operation without having to publish a new function. (2024)
    if "(" in nombre_funcion:
        return _evaluate_composite(nombre_funcion, var1, var2)

    funcion = REGISTRY.get(nombre_funcion)
    if funcion is None:
        raise OperationNotAllowed(f"operation not allowed: {nombre_funcion!r}")
    resultado = funcion(var1, var2)
    return _formatear_salida(resultado)


def _evaluate_composite(expression, var1, var2):
    # Replaces eval(): only calls to registered operations, with var1, var2, literals
    # or other calls as arguments. Anything else is rejected without being executed.
    if len(expression) > MAX_EXPRESSION_LENGTH:
        raise OperationNotAllowed(f"composite operation longer than {MAX_EXPRESSION_LENGTH} chars")
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise OperationNotAllowed(f"operation not allowed: {expression!r}") from None
    return _evaluate_node(tree.body, {"var1": var1, "var2": var2}, expression)


def _evaluate_node(node, variables, expression):
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name) or node.func.id not in REGISTRY or node.keywords:
            raise OperationNotAllowed(f"operation not allowed: {expression!r}")
        args = [_evaluate_node(arg, variables, expression) for arg in node.args]
        return REGISTRY[node.func.id](*args)
    if isinstance(node, ast.Name):
        if node.id not in variables:
            raise OperationNotAllowed(f"operation not allowed: {expression!r}")
        return variables[node.id]
    try:
        return ast.literal_eval(node)  # literals only (1, -1, "a"...): never names or calls
    except (ValueError, TypeError):
        raise OperationNotAllowed(f"operation not allowed: {expression!r}") from None


if __name__ == "__main__":
    print(main(sys.argv[1], sys.argv[2], sys.argv[3]))
