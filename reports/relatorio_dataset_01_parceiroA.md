# Relatório de Teste A/B — Parceiro A

*Gerado em 14/07/2026 22:57*

- **Período analisado:** 01/01/2011 a 02/04/2011
- **Grupos testados:** Grupo 1, Grupo 2, Grupo 3
- **Grupo controle:** Grupo 1

## Decisão recomendada

### Escalar **Grupo 1** para 100% do tráfego

O grupo controle (Grupo 1) já tem a maior margem total do período. Nenhuma variante testada superou o controle em margem.

## Métricas por variante (período completo)

| grupo | Compradores | GMV (R$) | Cashback (R$) | Comissão (R$) | Margem (R$) | Ticket médio (R$) |
|---|---|---|---|---|---|---|
| Grupo 1 | 9,633.00 | 5,605,173.00 | 233,424.00 | 638,135.00 | 404,711.00 | 581.87 |
| Grupo 2 | 10,814.00 | 6,423,096.00 | 370,659.00 | 728,178.00 | 357,519.00 | 593.96 |
| Grupo 3 | 11,410.00 | 6,785,856.00 | 503,600.00 | 767,887.00 | 264,287.00 | 594.73 |

*Margem = Comissão − Cashback. É o valor que fica pro Méliuz depois de pagar o cashback ao usuário.*

## Significância estatística (vs. grupo controle)

| Grupo | Métrica | Diferença | p-valor | Confiável? |
|---|---|---|---|---|
| Grupo 2 | margem | -11.7% | 2.78e-05 | Sim |
| Grupo 2 | compradores | +12.3% | 9.45e-10 | Sim |
| Grupo 2 | vendas_totais | +14.6% | 1.06e-05 | Sim |
| Grupo 3 | margem | -34.7% | 1.52e-11 | Sim |
| Grupo 3 | compradores | +18.4% | 4.39e-11 | Sim |
| Grupo 3 | vendas_totais | +21.1% | 1.21e-07 | Sim |

*Diferença é considerada confiável quando p-valor < 0.05 (95% de confiança). Diferenças não confiáveis podem ser apenas variação natural entre os dias observados.*
