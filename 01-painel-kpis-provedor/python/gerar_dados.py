"""Gera a base sintética do ProvedorX (provedor de internet fibra fictício).

Tudo aqui é inventado: nomes de cidades, clientes, planos e números.
Rode com: python gerar_dados.py
Saída: CSVs e um Excel em ../dados/
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
OUT = Path(__file__).resolve().parent.parent / "dados"
OUT.mkdir(exist_ok=True)

INICIO = pd.Timestamp("2026-01-01")
FIM = pd.Timestamp("2026-12-31")
N_CLIENTES = 4000

# ---------- Planos ----------
planos = pd.DataFrame({
    "id_plano": [1, 2, 3, 4, 5],
    "plano": ["Fibra 300", "Fibra 500", "Fibra 700", "Fibra 1 Giga", "Empresarial 600"],
    "velocidade_mbps": [300, 500, 700, 1000, 600],
    "mensalidade": [89.90, 109.90, 129.90, 159.90, 199.90],
    "tipo": ["Residencial", "Residencial", "Residencial", "Residencial", "Empresarial"],
})
peso_plano = [0.30, 0.32, 0.20, 0.10, 0.08]

# ---------- Cidades (fictícias) ----------
cidades = pd.DataFrame({
    "id_cidade": [1, 2, 3, 4, 5, 6],
    "cidade": ["Vila Aurora", "Campo Sereno", "Porto Alecrim", "Serra Azul do Norte", "Lago Dourado", "Nova Esperança do Vale"],
    "regiao": ["Centro", "Centro", "Leste", "Norte", "Sul", "Norte"],
})
peso_cidade = [0.30, 0.22, 0.16, 0.12, 0.12, 0.08]

# ---------- Clientes ----------
dias_base = (FIM - pd.Timestamp("2023-01-01")).days
ativacao = pd.Timestamp("2023-01-01") + pd.to_timedelta(rng.integers(0, dias_base - 30, N_CLIENTES), unit="D")
clientes = pd.DataFrame({
    "id_cliente": np.arange(1, N_CLIENTES + 1),
    "id_plano": rng.choice(planos.id_plano, N_CLIENTES, p=peso_plano),
    "id_cidade": rng.choice(cidades.id_cidade, N_CLIENTES, p=peso_cidade),
    "data_ativacao": ativacao.normalize(),
    "canal_venda": rng.choice(["Loja", "Vendedor externo", "Site", "WhatsApp"], N_CLIENTES, p=[0.25, 0.35, 0.15, 0.25]),
    "fidelidade_meses": rng.choice([0, 12], N_CLIENTES, p=[0.35, 0.65]),
})

# ---------- Chamados ----------
motivos = ["Sem conexão", "Lentidão", "Wi-Fi instável", "Financeiro", "Mudança de endereço", "Troca de plano", "Equipamento com defeito"]
peso_motivo = [0.26, 0.22, 0.18, 0.12, 0.07, 0.07, 0.08]
sla_horas = {"Sem conexão": 8, "Lentidão": 24, "Wi-Fi instável": 24, "Financeiro": 48,
             "Mudança de endereço": 72, "Troca de plano": 48, "Equipamento com defeito": 24}
# cidades com rede mais antiga geram mais chamados (para o painel mostrar algo)
fator_cidade = {1: 1.0, 2: 0.9, 3: 1.1, 4: 1.6, 5: 1.0, 6: 1.3}

linhas = []
id_ch = 1
for c in clientes.itertuples():
    taxa = 3.0 * fator_cidade[c.id_cidade]  # chamados por ano, em média
    n = rng.poisson(taxa)
    for _ in range(n):
        abertura = INICIO + pd.Timedelta(minutes=int(rng.integers(0, 365 * 24 * 60)))
        if abertura < c.data_ativacao:
            continue
        motivo = rng.choice(motivos, p=peso_motivo)
        canal = rng.choice(["Telefone", "WhatsApp", "App", "Chat do site"], p=[0.35, 0.40, 0.15, 0.10])
        nivel = "N2" if motivo in ("Sem conexão", "Equipamento com defeito") and rng.random() < 0.45 else "N1"
        visita = motivo in ("Sem conexão", "Equipamento com defeito", "Mudança de endereço") and rng.random() < 0.55
        turno = "Noite" if abertura.hour >= 18 or abertura.hour < 6 else ("Manhã" if abertura.hour < 12 else "Tarde")
        base_h = rng.gamma(2.0, sla_horas[motivo] / 4.2)
        if visita:
            base_h += rng.gamma(2.0, 3)
        if c.id_cidade == 4:
            base_h *= 1.35
        resolucao_h = round(float(base_h), 1)
        tma_min = round(float(rng.gamma(3.0, 4.0 if canal != "App" else 2.5)), 1)
        linhas.append({
            "id_chamado": id_ch,
            "id_cliente": c.id_cliente,
            "data_abertura": abertura,
            "motivo": motivo,
            "canal": canal,
            "nivel": nivel,
            "turno": turno,
            "precisou_visita": "Sim" if visita else "Não",
            "tempo_atendimento_min": tma_min,
            "tempo_resolucao_horas": resolucao_h,
            "sla_horas": sla_horas[motivo],
            "dentro_sla": "Sim" if resolucao_h <= sla_horas[motivo] else "Não",
        })
        id_ch += 1
chamados = pd.DataFrame(linhas).sort_values("data_abertura").reset_index(drop=True)
chamados["id_chamado"] = np.arange(1, len(chamados) + 1)

# ---------- Cancelamentos ----------
# risco maior para quem abre muitos chamados, está sem fidelidade e mora na cidade com rede antiga
qtd = chamados.groupby("id_cliente").size().reindex(clientes.id_cliente, fill_value=0).values
fora_sla = chamados[chamados.dentro_sla == "Não"].groupby("id_cliente").size().reindex(clientes.id_cliente, fill_value=0).values
risco = 0.12 + 0.03 * qtd + 0.06 * fora_sla + np.where(clientes.fidelidade_meses == 0, 0.08, 0) + np.where(clientes.id_cidade == 4, 0.05, 0)
cancelou = rng.random(N_CLIENTES) < np.clip(risco, 0, 0.85) * 0.55
motivos_canc = ["Instabilidade na conexão", "Preço", "Mudança de cidade", "Atendimento", "Concorrente com oferta melhor"]
data_canc = []
motivo_canc = []
for c, sim in zip(clientes.itertuples(), cancelou):
    if not sim:
        data_canc.append(pd.NaT); motivo_canc.append(None); continue
    ini = max(INICIO, c.data_ativacao + pd.Timedelta(days=30))
    dias = (FIM - ini).days
    if dias <= 0:
        data_canc.append(pd.NaT); motivo_canc.append(None); continue
    data_canc.append((ini + pd.Timedelta(days=int(rng.integers(0, dias)))).normalize())
    motivo_canc.append(rng.choice(motivos_canc, p=[0.32, 0.25, 0.15, 0.13, 0.15]))
clientes["data_cancelamento"] = data_canc
clientes["motivo_cancelamento"] = motivo_canc
clientes["status"] = np.where(clientes.data_cancelamento.notna(), "Cancelado", "Ativo")

# remove chamados abertos depois do cancelamento
chamados = chamados.merge(clientes[["id_cliente", "data_cancelamento"]], on="id_cliente", how="left")
chamados = chamados[chamados.data_cancelamento.isna() | (chamados.data_abertura <= chamados.data_cancelamento)]
chamados = chamados.drop(columns="data_cancelamento").reset_index(drop=True)
chamados["id_chamado"] = np.arange(1, len(chamados) + 1)

# ---------- Pesquisa NPS ----------
amostra = chamados.sample(frac=0.30, random_state=SEED)
notas = []
for ch in amostra.itertuples():
    media = 9.2
    if ch.dentro_sla == "Não":
        media -= 2.8
    if ch.precisou_visita == "Sim":
        media -= 0.4
    notas.append(int(np.clip(round(rng.normal(media, 1.3)), 0, 10)))
nps = pd.DataFrame({
    "id_resposta": np.arange(1, len(amostra) + 1),
    "id_chamado": amostra.id_chamado.values,
    "id_cliente": amostra.id_cliente.values,
    "data_resposta": (amostra.data_abertura + pd.to_timedelta(rng.integers(1, 4, len(amostra)), unit="D")).dt.normalize().values,
    "nota": notas,
})
nps["categoria"] = pd.cut(nps.nota, bins=[-1, 6, 8, 10], labels=["Detrator", "Neutro", "Promotor"]).astype(str)
nps = nps.sort_values("data_resposta").reset_index(drop=True)
nps["id_resposta"] = np.arange(1, len(nps) + 1)

# ---------- Salvar ----------
chamados["data_abertura"] = chamados.data_abertura.dt.strftime("%Y-%m-%d %H:%M")
for nome, df in [("planos", planos), ("cidades", cidades), ("clientes", clientes), ("chamados", chamados), ("nps", nps)]:
    df.to_csv(OUT / f"{nome}.csv", index=False, encoding="utf-8-sig", sep=";", decimal=",")

with pd.ExcelWriter(OUT / "provedorx_base_2026.xlsx", engine="openpyxl") as xw:
    for nome, df in [("clientes", clientes), ("planos", planos), ("cidades", cidades), ("chamados", chamados), ("nps", nps)]:
        df.to_excel(xw, sheet_name=nome, index=False)

# ---------- Resumo para conferência ----------
ativos_ini = ((clientes.data_ativacao < INICIO) & (clientes.data_cancelamento.isna() | (clientes.data_cancelamento >= INICIO))).sum()
canc_2026 = clientes.data_cancelamento.between(INICIO, FIM).sum()
nps_score = (nps.categoria.eq("Promotor").mean() - nps.categoria.eq("Detrator").mean()) * 100
print(f"Clientes: {len(clientes)} | ativos em 01/01/2026: {ativos_ini} | cancelados em 2026: {canc_2026}")
print(f"Chamados: {len(chamados)} | dentro do SLA: {chamados.dentro_sla.eq('Sim').mean():.1%}")
print(f"TMA médio: {chamados.tempo_atendimento_min.mean():.1f} min | NPS: {nps_score:.0f} ({len(nps)} respostas)")
