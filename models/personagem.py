# models/personagem.py
from __future__ import annotations
from typing import Optional, List, Dict
from dado import d6, d20, rolar_multiplos_dados, somar_dados
from utils.logger import logger
from .base import Atributos, Entidade  # mantém compat: from models.personagem import Entidade

# ========================== EFEITOS / TICKS ===============================

def log_efeito_aplicado(alvo: Entidade, efeito: str, duracao: int = 0) -> None:
    """Loga a aplicação de efeitos em entidades."""
    logger.info(f"💫 {efeito} aplicado em {alvo.nome}" + (f" por {duracao} turnos" if duracao > 0 else ""))

def log_dano_causado(atacante: Entidade, alvo: Entidade, dano: int, habilidade: str = "") -> None:
    """Loga o dano causado em combate."""
    if habilidade:
        logger.info(f"⚔️ {atacante.nome} usa {habilidade} em {alvo.nome}: {dano} de dano")
    else:
        logger.info(f"⚔️ {atacante.nome} ataca {alvo.nome}: {dano} de dano")

def log_cura_realizada(curandeiro: Entidade, alvo: Entidade, cura: int, habilidade: str = "") -> None:
    """Loga ações de cura."""
    if habilidade:
        logger.info(f"✨ {curandeiro.nome} usa {habilidade} em {alvo.nome}: +{cura} de vida")
    else:
        logger.info(f"✨ {curandeiro.nome} cura {alvo.nome}: +{cura} de vida")

def tick_efeitos_inicio_turno(alvo: Entidade) -> int:
    """
    Aplica efeitos de início de turno em 'alvo'.
    Retorna o dano total sofrido neste início de turno.
    """
    if not hasattr(alvo, "efeitos"):
        return 0

    total = 0
    inv = alvo.efeitos.get("invulneravel_turnos", 0) > 0

    # Eletrocussão: 1d6-1 por turno
    if alvo.efeitos.get("eletro_turnos", 0) > 0:
        if not inv:
            dano_eletro = max(0, d6("Eletrocussão - Dano por Turno") - 1)
            total += alvo.receber_dano(dano_eletro)
            logger.info(f"⚡ Eletrocussão em {alvo.nome}: {dano_eletro} de dano")
        alvo.efeitos["eletro_turnos"] -= 1

    # Veneno: dano fixo (default 2)
    if alvo.efeitos.get("veneno_turnos", 0) > 0:
        if not inv:
            dano_veneno = max(0, alvo.efeitos.get("veneno_dano", 2))
            total += alvo.receber_dano(dano_veneno)
            logger.info(f"☠️ Veneno em {alvo.nome}: {dano_veneno} de dano")
        alvo.efeitos["veneno_turnos"] -= 1

    # Sangramento: tipo "d6" (rola 1d6/turno) ou fixo
    if alvo.efeitos.get("sangramento_turnos", 0) > 0:
        if not inv:
            if alvo.efeitos.get("sangramento_tipo") == "d6":
                dano_sangramento = d6("Sangramento - Dano por Turno")
            else:
                dano_sangramento = max(0, alvo.efeitos.get("sangramento_dano", 1))
            total += alvo.receber_dano(dano_sangramento)
            logger.info(f"🩸 Sangramento em {alvo.nome}: {dano_sangramento} de dano")
        alvo.efeitos["sangramento_turnos"] -= 1

    # Marca Fatal: 1d6 por turno
    if alvo.efeitos.get("marca_fatal_turnos", 0) > 0:
        if not inv:
            dano_marca = d6("Marca Fatal - Dano por Turno")
            total += alvo.receber_dano(dano_marca)
            logger.info(f"🎯 Marca Fatal em {alvo.nome}: {dano_marca} de dano")
        alvo.efeitos["marca_fatal_turnos"] -= 1

    # Semente Engatilhada: quando zera, cura 1d20-5
    if alvo.efeitos.get("semente_turnos", 0) > 0:
        alvo.efeitos["semente_turnos"] -= 1
        if alvo.efeitos["semente_turnos"] == 0 and hasattr(alvo, "curar"):
            cura_semente = max(0, d20("Semente Engatilhada - Cura") - 5)
            alvo.curar(cura_semente)
            logger.info(f"🌱 Semente Engatilhada ativa em {alvo.nome}: +{cura_semente} de vida")

    # Log de efeitos que estão terminando
    for efeito, turnos in list(alvo.efeitos.items()):
        if isinstance(turnos, int) and turnos == 1:  # Último turno
            if "turnos" in efeito and efeito != "turnos":
                logger.info(f"⏰ {efeito.replace('_turnos', '').title()} está prestes a terminar em {alvo.nome}")

    # Contadores "não-dano"
    for k in ("nao_pode_atacar", "refletir_dano_turnos", "invulneravel_turnos"):
        if alvo.efeitos.get(k, 0) > 0:
            alvo.efeitos[k] -= 1

    # Normalização simples
    try:
        vmax = getattr(alvo._atrib, "vida_max", None) or getattr(alvo._atrib, "vida", 0)
        if alvo._atrib.vida < 0:
            alvo._atrib.vida = 0
        if alvo._atrib.vida > vmax:
            alvo._atrib.vida = vmax
    except Exception:
        pass

    return total


def aplicar_buffs_de_ataque(user: "Personagem", dano_base: int) -> int:
    """Aplica bônus/crítico do próximo ataque e reseta flags."""
    if not hasattr(user, "efeitos"):
        return max(0, dano_base)
    dano = dano_base + user.efeitos.get("bonus_proximo", 0)
    user.efeitos["bonus_proximo"] = 0
    if user.efeitos.get("critico_proximo"):
        dano *= 2
        user.efeitos["critico_proximo"] = False
        logger.info(f"🎯 Crítico aplicado! Dano dobrado: {dano}")
    return max(0, dano)

# =============================== PERSONAGEM ===============================

class Personagem(Entidade):
    """
    Base dos personagens jogáveis.
    - Ataque básico: definido por classe.
    - 7 especiais por classe (4 originais liberadas desde o nível 1; +1 nos níveis 2, 4 e 6).
    """

    def __init__(self, nome: str, atrib: Atributos, ataque_magico: int = 0):
        super().__init__(nome, atrib)
        self.ataque_magico: int = ataque_magico
        self.nivel: int = 1
        self.xp: int = 0
        self.efeitos: Dict[str, int | bool] = {
            # DOTs
            "eletro_turnos": 0,
            "veneno_turnos": 0, "veneno_dano": 2,
            "sangramento_turnos": 0, "sangramento_tipo": None, "sangramento_dano": 0,
            "marca_fatal_turnos": 0,
            "semente_turnos": 0,
            # CC/mitigação
            "nao_pode_atacar": 0,
            "refletir_dano_turnos": 0,
            "invulneravel_turnos": 0,
            # Bônus de ataque
            "critico_proximo": False,
            "bonus_proximo": 0,
            # Controle de missão/habilidade
            "turnos": 0,
            "empurrao_sismico_usado": False,
            "prox_flecha_d20_critico": False,
        }

    # -------- utilitários --------
    def inicio_turno(self) -> int:
        return tick_efeitos_inicio_turno(self)

    def curar(self, qtd: int) -> int:
        ant = self._atrib.vida
        vmax = self._atrib.vida_max or self._atrib.vida
        self._atrib.vida = min(vmax, self._atrib.vida + max(0, int(qtd)))
        curado = self._atrib.vida - ant
        if curado > 0:
            logger.info(f"❤️ {self.nome} cura {curado} de vida")
        return curado

    def gastar_mana(self, custo: int) -> bool:
        if custo <= 0:
            return True
        atual = getattr(self._atrib, "mana", 0)
        if atual < custo:
            logger.warning(f"🔮 {self.nome} não tem mana suficiente ({atual}/{custo}).")
            return False
        self._atrib.mana = atual - custo
        logger.debug(f"🔮 {self.nome} gasta {custo} de mana (restante: {self._atrib.mana})")
        return True

    def calcular_dano_base(self) -> int:
        """Dano físico base: 1d6 + ataque (+ buffs/crítico do próximo ataque)."""
        if self.efeitos.get("nao_pode_atacar", 0) > 0:
            logger.warning(f"🚫 {self.nome} está impossibilitado de atacar!")
            return 0
        bruto = d6("Ataque Básico - Dano Base") + self._atrib.ataque
        return aplicar_buffs_de_ataque(self, bruto)

    # -------- XP (nível máx. 10) --------
    def _xp_para_proximo(self) -> int:
        return 100 * self.nivel

    def ganhar_xp(self, qtd: int) -> List[str]:
        logs: List[str] = []
        qtd = max(0, int(qtd))
        if qtd == 0 or self.nivel >= 10:
            return logs

        self.xp += qtd
        logger.info(f"📈 {self.nome} ganhou {qtd} XP (Total: {self.xp}/{self._xp_para_proximo()})")
        
        while self.nivel < 10 and self.xp >= self._xp_para_proximo():
            self.xp -= self._xp_para_proximo()
            self.nivel += 1

            # progressão simples
            self._atrib.vida_max = (self._atrib.vida_max or self._atrib.vida) + 5
            self._atrib.vida = min(self._atrib.vida_max, self._atrib.vida + 5)
            self._atrib.ataque += 1
            self._atrib.defesa += 1
            self._atrib.mana += 5

            if self.nivel in (2, 4, 6):
                logs.append(f"Subiu para o nível {self.nivel}! Nova habilidade desbloqueada.")
                logger.info(f"🎉 {self.nome} alcançou nível {self.nivel}! Nova habilidade desbloqueada!")
            else:
                logs.append(f"Subiu para o nível {self.nivel}!")
                logger.info(f"🎉 {self.nome} alcançou nível {self.nivel}!")

        if self.nivel >= 10:
            self.xp = 0
            logs.append("Nível máximo atingido (10).")
            logger.info(f"🏆 {self.nome} atingiu o nível máximo (10)!")
        return logs

# =============================== GUERREIRO ================================

class Guerreiro(Personagem):
    """Vida 50 | Ataque 8 | Defesa 10 | Mana 5 | Magia 0"""
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=50, ataque=8, defesa=10, mana=5, vida_max=50), ataque_magico=0)

    # Ataque básico — 0 mana | 1d6 + ataque
    def ataque_basico(self, alvo: Entidade) -> int:
        if not self.gastar_mana(0):
            return 0
        dano = d6("Guerreiro - Ataque Básico") + self._atrib.ataque
        log_dano_causado(self, alvo, dano, "Ataque Básico")
        return alvo.receber_dano(dano)

    # 4 ORIGINAIS (nível 1)
    def esp_execucao_publica(self, alvo: Entidade) -> int:
        # 7 mana | 5d6, crítico garantido +3; só após 4 turnos
        if self.efeitos.get("turnos", 0) < 4:
            logger.warning("Execução Pública só após 4 turnos.")
            return 0
        if not self.gastar_mana(7):
            return 0
        dano = somar_dados(5, 6, "Execução Pública - Dano")
        dano = dano * 2 + 3
        logger.info(f"🎯 Execução Pública - Crítico garantido +3!")
        log_dano_causado(self, alvo, dano, "Execução Pública")
        return alvo.receber_dano(dano)

    def esp_perseveranca(self) -> int:
        # 0 mana | 1 turno invulnerável
        if not self.gastar_mana(0):
            return 0
        self.efeitos["invulneravel_turnos"] = max(self.efeitos.get("invulneravel_turnos", 0), 1)
        logger.info(f"🛡️ {self.nome} está impenetrável por 1 turno.")
        return 0

    def esp_golpe_trovejante(self, alvo: Entidade) -> int:
        # 1 mana | 1d20 + ataque
        if not self.gastar_mana(1):
            return 0
        resultado_d20 = d20("Golpe Trovejante")
        dano = resultado_d20 + self._atrib.ataque
        log_dano_causado(self, alvo, dano, "Golpe Trovejante")
        return alvo.receber_dano(dano)

    def esp_lamina_infera(self, alvo: Entidade) -> int:
        # 2 mana | 3d6 + sangramento (1d6) por 2 turnos
        if not self.gastar_mana(2):
            return 0
        dano_dados = somar_dados(3, 6, "Lâmina Ínfera - Dano")
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 2)
            alvo.efeitos["sangramento_tipo"] = "d6"
            log_efeito_aplicado(alvo, "Sangramento", 2)
        log_dano_causado(self, alvo, dano_dados, "Lâmina Ínfera")
        return alvo.receber_dano(dano_dados)

    # 3 ADICIONAIS (desbloqueiam 2,4,6)
    def esp_duro_na_queda(self) -> int:
        # 0 mana | +1d6 no PRÓXIMO ataque
        if not self.gastar_mana(0):
            return 0
        bonus = d6("Duro na Queda - Bônus")
        self.efeitos["bonus_proximo"] = self.efeitos.get("bonus_proximo", 0) + bonus
        logger.info(f"💪 {self.nome} ativa Duro na Queda: +{bonus} no próximo ataque.")
        return 0

    def esp_determinacao_mortal(self) -> int:
        # 2 mana | cura 1d20
        if not self.gastar_mana(2):
            return 0
        cura = d20("Determinação Mortal - Cura")
        self.curar(cura)
        logger.info(f"❤️ {self.nome} usa Determinação Mortal e cura {cura}.")
        return 0

    def esp_golpe_estilhacador(self) -> int:
        # 0 mana | crítico garantido no PRÓXIMO ataque
        if not self.gastar_mana(0):
            return 0
        self.efeitos["critico_proximo"] = True
        logger.info(f"🔪 {self.nome} prepara Golpe Estilhaçador (próximo ataque crítico).")
        return 0

    def usar_especial(self, n: int, alvo: Optional[Entidade] = None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_execucao_publica(alvo)
        if n == 2:          return self.esp_perseveranca()
        if n == 3 and alvo: return self.esp_golpe_trovejante(alvo)
        if n == 4 and alvo: return self.esp_lamina_infera(alvo)
        if n == 5:          return self.esp_duro_na_queda()
        if n == 6:          return self.esp_determinacao_mortal()
        if n == 7:          return self.esp_golpe_estilhacador()
        return 0

# ================================= MAGO ==================================

class Mago(Personagem):
    """Vida 30 | Ataque 1 | Defesa 4 | Mana 40 | Magia 10"""
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=30, ataque=1, defesa=4, mana=40, vida_max=30), ataque_magico=10)

    def ataque_basico(self, alvo: Entidade) -> int:
        # 1 mana | 1d6 + ataque
        if not self.gastar_mana(1):
            return 0
        dano = d6("Mago - Ataque Básico") + self._atrib.ataque
        log_dano_causado(self, alvo, dano, "Ataque Básico")
        return alvo.receber_dano(dano)

    # 4 ORIGINAIS
    def esp_colapso_minguante(self, alvo: Entidade) -> int:
        # 15 mana | 6d6
        if not self.gastar_mana(15):
            return 0
        dano = somar_dados(6, 6, "Colapso Minguante - Dano")
        log_dano_causado(self, alvo, dano, "Colapso Minguante")
        return alvo.receber_dano(dano)

    def esp_descarnar(self, alvo: Entidade) -> int:
        # 20 mana | 3d20 + sangramento (1d6) por 2 turnos
        if not self.gastar_mana(20):
            return 0
        dano = somar_dados(3, 20, "Descarnar - Dano")
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 2)
            alvo.efeitos["sangramento_tipo"] = "d6"
            log_efeito_aplicado(alvo, "Sangramento", 2)
        log_dano_causado(self, alvo, dano, "Descarnar")
        return alvo.receber_dano(dano)

    def esp_distorcao_no_tempo(self) -> int:
        # 0 mana | recupera 50 mana
        self._atrib.mana += 50
        logger.info(f"🔮 {self.nome} recupera 50 de mana.")
        return 0

    def esp_empurrao_sismico(self, alvo: Entidade) -> int:
        # 8 mana | 3d6 + alvo perde 1 turno (uma única vez por missão)
        if self.efeitos.get("empurrao_sismico_usado"):
            logger.warning("Empurrão Sísmico só pode ser usado uma vez por missão.")
            return 0
        if not self.gastar_mana(8):
            return 0
        dano = somar_dados(3, 6, "Empurrão Sísmico - Dano")
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["nao_pode_atacar"] = alvo.efeitos.get("nao_pode_atacar", 0) + 1
            log_efeito_aplicado(alvo, "Atordoado", 1)
        self.efeitos["empurrao_sismico_usado"] = True
        log_dano_causado(self, alvo, dano, "Empurrão Sísmico")
        return alvo.receber_dano(dano)

    # 3 ADICIONAIS
    def esp_paradoxo(self, alvo: Entidade) -> int:
        # 3 mana | 5d6
        if not self.gastar_mana(3):
            return 0
        dano = somar_dados(5, 6, "Paradoxo - Dano")
        log_dano_causado(self, alvo, dano, "Paradoxo")
        return alvo.receber_dano(dano)

    def esp_eletrocussao(self, alvo: Entidade) -> int:
        # 2 mana | 3d6 + DoT 1d6-1 por 2 turnos
        if not self.gastar_mana(2):
            return 0
        dano = somar_dados(3, 6, "Eletrocussão - Dano Inicial")
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["eletro_turnos"] = alvo.efeitos.get("eletro_turnos", 0) + 2
            log_efeito_aplicado(alvo, "Eletrocussão", 2)
        log_dano_causado(self, alvo, dano, "Eletrocussão")
        return alvo.receber_dano(dano)

    def esp_explosao_florescente(self, alvo: Entidade) -> int:
        # 8 mana | 10d6 e NÃO age no próximo turno
        if not self.gastar_mana(8):
            return 0
        total = somar_dados(10, 6, "Explosão Florescente - Dano")
        self.efeitos["nao_pode_atacar"] = self.efeitos.get("nao_pode_atacar", 0) + 1
        logger.warning(f"💥 {self.nome} não poderá agir no próximo turno!")
        log_dano_causado(self, alvo, total, "Explosão Florescente")
        return alvo.receber_dano(total)

    def usar_especial(self, n: int, alvo: Optional[Entidade] = None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_colapso_minguante(alvo)
        if n == 2 and alvo: return self.esp_descarnar(alvo)
        if n == 3:          return self.esp_distorcao_no_tempo()
        if n == 4 and alvo: return self.esp_empurrao_sismico(alvo)
        if n == 5 and alvo: return self.esp_paradoxo(alvo)
        if n == 6 and alvo: return self.esp_eletrocussao(alvo)
        if n == 7 and alvo: return self.esp_explosao_florescente(alvo)
        return 0

# ================================ ARQUEIRO ================================

class Arqueiro(Personagem):
    """Vida 35 | Ataque 5 | Defesa 4 | Mana 25 | Magia 3"""
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=35, ataque=5, defesa=4, mana=25, vida_max=35), ataque_magico=3)

    def ataque_basico(self, alvo: Entidade) -> int:
        # 0 mana | 1d6 + ataque (ou d20 crítico se estilo ativo)
        if not self.gastar_mana(0):
            return 0
        if self.efeitos.get("prox_flecha_d20_critico"):
            self.efeitos["prox_flecha_d20_critico"] = False
            dano = d20("Arqueiro - Estilo do Caçador") * 2 + self._atrib.ataque
            logger.info("🎯 Estilo do Caçador ativo - Dano crítico!")
            log_dano_causado(self, alvo, dano, "Estilo do Caçador")
            return alvo.receber_dano(dano)
        dano = d6("Arqueiro - Ataque Básico") + self._atrib.ataque
        log_dano_causado(self, alvo, dano, "Ataque Básico")
        return alvo.receber_dano(dano)

    # 4 ORIGINAIS
    def esp_curingas(self, alvo: Entidade) -> int:
        # 8 mana | 5d6
        if not self.gastar_mana(8):
            return 0
        dano = somar_dados(5, 6, "Curingas - Dano")
        log_dano_causado(self, alvo, dano, "Curingas")
        return alvo.receber_dano(dano)

    def esp_cortes_certeiros(self, alvo: Entidade) -> int:
        # 6 mana | sangramento por 5 turnos (1d6/turno)
        if not self.gastar_mana(6):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["sangramento_turnos"] = max(alvo.efeitos.get("sangramento_turnos", 0), 5)
            alvo.efeitos["sangramento_tipo"] = "d6"
            log_efeito_aplicado(alvo, "Cortes Certeiros", 5)
        logger.info(f"🎯 {self.nome} aplica cortes certeiros! O alvo sangrará por 5 turnos.")
        return 0

    def esp_estilo_do_cacador(self) -> int:
        # 10 mana | próxima flecha será 1d20 crítico
        if not self.gastar_mana(10):
            return 0
        self.efeitos["prox_flecha_d20_critico"] = True
        logger.info(f"🎯 {self.nome} prepara Estilo do Caçador (próximo tiro: d20 crítico).")
        return 0

    def esp_marca_fatal(self, alvo: Entidade) -> int:
        # 10 mana | 1d6 por 7 turnos
        if not self.gastar_mana(10):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["marca_fatal_turnos"] = max(alvo.efeitos.get("marca_fatal_turnos", 0), 7)
            log_efeito_aplicado(alvo, "Marca Fatal", 7)
        logger.info(f"🎯 {self.nome} marca o alvo: 1d6 por 7 turnos.")
        return 0

    # 3 ADICIONAIS
    def esp_aljava_da_ruina(self) -> int:
        # 1 mana | + (1d6+2) no PRÓXIMO ataque
        if not self.gastar_mana(1):
            return 0
        bonus = d6("Aljava da Ruína - Bônus") + 2
        self.efeitos["bonus_proximo"] = self.efeitos.get("bonus_proximo", 0) + bonus
        logger.info(f"🏹 {self.nome} ativa Aljava da Ruína: +{bonus} no próximo tiro.")
        return 0

    def esp_contaminar(self, alvo: Entidade) -> int:
        # 3 mana | veneno 2/turno por 3 turnos
        if not self.gastar_mana(3):
            return 0
        if hasattr(alvo, "efeitos"):
            alvo.efeitos["veneno_turnos"] = max(alvo.efeitos.get("veneno_turnos", 0), 3)
            alvo.efeitos["veneno_dano"] = 2
            log_efeito_aplicado(alvo, "Veneno", 3)
        logger.info(f"☠️ {self.nome} contamina o alvo (veneno por 3 turnos).")
        return 0

    def esp_as_na_manga(self) -> int:
        # 7 mana | próximo ataque crítico garantido +10
        if not self.gastar_mana(7):
            return 0
        self.efeitos["critico_proximo"] = True
        self.efeitos["bonus_proximo"] = self.efeitos.get("bonus_proximo", 0) + 10
        logger.info(f"🎲 {self.nome} prepara o Ás na Manga (próximo tiro crítico +10).")
        return 0

    def usar_especial(self, n: int, alvo: Optional[Entidade] = None, **kwargs) -> int:
        if n == 1 and alvo: return self.esp_curingas(alvo)
        if n == 2 and alvo: return self.esp_cortes_certeiros(alvo)
        if n == 3:          return self.esp_estilo_do_cacador()
        if n == 4 and alvo: return self.esp_marca_fatal(alvo)
        if n == 5:          return self.esp_aljava_da_ruina()
        if n == 6 and alvo: return self.esp_contaminar(alvo)
        if n == 7:          return self.esp_as_na_manga()
        return 0

# =============================== CURANDEIRO ===============================

class Curandeiro(Personagem):
    """Vida 20 | Ataque 0 | Defesa 3 | Mana 35 | Magia 8"""
    def __init__(self, nome: str):
        super().__init__(nome, Atributos(vida=20, ataque=0, defesa=3, mana=35, vida_max=20), ataque_magico=8)

    def ataque_basico(self, alvo: Entidade) -> int:
        # 0 mana | 1d6 - 2 (mín. 0)
        if not self.gastar_mana(0):
            return 0
        bruto = max(0, d6("Curandeiro - Ataque Básico") - 2 + self._atrib.ataque)
        log_dano_causado(self, alvo, bruto, "Ataque Básico")
        return alvo.receber_dano(bruto)

    # 4 ORIGINAIS
    def esp_capitulo_final(self, aliados: Optional[List[Personagem]]) -> int:
        # 3 mana | cura 1d6 a todos aliados
        if not self.gastar_mana(3):
            return 0
        if not aliados:
            logger.warning("(Sem aliados para curar.)")
            return 0
        cura = d6("Capítulo Final - Cura")
        for a in aliados:
            a.curar(cura)
        logger.info(f"📖 {self.nome} usa Capítulo Final e cura todos os aliados em {cura}.")
        return 0

    def esp_semente_engatilhada(self, aliado: Optional[Personagem]) -> int:
        # 5 mana | após 2 turnos, aliado recupera 1d20-5
        if not self.gastar_mana(5):
            return 0
        if not aliado:
            logger.warning("(Sem aliado alvo para a semente.)")
            return 0
        if hasattr(aliado, "efeitos"):
            aliado.efeitos["semente_turnos"] = 2
            log_efeito_aplicado(aliado, "Semente Engatilhada", 2)
        logger.info(f"🌱 {self.nome} planta uma semente curativa em {getattr(aliado, 'nome', 'aliado')}.")
        return 0

    def esp_ventos_revigorantes(self) -> int:
        # 15 mana | por 1 rodada reflete dano recebido
        if not self.gastar_mana(15):
            return 0
        self.efeitos["refletir_dano_turnos"] = max(self.efeitos.get("refletir_dano_turnos", 0), 1)
        logger.info(f"💨 {self.nome} invoca Ventos Revigorantes (reflexão por 1 rodada).")
        return 0

    def esp_golpe_de_misericordia(self, alvo: Entidade) -> int:
        # 0 mana | sacrifica a própria vida e causa 4d20
        if not self.gastar_mana(0):
            return 0
        dano = somar_dados(4, 20, "Golpe de Misericórdia - Dano")
        ef = alvo.receber_dano(dano)
        self._atrib.vida = 0
        logger.warning(f"💀 {self.nome} sacrifica-se em um Golpe de Misericórdia!")
        log_dano_causado(self, alvo, dano, "Golpe de Misericórdia")
        return ef

    # 3 ADICIONAIS
    def esp_hemofagia(self, alvo: Entidade) -> int:
        # 4 mana | 2d6 de dano e cura 1d6
        if not self.gastar_mana(4):
            return 0
        dano = somar_dados(2, 6, "Hemofagia - Dano")
        cura = d6("Hemofagia - Cura")
        self.curar(cura)
        logger.info(f"🩸 {self.nome} usa Hemofagia: causa {dano} e cura {cura}.")
        ef = alvo.receber_dano(dano)
        return ef

    def esp_transfusao_vital(self, aliado: Optional[Personagem]) -> int:
        # 30 mana | transfere 15 de vida para 1 aliado
        if not self.gastar_mana(30):
            return 0
        if not aliado:
            logger.warning("(Sem aliado para Transfusão Vital.)")
            return 0
        qtd = min(15, self._atrib.vida)
        self._attrib_vida_backup = self._atrib.vida  # opcional debug
        self._atrib.vida -= qtd
        aliado.curar(qtd)
        logger.info(f"💝 {self.nome} transfere {qtd} de vida para {getattr(aliado, 'nome', 'aliado')}.")
        return 0

    def esp_resplendor_cosmico(self, aliados: Optional[List[Personagem]]) -> int:
        # 15 mana | cura TODOS os aliados em 20
        if not self.gastar_mana(15):
            return 0
        if not aliados:
            logger.warning("(Sem aliados para Resplendor Cósmico.)")
            return 0
        for a in aliados:
            a.curar(20)
        logger.info(f"🌟 {self.nome} usa Resplendor Cósmico e cura todos os aliados em 20.")
        return 0

    def usar_especial(self, n: int, alvo: Optional[Entidade] = None,
                      aliado: Optional[Personagem] = None,
                      aliados: Optional[List[Personagem]] = None) -> int:
        if n == 1 and aliados is not None: return self.esp_capitulo_final(aliados)
        if n == 2 and aliado  is not None: return self.esp_semente_engatilhada(aliado)
        if n == 3:                         return self.esp_ventos_revigorantes()
        if n == 4 and alvo  is not None:   return self.esp_golpe_de_misericordia(alvo)
        if n == 5 and alvo  is not None:   return self.esp_hemofagia(alvo)
        if n == 6 and aliado is not None:  return self.esp_transfusao_vital(aliado)
        if n == 7 and aliados is not None: return self.esp_resplendor_cosmico(aliados)
        return 0

# ========================== HELPERS PÚBLICOS ==============================

# 1) Mapa de arquétipos
ARQUETIPOS: dict[str, type[Personagem]] = {
    "Guerreiro": Guerreiro,
    "Mago": Mago,
    "Arqueiro": Arqueiro,
    "Curandeiro": Curandeiro,
}

def criar_personagem(nome_arquetipo: str, nome: str) -> Personagem:
    """Cria a instância do arquétipo informado (fallback: Guerreiro)."""
    cls = ARQUETIPOS.get((nome_arquetipo or "").strip(), Guerreiro)
    return cls(nome or "Herói")

def custo_ataque_basico(p: Personagem) -> int:
    """Custo de mana do ataque básico (Mago=1; demais=0)."""
    return 1 if isinstance(p, Mago) else 0

def _num_especiais_desbloqueadas(nivel: int) -> int:
    """
    7 especiais no total. Começa com 4 "originais" e ganha +1 nos níveis 2, 4 e 6.
    """
    count = 4
    for marco in (2, 4, 6):
        if nivel >= marco:
            count += 1
    return min(7, count)

def especiais_do_personagem(p: Personagem, considerar_nivel: bool = True) -> List[tuple[int, str, int]]:
    """
    Retorna (id, nome, custo) das especiais — 7 por classe.
    As 4 primeiras são as "originais", seguidas das 3 "anteriores".
    """
    base_por_classe: dict[str, List[tuple[int, str, int]]] = {
        "Guerreiro": [
            # 4 originais
            (1, "Execução Pública", 7),
            (2, "Perseverança", 0),
            (3, "Golpe Trovejante", 1),
            (4, "Lâmina Ínfera", 2),
            # 3 anteriores
            (5, "Duro na Queda", 0),
            (6, "Determinação Mortal", 2),
            (7, "Golpe Estilhaçador", 0),
        ],
        "Mago": [
            (1, "Colapso Minguante", 15),
            (2, "Descarnar", 20),
            (3, "Distorção no Tempo", 0),
            (4, "Empurrão Sísmico", 8),
            (5, "Paradoxo", 3),
            (6, "Eletrocussão", 2),
            (7, "Explosão Florescente", 8),
        ],
        "Arqueiro": [
            (1, "Curingas", 8),
            (2, "Cortes Certeiros", 6),
            (3, "Estilo do Caçador", 10),
            (4, "Marca Fatal", 10),
            (5, "Aljava da Ruína", 1),
            (6, "Contaminar", 3),
            (7, "Ás na Manga", 7),
        ],
        "Curandeiro": [
            (1, "Capítulo Final", 3),
            (2, "Semente Engatilhada", 5),
            (3, "Ventos Revigorantes", 15),
            (4, "Golpe de Misericórdia", 0),
            (5, "Hemofagia", 4),
            (6, "Transfusão Vital", 30),
            (7, "Resplendor Cósmico", 15),
        ],
    }

    chave = p.__class__.__name__
    todos = base_por_classe.get(chave, [])
    if not considerar_nivel:
        return todos

    n = getattr(p, "nivel", 1)
    return todos[:_num_especiais_desbloqueadas(n)]

def preview_personagem(p: Personagem) -> dict[str, int]:
    """Dados principais para HUD/preview."""
    atr = getattr(p, "_atrib", None)
    return {
        "vida": getattr(atr, "vida", 0),
        "vida_max": getattr(atr, "vida_max", getattr(atr, "vida", 0)),
        "ataque": getattr(atr, "ataque", 0),
        "defesa": getattr(atr, "defesa", 0),
        "mana": getattr(atr, "mana", 0),
        "ataque_magico": getattr(p, "ataque_magico", 0),
    }