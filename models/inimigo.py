from __future__ import annotations
from typing import Callable, Dict, List, Optional, Union
from .base import Entidade, Atributos
import random

class Inimigo(Entidade):
    def __init__(self, nome: str, vida: int, ataque: int, defesa: int):
        super().__init__(nome, Atributos(vida=vida, ataque=ataque, defesa=defesa, mana=0, vida_max=vida))
        # efeitos usados pela engine/skills (podem começar zerados)
        self.efeitos = {
            "eletro_turnos": 0,
            "veneno_turnos": 0, "veneno_dano": 2,
            "sangramento_turnos": 0, "sangramento_tipo": None, "sangramento_dano": 0,
            "marca_fatal_turnos": 0,
            "semente_turnos": 0,
            "nao_pode_atacar": 0,
            "refletir_dano_turnos": 0,
            "invulneravel_turnos": 0,
            "critico_proximo": False,
            "bonus_proximo": 0,
        }

# --------- Tabelas de configuração ----------

# Dicionário de Inimigos
ENEMY_BASE_STATS: dict[str, tuple[int, int, int]] = {
    # tipo: (vida, ataque, defesa)  -- valores base para NÃO chefes

    "Goblin": (12, 3, 1),
    "Orc": (20, 5, 2),
    "Troll": (60, 7, 3),

    "Lobo Alterado": (14, 4, 1),
    "Espírito": (16, 4, 2),
    "Wendigo": (80, 8, 3),

    "Toupeira de Lodo": (15, 3, 2),
    "Ungoliant": (22, 5, 2),
    "Gollum": (70, 6, 3),

    "Cadáver de Guerreiro": (18, 4, 2),
    "Ceifador": (22, 6, 2),
    "Rei Amaldiçoado": (90, 9, 4),
}

#Cenário e planejamento
SCENARIO_PLAN: dict[str, tuple[tuple[str, str], str]] = {
    "Trilha":   (("Goblin", "Orc"), "Troll"),
    "Floresta": (("Lobo Alterado", "Espírito"), "Wendigo"),
    "Caverna":  (("Toupeira de Lodo", "Ungoliant"), "Gollum"),
    "Ruínas":   (("Cadáver de Guerreiro", "Ceifador"), "Rei Amaldiçoado"),
}

#hp do chefe de acordo com a dificuldade
BOSS_HP_BY_DIFFICULTY: dict[str, int] = {
    "Fácil": 100,
    "Média": 300,
    "Difícil": 500,
}

# qtd de minions por dificuldade: (qtd do minion 1,qtd do minion 2 )
MINION_COUNTS: dict[str, tuple[int, int]] = {
    "Fácil": (2, 1),
    "Média": (3, 2),
    "Difícil": (4, 3),
}

# --------- Helpers públicos para a engine ----------
def hp_boss_chef(dificuldade: str) -> int:
    """
    Retorna HP do Chef de acordo com a dificuldade
    """
    return BOSS_HP_BY_DIFFICULTY.get(dificuldade, 100)

def plan_for_scenario(cenario: str) -> tuple[tuple[str, str], str]:
    """
    Retorna a configuração dos inimigos de acordo com o cenário escolhido
    """
    return SCENARIO_PLAN.get(cenario, (("Goblin", "Orc"), "Troll"))

def criar_inimigo(tipo: str, dificuldade: str, boss: bool = False) -> Inimigo:
    """
    Cria um Inimigo com stats base; se for boss, usa HP escalado pela dificuldade
    """
    vida, atk, defe = ENEMY_BASE_STATS.get(tipo, (15, 4, 2))
    if boss:
        vida = hp_boss_chef(dificuldade)
    inimigo = Inimigo(tipo, vida, atk, defe)

    if boss and hasattr(inimigo, "efeitos"):
        inimigo.efeitos["is_boss"] = True

    return inimigo

def generate_horde(cenario: str, dificuldade: str) -> list[Inimigo]:
    """
    Monta a fila/horda: minions do tipo1, minions do tipo2, e por fim o chefe.
    """
    (m1, m2), chefe = plan_for_scenario(cenario)
    qtd1, qtd2 = MINION_COUNTS.get(dificuldade, MINION_COUNTS["Fácil"])
    fila: list[Inimigo] = []
    fila += [criar_inimigo(m1, dificuldade) for _ in range(qtd1)]
    fila += [criar_inimigo(m2, dificuldade) for _ in range(qtd2)]
    fila += [criar_inimigo(chefe, dificuldade, boss=True)] # enfrentar chefao após os minions
    return fila

