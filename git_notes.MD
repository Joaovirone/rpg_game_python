# 🧭 Guia Completo de Comandos Git com Conventional Commits

Padronizar suas mensagens de commit ajuda a manter o histórico do projeto limpo, organizado e fácil de entender.

---

## 🏷️ Padrão de Conventional Commits (Prefixos)

| Prefixo | Tipo de Mudança | Quando Usar | Exemplo |

| :--- | :--- | :--- | :--- |

| **feat:** | Nova funcionalidade (MINOR) | Adiciona algo novo ao código ou projeto. | `feat: adicionar componente de login` |

| **fix:** | Correção de erro (PATCH) | Corrige um bug ou erro existente. | `fix: corrigir erro de autenticação` |

| **docs:** | Documentação | Altera ou adiciona README, comentários, docs. | `docs: atualizar instruções de instalação` |

| **style:** | Estilo (sem alterar funcionalidade) | Ajustes visuais, formatação, espaços, vírgulas. | `style: formatar código com prettier` |

| **refactor:** | Refatoração de código | Melhora o código sem mudar o comportamento. | `refactor: otimizar função de login` |

| **perf:** | Melhoria de performance | Torna o sistema mais rápido ou eficiente. | `perf: melhorar tempo de carregamento` |

| **test:** | Testes | Cria, ajusta ou remove testes. | `test: adicionar testes para componente de login` |

| **chore:** | Tarefas de manutenção | Mudanças que não afetam o código de produção (build, dependências, configs). | `chore: atualizar dependências do projeto` |

| **build:** | Processo de build ou dependências | Muda algo que afeta o build (webpack, npm, etc). | `build: adicionar configuração do webpack` |

| **ci:** | Integração contínua | Altera pipelines, GitHub Actions, etc. | `ci: ajustar workflow de deploy` |

| **revert:** | Reverter commit anterior | Desfaz uma alteração anterior. | `revert: reverter commit 4f2a1b7` |

---

## 💡 Dicas e Boas Práticas

* Sempre use **letras minúsculas** nos prefixos.

* Use o **imperativo** na mensagem (ex: "adicionar", não "adicionado").

* Mantenha a mensagem curta e direta (máx. 50 caracteres na primeira linha).

* **BREAKING CHANGE (Major Version):** Adicione um `!` após o prefixo se houver quebra de compatibilidade. Ex: `feat!: alterar assinatura da função`.

---

## 🛠️ Comandos Essenciais do Git

### 1. Preparação e Mudança de Branch

| Comando | Descrição |
| :--- | :--- |

| `git status` | Exibe o estado da área de trabalho. |

| `git branch` | Lista as branches locais. |

| `git checkout -b <nome-branch>` | Cria e muda para uma nova branch. |

| `git checkout <nome-branch>` | Alterna para uma branch existente. |

### 2. Sincronização e Mesclagem

| Comando | Descrição |

| :--- | :--- |

| `git pull origin main` | Baixa e mescla as últimas alterações da `main` remota. |

| `git merge main` | Mescla as alterações da `main` na sua branch atual. |

| `git merge --abort` | Aborta o processo de merge em caso de conflito. |

### 3. Commit e Staging

| Comando | Descrição |

| :--- | :--- |

| `git add .` | Adiciona **todos** os arquivos modificados e novos à área de staging. |

| `git add <caminho/arquivo>` | Adiciona um arquivo específico. |

| `git reset <arquivo>` | Remove um arquivo da área de staging (desfaz o `git add`). |

| `git commit -m "<prefixo>: <mensagem>"` | Cria o commit padronizado. |

| **Exemplo:** | `git commit -m "feat: adicionar botão de logout"` |

### 4. Correção e Histórico

| Comando | Descrição |

| :--- | :--- |

| `git commit --amend` | Altera a mensagem do último commit (ou adiciona arquivos a ele). |

| `git log --oneline` | Exibe o histórico de commits resumido. |

| `git reset --soft HEAD~1` | Desfaz o último commit, **mantendo as alterações** na área de staging. |

| `git reset --hard HEAD~1` | Desfaz o último commit, **descartando as alterações** (CUIDADO!). |

### 5. Envio Remoto

| Comando | Descrição |

| :--- | :--- |

| `git push origin <sua-branch>` | Envia os commits locais para o repositório remoto. |

| `git push -f` | Força o envio, sobrescrevendo o histórico remoto (necessário após `amend` ou `rebase`). **Use com cautela.** |