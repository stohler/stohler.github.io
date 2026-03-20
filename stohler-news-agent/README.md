# Agente de Notícias para X (stohler)

Projeto para rodar um agente que:

1. recebe um **tema** configurável;
2. consulta diariamente jornais internacionais confiáveis via RSS;
3. seleciona manchetes e imagens mais relevantes sobre o tema;
4. resume o conteúdo (com IA opcional);
5. gera/publica **2 posts por dia no X**.

## Fontes de notícias usadas

- Reuters
- BBC
- AP News
- The Guardian
- NPR
- Financial Times

> As fontes estão em `news_agent/rss_sources.py`.

## Como funciona

- O módulo `news_fetcher` coleta notícias das fontes e calcula uma pontuação de relevância por tema.
- O módulo `ai_summarizer` usa Gemini (se configurada) para resumir em português.
- O módulo `post_builder` monta o texto final no limite do X.
- O módulo `x_client` publica no X e tenta anexar imagem quando disponível.
- O `runner` evita repetir links já postados via arquivo `.state/posted_articles.json`.

## Configuração local

### 1) Criar ambiente e instalar

```bash
cd stohler-news-agent
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install .
```

### 2) Configurar variáveis

```bash
cp .env.example .env
```

Edite `.env`:

- `TOPIC`: tema principal (ex.: `energia renovavel`)
- `TOPIC_KEYWORDS`: palavras-chave separadas por vírgula
- `GEMINI_API_KEY`: opcional, para sumarização melhor
- credenciais do X (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_TOKEN_SECRET`)
- `DRY_RUN=true` para testar sem publicar

### 3) Executar

```bash
news-agent
```

Para gerar 2 posts na mesma execução:

```bash
news-agent --posts-per-run 2
```

## Automação (2 posts/dia)

Workflow em `.github/workflows/post_x.yml` roda:

- 10:00 UTC
- 18:00 UTC

Cada execução publica 1 post (`POSTS_PER_RUN=1`), totalizando 2 por dia.

No repositório GitHub, configure em **Settings > Secrets and variables > Actions**:

- **Variables**:
  - `TOPIC`
  - `TOPIC_KEYWORDS`
  - `GEMINI_MODEL` (opcional, ex.: `gemini-2.0-flash`)
- **Secrets**:
  - `GEMINI_API_KEY` (opcional)
  - `X_API_KEY`
  - `X_API_SECRET`
  - `X_ACCESS_TOKEN`
  - `X_ACCESS_TOKEN_SECRET`

## Setup automático para Cloud Agents

Foi adicionada configuração de ambiente em:

- `.cursor/environment.json`
- `.cursor/setup-cloud-agent.sh`

No boot de cada cloud agent, o setup:

1. valida que a versão do Python é `>= 3.11`;
2. garante disponibilidade do `pip`;
3. executa automaticamente:

```bash
python3 -m pip install ./stohler-news-agent
```

Assim, o projeto já sobe pronto sem setup manual extra.

## Criar o repositório na conta `stohler`

No seu terminal autenticado no GitHub:

```bash
gh repo create stohler/agente-noticias-x --private --source=. --remote=origin --push
```

Se preferir público, troque `--private` por `--public`.

