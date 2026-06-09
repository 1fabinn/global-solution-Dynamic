"""
test_algorithms.py
==================
Testes unitários com pytest para todas as estruturas e algoritmos do sistema.

Cobertura:
    - Grafo: inserção, adjacência, arestas
    - BST: inserção, in-order, busca por intervalo, altura, remoção
    - Força Bruta: caminho mínimo em grafo pequeno
    - Dijkstra: corretude em grafo pequeno, comparação com FB

Global Solution 2026 — FIAP | Dynamic Programming
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from src.data_structures import Grafo, BinarySearchTree, Node
from src.brute_force import forca_bruta_caminhos
from src.greedy import dijkstra


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture
def grafo_simples():
    """
    Grafo de 5 vértices (0–4) com pesos conhecidos.
    Caminho mínimo 0→4: 0→1→3→4, custo = 1+2+1 = 4
    """
    g = Grafo()
    for i in range(5):
        g.adicionar_vertice(i, f"M{i}", round(0.1 * i + 0.2, 2), 100.0, 10000)
    g.adicionar_aresta(0, 1, 1.0)
    g.adicionar_aresta(0, 2, 4.0)
    g.adicionar_aresta(1, 2, 2.0)
    g.adicionar_aresta(1, 3, 2.0)
    g.adicionar_aresta(2, 4, 3.0)
    g.adicionar_aresta(3, 4, 1.0)
    return g


@pytest.fixture
def bst_populada():
    bst = BinarySearchTree()
    dados = [
        (1, "A", 0.50, 100, 5000),
        (2, "B", 0.30, 200, 6000),
        (3, "C", 0.70, 300, 7000),
        (4, "D", 0.20, 150, 4000),
        (5, "E", 0.60, 250, 8000),
        (6, "F", 0.80, 180, 9000),
        (7, "G", 0.40, 220, 5500),
    ]
    for id_m, nome, risco, custo, pop in dados:
        bst.inserir(id_m, nome, risco, custo, pop)
    return bst


# ─────────────────────────────────────────────────────────────────────────────
# Testes de Grafo
# ─────────────────────────────────────────────────────────────────────────────

class TestGrafo:

    def test_num_vertices(self, grafo_simples):
        assert grafo_simples.num_vertices() == 5

    def test_num_arestas(self, grafo_simples):
        assert grafo_simples.num_arestas() == 6

    def test_vizinhos(self, grafo_simples):
        viz = dict(grafo_simples.vizinhos(0))
        assert 1 in viz and 2 in viz
        assert viz[1] == pytest.approx(1.0)

    def test_atributos(self, grafo_simples):
        attrs = grafo_simples.atributos(0)
        assert attrs[0] == 0
        assert attrs[1] == "M0"

    def test_aresta_bidirecional(self, grafo_simples):
        viz_0 = [v for v, _ in grafo_simples.vizinhos(0)]
        viz_1 = [v for v, _ in grafo_simples.vizinhos(1)]
        assert 1 in viz_0
        assert 0 in viz_1

    def test_todas_arestas_sem_duplicata(self, grafo_simples):
        arestas = grafo_simples.todas_arestas()
        pares = [frozenset((u, v)) for u, v, _ in arestas]
        assert len(pares) == len(set(pares)), "Há arestas duplicadas"


# ─────────────────────────────────────────────────────────────────────────────
# Testes de BST
# ─────────────────────────────────────────────────────────────────────────────

class TestBST:

    def test_tamanho_apos_insercoes(self, bst_populada):
        assert len(bst_populada) == 7

    def test_in_order_crescente(self, bst_populada):
        nos = bst_populada.percurso_in_order()
        riscos = [no.indice_risco for no in nos]
        assert riscos == sorted(riscos), "In-order deve ser crescente"

    def test_busca_por_intervalo(self, bst_populada):
        resultado = bst_populada.buscar(0.50, 0.70)
        riscos = [no.indice_risco for no in resultado]
        assert all(0.50 <= r <= 0.70 for r in riscos)
        assert len(resultado) == 3  # 0.50, 0.60, 0.70

    def test_busca_sem_resultado(self, bst_populada):
        resultado = bst_populada.buscar(0.95, 1.0)
        assert resultado == []

    def test_altura_valida(self, bst_populada):
        h = bst_populada.altura()
        assert h >= math.floor(math.log2(7))   # ≥ altura mínima
        assert h <= 6                            # ≤ altura máxima (degenerada)

    def test_remover_no_existente(self, bst_populada):
        ok = bst_populada.remover(4)   # id=4, risco=0.20
        assert ok
        assert len(bst_populada) == 6
        # In-order não deve mais conter risco=0.20
        riscos = [no.indice_risco for no in bst_populada.percurso_in_order()]
        assert 0.20 not in riscos

    def test_remover_no_inexistente(self, bst_populada):
        ok = bst_populada.remover(9999)
        assert not ok
        assert len(bst_populada) == 7

    def test_propriedade_bst_apos_insercoes(self, bst_populada):
        """Verifica propriedade BST: in-order deve ser estritamente ordenado."""
        nos = bst_populada.percurso_in_order()
        for i in range(len(nos) - 1):
            assert nos[i].indice_risco <= nos[i + 1].indice_risco


# ─────────────────────────────────────────────────────────────────────────────
# Testes de Força Bruta
# ─────────────────────────────────────────────────────────────────────────────

class TestForcaBruta:

    def test_caminho_otimo_conhecido(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, origem=0, destino=4)
        assert res.custo_otimo == pytest.approx(4.0, rel=1e-5)
        assert res.caminho_otimo[0] == 0
        assert res.caminho_otimo[-1] == 4

    def test_caminhos_avaliados_positivo(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, origem=0, destino=4)
        assert res.caminhos_avaliados >= 1

    def test_chamadas_recursivas_maior_que_caminhos(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, origem=0, destino=4)
        assert res.chamadas_recursivas >= res.caminhos_avaliados

    def test_origem_igual_destino(self, grafo_simples):
        res = forca_bruta_caminhos(grafo_simples, origem=0, destino=0)
        assert res.custo_otimo == pytest.approx(0.0)

    def test_destino_inalcancavel(self):
        g = Grafo()
        for i in range(3):
            g.adicionar_vertice(i, f"M{i}", 0.5, 100, 1000)
        g.adicionar_aresta(0, 1, 1.0)
        # vértice 2 isolado
        res = forca_bruta_caminhos(g, origem=0, destino=2)
        assert math.isinf(res.custo_otimo)


# ─────────────────────────────────────────────────────────────────────────────
# Testes de Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

class TestDijkstra:

    def test_caminho_otimo_igual_fb(self, grafo_simples):
        """Dijkstra deve encontrar o mesmo custo que a Força Bruta."""
        fb  = forca_bruta_caminhos(grafo_simples, 0, 4)
        dij = dijkstra(grafo_simples, 0)
        _, custo_dij = dij.caminho_ate(4)
        assert custo_dij == pytest.approx(fb.custo_otimo, rel=1e-5)

    def test_distancia_zero_para_origem(self, grafo_simples):
        res = dijkstra(grafo_simples, 0)
        assert res.dist[0] == pytest.approx(0.0)

    def test_todos_vertices_alcancados(self, grafo_simples):
        res = dijkstra(grafo_simples, 0)
        for v in grafo_simples.vertices():
            assert not math.isinf(res.dist[v]), f"Vértice {v} não alcançado"

    def test_reconstrucao_de_caminho(self, grafo_simples):
        res = dijkstra(grafo_simples, 0)
        cam, custo = res.caminho_ate(4)
        assert cam[0] == 0
        assert cam[-1] == 4
        assert custo == pytest.approx(4.0, rel=1e-5)

    def test_operacoes_elementares_positivas(self, grafo_simples):
        res = dijkstra(grafo_simples, 0)
        assert res.insercoes_heap >= 1
        assert res.relaxamentos >= 1

    def test_destino_inalcancavel(self):
        g = Grafo()
        for i in range(3):
            g.adicionar_vertice(i, f"M{i}", 0.5, 100, 1000)
        g.adicionar_aresta(0, 1, 2.0)
        res = dijkstra(g, 0)
        _, custo = res.caminho_ate(2)
        assert math.isinf(custo)


# ─────────────────────────────────────────────────────────────────────────────
# Teste de integração: BST → Dijkstra
# ─────────────────────────────────────────────────────────────────────────────

class TestIntegracao:

    def test_municipios_criticos_encontrados(self):
        from src.greedy import dijkstra_municipios_criticos
        from src.scenarios import criar_cenario_RS
        grafo, bst = criar_cenario_RS()
        _, rotas = dijkstra_municipios_criticos(
            grafo, bst, origem=4314902, limiar_risco=0.70
        )
        # Deve encontrar pelo menos um município crítico
        assert len(rotas) >= 1
        # Todos os retornados devem ter risco >= 0.70
        for id_m, nome, risco, caminho, custo in rotas:
            assert risco >= 0.70

    def test_bst_in_order_rs(self):
        from src.scenarios import criar_cenario_RS
        _, bst = criar_cenario_RS()
        nos = bst.percurso_in_order()
        riscos = [no.indice_risco for no in nos]
        assert riscos == sorted(riscos)
