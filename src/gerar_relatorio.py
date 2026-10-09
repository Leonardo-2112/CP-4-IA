"""Gera o PDF do Checkpoint 02 no padrão ABNT NBR 14724 e o texto do e-mail de entrega.

Uso:
    python src/gerar_graficos.py   # gera as figuras
    python src/gerar_relatorio.py  # monta entrega/Checkpoint02_<TURMA>.pdf e entrega/email.txt

Formatação aplicada (NBR 14724:2011):
    - papel A4, margens superior/esquerda 3 cm e inferior/direita 2 cm;
    - fonte 12 (Arial/Liberation Sans) no texto e 10 em legendas, fontes e natureza do trabalho;
    - espaçamento 1,5 no texto e simples em legendas, fontes, natureza e referências;
    - páginas contadas a partir da folha de rosto e numeradas a partir da Introdução,
      no canto superior direito, a 2 cm da borda;
    - ilustrações com identificação na parte superior e fonte na parte inferior.
"""
from pathlib import Path

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,
                                PageBreak, PageTemplate, Paragraph, Spacer)
from reportlab.platypus.tableofcontents import TableOfContents

import config as cfg

RAIZ = Path(__file__).resolve().parent.parent
FIGURAS = RAIZ / "graficos"
ENTREGA = RAIZ / "entrega"
PDF = ENTREGA / f"Checkpoint02_{cfg.TURMA}.pdf"

FONTES = Path("/usr/share/fonts/truetype/liberation")
pdfmetrics.registerFont(TTFont("Arial", FONTES / "LiberationSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Bold", FONTES / "LiberationSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Arial-Italic", FONTES / "LiberationSans-Italic.ttf"))
pdfmetrics.registerFont(TTFont("Arial-BoldItalic", FONTES / "LiberationSans-BoldItalic.ttf"))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                              italic="Arial-Italic", boldItalic="Arial-BoldItalic")

LARGURA, ALTURA = A4
M_ESQ, M_SUP, M_DIR, M_INF = 3 * cm, 3 * cm, 2 * cm, 2 * cm
MANCHA = LARGURA - M_ESQ - M_DIR  # 16 cm

TITULO = "PERFIL DE SAÚDE E ESTILO DE VIDA"
SUBTITULO = "análise visual dos fatores associados ao diagnóstico de diabetes"

# ---------------------------------------------------------------- estilos
texto = ParagraphStyle("texto", fontName="Arial", fontSize=12, leading=18, alignment=TA_JUSTIFY,
                       firstLineIndent=1.25 * cm, spaceAfter=0)
centro = ParagraphStyle("centro", parent=texto, alignment=TA_CENTER, firstLineIndent=0)
centro_negrito = ParagraphStyle("centro_negrito", parent=centro, fontName="Arial-Bold")
secao1 = ParagraphStyle("secao1", fontName="Arial-Bold", fontSize=12, leading=18, alignment=TA_LEFT,
                        spaceBefore=0, spaceAfter=18)
secao2 = ParagraphStyle("secao2", parent=secao1, spaceBefore=18)
titulo_sem_numero = ParagraphStyle("titulo_sem_numero", parent=secao1, alignment=TA_CENTER)
legenda = ParagraphStyle("legenda", fontName="Arial", fontSize=10, leading=12, alignment=TA_CENTER,
                         spaceBefore=12, spaceAfter=4)
fonte_fig = ParagraphStyle("fonte_fig", parent=legenda, spaceBefore=4, spaceAfter=12)
# Alinhada à esquerda para não abrir espaços grandes entre as palavras na coluna estreita
natureza = ParagraphStyle("natureza", fontName="Arial", fontSize=10, leading=12, alignment=TA_LEFT,
                          leftIndent=8 * cm)
referencia = ParagraphStyle("referencia", fontName="Arial", fontSize=12, leading=14, alignment=TA_LEFT,
                            spaceAfter=14)


# ---------------------------------------------------------------- documento
class Relatorio(BaseDocTemplate):
    """Registra as seções no sumário com a numeração ABNT (capa não é contada)."""

    def afterFlowable(self, flowable):
        nivel = getattr(flowable, "nivel_sumario", None)
        if nivel is not None:
            self.notify("TOCEntry", (nivel, flowable.getPlainText(), self.page - 1))


def centralizado(c, texto_, y, estilo):
    p = Paragraph(texto_, estilo)
    _, h = p.wrap(MANCHA, ALTURA)
    p.drawOn(c, M_ESQ, y - h)
    return h


def autores_html():
    return "<br/>".join(f"{rm} – {nome.upper()}" for rm, nome in cfg.INTEGRANTES)


def desenhar_capa(c, _doc):
    c.saveState()
    topo = ALTURA - M_SUP
    centralizado(c, f"{cfg.INSTITUICAO}<br/>{cfg.CURSO}", topo, centro_negrito)
    centralizado(c, autores_html(), topo - 4 * cm, centro)
    centralizado(c, f"<b>{TITULO}:</b><br/>{SUBTITULO}", ALTURA / 2 + 1 * cm, centro)
    centralizado(c, f"{cfg.CIDADE}<br/>{cfg.ANO}", M_INF + 1.6 * cm, centro)
    c.restoreState()


def desenhar_folha_rosto(c, _doc):
    # Os integrantes (com RM) aparecem só na capa, por pedido do grupo
    c.saveState()
    y_titulo = ALTURA / 2 + 3 * cm
    h = centralizado(c, f"<b>{TITULO}:</b><br/>{SUBTITULO}", y_titulo, centro)
    nota = (f"Trabalho apresentado à disciplina {cfg.DISCIPLINA}, do curso de Tecnologia em "
            f"Análise e Desenvolvimento de Sistemas da Faculdade de Informática e Administração "
            f"Paulista (FIAP), como requisito parcial para a avaliação do "
            f"{cfg.CHECKPOINT.replace(' ', '&nbsp;')}."
            f"<br/><br/>Orientador: {cfg.PROFESSOR}")
    centralizado(c, nota, y_titulo - h - 2 * cm, natureza)
    centralizado(c, f"{cfg.CIDADE}<br/>{cfg.ANO}", M_INF + 1.6 * cm, centro)
    c.restoreState()


def numerar(c, doc):
    c.saveState()
    c.setFont("Arial", 10)
    # A folha de rosto é a página 1; a capa não é contada.
    c.drawRightString(LARGURA - M_DIR, ALTURA - 2 * cm, str(doc.page - 1))
    c.restoreState()


# ---------------------------------------------------------------- conteúdo
def titulo(texto_, nivel):
    p = Paragraph(texto_, secao1 if nivel == 0 else secao2)
    p.nivel_sumario = nivel
    return p


def par(texto_):
    return Paragraph(texto_, texto)


def figura(numero, titulo_fig, arquivo, largura=MANCHA):
    img = Image(str(FIGURAS / arquivo))
    escala = largura / img.imageWidth
    img.drawWidth, img.drawHeight = largura, img.imageHeight * escala
    return KeepTogether([
        Paragraph(f"Figura {numero} – {titulo_fig}", legenda),
        img,
        Paragraph("Fonte: Elaborado pelos autores (2026), com base na base de dados normalizada "
                  "do Checkpoint 01.", fonte_fig),
    ])


def conteudo():
    s = []

    # Capa e folha de rosto (desenhadas nos templates) ---------------------------
    s += [NextPageTemplate("rosto"), Spacer(1, 1), PageBreak()]
    s += [NextPageTemplate("sumario"), Spacer(1, 1), PageBreak()]

    # Sumário --------------------------------------------------------------------
    sumario = TableOfContents(dotsMinLevel=0)
    sumario.levelStyles = [
        ParagraphStyle("sum1", fontName="Arial-Bold", fontSize=12, leading=18, leftIndent=0,
                       firstLineIndent=0),
        ParagraphStyle("sum2", fontName="Arial", fontSize=12, leading=18, leftIndent=0,
                       firstLineIndent=0),
    ]
    s += [Paragraph("SUMÁRIO", titulo_sem_numero), sumario,
          NextPageTemplate("textual"), PageBreak()]

    # 1 Introdução ---------------------------------------------------------------
    s += [titulo("1 INTRODUÇÃO", 0)]
    s += [par(
        "Este trabalho tem como objetivo utilizar a base de dados normalizada no Checkpoint 01 para "
        "responder, por meio de visualização de dados (<i>dataviz</i>), à seguinte pergunta central: "
        "quais características de saúde e de estilo de vida estão associadas ao diagnóstico de "
        "diabetes? Como o dicionário de dados indica a variável Diabetes como a variável-alvo sugerida "
        "para modelos de classificação (diagnóstico presente em 26,2% dos 1.000 pacientes), os "
        "gráficos foram "
        "construídos para comparar o grupo de pacientes com diabetes ao grupo sem a doença. Foram "
        "elaborados cinco gráficos de tipos diferentes (colunas agrupadas, linhas, caixa, dispersão e "
        "mapa de calor), cada um acompanhado de um parágrafo que explica o que ele mostra.")]

    # 2 Base de dados e metodologia ----------------------------------------------
    s += [Spacer(1, 18), titulo("2 BASE DE DADOS E METODOLOGIA", 0)]
    s += [par(
        "A base utilizada é sintética, gerada para fins didáticos, e possui 1.000 registros de "
        "pacientes, sem valores ausentes nem linhas duplicadas. Cada registro contém idade, sexo, "
        "altura, peso, hábito de fumar, frequência de exercício físico, meio de transporte, região, "
        "pressão arterial sistólica, colesterol total, renda mensal, posse de plano de saúde e "
        "diagnóstico de diabetes. No Checkpoint 01, as variáveis numéricas receberam normalização "
        "Min-Max (colunas com prefixo N_), as categóricas binárias foram convertidas em 0 e 1, a "
        "frequência de exercício recebeu codificação ordinal e as variáveis transporte e região "
        "passaram por <i>One-Hot Encoding</i>. Para que os gráficos fossem compreendidos visualmente, "
        "foram usados os valores originais das variáveis numéricas e os códigos foram traduzidos de "
        "volta para rótulos conforme o dicionário de dados (por exemplo, 1 = “Com diabetes” e "
        "0 = “Sem diabetes”). Também foram derivados o Índice de Massa Corporal (IMC), "
        "calculado como peso dividido pelo quadrado da altura em metros, e seis faixas etárias. O "
        "processamento foi feito em Python com as bibliotecas pandas (MCKINNEY, 2010) e Matplotlib "
        "(HUNTER, 2007), utilizando cores distinguíveis por pessoas com daltonismo e formatos de "
        "marcador diferentes para cada grupo.")]

    # 3 Análise dos gráficos -----------------------------------------------------
    s += [PageBreak()]
    secoes = []

    secoes.append([titulo("3 ANÁLISE DOS GRÁFICOS", 0),
                   titulo("3.1 Exercício físico, tabagismo e diabetes", 1), par(
        "A Figura 1 apresenta, em um gráfico de colunas agrupadas, o percentual de pacientes com "
        "diabetes em cada nível de frequência de exercício físico, separando não fumantes (azul) e "
        "fumantes (laranja); a taxa geral de cada nível aparece abaixo do eixo. A taxa geral diminui "
        "à medida que a prática de atividade física aumenta: 38,8% entre os que nunca se exercitam, "
        "22,0% entre os que se exercitam às vezes e 18,0% entre os que se exercitam frequentemente. "
        "Em todos os níveis, os fumantes têm percentual maior que os não fumantes, e entre os mais "
        "ativos a taxa dos fumantes é quase o dobro (28,6% contra 14,8%). A combinação de sedentarismo e tabagismo "
        "concentra o maior risco observado (46,1%), mais de três vezes a taxa dos não fumantes que "
        "se exercitam com frequência, o que indica as duas variáveis como relevantes para "
        "diferenciar os pacientes com e sem a doença."),
        figura(1, "Taxa de diabetes por frequência de exercício físico e tabagismo", "figura1.png")])

    secoes.append([titulo("3.2 Idade, sexo e diabetes", 1), par(
        "A Figura 2 utiliza um gráfico de linhas para mostrar como a taxa de diabetes evolui ao "
        "longo das faixas etárias. A linha preta, que representa todos os pacientes, cresce de forma "
        "praticamente contínua, de 13,6% na faixa de 18 a 29 anos para 44,0% na faixa de 70 a 79 "
        "anos, o que evidencia a idade como fator associado ao diagnóstico (r = 0,25). As linhas "
        "tracejadas separam os sexos: no conjunto, os homens têm taxa maior (31,2%) que as mulheres "
        "(21,3%), e na faixa de 70 a 79 anos chegam a 49,4%, contra 37,1% das mulheres. As "
        "oscilações das linhas por sexo, como a queda entre as mulheres de 60 a 69 anos, decorrem "
        "do menor número de pacientes em cada faixa (entre 67 e 109 pessoas), mas a tendência de "
        "alta com a idade se mantém nos dois grupos."),
        figura(2, "Taxa de diabetes por faixa etária, geral e por sexo", "figura2.png")])

    secoes.append([titulo("3.3 Índice de Massa Corporal e diabetes", 1), par(
        "A Figura 3 é um gráfico de caixa (<i>boxplot</i>), que resume a distribuição do IMC em cada "
        "grupo: a caixa reúne os 50% centrais dos pacientes, a linha branca marca a mediana, o losango "
        "marca a média, as hastes indicam a variação típica e os pontos cinza são valores atípicos. "
        "A caixa dos pacientes com diabetes está deslocada para cima: a mediana do IMC é 26,4 "
        "kg/m², contra 24,7 kg/m² no grupo sem diabetes, e os 50% centrais vão de 24,4 a 29,3 kg/m², "
        "contra 22,2 a 27,6 kg/m². A linha tracejada marca o IMC 25, a partir do qual a Organização "
        "Mundial da Saúde classifica o sobrepeso (WORLD HEALTH ORGANIZATION, 2000); 64,1% dos "
        "pacientes com diabetes estão acima desse limite, contra 47,6% dos pacientes sem a doença. "
        "Ainda assim, as caixas se sobrepõem bastante, o que indica que o IMC contribui para o risco, "
        "mas não o determina isoladamente (r = 0,21)."),
        figura(3, "Distribuição do IMC por diagnóstico de diabetes", "figura3.png")])

    secoes.append([titulo("3.4 Idade e pressão arterial", 1), par(
        "A Figura 4 é um gráfico de dispersão em que cada ponto representa um paciente, posicionado "
        "pela idade (eixo horizontal) e pela pressão arterial sistólica (eixo vertical); os círculos "
        "azuis são pacientes sem diabetes e os triângulos laranja, pacientes com diabetes. A linha "
        "tracejada mostra a tendência geral: a pressão sobe cerca de 3,3 mmHg a cada dez anos de "
        "vida, de aproximadamente 110 mmHg aos 18 anos para 130 mmHg aos 79 anos, com correlação "
        "positiva moderada (r = 0,54), a mais forte entre as variáveis da base. Os "
        "triângulos se concentram na parte direita e superior do gráfico, o que confirma que os "
        "pacientes com diabetes são, em média, mais velhos (55,1 anos contra 45,0) e têm pressão "
        "arterial mais alta (123,5 mmHg contra 118,2 mmHg)."),
        figura(4, "Idade e pressão arterial sistólica por diagnóstico de diabetes", "figura4.png")])

    secoes.append([titulo("3.5 Correlação entre as variáveis", 1), par(
        "A Figura 5 é um mapa de calor com o coeficiente de correlação de Pearson entre as variáveis "
        "numéricas e binárias da base. Tons de vermelho indicam correlação positiva (as duas "
        "variáveis aumentam juntas), tons de azul indicam correlação negativa (uma aumenta enquanto a "
        "outra diminui) e o cinza claro indica ausência de relação; quanto mais forte a cor, mais "
        "forte a relação. Na última linha, que relaciona cada variável com o diagnóstico, as maiores "
        "associações positivas são com peso (0,27), idade (0,25), IMC e pressão (0,21), colesterol "
        "(0,19) e tabagismo (0,12), enquanto o exercício físico tem associação negativa (−0,18) "
        "e a renda praticamente não tem relação (0,04). Como nenhuma correlação isolada é forte, o "
        "diagnóstico depende da combinação de vários fatores, o que justifica o uso de um modelo de "
        "classificação com múltiplas variáveis."),
        figura(5, "Correlação entre as variáveis de saúde e estilo de vida", "figura5.png",
                  largura=14.5 * cm)])
    for i, bloco in enumerate(secoes):
        # título, parágrafo e figura de cada subseção ficam na mesma página
        s += ([] if i == 0 else [PageBreak()]) + [KeepTogether(bloco)]

    # 4 Conclusão ----------------------------------------------------------------
    s += [PageBreak(), titulo("4 CONCLUSÃO", 0)]
    s += [par(
        "Os cinco gráficos mostram um perfil consistente: os pacientes com diabetes da base são, em "
        "média, mais velhos, mais pesados, mais sedentários, com pressão arterial e colesterol mais "
        "altos, e o diagnóstico é mais frequente entre fumantes e entre homens. Por outro lado, a "
        "renda não apresentou relação com o diagnóstico. Como cada fator, isoladamente, tem "
        "associação apenas fraca ou moderada com a doença, a visualização indica que um modelo de "
        "classificação deve considerar as variáveis em conjunto, priorizando idade, peso ou IMC, "
        "exercício físico, tabagismo, pressão arterial e colesterol; como próxima etapa, recomenda-se "
        "treinar esse modelo com as variáveis normalizadas no Checkpoint 01. Por se tratar de uma "
        "base sintética e de correlações, os resultados têm caráter exploratório e didático, não "
        "indicam relação de causa e efeito e não devem ser generalizados para a população real.")]

    # Referências ----------------------------------------------------------------
    s += [PageBreak(), titulo("REFERÊNCIAS", 0)]
    s[-1].style = titulo_sem_numero
    refs = [
        "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. <b>NBR 6023</b>: informação e documentação: "
        "referências: elaboração. Rio de Janeiro: ABNT, 2018.",
        "ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. <b>NBR 14724</b>: informação e documentação: "
        "trabalhos acadêmicos: apresentação. Rio de Janeiro: ABNT, 2011.",
        "HUNTER, J. D. Matplotlib: a 2D graphics environment. <b>Computing in Science &amp; "
        "Engineering</b>, v. 9, n. 3, p. 90-95, 2007.",
        "BASE DE SAÚDE NORMALIZADA. <b>Dicionário de dados</b>: perfil de saúde e estilo de vida. "
        "Base sintética, 1.000 registros. São Paulo: FIAP, 2026.",
        "MCKINNEY, W. Data structures for statistical computing in Python. <i>In</i>: PYTHON IN "
        "SCIENCE CONFERENCE, 9., 2010, Austin. <b>Proceedings</b> [...]. Austin: SciPy, 2010. "
        "p. 56-61.",
        "RODRIGUEZ, A. <b>AI &amp; Chatbot</b>: Checkpoint 02: gráficos e gerenciamento de dados, "
        "classificação com dataviz. São Paulo: FIAP, 2026. Material didático.",
        "WORLD HEALTH ORGANIZATION. <b>Obesity</b>: preventing and managing the global epidemic. "
        "Geneva: WHO, 2000. (WHO Technical Report Series, 894).",
    ]
    s += [Paragraph(r, referencia) for r in refs]
    return s


def gerar_pdf():
    ENTREGA.mkdir(exist_ok=True)
    doc = Relatorio(
        str(PDF), pagesize=A4, leftMargin=M_ESQ, rightMargin=M_DIR, topMargin=M_SUP,
        bottomMargin=M_INF, title=f"{cfg.CHECKPOINT} – Perfil de saúde e estilo de vida",
        author=", ".join(nome for _, nome in cfg.INTEGRANTES),
        subject=f"{cfg.DISCIPLINA} – {cfg.CHECKPOINT} – {cfg.TURMA}",
    )
    quadro = Frame(M_ESQ, M_INF, MANCHA, ALTURA - M_SUP - M_INF, id="corpo",
                   leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates([
        PageTemplate("capa", [quadro], onPage=desenhar_capa),
        PageTemplate("rosto", [quadro], onPage=desenhar_folha_rosto),
        PageTemplate("sumario", [quadro]),
        PageTemplate("textual", [quadro], onPage=numerar),
    ])
    doc.multiBuild(conteudo())


def gerar_email():
    corpo = [
        f"Para: {cfg.EMAIL_PROFESSOR}",
        f"Assunto: {cfg.CHECKPOINT} - {cfg.TURMA}",
        f"Anexo: {PDF.name}",
        "",
        "Prezado Prof. Alfonso,",
        "",
        f"Segue em anexo o {cfg.CHECKPOINT} do nosso grupo.",
        "",
        "Integrantes:",
        *[f"{rm} - {nome}" for rm, nome in cfg.INTEGRANTES],
        "",
        "Atenciosamente,",
        "",
    ]
    (ENTREGA / "email.txt").write_text("\n".join(corpo), encoding="utf-8")


if __name__ == "__main__":
    gerar_pdf()
    gerar_email()
    print(f"Gerado: {PDF.relative_to(RAIZ)} e entrega/email.txt")
