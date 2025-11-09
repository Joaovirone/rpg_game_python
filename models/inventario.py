from personagem import Personagem
from base import Entidade
class Inventario:
    def __init__(self, capacidade_maxima: int = 20):
        self.itens = []
        self.capacidade_maxima = capacidade_maxima

    def adicionar_item(self, item):
        if len(self.itens) < self.capacidade_maxima:
            self.itens.append(item)
            return True
        return False

    def remover_item(self, item):
        if item in self.itens:
            self.itens.remove(item)
            return True
        return False

    def listar_itens(self):
        return self.itens
    
    def listar_por_tipo(self, tipo: str):
        """Lista todos os itens de um determinado tipo"""
        return [item for item in self.itens if item.tipo.lower() == tipo.lower()]
    
    def listar_por_raridade(self, raridade: str):
        """Lista todos os itens de uma determinada raridade"""
        return [item for item in self.itens if item.raridade.lower() == raridade.lower()]
    
    def espaco_disponivel(self):
        """Retorna a quantidade de espaços disponíveis no inventário"""
        return self.capacidade_maxima - len(self.itens)
    
    def esta_cheio(self):
        """Verifica se o inventário está cheio"""
        return len(self.itens) >= self.capacidade_maxima
    


class Drop_rate:
    RARIDADE_MODIFICADOR = {
        "comum": 1.0,
        "incomum": 0.7,
        "raro": 0.4,
        "épico": 0.2,
        "lendário": 0.1
    }

    def __init__(self, personagem: Personagem):
        self.personagem = personagem

    def calcular_drop_rate(self, raridade: str = "comum"):
        base_rate = 0.1  # Taxa base de drop
        level_modifier = self.personagem.nivel * 0.01  # Modificador baseado no nível do personagem
        raridade_modifier = self.RARIDADE_MODIFICADOR.get(raridade.lower(), 1.0)
        
        drop_rate = (base_rate + level_modifier) * raridade_modifier
        return min(drop_rate, 0.5)  # Limita a taxa máxima de drop a 50%

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

class Item:
    def __init__(self, nome: str, tipo: str, valor: int, raridade: str, dano: None, defesa: int = None):
        self.nome = nome
        self.tipo = tipo
        self.valor = valor
        self.raridade = raridade
        self.dano = dano
        self.defesa = defesa


    items = list[dict] =[{
        "nome": "Poção de Vida",
        "tipo": "consumível",
        "valor": 50,
        "raridade": "comum",
        "cura": 50
    },{
        "nome": "Poção de Mana",
        "tipo": "consumível",
        "valor": 70,
        "raridade": "comum",
        "cura": 30
    },{
        "nome": "Poção de Cura Maior",
        "tipo": "consumível",
        "valor": 150,
        "raridade": "raro",
        "cura": 150
    },{
        "nome": "Poção de Mana Maior",
        "tipo": "consumível",
        "valor": 200,
        "raridade": "raro",
        "cura": 100
    },
    {
        "nome": "Elixir de Força",
        "tipo": "consumível",
        "valor": 80,
        "raridade": "raro",
        "aumento_forca": 10
    },{
        "nome": "Espada Longa",
        "tipo": "arma",
        "valor": 300,
        "raridade": "incomum",
        "dano": 25,
        "defesa": None
    },{
        "nome": "Escudo de Madeira",
        "tipo": "armadura",
        "valor": 150,
        "raridade": "comum",
        "dano": None,
        "defesa": 15
    },{
        "nome": "Arco Curto",
        "tipo": "arma",
        "valor": 250,
        "raridade": "incomum",
        "dano": 20,
        "defesa": None
    },{
        "nome": "Cajado Mágico",
        "tipo": "arma",
        "valor": 400,
        "raridade": "raro",
        "dano": 30,
        "defesa": None
    },{
        "nome": "Armadura de Couro",
        "tipo": "armadura",
        "valor": 200,
        "raridade": "incomum",
        "dano": None,
        "defesa": 25
    },{
        "nome": "Armadura de Obsidiana",
        "tipo": "armadura",
        "valor": 500,
        "raridade": "raro",
        "dano": None,
        "defesa": 40
    },{
        "nome": "Anel da Sorte",
        "tipo": "acessório",
        "valor": 100,
        "raridade": "raro",
        "dano": None,
        "defesa": None
    }]