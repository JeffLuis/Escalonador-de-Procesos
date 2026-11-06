"""Leitura e validação da entrada do simulador.

Esta camada não conhece nenhuma política de escalonamento: apenas verifica se o
JSON recebido respeita o enunciado e devolve estruturas já normalizadas.
"""

from dataclasses import dataclass

ALGORITMOS_CONHECIDOS = {"FCFS", "SJF", "SRTF", "RR", "MLFQ", "CFS"}
ALGORITMOS_IMPLEMENTADOS = {"SJF", "SRTF"}
ID_RESERVADO = "OCIOSO"


class ErroEntrada(Exception):
    """Entrada inválida; a mensagem é devolvida ao usuário no campo "erro"."""


@dataclass
class Processo:
    id: str
    chegada: int
    cpu: int
    restante: int = 0  # usado pelos escalonadores (preenchido no início)

    def __post_init__(self):
        self.restante = self.cpu


def _eh_inteiro(valor):
    # bool é subclasse de int em Python; "true" não é um inteiro válido aqui.
    return isinstance(valor, int) and not isinstance(valor, bool)


def validar_entrada(dados):
    """Valida o objeto JSON de entrada e devolve (algoritmo, configuracao, processos)."""
    if not isinstance(dados, dict):
        raise ErroEntrada("A entrada deve ser um objeto JSON.")

    # --- algoritmo ---------------------------------------------------------
    if "algoritmo" not in dados:
        raise ErroEntrada("O campo 'algoritmo' é obrigatório.")
    algoritmo = dados["algoritmo"]
    if not isinstance(algoritmo, str):
        raise ErroEntrada("O campo 'algoritmo' deve ser uma string.")
    if algoritmo not in ALGORITMOS_CONHECIDOS:
        raise ErroEntrada(f"Algoritmo desconhecido: '{algoritmo}'.")
    if algoritmo not in ALGORITMOS_IMPLEMENTADOS:
        raise ErroEntrada(f"Algoritmo não implementado: '{algoritmo}'.")

    # --- configuração ------------------------------------------------------
    # SJF e SRTF não possuem parâmetros; qualquer chave presente é ignorada.
    if "configuracao" not in dados:
        raise ErroEntrada("O campo 'configuracao' é obrigatório (use {}).")
    configuracao = dados["configuracao"]
    if not isinstance(configuracao, dict):
        raise ErroEntrada("O campo 'configuracao' deve ser um objeto.")

    # --- processos ---------------------------------------------------------
    if "processos" not in dados:
        raise ErroEntrada("O campo 'processos' é obrigatório.")
    lista = dados["processos"]
    if not isinstance(lista, list) or len(lista) == 0:
        raise ErroEntrada("O campo 'processos' deve ser uma lista não vazia.")

    processos = []
    ids_vistos = set()
    for indice, item in enumerate(lista):
        if not isinstance(item, dict):
            raise ErroEntrada(f"O processo na posição {indice} deve ser um objeto.")

        for campo in ("id", "chegada", "cpu"):
            if campo not in item:
                raise ErroEntrada(f"O processo na posição {indice} não possui o campo '{campo}'.")

        pid = item["id"]
        if not isinstance(pid, str) or pid == "":
            raise ErroEntrada("O ID do processo deve ser uma string não vazia.")
        if pid == ID_RESERVADO:
            raise ErroEntrada(f"O ID '{ID_RESERVADO}' é reservado.")
        if pid in ids_vistos:
            raise ErroEntrada(f"O ID '{pid}' está repetido.")
        ids_vistos.add(pid)

        if not _eh_inteiro(item["chegada"]) or item["chegada"] < 0:
            raise ErroEntrada("O instante de chegada deve ser um inteiro maior ou igual a zero.")
        if not _eh_inteiro(item["cpu"]) or item["cpu"] <= 0:
            raise ErroEntrada("O tempo de CPU deve ser um inteiro positivo.")

        # 'peso' (usado só pelo CFS) e quaisquer outros campos são ignorados.
        processos.append(Processo(pid, item["chegada"], item["cpu"]))

    return algoritmo, configuracao, processos
