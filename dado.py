from __future__ import annotations
import random

"""
Sistema de Rolar Dados com import random
Rolar D6 = Dados de 1 a 6
Rolar D20 = Dados de 1 a 20
"""


def d6():
    return random.randint(1, 6)

def d20() -> int:
    return random.randint(1, 20)

