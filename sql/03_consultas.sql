-- =====================================================================
-- Gerir Manutenção (SGM) - Projeto Físico (PostgreSQL)
-- Script 03: consultas
-- Executar depois do 01_criacao.sql e do 02_insercao.sql
--
-- Data de referencia da carga ("hoje"): 19/10/2026 08:00.
-- As consultas que dependem de "hoje" usam TIMESTAMP '2026-10-19 08:00' para
-- que o resultado seja reproduzível; no sistema, troque por now() / CURRENT_DATE.
--
-- Parte 1 - consultas de exemplo (SELECT, WHERE, JOIN, GROUP BY, LEFT JOIN)
-- Parte 2 - consultas de exercício (IN / EXISTS / JOIN, divisão, HAVING, UNION, anti-junção)
-- Parte 3 - consultas que atendem os requisitos funcionais (RF06 a RF16)
-- =====================================================================

SET search_path TO sgm;

-- =====================================================================
-- PARTE 1 - CONSULTAS DE EXEMPLO
-- =====================================================================

-- 1.1 todos os equipamentos
SELECT * FROM equipamento;

-- 1.2 equipamentos da linha 1
SELECT * FROM equipamento WHERE id_linha = 1;

-- 1.3 equipamentos das linhas 1 e 2
SELECT codigo, nome, id_linha FROM equipamento WHERE id_linha IN (1, 2);

-- 1.4 equipamentos de criticidade ALTA ainda em operação
SELECT codigo, nome, criticidade FROM equipamento WHERE criticidade = 'ALTA' AND ativo;

-- 1.5 usuários sem telefone cadastrado
SELECT nome, login, tipo_usuario FROM usuario WHERE telefone IS NULL;

-- 1.6 equipamentos cujo nome começa com "Prensa"
SELECT codigo, nome, modelo FROM equipamento WHERE nome LIKE 'Prensa%';

-- 1.7 todos os técnicos com especialidade e equipe (junção na cláusula WHERE)
SELECT u.nome, t.especialidade, t.id_equipe
FROM usuario u, tecnico t
WHERE u.id_usuario = t.id_usuario
ORDER BY u.nome;

-- 1.8 técnicos eletricistas com o nome da equipe (INNER JOIN)
SELECT u.nome, t.especialidade, e.nome AS equipe
FROM usuario u
INNER JOIN tecnico t ON t.id_usuario = u.id_usuario
INNER JOIN equipe e ON e.id_equipe = t.id_equipe
WHERE t.especialidade = 'Eletrica';

-- 1.9 total de ordens de serviço corretivas
SELECT count(*) AS total_corretivas FROM ordem_servico WHERE tipo_os = 'C';

-- 1.10 quantidade de OS por tipo e status
SELECT tipo_os, status, count(*) AS quantidade
FROM ordem_servico
GROUP BY tipo_os, status
ORDER BY tipo_os, status;

-- 1.11 fabricantes distintos
SELECT DISTINCT fabricante FROM equipamento ORDER BY fabricante;

-- 1.12 quantidade de equipamentos por linha de produção
SELECT l.nome AS linha, count(*) AS equipamentos
FROM linha_producao l JOIN equipamento e ON e.id_linha = l.id_linha
GROUP BY l.nome
ORDER BY l.nome;

-- 1.13 equipamentos com seus planos preventivos (só os que têm plano)
SELECT e.codigo || ' - ' || e.nome AS equipamento, p.descricao, p.periodicidade
FROM equipamento e JOIN plano_preventivo p ON p.id_equipamento = e.id_equipamento
ORDER BY equipamento;

-- 1.14 todas as peças e, para as que foram usadas, o total baixado (LEFT JOIN)
SELECT p.codigo, p.descricao, coalesce(sum(b.quantidade), 0) AS total_baixado
FROM peca p LEFT JOIN baixa_peca b ON b.id_peca = p.id_peca
GROUP BY p.id_peca, p.codigo, p.descricao
ORDER BY total_baixado DESC;


-- =====================================================================
-- PARTE 2 - CONSULTAS DE EXERCICIO
-- =====================================================================

-- 2.1 nome e telefone de todos os técnicos da Equipe Beta
SELECT u.nome, u.telefone
FROM usuario u
JOIN tecnico t ON t.id_usuario = u.id_usuario
JOIN equipe e ON e.id_equipe = t.id_equipe
WHERE e.nome = 'Equipe Beta';

-- 2.2 equipe, turno, supervisor e técnicos (nome e especialidade) de todas as equipes
SELECT e.nome AS equipe, e.turno, us.nome AS supervisor, ut.nome AS tecnico, t.especialidade
FROM equipe e
JOIN usuario us ON us.id_usuario = e.id_supervisor
JOIN tecnico t ON t.id_equipe = e.id_equipe
JOIN usuario ut ON ut.id_usuario = t.id_usuario
ORDER BY e.nome, ut.nome;

-- 2.3 todas as linhas de produção (todos os dados) com os dados de seus equipamentos
SELECT l.*, e.codigo, e.nome AS equipamento, e.criticidade, e.ativo
FROM linha_producao l JOIN equipamento e ON e.id_linha = l.id_linha
ORDER BY l.id_linha, e.codigo;

-- 2.4 técnicos (nomes) que fizeram corretivas na Prensa Hidraulica (EQ-005):
--     código da OS, data da falha, horímetro e causa
SELECT u.nome AS tecnico, o.codigo_os, c.data_hora_falha, o.leitura_horimetro, c.causa_falha
FROM ordem_servico o
JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
JOIN usuario u ON u.id_usuario = o.id_tecnico
WHERE e.codigo = 'EQ-005'
ORDER BY c.data_hora_falha;

-- 2.5 supervisores com os registros profissionais e as OS que avaliaram em outubro de 2026
SELECT u.nome AS supervisor, s.registro_profissional, o.codigo_os, o.decisao_avaliacao, o.data_avaliacao
FROM supervisor s
JOIN usuario u ON u.id_usuario = s.id_usuario
JOIN ordem_servico o ON o.id_supervisor_avaliador = s.id_usuario
WHERE o.data_avaliacao >= DATE '2026-10-01'
ORDER BY u.nome, o.data_avaliacao;

-- 2.6 técnicos (nomes) que fizeram OS em equipamentos da Linha 1 - Usinagem e que nunca atenderam
--     uma corretiva com parada de produção (código da OS, equipamento e data de início)
SELECT u.nome AS tecnico, o.codigo_os, e.codigo, e.nome AS equipamento, o.data_inicio_execucao
FROM ordem_servico o
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
JOIN linha_producao l ON l.id_linha = e.id_linha
JOIN usuario u ON u.id_usuario = o.id_tecnico
WHERE l.nome = 'Linha 1 - Usinagem'
  AND NOT EXISTS (SELECT 1 FROM ordem_servico o2 JOIN manutencao_corretiva c ON c.codigo_os = o2.codigo_os
                  WHERE o2.id_tecnico = o.id_tecnico AND c.impacto_producao)
ORDER BY u.nome, o.data_inicio_execucao;

-- 2.7 dados dos equipamentos que já tiveram falha com parada de produção
--     resolvida de três formas: IN, EXISTS e JOIN (as três devem trazer o mesmo resultado)

-- (a) usando IN
SELECT * FROM equipamento
WHERE id_equipamento IN (SELECT o.id_equipamento
                         FROM ordem_servico o JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
                         WHERE c.impacto_producao)
ORDER BY codigo;

-- (b) usando EXISTS
SELECT * FROM equipamento e
WHERE EXISTS (SELECT 1
              FROM ordem_servico o JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
              WHERE o.id_equipamento = e.id_equipamento AND c.impacto_producao)
ORDER BY codigo;

-- (c) usando JOIN
SELECT DISTINCT e.*
FROM equipamento e
JOIN ordem_servico o ON o.id_equipamento = e.id_equipamento
JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
WHERE c.impacto_producao
ORDER BY e.codigo;

-- 2.8 DIVISÃO: nome dos técnicos que atenderam TODOS os equipamentos que o técnico
--     Bruno Cesar Cardoso atendeu (EQ-005, EQ-006, EQ-007 e EQ-008).
--     Resposta esperada com a carga original: Thiago Ribeiro Dias
SELECT u.nome
FROM tecnico t JOIN usuario u ON u.id_usuario = t.id_usuario
WHERE u.nome <> 'Bruno Cesar Cardoso'
  AND NOT EXISTS (
      SELECT o.id_equipamento FROM ordem_servico o JOIN usuario b ON b.id_usuario = o.id_tecnico
      WHERE b.nome = 'Bruno Cesar Cardoso'
      EXCEPT
      SELECT o.id_equipamento FROM ordem_servico o WHERE o.id_tecnico = t.id_usuario);

-- 2.8 (b) mesma divisão com NOT EXISTS duplo (forma clássica, sem EXCEPT)
SELECT u.nome
FROM tecnico t JOIN usuario u ON u.id_usuario = t.id_usuario
WHERE u.nome <> 'Bruno Cesar Cardoso'
  AND NOT EXISTS (
      SELECT 1 FROM ordem_servico ob JOIN usuario b ON b.id_usuario = ob.id_tecnico
      WHERE b.nome = 'Bruno Cesar Cardoso'
        AND NOT EXISTS (SELECT 1 FROM ordem_servico ot
                        WHERE ot.id_tecnico = t.id_usuario AND ot.id_equipamento = ob.id_equipamento));
-- Experimento: dentro de uma transação, a Mariana passa a atender a Guilhotina (EQ-007)
-- e também passa a cobrir todos os equipamentos do Bruno. Resposta: Mariana Alves Barbosa; Thiago Ribeiro Dias
BEGIN;
INSERT INTO ordem_servico (tipo_os, descricao, data_abertura, prioridade, status, id_equipamento, id_tecnico)
VALUES ('C', 'OS de teste da consulta de divisao', TIMESTAMP '2026-10-19 08:00', 'BAIXA', 'PENDENTE', 7, 13);
SELECT u.nome
FROM tecnico t JOIN usuario u ON u.id_usuario = t.id_usuario
WHERE u.nome <> 'Bruno Cesar Cardoso'
  AND NOT EXISTS (
      SELECT o.id_equipamento FROM ordem_servico o JOIN usuario b ON b.id_usuario = o.id_tecnico
      WHERE b.nome = 'Bruno Cesar Cardoso'
      EXCEPT
      SELECT o.id_equipamento FROM ordem_servico o WHERE o.id_tecnico = t.id_usuario)
ORDER BY u.nome;
ROLLBACK;

-- 2.9 código, nome e quantidade de corretivas dos equipamentos de criticidade ALTA
--     que tiveram mais de 3 corretivas
SELECT e.codigo, e.nome, count(*) AS corretivas
FROM equipamento e JOIN ordem_servico o ON o.id_equipamento = e.id_equipamento
WHERE e.criticidade = 'ALTA' AND o.tipo_os = 'C'
GROUP BY e.codigo, e.nome
HAVING count(*) > 3
ORDER BY corretivas DESC;

-- 2.10 nome e especialidade dos técnicos com mais de 10 OS concluídas
SELECT u.nome, t.especialidade, count(*) AS concluidas
FROM tecnico t
JOIN usuario u ON u.id_usuario = t.id_usuario
JOIN ordem_servico o ON o.id_tecnico = t.id_usuario
WHERE o.status = 'CONCLUIDA'
GROUP BY u.nome, t.especialidade
HAVING count(*) > 10
ORDER BY concluidas DESC;

-- 2.11 nome e perfil de todas as pessoas cadastradas; para técnico, mostra também a equipe,
--      e para supervisor, a equipe que lidera
--      ex.:  Joao Batista Ferreira - Técnico da Equipe Alfa
--            Fernanda Souza Lima   - Supervisor(a) da Equipe Alfa
SELECT u.nome || ' - Tecnico da ' || e.nome AS pessoa
FROM usuario u JOIN tecnico t ON t.id_usuario = u.id_usuario JOIN equipe e ON e.id_equipe = t.id_equipe
UNION
SELECT u.nome || ' - Supervisor(a) da ' || coalesce(e.nome, 'nenhuma equipe')
FROM usuario u JOIN supervisor s ON s.id_usuario = u.id_usuario LEFT JOIN equipe e ON e.id_supervisor = s.id_usuario
UNION
SELECT u.nome || ' - Gestor(a): ' || coalesce(g.cargo, 'sem cargo')
FROM usuario u JOIN gestor g ON g.id_usuario = u.id_usuario
UNION
SELECT u.nome || ' - Administrativo(a): ' || coalesce(a.setor, 'sem setor')
FROM usuario u JOIN administrativo a ON a.id_usuario = u.id_usuario
UNION
SELECT u.nome || ' - Administrador(a) do Sistema'
FROM usuario u JOIN administrador_sistema x ON x.id_usuario = u.id_usuario
ORDER BY 1;

-- 2.12 nome dos técnicos que nunca receberam nenhuma OS
SELECT u.nome, u.data_cadastro
FROM tecnico t JOIN usuario u ON u.id_usuario = t.id_usuario
LEFT JOIN ordem_servico o ON o.id_tecnico = t.id_usuario
WHERE o.codigo_os IS NULL;

-- 2.13 código e descrição das peças que nunca foram usadas em nenhuma OS
SELECT p.codigo, p.descricao, p.quantidade_atual
FROM peca p
WHERE NOT EXISTS (SELECT 1 FROM baixa_peca b WHERE b.id_peca = p.id_peca);

-- 2.14 equipamentos sem nenhum plano preventivo ativo (e se o equipamento ainda opera)
SELECT e.codigo, e.nome, e.ativo AS equipamento_ativo
FROM equipamento e
WHERE e.id_equipamento NOT IN (SELECT id_equipamento FROM plano_preventivo WHERE ativo);

-- 2.15 nome, especialidade e equipe dos técnicos que atenderam mais de 5 equipamentos diferentes
SELECT u.nome, t.especialidade, e.nome AS equipe, count(DISTINCT o.id_equipamento) AS equipamentos
FROM tecnico t
JOIN usuario u ON u.id_usuario = t.id_usuario
JOIN equipe e ON e.id_equipe = t.id_equipe
JOIN ordem_servico o ON o.id_tecnico = t.id_usuario
GROUP BY u.nome, t.especialidade, e.nome
HAVING count(DISTINCT o.id_equipamento) > 5
ORDER BY equipamentos DESC;

-- 2.16 equipamentos atendidos por técnicos de todas as 3 equipes, com as equipes envolvidas
SELECT e.codigo, e.nome, string_agg(DISTINCT eq.nome, ', ') AS equipes
FROM ordem_servico o
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
JOIN tecnico t ON t.id_usuario = o.id_tecnico
JOIN equipe eq ON eq.id_equipe = t.id_equipe
GROUP BY e.codigo, e.nome
HAVING count(DISTINCT t.id_equipe) = (SELECT count(*) FROM equipe)
ORDER BY e.codigo;


-- =====================================================================
-- PARTE 3 - CONSULTAS DOS REQUISITOS FUNCIONAIS
-- =====================================================================

-- RF08 - histórico completo de uma máquina, buscando por código ou nome parcial,
--        da intervenção mais recente para a mais antiga
SELECT e.codigo, e.nome AS equipamento, o.codigo_os,
       CASE o.tipo_os WHEN 'C' THEN 'Corretiva' ELSE 'Preventiva' END AS tipo,
       o.data_abertura, o.status, u.nome AS tecnico, o.leitura_horimetro,
       coalesce(c.causa_falha, p.observacao_geral) AS detalhe
FROM equipamento e
JOIN ordem_servico o ON o.id_equipamento = e.id_equipamento
JOIN usuario u ON u.id_usuario = o.id_tecnico
LEFT JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
LEFT JOIN manutencao_preventiva p ON p.codigo_os = o.codigo_os
WHERE e.codigo ILIKE '%compressor%' OR e.nome ILIKE '%compressor%'
ORDER BY o.data_abertura DESC;

-- RF09 - tarefas preventivas da semana (de hoje até 7 dias), por vencimento:
--        planos ativos que vencem na semana e, se já existir, a OS aberta para o vencimento
SELECT pl.proxima_data AS vencimento, e.codigo, e.nome AS equipamento, pl.descricao AS plano,
       pl.periodicidade, os.codigo_os, os.tecnico, coalesce(os.status, 'OS AINDA NAO GERADA') AS status
FROM plano_preventivo pl
JOIN equipamento e ON e.id_equipamento = pl.id_equipamento
LEFT JOIN (SELECT mp.id_plano, o.prazo, o.codigo_os, o.status, u.nome AS tecnico
           FROM manutencao_preventiva mp
           JOIN ordem_servico o ON o.codigo_os = mp.codigo_os
           JOIN usuario u ON u.id_usuario = o.id_tecnico) os
       ON os.id_plano = pl.id_plano AND os.prazo = pl.proxima_data
WHERE pl.ativo
  AND pl.proxima_data BETWEEN DATE '2026-10-19' AND DATE '2026-10-19' + 7   -- CURRENT_DATE no sistema
ORDER BY pl.proxima_data;

-- RF06 - alertas: preventivas que vencem em menos de 24 h e preventivas atrasadas há mais de 24 h
SELECT o.codigo_os, e.nome AS equipamento, o.prazo, u.nome AS tecnico,
       CASE WHEN o.prazo::timestamp < TIMESTAMP '2026-10-19 08:00' - INTERVAL '24 hours' THEN 'ATRASO'
            ELSE 'PROXIMIDADE' END AS alerta
FROM ordem_servico o
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
JOIN usuario u ON u.id_usuario = o.id_tecnico
WHERE o.tipo_os = 'P' AND o.status IN ('PENDENTE', 'EM_EXECUCAO')
  AND (o.prazo::timestamp < TIMESTAMP '2026-10-19 08:00' - INTERVAL '24 hours'
       OR o.prazo::timestamp <= TIMESTAMP '2026-10-19 08:00' + INTERVAL '24 hours')
ORDER BY o.prazo;

-- RF07 - relatório mensal de falhas por equipamento (corretivas por mês)
SELECT to_char(c.data_hora_falha, 'YYYY-MM') AS mes, e.codigo, e.nome, count(*) AS falhas,
       sum(CASE WHEN c.impacto_producao THEN 1 ELSE 0 END) AS com_parada
FROM manutencao_corretiva c
JOIN ordem_servico o ON o.codigo_os = c.codigo_os
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
GROUP BY mes, e.codigo, e.nome
ORDER BY mes, falhas DESC, e.codigo;

-- RF07 - relatório mensal de consumo de peças (quantidades baixadas), por peça
SELECT to_char(b.data_baixa, 'YYYY-MM') AS mes, p.codigo, p.descricao,
       sum(b.quantidade) AS quantidade, p.unidade_medida
FROM baixa_peca b JOIN peca p ON p.id_peca = b.id_peca
GROUP BY mes, p.codigo, p.descricao, p.unidade_medida
ORDER BY mes, quantidade DESC;

-- RF07 - consumo de peças por máquina em um período (setembro e outubro de 2026)
SELECT e.codigo, e.nome AS equipamento, p.descricao AS peca, sum(b.quantidade) AS quantidade, p.unidade_medida
FROM baixa_peca b
JOIN peca p ON p.id_peca = b.id_peca
JOIN ordem_servico o ON o.codigo_os = b.codigo_os
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
WHERE b.data_baixa >= DATE '2026-09-01' AND b.data_baixa < DATE '2026-11-01'
GROUP BY e.codigo, e.nome, p.descricao, p.unidade_medida
ORDER BY e.codigo, quantidade DESC;

-- RF05 - MTTR (tempo médio de reparo, em horas) por equipamento, com base nas corretivas concluídas
SELECT e.codigo, e.nome,
       count(*) AS reparos,
       round(avg(EXTRACT(EPOCH FROM (o.data_fim_execucao - o.data_inicio_execucao)) / 3600)::numeric, 2) AS mttr_horas
FROM ordem_servico o JOIN equipamento e ON e.id_equipamento = o.id_equipamento
WHERE o.tipo_os = 'C' AND o.status = 'CONCLUIDA'
GROUP BY e.codigo, e.nome
ORDER BY mttr_horas DESC;

-- RF15 - ranking das 10 máquinas com mais falhas nos últimos 90 dias, com o MTBF atual
--        (MTBF = média, em horas, do intervalo entre falhas consecutivas do equipamento;
--         fica nulo quando o equipamento tem uma única falha registrada)
WITH falhas AS (
    SELECT o.id_equipamento, c.data_hora_falha,
           c.data_hora_falha - lag(c.data_hora_falha) OVER (PARTITION BY o.id_equipamento
                                                            ORDER BY c.data_hora_falha) AS intervalo
    FROM manutencao_corretiva c JOIN ordem_servico o ON o.codigo_os = c.codigo_os
),
mtbf AS (
    SELECT id_equipamento, round(avg(EXTRACT(EPOCH FROM intervalo) / 3600)::numeric, 1) AS mtbf_horas
    FROM falhas GROUP BY id_equipamento
)
SELECT e.codigo, e.nome, count(*) AS falhas_no_periodo, m.mtbf_horas
FROM falhas f
JOIN equipamento e ON e.id_equipamento = f.id_equipamento
JOIN mtbf m ON m.id_equipamento = f.id_equipamento
WHERE f.data_hora_falha >= TIMESTAMP '2026-10-19 08:00' - INTERVAL '90 days'   -- now() no sistema
GROUP BY e.codigo, e.nome, m.mtbf_horas
ORDER BY falhas_no_periodo DESC, e.codigo
LIMIT 10;

-- RF05 - disponibilidade atual das máquinas: em manutenção se há OS em execução
SELECT e.codigo, e.nome, e.criticidade,
       CASE WHEN EXISTS (SELECT 1 FROM ordem_servico o
                         WHERE o.id_equipamento = e.id_equipamento AND o.status = 'EM_EXECUCAO')
            THEN 'EM MANUTENCAO' ELSE 'DISPONIVEL' END AS situacao
FROM equipamento e
WHERE e.ativo
ORDER BY situacao DESC, e.codigo;

-- RF14 - status de cada técnico, com a OS em andamento (se houver)
SELECT eq.nome AS equipe, u.nome AS tecnico, t.status_operacional,
       o.codigo_os AS os_em_andamento, e.nome AS equipamento
FROM tecnico t
JOIN usuario u ON u.id_usuario = t.id_usuario
JOIN equipe eq ON eq.id_equipe = t.id_equipe
LEFT JOIN ordem_servico o ON o.id_tecnico = t.id_usuario AND o.status = 'EM_EXECUCAO'
LEFT JOIN equipamento e ON e.id_equipamento = o.id_equipamento
ORDER BY eq.nome, u.nome;

-- RF16 - produtividade por equipe no mês corrente (01/10/2026 até hoje):
--        tarefas planejadas (prazo no período) x concluídas e percentual de conclusão
SELECT eq.nome AS equipe,
       count(*) AS planejadas,
       count(*) FILTER (WHERE o.status = 'CONCLUIDA') AS concluidas,
       round(100.0 * count(*) FILTER (WHERE o.status = 'CONCLUIDA') / count(*), 1) AS percentual
FROM ordem_servico o
JOIN tecnico t ON t.id_usuario = o.id_tecnico
JOIN equipe eq ON eq.id_equipe = t.id_equipe
WHERE o.prazo >= DATE '2026-10-01' AND o.prazo <= DATE '2026-10-19'   -- CURRENT_DATE no sistema
GROUP BY eq.nome
ORDER BY eq.nome;

-- RF16 - produtividade por técnico nas últimas 4 semanas (por semana)
SELECT date_trunc('week', o.prazo)::date AS semana, u.nome AS tecnico,
       count(*) AS planejadas,
       count(*) FILTER (WHERE o.status = 'CONCLUIDA') AS concluidas
FROM ordem_servico o JOIN usuario u ON u.id_usuario = o.id_tecnico
WHERE o.prazo >= DATE '2026-10-19' - 28 AND o.prazo < DATE '2026-10-19'
GROUP BY semana, u.nome
ORDER BY semana, u.nome;

-- RF12 - OS aguardando aprovação, por supervisor responsável pela equipe do técnico
SELECT us.nome AS supervisor, o.codigo_os, CASE o.tipo_os WHEN 'C' THEN 'Corretiva' ELSE 'Preventiva' END AS tipo,
       e.nome AS equipamento, ut.nome AS tecnico, o.data_fim_execucao
FROM ordem_servico o
JOIN tecnico t ON t.id_usuario = o.id_tecnico
JOIN equipe eq ON eq.id_equipe = t.id_equipe
JOIN usuario us ON us.id_usuario = eq.id_supervisor
JOIN usuario ut ON ut.id_usuario = o.id_tecnico
JOIN equipamento e ON e.id_equipamento = o.id_equipamento
WHERE o.status = 'AGUARDANDO_APROVACAO'
ORDER BY us.nome, o.data_fim_execucao;

-- RF12 - OS rejeitadas que voltaram para o técnico, com a justificativa
SELECT o.codigo_os, ut.nome AS tecnico, us.nome AS avaliador, o.data_avaliacao, o.justificativa
FROM ordem_servico o
JOIN usuario ut ON ut.id_usuario = o.id_tecnico
JOIN usuario us ON us.id_usuario = o.id_supervisor_avaliador
WHERE o.decisao_avaliacao = 'REJEITADA';

-- RF03 - checklist de uma preventiva (itens do equipamento x itens respondidos);
--        itens obrigatórios sem resposta bloqueiam a conclusão
SELECT o.codigo_os, i.num_item, i.descricao, i.obrigatorio,
       coalesce(r.resultado, 'SEM RESPOSTA') AS resultado, r.observacao
FROM ordem_servico o
JOIN item_checklist i ON i.id_equipamento = o.id_equipamento
LEFT JOIN resultado_checklist r ON r.codigo_os = o.codigo_os AND r.id_equipamento = i.id_equipamento
                               AND r.num_item = i.num_item
WHERE o.tipo_os = 'P' AND o.status = 'EM_EXECUCAO'
ORDER BY o.codigo_os, i.num_item;

-- RF13 - peças no estoque mínimo ou abaixo dele, com a data do último alerta gerado
SELECT p.codigo, p.descricao, p.quantidade_atual, p.estoque_minimo, p.unidade_medida,
       (SELECT max(n.data_geracao) FROM notificacao n
        WHERE n.id_peca = p.id_peca AND n.tipo = 'ESTOQUE_MINIMO') AS ultimo_alerta
FROM peca p
WHERE p.ativo AND p.quantidade_atual <= p.estoque_minimo
ORDER BY p.quantidade_atual::numeric / nullif(p.estoque_minimo, 0);

-- Notificações não lidas por usuário e por tipo
SELECT u.nome, n.tipo, count(*) AS nao_lidas
FROM notificacao_usuario nu
JOIN notificacao n ON n.id_notificacao = nu.id_notificacao
JOIN usuario u ON u.id_usuario = nu.id_usuario
WHERE nu.data_leitura IS NULL
GROUP BY u.nome, n.tipo
ORDER BY u.nome, n.tipo;
