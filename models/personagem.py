# models/personagem.py
from __future__ import annotations
from .base import Entidade, Atributos
from typing import Optional, List, Dict
from dado import d6 , d20 
from .base import Atributos, Entidade  # reexport Entidade para compatibilidade

# ========================== EFEITOS / TICKS ===============================

def tick_efeitos_inicio_turno(alvo: Entidade) -> int:
    """
    Aplica efeitos de início de turno em 'alvo'.
    Respeita invulnerabilidade (não recebe dano neste turno).
    Diminui contadores mesmo quando não causa dano.
    Retorna o dano total sofrido por efeitos.
    """
    if not hasattr(alvo, "efeitos"):
        return 0

    total = 0
    inv = alvo.efeitos.get("invulneravel_turnos", 0) > 0

    # Eletrocussão: 1d6-1 por turno (mín. 0)
    if alvo.efeitos.get("eletro_turnos", 0) > 0:
        if not inv:
            dano = max(0, d6() - 1)
            total += alvo.receber_dano(dano)
        alvo.efeitos["eletro_turnos"] -= 1

    # Veneno: dano fixo por turno (ex.: 2)
    if alvo.efeitos.get("veneno_turnos", 0) > 0:
        if not inv:
            dano = max(0, alvo.efeitos.get("veneno_dano", 2))
            total += alvo.receber_dano(dano)
        alvo.efeitos["veneno_turnos"] -= 1

    # Sangramento: tipo "d6" (rolado) ou fixo (sangramento_dano)
    if alvo.efeitos.get("sangramento_turnos", 0) > 0:
        if not inv:
            if alvo.efeitos.get("sangramento_tipo") == "d6":
                dano = d6()
            else:
                dano = max(0, alvo.efeitos.get("sangramento_dano", 1))
            total += alvo.receber_dano(dano)
        alvo.efeitos["sangramento_turnos"] -= 1

    # Marca Fatal: 1d6 por turno
    if alvo.efeitos.get("marca_fatal_turnos", 0) > 0:
        if not inv:
            total += alvo.receber_dano(d6())
        alvo.efeitos["marca_fatal_turnos"] -= 1

    # Semente Engatilhada: após 2 turnos, cura 1d20-5
    if alvo.efeitos.get("semente_turnos", 0) > 0:
        alvo.efeitos["semente_turnos"] -= 1
        if alvo.efeitos["semente_turnos"] == 0 and hasattr(alvo, "curar"):
            cura = max(0, d20() - 5)
            alvo.curar(cura)

    # Contadores "não-dano"
    if alvo.efeitos.get("nao_pode_atacar", 0) > 0:
        alvo.efeitos["nao_pode_atacar"] -= 1
    if alvo.efeitos.get("refletir_dano_turnos", 0) > 0:
        alvo.efeitos["refletir_dano_turnos"] -= 1
    if alvo.efeitos.get("invulneravel_turnos", 0) > 0:
        alvo.efeitos["invulneravel_turnos"] -= 1

    return total


def aplicar_buffs_de_ataque(user: Entidade, dano_base: int) -> int:
    """Aplica bônus/crit do 'próximo ataque' e reseta."""
    if not hasattr(user, "efeitos"):
        return dano_base
    dano = dano_base + user.efeitos.get("bonus_proximo", 0)
    user.efeitos["bonus_proximo"] = 0
    if user.efeitos.get("critico_proximo"):
        dano *= 2
        user.efeitos["critico_proximo"] = False
    return max(0, dano)


# =============================== PERSONAGEM ===============================

class Personagem(Entidade):
    """Base do jogador."""

    def __init__(self, nome: str, atrib: Atributos):
        super().__init__(nome, atrib)
        self.nivel = 1
        self.xp = 0
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

            # controle de missão/habilidade
            "turnos": 0,
            "empurrao_sismico_usado": False,
            "prox_flecha_d20_critico": False,
        }

    # -------- utilitários --------
    def inicio_turno(self) -> int:
        return tick_efeitos_inicio_turno(self)

    def curar(self, qtd: int) -> int:
        ant = self._atrib.vida
        self._atrib.vida = min(self._atrib.vida_max or self._atrib.vida,
                               self._atrib.vida + max(0, qtd))
        return self._atrib.vida - ant

    def gastar_mana(self, custo: int) -> bool:
        if custo <= 0:
            return True
        atual = getattr(self._atrib, "mana", 0)
        if atual < custo:
            print(f"{self.nome} não tem mana suficiente ({atual}/{custo}).")
            return False
        self._atrib.mana = atual - custo
        return True

    def calcular_dano_base(self) -> int:
        if self.efeitos.get("nao_pode_atacar", 0) > 0:
            return 0
        bruto = d6() + self._atrib.ataque
        return aplicar_buffs_de_ataque(self, bruto)

    # -------- XP (nível máx. 10, libera skill a cada 2 níveis) --------
    def _xp_para_proximo(self) -> int:
        return 100 * self.nivel

    def ganhar_xp(self, qtd: int) -> list[str]:
        logs: list[str] = []
        qtd = max(0, int(qtd))
        if qtd == 0 or self.nivel >= 10:
            return logs

        self.xp += qtd
        while self.nivel < 10 and self.xp >= self._xp_para_proximo():
            self.xp -= self._xp_para_proximo()
            self.nivel += 1

            # leve progressão
            self._atrib.vida_max = (self._atrib.vida_max or self._atrib.vida) + 5
            self._attrib_after = min(self._atrib.vida_max, self._atrib.vida + 5)
            self._atrib.vida = self._attrib_after
            self._atrib.ataque += 1
            self._atrib.defesa += 1
            self._atrib.mana += 5

            if self.nivel in (2, 4, 6, 8):
                logs.append(f"Subiu para o nível {self.nivel}! Nova habilidade desbloqueada.")
            else:
                logs.append(f"Subiu para o nível {self.nivel}!")

        if self.nivel >= 10:
            self.xp = 0
            logs.append("Nível máximo atingido (10).")
        return logs


# =============================== GUERREIRO ================================

class Guerreiro(Personagem):
    # Ataque básico (menu [1])
    def ataque_basico(self, alvo) -> int:
        # 0 mana | 1d6
        if not self.gastar_mana(0):
            return 0
        return alvo.receber_dano(d6() + self._atrib.ataque)

    # 1) Execução Pública
    def esp_execucao_publica(self, alvo) -> int:
        # 7 mana | 5d6, crítico garantido +3; só após 4 turnos
        if self.efeitos.get("turnos", 0) < 4:
            print("Execução Pública só após 4 turnos.")
            return 0
        if not self.gastar_mana(7):
            return 0
        dano = sum(d6() for _ in range(5))
        dano = dano * 2 + 3
        return alvo.receber_dano(dano)

    # 2) Perseverança
    def esp_perseveranca(self) -> int:
        # 0 mana | 1 turno invulnerável
        if not self.gastar_mana(0):
            return 0
        self.efeitos["invulneravel_turnos"] = max(self.efeitos.get("invulneravel_turnos", 0), 1)
        print(f"{self.nome} está impenetrável por 1 turno.")
        return 0

    # 3) Golpe Trovejante
    def esp_golpe_trovejante(self, alvo) -> int:
        # 1 mana | 1d20
        if not self.gastar_mana(1):
            return 0
        return alvo.receber_dano(d20() + self._atrib.ataque)

    # 4) Lâmina Ínfera
    def esp_lamina_infera(self, alvo) -> int:
        # 2 mana | 3d6 + sangramento (1d6) por 2 turnos
        if not self.gastar_mana(2):
            return 0
        dano = sum(d6() for _ in range(3))
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 2)
            alvo.efeitos["sangramento_tipo"] = "d6"
        return alvo.receber_dano(dano)

    def usar_especial(self, n: int, alvo=None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_execucao_publica(alvo)
        if n == 2:          return self.esp_perseveranca()
        if n == 3 and alvo: return self.esp_golpe_trovejante(alvo)
        if n == 4 and alvo: return self.esp_lamina_infera(alvo)
        return 0


# ================================= MAGO ==================================

class Mago(Personagem):
    def ataque_basico(self, alvo) -> int:
        # 1 mana | 1d6
        if not self.gastar_mana(1):
            return 0
        return alvo.receber_dano(d6() + self._atrib.ataque)

    def esp_colapso_minguante(self, alvo) -> int:
        # 15 mana | 6d6
        if not self.gastar_mana(15):
            return 0
        return alvo.receber_dano(sum(d6() for _ in range(6)))

    def esp_descarnar(self, alvo) -> int:
        # 20 mana | 3d20 + sangramento (1d6) por 2 turnos
        if not self.gastar_mana(20):
            return 0
        dano = sum(d20() for _ in range(3))
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 2)
            alvo.efeitos["sangramento_tipo"] = "d6"
        return alvo.receber_dano(dano)

    def esp_distorcao_no_tempo(self) -> int:
        # recupera 50 mana
        self._atrib.mana += 50
        print(f"{self.nome} recupera 50 de mana.")
        return 0

    def esp_empurrao_sismico(self, alvo) -> int:
        # 8 mana | 3d6 + alvo perde 1 turno (uma única vez por missão)
        if self.efeitos.get("empurrao_sismico_usado"):
            print("Empurrão Sísmico só pode ser usado uma vez.")
            return 0
        if not self.gastar_mana(8):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["nao_pode_atacar"] = alvo.efeitos.get("nao_pode_atacar", 0) + 1
        self.efeitos["empurrao_sismico_usado"] = True
        return alvo.receber_dano(sum(d6() for _ in range(3)))

    def usar_especial(self, n: int, alvo=None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_colapso_minguante(alvo)
        if n == 2 and alvo: return self.esp_descarnar(alvo)
        if n == 3:          return self.esp_distorcao_no_tempo()
        if n == 4 and alvo: return self.esp_empurrao_sismico(alvo)
        return 0


# ================================ ARQUEIRO ================================

class Arqueiro(Personagem):
    def ataque_basico(self, alvo) -> int:
        # 0 mana | 1d6 (ou d20 crítico se estilo ativo)
        if not self.gastar_mana(0):
            return 0
        if self.efeitos.get("prox_flecha_d20_critico"):
            self.efeitos["prox_flecha_d20_critico"] = False
            return alvo.receber_dano(d20() * 2 + self._atrib.ataque)
        return alvo.receber_dano(d6() + self._atrib.ataque)

    def esp_curingas(self, alvo) -> int:
        # 8 mana | 5d6
        if not self.gastar_mana(8):
            return 0
        return alvo.receber_dano(sum(d6() for _ in range(5)))

    def esp_cortes_certeiros(self, alvo) -> int:
        # 6 mana | sangramento por 5 rodadas (1d6/turno)
        if not self.gastar_mana(6):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 5)
            alvo.efeitos["sangramento_tipo"] = "d6"
        print(f"{self.nome} aplica cortes certeiros! O alvo sangrará por 5 turnos.")
        return 0

    def esp_estilo_do_cacador(self) -> int:
        # 10 mana | próxima flecha será 1d20 crítico
        if not self.gastar_mana(10):
            return 0
        self.efeitos["prox_flecha_d20_critico"] = True
        print(f"{self.nome} prepara Estilo do Caçador (próximo tiro: d20 crítico).")
        return 0

    def esp_marca_fatal(self, alvo) -> int:
        # 10 mana | 1d6 por 7 turnos
        if not self.gastar_mana(10):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["marca_fatal_turnos"] = max(alvo.efeitos.get("marca_fatal_turnos", 0), 7)
        print(f"{self.nome} marca o alvo: 1d6 por 7 turnos.")
        return 0

    def usar_especial(self, n: int, alvo=None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_curingas(alvo)
        if n == 2 and alvo: return self.esp_cortes_certeiros(alvo)
        if n == 3:          return self.esp_estilo_do_cacador()
        if n == 4 and alvo: return self.esp_marca_fatal(alvo)
        return 0


# =============================== CURANDEIRO ===============================

class Curandeiro(Personagem):
    def ataque_basico(self, alvo) -> int:
        # 0 mana | 1d6 - 2 (mín. 0)
        if not self.gastar_mana(0):
            return 0
        bruto = max(0, d6() - 2 + self._attrib_attack() )
        return alvo.receber_dano(bruto)

    def _attrib_attack(self):
        # helper p/ evitar None
        return getattr(self._atrib, "ataque", 0)

    def esp_capitulo_final(self, aliados: list["Personagem"] | None) -> int:
        # 3 mana | cura 1d6 a todos aliados
        if not self.gastar_mana(3):
            return 0
        if not aliados:
            print("(Sem aliados para curar.)")
            return 0
        cura = d6()
        for a in aliados:
            a.curar(cura)
        print(f"{self.nome} cura todos os aliados em {cura}.")
        return 0

    def esp_semente_engatilhada(self, aliado: Personagem | None) -> int:
        # 5 mana | após 2 turnos, aliado recupera 1d20-5
        if not self.gastar_mana(5):
            return 0
        if not aliado:
            print("(Sem aliado alvo para a semente.)")
            return 0
        if hasattr(aliado, "efeitos"):
            aliado.efeitos["semente_turnos"] = 2
        print(f"{self.nome} planta uma semente curativa em {aliado.nome}.")
        return 0

    def esp_ventos_revigorantes(self) -> int:
        # 15 mana | por 1 rodada reflete dano recebido
        if not self.gastar_mana(15):
            return 0
        self.efeitos["refletir_dano_turnos"] = max(self.efeitos.get("refletir_dano_turnos", 0), 1)
        print(f"{self.nome} invoca Ventos Revigorantes (reflexão por 1 rodada).")
        return 0

    def esp_golpe_de_misericordia(self, alvo) -> int:
        # 0 mana | sacrifica a própria vida e causa 4d20
        if not self.gastar_mana(0):
            return 0
        dano = sum(d20() for _ in range(4))
        ef = alvo.receber_dano(dano)
        self._atrib.vida = 0
        print(f"{self.nome} cai após um Golpe de Misericórdia!")
        return ef

    def usar_especial(self, n: int, alvo=None, aliado: Personagem | None = None,
                      aliados: list["Personagem"] | None = None) -> int:
        # mapping 1..4 (no HUD aparecem como 2..5)
        if n == 1 and aliados is not None: return self.esp_capitulo_final(aliados)
        if n == 2 and aliado  is not None: return self.esp_semente_engatilhada(aliado)
        if n == 3:                         return self.esp_ventos_revigorantes()
        if n == 4 and alvo  is not None:   return self.esp_golpe_de_misericordia(alvo)
        return 0

