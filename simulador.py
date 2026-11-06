#!/usr/bin/env python3
"""Simulador de escalonamento de processos (SJF e SRTF).

Uso:
    python simulador.py < entrada.json > resultado.json

Lê um objeto JSON da entrada padrão e escreve um objeto JSON na saída padrão.
Em caso de erro, escreve {"erro": "..."} e encerra com código diferente de zero.
Mensagens auxiliares (se houver) vão apenas para a saída de erro.
"""

import json
import sys

from escalonadores import POLITICAS
from metricas import calcular_metricas
from validacao import ErroEntrada, validar_entrada


def simular(dados):
    """Executa a simulação para um dicionário de entrada já carregado."""
    algoritmo, configuracao, processos = validar_entrada(dados)
    linha_do_tempo = POLITICAS[algoritmo](processos)
    individuais, medias = calcular_metricas(processos, linha_do_tempo)
    return {
        "algoritmo": algoritmo,
        "linha_do_tempo": [
            {"processo": nome, "inicio": inicio, "fim": fim}
            for nome, inicio, fim in linha_do_tempo
        ],
        "processos": individuais,
        "medias": medias,
    }


def main():
    try:
        try:
            dados = json.load(sys.stdin)
        except json.JSONDecodeError:
            raise ErroEntrada("A entrada não é um JSON válido.")
        resultado = simular(dados)
    except ErroEntrada as erro:
        print(json.dumps({"erro": str(erro)}, ensure_ascii=False))
        return 1

    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
