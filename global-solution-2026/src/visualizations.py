"""
visualizations.py
=================
Geração de todas as figuras obrigatórias do trabalho:

    Fig 1 — Grafo do Cenário A (RS) com Dijkstra destacado
    Fig 2 — Grafo do Cenário B (MATOPIBA) com Dijkstra destacado
    Fig 3 — Representação visual da BST (10–15 nós)
    Fig 4 — Gráfico comparativo de desempenho: tempo × N
    Fig 5 — Gráfico de gap de otimalidade FB vs. Dijkstra

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
import math
import os
import random
import time
import tracemalloc

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

from src.data_structures import Grafo, BinarySearchTree
from src.scenarios import criar_cenario_RS, criar_cenario_MATOPIBA
from src.greedy import dijkstra
from src.brute_force import forca_bruta_caminhos
from src.performance_monitor import (
    gerar_grafo_sintetico,
    medir_forca_bruta,
    medir_dijkstra,
)

OUTPUT_DIR = "output_figures"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Paleta de cores consistente
COR_RISCO_ALTO  = "#d62728"
COR_RISCO_MEDIO = "#ff7f0e"
COR_RISCO_BAIXO = "#2ca02c"
COR_CAMINHO     = "#1f77b4"
COR_HUB         = "#9467bd"
COR_ARESTA      = "#cccccc"
FONTE_TITULO    = {"fontsize": 13, "fontweight": "bold"}
FONTE_LEGENDA   = {"fontsize": 9}


# ─────────────────────────────────────────────────────────────────────────────
# Auxiliares
# ─────────────────────────────────────────────────────────────────────────────

def _cor_risco(risco: float) -> str:
    if risco >= 0.75:
        return COR_RISCO_ALTO
    elif risco >= 0.50:
        return COR_RISCO_MEDIO
    return COR_RISCO_BAIXO


def _grafo_para_nx(grafo: Grafo) -> nx.Graph:
    G = nx.Graph()
    for v in grafo.vertices():
        attrs = grafo.atributos(v)
        G.add_node(v, nome=attrs[1], risco=attrs[2],
                   custo=attrs[3], pop=attrs[4])
    for u, v, peso in grafo.todas_arestas():
        G.add_edge(u, v, weight=peso)
    return G


def _caminhos_dijkstra(grafo: Grafo, origem: int,
                        destinos: list[int]) -> list[list[int]]:
    res = dijkstra(grafo, origem)
    caminhos = []
    for d in destinos:
        cam, _ = res.caminho_ate(d)
        caminhos.append(cam)
    return caminhos


def _arestas_caminho(caminho: list[int]) -> set[frozenset]:
    s = set()
    for i in range(len(caminho) - 1):
        s.add(frozenset((caminho[i], caminho[i + 1])))
    return s


# ─────────────────────────────────────────────────────────────────────────────
# FIG 1 e 2 — Grafo de municípios com Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

def _plotar_grafo_cenario(grafo: Grafo, bst: BinarySearchTree,
                           origem: int, titulo: str,
                           nome_arquivo: str,
                           limiar_risco: float = 0.70) -> None:
    G = _grafo_para_nx(grafo)

    # Dijkstra para municípios de alto risco
    nos_criticos = bst.buscar(limiar_risco, 1.0)
    ids_criticos = [n.id_municipio for n in nos_criticos
                    if n.id_municipio != origem]

    res = dijkstra(grafo, origem)
    arestas_destacadas: set[frozenset] = set()
    for d in ids_criticos:
        cam, _ = res.caminho_ate(d)
        arestas_destacadas |= _arestas_caminho(cam)

    # Layout
    pos = nx.spring_layout(G, seed=7, k=2.5)

    # Cores dos nós
    node_colors = []
    node_sizes = []
    for v in G.nodes():
        attrs = grafo.atributos(v)
        risco = attrs[2]
        if v == origem:
            node_colors.append(COR_HUB)
            node_sizes.append(900)
        else:
            node_colors.append(_cor_risco(risco))
            node_sizes.append(400 + int(risco * 400))

    # Cores das arestas
    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if frozenset((u, v)) in arestas_destacadas:
            edge_colors.append(COR_CAMINHO)
            edge_widths.append(2.5)
        else:
            edge_colors.append(COR_ARESTA)
            edge_widths.append(0.8)

    fig, ax = plt.subplots(figsize=(13, 8))
    nx.draw_networkx_nodes(G, pos, node_color=node_colors,
                           node_size=node_sizes, ax=ax, alpha=0.92)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors,
                           width=edge_widths, ax=ax, alpha=0.85)

    # Rótulos: nome + risco
    labels = {}
    for v in G.nodes():
        attrs = grafo.atributos(v)
        labels[v] = f"{attrs[1]}\nr={attrs[2]:.2f}"
    nx.draw_networkx_labels(G, pos, labels=labels,
                            font_size=6.5, ax=ax)

    # Pesos nas arestas
    edge_labels = {(u, v): f"{d['weight']:.0f}km"
                   for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels,
                                 font_size=5.5, ax=ax)

    # Legenda
    patches = [
        mpatches.Patch(color=COR_HUB,         label="Hub (origem Dijkstra)"),
        mpatches.Patch(color=COR_RISCO_ALTO,   label="Risco alto (≥ 0.75)"),
        mpatches.Patch(color=COR_RISCO_MEDIO,  label="Risco médio (0.50–0.74)"),
        mpatches.Patch(color=COR_RISCO_BAIXO,  label="Risco baixo (< 0.50)"),
        mpatches.Patch(color=COR_CAMINHO,      label=f"Caminho Dijkstra (risco ≥ {limiar_risco})"),
    ]
    ax.legend(handles=patches, loc="lower left", **FONTE_LEGENDA)
    ax.set_title(titulo, **FONTE_TITULO)
    ax.axis("off")
    plt.tight_layout()
    caminho = f"{OUTPUT_DIR}/{nome_arquivo}"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Fig] Salva: {caminho}")


def figura_grafo_RS() -> None:
    grafo, bst = criar_cenario_RS()
    _plotar_grafo_cenario(
        grafo, bst,
        origem=4314902,
        titulo=("Fig. 1 — Rede de Municípios do RS afetados pelas Enchentes 2024\n"
                "Dijkstra a partir de Porto Alegre · Arestas azuis = rotas mínimas "
                "para municípios críticos (risco ≥ 0.70)"),
        nome_arquivo="fig1_grafo_RS.png",
        limiar_risco=0.70,
    )


def figura_grafo_MATOPIBA() -> None:
    grafo, bst = criar_cenario_MATOPIBA()
    _plotar_grafo_cenario(
        grafo, bst,
        origem=1721000,
        titulo=("Fig. 2 — Rede de Municípios do MATOPIBA — Risco de Seca\n"
                "Dijkstra a partir de Palmas (TO) · Arestas azuis = rotas mínimas "
                "para municípios críticos (risco ≥ 0.70)"),
        nome_arquivo="fig2_grafo_MATOPIBA.png",
        limiar_risco=0.70,
    )


# ─────────────────────────────────────────────────────────────────────────────
# FIG 3 — BST Visual
# ─────────────────────────────────────────────────────────────────────────────

def figura_bst(n_nos: int = 12) -> None:
    """Desenha a BST de uma amostra de municípios do RS."""
    grafo_rs, bst_rs = criar_cenario_RS()

    # Pega os primeiros n_nos municípios do percurso in-order (BST já populada)
    nos = bst_rs.percurso_in_order()[:n_nos]

    # Reconstrói BST menor para visualização nítida
    bst_pequena = BinarySearchTree()
    random.seed(10)
    amostras = random.sample(nos, min(n_nos, len(nos)))
    for no in amostras:
        bst_pequena.inserir(no.id_municipio, no.nome,
                            no.indice_risco, no.custo_atendimento,
                            no.populacao)

    # Coleta posições para o desenho (BFS na árvore)
    from collections import deque
    fig, ax = plt.subplots(figsize=(14, 7))

    if bst_pequena.raiz is None:
        ax.text(0.5, 0.5, "BST vazia", ha="center")
        plt.savefig(f"{OUTPUT_DIR}/fig3_bst.png", dpi=120)
        plt.close()
        return

    # Atribui coordenadas: x por posição in-order, y por profundidade
    pos_map: dict[int, tuple[float, float]] = {}
    contador = [0]

    def atribuir_pos(no, profundidade):
        if no is None:
            return
        atribuir_pos(no.esquerda, profundidade + 1)
        pos_map[id(no)] = (contador[0], -profundidade)
        contador[0] += 1
        atribuir_pos(no.direita, profundidade + 1)

    atribuir_pos(bst_pequena.raiz, 0)

    # Desenha arestas
    fila = deque([bst_pequena.raiz])
    while fila:
        no = fila.popleft()
        px, py = pos_map[id(no)]
        for filho in [no.esquerda, no.direita]:
            if filho:
                fx, fy = pos_map[id(filho)]
                ax.plot([px, fx], [py, fy], "k-", lw=1.2, zorder=1)
                fila.append(filho)

    # Desenha nós
    fila = deque([bst_pequena.raiz])
    while fila:
        no = fila.popleft()
        px, py = pos_map[id(no)]
        cor = _cor_risco(no.indice_risco)
        circ = plt.Circle((px, py), 0.38, color=cor, zorder=2)
        ax.add_patch(circ)
        ax.text(px, py + 0.05, f"{no.indice_risco:.2f}",
                ha="center", va="center", fontsize=7.5,
                fontweight="bold", color="white", zorder=3)
        nome_curto = no.nome.split()[0][:8]
        ax.text(px, py - 0.55, nome_curto,
                ha="center", va="top", fontsize=6, color="#333333")
        for filho in [no.esquerda, no.direita]:
            if filho:
                fila.append(filho)

    ax.set_xlim(-1, contador[0])
    ax.set_ylim(-bst_pequena.altura() - 1, 1)
    ax.set_aspect("equal")
    ax.axis("off")

    patches = [
        mpatches.Patch(color=COR_RISCO_ALTO,  label="Risco alto (≥ 0.75)"),
        mpatches.Patch(color=COR_RISCO_MEDIO, label="Risco médio (0.50–0.74)"),
        mpatches.Patch(color=COR_RISCO_BAIXO, label="Risco baixo (< 0.50)"),
    ]
    ax.legend(handles=patches, loc="lower right", **FONTE_LEGENDA)
    ax.set_title(
        f"Fig. 3 — Árvore Binária de Busca (BST) — {len(amostras)} municípios do RS\n"
        "Chave = índice de risco · In-order produz municípios em ordem crescente de risco",
        **FONTE_TITULO,
    )
    plt.tight_layout()
    caminho = f"{OUTPUT_DIR}/fig3_bst.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Fig] Salva: {caminho}")


# ─────────────────────────────────────────────────────────────────────────────
# FIG 4 — Gráfico de desempenho tempo × N
# ─────────────────────────────────────────────────────────────────────────────

def figura_desempenho() -> tuple[list, list]:
    tamanhos_fb   = [5, 6, 7, 8, 9, 10, 11, 12]
    tamanhos_dijk = [5, 6, 7, 8, 9, 10, 11, 12, 20, 50, 100]

    print("[Benchmark] Iniciando medições de desempenho...")
    regs_fb   = []
    regs_dijk = []

    for n in tamanhos_fb:
        g = gerar_grafo_sintetico(n, densidade=0.5, seed=42)
        regs_fb.append(medir_forca_bruta(g, 0, n - 1, n))

    for n in tamanhos_dijk:
        g = gerar_grafo_sintetico(n, densidade=0.4, seed=42)
        regs_dijk.append(medir_dijkstra(g, 0, n - 1, n))

    ns_fb   = [r.n_vertices for r in regs_fb]
    ts_fb   = [r.tempo_ms   for r in regs_fb]
    ns_dijk = [r.n_vertices for r in regs_dijk]
    ts_dijk = [r.tempo_ms   for r in regs_dijk]

    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(ns_fb,   ts_fb,   "o-", color=COR_RISCO_ALTO,
            lw=2, ms=7, label="Força Bruta (backtracking)")
    ax.plot(ns_dijk, ts_dijk, "s--", color=COR_CAMINHO,
            lw=2, ms=7, label="Dijkstra (greedy + heap)")

    # Anotação do cruzamento
    crossover = None
    for r in regs_fb:
        n = r.n_vertices
        dijk_n = next((d.tempo_ms for d in regs_dijk
                       if d.n_vertices == n), None)
        if dijk_n and r.tempo_ms > dijk_n and crossover is None:
            crossover = n
    if crossover:
        ax.axvline(crossover, color="gray", linestyle=":", lw=1.5,
                   label=f"Cruzamento ≈ N={crossover}")
        ax.text(crossover + 0.2, max(ts_fb) * 0.6,
                f"FB inviável\na partir de\nN≈{crossover}",
                fontsize=8, color="gray")

    ax.set_xlabel("Número de vértices (N)", fontsize=11)
    ax.set_ylabel("Tempo de execução (ms)", fontsize=11)
    ax.set_title(
        "Fig. 4 — Comparativo de Desempenho: Força Bruta vs. Dijkstra\n"
        "Grafos sintéticos com densidade 0.4–0.5 · Instâncias N=5 a N=100",
        **FONTE_TITULO,
    )
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.35)
    ax.set_yscale("log")
    plt.tight_layout()
    caminho = f"{OUTPUT_DIR}/fig4_desempenho.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Fig] Salva: {caminho}")
    return regs_fb, regs_dijk


# ─────────────────────────────────────────────────────────────────────────────
# FIG 5 — Gap de otimalidade
# ─────────────────────────────────────────────────────────────────────────────

def figura_gap(regs_fb, regs_dijk) -> None:
    fb_map   = {r.n_vertices: r for r in regs_fb}
    dijk_map = {r.n_vertices: r for r in regs_dijk}
    n_comuns = sorted(set(fb_map) & set(dijk_map))

    gaps = []
    ns   = []
    for n in n_comuns:
        c_fb   = fb_map[n].custo_solucao
        c_dijk = dijk_map[n].custo_solucao
        if not math.isinf(c_fb) and c_fb > 0:
            gap = abs(c_dijk - c_fb) / c_fb * 100
        else:
            gap = 0.0
        gaps.append(gap)
        ns.append(n)

    fig, ax = plt.subplots(figsize=(9, 5))
    bars = ax.bar(ns, gaps, color=COR_RISCO_MEDIO, edgecolor="white",
                  width=0.6, alpha=0.85)
    ax.axhline(0, color="gray", lw=1)
    ax.axhline(5, color=COR_RISCO_ALTO, lw=1.2, linestyle="--",
               label="Limiar 5% de gap")

    for bar, gap in zip(bars, gaps):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.1,
                f"{gap:.1f}%", ha="center", va="bottom", fontsize=8)

    ax.set_xlabel("Número de vértices (N)", fontsize=11)
    ax.set_ylabel("Gap de otimalidade (%)", fontsize=11)
    ax.set_title(
        "Fig. 5 — Gap de Otimalidade: Dijkstra vs. Força Bruta (ótimo global)\n"
        "Gap = |custo_Dijkstra − custo_FB| / custo_FB × 100%",
        **FONTE_TITULO,
    )
    ax.legend(fontsize=9)
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    caminho = f"{OUTPUT_DIR}/fig5_gap.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Fig] Salva: {caminho}")


# ─────────────────────────────────────────────────────────────────────────────
# Ponto de entrada
# ─────────────────────────────────────────────────────────────────────────────

def figura_explosao_combinatoria() -> None:
    """
    Fig 6 — Gráfico de crescimento do número de caminhos em função de N.
    Evidencia a explosão combinatória da Força Bruta (item obrigatório 3.1).
    """
    from src.brute_force import forca_bruta_caminhos

    tamanhos = [3, 4, 5, 6, 7, 8, 9, 10]
    caminhos = []
    chamadas = []

    for n in tamanhos:
        g = Grafo()
        for i in range(n):
            g.adicionar_vertice(i, f"M{i}", round(i/n, 3), 100.0, 10000)
        for i in range(n):
            for j in range(i+1, n):
                g.adicionar_aresta(i, j, 1.0)
        res = forca_bruta_caminhos(g, 0, n-1, limite_caminhos=500_000)
        caminhos.append(res.caminhos_avaliados)
        chamadas.append(res.chamadas_recursivas)

    # Curva fatorial teórica para referência
    import math
    fatorial = [math.factorial(n-1) for n in tamanhos]

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Esquerda: caminhos avaliados vs N
    axes[0].bar(tamanhos, caminhos, color=COR_RISCO_ALTO,
                alpha=0.8, edgecolor="white", label="Caminhos avaliados (FB)")
    axes[0].plot(tamanhos, caminhos, "o-", color=COR_RISCO_ALTO, lw=2)
    for x, y in zip(tamanhos, caminhos):
        axes[0].text(x, y + max(caminhos)*0.02, f"{y:,}",
                     ha="center", fontsize=7.5, color="#333")
    axes[0].set_xlabel("Número de vértices (N)", fontsize=11)
    axes[0].set_ylabel("Número de caminhos avaliados", fontsize=11)
    axes[0].set_title("Crescimento dos Caminhos Avaliados", fontweight="bold")
    axes[0].grid(True, axis="y", alpha=0.3)

    # Direita: escala log, comparando com (N-1)!
    axes[1].semilogy(tamanhos, caminhos, "o-", color=COR_RISCO_ALTO,
                     lw=2, ms=8, label="Caminhos avaliados (FB)")
    axes[1].semilogy(tamanhos, fatorial, "s--", color=COR_RISCO_MEDIO,
                     lw=1.5, ms=6, label="(N-1)! teórico")
    axes[1].semilogy(tamanhos, chamadas, "^:", color=COR_CAMINHO,
                     lw=1.5, ms=6, label="Chamadas recursivas")
    axes[1].set_xlabel("Número de vértices (N)", fontsize=11)
    axes[1].set_ylabel("Quantidade (escala log)", fontsize=11)
    axes[1].set_title("Escala Logarítmica — Explosão Fatorial", fontweight="bold")
    axes[1].legend(fontsize=9)
    axes[1].grid(True, alpha=0.3)

    plt.suptitle(
        "Fig. 6 — Explosão Combinatória da Força Bruta\n"
        "Grafos completos com N vértices · Origem=0, Destino=N-1",
        **FONTE_TITULO
    )
    plt.tight_layout()
    caminho = f"{OUTPUT_DIR}/fig6_explosao_combinatoria.png"
    plt.savefig(caminho, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"[Fig] Salva: {caminho}")


def gerar_todas_figuras() -> None:
    print("\n=== Gerando todas as figuras obrigatórias ===\n")
    figura_grafo_RS()
    figura_grafo_MATOPIBA()
    figura_bst()
    regs_fb, regs_dijk = figura_desempenho()
    figura_gap(regs_fb, regs_dijk)
    figura_explosao_combinatoria()
    print(f"\n✓ Todas as figuras salvas em ./{OUTPUT_DIR}/")


if __name__ == "__main__":
    gerar_todas_figuras()
