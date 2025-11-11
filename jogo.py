from __future__ import annotations
import json
import os
from utils.logger import Logger
from models.base import Entidade
from models.inimigo import Inimigo
from models.personagem import Personagem
from models.missao import MissaoHordas, Missao, ResultadoMissao
from models.inventario import Inventario,Drop_rate, Loot, Item
from dado import d6, d20


class Jogo:
    """
    Estrutura base com menus e submenus.
    - Coleta nome/arquétipo, mas NÃO cria o personagem aqui.
    - A criação concreta é delegada a models.personagem.criar_personagem.
    - O HUD do turno é LOCAL deste arquivo (função _mostrar_hud_turno) e
      usa apenas helpers exportados por models.personagem.
    - Missões usam d20 para qualidade da ação e d6 para dano.
    """

    def __init__(self) -> None:
        self.logger = Logger()
        self.logger.info("Iniciando o jogo...")

        self.inventario = Inventario()

        self.itens = []
        self.capacidade_maxima = 20

        self.nome = None
        self.tipo = None
        self.valor = None
        self.raridade = None
        self.dano = None
        self.defesa = None


 

        # Somente escolhas do jogador; nada de instanciar aqui.
        self.personagem = {
            "nome": None,         # str
            "arquetipo": None,    # "Guerreiro" | "Mago" | "Arqueiro" | "Curandeiro"
        }

        self.missao_config = {
            "dificuldade": None,  # "Fácil" | "Média" | "Difícil"
            "cenario": None,      # "Trilha" | "Floresta" | "Caverna" | "Ruínas"
            "missao": None,       # rótulo da missão (se usar Missao*)
        }
    

        self._ultimo_save = None
        self._ultimo_load = None

        # Pasta de saves
        self.save_dir = os.path.join(os.getcwd(), "saves")
        os.makedirs(self.save_dir, exist_ok=True)

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

        # Especiais (até 7, destravados por nível; nomes/custos vindos do helper)
        especiais = especiais_do_personagem(heroi, considerar_nivel=True)
        for i, (_esp_id, nome, custo) in enumerate(especiais, start=2):
            if mana_atual >= custo:
                print(f"[{i}] {nome} — custo {custo} (ficará: {mana_atual - custo})")
            else:
                print(f"[{i}] {nome} — custo {custo} (insuficiente)")
        print("[0] Fugir")

    # ======================================================================
    # Ataque normal com d20 para decidir a qualidade da ação
    # 1–5: péssima (erra) | 6–10: normal | 11–15: boa (+1) | 16–20: excelente (crítico)
    # ======================================================================
    def _ataque_normal_com_d20(self, heroi: Personagem, inimigo: Entidade) -> int:
        r = d20()
        print(f"\n[d20] Você rolou: {r}")

        if 1 <= r <= 5:
            print("→ Ação PÉSSIMA: você erra o golpe. Sem dano.")
            return 0

        # dano base físico: 1d6 + ataque do herói (a lógica detalhada vive no Personagem)
        base = d6() + heroi._atrib.ataque

        if 6 <= r <= 10:
            dano = base
            print(f"→ Ação NORMAL: dano base = {base}")
        elif 11 <= r <= 15:
            dano = base + 1
            print(f"→ Ação BOA: {base} + 1 = {dano}")
        else:  # 16–20
            dano = base * 2
            print(f"→ Ação EXCELENTE (crítico): {base} x 2 = {dano}")

        efetivo = inimigo.receber_dano(dano)
        if efetivo != dano:
            print(f"(Defesa do alvo reduziu o dano para {efetivo})")
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
            print("[9] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self._definir_nome()
            elif op == "2":
                self._escolher_arquetipo()
            elif op == "3":
                self._confirmar_criacao()
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
            print(f"Arquétipo definido: {arq}")
        else:
            print("Opção inválida. Arquétipo não alterado.")

    def _confirmar_criacao(self) -> None:

        self.logger.info("Executando confirmação da criações do personagem...")

        """
        Aqui NÃO criamos o personagem. Apenas validamos escolhas.
        A criação concreta ocorrerá somente quando a missão iniciar,
        delegada a models.personagem.criar_personagem(...).
        """
        if not self.personagem["nome"]:
            print("Defina um nome antes de confirmar a criação.")
            return
        if not self.personagem["arquetipo"]:
            print("Escolha um arquétipo antes de confirmar a criação.")
            return

        print("\nPersonagem configurado!")
        print(f"Nome: {self.personagem['nome']} | Arquétipo: {self.personagem['arquetipo']}")
        print("(Obs.: a instância será criada apenas ao iniciar a missão.)")

    def _ajuda_criar_personagem(self) -> None:

        self.logger.info("Iniciando menu Ajuda da criação do personagem...")

        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo.")
        print("- O jogo NÃO cria a instância aqui; isso só acontece ao iniciar a missão.")
        print("- As classes têm atributos/habilidades diferentes (definidos em models.personagem).")

    # ================================ MISSÃO ===============================

    def menu_missao(self) -> None:

        self.logger.info("Iniciando menu Missões...")

        while True:
            print("\n=== Missão ===")
            print(f"Dificuldade atual: {self.missao_config['dificuldade'] or '(não definida)'}")
            print(f"Cenário atual:     {self.missao_config['cenario'] or '(não definido)'}")
            print(f"Missão atual:      {self.missao_config['missao'] or '(não definida)'}")
            print()
            print("[1] Escolher dificuldade")
            print("[2] Escolher cenário")
            print("[3] Pré-visualizar missão")
            print("[4] Iniciar missão (com d20 e d6)")
            print("[5] Escolher missão específica")
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
                self._iniciar_missao_placeholder()
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

        print("Escolha de Missões:")
        print("[1] Eliminar Ladrão")
        print("[2] Eliminar Goblin")
        print("[3] Eliminar Golem")
        print("[4] Eliminar Elfo")
        print("[5] Eliminar Dragão")
        op = input("> ").strip()
        # Se Missao.missao_X retorna rótulo/objeto de missão:
        mapa = {
            "1": Missao.missao_1(self),
            "2": Missao.missao_2(self),
            "3": Missao.missao_3(self),
            "4": Missao.missao_4(self),
            "5": Missao.missao_5(self),
        }
        escolha = mapa.get(op)
        if escolha:
            self.missao_config["missao"] = escolha
            print(f"Missão definida: {escolha}")

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
            print(f"Cenário definido: {cen}")
        else:
            print("Opção inválida.")

    def _preview_missao(self) -> None:

        self.logger.info("Iniciando Preview de Missões")

        print("\nPré-visualização da Missão")
        print(f"- Dificuldade: {self.missao_config['dificuldade'] or '(não definida)'}")
        print(f"- Cenário:     {self.missao_config['cenario'] or '(não definido)'}")
        print("- Hordas e chefe serão gerados conforme cenário e dificuldade.")
        print("  (A lógica fica em missão.py/inimigo.py; o herói é criado só ao iniciar.)")

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
        print(f"✔ Salvo em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        nome = input("Nome do arquivo de save (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        os.makedirs(self.save_dir, exist_ok=True)
        caminho = os.path.join(self.save_dir, nome)
        self.salvar_arquivo(caminho)
        self._ultimo_save = caminho
        print(f"✔ Progresso salvo como: {self._ultimo_save}")

    def salvar_arquivo(self, nome_arquivo: str) -> None:
        dados = {
            "personagem": self.personagem,
            "missao_config": self.missao_config,
        }
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                json.dump(dados, f, indent=4, ensure_ascii=False)
                self.logger.info(f"Jogo salvo em: {nome_arquivo}")
        except Exception as error:
            self.logger.info(f"Erro ao salvar arquivo: {error}")
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
        if not self._ultimo_save:
            return print("Nenhum save recente encontrado.")
        if not os.path.exists(self._ultimo_save):
            return print(f"Arquivo '{self._ultimo_save}' não foi encontrado.")
        self.carregar_arquivo(self._ultimo_save)
        print(f"✔ Progresso carregado de: {self._ultimo_save}")

    def _carregar_nomeado(self) -> None:
        nome = input("Nome do arquivo para carregar (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"
        caminho = os.path.join(self.save_dir, nome)
        if not os.path.exists(caminho):
            return print(f"Arquivo '{caminho}' não foi encontrado.")
        self.carregar_arquivo(caminho)
        print(f"✔ Progresso carregado de: {caminho}")

    def listar_saves(self) -> None:
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
        except Exception as error:
            self.logger.info(f"Erro ao carregar arquivo: {error}")
            print(f"Erro ao carregar arquivo: {error}")

    def _ajuda_carregar(self) -> None:
        print("\nAjuda — Carregar")
        print("- O carregamento usa os arquivos .json da pasta 'saves'.")

    def menu_inventario(self) -> None:
        self.logger.info("Iniciando menu Carregar progresso salvo...")

        while True:
            print("\n=== Inventário ===")
            print("[1] Mostrar todos os itens do inventário")
            print("[2] Remover Item")
            print("[3] Ajuda")
            print("[0] Voltar")
            op = input("> ").strip()

            if op == "1":
                self.mostrar_inventario()
            elif op == "2":
                self.remover_item_inventario()
            elif op == "3":
                self.ajuda_inventario()
            elif op == "0":
                break
            else:
                print("Opção inválida.")

    def ajuda_inventario(self) -> None:
        print("Ajuda sendo feita")
        

    def remover_item_inventario(self, item):
        """Remove um item do inventário do jogador."""
        if self.inventario.remover_item(item):
            print(f"🗑️ {item.nome} foi removido do inventário!")
        else:
            print("⚠️ Item não encontrado.")

    def mostrar_inventario(self):
        """Mostra todos os itens atuais."""
        itens = self.inventario.listar_itens()
        if not itens:
            print("\n📦 O inventário está vazio.")
            return
        
        print("\n🎒 Itens do inventário:")
        print("-" * 50)
        for i, item in enumerate(itens, start=1):
            print(f"{i}. {item.nome} | Tipo: {item.tipo} | Raridade: {item.raridade} | Valor: {item.valor}")
            if item.dano:
                print(f"   ⚔️ Dano: {item.dano}")
            if item.defesa:
                print(f"   🛡️ Defesa: {item.defesa}")
        print("-" * 50)


    

    # ========================= INICIAR MISSÃO ==============================

    def _iniciar_missao_placeholder(self, inimigo: Entidade | None = None) -> None:

        self.logger.info("Iniciando Missões...")
        """
        Inicia a missão de combate.
        ATENÇÃO: A criação do personagem é delegada a models.personagem.criar_personagem(...).
        Aqui apenas passamos as escolhas (nome/arquétipo) e usamos o retorno.
        """
        if not self.personagem.get("nome") or not self.personagem.get("arquetipo"):
            print("Crie/configure um personagem antes de iniciar uma missão.")
            return

        # Inimigo padrão, caso nenhum tenha sido passado
        if inimigo is None:
            try:
                inimigo = Inimigo.goblin()  # se seu Inimigo tiver fábrica
            except Exception:
                inimigo = Inimigo("Goblin", vida=10, ataque=2, defesa=0)

        # >>> ÚNICO ponto onde a instância do herói é obtida (fora do jogo.py)
        heroi = criar_personagem(self.personagem["arquetipo"], self.personagem["nome"])

        cenario = (self.missao_config.get("cenario") or "Caverna")
        dificuldade = (self.missao_config.get("dificuldade") or "Fácil")

        try:
            engine = Missao(inimigo=inimigo, heroi=heroi, cenario=cenario, dificuldade=dificuldade)
        except Exception as e:
            print("Erro ao criar engine de Missão:", e)
            return

        # Executa a missão (se sua engine aceitar 'auto', passe conforme desejar)
        try:
            resultado = engine.executar(auto=True)
        except TypeError:
            resultado = engine.executar()

        if isinstance(resultado, ResultadoMissao):
            if resultado.venceu:
                print(f"Missão concluída! Encontros vencidos: {resultado.encontros_vencidos}")
            else:
                print(f"Missão falhou. Encontros vencidos: {resultado.encontros_vencidos} — {resultado.detalhes}")
        else:
            print("Resultado da missão:", resultado)
