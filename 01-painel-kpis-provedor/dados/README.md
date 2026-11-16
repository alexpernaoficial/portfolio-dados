# Base sintética do ProvedorX (2026)

Dados 100% fictícios, gerados por `../python/gerar_dados.py` (semente fixa 42, então o resultado é sempre o mesmo). Os CSVs usam ponto e vírgula e vírgula decimal, para abrir direto no Excel em português. O arquivo `provedorx_base_2026.xlsx` traz as mesmas tabelas, uma por aba.

## Tabelas

**clientes** (4.000 linhas): id_cliente, id_plano, id_cidade, data_ativacao, canal_venda, fidelidade_meses, data_cancelamento, motivo_cancelamento, status.

**planos** (5 linhas): id_plano, plano, velocidade_mbps, mensalidade, tipo.

**cidades** (6 linhas, cidades inventadas): id_cidade, cidade, regiao.

**chamados** (cerca de 10.700 linhas, ano de 2026): id_chamado, id_cliente, data_abertura, motivo, canal, nivel (N1 ou N2), turno, precisou_visita, tempo_atendimento_min, tempo_resolucao_horas, sla_horas, dentro_sla.

**nps** (cerca de 3.200 respostas, 30% dos chamados): id_resposta, id_chamado, id_cliente, data_resposta, nota (0 a 10), categoria (Detrator, Neutro, Promotor).

## Ligações entre tabelas

- clientes.id_plano → planos.id_plano
- clientes.id_cidade → cidades.id_cidade
- chamados.id_cliente → clientes.id_cliente
- nps.id_chamado → chamados.id_chamado

## Números esperados (para conferir seus cálculos)

- Cerca de 3.060 clientes ativos em 01/01/2026 e cerca de 620 cancelamentos em 2026 (churn perto de 1,7% ao mês).
- Cerca de 83% dos chamados dentro do SLA.
- TMA médio perto de 11 minutos.
- NPS perto de 45.

## Pistas escondidas nos dados

A base foi gerada com alguns padrões de propósito, para a análise ter o que descobrir. Tente achá-los antes de ler o script:

1. Uma cidade tem rede mais antiga: mais chamados, resolução mais lenta e mais cancelamentos.
2. Chamado fora do SLA derruba a nota do NPS.
3. Cliente sem fidelidade cancela mais.

## Exercícios de Excel sugeridos

1. PROCV ou PROCX para trazer o nome do plano e da cidade para a aba de clientes.
2. Tabela dinâmica de chamados por motivo e por mês.
3. Percentual dentro do SLA por motivo, com formatação condicional.
4. NPS por mês: (promotores menos detratores) dividido pelo total, vezes 100.
5. Churn mensal: cancelamentos do mês divididos pelos ativos no início do mês.
