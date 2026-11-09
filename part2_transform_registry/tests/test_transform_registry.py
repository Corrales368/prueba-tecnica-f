import os

import pytest

import transform_registry as fixed
import transform_registry_2 as original
from transform_registry import REGISTRY, OperationNotAllowed, operation


@pytest.fixture
def clean_registry():
    snapshot = dict(REGISTRY)
    yield
    REGISTRY.clear()
    REGISTRY.update(snapshot)


def raised(func, *args):
    with pytest.raises(Exception) as exc:
        func(*args)
    return type(exc.value)


@pytest.mark.parametrize("op, var1, var2", [
    ("suma", "1", "2"),
    ("suma", "0.1", "0.2"),
    ("resta", "10", "4.5"),
    ("mayuscula_a_minuscula", "HELLO World", "x"),
    ("suma(resta(var1, var2), var2)", "5", "3"),
    ("resta(suma(var1, var2), 10)", "5", "3"),
    ("suma(var1, -1)", "5", "3"),
    ("mayuscula_a_minuscula(var1, var2)", "ABC", "x"),
])
def test_same_output_as_the_original(op, var1, var2):
    expected = original.main(op, var1, var2)
    result = fixed.main(op, var1, var2)
    assert result == expected
    assert type(result) is type(expected)


# Known issues left for later (they change what the ERP receives): same behavior.
@pytest.mark.parametrize("op, var1, var2", [
    ("suma", "1,5", "2"),
    ("mayuscula_a_minuscula", 5, "x"),
])
def test_bad_values_fail_as_before(op, var1, var2):
    assert raised(fixed.main, op, var1, var2) is raised(original.main, op, var1, var2)


@pytest.mark.parametrize("payload", [
    "os.getcwd()",
    "__import__('os').getcwd()",
    "(9**9**9)",
    "eval('1+1')",
    "suma.__globals__",
    "suma.__globals__['os']",
    "suma(var1, var2).__class__",
    "suma(var1, var2) or open('x')",
    "[c for c in ('a', 'b')]",
    "suma(*var1)",
    "suma(var1=1, var2=2)",
    "lambda: 1",
    "_formatear_salida",
    "os",
    "sys",
    "main",
    "REGISTRY",
    "operation",
    "suma(" + "1, " * 100 + "2)",
])
def test_attack_is_rejected(payload):
    with pytest.raises(OperationNotAllowed):
        fixed.main(payload, "1", "2")


def test_the_original_executes_arbitrary_code(monkeypatch):
    calls = []
    monkeypatch.setattr(os, "getcwd", lambda: calls.append("executed"))
    original.main("os.getcwd()", "1", "2")
    assert calls == ["executed"]


def test_the_fix_never_executes_it(monkeypatch):
    calls = []
    monkeypatch.setattr(os, "getcwd", lambda: calls.append("executed"))
    with pytest.raises(OperationNotAllowed):
        fixed.main("__import__('os').getcwd()", "1", "2")
    assert calls == []


def test_unknown_operation_gives_a_clear_error():
    with pytest.raises(OperationNotAllowed, match="power"):
        fixed.main("power", "1", "2")


def test_new_operation_from_another_module_is_available(clean_registry):
    @operation
    def multiply(var1, var2):
        return float(var1) * float(var2)

    assert fixed.main("multiply", "3", "4") == "12.0"
    assert fixed.main("suma(multiply(var1, var2), var2)", "3", "4") == 16.0


def test_duplicate_name_fails_when_registering(clean_registry):
    with pytest.raises(ValueError, match="already registered"):
        @operation
        def suma(var1, var2):
            return 0

    assert fixed.main("suma", "1", "2") == "3.0"


def test_wrong_signature_fails_when_registering(clean_registry):
    with pytest.raises(TypeError, match="must accept"):
        @operation
        def three_params(a, b, c):
            return a

    assert "three_params" not in REGISTRY
