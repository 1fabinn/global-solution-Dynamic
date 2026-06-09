"""
main.py
=======
Ponto de entrada principal do sistema de monitoramento de riscos ambientais.

Executa:
    1. Cenário A — Enchentes RS: BST + Dijkstra
    2. Cenário B — MATOPIBA: BST + Dijkstra
    3. Experimento de desempenho: FB vs. Dijkstra (N=5..12 / N=5..100)
    4. Geração de todas as figuras obrigatórias

Global Solution 2026 — FIAP | Dynamic Programming
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.scenarios import criar_cenario_RS, criar_cenario_MATOPIBA
from src.greedy import dijkstra, dijkstra_municipios_criticos
from src.brute_force import forca_bruta_caminhos, experimento_explosao_combinatoria
from src.performance_monitor import rodar_experimento
from src.visualizations import gerar_todas_figuras


def secao(titulo: str) -> None:
    print(f"\n{'='*70}")
    print(f"  {titulo}")
    print(f"{'='*70}")


def run_cenario_RS():
    secao("CENÁRIO A — Enchentes RS 2024")
    grafo, bst = criar_cenario_RS()
    print(f"Grafo: {grafo}")
    print(f"BST  : {bst}")

    print("\n[BST] Municípios em ordem crescente de risco:")
    for no in bst.percurso_in_order():
        print(f"  risco={no.indice_risco:.2f}  {no.nome}")

    print("\n[BST] Municípios com risco entre 0.70 e 1.00:")
    criticos = bst.buscar(0.70, 1.0)
    for no in criticos:
        print(f"  {no.nome}: risco={no.indice_risco:.2f}, "
              f"custo=R${no.custo_atendimento:.0f}k")

    print("\n[Dijkstra] Rotas mínimas de Porto Alegre para municípios críticos:")
    _, rotas = dijkstra_municipios_criticos(
        grafo, bst, origem=4314902, limiar_risco=0.70
    )
    for id_m, nome, risco, caminho, custo in rotas:
        print(f"  → {nome} (risco={risco:.2f}) | custo={custo:.0f} km | "
              f"nós no caminho: {len(caminho)}")


def run_cenario_MATOPIBA():
    secao("CENÁRIO B — Seca MATOPIBA")
    grafo, bst = criar_cenario_MATOPIBA()
    print(f"Grafo: {grafo}")
    print(f"BST  : {bst}")

    print("\n[BST] Municípios com risco > 0.75 (alta criticidade):")
    criticos = bst.buscar(0.75, 1.0)
    for no in sorted(criticos, key=lambda x: -x.indice_risco):
        print(f"  {no.nome}: risco={no.indice_risco:.2f}")

    print("\n[Dijkstra] Rotas mínimas de Palmas para municípios críticos:")
    _, rotas = dijkstra_municipios_criticos(
        grafo, bst, origem=1721000, limiar_risco=0.75
    )
    for id_m, nome, risco, caminho, custo in rotas:
        print(f"  → {nome} (risco={risco:.2f}) | distância≈{custo:.0f} km")


def run_forca_bruta_pequeno():
    secao("FORÇA BRUTA — Validação em instância pequena (N=7)")
    from src.performance_monitor import gerar_grafo_sintetico
    g = gerar_grafo_sintetico(7, densidade=0.5, seed=42)
    res_fb  = forca_bruta_caminhos(g, 0, 6)
    res_dij = dijkstra(g, 0)
    _, custo_dij = res_dij.caminho_ate(6)

    print(f"Força Bruta  → custo ótimo = {res_fb.custo_otimo:.3f}")
    print(f"             → caminhos avaliados = {res_fb.caminhos_avaliados}")
    print(f"             → chamadas recursivas = {res_fb.chamadas_recursivas}")
    print(f"Dijkstra     → custo = {custo_dij:.3f}")
    gap = abs(custo_dij - res_fb.custo_otimo) / res_fb.custo_otimo * 100
    print(f"Gap de otimalidade = {gap:.2f}%")


def run_explosao_combinatoria():
    secao("EXPLOSÃO COMBINATÓRIA — Crescimento N vs. caminhos")
    experimento_explosao_combinatoria([3, 4, 5, 6, 7, 8, 9, 10])


if __name__ == "__main__":
    import subprocess, sys

    # Serializa grafos em data/processed/
    secao("SERIALIZANDO DADOS EM data/processed/")
    subprocess.run([sys.executable, "data/serialize_data.py"], check=True)

    run_cenario_RS()
    run_cenario_MATOPIBA()
    run_forca_bruta_pequeno()
    run_explosao_combinatoria()

    secao("BENCHMARK DE DESEMPENHO — FB vs. Dijkstra")
    rodar_experimento(
        tamanhos_fb=[5, 6, 7, 8, 9, 10, 11, 12],
        tamanhos_dijk=[5, 6, 7, 8, 9, 10, 11, 12, 20, 50, 100],
    )

    secao("GERANDO FIGURAS OBRIGATÓRIAS")
    gerar_todas_figuras()

    print("\n✓ Sistema executado com sucesso.")
    print("  Figuras disponíveis em: ./output_figures/")
