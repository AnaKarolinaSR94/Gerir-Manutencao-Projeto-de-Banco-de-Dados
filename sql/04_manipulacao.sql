-- =====================================================================
-- Gerir Manutenção (SGM) - Projeto Físico (PostgreSQL)
-- Script 04: manipulação de dados (INSERT, UPDATE, DELETE)
-- Executar depois do 02_insercao.sql
--
-- Simula as operações do sistema na ordem em que acontecem: cadastros, o ciclo de vida de
-- uma OS corretiva (distribuir, iniciar, dar baixa de peça, concluir, rejeitar, aprovar) e de
-- uma OS preventiva (checklist, aprovação e reagendamento pelo plano), além de exclusões.
--
-- Tudo roda dentro de uma transação terminada em ROLLBACK, para a base voltar ao estado
-- da carga e as respostas do 03_consultas.sql continuarem valendo.
-- Para gravar de verdade, troque o ROLLBACK do final por COMMIT.
-- =====================================================================

SET search_path TO sgm;

BEGIN;

-- ---------------------------------------------------------------------
-- 1. Cadastros (perfil Administrativo / Administrador do Sistema) - RF01
-- ---------------------------------------------------------------------

-- 1.1 novo equipamento na linha de Montagem
INSERT INTO equipamento (codigo, nome, fabricante, modelo, numero_serie, localizacao, criticidade, data_aquisicao, id_linha)
VALUES ('EQ-016', 'Parafusadeira Automatica', 'Atlas Copco', 'Tensor ST', 'AC-TST-99120', 'Galpao C - Celula 2',
        'MEDIA', DATE '2026-10-15', 4);

-- 1.2 checklist próprio do novo equipamento (entidade fraca: chave = equipamento + número do item)
INSERT INTO item_checklist (id_equipamento, num_item, descricao, obrigatorio)
SELECT id_equipamento, 1, 'Verificar calibracao de torque', true FROM equipamento WHERE codigo = 'EQ-016'
UNION ALL
SELECT id_equipamento, 2, 'Inspecionar cabo e conector da ferramenta', true FROM equipamento WHERE codigo = 'EQ-016'
UNION ALL
SELECT id_equipamento, 3, 'Limpar bits e soquetes', false FROM equipamento WHERE codigo = 'EQ-016';

-- 1.3 plano preventivo mensal para o novo equipamento
INSERT INTO plano_preventivo (descricao, periodicidade, proxima_data, id_equipamento)
SELECT 'Calibracao mensal da parafusadeira', 'MENSAL', DATE '2026-11-16', id_equipamento
FROM equipamento WHERE codigo = 'EQ-016';

SELECT e.codigo, e.nome, i.num_item, i.descricao, p.descricao AS plano, p.proxima_data
FROM equipamento e
JOIN item_checklist i ON i.id_equipamento = e.id_equipamento
JOIN plano_preventivo p ON p.id_equipamento = e.id_equipamento
WHERE e.codigo = 'EQ-016';

-- 1.4 nova peça no catálogo e reposição de estoque de uma peça abaixo do mínimo
INSERT INTO peca (codigo, descricao, unidade_medida, fornecedor, estoque_minimo, quantidade_atual)
VALUES ('PC-BIT-PH2', 'Bit Phillips PH2 para parafusadeira', 'UN', 'Atlas Copco', 10, 50);

UPDATE peca SET quantidade_atual = quantidade_atual + 4 WHERE codigo = 'PC-RES-SEL';

SELECT codigo, descricao, quantidade_atual, estoque_minimo FROM peca WHERE codigo IN ('PC-BIT-PH2', 'PC-RES-SEL');

-- 1.5 novo técnico: primeiro a superclasse USUARIO, depois a subclasse TECNICO
INSERT INTO usuario (nome, login, senha_hash, email, telefone, tipo_usuario)
VALUES ('Vanessa Cristina Moura', 'vanessa.moura', '$2b$12$exemploDeHashSomenteParaTeste000000000000000000000000',
        'vanessa.moura@gerirmanutencao.com.br', '(62) 99810-1021', 'T');
INSERT INTO tecnico (id_usuario, especialidade, id_equipe)
SELECT id_usuario, 'Eletrica', 2 FROM usuario WHERE login = 'vanessa.moura';

-- 1.6 desativar o plano anual da prensa (o histórico continua no banco)
UPDATE plano_preventivo SET ativo = false WHERE id_plano = 6;

-- ---------------------------------------------------------------------
-- 2. Ciclo de vida de uma OS corretiva - RF11, RF02, RF10, RF13, RF14, RF12
-- ---------------------------------------------------------------------

-- 2.1 supervisora Fernanda distribui uma corretiva do Torno CNC para o técnico Joao (RF11)
INSERT INTO ordem_servico (tipo_os, descricao, prioridade, prazo, status, id_equipamento, id_tecnico, id_supervisor)
VALUES ('C', 'Ruido anormal no cabecote durante usinagem de eixos', 'ALTA', CURRENT_DATE + 1, 'PENDENTE', 1, 9, 2);
INSERT INTO manutencao_corretiva (codigo_os, impacto_producao, data_hora_falha)
VALUES (currval(pg_get_serial_sequence('ordem_servico', 'codigo_os')), true, now() - INTERVAL '40 minutes');

-- notificação NOVA_OS para o técnico
WITH nova AS (
    INSERT INTO notificacao (tipo, mensagem, codigo_os)
    SELECT 'NOVA_OS', 'Nova OS corretiva #' || o.codigo_os || ' atribuida: ' || e.nome || ' (' || e.codigo
           || '), prioridade ' || o.prioridade, o.codigo_os
    FROM ordem_servico o JOIN equipamento e ON e.id_equipamento = o.id_equipamento
    WHERE o.codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'))
    RETURNING id_notificacao, codigo_os
)
INSERT INTO notificacao_usuario (id_notificacao, id_usuario, canal, data_envio)
SELECT nova.id_notificacao, o.id_tecnico, 'NAVEGADOR', now()
FROM nova JOIN ordem_servico o ON o.codigo_os = nova.codigo_os;

-- 2.2 o técnico inicia a execução: OS em execução e técnico OCUPADO (RF14)
UPDATE ordem_servico SET status = 'EM_EXECUCAO', data_inicio_execucao = now()
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE tecnico SET status_operacional = 'OCUPADO' WHERE id_usuario = 9;

-- 2.3 baixa de 3 correias A-42 (RF10): registra a baixa e reduz o saldo
--     (o WHERE impede que o saldo fique negativo)
INSERT INTO baixa_peca (codigo_os, id_peca, quantidade)
VALUES (currval(pg_get_serial_sequence('ordem_servico', 'codigo_os')), 2, 3);
UPDATE peca SET quantidade_atual = quantidade_atual - 3 WHERE id_peca = 2 AND quantidade_atual >= 3;

-- 2.4 alerta de estoque mínimo (RF13): só gera se a peça atingiu o mínimo e se não houve
--     alerta da mesma peça nas últimas 24 h; avisa Administrativos (e-mail) e Supervisores (navegador)
WITH nova AS (
    INSERT INTO notificacao (tipo, mensagem, id_peca)
    SELECT 'ESTOQUE_MINIMO', 'Estoque minimo atingido: ' || p.descricao || ' (' || p.codigo || ') - quantidade atual '
           || p.quantidade_atual || ' ' || p.unidade_medida || ', estoque minimo ' || p.estoque_minimo || ' '
           || p.unidade_medida, p.id_peca
    FROM peca p
    WHERE p.id_peca = 2
      AND p.quantidade_atual <= p.estoque_minimo
      AND NOT EXISTS (SELECT 1 FROM notificacao n
                      WHERE n.id_peca = p.id_peca AND n.tipo = 'ESTOQUE_MINIMO'
                        AND n.data_geracao > now() - INTERVAL '24 hours')
    RETURNING id_notificacao
)
INSERT INTO notificacao_usuario (id_notificacao, id_usuario, canal, data_envio)
SELECT nova.id_notificacao, u.id_usuario, CASE u.tipo_usuario WHEN 'A' THEN 'EMAIL' ELSE 'NAVEGADOR' END, now()
FROM nova CROSS JOIN usuario u
WHERE u.tipo_usuario IN ('A', 'S') AND u.ativo;

SELECT p.codigo, p.quantidade_atual, p.estoque_minimo, n.mensagem, count(nu.id_usuario) AS destinatarios
FROM peca p
JOIN notificacao n ON n.id_peca = p.id_peca AND n.tipo = 'ESTOQUE_MINIMO'
JOIN notificacao_usuario nu ON nu.id_notificacao = n.id_notificacao
WHERE p.id_peca = 2 AND n.data_geracao > now() - INTERVAL '1 minute'
GROUP BY p.codigo, p.quantidade_atual, p.estoque_minimo, n.mensagem;

-- 2.5 o técnico conclui: informa causa e horímetro; OS vai para aprovação (RF02)
UPDATE manutencao_corretiva SET causa_falha = 'Correia do cabecote com desgaste'
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE ordem_servico
SET status = 'AGUARDANDO_APROVACAO', data_fim_execucao = now() + INTERVAL '2 hours', leitura_horimetro = 3950.0
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE equipamento SET horimetro_atual = 3950.0 WHERE id_equipamento = 1;
-- técnico volta a DISPONIVEL se não tiver outra OS em execução
UPDATE tecnico t SET status_operacional = 'DISPONIVEL'
WHERE t.id_usuario = 9
  AND NOT EXISTS (SELECT 1 FROM ordem_servico o WHERE o.id_tecnico = t.id_usuario AND o.status = 'EM_EXECUCAO');

-- 2.6 a supervisora rejeita com justificativa: a OS volta para o técnico (RF12)
UPDATE ordem_servico
SET status = 'EM_EXECUCAO', decisao_avaliacao = 'REJEITADA', data_avaliacao = now() + INTERVAL '3 hours',
    id_supervisor_avaliador = 2, justificativa = 'Informar tambem o estado do rolamento do eixo arvore'
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE tecnico SET status_operacional = 'OCUPADO' WHERE id_usuario = 9;

-- 2.7 o técnico complementa e conclui de novo; a supervisora aprova e a OS é consolidada
UPDATE manutencao_corretiva SET causa_falha = 'Correia do cabecote com desgaste; rolamento do eixo arvore em bom estado'
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE ordem_servico
SET status = 'CONCLUIDA', decisao_avaliacao = 'APROVADA', data_avaliacao = now() + INTERVAL '5 hours',
    data_fim_execucao = now() + INTERVAL '4 hours', justificativa = NULL
WHERE codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));
UPDATE tecnico t SET status_operacional = 'DISPONIVEL'
WHERE t.id_usuario = 9
  AND NOT EXISTS (SELECT 1 FROM ordem_servico o WHERE o.id_tecnico = t.id_usuario AND o.status = 'EM_EXECUCAO');

-- (o Joao continua OCUPADO porque a OS 105, rejeitada na carga, voltou para ele e segue em execução)
SELECT o.codigo_os, o.status, o.decisao_avaliacao, c.causa_falha, b.quantidade AS correias_baixadas,
       t.status_operacional AS status_tecnico
FROM ordem_servico o
JOIN manutencao_corretiva c ON c.codigo_os = o.codigo_os
JOIN baixa_peca b ON b.codigo_os = o.codigo_os
JOIN tecnico t ON t.id_usuario = o.id_tecnico
WHERE o.codigo_os = currval(pg_get_serial_sequence('ordem_servico', 'codigo_os'));

-- ---------------------------------------------------------------------
-- 3. Ciclo de vida de uma OS preventiva - RF03 e RF04
--    OS 112: inspeção mensal da fresadora (plano 3), vence hoje
-- ---------------------------------------------------------------------

-- 3.1 o técnico inicia e responde o checklist do equipamento
UPDATE ordem_servico SET status = 'EM_EXECUCAO', data_inicio_execucao = now() WHERE codigo_os = 112;
UPDATE tecnico SET status_operacional = 'OCUPADO' WHERE id_usuario = (SELECT id_tecnico FROM ordem_servico WHERE codigo_os = 112);

INSERT INTO resultado_checklist (codigo_os, id_equipamento, num_item, resultado, observacao)
SELECT o.codigo_os, i.id_equipamento, i.num_item, 'VERIFICADO', NULL
FROM ordem_servico o JOIN item_checklist i ON i.id_equipamento = o.id_equipamento
WHERE o.codigo_os = 112 AND i.num_item <= 2;

-- 3.2 itens obrigatórios ainda sem resposta (bloqueiam a conclusão): deve aparecer o item 3
SELECT i.num_item, i.descricao
FROM ordem_servico o JOIN item_checklist i ON i.id_equipamento = o.id_equipamento
WHERE o.codigo_os = 112 AND i.obrigatorio
  AND NOT EXISTS (SELECT 1 FROM resultado_checklist r
                  WHERE r.codigo_os = o.codigo_os AND r.id_equipamento = i.id_equipamento AND r.num_item = i.num_item);

INSERT INTO resultado_checklist (codigo_os, id_equipamento, num_item, resultado, observacao)
VALUES (112, 3, 3, 'VERIFICADO', 'Botao de emergencia testado e funcionando');

-- 3.3 conclusão: só passa para aprovação se todos os obrigatórios foram respondidos
UPDATE ordem_servico o
SET status = 'AGUARDANDO_APROVACAO', data_fim_execucao = now() + INTERVAL '90 minutes', leitura_horimetro = 3330.0
WHERE o.codigo_os = 112
  AND NOT EXISTS (SELECT 1 FROM item_checklist i
                  WHERE i.id_equipamento = o.id_equipamento AND i.obrigatorio
                    AND NOT EXISTS (SELECT 1 FROM resultado_checklist r
                                    WHERE r.codigo_os = o.codigo_os AND r.id_equipamento = i.id_equipamento
                                      AND r.num_item = i.num_item));
UPDATE manutencao_preventiva SET observacao_geral = 'Guias lubrificadas; correias em bom estado.' WHERE codigo_os = 112;
UPDATE equipamento SET horimetro_atual = 3330.0 WHERE id_equipamento = 3;
UPDATE tecnico t SET status_operacional = 'DISPONIVEL'
WHERE t.id_usuario = (SELECT id_tecnico FROM ordem_servico WHERE codigo_os = 112)
  AND NOT EXISTS (SELECT 1 FROM ordem_servico o WHERE o.id_tecnico = t.id_usuario AND o.status = 'EM_EXECUCAO');

-- 3.4 aprovação pelo supervisor da equipe do técnico
UPDATE ordem_servico o
SET status = 'CONCLUIDA', decisao_avaliacao = 'APROVADA', data_avaliacao = now() + INTERVAL '3 hours',
    id_supervisor_avaliador = (SELECT e.id_supervisor FROM tecnico t JOIN equipe e ON e.id_equipe = t.id_equipe
                               WHERE t.id_usuario = o.id_tecnico)
WHERE o.codigo_os = 112 AND o.status = 'AGUARDANDO_APROVACAO';

-- 3.5 RF04: preventiva aprovada -> calcula a próxima data pela periodicidade e gera a nova OS
UPDATE plano_preventivo
SET proxima_data = proxima_data + CASE periodicidade
        WHEN 'DIARIA' THEN INTERVAL '1 day'    WHEN 'SEMANAL' THEN INTERVAL '7 days'
        WHEN 'MENSAL' THEN INTERVAL '1 month'  WHEN 'TRIMESTRAL' THEN INTERVAL '3 months'
        WHEN 'SEMESTRAL' THEN INTERVAL '6 months' ELSE INTERVAL '1 year' END
WHERE id_plano = 3;

INSERT INTO ordem_servico (tipo_os, descricao, prioridade, prazo, status, id_equipamento, id_tecnico, id_supervisor)
SELECT 'P', p.descricao, 'MEDIA', p.proxima_data, 'PENDENTE', p.id_equipamento, o.id_tecnico, o.id_supervisor
FROM plano_preventivo p
JOIN manutencao_preventiva mp ON mp.id_plano = p.id_plano
JOIN ordem_servico o ON o.codigo_os = mp.codigo_os
WHERE p.id_plano = 3 AND o.codigo_os = 112;
INSERT INTO manutencao_preventiva (codigo_os, id_plano)
VALUES (currval(pg_get_serial_sequence('ordem_servico', 'codigo_os')), 3);

SELECT p.id_plano, p.descricao, p.proxima_data, o.codigo_os, o.status, o.prazo
FROM plano_preventivo p
JOIN manutencao_preventiva mp ON mp.id_plano = p.id_plano
JOIN ordem_servico o ON o.codigo_os = mp.codigo_os
WHERE p.id_plano = 3 AND o.codigo_os >= 112
ORDER BY o.codigo_os;

-- ---------------------------------------------------------------------
-- 4. Restrições de integridade em ação
--    cada tentativa inválida é capturada e mostrada como NOTICE, sem abortar a transação
-- ---------------------------------------------------------------------
DO $$
BEGIN
    BEGIN  -- rejeitar sem justificativa
        UPDATE ordem_servico SET decisao_avaliacao = 'REJEITADA', data_avaliacao = now(),
               id_supervisor_avaliador = 2, justificativa = NULL WHERE codigo_os = 114;
        RAISE NOTICE 'ERRO: rejeicao sem justificativa foi aceita';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: rejeicao sem justificativa bloqueada (%)', SQLERRM;
    END;
    BEGIN  -- concluir sem aprovação
        UPDATE ordem_servico SET status = 'CONCLUIDA' WHERE codigo_os = 114;
        RAISE NOTICE 'ERRO: OS concluida sem aprovacao foi aceita';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: OS concluida sem aprovacao bloqueada (%)', SQLERRM;
    END;
    BEGIN  -- baixa com quantidade zero
        INSERT INTO baixa_peca (codigo_os, id_peca, quantidade) VALUES (114, 1, 0);
        RAISE NOTICE 'ERRO: baixa com quantidade zero foi aceita';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: baixa com quantidade zero bloqueada (%)', SQLERRM;
    END;
    BEGIN  -- criticidade fora da lista fechada
        UPDATE equipamento SET criticidade = 'ALTO' WHERE codigo = 'EQ-001';
        RAISE NOTICE 'ERRO: criticidade invalida foi aceita';
    EXCEPTION WHEN check_violation THEN
        RAISE NOTICE 'OK: criticidade invalida bloqueada (%)', SQLERRM;
    END;
    BEGIN  -- número de série duplicado
        INSERT INTO equipamento (codigo, nome, modelo, numero_serie, criticidade, id_linha)
        VALUES ('EQ-099', 'Duplicado', 'X', 'RM-GL240-88213', 'BAIXA', 1);
        RAISE NOTICE 'ERRO: numero de serie duplicado foi aceito';
    EXCEPTION WHEN unique_violation THEN
        RAISE NOTICE 'OK: numero de serie duplicado bloqueado (%)', SQLERRM;
    END;
    BEGIN  -- OS para um usuário que não é técnico (FK para TECNICO)
        INSERT INTO ordem_servico (tipo_os, descricao, prioridade, id_equipamento, id_tecnico)
        VALUES ('C', 'Teste', 'BAIXA', 1, 5);
        RAISE NOTICE 'ERRO: OS atribuida a um gestor foi aceita';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'OK: OS para quem nao e tecnico bloqueada (%)', SQLERRM;
    END;
    BEGIN  -- excluir equipamento com histórico de OS (ON DELETE RESTRICT)
        DELETE FROM equipamento WHERE codigo = 'EQ-005';
        RAISE NOTICE 'ERRO: equipamento com historico foi excluido';
    EXCEPTION WHEN foreign_key_violation THEN
        RAISE NOTICE 'OK: exclusao de equipamento com plano e historico de OS bloqueada (%)', SQLERRM;
    END;
END $$;

-- ---------------------------------------------------------------------
-- 5. Atualizações e exclusões de rotina
-- ---------------------------------------------------------------------

-- 5.1 o técnico Joao lê todas as notificações pendentes
UPDATE notificacao_usuario SET data_leitura = now() WHERE id_usuario = 9 AND data_leitura IS NULL;

-- 5.2 supervisor muda manualmente o status de um técnico (RF14)
UPDATE tecnico SET status_operacional = 'DISPONIVEL' WHERE id_usuario = 17;

-- 5.3 limpeza: apaga notificações com mais de 120 dias já lidas por todos os destinatários
--     (as linhas de notificacao_usuario saem junto por ON DELETE CASCADE)
SELECT count(*) AS notificacoes_antes FROM notificacao;
DELETE FROM notificacao n
WHERE n.data_geracao < now() - INTERVAL '120 days'
  AND NOT EXISTS (SELECT 1 FROM notificacao_usuario nu
                  WHERE nu.id_notificacao = n.id_notificacao AND nu.data_leitura IS NULL);
SELECT count(*) AS notificacoes_depois FROM notificacao;

-- 5.4 excluir o usuário criado em 1.5: a linha de TECNICO sai junto (ON DELETE CASCADE da herança)
DELETE FROM usuario WHERE login = 'vanessa.moura';
SELECT count(*) AS tecnicos_vanessa FROM tecnico t JOIN usuario u ON u.id_usuario = t.id_usuario
WHERE u.login = 'vanessa.moura';

-- 5.5 excluir o equipamento novo (sem OS): o plano tem FK obrigatória (RESTRICT) e precisa sair antes;
--     os itens de checklist (entidade fraca) saem sozinhos por ON DELETE CASCADE
DELETE FROM plano_preventivo WHERE id_equipamento = (SELECT id_equipamento FROM equipamento WHERE codigo = 'EQ-016');
DELETE FROM equipamento WHERE codigo = 'EQ-016';
SELECT count(*) AS itens_checklist_eq016 FROM item_checklist i
WHERE NOT EXISTS (SELECT 1 FROM equipamento e WHERE e.id_equipamento = i.id_equipamento);

-- desfaz tudo (troque por COMMIT para gravar as alterações)
ROLLBACK;
