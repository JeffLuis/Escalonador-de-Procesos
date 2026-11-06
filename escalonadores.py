"""Políticas de escalonamento: SJF (sem preempção) e SRTF (com preempção).

Cada função recebe a lista de `Processo` e devolve a linha do tempo como uma
lista de tuplas (processo, inicio, fim), já coberta de ponta a ponta e com
intervalos adjacentes do mesmo processo unidos. O tempo é uma variável inteira
que apenas avança; não há esperas reais.

Desempate geral (enunciado, seção 3): menor instante de chegada e, depois, ID
em ordem lexicográfica.
"""

OCIOSO = "OCIOSO"


def _unir_adjacentes(fatias):
    """Une fatias consecutivas do mesmo processo (apenas apresentação)."""
    unidas = []
    for nome, inicio, fim in fatias:
        if unidas and unidas[-1][0] == nome and unidas[-1][2] == inicio:
            unidas[-1] = (nome, unidas[-1][1], fim)
        else:
            unidas.append((nome, inicio, fim))
    return unidas


def _admitir_chegadas(pendentes, indice, tempo, prontos):
    """Move para `prontos` todos os processos com chegada <= tempo."""
    while indice < len(pendentes) and pendentes[indice].chegada <= tempo:
        prontos.append(pendentes[indice])
        indice += 1
    return indice


def sjf(processos):
    """Shortest Job First: escolhe o menor tempo total de CPU entre os prontos
    e o executa até concluir (não há preempção)."""
    pendentes = sorted(processos, key=lambda p: (p.chegada, p.id))
    prontos = []
    fatias = []
    tempo = 0
    indice = 0
    concluidos = 0

    while concluidos < len(pendentes):
        indice = _admitir_chegadas(pendentes, indice, tempo, prontos)

        if not prontos:  # CPU ociosa até a próxima chegada
            proxima = pendentes[indice].chegada
            fatias.append((OCIOSO, tempo, proxima))
            tempo = proxima
            continue

        escolhido = min(prontos, key=lambda p: (p.cpu, p.chegada, p.id))
        prontos.remove(escolhido)
        fatias.append((escolhido.id, tempo, tempo + escolhido.cpu))
        tempo += escolhido.cpu
        concluidos += 1

    return _unir_adjacentes(fatias)


def srtf(processos):
    """Shortest Remaining Time First: a cada chegada ou conclusão, executa o
    pronto com menor tempo restante. O processo atual só é interrompido por
    outro com tempo restante ESTRITAMENTE menor; em empate, o atual permanece."""
    pendentes = sorted(processos, key=lambda p: (p.chegada, p.id))
    prontos = []   # inclui o processo em execução
    atual = None
    fatias = []
    tempo = 0
    indice = 0
    concluidos = 0

    while concluidos < len(pendentes):
        indice = _admitir_chegadas(pendentes, indice, tempo, prontos)

        if not prontos:  # CPU ociosa até a próxima chegada
            proxima = pendentes[indice].chegada
            fatias.append((OCIOSO, tempo, proxima))
            tempo = proxima
            continue

        melhor = min(prontos, key=lambda p: (p.restante, p.chegada, p.id))
        if atual is None:
            atual = melhor                         # CPU livre: desempate geral
        elif melhor.restante < atual.restante:
            atual = melhor                         # preempção (estritamente menor)

        # Só uma nova chegada pode mudar a decisão antes de o atual terminar.
        proxima_chegada = pendentes[indice].chegada if indice < len(pendentes) else None
        duracao = atual.restante
        if proxima_chegada is not None:
            duracao = min(duracao, proxima_chegada - tempo)

        fatias.append((atual.id, tempo, tempo + duracao))
        tempo += duracao
        atual.restante -= duracao

        if atual.restante == 0:
            prontos.remove(atual)
            atual = None
            concluidos += 1

    return _unir_adjacentes(fatias)


POLITICAS = {"SJF": sjf, "SRTF": srtf}
