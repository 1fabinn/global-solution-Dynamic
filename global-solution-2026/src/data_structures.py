"""
data_structures.py
==================
Implementação das estruturas de dados fundamentais do sistema de
monitoramento de riscos ambientais.

Estruturas implementadas:
  - Grafo ponderado (lista de adjacência via dicionário)
  - Árvore Binária de Busca (BST) por índice de risco
  - Funções auxiliares para heap (heapq nativo)

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
import heapq
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# 1. GRAFO PONDERADO — lista de adjacência
# ─────────────────────────────────────────────────────────────────────────────

class Grafo:
    """
    Grafo ponderado não-dirigido representado como dicionário de listas de
    adjacência.

    Escolha de representação:
        Lista de adjacência  →  O(V + E) de espaço.
        Adequada para grafos esparsos (municípios brasileiros têm poucos
        vizinhos diretos), enquanto a matriz de adjacência exigiria O(V²).
        Operações de iteração sobre vizinhos são O(grau(v)), ideais para
        Dijkstra e BFS/DFS.

    Cada vértice é armazenado como tupla imutável:
        (id_municipio: int, nome: str, indice_risco: float,
         custo_atendimento: float, populacao: int)
    """

    def __init__(self):
        # dict: id_municipio → tupla de atributos
        self._vertices: dict[int, tuple] = {}
        # dict: id_municipio → lista de (id_vizinho, peso)
        self._adjacencia: dict[int, list[tuple[int, float]]] = {}

    # ── Construção ────────────────────────────────────────────────────────────

    def adicionar_vertice(self,
                          id_municipio: int,
                          nome: str,
                          indice_risco: float,
                          custo_atendimento: float,
                          populacao: int) -> None:
        """Insere um município (vértice) no grafo."""
        vertice: tuple = (id_municipio, nome, indice_risco,
                          custo_atendimento, populacao)
        self._vertices[id_municipio] = vertice
        if id_municipio not in self._adjacencia:
            self._adjacencia[id_municipio] = []

    def adicionar_aresta(self,
                         u: int,
                         v: int,
                         peso: float) -> None:
        """
        Insere aresta bidirecional (u, v) com peso (distância em km ou
        tempo em horas).  Aresta representada como tupla (vizinho, peso).
        """
        if u not in self._adjacencia:
            self._adjacencia[u] = []
        if v not in self._adjacencia:
            self._adjacencia[v] = []
        self._adjacencia[u].append((v, peso))
        self._adjacencia[v].append((u, peso))

    # ── Consultas ─────────────────────────────────────────────────────────────

    def vizinhos(self, u: int) -> list[tuple[int, float]]:
        """Retorna lista de (vizinho, peso) para o vértice u."""
        return self._adjacencia.get(u, [])

    def vertices(self) -> list[int]:
        """Retorna lista de todos os ids de vértices."""
        return list(self._vertices.keys())

    def atributos(self, id_municipio: int) -> tuple:
        """Retorna a tupla de atributos do município."""
        return self._vertices[id_municipio]

    def num_vertices(self) -> int:
        return len(self._vertices)

    def num_arestas(self) -> int:
        return sum(len(v) for v in self._adjacencia.values()) // 2

    def todas_arestas(self) -> list[tuple[int, int, float]]:
        """Retorna lista de arestas (u, v, peso) sem duplicatas."""
        vistas: set[frozenset] = set()
        arestas = []
        for u, vizinhos in self._adjacencia.items():
            for v, peso in vizinhos:
                chave = frozenset((u, v))
                if chave not in vistas:
                    vistas.add(chave)
                    arestas.append((u, v, peso))
        return arestas

    def __repr__(self) -> str:
        return (f"Grafo(vértices={self.num_vertices()}, "
                f"arestas={self.num_arestas()})")


# ─────────────────────────────────────────────────────────────────────────────
# 2. ÁRVORE BINÁRIA DE BUSCA (BST) — ordenada por índice de risco
# ─────────────────────────────────────────────────────────────────────────────

class Node:
    """Nó da BST. Chave = indice_risco (float); valor = tupla do município."""

    def __init__(self, id_municipio: int, nome: str,
                 indice_risco: float, custo_atendimento: float,
                 populacao: int):
        self.id_municipio = id_municipio
        self.nome = nome
        self.indice_risco = indice_risco          # chave BST
        self.custo_atendimento = custo_atendimento
        self.populacao = populacao
        self.esquerda: Optional[Node] = None
        self.direita: Optional[Node] = None

    def como_tupla(self) -> tuple:
        return (self.id_municipio, self.nome, self.indice_risco,
                self.custo_atendimento, self.populacao)

    def __repr__(self) -> str:
        return (f"Node({self.nome!r}, risco={self.indice_risco:.3f})")


class BinarySearchTree:
    """
    Árvore Binária de Busca para municípios ordenados por índice de risco.

    Propriedade BST:
        risco(esquerda) < risco(pai) ≤ risco(direita)

    Complexidades:
        Inserção / Busca pontual : O(h)  — h = altura da árvore
        Percurso in-order        : O(n)
        Busca por intervalo      : O(h + k), k = resultados retornados
        Altura (pior caso árvore degenerada): O(n)
        Altura (caso médio dados aleatórios): O(log n)
    """

    def __init__(self):
        self.raiz: Optional[Node] = None
        self._tamanho: int = 0

    # ── Inserção ──────────────────────────────────────────────────────────────

    def inserir(self, id_municipio: int, nome: str,
                indice_risco: float, custo_atendimento: float,
                populacao: int) -> None:
        """Insere novo nó mantendo propriedade BST."""
        novo = Node(id_municipio, nome, indice_risco,
                    custo_atendimento, populacao)
        if self.raiz is None:
            self.raiz = novo
        else:
            self._inserir_recursivo(self.raiz, novo)
        self._tamanho += 1

    def _inserir_recursivo(self, atual: Node, novo: Node) -> None:
        if novo.indice_risco < atual.indice_risco:
            if atual.esquerda is None:
                atual.esquerda = novo
            else:
                self._inserir_recursivo(atual.esquerda, novo)
        else:
            if atual.direita is None:
                atual.direita = novo
            else:
                self._inserir_recursivo(atual.direita, novo)

    # ── Percurso in-order ─────────────────────────────────────────────────────

    def percurso_in_order(self) -> list[Node]:
        """Retorna nós em ordem crescente de índice de risco — O(n)."""
        resultado: list[Node] = []
        self._in_order(self.raiz, resultado)
        return resultado

    def _in_order(self, no: Optional[Node], resultado: list) -> None:
        if no is None:
            return
        self._in_order(no.esquerda, resultado)
        resultado.append(no)
        self._in_order(no.direita, resultado)

    # ── Busca por intervalo ───────────────────────────────────────────────────

    def buscar(self, r_min: float, r_max: float) -> list[Node]:
        """
        Retorna todos os municípios com indice_risco ∈ [r_min, r_max].
        Poda subárvores fora do intervalo: O(h + k).
        """
        resultado: list[Node] = []
        self._buscar_intervalo(self.raiz, r_min, r_max, resultado)
        return resultado

    def _buscar_intervalo(self, no: Optional[Node],
                          r_min: float, r_max: float,
                          resultado: list) -> None:
        if no is None:
            return
        if no.indice_risco >= r_min:
            self._buscar_intervalo(no.esquerda, r_min, r_max, resultado)
        if r_min <= no.indice_risco <= r_max:
            resultado.append(no)
        if no.indice_risco <= r_max:
            self._buscar_intervalo(no.direita, r_min, r_max, resultado)

    # ── Altura ────────────────────────────────────────────────────────────────

    def altura(self) -> int:
        """Calcula a altura da árvore — O(n)."""
        return self._altura_rec(self.raiz)

    def _altura_rec(self, no: Optional[Node]) -> int:
        if no is None:
            return -1
        return 1 + max(self._altura_rec(no.esquerda),
                       self._altura_rec(no.direita))

    def balanceamento(self) -> str:
        """Avalia qualitativamente o balanceamento da árvore."""
        h = self.altura()
        n = self._tamanho
        if n == 0:
            return "vazia"
        ideal = __import__("math").log2(n + 1)
        razao = h / ideal if ideal > 0 else float("inf")
        if razao <= 1.5:
            return f"balanceada (h={h}, ideal≈{ideal:.1f})"
        elif razao <= 2.5:
            return f"moderadamente desbalanceada (h={h}, ideal≈{ideal:.1f})"
        else:
            return f"desbalanceada / degenerada (h={h}, ideal≈{ideal:.1f})"

    # ── Remoção ───────────────────────────────────────────────────────────────

    def remover(self, id_municipio: int) -> bool:
        """
        Remove o nó com id_municipio informado.
        Usa o sucessor in-order (menor da subárvore direita) para substituição.
        Retorna True se removido, False se não encontrado.
        """
        self.raiz, removido = self._remover_rec(self.raiz, id_municipio)
        if removido:
            self._tamanho -= 1
        return removido

    def _remover_rec(self, no: Optional[Node],
                     id_alvo: int) -> tuple[Optional[Node], bool]:
        if no is None:
            return None, False

        removido = False
        # Procura pelo id (busca por toda a árvore via in-order implícito)
        if id_alvo == no.id_municipio:
            removido = True
            if no.esquerda is None:
                return no.direita, removido
            if no.direita is None:
                return no.esquerda, removido
            # Dois filhos: substitui pelo sucessor in-order
            sucessor = self._minimo(no.direita)
            no.id_municipio = sucessor.id_municipio
            no.nome = sucessor.nome
            no.indice_risco = sucessor.indice_risco
            no.custo_atendimento = sucessor.custo_atendimento
            no.populacao = sucessor.populacao
            no.direita, _ = self._remover_rec(no.direita, sucessor.id_municipio)
        else:
            no.esquerda, rem_e = self._remover_rec(no.esquerda, id_alvo)
            no.direita, rem_d = self._remover_rec(no.direita, id_alvo)
            removido = rem_e or rem_d
        return no, removido

    def _minimo(self, no: Node) -> Node:
        while no.esquerda is not None:
            no = no.esquerda
        return no

    def __len__(self) -> int:
        return self._tamanho

    def __repr__(self) -> str:
        return (f"BST(n={self._tamanho}, "
                f"altura={self.altura()}, "
                f"{self.balanceamento()})")


# ─────────────────────────────────────────────────────────────────────────────
# 3. UNION-FIND (para Kruskal, caso necessário em extensão futura)
# ─────────────────────────────────────────────────────────────────────────────

class UnionFind:
    """
    Estrutura de conjuntos disjuntos com compressão de caminho e união por
    posto.  Usada internamente como apoio se o grupo estender para Kruskal.
    Complexidade amortizada: O(α(n)) por operação.
    """

    def __init__(self, elementos: list[int]):
        self._pai: dict[int, int] = {e: e for e in elementos}
        self._posto: dict[int, int] = {e: 0 for e in elementos}

    def encontrar(self, x: int) -> int:
        if self._pai[x] != x:
            self._pai[x] = self.encontrar(self._pai[x])  # compressão
        return self._pai[x]

    def unir(self, x: int, y: int) -> bool:
        """Une os conjuntos de x e y. Retorna False se já estavam unidos."""
        rx, ry = self.encontrar(x), self.encontrar(y)
        if rx == ry:
            return False
        if self._posto[rx] < self._posto[ry]:
            rx, ry = ry, rx
        self._pai[ry] = rx
        if self._posto[rx] == self._posto[ry]:
            self._posto[rx] += 1
        return True
