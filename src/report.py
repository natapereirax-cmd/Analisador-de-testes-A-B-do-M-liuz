import sys
from pathlib import Path
from datetime import datetime

from load_data import carregar_csv
from compute_metrics import metricas_agregadas
from ab_test import comparar_todos_contra_controle
from decision_engine import gerar_decisao


def _tabela_markdown(df_num, colunas, nomes_exibicao):
    #converte um DataFrame numérico numa tabela Markdown simples
    linhas = ["| grupo | " + " | ".join(nomes_exibicao) + " |"]
    linhas.append("|" + "---|" * (len(colunas) + 1))
    for grupo, linha in df_num.iterrows():
        valores = " | ".join(f"{linha[c]:,.2f}" for c in colunas)
        linhas.append(f"| {grupo} | {valores} |")
    return "\n".join(linhas)


def gerar_relatorio_markdown(caminho_csv):
    df = carregar_csv(caminho_csv)
    parceiro = df["parceiro"].iloc[0]
    periodo_inicio = df["data"].min().strftime("%d/%m/%Y")
    periodo_fim = df["data"].max().strftime("%d/%m/%Y")
    grupos = sorted(df["grupo"].unique())

    decisao = gerar_decisao(df)
    metricas = decisao["metricas"]
    controle = decisao["grupo_controle"]

    testes = comparar_todos_contra_controle(df, controle, metricas=("margem", "compradores", "vendas_totais"))

    linhas = []
    linhas.append(f"# Relatório de Teste A/B — {parceiro}")
    linhas.append("")
    linhas.append(f"*Gerado em {datetime.now().strftime('%d/%m/%Y %H:%M')}*")
    linhas.append("")
    linhas.append(f"- **Período analisado:** {periodo_inicio} a {periodo_fim}")
    linhas.append(f"- **Grupos testados:** {', '.join(grupos)}")
    linhas.append(f"- **Grupo controle:** {controle}")
    linhas.append("")

    linhas.append("## Decisão recomendada")
    linhas.append("")
    linhas.append(f"### Escalar **{decisao['recomendacao']}** para 100% do tráfego")
    linhas.append("")
    linhas.append(decisao["motivo"])
    linhas.append("")

    linhas.append("## Métricas por variante (período completo)")
    linhas.append("")
    linhas.append(_tabela_markdown(
        metricas,
        ["compradores", "vendas_totais", "cashback", "comissao", "margem", "ticket_medio"],
        ["Compradores", "GMV (R$)", "Cashback (R$)", "Comissão (R$)", "Margem (R$)", "Ticket médio (R$)"],
    ))
    linhas.append("")
    linhas.append(
        "*Margem = Comissão − Cashback. É o valor que fica pro Méliuz depois de pagar o cashback ao usuário.*"
    )
    linhas.append("")

    linhas.append("## Significância estatística (vs. grupo controle)")
    linhas.append("")
    linhas.append("| Grupo | Métrica | Diferença | p-valor | Confiável? |")
    linhas.append("|---|---|---|---|---|")
    for t in testes:
        veredito = "Sim" if t["significativo_95pct"] else "Não (pode ser ruído)"
        linhas.append(
            f"| {t['grupo_comparado']} | {t['metrica']} | {t['diferenca_pct']:+.1f}% | {t['p_valor']} | {veredito} |"
        )
    linhas.append("")
    linhas.append(
        "*Diferença é considerada confiável quando p-valor < 0.05 (95% de confiança). "
        "Diferenças não confiáveis podem ser apenas variação natural entre os dias observados.*"
    )
    linhas.append("")

    alertas = []
    if (metricas["margem"] <= 0).any():
        grupos_zerados = metricas[metricas["margem"] <= 0].index.tolist()
        alertas.append(f"⚠️ Margem zerada ou negativa em: {', '.join(grupos_zerados)}.")

    if alertas:
        linhas.append("## Alertas")
        linhas.append("")
        linhas.extend(alertas)
        linhas.append("")

    return "\n".join(linhas)


def salvar_relatorio(caminho_csv, pasta_saida="reports"):
    conteudo = gerar_relatorio_markdown(caminho_csv)

    nome_arquivo = Path(caminho_csv).stem  # ex: dataset_01_parceiroA
    pasta_saida = Path(pasta_saida)
    pasta_saida.mkdir(parents=True, exist_ok=True)

    caminho_saida = pasta_saida / f"relatorio_{nome_arquivo}.md"
    caminho_saida.write_text(conteudo, encoding="utf-8")

    return caminho_saida


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: py report.py caminho/do/arquivo.csv")
        sys.exit(1)

    caminho_saida = salvar_relatorio(sys.argv[1])
    print(f"\nRelatório salvo em: {caminho_saida}")
