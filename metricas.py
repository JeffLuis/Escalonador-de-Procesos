"""Cálculo das métricas a partir da linha do tempo (independente da política).

    turnaround = conclusão − chegada
    espera     = turnaround − tempo de CPU
    resposta   = primeira execução − chegada
"""

from escalonadores import OCIOSO


def calcular_metricas(processos, linha_do_tempo):
    primeira = {}
    conclusao = {}
    for nome, inicio, fim in linha_do_tempo:
        if nome == OCIOSO:
            continue
        primeira.setdefault(nome, inicio)   # primeiro início encontrado
        conclusao[nome] = fim               # último fim encontrado

    individuais = []
    for p in sorted(processos, key=lambda p: p.id):
        turnaround = conclusao[p.id] - p.chegada
        individuais.append({
            "id": p.id,
            "primeira_execucao": primeira[p.id],
            "conclusao": conclusao[p.id],
            "turnaround": turnaround,
            "espera": turnaround - p.cpu,
            "resposta": primeira[p.id] - p.chegada,
        })

    n = len(individuais)
    medias = {
        chave: sum(item[chave] for item in individuais) / n
        for chave in ("turnaround", "espera", "resposta")
    }
    return individuais, medias
