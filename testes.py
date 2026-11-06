"""Testes do simulador. Execute com: python testes.py

1. Compara SJF e SRTF com uma implementação de referência independente, que
   simula unidade de tempo por unidade de tempo (sem pular intervalos).
2. Verifica invariantes: cobertura da linha do tempo, fórmulas das métricas.
3. Confere o exemplo da seção 5.1 do enunciado e casos de entrada inválida.
"""

import json
import random
import subprocess
import sys
import unittest
from pathlib import Path

from simulador import simular

AQUI = Path(__file__).parent


# --------------------------------------------------------------------------
# Referência: simulação unidade a unidade
# --------------------------------------------------------------------------
def referencia(algoritmo, processos):
    """Devolve a linha do tempo por unidade: lista com o nome em cada instante."""
    restante = {p["id"]: p["cpu"] for p in processos}
    chegada = {p["id"]: p["chegada"] for p in processos}
    cpu = {p["id"]: p["cpu"] for p in processos}
    por_unidade = []
    atual = None
    t = 0
    while any(r > 0 for r in restante.values()):
        prontos = [i for i in restante if restante[i] > 0 and chegada[i] <= t]
        if not prontos:
            por_unidade.append("OCIOSO")
            atual = None
            t += 1
            continue
        if algoritmo == "SJF":
            if atual is None or restante[atual] == 0:
                atual = min(prontos, key=lambda i: (cpu[i], chegada[i], i))
        else:  # SRTF: em empate, o processo atual tem preferência
            atual = min(prontos, key=lambda i: (restante[i], 0 if i == atual else 1, chegada[i], i))
        por_unidade.append(atual)
        restante[atual] -= 1
        if restante[atual] == 0:
            atual = None
        t += 1
    return por_unidade


def expandir(linha_do_tempo):
    por_unidade = []
    for item in linha_do_tempo:
        por_unidade.extend([item["processo"]] * (item["fim"] - item["inicio"]))
    return por_unidade


def gerar_caso(rng):
    n = rng.randint(1, 8)
    ids = [f"P{i:02d}" for i in range(1, n + 1)]
    processos = [
        {"id": i, "chegada": rng.randint(0, 12), "cpu": rng.randint(1, 8)}
        for i in ids
    ]
    rng.shuffle(processos)  # a ordem do arquivo não pode influenciar
    return processos


class TestesSimulador(unittest.TestCase):
    def test_contra_referencia_aleatoria(self):
        rng = random.Random(2024)
        for _ in range(3000):
            processos = gerar_caso(rng)
            for alg in ("SJF", "SRTF"):
                saida = simular({"algoritmo": alg, "configuracao": {}, "processos": processos})
                self.assertEqual(expandir(saida["linha_do_tempo"]), referencia(alg, processos),
                                 f"{alg} diverge em {processos}")

    def test_invariantes(self):
        rng = random.Random(7)
        for _ in range(1000):
            processos = gerar_caso(rng)
            for alg in ("SJF", "SRTF"):
                saida = simular({"algoritmo": alg, "configuracao": {}, "processos": processos})
                tl = saida["linha_do_tempo"]
                self.assertEqual(tl[0]["inicio"], 0)
                for a, b in zip(tl, tl[1:]):
                    self.assertEqual(a["fim"], b["inicio"])        # sem lacunas/sobreposição
                    self.assertNotEqual(a["processo"], b["processo"])  # adjacentes unidos
                for item in tl:
                    self.assertGreater(item["fim"], item["inicio"])
                cpu = {p["id"]: p["cpu"] for p in processos}
                cheg = {p["id"]: p["chegada"] for p in processos}
                for m in saida["processos"]:
                    recebido = sum(i["fim"] - i["inicio"] for i in tl if i["processo"] == m["id"])
                    self.assertEqual(recebido, cpu[m["id"]])
                    self.assertEqual(m["turnaround"], m["conclusao"] - cheg[m["id"]])
                    self.assertEqual(m["espera"], m["turnaround"] - cpu[m["id"]])
                    self.assertEqual(m["resposta"], m["primeira_execucao"] - cheg[m["id"]])
                    self.assertGreaterEqual(m["primeira_execucao"], cheg[m["id"]])
                self.assertEqual([m["id"] for m in saida["processos"]],
                                 sorted(m["id"] for m in saida["processos"]))

    def test_exemplo_do_enunciado(self):
        procs = [{"id": "P01", "chegada": 0, "cpu": 8}, {"id": "P02", "chegada": 1, "cpu": 4},
                 {"id": "P03", "chegada": 2, "cpu": 2}, {"id": "P04", "chegada": 4, "cpu": 1}]
        sjf = simular({"algoritmo": "SJF", "configuracao": {}, "processos": procs})
        self.assertEqual([(i["processo"], i["inicio"], i["fim"]) for i in sjf["linha_do_tempo"]],
                         [("P01", 0, 8), ("P04", 8, 9), ("P03", 9, 11), ("P02", 11, 15)])
        self.assertAlmostEqual(sjf["medias"]["espera"], 5.25)
        srtf = simular({"algoritmo": "SRTF", "configuracao": {}, "processos": procs})
        self.assertEqual([(i["processo"], i["inicio"], i["fim"]) for i in srtf["linha_do_tempo"]],
                         [("P01", 0, 1), ("P02", 1, 2), ("P03", 2, 4), ("P04", 4, 5),
                          ("P02", 5, 8), ("P01", 8, 15)])
        self.assertAlmostEqual(srtf["medias"]["turnaround"], 6.25)

    def test_ocioso_inicial_e_intermediario(self):
        procs = [{"id": "P01", "chegada": 2, "cpu": 1}, {"id": "P02", "chegada": 6, "cpu": 1}]
        for alg in ("SJF", "SRTF"):
            tl = simular({"algoritmo": alg, "configuracao": {}, "processos": procs})["linha_do_tempo"]
            self.assertEqual([(i["processo"], i["inicio"], i["fim"]) for i in tl],
                             [("OCIOSO", 0, 2), ("P01", 2, 3), ("OCIOSO", 3, 6), ("P02", 6, 7)])

    def test_srtf_empate_mantem_atual(self):
        procs = [{"id": "P01", "chegada": 0, "cpu": 4}, {"id": "P02", "chegada": 1, "cpu": 3}]
        tl = simular({"algoritmo": "SRTF", "configuracao": {}, "processos": procs})["linha_do_tempo"]
        self.assertEqual([(i["processo"], i["inicio"], i["fim"]) for i in tl],
                         [("P01", 0, 4), ("P02", 4, 7)])

    def test_ignora_campos_extras(self):
        procs = [{"id": "P01", "chegada": 0, "cpu": 2, "peso": 2048}]
        saida = simular({"algoritmo": "SJF", "configuracao": {"quantum": 2}, "processos": procs})
        self.assertEqual(saida["medias"]["turnaround"], 2)


class TestesCLI(unittest.TestCase):
    def executar(self, texto):
        return subprocess.run([sys.executable, str(AQUI / "simulador.py")], input=texto,
                              capture_output=True, text=True)

    def test_entradas_invalidas(self):
        base = {"algoritmo": "SJF", "configuracao": {},
                "processos": [{"id": "P01", "chegada": 0, "cpu": 1}]}

        def com(**mudancas):
            copia = json.loads(json.dumps(base))
            for chave, valor in mudancas.items():
                if chave == "proc":
                    copia["processos"][0].update(valor)
                else:
                    copia[chave] = valor
            return json.dumps(copia)

        casos = [
            "isto não é json",
            "[]",
            com(algoritmo="RR"),            # conhecido, mas não implementado
            com(algoritmo="XYZ"),
            com(processos=[]),
            com(configuracao=[]),
            com(proc={"cpu": 0}),
            com(proc={"cpu": 2.5}),
            com(proc={"cpu": True}),
            com(proc={"chegada": -1}),
            com(proc={"id": ""}),
            com(proc={"id": "OCIOSO"}),
            com(processos=[{"id": "P01", "chegada": 0, "cpu": 1},
                           {"id": "P01", "chegada": 1, "cpu": 1}]),
        ]
        for texto in casos:
            resultado = self.executar(texto)
            self.assertNotEqual(resultado.returncode, 0, texto)
            self.assertIn("erro", json.loads(resultado.stdout), texto)

    def test_execucao_valida(self):
        entrada = {"algoritmo": "SRTF", "configuracao": {},
                   "processos": [{"id": "P01", "chegada": 0, "cpu": 3}]}
        resultado = self.executar(json.dumps(entrada))
        self.assertEqual(resultado.returncode, 0)
        self.assertEqual(json.loads(resultado.stdout)["linha_do_tempo"],
                         [{"processo": "P01", "inicio": 0, "fim": 3}])


if __name__ == "__main__":
    unittest.main(verbosity=2)
