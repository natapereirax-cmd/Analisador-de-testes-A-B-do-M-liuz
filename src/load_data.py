import sys
from pathlib import Path
import pandas as pd

"""Transforma os valores de números em float"""
def parse_moeda(valor):
    if valor is None:  #A função recebe um valor.
        return None    #Se vizer vazio, já desiste


    #garante que a variavel é texto, tira o "R$" e tira o espaço sobrando nas pontas
    texto = str(valor).replace("R$", "").strip()


    #se a variável é um campo de texto vazio
    #ou o campo preenchido é "nan"(.lower() converte as letras para minúsculo)
    #retorna None
    if texto == "" or texto.lower() == "nan":
        return None


    #se o texto possui ",", remove todos os pontos do texto e substitui vírgula por ponto
    #se o texto não possui ",", apenas remove os pontos
    #Resultado: "1.234,56" -->  "1234.56"
    if "," in texto:
        texto = texto.replace(".", "").replace(",", ".")
    else:
        texto = texto.replace(".", "")


    #tenta converter string para float
    try:
        return float(texto)
    except ValueError:
        return None



def carregar_csv(caminho):


    #pega o valor que veio no parâmetro "caminho"(ex: dados/aqruivo.csv) e transforma em um objeto Path
    caminho = Path(caminho)


    #verifica se esse caminho realmente existe no sistema de arquivos
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")


    #lê o arquivo CSV e carrega-lo na memória
    df = pd.read_csv(caminho)


    #renomea as colunas do DataFrame
    df = df.rename(columns={
        "Data" : "data",
        "Grupos de usuários" : "grupo",
        "Parceiro" : "parceiro",
        "compradores" : "compradores",
        "comissão" : "comissao",
        "cashback" : "cashback",
        "vendas totais" : "vendas_totais",
    })


    #retorna o número de linhas que o DataFrame contém
    total_linhas = len(df)


    #conversão de tipos e limpeza de cada coluna do DataFrame
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    df["grupo"] = df["grupo"].astype(str).str.strip()
    df["parceiro"] = df["parceiro"].astype(str).str.strip()
    df["compradores"] = pd.to_numeric(df["compradores"], errors="coerce")
    df["comissao"] = df["comissao"].apply(parse_moeda)
    df["cashback"] = df["cashback"].apply(parse_moeda)
    df["vendas_totais"] = df["vendas_totais"].apply(parse_moeda)


    #lista que contém strings, e cada string é o nome  de uma coluna do DataFrame
    colunas_numericas = ["compradores", "comissao", "cashback", "vendas_totais"]


    #constrói uma máscara booleana (uma série de True/False, uma por linha)
    #que indica se cada linha do DataFrame é considerada "válida" ou não
    linha_valida = (
        df["data"].notna()
        & df["grupo"].ne("")
        & df["grupo"].ne("nan")
        & df[colunas_numericas].notna().all(axis=1)
        & (df[colunas_numericas] >= 0).all(axis=1)
    )


    #filtra o DataFrame mantendo só as linhas onde a máscara é True
    #remove linhas que tenham a mesma combinação de data + grupo + parceiro
    df = df[linha_valida].drop_duplicates(subset=["data", "grupo", "parceiro"])


    #calcula quantas linhas foram descartadas
    linhas_removidas = total_linhas - len(df)


    #se depois de todos os filtros o DataFrame ficou sem nenhuma linha
    #interrompe a excução e lança um erro
    if df.empty:
        raise ValueError("Nenhuma linha válida sobrou depois da limpeza.")


    #imprime um resumo do processamento
    print(f"Linhas lidas: {total_linhas} | Válidas: {len(df)} | Removidas: {linhas_removidas}")

    #Pega os valores únicos da coluna grupo com .unique(), ordena com sorted() e imprime,
    # mostrando quais grupos distintos existem no DataFrame já limpo.
    print(f"Grupos encontrados: {sorted(df['grupo'].unique())}")


    #ordena o DataFrame pelas colunas "grupo" e "data"
    #reconstrói o índice do DataFrame de forma sequencial
    return df.sort_values(["grupo", "data"]).reset_index(drop=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py src/load_data.py data/dataset_01_parceiroA.csv")
        sys.exit(1)
 
    df = carregar_csv(sys.argv[1])
    print(df.head(10))