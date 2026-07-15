import sys
from load_data import carregar_csv


def metricas_diarias(df):

    #recebe o DataFrame e seleciona as colunas: data, grupo, compradores, comissao, cashback e vendas_totais
    #usa .copy() para retornar uma cópia independente desse subconjunto
    return df[["data", "grupo", "compradores", "comissao", "cashback", "vendas_totais"]].copy()


def metricas_agregadas(df, grupo_controle=None):

    #df.groupby("grupo") agrupa as linhas do DataFrame pelos valores da coluna "grupo"
    #["data"].nunique() conta, para cada grupo, quantos valores únicos existem na coluna "data"
    dias_por_grupo = df.groupby("grupo")["data"].nunique()


    #Agrupa o DataFrame por "grupo" e calcula agregações para cada grupo
    resumo = df.groupby("grupo").agg(
        compradores=("compradores", "sum"),
        comissao=("comissao", "sum"),
        cashback=("cashback", "sum"),
        vendas_totais=("vendas_totais", "sum"),
    )


    #adiciona uma nova coluna "dias", atribuindo a Series calculada antes
    resumo["dias"] = dias_por_grupo


    #criam colunas calculadas a partir das já existentes, linha a linha
    resumo["margem"] = resumo["comissao"] - resumo["cashback"]
    resumo["ticket_medio"] = resumo["vendas_totais"] / resumo["compradores"]
    resumo["compradores_por_dia"] = resumo["compradores"] / resumo["dias"]


    #se "grupo_controle" é 'None', define automaticamente como grupo de controle
    # o primeiro em ordem alfabética/numérica dentre os índices de 'resumo'
    if grupo_controle is None:
        grupo_controle = sorted(resumo.index)[0]


    #verifica se o valor de "grupo_controle" está entre os grupos existentes em 'resumo.index'
    #se não estiver, interrompe a execução e lança um erro
    if grupo_controle not in resumo.index:
        raise ValueError(f"Grupo controle '{grupo_controle}' não existe nos dados.")

    #pega o valor específico de "compradores por dia" referente ao grupo de controle
    # e guarda em "compradores_controle_dia"
    compradores_controle_dia = resumo.loc[grupo_controle, "compradores_por_dia"]


    #cria uma lista vazia que vai acumular resultados
    cac_incremental = []

    #um 'for' percorre cada 'grupo' presente no índice de 'resumo'
    for grupo in resumo.index:

        #se o 'grupo' atual for igual ao 'grupo_controle',
        # adiciona 'None' na lista e 'continue' pula para a próxima iteração do loop, sem executar o restante do código do 'for'
        if grupo == grupo_controle:
            cac_incremental.append(None)
            continue


        #calcula a diferença entre os compradores por dia daquele grupo e os compradores por dia do grupo controle
        incremento_dia = resumo.loc[grupo, "compradores_por_dia"] - compradores_controle_dia

        #multiplica o incremento pelo número de dias daquele grupo, estimando o total de compradores incrementais no período todo
        incremento_total = incremento_dia * resumo.loc[grupo, "dias"]


        #se 'incremento_total' for zero ou negativo adiciona 'None' na lista
        if incremento_total <= 0:
            cac_incremental.append(None)

        #calcula o CAC incremental daquele grupo: pega o 'cashback' total do grupo e divide pelo 'incremento_total' de compradores
        else:
            cac_incremental.append(resumo.loc[grupo, "cashback"] / incremento_total)

    #adiciona a lista calculada no loop como uma nova coluna do DataFrame 'resumo'
    resumo["cac_incremental"] = cac_incremental

    #cria outra coluna, preenchendo todas as linhas com o mesmo valor: o nome do grupo que foi usado como controle
    resumo["grupo_controle"] = grupo_controle

    #retorna o DataGrame 'resumo', mas antes arredonda todos os valores numéricos para 2 casas decimais
    return resumo.round(2)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py compute_metrics.py caminho/do/arquivo.csv")
        sys.exit(1)

    df = carregar_csv(sys.argv[1])

    print("\n--- Métricas agregadas (período inteiro) ---")
    print(metricas_agregadas(df))

    print("\n--- Métricas diárias (amostra) ---")
    print(metricas_diarias(df).head(5))
