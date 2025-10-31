from __future__ import annotations
from .base import Entidade, Atributos
import random


class Personagem(Entidade):
    """
    Classe base única do jogador.
    Implementa atributos geral e comportamento padrão no combate
    """

    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0

    def calcular_dano_base(self) -> int: # Métodos de combate
        """
        Deve retornar um inteiro com o dano base do personagem.
        (ex.: usar self._atrib.ataque, aplicar aleatoriedade/crítico/etc.)
        """
        base = self._atrib.ataque #atribui dano base

        variacao = random.uniform(-0.1, 0.1) * base # gera uma porcentagem entre -10% a 10%
        dano = base + variacao # dano recebe valor da soma de sabe + variacao


        if random.random() < 0.10:  #SE CHANCE DE CRÍTICO FOR menor que 10%
            dano *= 1.5 # critico aumenta em 50%

        # Ajusta o dano com base no nível do personagem
        dano *= 1 + (self.nivel - 1) * 0.05

        return max(1, int(dano)) #conversao para inteiro e garante que o valor seja no minimo 1, evitando dano zerado

    def habilidade_especial(self) -> int:
        """
        Deve retornar dano especial (ou 0 se indisponível).
        (ex.: consumir self._atrib.mana e aplicar bônus de dano)
        """
        if self._atrib.mana < 10:
            return 0 # mana insuficiente (indisponivel)

        self._atrib.mana -= 10
        dano = int(self.calcular_dano_base() * 2) # dano especial aplicado 2x sobre o  dano base
        return dano

    def ganhar_xp(self, quantidade: int) -> None:

        """
        Adiciona XP ao personagem e verifica se houve subida de nível.
        A cada 100xp, o personagem sobe 1 nível
        """

        self.xp += quantidade
        while self.xp >= 100: # while permite acumular múltiplos níveis caso a quantidade de XP seja alta
            self.xp -= 100 # diminui xp em 100 para subir nivel
            self.nivel += 1 #sobe o nivel em +1
            self._atrib.vida_max += 10 # atribui a vida máxima em 10
            self._atrib.vida = self._atrib.vida_max #restaura a vida para o máximo atual
            self._atrib.ataque += 2 # sobe o nivel de ataque
            self._atrib.defesa += 1 # sobe o nivel de defesa
            print(f"{self.nome} subiu para o nível {self.nivel}")

    def restaurar(self):
        """Restuara HP e mana ao máximo"""

        self._atrib.vida = self._atrib.vida_max #vida restaurada para o máximo
        self._atrib.mana = max(self._atrib.mana, 30) # mana restaurada garantindo 30 de mana (garante que nunca fique abaixo de 30

    def __str__(self):
        return f"{self.nome} (Nivel: {self.nivel}) - {self._atrib.vida}/{self._atrib.vida_max} HP, {self._atrib.mana} mana"