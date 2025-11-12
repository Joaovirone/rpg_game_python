from .personagem import Personagem
from .base import Entidade
import random





class Item:
    def __init__(self, nome: str, tipo: str, valor: int, raridade: str, dano: None, defesa: int = None):
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.raridade = raridade
        self.dano = dano
        self.defesa = defesa


    items =[
        # 💊 Itens de consumo
        {"nome": "Poção de Vida", "tipo": "consumível", "valor": 50, "raridade": "comum", "cura": 50},
        {"nome": "Poção de Mana", "tipo": "consumível", "valor": 70, "raridade": "comum", "cura": 30},
        {"nome": "Poção de Cura Maior", "tipo": "consumível", "valor": 150, "raridade": "raro", "cura": 150},
        {"nome": "Poção de Mana Maior", "tipo": "consumível", "valor": 200, "raridade": "raro", "cura": 100},
        {"nome": "Elixir de Força", "tipo": "consumível", "valor": 80, "raridade": "incomum", "aumento_forca": 10},
        {"nome": "Elixir de Agilidade", "tipo": "consumível", "valor": 90, "raridade": "incomum", "aumento_agilidade": 8},
        {"nome": "Elixir da Resistência", "tipo": "consumível", "valor": 120, "raridade": "raro", "aumento_defesa": 15},
        {"nome": "Poção de Invisibilidade", "tipo": "consumível", "valor": 300, "raridade": "épico", "efeito": "invisível por 10s"},

        # ⚔️ Armas
        {"nome": "Espada Longa", "tipo": "arma", "valor": 300, "raridade": "incomum", "dano": 25, "defesa": None},
        {"nome": "Espada Curta", "tipo": "arma", "valor": 150, "raridade": "comum", "dano": 15, "defesa": None},
        {"nome": "Arco Curto", "tipo": "arma", "valor": 250, "raridade": "incomum", "dano": 20, "defesa": None},
        {"nome": "Cajado Mágico", "tipo": "arma", "valor": 400, "raridade": "raro", "dano": 30, "defesa": None},
        {"nome": "Machado Duplo", "tipo": "arma", "valor": 450, "raridade": "épico", "dano": 45, "defesa": None},
        {"nome": "Lâmina do Dragão", "tipo": "arma", "valor": 900, "raridade": "lendário", "dano": 70, "defesa": None},

        # 🛡️ Armaduras
        {"nome": "Escudo de Madeira", "tipo": "armadura", "valor": 150, "raridade": "comum", "dano": None, "defesa": 15},
        {"nome": "Armadura de Couro", "tipo": "armadura", "valor": 200, "raridade": "incomum", "dano": None, "defesa": 25},
        {"nome": "Armadura de Aço", "tipo": "armadura", "valor": 350, "raridade": "raro", "dano": None, "defesa": 35},
        {"nome": "Armadura de Obsidiana", "tipo": "armadura", "valor": 500, "raridade": "épico", "dano": None, "defesa": 50},
        {"nome": "Armadura Dourada dos Deuses", "tipo": "armadura", "valor": 1000, "raridade": "lendário", "dano": None, "defesa": 80},
        {"nome": "Escudo Divino", "tipo": "armadura", "valor": 850, "raridade": "lendário", "dano": None, "defesa": 90},

        # 💍 Acessórios
        {"nome": "Anel da Sorte", "tipo": "acessório", "valor": 100, "raridade": "raro", "dano": None, "defesa": None},
        {"nome": "Amuleto da Vida", "tipo": "acessório", "valor": 200, "raridade": "incomum", "dano": None, "defesa": 10},
        {"nome": "Colar do Mago", "tipo": "acessório", "valor": 400, "raridade": "raro", "dano": None, "defesa": 15},
        {"nome": "Anel do Tempo", "tipo": "acessório", "valor": 800, "raridade": "épico", "dano": None, "defesa": 20},
        {"nome": "Relíquia Ancestral", "tipo": "acessório", "valor": 1200, "raridade": "lendário", "dano": None, "defesa": 30}
    ]




class Inventario:
    def __init__(self, capacidade_maxima: int = 20):
        self.itens = []
        self.capacidade_maxima = capacidade_maxima

    def remover_item(self, item):
        if item in self.itens:
            self.itens.remove(item)
            return True
        return False

    def listar_itens(self):
        return self.itens
    

class Drop_rate:

    def __init__(self, personagem: Personagem):
        self.personagem = personagem


    RARIDADE_MODIFICADOR = {
        "comum": 1.0,
        "incomum": 0.7,
        "raro": 0.4,
        "épico": 0.2,
        "lendário": 0.1
    }

    def calcular_drop_rate(self, raridade: str = "comum"):
        base_rate = 0.1  # Taxa base de drop
        level_modifier = self.personagem.nivel * 0.01  # Modificador baseado no nível do personagem
        raridade_modifier = self.RARIDADE_MODIFICADOR.get(raridade.lower(), 1.0)
        
        drop_rate = (base_rate + level_modifier) * raridade_modifier
        return min(drop_rate, 0.5)  # Limita a taxa máxima de drop a 50%

    @staticmethod
    def gerar_drop():
        """Sorteia um item baseado nas chances de raridade de drop dele"""

        raridade = list(Drop_rate.RARIDADE_MODIFICADOR.keys())
        probabilidades = [Drop_rate.RARIDADE_MODIFICADOR[r] for r in raridade]
        raridade_escolhida = random.choices(raridade, weights=probabilidades, k=1 [0])


        itens_raridade = [item for item in Item.items if item["raridade"] == raridade_escolhida]

        if not itens_raridade:
            return None
        
        item_escolhido = random.choice(itens_raridade)
        return item_escolhido
    
    def dropar_itens(self)-> None:

        item_dict = random.choice(Item.items)
        raridade = item_dict['raridade']

        chance = self.calcular_drop_rate(raridade)
        print(f"Tentando dropar {item_dict['nome']} ({raridade}) - Chance: {chance*100:.1f}%")

        if random.random() < chance:
            return Item(**item_dict)
        return None


class Loot:
    def __init__(self, inventario: Inventario, drop_rate: Drop_rate):
        self.inventario = inventario
        self.drop_rate = drop_rate

    def tentar_dropar_item(self, item):
        import random
        if random.random() < self.drop_rate.calcular_drop_rate(item.raridade):
            self.inventario.adicionar_item(item)
            return True
        return False

    def gerar_loot_aleatorio(self, quantidade: int = 1):
        """Gera uma quantidade específica de itens aleatórios com base na raridade"""
        import random
        itens_dropados = []
        
        for _ in range(quantidade):
            # Escolhe um item aleatório da lista de itens disponíveis
            item_base = random.choice(Item.items)
            
            # Cria uma nova instância do item
            novo_item = Item(
                nome=item_base["nome"],
                tipo=item_base["tipo"],
                valor=item_base["valor"],
                raridade=item_base["raridade"],
                dano=item_base.get("dano"),
                defesa=item_base.get("defesa")
            )
            
            # Tenta dropar o item
            if self.tentar_dropar_item(novo_item):
                itens_dropados.append(novo_item)
        
        return itens_dropados

