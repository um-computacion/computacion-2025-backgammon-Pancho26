import pytest
from dataclasses import FrozenInstanceError
from core.checker import Checker, BLANCO, NEGRO, COLORES_VALIDOS


def test_creacion_checker_valida():
    c_blanco = Checker(BLANCO)
    c_negro = Checker(NEGRO)

    assert c_blanco.es_blanco() is True
    assert c_blanco.es_negro() is False

    assert c_negro.es_negro() is True
    assert c_negro.es_blanco() is False


def test_creacion_checker_color_invalido():
    with pytest.raises(ValueError) as exc:
        Checker("rojo")
    assert "Color inválido" in str(exc.value)


def test_validate_color_valido_no_excepcion():
    # No debe lanzar excepción
    Checker.validate_color(BLANCO)
    Checker.validate_color(NEGRO)


def test_validate_color_invalido_excepcion():
    with pytest.raises(ValueError) as exc:
        Checker.validate_color("verde")
    assert "Color inválido" in str(exc.value)


def test_contrario_devuelve_color_opuesto():
    assert Checker(BLANCO).contrario() == NEGRO
    assert Checker(NEGRO).contrario() == BLANCO


def test_checker_es_inmutable():
    c = Checker(BLANCO)
    with pytest.raises(FrozenInstanceError):
        c.color = NEGRO  # type: ignore[attr-defined]


def test_constantes_y_conjunto_validos():
    assert BLANCO in COLORES_VALIDOS
    assert NEGRO in COLORES_VALIDOS
    assert COLORES_VALIDOS == {BLANCO, NEGRO}
