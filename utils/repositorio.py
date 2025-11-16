from __future__ import annotations
from typing import Any
import os
import json


class Repositorio:
    """
    Placeholder de persistência.
    Nesta base, não grava nem lê de disco — apenas mantém interface.
    """

    def salvar(self, dados: dict[str, Any]) -> None:
        print("(simulado) salvar:", dados)

    def carregar(self) -> dict[str, Any]:
        print("(simulado) carregar: sem dados reais nesta base.")
        return {}

