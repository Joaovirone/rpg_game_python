from __future__ import annotations
import json
import os
import glob
from utils.logger import Logger
from models.inventario import Drop_rate, Inventario, Item
from models.base import Entidade
from models.inimigo import Inimigo
from models.personagem import (
    Personagem,
    criar_personagem,              # fábrica central (models.personagem)
    especiais_do_personagem,       # lista (id, nome, custo) por nível
    custo_ataque_basico,           # custo do ataque básico por classe
    preview_personagem,            # helper para exibir stats
)
from models.missao import Missao, ResultadoMissao
from dado import d6, d20   # nomes corretos


class Jogo:
    """
    Estrutura base com menus e submenus.
    - Coleta nome/arquétipo, mas NÃO instancia classes aqui manualmente.
    - Criação concreta é delegada a models.personagem.criar_personagem(...).
    - O HUD do turno é local deste arquivo (_mostrar_hud_turno) e usa helpers do módulo de personagem.
    - Missões usam d20 para qualidade da ação e d6 para dano.
    """

    def __init__(self) -> None:
        self.logger = Logger()
        self.logger.info("Iniciando o jogo...")

        # Somente escolhas do jogador; nada de instanciar aqui.
        self.personagem = {
            "nome": None,         # str
            "arquetipo": None,    # "Guerreiro" | "Mago" | "Arqueiro" | "Curandeiro"
        }

        self.missao_config = {
            "dificuldade": None,  # "Fácil" | "Média" | "Difícil"
            "cenario": None,      # "Trilha" | "Floresta" | "Caverna" | "Ruínas"
            "missao": None,       # rótulo/string da missão (simples)
        }

        self.inven = Inventario()
        self.item = None
        self.drop_de_itens = None
        self._ultimo_save = None
        self._ultimo_load = None

        # Pasta de saves
        self.save_dir = os.path.join(os.getcwd(), "saves")
        os.makedirs(self.save_dir, exist_ok=True)

    # ------------------------ util internos de UI -------------------------

    def _nivel_requerido_por_indice(self, idx: int) -> int:
        """
        Mapa de desbloqueio (posição na lista de especiais):
        1..4 => nível 1 | 5 => nível 2 | 6 => nível 4 | 7 => nível 6
        """
        if idx <= 4:
            return 1
        return {5: 2, 6: 4, 7: 6}.get(idx, 10)

    def _descricao_habilidade(self, cls_nome: str, nome_hab: str) -> str:
        """
        Descrições curtas das habilidades por classe.
        Apenas texto (apresentação); lógica real está em models.personagem.
        """
        desc: dict[str, dict[str, str]] = {
            "Guerreiro": {
                "Execução Pública": "5d6 com crítico garantido +3 (após 4 turnos).",
                "Perseverança": "Fica invulnerável por 1 turno.",
                "Golpe Trovejante": "1d20 + ataque de dano direto.",
                "Lâmina Ínfera": "3d6 e aplica sangramento 1d6/turno por 2 turnos.",
                "Duro na Queda": "Ganha +1d6 no próximo ataque.",
                "Determinação Mortal": "Cura 1d20 de vida.",
                "Golpe Estilhaçador": "Próximo ataque com crítico garantido.",
            },
            "Mago": {
                "Colapso Minguante": "6d6 de dano arcano.",
                "Descarnar": "3d20 e aplica sangramento 1d6/turno por 2 turnos.",
                "Distorção no Tempo": "Recupera 50 de mana.",
                "Empurrão Sísmico": "3d6 e alvo perde 1 turno (1x por missão).",
                "Paradoxo": "5d6 de dano.",
                "Eletrocussão": "3d6 e 1d6-1 por turno por 2 turnos.",
                "Explosão Florescente": "10d6 e não age no próximo turno.",
            },
            "Arqueiro": {
                "Curingas": "5d6 de dano.",
                "Cortes Certeiros": "Aplica sangramento 1d6/turno por 5 turnos.",
                "Estilo do Caçador": "Próximo tiro vira 1d20 com crítico.",
                "Marca Fatal": "Aplica 1d6/turno por 7 turnos.",
                "Aljava da Ruína": "Ganha +(1d6+2) no próximo ataque.",
                "Contaminar": "Aplica veneno (2 de dano) por 3 turnos.",
                "Ás na Manga": "Próximo ataque crítico garantido +10.",
            },
            "Curandeiro": {
                "Capítulo Final": "Cura 1d6 todos os aliados.",
                "Semente Engatilhada": "Após 2 turnos, aliado cura 1d20-5.",
                "Ventos Revigorantes": "Reflete o dano recebido por 1 rodada.",
                "Golpe de Misericórdia": "Causa 4d20 e sacrifica a própria vida.",
                "Hemofagia": "Causa 2d6 e cura 1d6.",
                "Transfusão Vital": "Transfere 15 de vida a um aliado.",
                "Resplendor Cósmico": "Cura todos os aliados em 20.",
            },
        }
        return desc.get(cls_nome, {}).get(nome_hab, "")

    # ======================================================================
    # PREVIEW do personagem (apenas exibe; instancia via fábrica e descarta)
    # ======================================================================
    def mostrar_personagem(self) -> None:
        """Mostra um preview do personagem com stats, XP e habilidades (inclui bloqueadas com aviso)."""
        if not self.personagem.get("nome") or not self.personagem.get("arquetipo"):
            print("Defina nome e arquétipo para visualizar o personagem.")
            return

        # Instância temporária via fábrica (sem criar nada "na mão" aqui)
        heroi_tmp: Personagem = criar_personagem(
            self.personagem["arquetipo"],
            self.personagem["nome"]
        )
        stats = preview_personagem(heroi_tmp)

        # ---- Cabeçalho / Stats ----
        print("\n=== Preview do Personagem ===")
        print(f"Nome: {heroi_tmp.nome} | Classe: {heroi_tmp.__class__.__name__} | Nível: {heroi_tmp.nivel}")
        print(f"🩸 Vida: {stats['vida']}/{stats['vida_max']}  |  🛡️ Defesa: {stats['defesa']}")
        print(f"⚔️ Ataque: {stats['ataque']}  |  🔮 Mana: {stats['mana']}  |  ✨ Magia: {stats['ataque_magico']}")

        # ---- XP / Progressão ----
        if heroi_tmp.nivel >= 10:
            print("📈 XP: Nível máximo (10) atingido.")
        else:
            xp_atual = getattr(heroi_tmp, "xp", 0)
            xp_prox = 100 * heroi_tmp.nivel
            faltam = max(0, xp_prox - xp_atual)
            print(f"📈 XP: {xp_atual}/{xp_prox}  (faltam {faltam} para o nível {heroi_tmp.nivel + 1})")

        # ---- Ataque básico ----
        custo_bas = custo_ataque_basico(heroi_tmp)
        print(f"\nAtaque básico: custo {custo_bas} mana (sempre disponível)")

        # ---- Habilidades (todas) com bloqueio por nível + descrição ----
        print("\nHabilidades da classe:")
        todas = especiais_do_personagem(heroi_tmp, considerar_nivel=False)
        cls_nome = heroi_tmp.__class__.__name__

        for i, (_esp_id, nome, custo) in enumerate(todas, start=1):
            req = self._nivel_requerido_por_indice(i)
            disponivel = heroi_tmp.nivel >= req
            desc = self._descricao_habilidade(cls_nome, nome)
            status = "Disponível" if disponivel else f"Bloqueada: requer nível {req}"
            print(f" - [{i}] {nome} — custo {custo}  ({status})")
            if desc:
                print(f"     • {desc}")

        print("================================")

    # ======================================================================
    # HUD do turno (LOCAL; usa helpers do módulo de personagem)
    # ======================================================================
    def _mostrar_hud_turno(self, heroi: Personagem, inimigo: Entidade) -> None:
        mana_atual = getattr(heroi._atrib, "mana", 0)
        print(f"HP {heroi.nome}: {heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")

        # Ataque básico: custo por classe (helper)
        custo_bas = custo_ataque_basico(heroi)
        if mana_atual >= custo_bas:
            print(f"[1] Ataque normal (d20) — custo {custo_bas} (ficará: {mana_atual - custo_bas})")
        else:
            print(f"[1] Ataque normal (d20) — custo {custo_bas} (insuficiente)")

        # Especiais liberadas (menu 2..8)
        liberadas = especiais_do_personagem(heroi, considerar_nivel=True)
        for i, (_esp_id, nome, custo) in enumerate(liberadas, start=2):
            if mana_atual >= custo:
                print(f"[{i}] {nome} — custo {custo} (ficará: {mana_atual - custo})")
            else:
                print(f"[{i}] {nome} — custo {custo} (insuficiente)")

        # Especiais bloqueadas (apenas aviso; não selecionáveis)
        todas = especiais_do_personagem(heroi, considerar_nivel=False)
        if len(liberadas) < len(todas):
            bloqueadas_txt = []
            for i, (_esp_id, nome, _c) in enumerate(todas, start=1):
                req = self._nivel_requerido_por_indice(i)
                if heroi.nivel < req:
                    bloqueadas_txt.append(f"{nome} (requer nível {req})")
            if bloqueadas_txt:
                print("Bloqueadas (não selecionáveis): " + "; ".join(bloqueadas_txt))

        print("[0] Fugir")

    # ======================================================================
    # Ataque normal com d20 para decidir a qualidade da ação
    # 1–5: péssima (erra) | 6–10: normal | 11–15: boa (+1) | 16–20: excelente (crítico)
    # ======================================================================
    def _ataque_normal_com_d20(self, heroi: Personagem, inimigo: Entidade) -> int:
        r = d20("Ataque Normal - Qualidade")
        self.logger.info(f"🎯 {heroi.nome} rola d20 para ataque normal: {r}")

        if 1 <= r <= 5:
            self.logger.warning("💥 Ação PÉSSIMA: você erra o golpe. Sem dano.")
            return 0

        # dano base físico: 1d6 + ataque do herói
        base_roll = d6("Ataque Normal - Dano Base")
        base = base_roll + heroi._atrib.ataque

        if 6 <= r <= 10:
            dano = base
            self.logger.info(f"🎯 Ação NORMAL: dano base = {base_roll} + {heroi._atrib.ataque} = {base}")
        elif 11 <= r <= 15:
            dano = base + 1
            self.logger.info(f"🎯 Ação BOA: {base} + 1 = {dano}")
        else:  # 16–20
            dano = base * 2
            self.logger.info(f"🎯 Ação EXCELENTE (crítico): {base} x 2 = {dano}")

        efetivo = inimigo.receber_dano(dano)
        if efetivo != dano:
            self.logger.info(f"🛡️ Defesa do {inimigo.nome} reduziu o dano de {dano} para {efetivo}")
        else:
            self.logger.info(f"⚔️ Dano total: {efetivo}")
        
        return efetivo

    # ============================ MENUS ===================================

    def menu_criar_personagem(self) -> None:
        self.logger.info("Iniciando menu Criação de Personagem...")

        while True:
            print("\n=== Criar Personagem ===")
            print(f"Nome atual: {self.personagem['nome'] or '(não definido)'}")
            print(f"Arquétipo:  {self.personagem['arquetipo'] or '(não definido)'}")
            print("[1] Definir nome")
            print("[2] Escolher arquétipo")
            print("[3] Confirmar criação")
            print("[4] Mostrar personagem (preview)")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._definir_nome()
            elif op == "2":
                self._escolher_arquetipo()
            elif op == "3":
                self._confirmar_criacao()
            elif op == "4":
                self.mostrar_personagem()
            elif op == "9":
                self._ajuda_criar_personagem()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _definir_nome(self) -> None:
        self.logger.info("Iniciando definição de nome do personagem...")
        nome = input("Digite o nome do personagem: ").strip()
        if nome:
            self.personagem["nome"] = nome
            self.logger.info(f"✅ Nome definido: {nome}")
            print(f"Nome definido: {nome}")
        else:
            print("Nome não alterado.")

    def _escolher_arquetipo(self) -> None:
        self.logger.info("Iniciando menu Definição de Arquétipo...")
        print("\nArquétipos disponíveis:")
        print("[1] Guerreiro")
        print("[2] Mago")
        print("[3] Arqueiro")
        print("[4] Curandeiro")
        print("[5] Personalizado (usa Guerreiro por padrão)")
        escolha = input("> ").strip()

        mapa = {"1": "Guerreiro", "2": "Mago", "3": "Arqueiro", "4": "Curandeiro", "5": "Personalizado"}
        arq = mapa.get(escolha)
        if arq:
            self.personagem["arquetipo"] = arq
            self.logger.info(f"✅ Arquétipo definido: {arq}")
            print(f"Arquétipo definido: {arq}")
        else:
            print("Opção inválida. Arquétipo não alterado.")

    def _confirmar_criacao(self) -> None:
        self.logger.info("Executando confirmação da criação do personagem...")
        if not self.personagem["nome"]:
            print("Defina um nome antes de confirmar a criação.")
            return
        if not self.personagem["arquetipo"]:
            print("Escolha um arquétipo antes de confirmar a criação.")
            return

        print("\nPersonagem configurado!")
        print(f"Nome: {self.personagem['nome']} | Arquétipo: {self.personagem['arquetipo']}")
        self.logger.info(f"🎉 Personagem criado: {self.personagem['nome']} ({self.personagem['arquetipo']})")

        # Mostra o preview imediatamente (sem manter instância)
        self.mostrar_personagem()

    def _ajuda_criar_personagem(self) -> None:
        self.logger.info("Iniciando menu Ajuda da criação do personagem...")
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo.")
        print("- O jogo NÃO cria a instância aqui; isso só acontece ao iniciar a missão.")
        print("- As classes têm atributos/habilidades diferentes.")

    # ================================ MISSÃO ===============================

    def menu_missao(self) -> None:
        self.logger.info("Iniciando menu Missões...")

        while True:
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão")
            print("[5] Escolher missão")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._escolher_dificuldade()
            elif op == "2":
                self._escolher_cenario()
            elif op == "3":
                self._preview_missao()
            elif op == "4":
                self._iniciar_missao()
                print("Retornando ao menu inicial.....")
                break
            elif op == "5":
                self.escolher_missao()
            elif op == "9":
                self._ajuda_missao()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def escolher_missao(self) -> None:
        self.logger.info("Iniciando menu Escolha de missões...")
        """
                Gera dinamicamente opções de missão com base no cenário selecionado.
                Usa plan_for_scenario em models.inimigo para descobrir minions/chefe.
                """
        # Verifica se cenário/dificuldade foram escolhidos
        cen = self.missao_config.get("cenario")
        dif = self.missao_config.get("dificuldade")
        if not cen or not dif:
            print("Escolha um cenário e uma dificuldade antes de selecionar uma missão.")
            return

        # import local (evita import circular no topo)
        try:
            from models.inimigo import plan_for_scenario
        except Exception:
            print("Erro ao acessar configuração de inimigos. Verifique models.inimigo.")
            return

        (min1, min2), chefe = plan_for_scenario(cen)

        print("Escolha de Missões:")
        print("⚠️ As escolhas das missões tem como finalidade o usuário escolher qual inimigo combater primeiro!")
        print()
        print(f"[1] Eliminar {min1}")
        print(f"[2] Eliminar {min2}")
        print(f"[3] Eliminar CHEFE: {chefe}")
        print("[4] Horda completa (Minions + Chefe)")
        print("[0] Voltar")

        op = input("> ").strip()

        # estimativa simples de recompensa (pode ser refinada)
        recompensa_base = {"Fácil": 50, "Média": 100, "Difícil": 200}.get(dif, 50)

        if op == "1":
            miss = {"nome": f"Matar {min1}", "objetivo": f"Eliminar {min1.lower()}s em {cen}",
                    "recompensa": recompensa_base}
        elif op == "2":
            miss = {"nome": f"Matar {min2}", "objetivo": f"Eliminar {min2.lower()}s em {cen}",
                    "recompensa": int(recompensa_base * 1.2)}
        elif op == "3":
            miss = {"nome": f"Matar {chefe}", "objetivo": f"Derrotar o chefe {chefe} em {cen}",
                    "recompensa": int(recompensa_base * 3)}
        elif op == "4":
            miss = {"nome": "Horda Completa", "objetivo": f"Enfrentar todos os inimigos em {cen} (minions + chefe)",
                    "recompensa": int(recompensa_base * 2)}
        elif op == "0":
            print("Voltando...")
            return
        else:
            print("Opção inválida.")
            return

        self.missao_config["missao"] = miss
        

    def _escolher_dificuldade(self) -> None:
        self.logger.info("Iniciando Definição de dificuldade...")
        print("\nDificuldades:")
        print("[1] Fácil")
        print("[2] Média")
        print("[3] Difícil")
        op = input("> ").strip()
        mapa = {"1": "Fácil", "2": "Média", "3": "Difícil"}
        escolha = mapa.get(op)
        if escolha:
            self.missao_config["dificuldade"] = escolha
            self.logger.info(f"✅ Dificuldade definida: {escolha}")
            print(f"Dificuldade definida: {escolha}")
        else:
            print("Opção inválida.")

    def _escolher_cenario(self) -> None:
        self.logger.info("Iniciando Definição de cenários(mapa)...")
        print("\nCenários:")
        print("[1] Trilha")
        print("[2] Floresta")
        print("[3] Caverna")
        print("[4] Ruínas")
        op = input("> ").strip()
        mapa = {"1": "Trilha", "2": "Floresta", "3": "Caverna", "4": "Ruínas"}
        cen = mapa.get(op)
        if cen:
            self.missao_config["cenario"] = cen
            self.logger.info(f"✅ Cenário definido: {cen}")
            print(f"Cenário definido: {cen}")
        else:
            print("Opção inválida.")

    def _preview_missao(self) -> None:
        self.logger.info("Iniciando Preview de Missões")

        borda = "=" * 35

        dificuldade = self.missao_config['dificuldade'] or '(não definida)'
        cenario = self.missao_config['cenario'] or '(não definido)'
        missao = self.missao_config["missao"] or '(não definido)'

        missao_config_valor = self.missao_config["missao"]
        
        if isinstance(missao_config_valor, dict):
            nome_missao = missao_config_valor.get('nome', 'Missão Não Definida')
        else:
            nome_missao = missao_config_valor or 'N/A'

        print(f"\n{borda}")
        print("📜 **PRÉ-VISUALIZAÇÃO DA MISSÃO**")
        print(f"{borda}")
        
        
        print(f"| 💪 Dificuldade: **{dificuldade.capitalize()}**")
        print(f"| 📍 Cenário:     **{cenario.capitalize()}**")
        print(f"| 🎯 Missão:      **{nome_missao.capitalize()}**")
        print("")
       
        print("-" * 35)
        print("ℹ️ OBS: Hordas e chefe serão gerados conforme cenário e dificuldade.")
        print(f"{borda}")

        

    def _ajuda_missao(self) -> None:
        self.logger.info("Iniciando menu Ajuda de missões...")
        print("\nAjuda — Missão")
        print("- Em 'Iniciar missão', o ataque normal usa d20 para decidir a qualidade:")
        print("  1–5: péssima (erra), 6–10: normal, 11–15: boa (+1), 16–20: excelente (crítico).")
        print("- O HUD (local do jogo.py) mostra Mana e o custo dos especiais (bloqueia sem mana).")

    # ========================= SALVAR/CARREGAR ==============================

    def menu_salvar(self) -> None:
        self.logger.info("Iniciando menu Salvar progresso do jogo...")
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido")
            print("[2] Salvar com nome")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._salvar_rapido()
            elif op == "2":
                self._salvar_nomeado()
            elif op == "9":
                self._ajuda_salvar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _salvar_rapido(self) -> None:
        nome_arquivo = os.path.join(self.save_dir, "quick_save.json")
        self.salvar_arquivo(nome_arquivo)
        self._ultimo_save = nome_arquivo
        self.logger.info(f"💾 Salvamento rápido realizado: {self._ultimo_save}")
        print(f"✔ Salvo em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        nome = input("Nome do arquivo de save (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        os.makedirs(self.save_dir, exist_ok=True)
        caminho = os.path.join(self.save_dir, nome)
        self.salvar_arquivo(caminho)
        self._ultimo_save = caminho
        self.logger.info(f"💾 Salvamento nomeado realizado: {self._ultimo_save}")
        print(f"✔ Progresso salvo como: {self._ultimo_save}")

    def salvar_arquivo(self, nome_arquivo: str) -> None:
        dados = {
            "personagem": self.personagem,
            "missao_config": self.missao_config,
        }
        # serializar inventário (lista de dicts)
        try:
            itens_serializados = []
            for it in (self.inven.itens or []):
                if isinstance(it, Item):
                    itens_serializados.append({
                        "nome": getattr(it, "nome", None),
                        "tipo": getattr(it, "tipo", None),
                        "valor": getattr(it, "valor", None),
                        "raridade": getattr(it, "raridade", None),
                        "dano": getattr(it, "dano", None),
                        "defesa": getattr(it, "defesa", None),
                        "cura": getattr(it, "cura", None),
                    })
                elif isinstance(it, dict):
                    itens_serializados.append(it)
                else:
                    # fallback: stringify
                    itens_serializados.append({"nome": str(it)})
            dados["inventario"] = itens_serializados
        except Exception:
            pass
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
                self.logger.info(f"💾 Jogo salvo em: {nome_arquivo}")
        except Exception as error:
            self.logger.error(f"❌ Erro ao salvar arquivo: {error}")
            print(f"Erro ao salvar arquivo: {error}")

    def _ajuda_salvar(self) -> None:
        print("\nAjuda — Salvar")
        print("- Salvar rápido usa um nome padrão.")
        print("- Salvar nomeado permite informar o nome do arquivo.")

    def menu_carregar(self) -> None:
        self.logger.info("Iniciando menu Carregar progresso salvo...")
        while True:
            print("\n=== Carregar ===")
            print("[1] Carregar último save")
            print("[2] Carregar por nome")
            print("[3] Mostrar saves disponíveis")
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._carregar_ultimo()
            elif op == "2":
                self._carregar_nomeado()
            elif op == "3":
                self.listar_saves()
            elif op == "9":
                self._ajuda_carregar()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def _carregar_ultimo(self) -> None:
            # --- CORREÇÃO: Preencher a variável se ela estiver vazia ---
        if not self._ultimo_save:
            import glob
            # Procura arquivos na pasta 'saves'. 
            # IMPORTANTE: Se seus saves forem .txt ou .pkl, mude o ".json" abaixo.
            lista_arquivos = glob.glob("saves/*.json") 
            
            if lista_arquivos:
                # Define self._ultimo_save como o arquivo mais recente encontrado
                self._ultimo_save = max(lista_arquivos, key=os.path.getmtime)



        if not self._ultimo_save:
            self.logger.warning("Nenhum save recente encontrado.")
            return print("Nenhum save recente encontrado.")
        if not os.path.exists(self._ultimo_save):
            self.logger.error(f"Arquivo não encontrado: {self._ultimo_save}")
            return print(f"Arquivo '{self._ultimo_save}' não foi encontrado.")
        self.carregar_arquivo(self._ultimo_save)

        self.logger.info(f"📂 Progresso carregado: {self._ultimo_save}")
        print(f"✔ Progresso carregado de: {self._ultimo_save}")

    def _carregar_nomeado(self) -> None:
        nome = input("Nome do arquivo para carregar (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        caminho = os.path.join(self.save_dir, nome)
        if not os.path.exists(caminho):
            self.logger.error(f"Arquivo não encontrado: {caminho}")
            return print(f"Arquivo '{caminho}' não foi encontrado.")
        self.carregar_arquivo(caminho)
        self.logger.info(f"📂 Progresso carregado: {caminho}")
        print(f"✔ Progresso carregado de: {caminho}")

    def listar_saves(self) -> None:
        self.logger.info("Listando arquivos de save disponíveis...")
        print("\nArquivos de Save Disponíveis:")
        for arquivo in os.listdir(self.save_dir):
            if arquivo.endswith(".json"):
                print(f"- {arquivo}")

    def carregar_arquivo(self, nome_arquivo: str) -> None:
        try:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                dados = json.load(f)
            self.personagem = dados.get("personagem", self.personagem)
            self.missao_config = dados.get("missao_config", self.missao_config)
            # carregar inventário serializado
            itens = dados.get("inventario")
            if itens is not None:
                try:
                    self.inven = Inventario()
                    restored = []
                    for it in itens:
                        if isinstance(it, dict):
                            restored.append(Item(**it))
                        else:
                            restored.append(it)
                    self.inven.itens = restored
                except Exception:
                    self.logger.error("Erro ao restaurar inventário do save.")
            self.logger.info("✅ Dados do jogo carregados com sucesso")
        except Exception as error:
            self.logger.error(f"❌ Erro ao carregar arquivo: {error}")
            print(f"Erro ao carregar arquivo: {error}")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- O carregamento usa os arquivos .json da pasta 'saves'.")

    # ========================= INICIAR MISSÃO ==============================

    def _iniciar_missao(self, inimigo: Entidade | None = None) -> None:
        self.logger.info("Iniciando Missões...")
        if not self.personagem.get("nome") or not self.personagem.get("arquetipo"):
            print("Crie/configure um personagem antes de iniciar uma missão.")
            return

        # Inimigo padrão, caso nenhum tenha sido passado
        if inimigo is None:
            try:
                inimigo = Inimigo.goblin()  # se seu Inimigo tiver fábrica
            except Exception:
                inimigo = Inimigo("Goblin", vida=10, ataque=2, defesa=0)

        # Instância do herói obtida via fábrica central (fora do jogo.py)
        heroi = criar_personagem(self.personagem["arquetipo"], self.personagem["nome"])
        self.logger.info(f"🎮 Herói instanciado: {heroi.nome} ({heroi.__class__.__name__})")
        # sincroniza inventário global do jogo com o herói (persistência entre missões)
        try:
            if hasattr(heroi, "inventario"):
                # usa o inventário do jogo como fonte única
                heroi.inventario = self.inven
            else:
                heroi.inventario = self.inven
        except Exception:
            pass

        cenario = (self.missao_config.get("cenario") or "Caverna")
        dificuldade = (self.missao_config.get("dificuldade") or "Fácil")

        try:
            engine = Missao(inimigo=inimigo, heroi=heroi, cenario=cenario, dificuldade=dificuldade, missao= self.missao_config.get("missao"))
            self.logger.info("🎯 Engine de missão criada com sucesso")
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar engine de Missão: {e}")
            print("Erro ao criar engine de Missão:", e)
            return

        # Executa a missão
        try:
            resultado = engine.executar(auto=True)
        except TypeError:
            resultado = engine.executar()

        if isinstance(resultado, ResultadoMissao):
            if resultado.venceu:
                self.logger.info(f"🏆 Missão concluída com sucesso! Encontros vencidos: {resultado.encontros_vencidos}")
                print(f"Missão concluída! Encontros vencidos: {resultado.encontros_vencidos}")
            else:
                self.logger.warning(f"💀 Missão falhou. Encontros vencidos: {resultado.encontros_vencidos} — {resultado.detalhes}")
                print(f"Missão falhou. Encontros vencidos: {resultado.encontros_vencidos} — {resultado.detalhes}")
        else:
            self.logger.info(f"📊 Resultado da missão: {resultado}")
            print("Resultado da missão:", resultado)
    #---------------------MENU INVENTÁRIO ------------------------------
    def menu_inventario(self) -> None:
        """Mostra o inventário do personagem."""
        self.logger.info("Acessando Menu do inventário...")

        while True:
            print("\n=== Inventário ===")
            print("[1] Mostrar todos os itens")
            print("[2] Remover itens")
            print("[3] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._mostrar_inventario()
            elif op == "2":
                self._remover_itens_inven()
            elif op == "3":
                self._ajuda_inventario()
            elif op == "0":
                break
            else:
                print("Opção inválida.")
                

    def _ajuda_inventario(self) -> None:
        print("\nO inventário mostra todos os itens que você guardou enquanto estava em batalha")
        print("\nA remoção de itens remove o item pelo nome dele, basta abrir o inventário e digitar o nome do item para remove-lo")
        

    def _mostrar_inventario(self) -> None:
        print("\n=== Inventário ===")
        self.logger.info("Inventário visualizado")
        itens =self.inven.listar_itens()
        if not itens:
            print("📦 O inventário está vazio.")
        else: 
            for i, item in enumerate(itens, 1):
                print(f"{i} . {item}")

        

    def _remover_itens_inven(self) -> None:
        """Remoção de itens do Inventário"""

        self.logger.info("Iniciando Remoção de Intes do Inventário")
        
        if not self.inven.itens:
            print("O invetário está vazio. Não existe nada para remover")
            return
        
        
        print("\n======Itens do Inventário ======")
        for i, item in enumerate(self.inven.itens, 1):
            print(f"{i} . {item}")

        nome_item = input("Digite o nome do item para remove-lo do Inventário").strip()

        item_encontrado = None
        nome_item_mm = nome_item.strip().lower()
        for item in self.inven.itens:
                if isinstance(item, str):
                    if item.lower() == nome_item_mm:
                        item_encontrado = item
                        break

                elif isinstance(item, dict):
                    nome = item.get("nome")
                    if isinstance(nome, str) and nome.lower() == nome_item_mm:
                        item_encontrado=item
                        break
                
                else:
                    nome = getattr(item,"nome", None)
                    if isinstance(nome, str) and nome.lower()==nome_item_mm:
                        item_encontrado=item
                        break

        if item_encontrado:
            self.inven.remover_item(item_encontrado)
            print(f"Item '{nome_item}' Removido com Sucesso!")
            self.logger.info(f"Item '{nome_item}' Removido do inventário")

        else:
            print(f"Item '{nome_item}' não encontrado no inventário.")
            self.logger.info(f"Tentativa de remover item inexistente: '{nome_item}' ")
