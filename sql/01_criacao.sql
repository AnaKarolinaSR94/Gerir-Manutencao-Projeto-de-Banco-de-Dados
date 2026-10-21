-- =====================================================================
-- Gerir Manutencao (SGM) - Projeto Fisico (PostgreSQL)
-- Script 01: criacao do banco de dados
-- ARQUIVO GERADO por ferramentas/gen_ddl.py a partir de ferramentas/schema.py
-- (altere o schema.py e regenere; nao edite este arquivo a mao)
-- =====================================================================

-- Passo opcional (executar uma vez, conectado ao banco postgres):
-- CREATE DATABASE gerir_manutencao;
-- Depois conecte-se ao banco gerir_manutencao e execute o restante.

DROP SCHEMA IF EXISTS sgm CASCADE;
CREATE SCHEMA sgm;
SET search_path TO sgm;

-- ---------------------------------------------------------- Pessoas

-- Entidade USUARIO (superclasse)
CREATE TABLE usuario (
    id_usuario SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(120) NOT NULL,
    login VARCHAR(60) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    telefone VARCHAR(20),
    status_2fa BOOLEAN NOT NULL DEFAULT false,
    ativo BOOLEAN NOT NULL DEFAULT true,
    data_cadastro TIMESTAMP NOT NULL DEFAULT now(),
    tipo_usuario CHAR(1) NOT NULL,
    CHECK (tipo_usuario IN ('T','S','G','A','X'))
);

-- Subclasse SUPERVISOR
CREATE TABLE supervisor (
    id_usuario INTEGER NOT NULL PRIMARY KEY,
    registro_profissional VARCHAR(30),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- Entidade EQUIPE + relacionamento lidera (1:N)
CREATE TABLE equipe (
    id_equipe SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    turno VARCHAR(20) NOT NULL,
    id_supervisor INTEGER NOT NULL,
    FOREIGN KEY (id_supervisor) REFERENCES supervisor(id_usuario) ON DELETE RESTRICT
);

-- Subclasse TECNICO + relacionamento pertence (N:1)
CREATE TABLE tecnico (
    id_usuario INTEGER NOT NULL PRIMARY KEY,
    status_operacional VARCHAR(12) NOT NULL DEFAULT 'DISPONIVEL',
    especialidade VARCHAR(60),
    id_equipe INTEGER NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_equipe) REFERENCES equipe(id_equipe) ON DELETE RESTRICT,
    CHECK (status_operacional IN ('DISPONIVEL','OCUPADO'))
);

-- Subclasse GESTOR
CREATE TABLE gestor (
    id_usuario INTEGER NOT NULL PRIMARY KEY,
    cargo VARCHAR(60),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- Subclasse ADMINISTRATIVO
CREATE TABLE administrativo (
    id_usuario INTEGER NOT NULL PRIMARY KEY,
    setor VARCHAR(60),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- Subclasse ADMINISTRADOR_SISTEMA (perfil tecnico de TI; sem atributos proprios)
CREATE TABLE administrador_sistema (
    id_usuario INTEGER NOT NULL PRIMARY KEY,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE
);

-- ---------------------------------------------------------- Ativos

-- Entidade LINHA_PRODUCAO
CREATE TABLE linha_producao (
    id_linha SERIAL NOT NULL PRIMARY KEY,
    nome VARCHAR(80) NOT NULL UNIQUE,
    setor VARCHAR(80)
);

-- Entidade EQUIPAMENTO + fica_na_linha (N:1)
CREATE TABLE equipamento (
    id_equipamento SERIAL NOT NULL PRIMARY KEY,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nome VARCHAR(100) NOT NULL,
    fabricante VARCHAR(80),
    modelo VARCHAR(80) NOT NULL,
    numero_serie VARCHAR(60) NOT NULL UNIQUE,
    localizacao VARCHAR(120),
    criticidade VARCHAR(5) NOT NULL,
    horimetro_atual NUMERIC(10,1) NOT NULL DEFAULT 0,
    data_aquisicao DATE,
    ativo BOOLEAN NOT NULL DEFAULT true,
    id_linha INTEGER NOT NULL,
    FOREIGN KEY (id_linha) REFERENCES linha_producao(id_linha) ON DELETE RESTRICT,
    CHECK (criticidade IN ('ALTA','MEDIA','BAIXA'))
);

-- Entidade fraca ITEM_CHECKLIST (identificada por possui_item)
CREATE TABLE item_checklist (
    id_equipamento INTEGER NOT NULL,
    num_item SMALLINT NOT NULL,
    descricao VARCHAR(200) NOT NULL,
    obrigatorio BOOLEAN NOT NULL DEFAULT true,
    PRIMARY KEY (id_equipamento, num_item),
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id_equipamento) ON DELETE CASCADE
);

-- Entidade PLANO_PREVENTIVO + tem_plano (N:1)
CREATE TABLE plano_preventivo (
    id_plano SERIAL NOT NULL PRIMARY KEY,
    descricao VARCHAR(150) NOT NULL,
    periodicidade VARCHAR(10) NOT NULL,
    proxima_data DATE NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT true,
    id_equipamento INTEGER NOT NULL,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id_equipamento) ON DELETE RESTRICT,
    CHECK (periodicidade IN ('DIARIA','SEMANAL','MENSAL','TRIMESTRAL','SEMESTRAL','ANUAL'))
);

-- ---------------------------------------------------------- Manutencao

-- Entidade ORDEM_SERVICO (superclasse) + sofre, executa, distribui e avalia (1:N com atributos)
CREATE TABLE ordem_servico (
    codigo_os SERIAL NOT NULL PRIMARY KEY,
    tipo_os CHAR(1) NOT NULL,
    descricao VARCHAR(500) NOT NULL,
    data_abertura TIMESTAMP NOT NULL DEFAULT now(),
    prioridade VARCHAR(5) NOT NULL,
    prazo DATE,
    status VARCHAR(22) NOT NULL DEFAULT 'PENDENTE',
    data_inicio_execucao TIMESTAMP,
    data_fim_execucao TIMESTAMP,
    leitura_horimetro NUMERIC(10,1),
    decisao_avaliacao VARCHAR(9),
    data_avaliacao TIMESTAMP,
    justificativa VARCHAR(500),
    id_equipamento INTEGER NOT NULL,
    id_tecnico INTEGER NOT NULL,
    id_supervisor INTEGER,
    id_supervisor_avaliador INTEGER,
    FOREIGN KEY (id_equipamento) REFERENCES equipamento(id_equipamento) ON DELETE RESTRICT,
    FOREIGN KEY (id_tecnico) REFERENCES tecnico(id_usuario) ON DELETE RESTRICT,
    FOREIGN KEY (id_supervisor) REFERENCES supervisor(id_usuario) ON DELETE SET NULL,
    FOREIGN KEY (id_supervisor_avaliador) REFERENCES supervisor(id_usuario) ON DELETE SET NULL,
    CHECK (tipo_os IN ('C','P')),
    CHECK (prioridade IN ('ALTA','MEDIA','BAIXA')),
    CHECK (status IN ('PENDENTE','EM_EXECUCAO','AGUARDANDO_APROVACAO','CONCLUIDA')),
    CHECK (decisao_avaliacao IN ('APROVADA','REJEITADA')),
    CHECK (decisao_avaliacao IS DISTINCT FROM 'REJEITADA' OR justificativa IS NOT NULL),
    CHECK (data_fim_execucao IS NULL OR data_inicio_execucao IS NULL OR data_fim_execucao >= data_inicio_execucao),
    CHECK ((status = 'CONCLUIDA') = (coalesce(decisao_avaliacao, '') = 'APROVADA')),
    CHECK (decisao_avaliacao IS NULL OR (data_avaliacao IS NOT NULL AND id_supervisor_avaliador IS NOT NULL))
);

-- Subclasse MANUTENCAO_CORRETIVA
CREATE TABLE manutencao_corretiva (
    codigo_os INTEGER NOT NULL PRIMARY KEY,
    causa_falha VARCHAR(300),
    impacto_producao BOOLEAN NOT NULL DEFAULT false,
    data_hora_falha TIMESTAMP,
    FOREIGN KEY (codigo_os) REFERENCES ordem_servico(codigo_os) ON DELETE CASCADE
);

-- Subclasse MANUTENCAO_PREVENTIVA + gera (N:1)
CREATE TABLE manutencao_preventiva (
    codigo_os INTEGER NOT NULL PRIMARY KEY,
    observacao_geral TEXT,
    id_plano INTEGER,
    FOREIGN KEY (codigo_os) REFERENCES ordem_servico(codigo_os) ON DELETE CASCADE,
    FOREIGN KEY (id_plano) REFERENCES plano_preventivo(id_plano) ON DELETE SET NULL
);

-- Relacionamento N:N verifica (com atributos)
CREATE TABLE resultado_checklist (
    codigo_os INTEGER NOT NULL,
    id_equipamento INTEGER NOT NULL,
    num_item SMALLINT NOT NULL,
    resultado VARCHAR(14) NOT NULL,
    observacao VARCHAR(300),
    PRIMARY KEY (codigo_os, id_equipamento, num_item),
    FOREIGN KEY (codigo_os) REFERENCES manutencao_preventiva(codigo_os) ON DELETE CASCADE,
    FOREIGN KEY (id_equipamento, num_item) REFERENCES item_checklist(id_equipamento, num_item) ON DELETE RESTRICT,
    CHECK (resultado IN ('VERIFICADO','NAO_APLICAVEL'))
);

-- ---------------------------------------------------------- Estoque

-- Entidade PECA
CREATE TABLE peca (
    id_peca SERIAL NOT NULL PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    descricao VARCHAR(150) NOT NULL,
    unidade_medida VARCHAR(10) NOT NULL DEFAULT 'UN',
    fornecedor VARCHAR(120) NOT NULL,
    estoque_minimo INTEGER NOT NULL,
    quantidade_atual INTEGER NOT NULL,
    ativo BOOLEAN NOT NULL DEFAULT true,
    CHECK (estoque_minimo >= 0),
    CHECK (quantidade_atual >= 0)
);

-- Relacionamento N:N consome (com atributos)
CREATE TABLE baixa_peca (
    codigo_os INTEGER NOT NULL,
    id_peca INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    data_baixa TIMESTAMP NOT NULL DEFAULT now(),
    PRIMARY KEY (codigo_os, id_peca),
    FOREIGN KEY (codigo_os) REFERENCES ordem_servico(codigo_os) ON DELETE CASCADE,
    FOREIGN KEY (id_peca) REFERENCES peca(id_peca) ON DELETE RESTRICT,
    CHECK (quantidade > 0)
);

-- ---------------------------------------------------------- Notificacao

-- Entidade NOTIFICACAO + refere_os (N:1) + refere_peca (N:1)
CREATE TABLE notificacao (
    id_notificacao SERIAL NOT NULL PRIMARY KEY,
    tipo VARCHAR(15) NOT NULL,
    mensagem VARCHAR(500) NOT NULL,
    data_geracao TIMESTAMP NOT NULL DEFAULT now(),
    codigo_os INTEGER,
    id_peca INTEGER,
    FOREIGN KEY (codigo_os) REFERENCES ordem_servico(codigo_os) ON DELETE SET NULL,
    FOREIGN KEY (id_peca) REFERENCES peca(id_peca) ON DELETE SET NULL,
    CHECK (tipo IN ('PROXIMIDADE','ATRASO','ESTOQUE_MINIMO','NOVA_OS','APROVACAO','REJEICAO'))
);

-- Relacionamento N:N recebe (com atributos)
CREATE TABLE notificacao_usuario (
    id_notificacao INTEGER NOT NULL,
    id_usuario INTEGER NOT NULL,
    canal VARCHAR(10) NOT NULL,
    data_envio TIMESTAMP,
    data_leitura TIMESTAMP,
    PRIMARY KEY (id_notificacao, id_usuario),
    FOREIGN KEY (id_notificacao) REFERENCES notificacao(id_notificacao) ON DELETE CASCADE,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    CHECK (canal IN ('EMAIL','NAVEGADOR')),
    CHECK (data_leitura IS NULL OR (data_envio IS NOT NULL AND data_leitura >= data_envio))
);

-- ---------------------------------------------------------- Indices

CREATE INDEX idx_os_equipamento ON ordem_servico (id_equipamento, data_abertura);
CREATE INDEX idx_os_tecnico ON ordem_servico (id_tecnico);
CREATE INDEX idx_os_status ON ordem_servico (status);
CREATE INDEX idx_plano_proxima_data ON plano_preventivo (proxima_data);
CREATE INDEX idx_baixa_peca ON baixa_peca (id_peca, data_baixa);
CREATE INDEX idx_notificacao_data ON notificacao (tipo, data_geracao);
CREATE INDEX idx_tecnico_equipe ON tecnico (id_equipe);
