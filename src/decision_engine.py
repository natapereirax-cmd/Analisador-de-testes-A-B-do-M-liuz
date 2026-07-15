import sys
from load_data import carregar_csv
from compute_metrics import metricas_agregadas
from ab_test import comparar_todos_contra_controle


def gerar_decisao(df, grupo_controle=None):
    """
    Decide qual variante escalar pra 100% do tráfego.

    Regra de negócio (nessa ordem):
    1. Margem (comissão - cashback) mais volume de venda não importa se a
       margem cai.
    2. Só recomenda escalar uma variante diferente do controle se a margem
       maior dela for estatisticamente significativa (não pode ser ruído).
    3. Se nenhuma variante bate o controle em margem de forma confiável,
       a recomendação é manter o controle.
    """


    #chama metricas_agregadas(df, grupo_controle) e guarda o resultado (o DataFrame com as métricas por grupo)
    metricas = metricas_agregadas(df, grupo_controle)


    #pega o valor da primeira linha da coluna 'grupo_controle'
    controle = metricas["grupo_controle"].iloc[0]


    #chama 'comparar_todos_contra_controle', comparando o grupo 'controle' contra os outros grupos,
    #nas métricas 'margem', 'compradores' e vendas_totais'
    testes = comparar_todos_contra_controle(
        df, controle, metricas=("margem", "compradores", "vendas_totais")
    )


    #transforma essa lista num dicionario
    testes_idx = {(t["grupo_comparado"], t["metrica"]): t for t in testes}


    #usa '.idxmax()' na coluna 'margem' de 'metricas', retornando o nome do índice
    melhor_em_margem = metricas["margem"].idxmax()


    """
    Se o grupo com maior margem já é o próprio controle, não tem o que decidir (Logo, 'recomendacao' recebe o próprio 'controle',
    e 'motivo' explica que nenhuma variante superou ele)
    """
    if melhor_em_margem == controle:
        recomendacao = controle
        motivo = (
            f"O grupo controle ({controle}) já tem a maior margem total do período. "
            f"Nenhuma variante testada superou o controle em margem."
        )

    #o melhor é outra variante, diferente do controle
    else:

        #busca no dicionário 'testes_idx' o resultado do teste estatístico específico do grupo 'melhor_em_margem' na métrica 'margem'
        teste_margem = testes_idx[(melhor_em_margem, "margem")]

        """
        checa duas condições ao mesmo tempo: o resultado é estatisticamente significativo 'significativo_95pct'
        e a diferença de média é positiva 'diferenca_media_dia > 0', confirmando que a variante é realmente melhor
        """
        ganhou_de_verdade = teste_margem["significativo_95pct"] and teste_margem["diferenca_media_dia"] > 0


        #se sim, recomenda escalar essa variante
        if ganhou_de_verdade:
            recomendacao = melhor_em_margem
            motivo = (
                f"{melhor_em_margem} tem a maior margem total do período, e a diferença "
                f"frente ao controle ({controle}) é estatisticamente significativa "
                f"(p={teste_margem['p_valor']}) — não é coincidência dos dias observados."
            )

            """
            se não, 'recomendacao' mantém o 'controle', e 'motivo' explica que apesar
            da margem numérica maior, não há evidência estatística suficiente para trocar
            """
        else:
            recomendacao = controle
            motivo = (
                f"{melhor_em_margem} teve margem numericamente maior que o controle, mas a "
                f"diferença não é estatisticamente significativa (p={teste_margem['p_valor']}). "
                f"Não há evidência suficiente pra escalar — mantenha o controle ({controle})."
            )

    # contexto adicional: mesmo não sendo o critério de decisão, o time de
    # growth precisa ver o trade-off de volume x margem pra cada variante


    #lista vazia pra acumular esse resumo por grupo
    contexto = []

    #percorre cada grupo. Se for o próprio 'controle', pula com 'continue'
    for grupo in metricas.index:
        if grupo == controle:
            continue

        #buscam no 'testes_idx' os resultados do teste estatístico daquele grupo nas métricas 'margem' e 'compradores'
        t_margem = testes_idx[(grupo, "margem")]
        t_compradores = testes_idx[(grupo, "compradores")]


        #adiciona um dicionário com três informações:
        #nome do grupo
        #diferença percentual de margem, o p-valor, e se é significativo 'sig.' ou não 'não sig.'
        #métrica de compradores
        contexto.append({
            "grupo": grupo,
            "margem_vs_controle": f"{t_margem['diferenca_pct']:+.1f}% (p={t_margem['p_valor']}, {'sig.' if t_margem['significativo_95pct'] else 'não sig.'})",
            "compradores_vs_controle": f"{t_compradores['diferenca_pct']:+.1f}% (p={t_compradores['p_valor']}, {'sig.' if t_compradores['significativo_95pct'] else 'não sig.'})",
        })

    return {
        "grupo_controle": controle,
        "recomendacao": recomendacao,
        "motivo": motivo,
        "metricas": metricas,
        "contexto_trade_off": contexto,
    }


"""
Essa função pega tudo que foi calculado e apresenta
de forma legível
"""
def imprimir_decisao(decisao):
    print("=" * 60)
    print(f"DECISÃO: escalar '{decisao['recomendacao']}' para 100% do tráfego")
    print("=" * 60)
    print(f"\nMotivo: {decisao['motivo']}\n")

    print("--- Métricas por grupo (período inteiro) ---")
    print(decisao["metricas"][["compradores", "vendas_totais", "cashback", "comissao", "margem"]])

    if decisao["contexto_trade_off"]:
        print("\n--- Trade-off volume x margem (vs. controle) ---")
        for c in decisao["contexto_trade_off"]:
            print(f"{c['grupo']}: margem {c['margem_vs_controle']} | compradores {c['compradores_vs_controle']}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py decision_engine.py caminho/do/arquivo.csv")
        sys.exit(1)

    df = carregar_csv(sys.argv[1])
    decisao = gerar_decisao(df)
    print()
    imprimir_decisao(decisao)
