# Projeto 1: Painel de KPIs de um provedor fictício

Painel de indicadores do suporte e da base de clientes do **ProvedorX**, um provedor de internet fibra fictício.

## Pergunta de negócio

Como está a saúde do atendimento e da base de clientes do ProvedorX, e onde agir primeiro para reduzir o cancelamento?

## Indicadores

- **Churn mensal:** clientes que cancelaram no mês divididos pela base ativa no início do mês.
- **SLA de atendimento:** percentual de chamados resolvidos dentro do prazo combinado.
- **NPS:** percentual de promotores menos percentual de detratores.
- **Tempo médio de atendimento (TMA):** duração média dos chamados.
- **Chamados por 1.000 clientes:** volume de suporte em relação ao tamanho da base.
- **Reincidência:** clientes com mais de um chamado sobre o mesmo motivo em 30 dias.

## Etapas e ferramentas

1. **Dados (Python):** gerar uma base sintética de clientes, chamados e pesquisas de NPS em `python/`.
2. **Excel:** primeira análise e tabelas dinâmicas, para validar os números.
3. **SQL:** modelo dimensional (fatos de chamados e cancelamentos, dimensões de cliente, plano, cidade e data) e consultas dos KPIs em `sql/`.
4. **Power BI:** painel com visão geral, atendimento, churn e NPS, em `powerbi/`.
5. **Conclusões:** três recomendações para a diretoria do ProvedorX em `docs/`.

## Estrutura

- `dados/` bases sintéticas em CSV
- `python/` script que gera os dados
- `sql/` modelo e consultas
- `powerbi/` arquivo do painel e imagens
- `docs/` conclusões e aprendizados

## Status

- [x] Gerar dados sintéticos (dados/provedorx_base_2026.xlsx e CSVs)
- [ ] Análise inicial no Excel
- [ ] Modelo e consultas em SQL
- [ ] Painel no Power BI
- [ ] Conclusões e post no LinkedIn

Dados 100% fictícios.
