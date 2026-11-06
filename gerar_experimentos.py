"""Gera os arquivos JSON dos experimentos, executa o simulador pela interface
padrão (stdin/stdout), desenha os diagramas de Gantt e imprime um resumo.

Uso: python gerar_experimentos.py
Requer matplotlib apenas para os PNGs (o simulador não depende dele).
"""

import json
import subprocess
import sys
from pathlib import Path

AQUI = Path(__file__).parent
ENTRADAS = AQUI / "experimentos" / "entradas"
SAIDAS = AQUI / "experimentos" / "saidas"
GANTT = AQUI / "experimentos" / "gantt"
ALGORITMOS = ("SJF", "SRTF")


def p(id_, chegada, cpu):
    return {"id": id_, "chegada": chegada, "cpu": cpu}


EXPERIMENTOS = {
    # Experimento 1: conjunto comum (seção 5.1 do enunciado)
    "exp1_comum": [p("P01", 0, 8), p("P02", 1, 4), p("P03", 2, 2), p("P04", 4, 1)],
    # Experimento 2a: CPU ociosa antes da primeira chegada e entre chegadas
    "exp2a_ocioso": [p("P01", 2, 3), p("P02", 3, 2), p("P03", 10, 4), p("P04", 11, 1)],
    # Experimento 2b: durações diferentes, chegadas durante uma execução
    "exp2b_duracoes": [p("P01", 0, 9), p("P02", 1, 5), p("P03", 3, 2), p("P04", 4, 7), p("P05", 6, 1)],
    # Experimento 2c: empates (P03 listado antes de P02 de propósito)
    "exp2c_empates": [p("P01", 0, 6), p("P03", 2, 4), p("P02", 2, 4), p("P04", 3, 2), p("P05", 4, 4)],
    # Experimento 3 (SJF): processo longo P02 espera enquanto curtos chegam sem parar
    "exp3_sjf_longo": [p("P01", 0, 3), p("P02", 1, 10)]
                      + [p(f"P{i:02d}", 2 * (i - 2), 2) for i in range(3, 13)],
    # Experimento 3 (SRTF): chegadas que interrompem (P02) e que não interrompem (P03, P04, P05)
    "exp3_srtf_preempcao": [p("P01", 0, 7), p("P02", 2, 2), p("P03", 3, 6), p("P04", 5, 5), p("P05", 6, 3)],
}


def executar(arquivo_entrada, arquivo_saida):
    with open(arquivo_entrada) as entrada:
        resultado = subprocess.run([sys.executable, str(AQUI / "simulador.py")],
                                   stdin=entrada, capture_output=True, text=True, check=True)
    arquivo_saida.write_text(resultado.stdout)
    return json.loads(resultado.stdout)


def desenhar_gantt(nome, resultados):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    ids = sorted({i["processo"] for r in resultados.values() for i in r["linha_do_tempo"]} - {"OCIOSO"})
    cores = plt.get_cmap("tab10")
    fim_total = max(r["linha_do_tempo"][-1]["fim"] for r in resultados.values())
    fig, eixos = plt.subplots(len(resultados), 1, figsize=(10, 1.0 + 2.1 * len(resultados)), sharex=True)
    for eixo, (alg, r) in zip(eixos, resultados.items()):
        for item in r["linha_do_tempo"]:
            if item["processo"] == "OCIOSO":
                eixo.axvspan(item["inicio"], item["fim"], color="#dddddd", hatch="//", ec="#aaaaaa")
                continue
            linha = ids.index(item["processo"])
            eixo.barh(linha, item["fim"] - item["inicio"], left=item["inicio"], height=0.6,
                      color=cores(linha % 10), edgecolor="black")
        eixo.set_yticks(range(len(ids)))
        eixo.set_yticklabels(ids, fontsize=8)
        eixo.invert_yaxis()
        eixo.set_title(f"{alg}  (turnaround médio {r['medias']['turnaround']:.2f} | "
                       f"espera média {r['medias']['espera']:.2f} | resposta média {r['medias']['resposta']:.2f})",
                       fontsize=9, loc="left")
        eixo.grid(axis="x", alpha=0.3)
    eixos[-1].set_xticks(range(0, fim_total + 1, 1 if fim_total <= 25 else 2))
    eixos[-1].tick_params(axis="x", labelsize=8)
    eixos[-1].set_xlabel("tempo (unidades simuladas); cinza hachurado = CPU ociosa")
    fig.tight_layout()
    fig.savefig(GANTT / f"{nome}.png", dpi=130)
    plt.close(fig)


def principal():
    for pasta in (ENTRADAS, SAIDAS, GANTT):
        pasta.mkdir(parents=True, exist_ok=True)

    for nome, processos in EXPERIMENTOS.items():
        resultados = {}
        for alg in ALGORITMOS:
            entrada = ENTRADAS / f"{nome}_{alg}.json"
            entrada.write_text(json.dumps({"algoritmo": alg, "configuracao": {}, "processos": processos},
                                          indent=2, ensure_ascii=False) + "\n")
            resultados[alg] = executar(entrada, SAIDAS / f"{nome}_{alg}.json")
        desenhar_gantt(nome, resultados)

        print(f"\n=== {nome} ===")
        for alg, r in resultados.items():
            tl = " | ".join(f"{i['processo']} [{i['inicio']},{i['fim']})" for i in r["linha_do_tempo"])
            print(f"{alg}: {tl}")
            for m in r["processos"]:
                print(f"   {m['id']}: 1ª exec={m['primeira_execucao']:>2} concl={m['conclusao']:>2} "
                      f"TA={m['turnaround']:>2} esp={m['espera']:>2} resp={m['resposta']:>2}")
            md = r["medias"]
            print(f"   médias: TA={md['turnaround']:.4f} esp={md['espera']:.4f} resp={md['resposta']:.4f}")


if __name__ == "__main__":
    principal()
