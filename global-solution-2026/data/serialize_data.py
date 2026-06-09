"""
serialize_data.py
=================
Serializa os grafos e BSTs dos cenários em JSON para data/processed/.
Executado automaticamente pelo main.py.
"""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from src.scenarios import criar_cenario_RS, criar_cenario_MATOPIBA

OUT = os.path.join(os.path.dirname(__file__), "..", "data", "processed")
os.makedirs(OUT, exist_ok=True)

def serializar_cenario(nome, grafo, bst):
    # Grafo → JSON
    grafo_dict = {
        "vertices": [
            {"id": v, "nome": grafo.atributos(v)[1],
             "risco": grafo.atributos(v)[2],
             "custo": grafo.atributos(v)[3],
             "populacao": grafo.atributos(v)[4]}
            for v in grafo.vertices()
        ],
        "arestas": [
            {"u": u, "v": v, "peso": peso}
            for u, v, peso in grafo.todas_arestas()
        ]
    }
    path_grafo = os.path.join(OUT, f"grafo_{nome}.json")
    with open(path_grafo, "w", encoding="utf-8") as f:
        json.dump(grafo_dict, f, ensure_ascii=False, indent=2)

    # BST in-order → JSON
    bst_list = [
        {"id": no.id_municipio, "nome": no.nome,
         "risco": no.indice_risco, "custo": no.custo_atendimento,
         "populacao": no.populacao}
        for no in bst.percurso_in_order()
    ]
    path_bst = os.path.join(OUT, f"bst_{nome}.json")
    with open(path_bst, "w", encoding="utf-8") as f:
        json.dump(bst_list, f, ensure_ascii=False, indent=2)

    print(f"  ✓ {path_grafo}")
    print(f"  ✓ {path_bst}")

if __name__ == "__main__":
    print("Serializando cenários em data/processed/...")
    serializar_cenario("RS", *criar_cenario_RS())
    serializar_cenario("MATOPIBA", *criar_cenario_MATOPIBA())
    print("Serialização concluída.")
