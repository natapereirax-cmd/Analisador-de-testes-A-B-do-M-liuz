# Relatório de Teste A/B — Parceiro C

*Gerado em 14/07/2026 22:59*

- **Período analisado:** 01/07/2011 a 14/08/2011
- **Grupos testados:** Grupo 1, Grupo 2
- **Grupo controle:** Grupo 1

## Decisão recomendada

### Escalar **Grupo 1** para 100% do tráfego

O grupo controle (Grupo 1) já tem a maior margem total do período. Nenhuma variante testada superou o controle em margem.

## Métricas por variante (período completo)

| grupo | Compradores | GMV (R$) | Cashback (R$) | Comissão (R$) | Margem (R$) | Ticket médio (R$) |
|---|---|---|---|---|---|---|
| Grupo 1 | 4,549.00 | 1,738,460.00 | 86,924.00 | 121,693.00 | 34,769.00 | 382.16 |
| Grupo 2 | 4,522.00 | 1,685,235.00 | 117,967.00 | 117,967.00 | 0.00 | 372.67 |

*Margem = Comissão − Cashback. É o valor que fica pro Méliuz depois de pagar o cashback ao usuário.*

## Significância estatística (vs. grupo controle)

| Grupo | Métrica | Diferença | p-valor | Confiável? |
|---|---|---|---|---|
| Grupo 2 | margem | -100.0% | 2.60e-28 | Sim |
| Grupo 2 | compradores | -0.6% | 0.9052 | Não (pode ser ruído) |
| Grupo 2 | vendas_totais | -3.1% | 0.5803 | Não (pode ser ruído) |

*Diferença é considerada confiável quando p-valor < 0.05 (95% de confiança). Diferenças não confiáveis podem ser apenas variação natural entre os dias observados.*

## Alertas

⚠️ Margem zerada ou negativa em: Grupo 2.
