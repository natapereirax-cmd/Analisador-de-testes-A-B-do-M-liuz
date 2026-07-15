import sys
from scipy import stats
from load_data import carregar_csv

ALPHA = 0.05  # nível de significância padrão (95% de confiança)

"""A função '_serie_diaria'(o underscore no início é uma convenção
indicando que é uma função 'privada'/de uso interno do módulo), recebndo o DataFrame, 
o nome de um 'grupo' e uma 'metrica'.
"""
def _serie_diaria(df, grupo, metrica):

    #filtra apenas as linhas daquele grupo específico e ordena por data
    dados = df[df["grupo"] == grupo].sort_values("data")

    #se 'metrica' for a string 'margem', retorna a diferença entre 'comissao' e cashback'
    if metrica == "margem":
        return dados.set_index("data")["comissao"] - dados.set_index("data")["cashback"]

    #se 'metrica' for qualquer outro nome, retorna diretamente essa coluna, também indexada por 'data'.
    return dados.set_index("data")[metrica]


"""A função 'comparar_grupos' recebe o DataFrme, grupo A e B, 
e uma metrica(valor padrão 'margem' caso não seja informada)"""
def comparar_grupos(df, grupo_a, grupo_b, metrica="margem"):

    #chama a função '_serie_diaria' para pegar a série temporal da métrica escolhida referente ao grupo A
    serie_a = _serie_diaria(df, grupo_a, metrica)

    #chama a função '_serie_diaria' para pegar a série temporal da métrica escolhida referente ao grupo A
    serie_b = _serie_diaria(df, grupo_b, metrica)


    #o conjunto de dias em que tanto o grupo A quanto o B tem registro    
    datas_em_comum = serie_a.index.intersection(serie_b.index)


    #verifica se as duas séries tem exatamente as mesmas datas
    pareado = len(datas_em_comum) == len(serie_a) == len(serie_b)


    """
    Se 'pareado' for verdadeiro (mesmas datas nos dois grupos): A e B recebem valores
    das séries filtrados apenas pelas 'datas_em_comum'. Depois, 'stats.ttest_rel(b, a)'
    executa um teste t pareado, comparando as duas séries observação por observação.
    """
    if pareado:
        a = serie_a.loc[datas_em_comum]
        b = serie_b.loc[datas_em_comum]

        #Retorna a estatística do teste e o 'p_valor'
        estatistica, p_valor = stats.ttest_rel(b, a)

        #guarda a string 'pareado' como registro de qual teste foi usado
        tipo_teste = "pareado"

        """
        Se 'pareado' for False, A e B recebem a séries completas, sem filtrar por data
        em comum
        """
    else:
        a = serie_a
        b = serie_b
        estatistica, p_valor = stats.ttest_ind(b, a, equal_var=False)
        tipo_teste = "independente (Welch)"


    #calculam a média dos valores em cada série (A e B)
    media_a = a.mean()
    media_b = b.mean()

    #calcula a diferença das duas médias
    diferenca_media = media_b - media_a

    #calcula essa diferença média em termos percentuais, relativa à média do grupo A
    #só executa a divisão se a média A for diferente de 0
    # Caso a média A seja 0, atrbui float("nan")
    diferenca_pct = (diferenca_media / media_a * 100) if media_a != 0 else float("nan")


    #compara o 'p_valor' obtido no teste estatístico com uma constante ALPHA
    #se o 'p_valor' for menor que ALPHA, considera-se o resultado estaticamente significativo, recebendo True
    significativo = p_valor < ALPHA

    #formata o 'p_valor' para exibição
    #se 'p_valor' for muito pequeno, usa notação científica. Se não, arredonda para 4 casas decimais
    p_valor_exibicao = f"{p_valor:.2e}" if p_valor < 0.0001 else round(p_valor, 4)


    #retorna um dicionário consolidando todos os resultados da comparação entre os dois grupos
    return {
        "grupo_base": grupo_a,
        "grupo_comparado": grupo_b,
        "metrica": metrica,
        "tipo_teste": tipo_teste,
        "media_base": round(media_a, 2),
        "media_comparado": round(media_b, 2),
        "diferenca_media_dia": round(diferenca_media, 2),
        "diferenca_pct": round(diferenca_pct, 1),
        "p_valor": p_valor_exibicao,
        "significativo_95pct": significativo,
    }


#define a função 'comparar_todos_contra_controle, recebendo o DataFrame, 
# um 'grupo_controle e uma tupla 'metrica' com valores padrão ('margem', 'compradores', 'vendas_totais)
def comparar_todos_contra_controle(df, grupo_controle=None, metricas=("margem", "compradores", "vendas_totais")):
    """Roda comparar_grupos do grupo controle contra cada outro grupo, em várias métricas."""


    #pega os valores únicos da coluna 'grupo' com '.unique()' e ordena com 'sorted()'
    grupos = sorted(df["grupo"].unique())

    if grupo_controle is None:
        grupo_controle = grupos[0]


    #lista vazia de 'resultados'
    resultados = []

    #percorre cada 'grupo' na lista 'grupos'
    for grupo in grupos:

        #se o grupo atual for igual ao 'grupo_controle', pula essa interação com 'continue'
        if grupo == grupo_controle:
            continue

        #percorre cada 'metrica' na tupla 'metricas' recebida pela função
        #em cada volta, chama 'comparar_grupos'
        for metrica in metricas:
            resultados.append(comparar_grupos(df, grupo_controle, grupo, metrica))


    #devolve a lista completa com todos os dicionários de comparação gerados
    # um para cada combinação de grupo x métrica
    return resultados


#função que recebe uma lista 'resultados'
def _imprimir_resultados(resultados):

    #percorre cada dicionário 'r' da lista
    for r in resultados:
        veredito = "SIGNIFICATIVO" if r["significativo_95pct"] else "não significativo (pode ser ruído)"
        print(
            f"[{r['metrica']}] {r['grupo_base']} vs {r['grupo_comparado']} "
            f"({r['tipo_teste']}): {r['diferenca_pct']:+.1f}% "
            f"(p={r['p_valor']}) -> {veredito}"
        )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py ab_test.py caminho/do/arquivo.csv")
        sys.exit(1)

    df = carregar_csv(sys.argv[1])
    resultados = comparar_todos_contra_controle(df)
    print()
    _imprimir_resultados(resultados)
