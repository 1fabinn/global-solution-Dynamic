#  Sistema de Monitoramento de Riscos Ambientais
### Global Solution 2026 — FIAP | Dynamic Programming
### Disciplina: Estruturas de Dados e Algoritmos

---

##  Integrantes do Grupo

| RA     | Nome                         |
|--------|------------------------------|
| 561828 | **Fabio Apolinário da Cruz** |
| 562171 | **Leonardo Lopes Bellim**    |
| 566238 | **Márcio Alexandre**         |


---

##  Descrição

Sistema computacional para monitoramento e triagem de riscos ambientais em municípios brasileiros, desenvolvido como solução para a **Global Solution 2026** da FIAP. O projeto aplica estruturas de dados avançadas (grafo ponderado, BST, heap) e algoritmos (Força Bruta com backtracking, Dijkstra guloso) para apoiar decisões de defesa civil em dois cenários reais:

- **Cenário A** — Rede de resposta a enchentes no **Rio Grande do Sul** (2024)
- **Cenário B** — Triagem de risco de seca no **MATOPIBA** (MA/TO/PI/BA)

---

##  Estrutura do Repositório

```
global-solution-2026/
├── README.md                    ← Este arquivo
├── requirements.txt             ← Dependências Python
├── main.py                      ← Ponto de entrada principal
├── data/
│   ├── raw/                     ← Dados brutos (fontes indicadas no relatório)
│   └── processed/               ← Grafos e árvores serializados
├── src/
│   ├── data_structures.py       ← Grafo, BST (Node + BinarySearchTree), UnionFind
│   ├── brute_force.py           ← Enumeração exaustiva com backtracking
│   ├── greedy.py                ← Dijkstra (guloso) + integração BST
│   ├── scenarios.py             ← Instâncias RS e MATOPIBA
│   ├── performance_monitor.py   ← Tempo (perf_counter), memória (tracemalloc), contadores
│   └── visualizations.py        ← Geração das 5 figuras obrigatórias
├── notebooks/
│   └── analise_resultados.ipynb ← Análise interativa e escala de decisão
├── tests/
│   └── test_algorithms.py       ← 27 testes unitários (pytest)
├── output_figures/              ← Figuras geradas automaticamente
└── report/
    └── relatorio_final.pdf      ← Relatório técnico (≤ 12 páginas)
```

---

##  Como Executar

### Pré-requisitos

- Python 3.10 ou superior
- pip

### Instalação

```bash
git clone https://github.com/SEU_USUARIO/global-solution-2026.git
cd global-solution-2026
pip install -r requirements.txt
```

### Execução completa

```bash
python main.py
```

Isso executa na sequência:
1. Cenário A (RS) — BST + Dijkstra
2. Cenário B (MATOPIBA) — BST + Dijkstra
3. Validação Força Bruta vs. Dijkstra (N=7)
4. Experimento de explosão combinatória (N=3..10)
5. Benchmark de desempenho (N=5..100)
6. Geração das 5 figuras obrigatórias em `output_figures/`

### Testes unitários

```bash
pytest tests/ -v
```

### Notebook de análise

```bash
jupyter notebook notebooks/analise_resultados.ipynb
```

---

##  Módulos

### `src/data_structures.py`
- **`Grafo`**: grafo ponderado não-dirigido via dicionário de listas de adjacência. Escolha justificada: O(V+E) de espaço vs. O(V²) da matriz — adequado para grafos esparsos de municípios.
- **`BinarySearchTree`** + **`Node`**: BST implementada do zero (sem bibliotecas externas). Chave = índice de risco. Suporta inserção, in-order, busca por intervalo [r_min, r_max], cálculo de altura e remoção com sucessor in-order.
- **`UnionFind`**: estrutura de conjuntos disjuntos com compressão de caminho (extensibilidade para Kruskal).

### `src/brute_force.py`
Enumeração exaustiva com backtracking recursivo. Instrumentado com contadores de chamadas e caminhos avaliados. Complexidade O(n!) — inviável para N > 12 (demonstrado empiricamente).

### `src/greedy.py`
Algoritmo de Dijkstra com heap binário (`heapq`). Critério guloso: extrai sempre o vértice de menor custo acumulado. Corretude garantida para pesos não-negativos (prova por contradição no módulo). Integração com BST para filtrar municípios prioritários por risco.

### `src/performance_monitor.py`
Benchmark sistemático: `time.perf_counter()` para tempo, `tracemalloc` para memória. Executa ambos os algoritmos para N ∈ {5,6,7,8,9,10,11,12,20,50,100} e exibe tabela comparativa com gap de otimalidade.

### `src/scenarios.py`
Dois grafos calibrados com dados reais:
- **RS**: 19 municípios, 22 arestas, hub em Porto Alegre
- **MATOPIBA**: 18 municípios, 20 arestas, hub em Palmas (TO)

---

##  Resultados Principais

### Explosão Combinatória (Força Bruta)

| N | Caminhos avaliados | Tempo |
|---|---|---|
| 5 | 16 | < 1 ms |
| 8 | 1.957 | ~7 ms |
| 10 | 109.601 | ~400 ms |
| 12 | > 500.000 | > 2.600 ms |

**Dijkstra** resolve N=100 em **< 2 ms**.

### Gap de Otimalidade (Dijkstra vs. Força Bruta)

Para N ≤ 8: gap = **0%** (Dijkstra encontra o ótimo global).
Para N = 9–12: gap pode ser > 0% quando existem múltiplos caminhos com custos similares — resultado esperado e discutido no relatório.

---

##  Alinhamento com ODS da ONU

| ODS | Conexão com o projeto |
|-----|----------------------|
| ODS 2 — Fome Zero | Triagem de municípios agrícolas em risco de seca (MATOPIBA) |
| ODS 9 — Indústria e Infraestrutura | Otimização de rotas de atendimento emergencial |
| ODS 11 — Cidades Sustentáveis | Planejamento de resposta a enchentes no RS |
| ODS 13 — Ação Climática | Monitoramento de riscos ambientais via dados de satélite |

---

##  Fontes de Dados

- **Defesa Civil RS** — Relatório de Danos Abril/Maio 2024
- **IBGE** — Populações estimadas 2022, malha municipal
- **DNIT** — Malha rodoviária federal
- **INPE** — Monitoramento PRODES/DETER
- **NASA MODIS** — Produto MOD13Q1 (NDVI 250m)
- **INMET** — Estações automáticas MA/TO/PI/BA

---

##  Dependências

```
matplotlib>=3.7
networkx>=3.0
numpy>=1.24
seaborn>=0.12
pytest>=7.0
```
