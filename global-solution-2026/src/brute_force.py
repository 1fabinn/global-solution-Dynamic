"""
brute_force.py
==============
Enumeração exaustiva de todos os caminhos entre origem e destino em um grafo
ponderado.  Serve como baseline de validação (oráculo) para instâncias
pequenas (N ≤ 12).

Estratégia:
    Recursão com backtracking — percorre todos os caminhos simples (sem
    repetição de vértices) e registra o de menor custo acumulado.

Instrumentação:
    - Contador de chamadas recursivas
    - Contador de caminhos avaliados (chegaram ao destino)
    - Registro de todos os caminhos com seus custos

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
import math
from typing import Optional
from src.data_structures import Grafo


# ─────────────────────────────────────────────────────────────────────────────
# Resultado de uma execução de força bruta
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoFB:
    """Agrupa todos os dados produzidos pela busca exaustiva."""

    def __init__(self):
        self.caminho_otimo: list[int] = []
        self.custo_otimo: float = math.inf
        self.todos_caminhos: list[tuple[list[int], float]] = []   # (caminho, custo)
        self.chamadas_recursivas: int = 0
        self.caminhos_avaliados: int = 0

    def __repr__(self) -> str:
        return (f"ResultadoFB("
                f"custo_ótimo={self.custo_otimo:.2f}, "
                f"caminhos_avaliados={self.caminhos_avaliados}, "
                f"chamadas_recursivas={self.chamadas_recursivas})")


# ─────────────────────────────────────────────────────────────────────────────
# Algoritmo principal
# ─────────────────────────────────────────────────────────────────────────────

def forca_bruta_caminhos(grafo: Grafo,
                         origem: int,
                         destino: int,
                         limite_caminhos: int = 100_000
                         ) -> ResultadoFB:
    """
    Enumera todos os caminhos simples de `origem` a `destino` no grafo,
    identificando o de menor custo total.

    Parâmetros
    ----------
    grafo          : Grafo ponderado (lista de adjacência).
    origem         : Id do vértice inicial.
    destino        : Id do vértice final.
    limite_caminhos: Interrompe a busca se esse número de caminhos for
                     atingido (segurança para grafos maiores que N=12).

    Retorno
    -------
    ResultadoFB com caminho ótimo, custo, contadores e lista de caminhos.

    Complexidade
    ------------
    O(n!) no pior caso (grafo completo) — explosão combinatória demonstrada
    pelo gráfico gerado em visualizations.py.
    """
    resultado = ResultadoFB()

    def backtrack(atual: int,
                  visitados: set[int],
                  caminho_atual: list[int],
                  custo_atual: float) -> None:

        resultado.chamadas_recursivas += 1

        # Limite de segurança
        if resultado.caminhos_avaliados >= limite_caminhos:
            return

        if atual == destino:
            resultado.caminhos_avaliados += 1
            # Registra o caminho (cópia)
            resultado.todos_caminhos.append(
                (list(caminho_atual), custo_atual)
            )
            # Atualiza ótimo
            if custo_atual < resultado.custo_otimo:
                resultado.custo_otimo = custo_atual
                resultado.caminho_otimo = list(caminho_atual)
            return

        for vizinho, peso in grafo.vizinhos(atual):
            if vizinho not in visitados:
                visitados.add(vizinho)
                caminho_atual.append(vizinho)
                backtrack(vizinho, visitados, caminho_atual,
                          custo_atual + peso)
                # Backtrack
                caminho_atual.pop()
                visitados.remove(vizinho)

    # Inicia a busca
    visitados_iniciais: set[int] = {origem}
    backtrack(origem, visitados_iniciais, [origem], 0.0)

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# Experimento de crescimento combinatório
# ─────────────────────────────────────────────────────────────────────────────

def experimento_explosao_combinatoria(
        tamanhos: list[int] | None = None
) -> list[dict]:
    """
    Gera grafos completos de N vértices (N ∈ tamanhos) e mede o número de
    caminhos enumerados entre o vértice 0 e o N-1.

    Retorna lista de dicionários com chaves:
        n, num_caminhos, chamadas_recursivas, tempo_ms
    """
    import time

    if tamanhos is None:
        tamanhos = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    registros = []

    for n in tamanhos:
        # Grafo completo com pesos unitários
        g = Grafo()
        for i in range(n):
            g.adicionar_vertice(i, f"M{i}", round(i / n, 3), 100.0, 10000)
        for i in range(n):
            for j in range(i + 1, n):
                g.adicionar_aresta(i, j, 1.0)

        t0 = time.perf_counter()
        res = forca_bruta_caminhos(g, origem=0, destino=n - 1,
                                   limite_caminhos=500_000)
        t1 = time.perf_counter()

        registros.append({
            "n": n,
            "num_caminhos": res.caminhos_avaliados,
            "chamadas_recursivas": res.chamadas_recursivas,
            "tempo_ms": (t1 - t0) * 1000,
        })

        print(f"N={n:2d} | caminhos={res.caminhos_avaliados:8,d} | "
              f"chamadas={res.chamadas_recursivas:10,d} | "
              f"tempo={registros[-1]['tempo_ms']:8.2f} ms")

    return registros
