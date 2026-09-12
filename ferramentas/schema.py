# -*- coding: utf-8 -*-
"""Esquema relacional do Gerir Manutencao (SGM) - fonte unica para DER relacional, notacao formal e dicionario.

Cada coluna: (nome, tipo_postgres, nulo?, descricao, flags)
flags: PK = chave primaria, FK:tabela.coluna = chave estrangeira (FK2 = parte de FK composta),
       UK = unico, CK:regra = check, DEF:valor = default
Revisao de 11/09/2026 (alinhamento com os documentos da Karol): sem anexos, sem fornecedor como entidade,
checklist por equipamento, avaliacao unica na OS, telefone monovalorado, periodicidade fixa, 5o perfil.
"""

TABLES = [
    # ------------------------------------------------------------------ pessoas
    dict(name="usuario", modulo="Pessoas", origem="Entidade USUARIO (superclasse)", cols=[
        ("id_usuario", "SERIAL", False, "Identificador do usuario", ["PK"]),
        ("nome", "VARCHAR(120)", False, "Nome completo", []),
        ("login", "VARCHAR(60)", False, "Login de acesso", ["UK"]),
        ("senha_hash", "VARCHAR(255)", False, "Senha armazenada apenas como hash", []),
        ("email", "VARCHAR(120)", False, "E-mail para notificacoes", ["UK"]),
        ("telefone", "VARCHAR(20)", True, "Telefone de contato", []),
        ("status_2fa", "BOOLEAN", False, "Autenticacao em dois fatores habilitada", ["DEF:false"]),
        ("ativo", "BOOLEAN", False, "Usuario ativo no sistema", ["DEF:true"]),
        ("data_cadastro", "TIMESTAMP", False, "Data/hora do cadastro", ["DEF:now()"]),
        ("tipo_usuario", "CHAR(1)", False,
         "Discriminador: T=Tecnico, S=Supervisor, G=Gestor, A=Administrativo, X=Administrador do Sistema",
         ["CK:tipo_usuario IN ('T','S','G','A','X')"]),
    ]),
    dict(name="equipe", modulo="Pessoas", origem="Entidade EQUIPE + relacionamento lidera (1:N)", cols=[
        ("id_equipe", "SERIAL", False, "Identificador da equipe", ["PK"]),
        ("nome", "VARCHAR(80)", False, "Nome da equipe", ["UK"]),
        ("turno", "VARCHAR(20)", False, "Turno de trabalho (Manha, Tarde, Noite)", []),
        ("id_supervisor", "INTEGER", False, "Supervisor que lidera a equipe", ["FK:supervisor.id_usuario"]),
    ]),
    dict(name="tecnico", modulo="Pessoas", origem="Subclasse TECNICO + relacionamento pertence (N:1)", cols=[
        ("id_usuario", "INTEGER", False, "Mesmo id do usuario (heranca)", ["PK", "FK:usuario.id_usuario"]),
        ("status_operacional", "VARCHAR(12)", False, "DISPONIVEL ou OCUPADO",
         ["DEF:'DISPONIVEL'", "CK:status_operacional IN ('DISPONIVEL','OCUPADO')"]),
        ("especialidade", "VARCHAR(60)", True, "Especialidade tecnica (mecanica, eletrica...)", []),
        ("id_equipe", "INTEGER", False, "Equipe a que pertence", ["FK:equipe.id_equipe"]),
    ]),
    dict(name="supervisor", modulo="Pessoas", origem="Subclasse SUPERVISOR", cols=[
        ("id_usuario", "INTEGER", False, "Mesmo id do usuario (heranca)", ["PK", "FK:usuario.id_usuario"]),
        ("registro_profissional", "VARCHAR(30)", True, "Registro no conselho (ex.: CREA)", []),
    ]),
    dict(name="gestor", modulo="Pessoas", origem="Subclasse GESTOR", cols=[
        ("id_usuario", "INTEGER", False, "Mesmo id do usuario (heranca)", ["PK", "FK:usuario.id_usuario"]),
        ("cargo", "VARCHAR(60)", True, "Cargo executivo", []),
    ]),
    dict(name="administrativo", modulo="Pessoas", origem="Subclasse ADMINISTRATIVO", cols=[
        ("id_usuario", "INTEGER", False, "Mesmo id do usuario (heranca)", ["PK", "FK:usuario.id_usuario"]),
        ("setor", "VARCHAR(60)", True, "Setor administrativo", []),
    ]),
    dict(name="administrador_sistema", modulo="Pessoas",
         origem="Subclasse ADMINISTRADOR_SISTEMA (perfil tecnico de TI; sem atributos proprios)", cols=[
        ("id_usuario", "INTEGER", False, "Mesmo id do usuario (heranca)", ["PK", "FK:usuario.id_usuario"]),
    ]),
    # ------------------------------------------------------------------ ativos
    dict(name="linha_producao", modulo="Ativos", origem="Entidade LINHA_PRODUCAO", cols=[
        ("id_linha", "SERIAL", False, "Identificador da linha", ["PK"]),
        ("nome", "VARCHAR(80)", False, "Nome da linha de producao", ["UK"]),
        ("setor", "VARCHAR(80)", True, "Setor/galpao da fabrica", []),
    ]),
    dict(name="equipamento", modulo="Ativos", origem="Entidade EQUIPAMENTO + fica_na_linha (N:1)", cols=[
        ("id_equipamento", "SERIAL", False, "Identificador do equipamento", ["PK"]),
        ("codigo", "VARCHAR(20)", False, "Codigo interno (patrimonio), usado na busca", ["UK"]),
        ("nome", "VARCHAR(100)", False, "Nome do equipamento", []),
        ("fabricante", "VARCHAR(80)", True, "Fabricante", []),
        ("modelo", "VARCHAR(80)", False, "Modelo do equipamento", []),
        ("numero_serie", "VARCHAR(60)", False, "Numero de serie do fabricante", ["UK"]),
        ("localizacao", "VARCHAR(120)", True, "Localizacao fisica na fabrica", []),
        ("criticidade", "VARCHAR(5)", False, "ALTA, MEDIA ou BAIXA", ["CK:criticidade IN ('ALTA','MEDIA','BAIXA')"]),
        ("horimetro_atual", "NUMERIC(10,1)", False, "Ultima leitura de horas de operacao", ["DEF:0"]),
        ("data_aquisicao", "DATE", True, "Data de aquisicao", []),
        ("ativo", "BOOLEAN", False, "Equipamento em operacao", ["DEF:true"]),
        ("id_linha", "INTEGER", False, "Linha de producao", ["FK:linha_producao.id_linha"]),
    ]),
    dict(name="item_checklist", modulo="Ativos", origem="Entidade fraca ITEM_CHECKLIST (identificada por possui_item)", cols=[
        ("id_equipamento", "INTEGER", False, "Equipamento dono do checklist", ["PK", "FK:equipamento.id_equipamento"]),
        ("num_item", "SMALLINT", False, "Numero sequencial do item (chave parcial)", ["PK"]),
        ("descricao", "VARCHAR(200)", False, "Descricao da verificacao", []),
        ("obrigatorio", "BOOLEAN", False, "Item obrigatorio para concluir a preventiva", ["DEF:true"]),
    ]),
    dict(name="plano_preventivo", modulo="Ativos", origem="Entidade PLANO_PREVENTIVO + tem_plano (N:1)", cols=[
        ("id_plano", "SERIAL", False, "Identificador do plano", ["PK"]),
        ("descricao", "VARCHAR(150)", False, "Descricao (ex.: lubrificacao mensal)", []),
        ("periodicidade", "VARCHAR(10)", False, "DIARIA, SEMANAL, MENSAL, TRIMESTRAL, SEMESTRAL ou ANUAL",
         ["CK:periodicidade IN ('DIARIA','SEMANAL','MENSAL','TRIMESTRAL','SEMESTRAL','ANUAL')"]),
        ("proxima_data", "DATE", False, "Proximo vencimento calculado pela periodicidade", []),
        ("ativo", "BOOLEAN", False, "Plano em vigor", ["DEF:true"]),
        ("id_equipamento", "INTEGER", False, "Equipamento do plano", ["FK:equipamento.id_equipamento"]),
    ]),
    # ------------------------------------------------------------------ manutencao
    dict(name="ordem_servico", modulo="Manutencao",
         origem="Entidade ORDEM_SERVICO (superclasse) + sofre, executa, distribui e avalia (1:N com atributos)", cols=[
        ("codigo_os", "SERIAL", False, "Codigo da OS", ["PK"]),
        ("tipo_os", "CHAR(1)", False, "Discriminador: C=Corretiva, P=Preventiva", ["CK:tipo_os IN ('C','P')"]),
        ("descricao", "VARCHAR(500)", False, "Descricao do servico/falha (ate 500 caracteres)", []),
        ("data_abertura", "TIMESTAMP", False, "Data/hora de abertura (automatica)", ["DEF:now()"]),
        ("prioridade", "VARCHAR(5)", False, "ALTA, MEDIA ou BAIXA", ["CK:prioridade IN ('ALTA','MEDIA','BAIXA')"]),
        ("prazo", "DATE", True, "Prazo de entrega", []),
        ("status", "VARCHAR(22)", False, "PENDENTE, EM_EXECUCAO, AGUARDANDO_APROVACAO, CONCLUIDA",
         ["DEF:'PENDENTE'", "CK:status IN ('PENDENTE','EM_EXECUCAO','AGUARDANDO_APROVACAO','CONCLUIDA')"]),
        ("data_inicio_execucao", "TIMESTAMP", True, "Inicio da execucao pelo tecnico", []),
        ("data_fim_execucao", "TIMESTAMP", True, "Fim da execucao (base do MTTR e das horas trabalhadas)", []),
        ("leitura_horimetro", "NUMERIC(10,1)", True, "Horimetro informado pelo tecnico na manutencao", []),
        ("decisao_avaliacao", "VARCHAR(9)", True, "APROVADA ou REJEITADA (atributo do relacionamento avalia)",
         ["CK:decisao_avaliacao IN ('APROVADA','REJEITADA')"]),
        ("data_avaliacao", "TIMESTAMP", True, "Data/hora da decisao do supervisor", []),
        ("justificativa", "VARCHAR(500)", True, "Obrigatoria quando REJEITADA",
         ["CK:decisao_avaliacao IS DISTINCT FROM 'REJEITADA' OR justificativa IS NOT NULL"]),
        ("id_equipamento", "INTEGER", False, "Equipamento atendido", ["FK:equipamento.id_equipamento"]),
        ("id_tecnico", "INTEGER", False, "Tecnico responsavel", ["FK:tecnico.id_usuario"]),
        ("id_supervisor", "INTEGER", True, "Supervisor que distribuiu (nulo se aberta em campo)", ["FK:supervisor.id_usuario"]),
        ("id_supervisor_avaliador", "INTEGER", True, "Supervisor que aprovou/rejeitou", ["FK:supervisor.id_usuario"]),
    ]),
    dict(name="manutencao_corretiva", modulo="Manutencao", origem="Subclasse MANUTENCAO_CORRETIVA", cols=[
        ("codigo_os", "INTEGER", False, "Mesma OS (heranca)", ["PK", "FK:ordem_servico.codigo_os"]),
        ("causa_falha", "VARCHAR(300)", True, "Causa identificada da falha", []),
        ("impacto_producao", "BOOLEAN", False, "Houve parada de producao", ["DEF:false"]),
        ("data_hora_falha", "TIMESTAMP", True, "Momento da falha (base do MTBF)", []),
    ]),
    dict(name="manutencao_preventiva", modulo="Manutencao", origem="Subclasse MANUTENCAO_PREVENTIVA + gera (N:1)", cols=[
        ("codigo_os", "INTEGER", False, "Mesma OS (heranca)", ["PK", "FK:ordem_servico.codigo_os"]),
        ("observacao_geral", "TEXT", True, "Observacoes complementares do tecnico", []),
        ("id_plano", "INTEGER", True, "Plano que gerou a OS (nulo se avulsa)", ["FK:plano_preventivo.id_plano"]),
    ]),
    dict(name="resultado_checklist", modulo="Manutencao", origem="Relacionamento N:N verifica (com atributos)", cols=[
        ("codigo_os", "INTEGER", False, "OS preventiva", ["PK", "FK:manutencao_preventiva.codigo_os"]),
        ("id_equipamento", "INTEGER", False, "Equipamento do item", ["PK", "FK2:item_checklist.id_equipamento"]),
        ("num_item", "SMALLINT", False, "Item verificado", ["PK", "FK2:item_checklist.num_item"]),
        ("resultado", "VARCHAR(14)", False, "VERIFICADO ou NAO_APLICAVEL", ["CK:resultado IN ('VERIFICADO','NAO_APLICAVEL')"]),
        ("observacao", "VARCHAR(300)", True, "Observacao do item", []),
    ]),
    # ------------------------------------------------------------------ estoque
    dict(name="peca", modulo="Estoque", origem="Entidade PECA", cols=[
        ("id_peca", "SERIAL", False, "Identificador da peca", ["PK"]),
        ("codigo", "VARCHAR(30)", False, "Codigo unico da peca", ["UK"]),
        ("descricao", "VARCHAR(150)", False, "Descricao tecnica", []),
        ("unidade_medida", "VARCHAR(10)", False, "UN, KG, L, M...", ["DEF:'UN'"]),
        ("fornecedor", "VARCHAR(120)", False, "Nome do fornecedor homologado", []),
        ("estoque_minimo", "INTEGER", False, "Quantidade minima de seguranca", ["CK:estoque_minimo >= 0"]),
        ("quantidade_atual", "INTEGER", False, "Saldo atual em estoque", ["CK:quantidade_atual >= 0"]),
        ("ativo", "BOOLEAN", False, "Peca ativa no catalogo", ["DEF:true"]),
    ]),
    dict(name="baixa_peca", modulo="Estoque", origem="Relacionamento N:N consome (com atributos)", cols=[
        ("codigo_os", "INTEGER", False, "OS que consumiu", ["PK", "FK:ordem_servico.codigo_os"]),
        ("id_peca", "INTEGER", False, "Peca consumida", ["PK", "FK:peca.id_peca"]),
        ("quantidade", "INTEGER", False, "Quantidade baixada", ["CK:quantidade > 0"]),
        ("data_baixa", "TIMESTAMP", False, "Data/hora da baixa", ["DEF:now()"]),
    ]),
    # ------------------------------------------------------------------ notificacao
    dict(name="notificacao", modulo="Notificacao", origem="Entidade NOTIFICACAO + refere_os (N:1) + refere_peca (N:1)", cols=[
        ("id_notificacao", "SERIAL", False, "Identificador", ["PK"]),
        ("tipo", "VARCHAR(15)", False, "PROXIMIDADE, ATRASO, ESTOQUE_MINIMO, NOVA_OS, APROVACAO, REJEICAO",
         ["CK:tipo IN ('PROXIMIDADE','ATRASO','ESTOQUE_MINIMO','NOVA_OS','APROVACAO','REJEICAO')"]),
        ("mensagem", "VARCHAR(500)", False, "Texto da notificacao", []),
        ("data_geracao", "TIMESTAMP", False, "Data/hora de geracao (usada na supressao de duplicatas em 24 h)", ["DEF:now()"]),
        ("codigo_os", "INTEGER", True, "OS relacionada (se houver)", ["FK:ordem_servico.codigo_os"]),
        ("id_peca", "INTEGER", True, "Peca relacionada (se houver)", ["FK:peca.id_peca"]),
    ]),
    dict(name="notificacao_usuario", modulo="Notificacao", origem="Relacionamento N:N recebe (com atributos)", cols=[
        ("id_notificacao", "INTEGER", False, "Notificacao enviada", ["PK", "FK:notificacao.id_notificacao"]),
        ("id_usuario", "INTEGER", False, "Destinatario", ["PK", "FK:usuario.id_usuario"]),
        ("canal", "VARCHAR(10)", False, "EMAIL ou NAVEGADOR", ["CK:canal IN ('EMAIL','NAVEGADOR')"]),
        ("data_envio", "TIMESTAMP", True, "Data/hora do envio", []),
        ("data_leitura", "TIMESTAMP", True, "Data/hora da leitura", []),
    ]),
]


def flags(col):
    return col[4]


def is_pk(col):
    return "PK" in flags(col)


def fk_target(col):
    for f in flags(col):
        if f.startswith("FK:") or f.startswith("FK2:"):
            return f.split(":", 1)[1]
    return None


def formal(table):
    """Notacao formal: lista de (nome_exibido, eh_pk). FK prefixada com #."""
    parts = []
    for c in table["cols"]:
        n = c[0]
        if fk_target(c):
            n = "#" + n
        parts.append((n, is_pk(c)))
    return parts


def fks(table):
    """Lista de (colunas_locais, tabela_ref, colunas_ref). FK2 agrupa a FK composta."""
    simple, comp = [], []
    for c in table["cols"]:
        t = fk_target(c)
        if not t:
            continue
        ref_t, ref_c = t.split(".")
        if any(f.startswith("FK2:") for f in flags(c)):
            comp.append((c[0], ref_t, ref_c))
        else:
            simple.append(([c[0]], ref_t, [ref_c]))
    if comp:
        simple.append(([c for c, _, _ in comp], comp[0][1], [r for _, _, r in comp]))
    return simple
