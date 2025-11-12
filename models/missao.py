# models/missao.py
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional

from models.personagem import (
    Personagem,
    especiais_do_personagem,      # lista (id, nome, custo) conforme o NÍVEL
    custo_ataque_basico,          # custo do ataque básico por classe
    tick_efeitos_inicio_turno,    # aplica efeitos (fonte única)
)
from models.inimigo import Inimigo, generate_horde
from dado import d6, d20
from utils.logger import logger


@dataclass
class ResultadoMissao:
    venceu: bool
    encontros_vencidos: int
    detalhes: str = ""


class MissaoHordas:
    def __init__(self, heroi: Personagem, cenario: str, dificuldade: str):
        self.heroi = heroi
        self.cenario = cenario
        self.dificuldade = dificuldade

    # Agora a fonte da verdade de especiais vem de models.personagem
    def _lista_especiais(self) -> List[Tuple[int, str, int]]:
        """
        Retorna a lista de especiais (id, nome, custo) conforme o nível do herói.
        - No nível baixo, apenas as 4 "originais" ficam disponíveis (liberadas por nível).
        - Ao upar, as demais aparecem até fechar as 7 especiais (básico + 7 = 8 ações).
        """
        return especiais_do_personagem(self.heroi, considerar_nivel=True)

    def _mostrar_hud(self, inimigo: Inimigo) -> None:
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
        print(f"HP {self.heroi.nome}: {self.heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")

        # Ataque básico (sempre opção 1)
        custo_basico = custo_ataque_basico(self.heroi)
        if mana_atual >= custo_basico:
            print(f"[1] Ataque básico — custo {custo_basico} (ficará: {mana_atual - custo_basico})")
        else:
            print(f"[1] Ataque básico — custo {custo_basico} (insuficiente)")

        # Especiais (id lógicos começam em 1, mas no menu são 2..8)
        especs = self._lista_especiais()
        for i, (_id, nome, custo) in enumerate(especs, start=2):
            if mana_atual >= custo:
                print(f"[{i}] {nome} — custo {custo} (ficará: {mana_atual - custo})")
            else:
                print(f"[{i}] {nome} — custo {custo} (insuficiente)")
        print("[0] Fugir")

    # ----------------- Autoplay simples -----------------
    def decidir_acao_auto(self, inimigo: Inimigo) -> str:
        """
        Retorna: "1" = básico, "2"/"3"/... = especiais, "0" = fugir (raro).
        Heurística:
         - Se Curandeiro com HP < 35% tenta uma especial "defensiva" entre as disponíveis.
         - Caso haja mana para alguma especial disponível, usa a primeira.
         - Senão, ataque básico.
        """
        mana = getattr(self.heroi._atrib, "mana", 0)
        vida_atual = getattr(self.heroi._atrib, "vida", 0)
        vida_max = getattr(self.heroi._atrib, "vida_max", vida_atual) or vida_atual
        hp_frac = vida_atual / vida_max if vida_max else 1.0

        classe_nome = self.heroi.__class__.__name__
        especs = self._lista_especiais()

        if classe_nome == "Curandeiro" and hp_frac < 0.35:
            # tenta uma entre (Capítulo Final, Semente, Ventos) se estiver liberada
            defensivos = {"Capítulo Final", "Semente Engatilhada", "Ventos Revigorantes"}
            for i, (_id, nome, custo) in enumerate(especs, start=2):
                if nome in defensivos and mana >= custo:
                    return str(i)

        for i, (_id, nome, custo) in enumerate(especs, start=2):
            if mana >= custo and custo > 0:
                return str(i)

        return "1"

    # ----------------- Execução (com auto) -----------------
    def executar(self, auto: bool = False) -> ResultadoMissao:
        encontros_vencidos = 0
        logger.info("🚀 Iniciando missão...")
        logger.info(f"📍 Cenário: {self.cenario} | 🎯 Dificuldade: {self.dificuldade}")
        logger.info(f"🧙 Herói: {self.heroi.nome} (Nível {self.heroi.nivel})")

        try:
            horda = generate_horde(self.cenario, self.dificuldade, getattr(self, "missao", None))
            encontros_vencidos = 0
        except TypeError:
            # Versão que aceita apenas (cenario, dificuldade)
            horda = generate_horde(self.cenario, self.dificuldade)

        for idx, inimigo in enumerate(horda, start=1):

            is_boss = getattr(inimigo, "efeitos", {}).get("is_boss", False)
            titulo = f"{inimigo.nome} (CHEFE)" if is_boss else inimigo.nome
            print(f"\n=== Encontro {idx}/{len(horda)} — {inimigo.nome} ===")
            logger.info(f"⚔️ Iniciando encontro {idx}/{len(horda)}: {titulo}")
            
            if is_boss:
                logger.warning(f"👑 CHEFE ENCONTRADO: {inimigo.nome}!")
                
            turno = 1

            while self.heroi.esta_vivo() and inimigo.esta_vivo():
                print(f"\n--- Turno {turno} ---")
                logger.debug(f"🔄 Turno {turno} iniciado")

                # Controle de turno do herói (p/ Execução Pública, etc.)
                self.heroi.efeitos["turnos"] = self.heroi.efeitos.get("turnos", 0) + 1

                # Efeitos no HERÓI (usa a lógica central do personagem)
                dano_tick = self.heroi.inicio_turno()
                if dano_tick:
                    print(f"(Efeitos) {self.heroi.nome} sofre {dano_tick} | {self.heroi.barra_hp()}")
                    logger.info(f"💥 Efeitos em {self.heroi.nome}: {dano_tick} de dano")

                if self.heroi.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{self.heroi.nome} está impossibilitado de agir neste turno!")
                else:
                    self._mostrar_hud(inimigo)

                    acao = self.decidir_acao_auto(inimigo) if auto else input("> ").strip()
                    dano_causado = 0
                    bloqueado = False

                    mana_atual = getattr(self.heroi._atrib, "mana", 0)
                    custo_basico = custo_ataque_basico(self.heroi)

                    # Bloqueio por mana (básico e especiais)
                    if acao == "1":
                        if mana_atual < custo_basico:
                            print(f"Mana insuficiente para Ataque Básico ({mana_atual}/{custo_basico}).")
                            bloqueado = True
                    elif acao.isdigit() and int(acao) >= 2:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        if 0 <= esp_idx < len(especs):
                            _id, nome, custo = especs[esp_idx]
                            if mana_atual < custo:
                                print(f"Mana insuficiente para {nome} ({mana_atual}/{custo}).")
                                bloqueado = True
                        else:
                            print("Especial inválida.")
                            bloqueado = True

                    # Execução
                    if acao == "1" and not bloqueado:
                        dano_causado = self.heroi.ataque_basico(inimigo)

                    elif acao.isdigit() and int(acao) >= 2 and not bloqueado:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        _id, nome, _c = especs[esp_idx]

                        # Curandeiro tem assinaturas variadas; demais usam alvo=Inimigo
                        if self.heroi.__class__.__name__ == "Curandeiro":
                            if _id == 1:          # Capítulo Final (cura grupo)
                                self.heroi.usar_especial(1, aliados=[])
                            elif _id == 2:        # Semente Engatilhada
                                self.heroi.usar_especial(2, aliado=None)
                            elif _id == 3:        # Ventos Revigorantes
                                self.heroi.usar_especial(3)
                            elif _id in (4, 5):   # Golpe de Misericórdia / Hemofagia
                                dano_causado = self.heroi.usar_especial(_id, alvo=inimigo)
                            elif _id == 6:        # Transfusão Vital
                                self.heroi.usar_especial(6, aliado=None)
                            elif _id == 7:        # Resplendor Cósmico
                                self.heroi.usar_especial(7, aliados=[])
                        else:
                            dano_causado = self.heroi.usar_especial(_id, alvo=inimigo)

                    elif acao == "0":
                        print("Você recuou da missão!")
                        logger.warning(f"🏃 {self.heroi.nome} fugiu da missão!")
                        return ResultadoMissao(False, encontros_vencidos, "Fugiu da missão.")
                    else:
                        if not bloqueado:
                            print("Ação inválida.")

                    if dano_causado:
                        print(f"Você causou {dano_causado}. HP do {inimigo.nome}: {inimigo.barra_hp()}")

                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} foi derrotado!")
                    logger.info(f"💀 {inimigo.nome} foi derrotado!")
                    encontros_vencidos += 1
                    
                    # XP por derrotar inimigo
                    xp_ganho = 10 * self.heroi.nivel
                    logs_xp = self.heroi.ganhar_xp(xp_ganho)
                    for log in logs_xp:
                        logger.info(f"📈 {log}")
                    
                    break

                # Efeitos no INIMIGO (usa helper central)
                dano_tick_i = tick_efeitos_inicio_turno(inimigo)
                if dano_tick_i:
                    print(f"(Efeitos) {inimigo.nome} sofre {dano_tick_i} | {inimigo.barra_hp()}")
                    logger.info(f"💥 Efeitos em {inimigo.nome}: {dano_tick_i} de dano")
                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} caiu pelos efeitos!")
                    logger.info(f"💀 {inimigo.nome} caiu pelos efeitos!")
                    encontros_vencidos += 1
                    
                    # XP por derrotar inimigo
                    xp_ganho = 10 * self.heroi.nivel
                    logs_xp = self.heroi.ganhar_xp(xp_ganho)
                    for log in logs_xp:
                        logger.info(f"📈 {log}")
                    
                    break

                if inimigo.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{inimigo.nome} está atordoado e não ataca.")
                    logger.info(f"😵 {inimigo.nome} está atordoado e não ataca.")
                else:
                    # Dano do inimigo (Entidade.receber_dano já considera defesa do herói)
                    dano_in = max(0, d6(f"{inimigo.nome} - Ataque") + inimigo._atrib.ataque)
                    logger.debug(f"🎲 {inimigo.nome} rola ataque: {dano_in - inimigo._atrib.ataque} + {inimigo._atrib.ataque} = {dano_in}")

                    # Invulnerável anula dano direto
                    if self.heroi.efeitos.get("invulneravel_turnos", 0) > 0:
                        print(f"{self.heroi.nome} está invulnerável e não sofre dano.")
                        logger.info(f"🛡️ {self.heroi.nome} está invulnerável e não sofre dano.")
                        dano_in = 0

                    aplicado = self.heroi.receber_dano(dano_in)
                    print(f"{inimigo.nome} causa {aplicado}. Seu HP: {self.heroi.barra_hp()} "
                          f"(Mana: {getattr(self.heroi._atrib, 'mana', 0)})")
                    
                    if aplicado > 0:
                        logger.info(f"⚔️ {inimigo.nome} causa {aplicado} de dano em {self.heroi.nome}")

                    # Reflexão de dano
                    if aplicado > 0 and self.heroi.efeitos.get("refletir_dano_turnos", 0) > 0:
                        refle = inimigo.receber_dano(aplicado)
                        print(f"Ventos Revigorantes refletem {refle} ao {inimigo.nome}! HP: {inimigo.barra_hp()}")
                        logger.info(f"💨 Ventos Revigorantes refletem {refle} de dano para {inimigo.nome}")

                turno += 1

            if not self.heroi.esta_vivo():
                print("\nVocê foi derrotado... Missão falhou.")
                logger.warning(f"💀 {self.heroi.nome} foi derrotado! Missão falhou.")
                return ResultadoMissao(False, encontros_vencidos, "Derrotado nas hordas.")

        print("\nParabéns! Você venceu todas as hordas da missão!")
        logger.info(f"🏆 {self.heroi.nome} venceu todas as hordas da missão!")
        return ResultadoMissao(True, encontros_vencidos, "Vitória!")


class Missao(MissaoHordas):
    """
    Estrutura da missão com mecânica de combate (usa helpers centrais).
    """
    def __init__(self, inimigo: Inimigo, heroi: Personagem, cenario: str, dificuldade: str, missao: dict | None = None):
        super().__init__(heroi, cenario, dificuldade)
        self.inimigo = inimigo
        self.missao = missao

        # Representação leve das missões (futuro: recompensas, objetivos, etc.)
        self.missoes: List[Dict] = [
            self.missao_1(),
            self.missao_2(),
            self.missao_3(),
            self.missao_4(),
            self.missao_5(),
        ]
        self.missao_atual = 0

    # Retornando dicts para permitir evolução futura
    def missao_1(self) -> Dict:
        return {"nome": "Matar Ladrões", "objetivo": "Eliminar ladrões no vilarejo", "recompensa": 50}

    def missao_2(self) -> Dict:
        return {"nome": "Matar Goblins", "objetivo": "Eliminar goblins na caverna", "recompensa": 75}

    def missao_3(self) -> Dict:
        return {"nome": "Matar Golens", "objetivo": "Destruir golens de pedra", "recompensa": 120}

    def missao_4(self) -> Dict:
        return {"nome": "Matar Elfos", "objetivo": "Conter elfos hostis", "recompensa": 150}

    def missao_5(self) -> Dict:
        return {"nome": "Matar Dragões", "objetivo": "Derrotar dragões ancestrais", "recompensa": 500}