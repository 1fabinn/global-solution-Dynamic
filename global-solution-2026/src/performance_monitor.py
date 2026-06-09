"""
performance_monitor.py
======================
Módulo de monitoramento de desempenho para os algoritmos do sistema de
monitoramento de riscos ambientais.

Métricas coletadas por execução:
    - Tempo de execução (ms) via time.perf_counter()
    - Memória alocada (MB) via tracemalloc
    - Operações elementares (chamadas recursivas, inserções no heap,
      relaxamentos de aresta)

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
import time
import tracemalloc
import random
import math
from dataclasses import dataclass, field
from src.data_structures import Grafo, BinarySearchTree
from src.brute_force import forca_bruta_caminhos
from src.greedy import dijkstra


# ─────────────────────────────────────────────────────────────────────────────
# Estrutura de resultado
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class RegistroDesempenho:
    algoritmo: str
    n_vertices: int
    tempo_ms: float
    memoria_mb: float
    operacoes: int          # chamadas rec. (FB) ou inserções heap (Dijkstra)
    custo_solucao: float = math.inf
    extra: dict = field(default_factory=dict)

    def __str__(self) -> str:
        return (f"{self.algoritmo:15s} | N={self.n_vertices:4d} | "
                f"tempo={self.tempo_ms:9.3f} ms | "
                f"mem={self.memoria_mb:.4f} MB | "
                f"ops={self.operacoes:8,d} | "
                f"custo={self.custo_solucao:.2f}")


# ─────────────────────────────────────────────────────────────────────────────
# Gerador de grafos sintéticos para benchmark
# ─────────────────────────────────────────────────────────────────────────────

def gerar_grafo_sintetico(n: int,
                           densidade: float = 0.4,
                           seed: int = 42) -> Grafo:
    """
    Gera um grafo conexo sintético com n vértices.

    Estratégia:
        1. Cria uma cadeia linear (garante conectividade)
        2. Adiciona arestas aleatórias adicionais conforme `densidade`
    """
    random.seed(seed)
    g = Grafo()
    for i in range(n):
        risco = round(random.uniform(0.1, 1.0), 3)
        custo = round(random.uniform(50.0, 2000.0), 1)
        pop = random.randint(5_000, 1_500_000)
        g.adicionar_vertice(i, f"Municipio_{i}", risco, custo, pop)

    # Cadeia linear para garantir conectividade
    for i in range(n - 1):
        peso = round(random.uniform(0.5, 10.0), 2)
        g.adicionar_aresta(i, i + 1, peso)

    # Arestas extras
    max_extras = int(n * (n - 1) / 2 * densidade)
    adicionadas: set[frozenset] = set(
        frozenset((i, i + 1)) for i in range(n - 1)
    )
    tentativas = 0
    while len(adicionadas) < max_extras + (n - 1) and tentativas < 10 * n:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        chave = frozenset((u, v))
        if u != v and chave not in adicionadas:
            g.adicionar_aresta(u, v, round(random.uniform(0.5, 10.0), 2))
            adicionadas.add(chave)
        tentativas += 1

    return g


def gerar_bst_sintetica(grafo: Grafo) -> BinarySearchTree:
    """Popula uma BST com todos os vértices do grafo."""
    bst = BinarySearchTree()
    vertices = grafo.vertices()
    random.shuffle(vertices)          # ordem aleatória → árvore mais balanceada
    for v in vertices:
        attrs = grafo.atributos(v)
        # attrs = (id, nome, risco, custo, pop)
        bst.inserir(attrs[0], attrs[1], attrs[2], attrs[3], attrs[4])
    return bst


# ─────────────────────────────────────────────────────────────────────────────
# Funções de benchmarking
# ─────────────────────────────────────────────────────────────────────────────

def medir_forca_bruta(grafo: Grafo,
                       origem: int,
                       destino: int,
                       n: int) -> RegistroDesempenho:
    tracemalloc.start()
    t0 = time.perf_counter()
    res = forca_bruta_caminhos(grafo, origem, destino,
                                limite_caminhos=500_000)
    t1 = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return RegistroDesempenho(
        algoritmo="Força Bruta",
        n_vertices=n,
        tempo_ms=(t1 - t0) * 1000,
        memoria_mb=pico / 1024 / 1024,
        operacoes=res.chamadas_recursivas,
        custo_solucao=res.custo_otimo,
        extra={"caminhos_avaliados": res.caminhos_avaliados}
    )


def medir_dijkstra(grafo: Grafo,
                   origem: int,
                   destino: int,
                   n: int) -> RegistroDesempenho:
    tracemalloc.start()
    t0 = time.perf_counter()
    res = dijkstra(grafo, origem)
    t1 = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    _, custo = res.caminho_ate(destino)

    return RegistroDesempenho(
        algoritmo="Dijkstra",
        n_vertices=n,
        tempo_ms=(t1 - t0) * 1000,
        memoria_mb=pico / 1024 / 1024,
        operacoes=res.insercoes_heap,
        custo_solucao=custo,
        extra={"relaxamentos": res.relaxamentos}
    )


# ─────────────────────────────────────────────────────────────────────────────
# Experimento completo
# ─────────────────────────────────────────────────────────────────────────────

def rodar_experimento(tamanhos_fb: list[int] | None = None,
                      tamanhos_dijk: list[int] | None = None
                      ) -> tuple[list[RegistroDesempenho],
                                  list[RegistroDesempenho]]:
    """
    Executa os dois algoritmos para vários tamanhos de instância.

    Parâmetros
    ----------
    tamanhos_fb   : Tamanhos para Força Bruta (padrão: 5,6,7,8,9,10,11,12)
    tamanhos_dijk : Tamanhos para Dijkstra (padrão: 5,8,10,12,20,50,100)

    Retorno
    -------
    (registros_fb, registros_dijkstra)
    """
    if tamanhos_fb is None:
        tamanhos_fb = [5, 6, 7, 8, 9, 10, 11, 12]
    if tamanhos_dijk is None:
        tamanhos_dijk = [5, 8, 10, 12, 20, 50, 100]

    print("=" * 75)
    print("BENCHMARK — Força Bruta vs. Dijkstra")
    print("=" * 75)

    registros_fb: list[RegistroDesempenho] = []
    registros_dijk: list[RegistroDesempenho] = []

    print("\n── Força Bruta ──────────────────────────────────────────────────")
    for n in tamanhos_fb:
        g = gerar_grafo_sintetico(n, densidade=0.5)
        origem, destino = 0, n - 1
        rec = medir_forca_bruta(g, origem, destino, n)
        registros_fb.append(rec)
        print(rec)

    print("\n── Dijkstra ─────────────────────────────────────────────────────")
    for n in tamanhos_dijk:
        g = gerar_grafo_sintetico(n, densidade=0.4)
        origem, destino = 0, n - 1
        rec = medir_dijkstra(g, origem, destino, n)
        registros_dijk.append(rec)
        print(rec)

    # Gap de otimalidade para N comuns
    print("\n── Gap de Otimalidade (instâncias N ≤ 12) ───────────────────────")
    n_comuns = sorted(set(tamanhos_fb) & set(tamanhos_dijk))
    print(f"{'N':>4} | {'Custo FB':>10} | {'Custo Dijk':>10} | {'Gap %':>8}")
    print("-" * 42)
    fb_map = {r.n_vertices: r for r in registros_fb}
    dijk_map = {r.n_vertices: r for r in registros_dijk}
    for n in n_comuns:
        if n in fb_map and n in dijk_map:
            c_fb = fb_map[n].custo_solucao
            c_dijk = dijk_map[n].custo_solucao
            if not math.isinf(c_fb) and c_fb > 0:
                gap = abs(c_dijk - c_fb) / c_fb * 100
            else:
                gap = 0.0
            print(f"{n:>4} | {c_fb:>10.3f} | {c_dijk:>10.3f} | {gap:>7.2f}%")

    return registros_fb, registros_dijk


if __name__ == "__main__":
    rodar_experimento()
