# 🧙‍♂️ RPG Game em Python

Um RPG de turnos desenvolvido totalmente em Python, com sistema completo de personagens, inimigos, combate tático, inventário, drops de itens e progressão por níveis. O projeto é orientado a objetos e modularizado para facilitar expansão de classes, missões e balanceamento.

## ✨ Destaques do Projeto

- 🎲 **Sistema de dados D&D-like**: Rolagens de d6, d20 e múltiplos dados para mecânicas de combate
- ⚔️ **Combate tático por turnos**: Qualidade de ação baseada em d20 (péssima, normal, boa, excelente)
- 🎭 **4 Classes jogáveis**: Cada uma com 7 habilidades únicas e progressão
- 📈 **Sistema de XP e níveis**: Progressão até o nível 10 com desbloqueio de novas habilidades --OBS--
- 🎁 **Sistema de drop dinâmico**: Itens com diferentes raridades e chances baseadas em nível
- 💾 **Save/Load completo**: Salve seu progresso em JSON
- 🌍 **Missões em cenários variados**: Trilha, Floresta, Caverna e Ruínas
- 📊 **Logger integrado**: Acompanhe todas as ações do jogo com logs detalhados

---

## 🚀 Funcionalidades Principais

### ⚔️ Sistema de Combate

- **Turnos táticos**: Escolha entre ataque básico, habilidades especiais ou fuga
- **Rolagem de qualidade (d20)**:
  - `1–5`: Ação péssima (erra o golpe)
  - `6–10`: Ação normal
  - `11–15`: Ação boa (+1 de dano)
  - `16–20`: Ação excelente (dano crítico x2)
- **Sistema de efeitos**: Sangramento, veneno, eletrocussão, atordoamento, invulnerabilidade
- **Gestão de mana**: Cada habilidade tem custo específico
- **HUD informativo**: Vida, mana e status em tempo real

### 🧩 Sistema de Personagens

Crie seu herói escolhendo entre 4 arquétipos únicos:

|     Classe     | Vida | Ataque | Defesa | Mana | Magia |           Estilo de Jogo              |
|----------------|------|--------|--------|------|-------|---------------------------------------|
| **Guerreiro**  |  50  |    8   |   10   |  5   |   0   |  Tank resistente com alto dano físico |
| **Mago**       |  30  |    1   |    4   |  40  |  10   |    DPS mágico com controle de campo   |
| **Arqueiro**   |  35  |    5   |    4   |  25  |   3   |   DPS equilibrado com DoTs poderosos  |
| **Curandeiro** |  20  |    0   |    3   |  35  |   8   |  Suporte com cura e reflexão de dano  |

#### 🎯 Sistema de Habilidades

Cada classe possui **7 habilidades especiais**:
- **4 habilidades iniciais** desbloqueadas no nível 1
- **+3 habilidades avançadas** desbloqueadas nos níveis 2, 4 e 6

**Exemplos de habilidades**:
- 🗡️ **Guerreiro**: Execução Pública (5d6 crítico +3), Perseverança (1 turno invulnerável)
- 🔮 **Mago**: Colapso Minguante (6d6), Empurrão Sísmico (atordoa por 1 turno)
- 🏹 **Arqueiro**: Marca Fatal (1d6/turno por 7 turnos), Ás na Manga (crítico +10)
- ✨ **Curandeiro**: Resplendor Cósmico (cura 20 em área), Ventos Revigorantes (reflexão)

### 💀 Sistema de Inimigos

- **Inimigos escaláveis**: Stats ajustados pela dificuldade da missão
- **Hordas dinâmicas**: Enfrentar grupos de minions + chefe final
- **Bosses poderosos**: HP escalado (100/300/500 conforme dificuldade)
- **Cenários temáticos**: Cada cenário tem seus próprios inimigos

**Exemplos**:
- 🌲 **Floresta**: Lobo Alterado, Espírito, Wendigo (chefe)
- 🕳️ **Caverna**: Toupeira de Lodo, Ungoliant, Gollum (chefe)
- 🏛️ **Ruínas**: Cadáver de Guerreiro, Ceifador, Rei Amaldiçoado (chefe)

### 🎲 Sistema de Drop de Itens

Cada inimigo derrotado pode dropar itens baseado em:
- **Raridade**: Comum → Incomum → Raro → Épico → Lendário
- **Nível do personagem**: Quanto maior o nível, maior a chance
- **Chance base**: Limitada a 50% (balanceamento)

**Tipos de itens**:
- ⚗️ **Consumíveis**: Poções de vida/mana, elixires
- ⚔️ **Armas**: Espadas, arcos, cajados, machados (15-70 de dano)
- 🛡️ **Armaduras**: Escudos, armaduras de couro/aço/obsidiana (15-90 de defesa)
- 💍 **Acessórios**: Anéis, amuletos, relíquias

### 🎒 Inventário

- Capacidade máxima de **20 itens**
- Adicionar/remover itens por nome
- Persistência entre missões e saves
- Sistema de feedback visual

### 📈 Sistema de Progressão

- **Nível máximo**: 10
- **XP por derrota**: 10 × nível do jogador
- **Ganhos por nível**:
  - +5 vida e vida máxima
  - +1 ataque
  - +1 defesa
  - +5 mana
- **Desbloqueio de habilidades**: Níveis 2, 4 e 6

### 💾 Sistema de Save/Load

- **Pasta dedicada**: `/saves/` no diretório do jogo
- **Formato JSON**: Fácil leitura e edição
- **Save rápido**: `quick_save.json`
- **Save nomeado**: Escolha o nome do arquivo
- **Persistência completa**: Personagem, inventário, missões

---

## 📂 Estrutura do Projeto

```
rpg_game_python/
│
├── main.py                  # 🎮 Ponto de entrada do jogo
├── jogo.py                  # 🎯 Classe principal (menus, fluxo, saves)
├── dado.py                  # 🎲 Sistema de rolagem de dados (d6, d20)
│
├── models/                  # 📦 Modelos do jogo
│   ├── __init__.py
│   ├── base.py              # 🧱 Classes base (Entidade, Atributos)
│   ├── personagem.py        # 🧙 Classes de personagens e habilidades
│   ├── inimigo.py           # 👹 Geração de inimigos e hordas
│   ├── inventario.py        # 🎒 Sistema de itens e drops
│   └── missao.py            # 🗺️ Engine de missões e combate
│
├── utils/                   # 🛠️ Utilitários
│   ├── __init__.py
│   ├── logger.py            # 📝 Sistema de logging
│   └── repositorio.py       # 💾 Interface de persistência
│
├── saves/                   # 💾 Arquivos de save (gerado automaticamente)
├── git_notes.MD             # 📚 Guia de Git e Conventional Commits
└── README.md                # 📖 Este arquivo
```

---

## 🔧 Instalação e Execução

### Requisitos

- Python 3.8 ou superior
- Nenhuma dependência externa necessária (usa apenas biblioteca padrão)

### Passos para rodar

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/rpg_game_python.git
cd rpg_game_python

# 2. (Opcional) Crie um ambiente virtual
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# 3. Execute o jogo
python main.py
```

---

## 🎮 Como Jogar

### ⚙️ Configuração de Execução das Missões

O método `engine.executar(auto: bool)` no arquivo `jogo.py`controla o fluxo das batalhas:

- **`auto=True`**: Ativa o piloto automático. O algoritmo seleciona as habilidades baseadas na classe e no estado atual do personagem (ex: Curandeiros priorizam cura quando HP < 35%).
- **`auto=False`** (Padrão): Ativa a interface interativa (CLI), solicitando input do usuário para cada turno.

Para alterar o modo padrão, edite a chamada na classe `Jogo` (método `_iniciar_missao`).

### Menu Principal

```
=== RPG OO — Menu Principal ===
[1] Criar personagem
[2] Encarar missão
[3] Salvar
[4] Carregar
[5] Personagem Atual
[6] Inventário
[0] Sair
```

### Criação de Personagem

1. **Defina o nome** do seu herói
2. **Escolha o arquétipo**: Guerreiro, Mago, Arqueiro ou Curandeiro
3. **Confirme a criação** para ver os stats iniciais
4. **Preview**: Veja vida, ataque, defesa, mana e habilidades disponíveis

### Configuração de Missão

1. **Escolha a dificuldade**: Fácil, Média ou Difícil
2. **Escolha o cenário**: Trilha, Floresta, Caverna ou Ruínas
3. **Selecione o tipo de missão**:
   - Eliminar minion específico
   - Eliminar o chefe
   - Enfrentar horda completa

### Durante o Combate

```
--- Turno 1 ---
HP Arthas: [########--------] 50/50   |   Mana: 5
HP Goblin: [####------------] 12/12

[1] Ataque básico — custo 0 (ficará: 5)
[2] Execução Pública — custo 7 (insuficiente)
[3] Perseverança — custo 0 (ficará: 5)
[4] Golpe Trovejante — custo 1 (ficará: 4)
[5] Lâmina Ínfera — custo 2 (ficará: 3)
[0] Fugir
>
```

**Dicas de combate**:
- Gerencie sua mana com sabedoria
- Use habilidades de DoT (Damage over Time) em bosses
- Classes de suporte podem virar a partida
- Observe os padrões de ataque dos inimigos

---

## 📊 Exemplos de Combate

### Exemplo 1: Guerreiro vs Goblin

```
🎯 Arthas rola d20 para ataque normal: 18
🎯 Ação EXCELENTE (crítico): 8 x 2 = 16
⚔️ Dano total: 15 (após defesa)

💀 Goblin foi derrotado!
🎁 Goblin dropou: Espada Curta (comum)!
📈 Arthas ganhou 10 XP
```

### Exemplo 2: Mago usando Colapso Minguante

```
🔮 Mago gasta 15 de mana (restante: 25)
🎲 Colapso Minguante - Dano: 6+5+4+6+3+2 = 26
⚔️ Ceifador recebe 24 de dano (após defesa)
HP Ceifador: [###-------------] 18/42
```

---

## 🏆 Sistema de Dificuldades

| Dificuldade | Minions (tipo 1) | Minions (tipo 2) | HP do Chefe | XP Bônus |
|-------------|------------------|------------------|-------------|----------|
| **Fácil**   |        2         |        1         |     100     |    50    |
| **Média**   |        3         |        2         |     300     |    100   |
| **Difícil** |        4         |        3         |     500     |    200   |

---

## 🛠️ Desenvolvimento

### Padrões de Commit

Este projeto segue **Conventional Commits**:

```bash
# Exemplos
git commit -m "feat: adicionar sistema de crafting"
git commit -m "fix: corrigir bug no cálculo de dano crítico"
git commit -m "docs: atualizar README com novos exemplos"
```

Consulte `git_notes.MD` para guia completo de Git.

### Estrutura de Código

- **Orientado a objetos**: Classes bem definidas e separadas
- **Type hints**: Facilita manutenção e IDE support
- **Logging integrado**: Debug facilitado com diferentes níveis
- **Modular**: Fácil adicionar novas classes, inimigos e habilidades

### Como Adicionar Nova Classe

1. Crie a classe em `models/personagem.py` herdando de `Personagem`
2. Defina os atributos iniciais no `__init__`
3. Implemente `ataque_basico` e 7 especiais (`esp_*`)
4. Adicione ao dicionário `ARQUETIPOS`
5. Configure custos e descrições no helper `especiais_do_personagem`

---

## 🤝 Contribuição

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feat/nova-classe`)
3. Commit suas mudanças (`git commit -m 'feat: adicionar classe Necromante'`)
4. Push para a branch (`git push origin feat/nova-classe`)
5. Abra um Pull Request

---

## 🛠️ Desenvolvedores:

- **João Vitor Pereira**
  - `Inventário` `Sistema de Saves` `Missões`

- **Pedro Henrique Santos Silva**
  - `Otimização de Missões` `Sistema de XP`

- **Pedro Henrique Oliveira Costa**
  - `QA (Quality Assurance)` `Documentação`

- **Henri José Sobral de Alcântara Mendonça**
  - `Estrutura de Missões` `Personagens`

- **Rone Marques Santos de de Jesus**
  - `Gestão do Projeto` `README`

- **João Francisco Costa**
  - `Sistema de XP` `Logger Otimizado`

- **Enzo Samuel Oliveira Gonçalves**
  - `Bug Fixes` `Correção de Loops`

---

## 🙏 Agradecimentos

- O obrigado de todo o grupo ao professor Mariano, pelos ensinamentos e pelo empenho e dedicação demonstrado por ele dentro e fora de sala.