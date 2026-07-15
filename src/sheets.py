import sys
import csv
from pathlib import Path
from datetime import datetime

from load_data import carregar_csv
from decision_engine import gerar_decisao

CAMINHO_CREDENCIAL = "credentials.json"
CSV_FALLBACK = "reports/acompanhamento_testes.csv"
COLUNAS = ["data_registro", "nome_teste", "descricao", "resultado", "decisao"]


def montar_registro(caminho_csv, grupo_controle=None):
    """Roda a análise completa e monta a linha que vai pra planilha."""
    df = carregar_csv(caminho_csv)
    decisao = gerar_decisao(df, grupo_controle)

    parceiro = df["parceiro"].iloc[0]
    periodo = f"{df['data'].min():%d/%m/%Y} a {df['data'].max():%d/%m/%Y}"
    variantes = ", ".join(sorted(df["grupo"].unique()))

    return {
        "data_registro": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "nome_teste": f"Cashback — {parceiro}",
        "descricao": f"Teste A/B de % de cashback ({variantes}) no {parceiro}, período {periodo}.",
        "resultado": decisao["motivo"],
        "decisao": f"Escalar {decisao['recomendacao']} para 100% do tráfego.",
    }


def _escrever_no_sheets(registro, planilha_id, aba="Testes A/B"):
    """Tenta escrever no Google Sheets. Lança exceção se não conseguir —
    quem chama decide se cai pro CSV."""
    import gspread
    from google.oauth2.service_account import Credentials

    escopo = ["https://www.googleapis.com/auth/spreadsheets"]
    credenciais = Credentials.from_service_account_file(CAMINHO_CREDENCIAL, scopes=escopo)
    cliente = gspread.authorize(credenciais)

    planilha = cliente.open_by_key(planilha_id)
    try:
        pagina = planilha.worksheet(aba)
    except gspread.exceptions.WorksheetNotFound:
        pagina = planilha.add_worksheet(title=aba, rows=1000, cols=len(COLUNAS))
        pagina.append_row(COLUNAS)

    pagina.append_row([registro[c] for c in COLUNAS])


def _escrever_no_csv(registro, caminho=CSV_FALLBACK):
    """Acrescenta uma linha no CSV local de acompanhamento, criando o
    cabeçalho se o arquivo ainda não existir."""
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    arquivo_existe = caminho.exists()

    with open(caminho, "a", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUNAS)
        if not arquivo_existe:
            escritor.writeheader()
        escritor.writerow(registro)

    return caminho


def registrar_teste(caminho_csv, planilha_id=None, grupo_controle=None):
    """
    Roda a análise e registra o resultado. Tenta o Google Sheets primeiro
    (se planilha_id foi passado e existe credentials.json); se não for
    possível, cai automaticamente pro CSV local — nunca falha silenciosamente,
    sempre avisa qual dos dois caminhos foi usado.
    """
    registro = montar_registro(caminho_csv, grupo_controle)

    if planilha_id and Path(CAMINHO_CREDENCIAL).exists():
        try:
            _escrever_no_sheets(registro, planilha_id)
            print(f"Registrado no Google Sheets (planilha {planilha_id}).")
            return "sheets"
        except Exception as e:
            print(f"Não foi possível escrever no Google Sheets ({e}). Usando CSV local.")

    caminho_salvo = _escrever_no_csv(registro)
    print(f"Registrado no CSV local: {caminho_salvo}")
    return "csv"


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: py sheets.py caminho/do/arquivo.csv [id_da_planilha]")
        sys.exit(1)

    caminho_csv = sys.argv[1]
    planilha_id = sys.argv[2] if len(sys.argv) > 2 else None

    registrar_teste(caminho_csv, planilha_id)
