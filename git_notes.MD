# 🧭 Guia de Prefixos para Commits (Conventional Commits)

Padronizar suas mensagens de commit ajuda a manter o histórico do projeto limpo, organizado e fácil de entender.

Abaixo estão os principais **prefixos** e seus significados:

---

| Prefixo | Tipo de Mudança | Quando Usar | Exemplo de Uso |
|----------|------------------|--------------|----------------|
| **feat:** | Nova funcionalidade | Sempre que você adiciona algo novo ao código ou projeto | `feat: adicionar componente de login` |

| **fix:** | Correção de erro | Quando você corrige um bug ou erro existente | `fix: corrigir erro de autenticação` |

| **docs:** | Documentação | Quando altera ou adiciona README, comentários, docs etc | `docs: atualizar instruções de instalação` |

| **style:** | Estilo (sem alterar funcionalidade) | Ajustes visuais, formatação, espaços, vírgulas etc | `style: formatar código com prettier` |

| **refactor:** | Refatoração de código | Quando melhora o código sem mudar o comportamento | `refactor: otimizar função de login` |

| **perf:** | Melhoria de performance | Quando torna o sistema mais rápido ou eficiente | `perf: melhorar tempo de carregamento da página` |

| **test:** | Testes | Quando cria, ajusta ou remove testes | `test: adicionar testes para componente de login` |

| **chore:** | Tarefas de manutenção | Mudanças que não afetam o código de produção (build, dependências, configs) | `chore: atualizar dependências do projeto` |

| **build:** | Processo de build ou dependências | Quando muda algo que afeta o build (webpack, npm, vite, etc) | `build: adicionar configuração do webpack` |

| **ci:** | Integração contínua | Quando altera pipelines, GitHub Actions, etc | `ci: ajustar workflow de deploy no GitHub Actions` |

| **revert:** | Reverter commit anterior | Quando desfaz uma alteração anterior | `revert: reverter commit 4f2a1b7` |

---

## 💡 Dicas de Boas Práticas

- Sempre use **letras minúsculas** nos prefixos.  
- Use o **imperativo** na mensagem (ex: "adicionar", não "adicionado").  
- Mantenha a mensagem curta e direta.  
- Evite commits genéricos como `update` ou `changes`.

---

## 🧩 Exemplo de Fluxo de Trabalho

```bash
# Atualizar a branch main
git checkout main
git pull origin main

# Voltar para sua branch
git checkout minha-branch

# Mesclar com a main atualizada
git merge main

# Adicionar e comitar mudanças
git add .
git commit -m "feat: adicionar botão de logout"

# Enviar para o repositório remoto
git push origin minha-branch
