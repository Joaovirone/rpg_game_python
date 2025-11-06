from __future__ import annotations
from dataclasses import dataclass
from .personagem import Personagem
from .inimigo import Inimigo  # generate_horde
from rpg_game_python.dado import rolar_d6, rolar_d20
from .horda import generate_horde
from typing import List, Tuple, Dict

# colocar após os imports em models/missao.py
from typing import Any

def tick_efeitos_inicio_turno(entidade: Any) -> int:
    """
    Função utilitária para aplicar efeitos no início do turno de uma entidade
    (herói ou inimigo). Retorna o dano total aplicado neste tick (int).
    Prioriza chamar entidade.inicio_turno() se existir (reuso).
    Caso contrário, faz um fallback parecido com o inicio_turno do Personagem:
    - processa chaves "<prefix>_turnos" e "<prefix>_dano"
    - processa "regen" via "regen_valor"
    - decrementa contadores e remove quando zeram
    """
    # Se a entidade já implementa a lógica, delega para ela
    inicio_fn = getattr(entidade, "inicio_turno", None)
    if callable(inicio_fn):
        try:
            return inicio_fn()
        except Exception:
            # se a implementação da entidade falhar por algum motivo,
            # caímos no fallback abaixo
            pass

    # --- Fallback: processar efeitos manualmente ---
    if not hasattr(entidade, "efeitos") or entidade.efeitos is None:
        entidade.efeitos = {}

    dano_total = 0
    vida_max = getattr(getattr(entidade, "_atrib", None), "vida_max", None)

    for chave in list(entidade.efeitos.keys()):
        if chave == "turnos":
            continue
        if not chave.endswith("_turnos"):
            continue

        prefixo = chave[:-7]
        contador = entidade.efeitos.get(chave, 0)

        if contador <= 0:
            entidade.efeitos.pop(chave, None)
            entidade.efeitos.pop(f"{prefixo}_dano", None)
            entidade.efeitos.pop(f"{prefixo}_curar", None)
            continue

        # aplica dano por tick se existir
        dano_por_tick = entidade.efeitos.get(f"{prefixo}_dano")
        if dano_por_tick:
            if entidade.efeitos.get("invulneravel_turnos", 0) <= 0:
                if hasattr(entidade, "receber_dano") and callable(entidade.receber_dano):
                    aplicado = entidade.receber_dano(dano_por_tick)
                else:
                    atual = getattr(getattr(entidade, "_atrib", None), "vida", 0)
                    # tentar setar vida diretamente
                    try:
                        nova = max(0, atual - dano_por_tick)
                        setattr(entidade._atrib, "vida", nova)
                        aplicado = atual - nova
                    except Exception:
                        aplicado = 0
                dano_total += aplicado

        # aplica cura por tick (regen)
        curar_por_tick = entidade.efeitos.get(f"{prefixo}_curar")
        if curar_por_tick is None and prefixo == "regen":
            curar_por_tick = entidade.efeitos.get("regen_valor")

        if curar_por_tick:
            if hasattr(entidade, "curar") and callable(entidade.curar):
                try:
                    entidade.curar(curar_por_tick)
                except Exception:
                    atual = getattr(getattr(entidade, "_atrib", None), "vida", 0)
                    try:
                        nova = min(vida_max or atual, atual + curar_por_tick)
                        setattr(entidade._atrib, "vida", nova)
                    except Exception:
                        pass
            else:
                atual = getattr(getattr(entidade, "_atrib", None), "vida", 0)
                try:
                    nova = min(vida_max or atual, atual + curar_por_tick)
                    setattr(entidade._atrib, "vida", nova)
                except Exception:
                    pass

        # decrementa contador
        contador -= 1
        if contador <= 0:
            entidade.efeitos.pop(chave, None)
            entidade.efeitos.pop(f"{prefixo}_dano", None)
            entidade.efeitos.pop(f"{prefixo}_curar", None)
            if prefixo == "regen":
                entidade.efeitos.pop("regen_valor", None)
        else:
            entidade.efeitos[chave] = contador

    # decrementa contadores especiais
    for special in ("invulneravel_turnos", "nao_pode_atacar", "refletir_dano_turnos"):
        if special in entidade.efeitos:
            entidade.efeitos[special] = max(0, entidade.efeitos[special] - 1)
            if entidade.efeitos[special] == 0:
                entidade.efeitos.pop(special, None)

    # normaliza vida
    try:
        vida_atual = getattr(entidade._atrib, "vida", 0)
        if vida_atual < 0:
            setattr(entidade._atrib, "vida", 0)
        if vida_max is not None:
            if getattr(entidade._atrib, "vida", 0) > vida_max:
                setattr(entidade._atrib, "vida", vida_max)
    except Exception:
        pass

    return dano_total



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

    # 4 habilidades por classe (além do ataque básico)
    def _lista_especiais(self) -> List[Tuple[int, str, int]]:
        n = self.heroi.nivel
        base = {
            "Guerreiro": [
                (1, "Execução Pública", 7),
                (2, "Perseverança", 0),
                (3, "Golpe Trovejante", 1),
                (4, "Lâmina Ínfera", 2),
            ],
            "Mago": [
                (1, "Colapso Minguante", 15),
                (2, "Descarnar", 20),
                (3, "Distorção no Tempo", 0),
                (4, "Empurrão Sísmico", 8),
            ],
            "Arqueiro": [
                (1, "Curingas", 8),
                (2, "Cortes Certeiros", 6),
                (3, "Estilo do Caçador", 10),
                (4, "Marca Fatal", 10),
            ],
            "Curandeiro": [
                (1, "Capítulo Final", 3),
                (2, "Semente Engatilhada", 5),
                (3, "Ventos Revigorantes", 15),
                (4, "Golpe de Misericórdia", 0),
            ],
        }
        todos = base.get(self.heroi.__class__.__name__, [])
        desbloq = 1
        if n >= 2: desbloq += 1
        if n >= 4: desbloq += 1
        if n >= 6: desbloq += 1
        if n >= 8: desbloq += 1
        return todos[:desbloq]


class Missao(MissaoHordas):
    """
    Estrutura da missão com mecânica de combate (refatorada).
    """

    def __init__(self, inimigo: Inimigo, cenario: str, dificuldade: str, heroi: Personagem):
        super().__init__(heroi,cenario, dificuldade)
        self.inimigo = inimigo
        self.cenario = cenario
        self.dificuldade = dificuldade
        self.heroi = heroi

        # agora cada missão é um dict (nome + metadados futuros)
        self.missoes: List[Dict] = [
            self.missao_1(),
            self.missao_2(),
            self.missao_3(),
            self.missao_4(),
            self.missao_5()
        ]
        self.missao_atual = 0

    # Retornando dicts para permitir evolução futura (recompensa, objetivo, etc.)
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

    def _mostrar_hud(self, inimigo: Inimigo) -> None:
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
        print(f"HP {self.heroi.nome}: {self.heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")

    def mana_classe(self) -> None:
        custo_basico = {"Guerreiro": 0, "Mago": 1, "Arqueiro": 0, "Curandeiro": 0}.get(
            self.heroi.__class__.__name__, 0
        )
        mana_atual = getattr(self.heroi._atrib, "mana", 0)
        print(f"[1] Ataque básico — custo {custo_basico} "
              f"({'ficará: ' + str(mana_atual - custo_basico) if mana_atual >= custo_basico else 'insuf.'})")

        for i, (_, nome, custo) in enumerate(self._lista_especiais(), start=2):
            if mana_atual >= custo:
                print(f"[{i}] {nome} — custo {custo} (ficará: {mana_atual - custo})")
            else:
                print(f"[{i}] {nome} — custo {custo} (insuficiente)")

        print("[0] Fugir")

    # ----------------- Autoplay: heurística simples -----------------
    def decidir_acao_auto(self, inimigo: Inimigo) -> str:
        """
        Retorna a ação a ser tomada automaticamente:
        "1" = ataque básico, "2"/"3"/... = especiais, "0" = fugir (raro).
        Heurística simples:
         - Se Curandeiro e HP < 35% -> tenta curar (opção "2" por heurística)
         - Se mana suficiente para alguma especial disponível -> usa a 1ª especial possível
         - Senão, ataque básico
        """
        mana = getattr(self.heroi._atrib, "mana", 0)
        vida_atual = getattr(self.heroi._atrib, "vida", 0)
        vida_max = getattr(self.heroi._atrib, "vida_max", vida_atual) or vida_atual
        hp_frac = vida_atual / vida_max if vida_max else 1.0

        classe_nome = self.heroi.__class__.__name__

        # Prioridade: Curandeiro cura quando crítico
        if classe_nome == "Curandeiro" and hp_frac < 0.35:
            # se tiver mana para especial 2 (heurística), tente 2
            especs = self._lista_especiais()
            # procurar uma especial com 'cura' heurística (aqui assumimos id 2 ou 3)
            for i, (_id, nome, custo) in enumerate(especs):
                if mana >= custo and _id in {1, 2, 3}:
                    return str(2 + i)  # ação mapeada (2 + índice)

        # Para outras classes: preferir especial se mana permitir (primeira que couber)
        especs = self._lista_especiais()
        for i, (_id, nome, custo) in enumerate(especs):
            if mana >= custo and custo > 0:
                return str(2 + i)

        # fallback: ataque básico
        return "1"

    # ----------------- execução (com opção auto) -----------------
    def executar(self, auto: bool = False) -> ResultadoMissao:
        print("\nIniciando missão...")
        print(f"Cenário: {self.cenario} | Dificuldade: {self.dificuldade}")

        horda = generate_horde(self.cenario, self.dificuldade)
        encontros_vencidos = 0

        for idx, inimigo in enumerate(horda, start=1):
            print(f"\n=== Encontro {idx}/{len(horda)} — {inimigo.nome} ===")
            turno = 1

            while self.heroi.esta_vivo() and inimigo.esta_vivo():
                print(f"\n--- Turno {turno} ---")

                # controle de turno do herói (para Execução Pública)
                self.heroi.efeitos["turnos"] = self.heroi.efeitos.get("turnos", 0) + 1

                # efeitos no herói
                dano_tick = self.heroi.inicio_turno()
                if dano_tick:
                    print(f"(Efeitos) {self.heroi.nome} sofre {dano_tick} | {self.heroi.barra_hp()}")

                if self.heroi.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{self.heroi.nome} está impossibilitado de agir neste turno!")
                else:
                    self._mostrar_hud(inimigo)

                    if auto:
                        acao = self.decidir_acao_auto(inimigo)
                        print(f"[AUTO] Escolha: {acao}")
                    else:
                        acao = input("> ").strip()

                    dano_causado = 0
                    bloqueado = False

                    custo_basico = {"Guerreiro": 0, "Mago": 1, "Arqueiro": 0, "Curandeiro": 0}.get(
                        self.heroi.__class__.__name__, 0
                    )
                    mana_atual = getattr(self.heroi._atrib, "mana", 0)

                    # bloqueio por mana
                    if acao == "1":
                        if mana_atual < custo_basico:
                            print(f"Mana insuficiente para Ataque Básico ({mana_atual}/{custo_basico}).")
                            bloqueado = True
                    elif acao in {"2", "3", "4", "5"}:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        if 0 <= esp_idx < len(especs):
                            _id, nome, custo = especs[esp_idx]
                            if mana_atual < custo:
                                print(f"Mana insuficiente para {nome} ({mana_atual}/{custo}).")
                                bloqueado = True

                    # execução
                    if acao == "1" and not bloqueado:
                        dano_causado = self.heroi.ataque_basico(inimigo)
                    elif acao in {"2", "3", "4", "5"} and not bloqueado:
                        esp_idx = int(acao) - 2
                        especs = self._lista_especiais()
                        # proteção caso o jogador/auto escolha índice inválido
                        if not (0 <= esp_idx < len(especs)):
                            print("Especial inválida.")
                        else:
                            _id, nome, _c = especs[esp_idx]
                            # verificar Curandeiro por nome da classe para evitar import extra
                            if self.heroi.__class__.__name__ == "Curandeiro":
                                if _id == 1:
                                    self.heroi.habilidade_especial(_id, aliados=[])
                                elif _id == 2:
                                    self.heroi.habilidade_especial(_id, aliado=None)
                                elif _id == 3:
                                    self.heroi.habilidade_especial(_id)
                                elif _id == 4:
                                    dano_causado = self.heroi.habilidade_especial(4, alvo=inimigo)
                            else:
                                dano_causado = self.heroi.habilidade_especial(_id, alvo=inimigo)

                    elif acao == "0":
                        print("Você recuou da missão!")
                        return ResultadoMissao(False, encontros_vencidos, "Fugiu da missão.")
                    else:
                        if not bloqueado:
                            print("Ação inválida.")

                    if dano_causado:
                        print(f"Você causou {dano_causado}. HP do {inimigo.nome}: {inimigo.barra_hp()}")

                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} foi derrotado!")
                    encontros_vencidos += 1
                    break

                # efeitos no inimigo
                dano_tick_i = tick_efeitos_inicio_turno(inimigo)
                if dano_tick_i:
                    print(f"(Efeitos) {inimigo.nome} sofre {dano_tick_i} | {inimigo.barra_hp()}")
                if not inimigo.esta_vivo():
                    print(f"{inimigo.nome} caiu pelos efeitos!")
                    encontros_vencidos += 1
                    break

                if inimigo.efeitos.get("nao_pode_atacar", 0) > 0:
                    print(f"{inimigo.nome} está atordoado e não ataca.")
                else:
                    # NÃO subtrair defesa aqui; Entidade.receber_dano aplica defesa.
                    dano_in = max(0, rolar_d6() + inimigo._atrib.ataque)

                    # Invulnerável anula dano direto (checado na missão)
                    if self.heroi.efeitos.get("invulneravel_turnos", 0) > 0:
                        print(f"{self.heroi.nome} está invulnerável e não sofre dano.")
                        dano_in = 0

                    aplicado = self.heroi.receber_dano(dano_in)
                    print(f"{inimigo.nome} causa {aplicado}. Seu HP: {self.heroi.barra_hp()} (Mana: {getattr(self.heroi._atrib, 'mana', 0)})")

                    # Reflexão
                    if aplicado > 0 and self.heroi.efeitos.get("refletir_dano_turnos", 0) > 0:
                        refle = inimigo.receber_dano(aplicado)
                        print(f"Ventos Revigorantes refletem {refle} ao {inimigo.nome}! HP: {inimigo.barra_hp()}")

                turno += 1

            if not self.heroi.esta_vivo():
                print("\nVocê foi derrotado... Missão falhou.")
                return ResultadoMissao(False, encontros_vencidos, "Derrotado nas hordas.")

        print("\nParabéns! Você venceu todas as hordas da missão!")
        return ResultadoMissao(True, encontros_vencidos, "Vitória!")
