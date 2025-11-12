from __future__ import annotations
import random
from utils.logger import logger

"""
Sistema de Rolar Dados com import random
Rolar D6 = Dados de 1 a 6
Rolar D20 = Dados de 1 a 20
"""


def d6(contexto: str = "") -> int:
    """Rola um dado de 6 faces e loga o resultado com contexto."""
    resultado = random.randint(1, 6)
    if contexto:
        logger.debug(f"[d6] {contexto}: {resultado}")
    return resultado

def d20(contexto: str = "") -> int:
    """Rola um dado de 20 faces e loga o resultado com contexto."""
    resultado = random.randint(1, 20)
    if contexto:
        logger.debug(f"[d20] {contexto}: {resultado}")
    return resultado

def rolar_multiplos_dados(quantidade: int, faces: int, contexto: str = "") -> list[int]:
    """Rola múltiplos dados e retorna os resultados individuais."""
    resultados = [random.randint(1, faces) for _ in range(quantidade)]
    if contexto:
        logger.debug(f"[{quantidade}d{faces}] {contexto}: {resultados} = {sum(resultados)}")
    return resultados

def somar_dados(quantidade: int, faces: int, contexto: str = "") -> int:
    """Rola múltiplos dados e retorna a soma."""
    resultados = rolar_multiplos_dados(quantidade, faces, contexto)
    return sum(resultados)