# Relatório de Teste A/B — Parceiro B

*Gerado em 14/07/2026 22:58*

- **Período analisado:** 01/05/2011 a 30/06/2011
- **Grupos testados:** Grupo 1, Grupo 2, Grupo 3
- **Grupo controle:** Grupo 1

## Decisão recomendada

### Escalar **Grupo 1** para 100% do tráfego

O grupo controle (Grupo 1) já tem a maior margem total do período. Nenhuma variante testada superou o controle em margem.

## Métricas por variante (período completo)

| grupo | Compradores | GMV (R$) | Cashback (R$) | Comissão (R$) | Margem (R$) | Ticket médio (R$) |
|---|---|---|---|---|---|---|
| Grupo 1 | 7,990.00 | 4,093,818.00 | 163,751.00 | 450,321.00 | 286,570.00 | 512.37 |
| Grupo 2 | 5,452.00 | 2,863,019.00 | 171,778.00 | 314,935.00 | 143,157.00 | 525.13 |
| Grupo 3 | 5,029.00 | 2,629,963.00 | 236,697.00 | 289,290.00 | 52,593.00 | 522.96 |

*Margem = Comissão − Cashback. É o valor que fica pro Méliuz depois de pagar o cashback ao usuário.*

## Significância estatística (vs. grupo controle)

| Grupo | Métrica | Diferença | p-valor | Confiável? |
|---|---|---|---|---|
| Grupo 2 | margem | -50.0% | 1.68e-22 | Sim |
| Grupo 2 | compradores | -31.8% | 7.45e-21 | Sim |
| Grupo 2 | vendas_totais | -30.1% | 1.42e-14 | Sim |
| Grupo 3 | margem | -81.6% | 3.43e-26 | Sim |
| Grupo 3 | compradores | -37.1% | 5.26e-19 | Sim |
| Grupo 3 | vendas_totais | -35.8% | 2.12e-15 | Sim |

*Diferença é considerada confiável quando p-valor < 0.05 (95% de confiança). Diferenças não confiáveis podem ser apenas variação natural entre os dias observados.*
