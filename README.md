# Simulador de escalonamento de processos: SJF e SRTF

**Disciplina:** Sistemas Operacionais
**Dupla 5:** `Jefferson
**Algoritmos implementados:** `SJF` (Shortest Job First) e `SRTF` (Shortest Remaining Time First)

## Requisitos

- Python 3.8 ou superior (apenas biblioteca padrão).
- `matplotlib` **somente** para regenerar os diagramas de Gantt (`gerar_experimentos.py`). O simulador não depende dele.

## Como executar

```bash
python simulador.py < entrada.json > resultado.json
```

O programa lê um objeto JSON da entrada padrão e escreve um objeto JSON na saída padrão, conforme o enunciado (seções 5.1 e 5.2). Exemplo de entrada:

```json
{
  "algoritmo": "SRTF",
  "configuracao": {},
  "processos": [
    {"id": "P01", "chegada": 0, "cpu": 8},
    {"id": "P02", "chegada": 1, "cpu": 4}
  ]
}
```

Para comparar os dois algoritmos, execute duas vezes alterando apenas o campo `algoritmo` (`"SJF"` ou `"SRTF"`). Em entrada inválida, o programa imprime `{"erro": "..."}` e encerra com código 1, sem simulação parcial.

Outros comandos:

```bash
python testes.py              # testes automáticos
python gerar_experimentos.py  # regenera entradas, saídas e Gantt dos experimentos
```

## Organização do código

| Arquivo | Responsabilidade |
|---|---|
| `validacao.py` | Leitura e validação da entrada (tipos, valores, IDs únicos, `OCIOSO` reservado, algoritmo implementado). |
| `escalonadores.py` | Política de escalonamento: `sjf()` e `srtf()`. Produzem a linha do tempo. |
| `metricas.py` | Turnaround, espera, resposta e médias, calculados **só a partir da linha do tempo**. |
| `simulador.py` | Programa principal (stdin → stdout, tratamento de erros e código de saída). |
| `testes.py` | Testes automáticos (ver abaixo). |
| `gerar_experimentos.py` | Gera os JSON dos experimentos, roda o simulador pela CLI e desenha os Gantt. |
| `experimentos/` | `entradas/`, `saidas/` e `gantt/` (PNG) de todos os experimentos. |
| `relatorio.md` | Relatório com Gantt, métricas, conferência manual e análises. |

## Estruturas de dados e decisões

- **`Processo`** (dataclass): `id`, `chegada`, `cpu` e `restante` (usado pelo SRTF).
- **Lista de pendentes**, ordenada por `(chegada, id)`, com um índice que avança conforme os processos chegam. Assim, a ordem dos processos no arquivo de entrada não influencia o resultado.
- **Lista de prontos**; a escolha usa `min()` com chave de desempate:
  - SJF: `(cpu, chegada, id)`.
  - SRTF: `(restante, chegada, id)`, mas o processo atual só é substituído se o melhor candidato tiver `restante` **estritamente menor**. Em empate com o atual, ele permanece na CPU.
- **Tempo simulado:** uma variável inteira `tempo` que apenas avança. Nada de esperas reais.
- **SJF** avança até o fim de cada processo escolhido. **SRTF** é orientado a eventos: executa o atual até o fim dele ou até a próxima chegada (único evento que pode mudar a decisão antes da conclusão) e então reavalia.
- **CPU ociosa:** quando não há prontos, registra-se `OCIOSO` até a próxima chegada (inclusive no início, se a primeira chegada for > 0).
- **Linha do tempo:** intervalos `[inicio, fim)` cobrindo a simulação toda; fatias adjacentes do mesmo processo são unidas apenas na apresentação.
- Complexidade: cada decisão percorre a lista de prontos (O(n)), logo O(n²) no pior caso. Uma heap reduziria isso, mas a lista deixa as regras de desempate mais fáceis de ler e explicar.
- `configuracao` é obrigatória (use `{}`); chaves de outros algoritmos e o campo `peso` são ignorados, como pede o enunciado.

## Testes

`testes.py` verifica:

1. **Referência independente:** 3000 conjuntos aleatórios por algoritmo são comparados com uma simulação unidade de tempo a unidade de tempo (que não usa nenhum atalho do código principal).
2. **Invariantes:** cobertura sem lacunas nem sobreposição, intervalos positivos, CPU recebida igual à pedida, fórmulas das métricas, métricas ordenadas por ID.
3. O exemplo da seção 5.1 do enunciado, CPU ociosa, empate no SRTF e entradas inválidas (via CLI, conferindo `erro` e código de saída).
