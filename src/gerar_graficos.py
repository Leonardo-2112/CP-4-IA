"""Gera os 5 gráficos do Checkpoint 02 a partir da base normalizada do Checkpoint 01.

Uso: python src/gerar_graficos.py
Saída: graficos/figura1.png ... graficos/figura5.png
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap

RAIZ = Path(__file__).resolve().parent.parent
BASE = RAIZ / "dados" / "base_saude_normalizada.csv"
SAIDA = RAIZ / "graficos"

# Paleta (categórica validada para daltonismo + tinta neutra para textos e eixos)
AZUL, LARANJA = "#2a78d6", "#eb6834"
VIOLETA, AQUA = "#4a3aa7", "#1baf7a"  # sexo (figura 2), cores distintas de diagnóstico/tabagismo
TINTA, TINTA_2, MUDO = "#0b0b0b", "#52514e", "#898781"
GRADE, EIXO = "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "font.family": "Liberation Sans",
    "font.size": 11,
    "text.color": TINTA,
    "axes.labelcolor": TINTA_2,
    "axes.edgecolor": EIXO,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.titlelocation": "left",
    "axes.titlepad": 12,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.color": GRADE,
    "grid.linewidth": 0.8,
    "xtick.color": TINTA_2,
    "ytick.color": TINTA_2,
    "legend.frameon": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def carregar() -> pd.DataFrame:
    df = pd.read_csv(BASE, sep=";", decimal=",")
    # Decodifica os campos conforme o dicionário de dados do Checkpoint 01
    df["Diagnostico"] = df["Diabetes"].map({0: "Sem diabetes", 1: "Com diabetes"})
    df["Fumante"] = df["Smoker"].map({0: "Não fumantes", 1: "Fumantes"})
    df["Sexo"] = df["Gender"].map({0: "Feminino", 1: "Masculino"})
    df["Exercicio"] = df["ExerciseFrequency"].map({0.0: "Nunca", 0.5: "Às vezes", 1.0: "Frequentemente"})
    df["IMC"] = df["Weight_kg"] / (df["Height_cm"] / 100) ** 2
    df["FaixaEtaria"] = pd.cut(
        df["Age"], bins=[17, 29, 39, 49, 59, 69, 79],
        labels=["18–29", "30–39", "40–49", "50–59", "60–69", "70–79"],
    )
    return df


def pct(valor: float) -> str:
    return f"{valor:.1f}%".replace(".", ",")


def figura1(df):
    """Colunas agrupadas: taxa de diabetes por frequência de exercício e tabagismo."""
    ordem = ["Nunca", "Às vezes", "Frequentemente"]
    t = df.groupby(["Exercicio", "Fumante"])["Diabetes"].mean().unstack().loc[ordem] * 100
    geral = df.groupby("Exercicio")["Diabetes"].mean().loc[ordem] * 100
    n = df.groupby("Exercicio").size().loc[ordem]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    x = np.arange(len(ordem))
    largura = 0.36
    for desloc, grupo, cor in [(-largura / 2, "Não fumantes", AZUL), (largura / 2, "Fumantes", LARANJA)]:
        # 0.02 de folga entre as barras vizinhas
        barras = ax.bar(x + desloc, t[grupo], width=largura - 0.02, color=cor, label=grupo, zorder=2)
        for bb, v in zip(barras, t[grupo]):
            ax.text(bb.get_x() + bb.get_width() / 2, v + 0.8, pct(v), ha="center", va="bottom",
                    fontsize=10, fontweight="bold", color=TINTA)
    # A taxa geral de cada nível vai no rótulo do eixo para não poluir as barras
    ax.set_xticks(x, [f"{o} (n = {int(k)})\ngeral: {pct(g)}" for o, k, g in zip(ordem, n, geral)])
    ax.set_title("Taxa de diabetes por frequência de exercício físico e tabagismo")
    ax.set_xlabel("Frequência de exercício físico")
    ax.set_ylabel("Pacientes com diabetes (%)")
    ax.set_ylim(0, 55)
    ax.grid(axis="x", visible=False)
    ax.legend(title="Grupo", loc="upper right", title_fontsize=10)
    fig.savefig(SAIDA / "figura1.png")
    plt.close(fig)


def figura2(df):
    """Linhas: taxa de diabetes por faixa etária, geral e por sexo."""
    geral = df.groupby("FaixaEtaria", observed=True)["Diabetes"].mean() * 100
    sexo = df.groupby(["FaixaEtaria", "Sexo"], observed=True)["Diabetes"].mean().unstack() * 100
    rotulos = geral.index.astype(str)

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for grupo, cor, marcador in [("Feminino", VIOLETA, "s"), ("Masculino", AQUA, "^")]:
        ax.plot(rotulos, sexo[grupo], color=cor, linewidth=2, linestyle="--", marker=marcador,
                markersize=8, markeredgecolor="white", markeredgewidth=1.2, label=grupo, zorder=3)
    ax.plot(rotulos, geral, color=TINTA, linewidth=2.6, marker="o", markersize=8,
            markeredgecolor="white", markeredgewidth=1.5, label="Geral", zorder=4)
    # Rótulos só nas pontas das linhas, para não encobrir os pontos
    ax.annotate(pct(geral.iloc[0]), (0, geral.iloc[0]), xytext=(-10, 0), textcoords="offset points",
                ha="right", va="center", fontsize=9.5, fontweight="bold", color=TINTA)
    for serie, negrito in [(sexo["Feminino"], False), (sexo["Masculino"], False), (geral, True)]:
        ultimo = serie.iloc[-1]
        ax.annotate(pct(ultimo), (len(geral) - 1, ultimo), xytext=(10, 0), textcoords="offset points",
                    va="center", fontsize=9.5, color=TINTA, fontweight="bold" if negrito else "normal")
    ax.set_title("Taxa de diabetes por faixa etária: geral e por sexo")
    ax.set_xlabel("Faixa etária (anos)")
    ax.set_ylabel("Pacientes com diabetes (%)")
    ax.set_ylim(0, 60)
    ax.set_xlim(-0.75, len(geral) - 0.3)
    ax.legend(title="Grupo", loc="upper left", title_fontsize=10)
    fig.savefig(SAIDA / "figura2.png")
    plt.close(fig)


def figura3(df):
    """Boxplot: distribuição do IMC por diagnóstico de diabetes."""
    grupos = ["Sem diabetes", "Com diabetes"]
    dados = [df.loc[df["Diagnostico"] == g, "IMC"] for g in grupos]
    cores = [AZUL, LARANJA]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    bp = ax.boxplot(dados, widths=0.45, patch_artist=True, showmeans=True,
                    medianprops=dict(color="white", linewidth=2),
                    meanprops=dict(marker="D", markerfacecolor="white", markeredgecolor=TINTA, markersize=6),
                    whiskerprops=dict(color=TINTA_2), capprops=dict(color=TINTA_2),
                    flierprops=dict(marker="o", markersize=4, markerfacecolor=MUDO, markeredgecolor="none"))
    for caixa, cor in zip(bp["boxes"], cores):
        caixa.set_facecolor(cor)
        caixa.set_edgecolor(cor)
    ax.set_xticks([1, 2], [f"{g}\n(n = {len(d)})" for g, d in zip(grupos, dados)])
    for i, d in enumerate(dados, start=1):
        ax.text(i + 0.27, d.median(), f"Mediana {d.median():.1f}".replace(".", ","),
                va="center", fontsize=10, color=TINTA)
    ax.axhline(25, color=MUDO, linestyle="--", linewidth=1, zorder=1)
    ax.set_xlim(0.5, 2.7)
    ax.set_title("Distribuição do IMC por diagnóstico de diabetes")
    ax.set_xlabel("Diagnóstico")
    ax.set_ylabel("IMC (kg/m²)")
    ax.grid(axis="x", visible=False)
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=AZUL, label="Sem diabetes"), Patch(color=LARANJA, label="Com diabetes"),
                       Line2D([], [], marker="D", color="none", markerfacecolor="white",
                              markeredgecolor=TINTA, label="Média"),
                       Line2D([], [], marker="o", color="none", markerfacecolor=MUDO,
                              markeredgecolor="none", label="Valores atípicos"),
                       Line2D([], [], color=MUDO, linestyle="--", label="IMC 25 (início do sobrepeso)")],
              loc="upper left", ncol=2, fontsize=9.5)
    ax.set_ylim(13, 41)
    fig.savefig(SAIDA / "figura3.png")
    plt.close(fig)


def figura4(df):
    """Dispersão: idade x pressão arterial sistólica, por diagnóstico."""
    fig, ax = plt.subplots(figsize=(8, 5))
    for grupo, cor, marcador in [("Sem diabetes", AZUL, "o"), ("Com diabetes", LARANJA, "^")]:
        d = df[df["Diagnostico"] == grupo]
        ax.scatter(d["Age"], d["BloodPressure"], s=26, c=cor, marker=marcador, alpha=0.65,
                   edgecolors="white", linewidths=0.5, label=grupo, zorder=2)
    a, b = np.polyfit(df["Age"], df["BloodPressure"], 1)
    x = np.array([18, 79])
    r = df["Age"].corr(df["BloodPressure"])
    ax.plot(x, a * x + b, color=TINTA, linewidth=2, linestyle="--", zorder=3,
            label=f"Tendência geral (r = {r:.2f})".replace(".", ","))
    ax.set_title("Idade x pressão arterial sistólica por diagnóstico de diabetes")
    ax.set_xlabel("Idade (anos)")
    ax.set_ylabel("Pressão arterial sistólica (mmHg)")
    ax.legend(loc="upper left", markerscale=1.4)
    fig.savefig(SAIDA / "figura4.png")
    plt.close(fig)


def figura5(df):
    """Mapa de calor: matriz de correlação entre as variáveis da base."""
    colunas = {
        "Age": "Idade", "Weight_kg": "Peso", "Height_cm": "Altura", "IMC": "IMC",
        "BloodPressure": "Pressão", "Cholesterol": "Colesterol", "Income": "Renda",
        "ExerciseFrequency": "Exercício", "Smoker": "Fumante", "Diabetes": "Diabetes",
    }
    completa = df[list(colunas)].rename(columns=colunas).corr()
    # Triângulo inferior sem a diagonal (r = 1 de cada variável com ela mesma)
    corr = completa.iloc[1:, :-1]
    mascara = np.triu(np.ones_like(corr, dtype=bool), k=1)
    valores = np.ma.array(corr.values, mask=mascara)

    # Divergente azul <-> vermelho com ponto médio cinza neutro
    cmap = LinearSegmentedColormap.from_list("div", ["#104281", "#3987e5", "#f0efec", "#e66767", "#a82c2c"])
    cmap.set_bad("white")

    fig, ax = plt.subplots(figsize=(8, 6.6))
    im = ax.imshow(valores, cmap=cmap, vmin=-1, vmax=1)
    n = len(corr)
    for i in range(n):
        for j in range(i + 1):
            v = corr.iloc[i, j]
            ax.text(j, i, f"{v:.2f}".replace(".", ","), ha="center", va="center", fontsize=9,
                    color="white" if abs(v) >= 0.6 else TINTA)
    ax.set_xticks(range(n), corr.columns, rotation=45, ha="right")
    ax.set_yticks(range(n), corr.index)
    ax.grid(False)
    for lado in ["left", "bottom"]:
        ax.spines[lado].set_visible(False)
    ax.tick_params(length=0)
    barra = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    barra.set_label("Coeficiente de correlação de Pearson (r)")
    barra.set_ticks([-1, -0.5, 0, 0.5, 1], labels=["−1,0", "−0,5", "0", "0,5", "1,0"])
    barra.outline.set_visible(False)
    ax.set_title("Correlação entre as variáveis de saúde e estilo de vida")
    fig.savefig(SAIDA / "figura5.png")
    plt.close(fig)


def resumo(df):
    """Imprime os números citados nos textos do relatório."""
    print((df.groupby(["Exercicio", "Fumante"])["Diabetes"].mean().unstack() * 100).round(1))
    print((df.groupby(["FaixaEtaria", "Sexo"], observed=True)["Diabetes"].mean().unstack() * 100).round(1))
    print("Sexo:", (df.groupby("Sexo")["Diabetes"].mean() * 100).round(1).to_dict())
    print("Exercício:", (df.groupby("Exercicio")["Diabetes"].mean() * 100).round(1).to_dict())
    print((df.groupby(["FaixaEtaria", "Fumante"], observed=True)["Diabetes"].mean().unstack() * 100).round(1))
    print(df.groupby(["FaixaEtaria", "Fumante"], observed=True).size().unstack())
    print("Fumante:", (df.groupby("Fumante")["Diabetes"].mean() * 100).round(1).to_dict())
    print(df.groupby("Diagnostico")["IMC"].describe().round(2))
    print(df.groupby("Diagnostico")[["Age", "BloodPressure"]].mean().round(1))
    print("r idade x pressão:", round(df["Age"].corr(df["BloodPressure"]), 2))


if __name__ == "__main__":
    SAIDA.mkdir(exist_ok=True)
    base = carregar()
    for f in (figura1, figura2, figura3, figura4, figura5):
        f(base)
    resumo(base)
