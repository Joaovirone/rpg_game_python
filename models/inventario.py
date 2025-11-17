from __future__ import annotations
from .base import Entidade
import random

# ============================================================
#  CLASSE ITEM
# ============================================================

class Item:
    def __init__(
        self,
        nome: str,
        tipo: str,
        valor: int,
        raridade: str,
        dano: int | None = None,
        defesa: int | None = None,
        **kwargs
    ):
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.raridade = raridade
        self.dano = dano
        self.defesa = defesa

        # Atributos extras (ex: cura, aumento_forca…)
        self.extra = kwargs

    def __repr__(self):
        return f"<Item {self.nome} ({self.raridade})>"


# Banco de dados simples de itens
Item.items = [
    # ---------------- Consumíveis ----------------
    {"nome": "Poção de Vida", "tipo": "consumível", "valor": 50, "raridade": "comum", "cura": 50},
    {"nome": "Poção de Mana", "tipo": "consumível", "valor": 70, "raridade": "comum", "cura": 30},
    {"nome": "Poção de Cura Maior", "tipo": "consumível", "valor": 150, "raridade": "raro", "cura": 150},
    {"nome": "Poção de Mana Maior", "tipo": "consumível", "valor": 200, "raridade": "raro", "cura": 100},
    {"nome": "Elixir de Força", "tipo": "consumível", "valor": 80, "raridade": "incomum", "aumento_forca": 10},
    {"nome": "Elixir de Agilidade", "tipo": "consumível", "valor": 90, "raridade": "incomum", "aumento_agilidade": 8},
    {"nome": "Elixir da Resistência", "tipo": "consumível", "valor": 120, "raridade": "raro", "aumento_defesa": 15},
    {"nome": "Poção de Invisibilidade", "tipo": "consumível", "valor": 300, "raridade": "épico", "efeito": "invisível por 10s"},

    # ---------------- Armas ----------------
    {"nome": "Espada Longa", "tipo": "arma", "valor": 300, "raridade": "incomum", "dano": 25},
    {"nome": "Espada Curta", "tipo": "arma", "valor": 150, "raridade": "comum", "dano": 15},
    {"nome": "Arco Curto", "tipo": "arma", "valor": 250, "raridade": "incomum", "dano": 20},
    {"nome": "Cajado Mágico", "tipo": "arma", "valor": 400, "raridade": "raro", "dano": 30},
    {"nome": "Machado Duplo", "tipo": "arma", "valor": 450, "raridade": "épico", "dano": 45},
    {"nome": "Lâmina do Dragão", "tipo": "arma", "valor": 900, "raridade": "lendário", "dano": 70},

    # ---------------- Armaduras ----------------
    {"nome": "Escudo de Madeira", "tipo": "armadura", "valor": 150, "raridade": "comum", "defesa": 15},
    {"nome": "Armadura de Couro", "tipo": "armadura", "valor": 200, "raridade": "incomum", "defesa": 25},
    {"nome": "Armadura de Aço", "tipo": "armadura", "valor": 350, "raridade": "raro", "defesa": 35},
    {"nome": "Armadura de Obsidiana", "tipo": "armadura", "valor": 500, "raridade": "épico", "defesa": 50},
    {"nome": "Armadura Dourada dos Deuses", "tipo": "armadura", "valor": 1000, "raridade": "lendário", "defesa": 80},
    {"nome": "Escudo Divino", "tipo": "armadura", "valor": 850, "raridade": "lendário", "defesa": 90},

    # ---------------- Acessórios ----------------
    {"nome": "Anel da Sorte", "tipo": "acessório", "valor": 100, "raridade": "raro"},
    {"nome": "Amuleto da Vida", "tipo": "acessório", "valor": 200, "raridade": "incomum", "defesa": 10},
    {"nome": "Colar do Mago", "tipo": "acessório", "valor": 400, "raridade": "raro", "defesa": 15},
    {"nome": "Anel do Tempo", "tipo": "acessório", "valor": 800, "raridade": "épico", "defesa": 20},
    {"nome": "Relíquia Ancestral", "tipo": "acessório", "valor": 1200, "raridade": "lendário", "defesa": 30},
]


# ============================================================
#  INVENTÁRIO
# ============================================================

class Inventario:

    def __init__(self, capacidade_maxima: int = 20):
        self.itens = []
        self.capacidade_maxima = capacidade_maxima

    def adicionar_item(self, item: Item):
        if len(self.itens) >= self.capacidade_maxima:
            print("❌ Inventário cheio! Não foi possível adicionar o item.")
            return False
        self.itens.append(item)
        print(f"📦 Item adicionado ao inventário: {item.nome} ({item.raridade})")
        return True

    def remover_item(self, item):
        if item in self.itens:
            self.itens.remove(item)
            return True
        return False

    def listar_itens(self):
        return self.itens



# ============================================================
#  SISTEMA DE DROP
# ============================================================

class Drop_rate:
    RARIDADE_MODIFICADOR = {
        "comum": 1.0,
        "incomum": 0.7,
        "raro": 0.4,
        "épico": 0.2,
        "lendário": 0.1,
    }

    def __init__(self, personagem: Personagem):
        self.personagem = personagem

    def calcular_drop_rate(self, raridade: str) -> float:
        base_rate = 0.10
        level_modifier = self.personagem.nivel * 0.01
        raridade_modifier = self.RARIDADE_MODIFICADOR.get(raridade, 1.0)

        chance = (base_rate + level_modifier) * raridade_modifier
        return min(chance, 0.50)

    @staticmethod
    def gerar_item_da_raridade(raridade: str) -> Item | None:
        itens = [i for i in Item.items if i["raridade"] == raridade]
        if not itens:
            return None
        escolhido = random.choice(itens)
        return Item(**escolhido)

    def tentar_drop(self) -> Item | None:
        raridades = list(self.RARIDADE_MODIFICADOR.keys())
        pesos = [self.RARIDADE_MODIFICADOR[r] for r in raridades]

        raridade_escolhida = random.choices(raridades, weights=pesos, k=1)[0]
        chance = self.calcular_drop_rate(raridade_escolhida)

        print(f"🔍 Tentando drop {raridade_escolhida.upper()} — Chance: {chance*100:.1f}%")

        if random.random() < chance:
            return self.gerar_item_da_raridade(raridade_escolhida)

        return None


# ============================================================
#  LOOT
# ============================================================

class Loot:
    def __init__(self, inventario: Inventario, drop_rate: Drop_rate):
        self.inventario = inventario
        self.drop_rate = drop_rate

    def dropar(self) -> Item | None:
        item = self.drop_rate.tentar_drop()
        if item:
            self.inventario.adicionar_item(item)
        return item
