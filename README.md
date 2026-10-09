# Checkpoint 02 – AI & Chatbot (FIAP)

Gráficos e gerenciamento de dados, classificação com dataviz, usando a base normalizada do Checkpoint 01.

## Estrutura

| Caminho | Conteúdo |
|---|---|
| `dados/base_saude_normalizada.csv` | Base do Checkpoint 01 (1000 pacientes, `;` como separador, `,` como decimal) |
| `dados/dicionario_de_dados.pdf` | Dicionário de dados da base |
| `src/config.py` | **Turma, RMs e nomes do grupo** (preencher antes de gerar a versão final) |
| `src/gerar_graficos.py` | Gera as 5 figuras em `graficos/` |
| `src/gerar_relatorio.py` | Monta o PDF no padrão ABNT NBR 14724 e o texto do e-mail |
| `entrega/Checkpoint02_<TURMA>.pdf` | **Arquivo único a ser enviado** |
| `entrega/email.txt` | Destinatário, assunto e corpo do e-mail |

## Como gerar

```bash
pip install -r requirements.txt
# 1. edite src/config.py com a turma, os RMs e os nomes
python src/gerar_graficos.py
python src/gerar_relatorio.py
```

A fonte usada é a Liberation Sans, métrica-compatível com a Arial (`/usr/share/fonts/truetype/liberation`).

## Os 5 gráficos (todos de tipos diferentes)

| Figura | Tipo | Pergunta respondida |
|---|---|---|
| 1 | Colunas | A frequência de exercício físico muda a taxa de diabetes? |
| 2 | Linhas | Como a taxa de diabetes evolui com a idade entre fumantes e não fumantes? |
| 3 | Caixa (boxplot) | Pacientes com diabetes têm IMC maior? |
| 4 | Dispersão | Qual a relação entre idade, pressão arterial e diabetes? |
| 5 | Mapa de calor | Quais variáveis se correlacionam com o diagnóstico? |

## Checklist dos requisitos

- [x] Usa a base do Checkpoint 01
- [x] 5 gráficos, nenhum repetido
- [x] Todos os gráficos com legenda
- [x] Gráficos legíveis: título, eixos com unidade, rótulos em português, cores acessíveis a daltônicos
- [x] Um parágrafo explicando cada gráfico
- [x] ABNT NBR 14724: capa, folha de rosto, sumário, A4, margens 3/2 cm, fonte 12, espaçamento 1,5,
      numeração no canto superior direito, figuras com identificação acima e fonte abaixo, referências
- [x] Entrega em um único arquivo PDF
- [ ] Preencher turma, RMs e nomes em `src/config.py` e gerar novamente
- [ ] Enviar para profalfonso.rodriguez@fiap.com.br com assunto `Checkpoint 02 - <TURMA>` e
      RM + nome dos integrantes, um abaixo do outro, no corpo do e-mail
- [ ] Prazo: 15/10/2026 (com atraso, até 19/10/2026, perde 2,5 pontos)
