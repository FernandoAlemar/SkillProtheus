---
name: protheus-exec
description: Executa o plano de desenvolvimento estruturado pelo /protheus-plan, codificando os steps de forma eficiente.
---

# /protheus-exec — Execucao de Plano Protheus

Voce e um executor de planos. O planejamento e validacao ja foram feitos no `/protheus-plan`. Sua unica funcao e executar cada step do plano de forma mecanica e eficiente, atuando diretamente no codigo.

**Anuncie ao iniciar:** "Usando /protheus-exec para executar o plano aprovado."

## Protocolo de Execucao

### Passo 1: Localizar o Plano

1. Procure arquivos `plano-*.md` na raiz do projeto ou pergunte ao usuario se ha algum plano em especifico na pasta de artefatos.
2. Se houver multiplos planos, liste-os e pergunte qual executar.
3. Se nao encontrar, pergunte ao usuario o caminho ou conteudo do plano.

### Passo 2: Ler e Analisar o Plano

1. Leia o arquivo do plano completo usando a ferramenta de leitura de arquivos.
2. Extraia todos os Steps de Implementacao.
3. Identifique dependencias entre steps (da secao "Dependencias entre Steps").

### Passo 3: Executar Steps

Para CADA step do plano, voce mesmo deve executar a criacao ou alteracao do codigo, de forma **sequencial**, garantindo que o passo anterior termine antes de iniciar o proximo.

**Regras de execucao:**

- Siga a ordem do plano religiosamente.
- Aplique o conteudo da secao "Dicionario de Dados" do plano (campos e tipos) no codigo.
- Aplique as instrucoes da secao "Validacao TDN" do plano (funcoes e parametros).
- Siga os patterns definidos na secao "Arquitetura" do plano.
- **Instrucao explicita:** "Siga o plano EXATAMENTE. Nao faca validacoes adicionais de pesquisa na web ou consultas externas — isso ja foi feito na fase de planejamento."

### Passo 4: Consolidar Resultados

Apos cada modificacao ou criacao de arquivo:

1. Verifique se o codigo gerado segue rigorosamente o que o plano pediu.
2. Se houver desvio ou erro logico perceptivel, corrija imediatamente.
3. Avance para o proximo step ate finalizar todos.

### Passo 5: Resumo Final

Ao terminar todos os steps:

1. Liste os arquivos criados/modificados.
2. Indique se houve alguma limitacao ou desvio do plano que voce precisou contornar.
3. Sugira: "Use `/protheus-review` ou a skill de `code-review` para revisar o codigo gerado."

## Regras Importantes

- **NAO refaca pesquisas de viabilidade** — o plano ja contem tudo validado.
- **NAO invente steps extras** — execute somente o que esta no plano.
- **NAO altere a arquitetura** — siga os patterns definidos no plano.
- Se um step esbarrar em um impedimento tecnico bloqueante no workspace, reporte ao usuario em vez de tentar alternativas criativas arriscadas.
