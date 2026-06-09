"""
scenarios.py
============
Instanciação dos dois cenários brasileiros escolhidos:

    Cenário A — Rede de resposta a enchentes no Rio Grande do Sul (2024)
    Cenário B — Triagem de risco de seca no MATOPIBA

Os dados são **sintéticos mas calibrados** com base em:
    - Malha viária DNIT / distâncias reais entre municípios (km)
    - Índices de risco derivados de dados públicos (Defesa Civil RS / INMET)
    - Populações reais IBGE 2022

Justificativa do uso de dados sintéticos:
    A ingestão automatizada das APIs do DNIT, IBGE e INMET requer chaves de
    acesso e processamento de shapefile (GeoPandas), o que ultrapassa o escopo
    didático.  Os valores numéricos foram calibrados para refletir a ordem de
    grandeza real, garantindo que os algoritmos operem em condições
    representativas.  Fontes reais são indicadas para extensão futura.

Global Solution 2026 — FIAP | Dynamic Programming
"""

from __future__ import annotations
from src.data_structures import Grafo, BinarySearchTree


# ─────────────────────────────────────────────────────────────────────────────
# CENÁRIO A — Enchentes RS 2024
# ─────────────────────────────────────────────────────────────────────────────

def criar_cenario_RS() -> tuple[Grafo, BinarySearchTree]:
    """
    Subgrafo de 20 municípios do Rio Grande do Sul afetados pelas enchentes
    de 2024.

    Vértice: (id_IBGE, nome, indice_risco, custo_atendimento_R$k, populacao)
    Aresta  : (u, v, distancia_km)

    Hub de origem para Dijkstra: Porto Alegre (4314902)

    Índice de risco [0,1]: ponderação de
        - % da área inundada (dados Defesa Civil RS)
        - Vulnerabilidade socioeconômica (IBGE)
        - Acesso viário comprometido

    Fonte de referência:
        Defesa Civil RS — Relatório de Danos Abril/Maio 2024
        IBGE Cidades — populações estimadas 2022
        DNIT — malha rodoviária federal RS
    """
    municipios_rs = [
        # (id_ibge, nome, risco, custo_R$k, populacao)
        (4314902, "Porto Alegre",      0.45, 1850.0, 1332570),
        (4300406, "Alegrete",          0.61,  210.0,   77653),
        (4301602, "Arroio do Meio",    0.88,   85.0,   18701),
        (4302105, "Bento Gonçalves",   0.52,  320.0,  121976),
        (4304630, "Canoas",            0.79,  780.0,  344572),
        (4305108, "Caxias do Sul",     0.41,  620.0,  503048),
        (4307005, "Eldorado do Sul",   0.93,  120.0,   40882),
        (4307609, "Encantado",         0.87,   75.0,   20987),
        (4309209, "Gramado",           0.31,  180.0,   36448),
        (4309308, "Gravataí",          0.66,  520.0,  272723),
        (4310801, "Lajeado",           0.91,  175.0,   82198),
        (4311700, "Montenegro",        0.74,  160.0,   61090),
        (4312401, "Novo Hamburgo",     0.58,  580.0,  238940),
        (4313409, "Passo Fundo",       0.47,  380.0,  211040),
        (4314100, "Pelotas",           0.55,  440.0,  342053),
        (4314407, "Porto Alegre (hub)", 0.45, 0.0,   1332570),  # hub
        (4314803, "Rio Grande",        0.49,  300.0,  207434),
        (4315602, "Santa Cruz do Sul", 0.63,  250.0,  130921),
        (4316808, "São Leopoldo",      0.71,  430.0,  229398),
        (4317202, "Uruguaiana",        0.58,  190.0,  125507),
    ]
    # Remove duplicata do hub
    municipios_rs = [m for m in municipios_rs if m[0] != 4314407]

    arestas_rs = [
        # (u, v, distancia_km)
        (4314902, 4304630, 18),
        (4314902, 4316808, 32),
        (4314902, 4312401, 43),
        (4314902, 4307005, 44),
        (4314902, 4309308, 29),
        (4316808, 4311700, 28),
        (4316808, 4312401, 12),
        (4312401, 4302105, 52),
        (4311700, 4310801, 35),
        (4310801, 4307609, 15),
        (4310801, 4301602, 8),
        (4307609, 4301602, 20),
        (4302105, 4305108, 122),
        (4305108, 4309209, 36),
        (4309209, 4315602, 120),
        (4315602, 4313409, 157),
        (4314902, 4314100, 272),
        (4314100, 4314803, 55),
        (4314803, 4317202, 600),
        (4317202, 4300406, 230),
        (4304630, 4307005, 27),
        (4313409, 4300406, 350),
    ]

    grafo = Grafo()
    bst = BinarySearchTree()

    for m in municipios_rs:
        id_m, nome, risco, custo, pop = m
        grafo.adicionar_vertice(id_m, nome, risco, custo, pop)
        bst.inserir(id_m, nome, risco, custo, pop)

    for u, v, dist in arestas_rs:
        grafo.adicionar_aresta(u, v, float(dist))

    return grafo, bst


# ─────────────────────────────────────────────────────────────────────────────
# CENÁRIO B — Seca no MATOPIBA
# ─────────────────────────────────────────────────────────────────────────────

def criar_cenario_MATOPIBA() -> tuple[Grafo, BinarySearchTree]:
    """
    Rede de 18 municípios do MATOPIBA (MA, TO, PI, BA) com risco de seca.

    Índice de risco: ponderação de
        - NDVI anomalia (MODIS/NASA) — quanto abaixo da média histórica
        - Precipitação acumulada (% desvio, INMET)
        - Dependência agrícola da economia local

    Hub de origem: Palmas (TO) — principal centro de logística da região.

    Fonte de referência:
        INPE — Monitoramento do bioma Cerrado
        NASA MODIS — produto MOD13Q1 (NDVI 250m)
        INMET — Estações automáticas MA/TO/PI/BA
        IBGE — Censo Agropecuário 2017
    """
    municipios_matopiba = [
        # (id_ibge, nome, risco, custo_R$k, populacao)
        (1721000, "Palmas",             0.38, 520.0,  313494),  # hub
        (2111300, "Balsas",             0.72, 180.0,   87039),
        (2101400, "Alto Parnaíba",      0.89,  65.0,   13842),
        (2105500, "Imperatriz",         0.51, 380.0,  258016),
        (2111532, "São Raimundo Mangabeira", 0.81, 48.0, 15200),
        (1703206, "Araguaína",          0.44, 310.0,  180470),
        (1707405, "Gurupi",             0.48, 175.0,   90799),
        (1716307, "Porto Nacional",     0.55, 130.0,   53249),
        (1707702, "Guaraí",             0.67,  95.0,   24753),
        (2207702, "Picos",              0.83, 140.0,   76629),
        (2208007, "Piripiri",           0.76,  90.0,   60803),
        (2210102, "Teresina",           0.41, 670.0,  868075),
        (2204202, "Floriano",           0.69, 115.0,   61286),
        (2910727, "Barreiras",          0.74, 220.0,  156975),
        (2918753, "Luís Eduardo Magalhães", 0.78, 195.0, 89141),
        (2933307, "Vitória da Conquista", 0.49, 290.0, 340002),
        (2900702, "Bom Jesus da Lapa",  0.82,  80.0,   63000),
        (1718402, "Taguatinga",         0.91,  55.0,   17643),
    ]

    arestas_matopiba = [
        # (u, v, distancia_km)
        (1721000, 1703206, 360),
        (1721000, 1716307, 58),
        (1721000, 1707405, 246),
        (1703206, 2105500, 610),
        (1703206, 1707702, 155),
        (1707702, 1707405, 91),
        (2105500, 2111300, 430),
        (2111300, 2101400, 280),
        (2111300, 2111532, 230),
        (2111300, 2207702, 490),
        (2207702, 2210102, 312),
        (2207702, 2204202, 200),
        (2210102, 2208007, 175),
        (2210102, 2204202, 230),
        (2204202, 2910727, 830),
        (2910727, 2918753, 68),
        (2918753, 2900702, 360),
        (2900702, 2933307, 265),
        (1716307, 1718402, 330),
        (1718402, 2101400, 480),
    ]

    grafo = Grafo()
    bst = BinarySearchTree()

    for m in municipios_matopiba:
        id_m, nome, risco, custo, pop = m
        grafo.adicionar_vertice(id_m, nome, risco, custo, pop)
        bst.inserir(id_m, nome, risco, custo, pop)

    for u, v, dist in arestas_matopiba:
        grafo.adicionar_aresta(u, v, float(dist))

    return grafo, bst
