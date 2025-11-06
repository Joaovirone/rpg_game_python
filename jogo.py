from __future__ import annotations
import json
import os

from utils.logger import Logger
from models.base import Atributos, Entidade
from models.inimigo import Inimigo
from models.personagem import Personagem, Entidade, Curandeiro, Arqueiro, Mago, Guerreiro
from models.missao import MissaoHordas, Missao, ResultadoMissao
from dado import rolar_d6, rolar_d20


class Jogo:
    """
    Estrutura base com menus e submenus completos.
    A missão usa d20 para decidir a qualidade da ação e d6 para o dano.
    Exibe HUD com Mana e custos dos especiais e bloqueia execução sem mana.
    """

    def __init__(self) -> None:


        self.nome_personagem : Personagem | None = None
        
        self.logger = Logger()
        self.logger.info("Iniciando o jogo...")

        self.personagem = {
            "nome": None,
            "arquetipo": None,   # "Guerreiro", "Mago", "Arqueiro", "Curandeiro"
        }

        self.arquetipos = {
            "Guerreiro": Guerreiro,
            "Mago": Mago,
            "Arqueiro": Arqueiro,
            "Curandeiro": Curandeiro
        }

        self.missao_config = {
            
            "dificuldade": None,  # Fácil | Média | Difícil
            "cenario": None,     # rótulo ilustrativo
            "missao": None,      # rótulo da missão

        }
        self._ultimo_save = None
        self._ultimo_load = None

        #Caminho que é feito para os saves irem pra pasta save
        self.save_dir = os.path.join(os.getcwd(), "saves")
        os.makedirs(self.save_dir, exist_ok=True) # garante que o diretório exista

    # ======================================================================
    # Construção do herói a partir do arquétipo escolhido no menu
    # ======================================================================

    
    # ======================================================================
    def _mostrar_hud_turno(self, heroi, inimigo) -> None:
        """Imprime HUD com HP/Mana e os especiais com custo/disponibilidade e prévia."""
        mana_atual = getattr(heroi._atrib, "mana", 0)
        print(f"HP {heroi.nome}: {heroi.barra_hp()}   |   Mana: {mana_atual}")
        print(f"HP {inimigo.nome}: {inimigo.barra_hp()}")
        print("[1] Ataque normal (usa d20 para decidir a qualidade)")
        especiais = self._lista_especiais(heroi)
        for i, (esp_id, nome, custo) in enumerate(especiais, start=2):
            if mana_atual >= custo:
                previa = mana_atual - custo
                print(f"[{i}] {nome} — custo {custo} mana (ficará: {previa})")
            else:
                print(f"[{i}] {nome} — custo {custo} mana (insuficiente)")
        print("[0] Fugir")

    # ======================================================================
    # Ataque normal com d20 para decidir a qualidade da ação
    # 1–5: péssima (erra) | 6–10: normal | 11–15: boa (+1) | 16–20: excelente (crítico)
    # ======================================================================
    def _ataque_normal_com_d20(self, heroi, inimigo) -> int:
        r = rolar_d20()
        print(f"\n[d20] Você rolou: {r}")

        if 1 <= r <= 5:
            print("→ Ação PÉSSIMA: você erra o golpe. Sem dano.")
            return 0

        base = heroi.calcular_dano_base()

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
        nome = input("Digite o nome do personagem: ").strip()
        if nome:
            self.personagem["nome"] = nome
            print(f"Nome definido: {nome}")
        else:
            print("Nome não alterado.")

    def _escolher_arquetipo(self) -> None:

        print("\nArquétipos disponíveis:")
        print("[1] Guerreiro")
        print("[2] Mago")
        print("[3] Arqueiro")
        print("[4] Curandeiro")
        print("[5] Personalizado (usa Guerreiro por padrão)")
        escolha = input("> ").strip()

        mapa = {
            "1": "Guerreiro",
            "2": "Mago",
            "3": "Arqueiro",
            "4": "Curandeiro",
            "5": "Personalizado",
        }
        arq = mapa.get(escolha)
        if arq:
            self.personagem["arquetipo"] = arq
            print(f"Arquétipo definido: {arq}")
            return arq


        else:
            print("Opção inválida. Arquétipo não alterado.")
            return None

    def mostrar_personagem(self, nome_arquetipo: str | None = None, nome_heroi: str | None = None):
        """
        Cria e retorna um personagem do arquétipo escolhido, exibindo preview das estatísticas.
        """
        if not nome_arquetipo or not nome_heroi:
            if self.nome_personagem:
                personagem = self.nome_personagem
                arq = personagem._atrib
                print(f"\nPersonagem atual: {personagem.nome} ({personagem.__class__.__name__})")
                print(f"🩸 Vida: {arq.vida}/{arq.vida_max}")
                print(f"⚔️ Ataque: {arq.ataque}")
                print(f"🛡️ Defesa: {arq.defesa}")
                print(f"🔮 Mana: {getattr(arq, 'mana', 0)}")
                print(f"✨ Ataque Mágico: {personagem.ataque_magico}\n")
                return personagem
            else:
                print("Nenhum personagem criado ainda.")
                return None

        # Pega o arquétipo que foi escolhido pelo usuário
        classe_arquetipo = self.arquetipos.get(nome_arquetipo)
        if not classe_arquetipo:
            print("Arquétipo não encontrado.")
            return None

        # Cria o personagem (atributos já são definidos no construtor do arquétipo)
        personagem = classe_arquetipo(nome_heroi)
        self.nome_personagem = personagem

        # Mostra estatísticas
        arq = personagem._atrib
        print(f"\nPreview de {personagem.nome}:")
        print(f"🩸 Vida: {arq.vida}/{arq.vida_max}")
        print(f"⚔️ Ataque: {arq.ataque}")
        print(f"🛡️ Defesa: {arq.defesa}")
        print(f"🔮 Mana: {getattr(arq, 'mana', 0)}")
        print(f"✨ Ataque Mágico: {personagem.ataque_magico}\n")

        self.nome_personagem = personagem
        return personagem

    def _confirmar_criacao(self) -> None:
        if not self.personagem["nome"]:
            print("Defina um nome antes de confirmar a criação.")
            return
        if not self.personagem["arquetipo"]:
            print("Escolha um arquétipo antes de confirmar a criação.")
            return

        nome_arquetipo = self.personagem["arquetipo"]
        nome_heroi = self.personagem["nome"]
        self.heroi = self.mostrar_personagem(nome_arquetipo, nome_heroi)

        print("\nPersonagem criado com sucesso!")
        print(f"Nome: {self.personagem['nome']} | Arquétipo: {self.personagem['arquetipo']}")
        print("(Obs.: atributos base são definidos automaticamente na missão.)")

    def _ajuda_criar_personagem(self) -> None:
        print("\nAjuda — Criar Personagem")
        print("- Defina um nome e um arquétipo para continuar.")
        print("- As escolhas afetam os especiais disponíveis na missão.")

    def menu_missao(self) -> None:
        while True:
            print("\n=== Missão ===")
            print(f"Dificuldade atual: {self.missao_config['dificuldade'] or '(não definida)'}")
            print(f"Cenário atual:     {self.missao_config['cenario'] or '(não definido)'}")
            print(f"Missão atual:      {self.missao_config['missao'] or '(não definida)'}")

            print() # Pular linha

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

        print("Escolha de Missões:")
        print("[1] Eliminar Ladrão")
        print("[2] Eliminar Goblin")
        print("[3] Eliminar Golem")
        print("[4] Eliminar Elfo")
        print("[5] Eliminar Dragão")
        op = input("> ").strip()
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
        print("\nDificuldades:")
        print("[1] Fácil")
        print("[2] Média")
        print("[3] Difícil")
        op = input("> ").strip()

        mapa = {
            "1": "Fácil",
            "2": "Média",
            "3": "Difícil"
                }
        escolha = mapa.get(op)
        if escolha:
            self.missao_config["dificuldade"] = escolha
            print(f"Dificuldade definida: {escolha}")
        else:
            print("Opção inválida.")

    def _escolher_cenario(self) -> None:
        print("\nCenários:")
        print("[1] Trilha")
        print("[2] Floresta")
        print("[3] Caverna")
        print("[4] Ruínas")
        op = input("> ").strip()

        mapa = {
            "1": "Trilha",
            "2": "Floresta",
            "3": "Caverna",
            "4": "Ruínas"
        }
        cen = mapa.get(op)
        if cen:
            self.missao_config["cenario"] = cen
            print(f"Cenário definido: {cen}")
        else:
            print("Opção inválida.")

    def _preview_missao(self) -> None:
        print("\nPré-visualização da Missão")
        print(f"- Dificuldade: {self.missao_config['dificuldade'] or '(não definida)'}")
        print(f"- Cenário:     {self.missao_config['cenario'] or '(não definido)'}")
        print("- Inimigos e recompensas: (em breve)")
   

    def _ajuda_missao(self) -> None:
        print("\nAjuda — Missão")
        print("- Em 'Iniciar missão', o ataque **normal** usa d20 para decidir a qualidade:")
        print("  1–5: péssima (erra), 6–10: normal, 11–15: boa (+1), 16–20: excelente (crítico).")
        print("- O HUD mostra sua Mana atual, o custo e a **prévia** de mana que ficará.")
        print("- Especiais são bloqueados se a mana for insuficiente.")

    # ========================= SALVAR/CARREGAR ==============================

    def menu_salvar(self) -> None:
        while True:
            print("\n=== Salvar ===")
            print("[1] Salvar rápido (simulado)")
            print("[2] Salvar com nome (simulado)")
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
        #parametro a ser usado para salvar na pasta saves
        nome_arquivo = os.path.join(self.save_dir, "quick_save.json")
        self.salvar_arquivo(nome_arquivo)
        self._ultimo_save = nome_arquivo
        print(f"✔ Salvo (simulado) em: {self._ultimo_save}")

    def _salvar_nomeado(self) -> None:
        nome = input("Nome do arquivo de save (ex.: meu_jogo.json): ").strip() or "save.json"
        if not nome.endswith(".json"):
            nome += ".json"

        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)

            
        #parametro a ser usado para salvar na pasta saves
        caminho_completo = os.path.join(self.save_dir, nome)
        self.salvar_arquivo(caminho_completo)
        self._ultimo_save = caminho_completo
        print(f"✔ Progresso Salvo Como: {self._ultimo_save}")
        

    def salvar_arquivo(self, nome_arquivo: str) -> None:
        dados = {
            "personagem": self.personagem,
            "missao_config": self.missao_config,
        }
        try:
            with open(nome_arquivo, "w", encoding="utf-8") as f:

                json.dump(dados, f, indent=4, ensure_ascii=False)
                self.logger.info(f"Jogo salvo em : {nome_arquivo}")
        except Exception as error:
            self.logger.info(f"Erro ao salvar arquivo: {error}")
            print(f"Erro ao salvar arquivo: {error}")

    def _ajuda_salvar(self) -> None:
        print("\nAjuda — Salvar")
        print("- Salvar rápido usa um nome padrão fictício.")
        print("- Salvar nomeado permite escolher um nome fictício.")
        print("- Não há escrita em disco nesta base — é apenas navegação.")

    def menu_carregar(self) -> None:
        while True:
            print("\n=== Carregar ===")
            print("[1] Carregar último save (simulado)")
            print("[2] Carregar por nome (simulado)")
            print("[3] Mostrar Saves disponíveis")  
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
        #parametro a ser usado para carregar na pasta saves
        caminho_completo = os.path.join(self.save_dir,nome)
        #Verifica se o arquivo existe na pasta saves
        if not os.path.exists(caminho_completo):
            return print(f"Arquivo '{caminho_completo}' não foi encontrado.")
        self.carregar_arquivo(caminho_completo)
        print(f"✔ Progresso carregado de: {caminho_completo}")

    def listar_saves(self) -> None:
        """Lista os arquivos de save na pasta de saves."""
        print("\nArquivos de Save Disponíveis:")
        arquivos = os.listdir(self.save_dir)
        for arquivo in arquivos:
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
        print("- O carregamento aqui é apenas ilustrativo (sem leitura real).")
        print("- Use o nome que você “salvou” anteriormente para simular.")

    def _iniciar_missao_placeholder(self, inimigo=None) -> None:
        """
        Inicia uma missão usando a engine Missao.
        Baseado no placeholder que você tinha: cria inimigo padrão se não informado,
        recupera o personagem criado no menu e executa a missão.
        """
        # verifica existência de personagem criado no menu
        if not hasattr(self, "personagem") or not self.personagem.get("nome") or not self.personagem.get("arquetipo"):
            print("Crie um personagem antes de iniciar uma missão.")
            return

        # cria inimigo padrão se não informado (assume que Inimigo.goblin() existe)
        if inimigo is None:
            try:
                inimigo = Inimigo.goblin()
            except Exception:
                # fallback simples: instancia padrão se constructor direto existir
                try:
                    inimigo = Inimigo("Goblin", vida=10, ataque=2, defesa=0)
                except Exception:
                    print("Erro ao criar inimigo padrão. Verifique a classe Inimigo.")
                    return

        # obtém dados do personagem (assume que self.mostrar_personagem(arquetipo, nome) retorna um Personagem)
        nome_arquetipo = self.personagem.get("arquetipo")
        nome_heroi = self.personagem.get("nome")

        try:
            heroi = self.mostrar_personagem(nome_arquetipo, nome_heroi)
        except Exception:
            # se mostrar_personagem não existir ou falhar, tentar usar atributo direto
            heroi = getattr(self, "heroi_atual", None) or getattr(self, "player", None)
            if heroi is None:
                print("Não foi possível recuperar o personagem. Verifique 'mostrar_personagem' ou a variável do herói.")
                return

        # pega configuração de missão (fallbacks seguros)
        cenario = getattr(self, "missao_config", {}).get("cenario", "Caverna")
        dificuldade = getattr(self, "missao_config", {}).get("dificuldade", "Fácil")

        # instancia engine de missão e executa
        try:
            engine = Missao(inimigo=inimigo, heroi=heroi, cenario=cenario, dificuldade=dificuldade)
        except Exception as e:
            print("Erro ao criar engine de Missão:", e)
            return

        # executa em modo manual (auto=False). Se preferir autoplay, passe auto=True.
        try:
            resultado = engine.executar(auto=True)
        except TypeError:
            # caso sua versão de Missao.executar não aceite 'auto', chamar sem argumento
            resultado = engine.executar()

        # exibe resultado
        if isinstance(resultado, ResultadoMissao):
            if resultado.venceu:
                print(f"Missão concluída! Encontros vencidos: {resultado.encontros_vencidos}")
            else:
                print(f"Missão falhou. Encontros vencidos: {resultado.encontros_vencidos} — {resultado.detalhes}")
        else:
            # resultado inesperado — apenas imprime
            print("Resultado da missão:", resultado)


