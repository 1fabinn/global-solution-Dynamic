"""
greedy.py
=========
Algoritmo Guloso escolhido: **Dijkstra** — caminho mínimo de fonte única.

Justificativa da escolha:
    O problema central dos cenários A (enchentes RS) e B (MATOPIBA) é
    encontrar a rota de menor custo de atendimento a partir de um hub de
    recursos (ex.: Porto Alegre, Palmas) para todos os municípios afetados.
    Dijkstra é o algoritmo canônico para esse problema em grafos com pesos
    não-negativos, com complexidade O((V + E) log V) usando heap binário —
    viável para redes com centenas de municípios.

Critério guloso local:
    A cada passo, relaxa a aresta de menor custo acumulado.  A invariante
    mantida é: ao extrair um vértice do heap, seu custo já é definitivamente
    mínimo (prova por contradição: qualquer caminho alternativo passaria por
    um vértice ainda não processado, cujo custo acumulado é ≥ ao atual).

Integração com BST:
    Antes de executar Dijkstra, a BST é consultada para filtrar apenas os
    municípios com índice de risco acima de um limiar, restringindo o conjunto
    de destinos prioritários.

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
import heapq
import math
from src.data_structures import Grafo, BinarySearchTree


# ─────────────────────────────────────────────────────────────────────────────
# Resultado de Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

class ResultadoDijkstra:
    """Agrupa os produtos da execução de Dijkstra."""

    def __init__(self):
        # dist[v] = custo mínimo de origem até v
        self.dist: dict[int, float] = {}
        # pred[v] = predecessor de v no caminho mínimo
        self.pred: dict[int, Optional[int]] = {}
        # Número de inserções no heap (operações elementares)
        self.insercoes_heap: int = 0
        # Número de relaxamentos de aresta
        self.relaxamentos: int = 0
        # Vértices processados na ordem de extração do heap
        self.ordem_processamento: list[int] = []

    def caminho_ate(self, destino: int) -> tuple[list[int], float]:
        """
        Reconstrói o caminho mínimo da origem até `destino`.

        Retorna (lista_de_ids, custo_total).
        """
        if destino not in self.dist or math.isinf(self.dist[destino]):
            return [], math.inf

        caminho: list[int] = []
        atual = destino
        while atual is not None:
            caminho.append(atual)
            atual = self.pred.get(atual)
        caminho.reverse()
        return caminho, self.dist[destino]

    def __repr__(self) -> str:
        alcancaveis = sum(1 for d in self.dist.values()
                          if not math.isinf(d))
        return (f"ResultadoDijkstra("
                f"alcançáveis={alcancaveis}, "
                f"inserções_heap={self.insercoes_heap}, "
                f"relaxamentos={self.relaxamentos})")


# ─────────────────────────────────────────────────────────────────────────────
# Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

def dijkstra(grafo: Grafo,
             origem: int,
             destinos_prioritarios: set[int] | None = None
             ) -> ResultadoDijkstra:
    """
    Algoritmo de Dijkstra com heap binário (heapq).

    Parâmetros
    ----------
    grafo                  : Grafo ponderado (lista de adjacência).
    origem                 : Id do vértice fonte.
    destinos_prioritarios  : Se fornecido, interrompe ao processar todos
                             os destinos (otimização early-stop).

    Retorno
    -------
    ResultadoDijkstra com distâncias, predecessores e contadores.

    Complexidade
    ------------
    Tempo : O((V + E) log V) com heap binário.
    Espaço: O(V) para dist e pred; O(V) para o heap no pior caso.

    Razão de corretude (informal)
    -----------------------------
    Quando um vértice v é extraído do heap com custo d, qualquer caminho
    alternativo passaria por algum vértice u ainda no heap com dist[u] ≥ d
    (pesos não-negativos).  Logo, dist[v] = d é definitivo.
    """
    resultado = ResultadoDijkstra()

    # Inicialização
    for v in grafo.vertices():
        resultado.dist[v] = math.inf
        resultado.pred[v] = None

    resultado.dist[origem] = 0.0

    # Heap: (custo_acumulado, id_vertice)
    heap: list[tuple[float, int]] = [(0.0, origem)]
    resultado.insercoes_heap += 1

    # Conjunto de vértices já finalizados — O(1) de verificação
    finalizados: set[int] = set()

    pendentes = (set(destinos_prioritarios)
                 if destinos_prioritarios else None)

    while heap:
        custo_atual, u = heapq.heappop(heap)

        # Entrada desatualizada no heap (lazy deletion)
        if u in finalizados:
            continue

        finalizados.add(u)
        resultado.ordem_processamento.append(u)

        # Early-stop: todos os destinos prioritários foram alcançados
        if pendentes is not None:
            pendentes.discard(u)
            if not pendentes:
                break

        # Relaxamento das arestas
        for vizinho, peso in grafo.vizinhos(u):
            if vizinho in finalizados:
                continue
            resultado.relaxamentos += 1
            novo_custo = resultado.dist[u] + peso
            if novo_custo < resultado.dist[vizinho]:
                resultado.dist[vizinho] = novo_custo
                resultado.pred[vizinho] = u
                heapq.heappush(heap, (novo_custo, vizinho))
                resultado.insercoes_heap += 1

    return resultado


# ─────────────────────────────────────────────────────────────────────────────
# Integração BST → Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

def dijkstra_municipios_criticos(grafo: Grafo,
                                  bst: BinarySearchTree,
                                  origem: int,
                                  limiar_risco: float = 0.6
                                  ) -> tuple[ResultadoDijkstra, list]:
    """
    Consulta a BST para obter municípios de alto risco (risco ≥ limiar_risco),
    usa esses ids como destinos prioritários no Dijkstra e retorna os caminhos
    mínimos para cada um.

    Fluxo:
        1. BST.buscar(limiar_risco, 1.0)  →  nós de alto risco
        2. Dijkstra(origem, destinos=ids_alto_risco)
        3. Reconstrução de caminhos para cada destino

    Retorno
    -------
    (resultado_dijkstra, lista_de_rotas)
    lista_de_rotas: [(id_municipio, nome, risco, caminho, custo), ...]
    """
    # 1. Consulta BST
    nos_criticos = bst.buscar(limiar_risco, 1.0)
    ids_criticos = {no.id_municipio for no in nos_criticos}

    if not ids_criticos:
        print(f"Nenhum município com risco ≥ {limiar_risco:.2f} encontrado.")
        return ResultadoDijkstra(), []

    print(f"[Dijkstra] {len(ids_criticos)} municípios críticos "
          f"(risco ≥ {limiar_risco:.2f}) identificados via BST.")

    # 2. Dijkstra
    resultado = dijkstra(grafo, origem, destinos_prioritarios=ids_criticos)

    # 3. Reconstrução de rotas
    rotas = []
    for no in sorted(nos_criticos,
                     key=lambda x: -x.indice_risco):   # ordem dec. de risco
        caminho, custo = resultado.caminho_ate(no.id_municipio)
        rotas.append((no.id_municipio, no.nome,
                      no.indice_risco, caminho, custo))

    return resultado, rotas
