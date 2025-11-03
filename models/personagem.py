from __future__ import annotations
from .base import Entidade, Atributos
import random

class Personagem(Entidade):
    """Classe base do jogador com comportamento padrão no combate"""

    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0

    def calcular_dano_base(self) -> int:
        base = self._atrib.ataque
        variacao = random.uniform(-0.1, 0.1) * base
        dano = base + variacao
        if random.random() < 0.10:
            dano *= 1.5
        dano *= 1 + (self.nivel - 1) * 0.05
        return max(1, int(dano))

    def habilidade_especial(self) -> int:
        if self._atrib.mana < 10:
            return 0
        self._atrib.mana -= 10
        return int(self.calcular_dano_base() * 2)

    def ganhar_xp(self, quantidade: int) -> None:
        self.xp += quantidade
        while self.xp >= 100:
            self.xp -= 100
            self.nivel += 1
            self._atrib.vida_max += 10
            self._atrib.vida = self._atrib.vida_max
            self._atrib.ataque += 2
            self._atrib.defesa += 1
            print(f"{self.nome} subiu para o nível {self.nivel}")

    def restaurar(self):
        self._atrib.vida = self._atrib.vida_max
        self._atrib.mana = max(self._atrib.mana, 30)

    def __str__(self):
        return f"{self.nome} (Nivel: {self.nivel}) - {self._atrib.vida}/{self._atrib.vida_max} HP, {self._atrib.mana} mana"

# =========================================
# Arquétipos
# =========================================

class Guerreiro(Personagem):
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=50, ataque=8, defesa=10, mana=5, vida_max=50))
        self.ataque_magico = 0

class Mago(Personagem):
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=30, ataque=1, defesa=4, mana=40, vida_max=30))
        self.ataque_magico = 10

class Arqueiro(Personagem):
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=35, ataque=5, defesa=4, mana=25, vida_max=35))
        self.ataque_magico = 3

class Curandeiro(Personagem):
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=20, ataque=0, defesa=3, mana=35, vida_max=20))
        self.ataque_magico = 8

# =========================================
# Lista de especiais
# =========================================

def lista_especiais(heroi) -> list[tuple[int, str, int]]:
    if isinstance(heroi, Guerreiro):
        return [
            (1, "Duro na Queda", 0),
            (2, "Determinação Mortal", 2),
            (3, "Golpe Estilhaçador", 0)
        ]
    if isinstance(heroi, Mago):
        return [
            (1, "Paradoxo", 3),
            (2, "Eletrocussão", 2),
            (3, "Explosão Florescente", 8)
        ]
    if isinstance(heroi, Arqueiro):
        return [
            (1, "Aljava da Ruína", 1),
            (2, "Contaminar", 3),
            (3, "Ás na Manga", 7)
        ]
    if isinstance(heroi, Curandeiro):
        return [
            (1, "Hemofagia", 4),
            (2, "Transfusão Vital", 30),
            (3, "Resplendor Cósmico", 15)
        ]
    return []
