# Relatório: simulação de escalonamento (SJF e SRTF)

**Sistemas Operacionais, Dupla 5:** Jefferson Luis

Convenções: intervalos `[inicio, fim)`; TA = turnaround, Esp = espera, Resp = resposta. Todas as entradas e saídas completas estão em `experimentos/entradas/` e `experimentos/saidas/`. Os Gantt estão em `experimentos/gantt/` (em cada imagem, o SJF fica em cima e o SRTF embaixo; cinza hachurado = CPU ociosa).

---

## Experimento 1: conjunto comum

Processos: P01 (chegada 0, CPU 8), P02 (1, 4), P03 (2, 2), P04 (4, 1).

![Gantt do experimento 1](experimentos/gantt/exp1_comum.png)

### 1.1 Métricas

**SJF**

| Processo | 1ª execução | Conclusão | TA | Esp | Resp |
|---|---|---|---|---|---|
| P01 | 0 | 8 | 8 | 0 | 0 |
| P02 | 11 | 15 | 14 | 10 | 10 |
| P03 | 9 | 11 | 9 | 7 | 7 |
| P04 | 8 | 9 | 5 | 4 | 4 |
| **Média** | | | **9,00** | **5,25** | **5,25** |

**SRTF**

| Processo | 1ª execução | Conclusão | TA | Esp | Resp |
|---|---|---|---|---|---|
| P01 | 0 | 15 | 15 | 7 | 0 |
| P02 | 1 | 8 | 7 | 3 | 0 |
| P03 | 2 | 4 | 2 | 0 | 0 |
| P04 | 4 | 5 | 1 | 0 | 0 |
| **Média** | | | **6,25** | **2,50** | **0,00** |

### 1.2 Decisões de escalonamento

**SJF** (sem preempção): em t=0 só P01 está pronto e executa até t=8, mesmo com P02, P03 e P04 chegando no meio. Em t=8, os prontos são P02 (CPU 4), P03 (2) e P04 (1); a ordem de escolha é pelo menor tempo total: P04 (8→9), P03 (9→11) e P02 (11→15). Nenhuma preempção.

**SRTF** (com preempção), com duas preempções:

- t=1: chega P02 (CPU 4) e P01 tem restante 7. Como 4 < 7, P02 **preempta** P01.
- t=2: chega P03 (CPU 2) e P02 tem restante 3. Como 2 < 3, P03 **preempta** P02. P03 termina em t=4.
- t=4: P03 conclui e P04 chega no mesmo instante (a conclusão é registrada e a chegada admitida antes da decisão). Restantes: P01=7, P02=3, P04=1 → P04 executa (4→5).
- t=5: P02 (3) < P01 (7) → P02 executa (5→8). Em t=8, P01 retoma e executa até 15.

### 1.3 Comparação

Neste conjunto, o SRTF teve médias menores nas três métricas (TA 6,25 contra 9,00; espera 2,50 contra 5,25; resposta 0,00 contra 5,25). O custo foi concentrado no processo longo: P01 passou de TA 8 e espera 0 (SJF) para TA 15 e espera 7 (SRTF). A conclusão do último processo é a mesma (t=15), pois não há ociosidade nem custo de troca de contexto: o que muda é *quem* espera. Isto vale para este conjunto; não prova superioridade em geral.

---

## Experimento 2: casos elaborados pela dupla

### 2a. CPU ociosa entre chegadas

**Objetivo:** verificar `OCIOSO` no início e no meio da linha do tempo, e uma chegada curta durante a execução de um processo mais longo.
P01 (2, 3), P02 (3, 2), P03 (10, 4), P04 (11, 1).

![Gantt 2a](experimentos/gantt/exp2a_ocioso.png)

| | Linha do tempo | TA médio | Esp média | Resp média |
|---|---|---|---|---|
| SJF | OCIOSO [0,2), P01 [2,5), P02 [5,7), OCIOSO [7,10), P03 [10,14), P04 [14,15) | 3,75 | 1,25 | 1,25 |
| SRTF | OCIOSO [0,2), P01 [2,5), P02 [5,7), OCIOSO [7,10), P03 [10,11), P04 [11,12), P03 [12,15) | 3,25 | 0,75 | 0,50 |

Até t=10 os dois são iguais. Em t=11, chega P04 (CPU 1) enquanto P03 ainda tem restante 3: o SRTF preempta e o SJF não.

### 2b. Durações diferentes e chegadas durante a execução

**Objetivo:** processo longo chegando primeiro, seguido de processos mais curtos enquanto ele executa.
P01 (0, 9), P02 (1, 5), P03 (3, 2), P04 (4, 7), P05 (6, 1).

![Gantt 2b](experimentos/gantt/exp2b_duracoes.png)

| | Linha do tempo | TA médio | Esp média | Resp média |
|---|---|---|---|---|
| SJF | P01 [0,9), P05 [9,10), P03 [10,12), P02 [12,17), P04 [17,24) | 11,60 | 6,80 | 6,80 |
| SRTF | P01 [0,1), P02 [1,3), P03 [3,5), P02 [5,6), P05 [6,7), P02 [7,9), P04 [9,16), P01 [16,24) | 9,40 | 4,60 | 1,00 |

No SRTF, P01 só volta à CPU em t=16 (espera 15, TA 24); no SJF ele termina em t=9 sem esperar (TA 9). Em compensação, P02, P03 e P05 praticamente não esperam no SRTF.

### 2c. Empates

**Objetivo:** exercitar os desempates. O arquivo lista **P03 antes de P02** de propósito, para mostrar que a ordem do arquivo não conta.
P01 (0, 6), P03 (2, 4), P02 (2, 4), P04 (3, 2), P05 (4, 4).

![Gantt 2c](experimentos/gantt/exp2c_empates.png)

| | Linha do tempo | TA médio | Esp média | Resp média |
|---|---|---|---|---|
| SJF | P01 [0,6), P04 [6,8), P02 [8,12), P03 [12,16), P05 [16,20) | 10,20 | 6,20 | 6,20 |
| SRTF | P01 [0,3), P04 [3,5), P01 [5,8), P02 [8,12), P03 [12,16), P05 [16,20) | 10,00 | 6,00 | 5,60 |

Empates exercitados:

- **Mesma chegada e mesmo CPU (P02 × P03):** vence o menor ID, P02, mesmo vindo depois no arquivo.
- **Mesmo CPU, chegadas diferentes (P02/P03 × P05):** P05 (chegada 4) fica por último.
- **SRTF, chegada empatada com o restante do atual:** em t=2, P01 tem restante 4 e chegam P02 e P03 com CPU 4. Empate → P01 **permanece**, sem preempção.

### Conferência manual (casos do Experimento 1 e 2c)

**Exp. 1, SRTF.** Já descrita em 1.2. Cálculos:

- P01: conclusão 15 → TA = 15 − 0 = 15; Esp = 15 − 8 = 7; Resp = 0 − 0 = 0.
- P02: conclusão 8 → TA = 8 − 1 = 7; Esp = 7 − 4 = 3; Resp = 1 − 1 = 0.
- P03: conclusão 4 → TA = 4 − 2 = 2; Esp = 2 − 2 = 0; Resp = 2 − 2 = 0.
- P04: conclusão 5 → TA = 5 − 4 = 1; Esp = 1 − 1 = 0; Resp = 4 − 4 = 0.
- Médias: TA = (15+7+2+1)/4 = 6,25; Esp = (7+3+0+0)/4 = 2,50; Resp = 0.

**Exp. 1, SJF.** P01 0→8; depois P04 8→9, P03 9→11, P02 11→15. P02: TA = 15 − 1 = 14, Esp = 14 − 4 = 10, Resp = 11 − 1 = 10. P03: TA = 11 − 2 = 9, Esp = 7, Resp = 9 − 2 = 7. P04: TA = 9 − 4 = 5, Esp = 4, Resp = 8 − 4 = 4. Esp média = (0+10+7+4)/4 = 5,25.

**Exp. 2c, SRTF (empates).**

- t=0–2: P01 executa (restante 4 em t=2).
- t=2: chegam P02 e P03 (CPU 4). Empate com o restante de P01 (4): P01 continua.
- t=3: chega P04 (CPU 2). P01 tem restante 3 e 2 < 3, então P04 preempta. Em t=4 chega P05 (CPU 4), mas o atual (P04) tem restante 1, e não há preempção.
- t=5: P04 termina. Restantes: P01=3, P02=4, P03=4, P05=4 → P01 executa (5→8).
- t=8: P02, P03 e P05 empatam em 4 → desempate por chegada e ID: P02 (8→12), P03 (12→16), P05 (16→20).
- Resultado: coincide com a saída do simulador. Esp média = (2+6+10+0+12)/5 = 6,00.

Além da conferência manual, `testes.py` compara os dois algoritmos com uma simulação independente, unidade a unidade, em 3000 conjuntos aleatórios cada.

---

## Experimento 3: características dos algoritmos

### 3.1 SJF: espera de processo longo e starvation

**Entrada:** P01 (0, 3); **P02 (1, 10)**, que é o processo longo; e dez processos curtos P03…P12, de CPU 2, chegando em t = 2, 4, 6, …, 20 (um a cada 2 unidades).

![Gantt exp 3 SJF](experimentos/gantt/exp3_sjf_longo.png)

SJF: P01 [0,3), P03 [3,5), P04 [5,7), …, P12 [21,23), **P02 [23,33)**.

- Em todo ponto de decisão entre t=3 e t=21 há pelo menos um processo curto pronto (cada novo curto chega antes de o anterior terminar). Como o SJF escolhe pelo menor tempo total (2 < 10), P02 nunca é escolhido. Ele só executa em t=23, após o último curto: **espera 22 unidades** (TA 32), enquanto cada curto espera só 1 unidade.
- A espera média do conjunto fica pequena (2,67), o que esconde o fato de que um processo está sendo preterido por muito tempo.
- **Starvation:** se os curtos continuassem chegando nesse ritmo (um de CPU 2 a cada 2 unidades), a CPU estaria sempre ocupada e sempre haveria um curto pronto, então P02 nunca seria escolhido. Aqui ele só roda porque as chegadas terminam. O que causa o problema é a continuidade de chegadas de processos menores que o longo, não o tamanho do processo longo por si só.
- Nesta mesma entrada, o SRTF produz a mesma linha do tempo (veja `exp3_sjf_longo_SRTF.json`), e o longo também espera até t=23. O SRTF tem risco igual ou maior de starvation, pois um longo pode ser preemptado a qualquer chegada de um processo com restante menor.

### 3.2 SRTF: chegada que interrompe e chegadas que não interrompem

**Entrada:** P01 (0, 7), P02 (2, 2), P03 (3, 6), P04 (5, 5), P05 (6, 3).

![Gantt exp 3 SRTF](experimentos/gantt/exp3_srtf_preempcao.png)

SRTF: P01 [0,2), P02 [2,4), P01 [4,9), P05 [9,12), P04 [12,17), P03 [17,23).

| Instante | Chegada | Processo atual (restante) | Decisão |
|---|---|---|---|
| t=2 | P02 (CPU 2) | P01 (5) | 2 < 5: **interrompe** P01 |
| t=3 | P03 (CPU 6) | P02 (1) | 6 > 1: não interrompe |
| t=5 | P04 (CPU 5) | P01 (4) | 5 > 4: não interrompe |
| t=6 | P05 (CPU 3) | P01 (3) | 3 = 3: **empate**, o atual permanece (a preempção exige restante *estritamente* menor) |

Em t=4, P02 termina; entre P01 (restante 5) e P03 (6), o menor é P01, que retoma. Em t=9, P01 termina e os prontos são P05 (3), P04 (5) e P03 (6), executados nessa ordem.

Médias: SRTF TA 9,80, Esp 5,20, Resp 4,80; SJF (mesma entrada) TA 10,40, Esp 5,80, Resp 5,80. A única diferença vem de P02: no SJF ele espera P01 inteiro (resposta 5), e no SRTF executa imediatamente (resposta 0). Mais uma vez, isto é uma observação sobre este conjunto específico.

---

## Observações finais

- Os dois algoritmos precisam conhecer o tempo de CPU de antemão (premissa do modelo), o que raramente ocorre em sistemas reais.
- O ganho do SRTF sobre o SJF em espera média nos nossos conjuntos veio de beneficiar os processos curtos às custas dos longos (exp. 1, 2a, 2b), o que também é a origem do risco de starvation discutido em 3.1.
- Neste modelo (custo de troca de contexto zero) a preempção não tem custo. Em um sistema real, o número de preempções do SRTF teria de ser considerado.
