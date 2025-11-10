from __future__ import annotations
from dataclasses import dataclass

@dataclass
class Atributos:
    vida: int
    ataque: int
    defesa: int
    mana: int = 0
    vida_max: int | None = None

class Entidade:
    def __init__(self, nome: str, atrib: Atributos):
        self.nome = nome
        self._atrib = atrib
        if self._atrib.vida_max is None:
            self._attrib_fix = self._atrib.vida  # evita None
            self._atrib.vida_max = self._attrib_fix

    def receber_dano(self, dano: int) -> int:
        """Aplica defesa da própria entidade e retorna dano efetivo aplicado."""
        bruto = max(0, int(dano))
        defesa = max(0, getattr(self._atrib, "defesa", 0))
        aplicado = max(0, bruto - defesa)
        self._atrib.vida = max(0, self._atrib.vida - aplicado)
        return aplicado

    def esta_vivo(self) -> bool:
        return self._atrib.vida > 0

    def barra_hp(self, largura: int = 20) -> str:
        max_hp = max(1, int(self._atrib.vida_max))
        cheio = int(round(largura * self._atrib.vida / max_hp))
        return "[" + "#" * cheio + "-" * (largura - cheio) + f"] {self._atrib.vida}/{self._atrib.vida_max}"
