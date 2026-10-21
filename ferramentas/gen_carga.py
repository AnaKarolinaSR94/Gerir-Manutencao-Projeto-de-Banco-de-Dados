# -*- coding: utf-8 -*-
"""Gera sql/02_insercao.sql - carga de dados de exemplo do Gerir Manutencao (SGM).

Os dados sao ficticios, mas coerentes com as regras de negocio:
  - toda OS CONCLUIDA foi APROVADA; OS rejeitada volta para EM_EXECUCAO com justificativa;
  - tecnico com OS EM_EXECUCAO fica OCUPADO; os demais ficam DISPONIVEL;
  - o horimetro de cada equipamento cresce a cada manutencao e horimetro_atual = ultima leitura;
  - quantidade_atual da peca = estoque inicial - soma das baixas;
  - alerta ESTOQUE_MINIMO gerado na baixa em que a peca atingiu o minimo.
Data de referencia ("hoje") da carga: 19/10/2026.
Rodar a partir da raiz do repositorio:  python ferramentas/gen_carga.py
"""
import random
from datetime import datetime, timedelta, date

random.seed(2026)
HOJE = datetime(2026, 10, 19, 8, 0)
OUT = []


def q(v):
    if v is None:
        return "NULL"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return str(v)
    if isinstance(v, datetime):
        return f"TIMESTAMP '{v:%Y-%m-%d %H:%M}'"
    if isinstance(v, date):
        return f"DATE '{v:%Y-%m-%d}'"
    return "'" + str(v).replace("'", "''") + "'"


def ins(table, cols, rows, titulo=None):
    OUT.append(f"-- {titulo or table}")
    for r in rows:
        OUT.append(f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(q(v) for v in r)});")
    OUT.append("")


# ------------------------------------------------------------------ pessoas
USUARIOS = [
    # id, nome, login, telefone, 2fa, tipo, cadastro
    (1, "Ricardo Almeida Prado", "ricardo.prado", "(62) 99810-1001", True, "X", datetime(2026, 1, 5, 9, 0)),
    (2, "Fernanda Souza Lima", "fernanda.lima", "(62) 99810-1002", True, "S", datetime(2026, 1, 6, 9, 0)),
    (3, "Carlos Eduardo Ramos", "carlos.ramos", "(62) 99810-1003", True, "S", datetime(2026, 1, 6, 9, 30)),
    (4, "Juliana Pereira Costa", "juliana.costa", "(62) 99810-1004", False, "S", datetime(2026, 1, 6, 10, 0)),
    (5, "Marcos Vinicius Teles", "marcos.teles", "(62) 99810-1005", True, "G", datetime(2026, 1, 7, 9, 0)),
    (6, "Patricia Gomes Andrade", "patricia.andrade", "(62) 99810-1006", True, "G", datetime(2026, 1, 7, 9, 30)),
    (7, "Luciana Martins Rocha", "luciana.rocha", "(62) 99810-1007", False, "A", datetime(2026, 1, 8, 9, 0)),
    (8, "Rafael Oliveira Nunes", "rafael.nunes", "(62) 3201-1008", False, "A", datetime(2026, 1, 8, 9, 30)),
    (9, "Joao Batista Ferreira", "joao.ferreira", "(62) 99810-1009", False, "T", datetime(2026, 1, 12, 7, 0)),
    (10, "Antonio Carlos Silva", "antonio.silva", "(62) 99810-1010", False, "T", datetime(2026, 1, 12, 7, 10)),
    (11, "Pedro Henrique Santos", "pedro.santos", "(62) 99810-1011", False, "T", datetime(2026, 1, 12, 7, 20)),
    (12, "Lucas Gabriel Moreira", "lucas.moreira", None, False, "T", datetime(2026, 1, 12, 7, 30)),
    (13, "Mariana Alves Barbosa", "mariana.barbosa", "(62) 99810-1013", False, "T", datetime(2026, 1, 12, 13, 0)),
    (14, "Thiago Ribeiro Dias", "thiago.dias", "(62) 99810-1014", False, "T", datetime(2026, 1, 12, 13, 10)),
    (15, "Bruno Cesar Cardoso", "bruno.cardoso", "(62) 99810-1015", False, "T", datetime(2026, 1, 12, 13, 20)),
    (16, "Rodrigo Mendes Freitas", "rodrigo.freitas", None, False, "T", datetime(2026, 1, 12, 13, 30)),
    (17, "Diego Araujo Pinto", "diego.pinto", "(62) 99810-1017", False, "T", datetime(2026, 1, 12, 22, 0)),
    (18, "Felipe Augusto Castro", "felipe.castro", "(62) 99810-1018", False, "T", datetime(2026, 1, 12, 22, 10)),
    (19, "Camila Rodrigues Teixeira", "camila.teixeira", "(62) 99810-1019", False, "T", datetime(2026, 1, 12, 22, 20)),
    (20, "Gustavo Henrique Lopes", "gustavo.lopes", "(62) 99810-1020", False, "T", datetime(2026, 10, 13, 22, 0)),
]
# hash ficticio (o sistema guarda so o hash, nunca a senha)
HASH = "$2b$12$Q9yQ0Jt1oT7xX0r8m0bQe.0f3m1H9w5mA6dZkq2b8sQ1o7cJ8k5yC"
TIPO_NOME = {"X": "Administrador do Sistema", "S": "Supervisor", "G": "Gestor", "A": "Administrativo", "T": "Tecnico"}

EQUIPES = [  # id, nome, turno, supervisor
    (1, "Equipe Alfa", "Manha", 2),
    (2, "Equipe Beta", "Tarde", 3),
    (3, "Equipe Gama", "Noite", 4),
]
TECNICOS = {  # id -> (especialidade, equipe)
    9: ("Mecanica", 1), 10: ("Eletrica", 1), 11: ("Hidraulica", 1), 12: ("Mecanica", 1),
    13: ("Eletrica", 2), 14: ("Mecanica", 2), 15: ("Automacao", 2), 16: ("Pneumatica", 2),
    17: ("Mecanica", 3), 18: ("Eletrica", 3), 19: ("Automacao", 3), 20: ("Hidraulica", 3),
}
SUP_DA_EQUIPE = {e[0]: e[3] for e in EQUIPES}

# ------------------------------------------------------------------ ativos
LINHAS = [
    (1, "Linha 1 - Usinagem", "Galpao A"),
    (2, "Linha 2 - Estamparia", "Galpao A"),
    (3, "Linha 3 - Pintura", "Galpao B"),
    (4, "Linha 4 - Montagem e Embalagem", "Galpao C"),
]
EQUIPAMENTOS = [
    # id, codigo, nome, fabricante, modelo, serie, localizacao, criticidade, aquisicao, ativo, linha
    (1, "EQ-001", "Torno CNC", "Romi", "GL 240", "RM-GL240-88213", "Galpao A - Box 1", "ALTA", date(2019, 3, 11), True, 1),
    (2, "EQ-002", "Centro de Usinagem Vertical", "Romi", "D 800", "RM-D800-55102", "Galpao A - Box 2", "ALTA", date(2020, 7, 2), True, 1),
    (3, "EQ-003", "Fresadora Ferramenteira", "Diplomat", "FVF 3000", "DP-FVF-30417", "Galpao A - Box 3", "MEDIA", date(2015, 5, 20), True, 1),
    (4, "EQ-004", "Retificadora Plana", "Mello", "P36", "ML-P36-11908", "Galpao A - Box 4", "BAIXA", date(2012, 9, 14), True, 1),
    (5, "EQ-005", "Prensa Hidraulica 250 t", "Schuler", "PH-250", "SC-PH250-77120", "Galpao A - Box 6", "ALTA", date(2018, 2, 8), True, 2),
    (6, "EQ-006", "Prensa Excentrica 80 t", "Jundiai", "PE-80", "JD-PE80-40031", "Galpao A - Box 7", "MEDIA", date(2014, 11, 3), True, 2),
    (7, "EQ-007", "Guilhotina Hidraulica", "Newton", "GHN 3006", "NW-GHN-90876", "Galpao A - Box 8", "MEDIA", date(2016, 4, 25), True, 2),
    (8, "EQ-008", "Cabine de Pintura", "Eisenmann", "CP-4000", "EI-CP4000-2231", "Galpao B - Setor 1", "ALTA", date(2021, 1, 19), True, 3),
    (9, "EQ-009", "Estufa de Cura", "Eisenmann", "EC-220", "EI-EC220-2290", "Galpao B - Setor 2", "MEDIA", date(2021, 1, 19), True, 3),
    (10, "EQ-010", "Compressor de Ar Parafuso", "Atlas Copco", "GA 37", "AC-GA37-61544", "Galpao B - Casa de Maquinas", "ALTA", date(2017, 8, 30), True, 3),
    (11, "EQ-011", "Esteira Transportadora", "Transmaq", "ET-12", "TM-ET12-33019", "Galpao C - Linha principal", "MEDIA", date(2019, 10, 7), True, 4),
    (12, "EQ-012", "Robo de Solda", "ABB", "IRB 2600", "ABB-2600-77810", "Galpao C - Celula 1", "ALTA", date(2022, 6, 13), True, 4),
    (13, "EQ-013", "Seladora Automatica", "Selamaq", "SA-500", "SM-SA500-10288", "Galpao C - Embalagem", "BAIXA", date(2020, 3, 3), True, 4),
    (14, "EQ-014", "Empilhadeira Eletrica", "Toyota", "8FBE20", "TY-8FBE-55419", "Galpao C - Expedicao", "BAIXA", date(2023, 2, 27), True, 4),
    (15, "EQ-015", "Furadeira de Coluna", "Kone", "KFC-32", "KN-KFC32-01002", "Galpao A - Deposito", "BAIXA", date(2008, 6, 1), False, 1),
]
HORIMETRO_INICIAL = {e[0]: random.randint(800, 9000) for e in EQUIPAMENTOS}

CHECKLIST_BASE = {
    1: ["Verificar nivel do oleo de lubrificacao", "Limpar cavacos do barramento", "Conferir aperto da placa e castanhas",
        "Testar parada de emergencia", "Verificar folga do fuso"],
    2: ["Verificar nivel do fluido de corte", "Inspecionar magazine de ferramentas", "Conferir pressao pneumatica",
        "Testar parada de emergencia"],
    3: ["Lubrificar guias e fusos", "Verificar correias", "Testar parada de emergencia"],
    4: ["Verificar rebolo (trincas e balanceamento)", "Limpar sistema de refrigeracao", "Testar mesa magnetica"],
    5: ["Verificar nivel e temperatura do oleo hidraulico", "Inspecionar mangueiras e conexoes", "Testar cortina de luz",
        "Verificar pressao de trabalho", "Testar comando bimanual"],
    6: ["Lubrificar biela e guias", "Verificar embreagem e freio", "Testar comando bimanual"],
    7: ["Verificar afiacao das laminas", "Inspecionar sistema hidraulico", "Testar protecao frontal"],
    8: ["Trocar ou limpar filtros de ar", "Verificar exaustores", "Limpar bicos da pistola", "Conferir iluminacao interna"],
    9: ["Verificar queimadores", "Conferir controle de temperatura", "Inspecionar vedacao das portas"],
    10: ["Drenar condensado", "Verificar nivel de oleo", "Trocar elemento do filtro de ar", "Conferir pressao de descarga"],
    11: ["Verificar tensao e alinhamento da correia", "Lubrificar rolamentos dos roletes", "Testar parada de emergencia"],
    12: ["Verificar cabos e conectores", "Limpar bocal e trocar bico de contato", "Calibrar ponto zero (TCP)",
         "Testar barreiras de seguranca"],
    13: ["Limpar resistencias de selagem", "Verificar teflon da barra", "Conferir temperatura de selagem"],
    14: ["Verificar carga e eletrolito da bateria", "Inspecionar garfos e correntes", "Testar freio e buzina"],
    15: ["Lubrificar coluna", "Verificar mandril"],
}
CHECKLIST = []  # (equip, num, descricao, obrigatorio)
for eq, itens in CHECKLIST_BASE.items():
    for i, d in enumerate(itens, 1):
        CHECKLIST.append((eq, i, d, not (i == len(itens) and len(itens) >= 4)))

PER_DIAS = {"DIARIA": 1, "SEMANAL": 7, "MENSAL": 30, "TRIMESTRAL": 90, "SEMESTRAL": 180, "ANUAL": 365}
PLANOS = [  # id, descricao, periodicidade, equipamento, ativo
    (1, "Lubrificacao e inspecao mensal do torno", "MENSAL", 1, True),
    (2, "Revisao trimestral do centro de usinagem", "TRIMESTRAL", 2, True),
    (3, "Inspecao mensal da fresadora", "MENSAL", 3, True),
    (4, "Revisao semestral da retificadora", "SEMESTRAL", 4, True),
    (5, "Inspecao mensal do sistema hidraulico da prensa", "MENSAL", 5, True),
    (6, "Revisao anual completa da prensa hidraulica", "ANUAL", 5, True),
    (7, "Lubrificacao mensal da prensa excentrica", "MENSAL", 6, True),
    (8, "Inspecao trimestral da guilhotina", "TRIMESTRAL", 7, True),
    (9, "Troca de filtros da cabine de pintura", "MENSAL", 8, True),
    (10, "Inspecao trimestral da estufa", "TRIMESTRAL", 9, True),
    (11, "Drenagem e inspecao mensal do compressor", "MENSAL", 10, True),
    (12, "Inspecao mensal da esteira", "MENSAL", 11, True),
    (13, "Manutencao mensal do robo de solda", "MENSAL", 12, True),
    (14, "Inspecao trimestral da seladora", "TRIMESTRAL", 13, True),
    (15, "Revisao trimestral da empilhadeira", "TRIMESTRAL", 14, True),
    (16, "Lubrificacao semestral da furadeira (equipamento desativado)", "SEMESTRAL", 15, False),
]

# ------------------------------------------------------------------ estoque
PECAS = [  # id, codigo, descricao, unidade, fornecedor, minimo, inicial
    (1, "PC-ROL-6205", "Rolamento rigido de esferas 6205-2RS", "UN", "SKF do Brasil", 10, 40),
    (2, "PC-COR-A42", "Correia em V perfil A-42", "UN", "Gates do Brasil", 6, 18),
    (3, "PC-OLH-68", "Oleo hidraulico ISO VG 68", "L", "Lubrax Distribuidora", 40, 220),
    (4, "PC-GRX-EP2", "Graxa de litio EP2", "KG", "Lubrax Distribuidora", 5, 25),
    (5, "PC-FIL-AR37", "Elemento filtrante de ar para compressor GA 37", "UN", "Atlas Copco", 2, 6),
    (6, "PC-FIL-CAB", "Filtro de teto para cabine de pintura", "UN", "Eisenmann Pecas", 4, 16),
    (7, "PC-RET-H60", "Kit de vedacao para cilindro hidraulico 60 mm", "UN", "Parker Hannifin", 2, 8),
    (8, "PC-CON-24V", "Contator tripolar 24 Vcc 18 A", "UN", "WEG Automacao", 3, 10),
    (9, "PC-SEN-IND", "Sensor indutivo M18 PNP", "UN", "Sick Sensores", 3, 12),
    (10, "PC-BIC-SOL", "Bico de contato para tocha de solda 1,2 mm", "UN", "ABB Pecas", 20, 60),
    (11, "PC-RES-SEL", "Resistencia de selagem 500 mm", "UN", "Selamaq", 2, 6),
    (12, "PC-FUS-10A", "Fusivel NH 10 A", "UN", "WEG Automacao", 10, 30),
    (13, "PC-MAN-HID", "Mangueira hidraulica 1/2 pol. (metro)", "M", "Parker Hannifin", 5, 30),
    (14, "PC-BAT-48V", "Bateria tracionaria 48 V", "UN", "Moura Baterias", 1, 2),
    (15, "PC-LAM-GUI", "Jogo de laminas para guilhotina 3 m", "UN", "Newton Pecas", 1, 2),
]
PECAS_POR_EQUIP = {
    1: [1, 2, 4, 9, 12], 2: [1, 4, 8, 9], 3: [1, 2, 4], 4: [1, 2, 12], 5: [3, 7, 13, 9],
    6: [1, 4, 8], 7: [3, 13], 8: [6, 8, 12], 9: [8, 12, 9], 10: [5, 3, 1], 11: [1, 2, 4, 9],
    12: [10, 8, 9], 13: [11, 12], 14: [12, 8],
}

FALHAS = {
    1: [("Torno parou com alarme de sobrecarga no eixo arvore", "Rolamento do eixo arvore desgastado"),
        ("Ruido anormal no cabecote", "Correia do cabecote com desgaste")],
    2: [("Troca automatica de ferramenta travando", "Sensor do magazine desalinhado"),
        ("Fuso Z com vibracao excessiva", "Falta de lubrificacao no fuso")],
    3: [("Mesa da fresadora sem avanco automatico", "Correia rompida")],
    4: [("Mesa magnetica sem fixacao", "Fusivel queimado no circuito da mesa")],
    5: [("Vazamento de oleo no cilindro principal", "Vedacao do cilindro danificada"),
        ("Prensa sem pressao de trabalho", "Mangueira hidraulica rompida"),
        ("Cortina de luz desarmando sem obstaculo", "Sensor da cortina desalinhado")],
    6: [("Freio da prensa com escorregamento", "Contator do freio com contato gasto")],
    7: [("Corte com rebarba excessiva", "Laminas sem afiacao"), ("Vazamento na unidade hidraulica", "Mangueira ressecada")],
    8: [("Exaustor da cabine desligando", "Contator do exaustor queimado"),
        ("Pintura com particulas", "Filtros de teto saturados")],
    9: [("Estufa nao atinge a temperatura de cura", "Sensor de temperatura com defeito")],
    10: [("Compressor desarmando por alta temperatura", "Filtro de ar obstruido"),
         ("Pressao de linha abaixo do normal", "Vazamento no separador ar/oleo")],
    11: [("Esteira parando com a correia patinando", "Correia frouxa e rolamento travado"),
         ("Esteira nao liga", "Fusivel queimado")],
    12: [("Robo com falha de arco na solda", "Bico de contato desgastado"),
         ("Robo parou com erro de comunicacao", "Conector do cabo de sinal danificado")],
    13: [("Selagem fraca nas embalagens", "Resistencia de selagem queimada")],
    14: [("Empilhadeira sem autonomia", "Fusivel de potencia queimado")],
}
# peso de falhas por equipamento (gera um ranking de maquinas criticas)
PESO_FALHA = {1: 6, 2: 3, 3: 1, 4: 1, 5: 8, 6: 2, 7: 2, 8: 5, 9: 1, 10: 6, 11: 4, 12: 3, 13: 1, 14: 1}

# ------------------------------------------------------------------ ordens de servico
tecs_por_equipe = {}
for t, (_, e) in TECNICOS.items():
    if t != 20:  # Gustavo entrou em 13/10/2026 e ainda nao executou nenhuma OS
        tecs_por_equipe.setdefault(e, []).append(t)
equipe_do_equip = {1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 2, 7: 2, 8: 2, 9: 3, 10: 3, 11: 3, 12: 3, 13: 1, 14: 2}
INICIO = datetime(2026, 4, 1, 7, 0)
ordens = []  # dicionarios

def novo_tecnico(eq):
    e = equipe_do_equip[eq]
    if random.random() < 0.2:  # as vezes uma OS vai para outra equipe
        e = random.choice([1, 2, 3])
    return random.choice(tecs_por_equipe[e])

# corretivas
eqs = [e for e, p in PESO_FALHA.items() for _ in range(p)]
for _ in range(44):
    eq = random.choice(eqs)
    falha = INICIO + timedelta(minutes=random.randint(0, int((HOJE - INICIO).total_seconds() // 60) - 600))
    desc, causa = random.choice(FALHAS[eq])
    ordens.append(dict(tipo="C", eq=eq, falha=falha, abertura=falha + timedelta(minutes=random.randint(5, 90)),
                       desc=desc, causa=causa, impacto=random.random() < 0.55))

# preventivas: geradas pelos planos a partir de 01/04/2026, a cada periodo
for pid, pdesc, per, eq, ativo in PLANOS:
    if not ativo:
        continue
    dias = PER_DIAS[per]
    venc = INICIO.date() + timedelta(days=random.randint(0, min(dias, 40) - 1))
    while venc <= HOJE.date() + timedelta(days=10):
        abertura = datetime.combine(venc - timedelta(days=3), datetime.min.time()) + timedelta(hours=7)
        if abertura < HOJE:
            ordens.append(dict(tipo="P", eq=eq, plano=pid, abertura=abertura, prazo=venc, desc=pdesc))
        venc += timedelta(days=dias)

ordens.sort(key=lambda o: o["abertura"])

# define execucao/status
for o in ordens:
    o["tec"] = novo_tecnico(o["eq"])
    sup = SUP_DA_EQUIPE[TECNICOS[o["tec"]][1]]
    if o["tipo"] == "C":
        o["prioridade"] = "ALTA" if o["impacto"] else random.choice(["MEDIA", "BAIXA", "ALTA"])
        o["prazo"] = (o["abertura"] + timedelta(days={"ALTA": 1, "MEDIA": 3, "BAIXA": 7}[o["prioridade"]])).date()
        o["sup"] = None if random.random() < 0.35 else sup  # aberta em campo pelo tecnico
        espera = timedelta(minutes=random.randint(10, 180 if o["prioridade"] == "ALTA" else 1440))
        duracao = timedelta(minutes=random.randint(45, 480))
    else:
        o["prioridade"] = random.choice(["MEDIA", "MEDIA", "BAIXA", "ALTA"])
        o["sup"] = sup
        espera = timedelta(days=random.randint(0, 4), hours=random.randint(0, 6))
        duracao = timedelta(minutes=random.randint(40, 240))
    o["inicio"] = o["abertura"] + espera
    o["fim"] = o["inicio"] + duracao
    o["avaliador"] = sup
    o["aval"] = o["fim"] + timedelta(hours=random.randint(1, 20))
    idade = HOJE - o["abertura"]
    if o["inicio"] > HOJE:
        o["status"] = "PENDENTE"
    elif o["fim"] > HOJE or (idade < timedelta(days=2) and random.random() < 0.5):
        o["status"] = "EM_EXECUCAO"
    elif o["aval"] > HOJE or (idade < timedelta(days=5) and random.random() < 0.5):
        o["status"] = "AGUARDANDO_APROVACAO"
    else:
        o["status"] = "CONCLUIDA"

# OS recentes em andamento: o fluxo Pendente -> Em Execucao -> Aguardando Aprovacao -> Concluida
# (ou Rejeitada -> volta para Em Execucao) precisa aparecer na carga
recentes = sorted([o for o in ordens if o["status"] == "CONCLUIDA" and o["abertura"] > HOJE - timedelta(days=25)],
                  key=lambda o: o["abertura"], reverse=True)
atrasada = next(o for o in recentes if o["tipo"] == "P")
atrasada["status"] = "PENDENTE_ATRASADA"  # preventiva vencida que ninguem iniciou
recentes.remove(atrasada)
justs = ["Checklist sem observacao sobre o vazamento relatado pela producao",
         "Peca trocada nao confere com a falha descrita; refazer diagnostico"]
for i, o in enumerate(recentes[:7]):
    if i < 2:
        o["status"] = "EM_EXECUCAO"
        o["inicio"] = max(o["inicio"], HOJE - timedelta(hours=random.randint(2, 20)))
    elif i < 5:
        o["status"] = "AGUARDANDO_APROVACAO"
    else:
        o["status"] = "REJEITADA"
        o["just"] = justs[i - 5]

# codigos, horimetro, checklist, baixas
estoque = {p[0]: p[6] for p in PECAS}
minimo = {p[0]: p[5] for p in PECAS}
horim = dict(HORIMETRO_INICIAL)
baixas, resultados, notifs = [], [], []
ITENS = {}
for eq, n, d, ob in CHECKLIST:
    ITENS.setdefault(eq, []).append(n)
for codigo, o in enumerate(ordens, 1):
    o["codigo"] = codigo
    st = o["status"]
    executou = st not in ("PENDENTE", "PENDENTE_ATRASADA")
    if not executou:
        o["inicio"] = o["fim"] = None
    elif st in ("EM_EXECUCAO",):
        o["fim"] = None
    if executou:
        horim[o["eq"]] += random.randint(60, 140)  # avanca com o uso
        o["horim"] = round(horim[o["eq"]] + random.random(), 1)
        horim[o["eq"]] = o["horim"]
    else:
        o["horim"] = None
    # checklist das preventivas
    if o["tipo"] == "P" and executou:
        itens = ITENS[o["eq"]]
        feitos = itens if o["fim"] else itens[: max(1, len(itens) // 2)]
        for n in feitos:
            res = "NAO_APLICAVEL" if random.random() < 0.08 else "VERIFICADO"
            obs = None
            if res == "NAO_APLICAVEL":
                obs = "Item nao se aplica nesta intervencao"
            elif random.random() < 0.12:
                obs = random.choice(["Desgaste leve, acompanhar na proxima", "Ajustado durante a inspecao",
                                     "Limpeza realizada", "Dentro do especificado"])
            resultados.append((codigo, o["eq"], n, res, obs))
    # baixas de pecas
    if executou and o["eq"] in PECAS_POR_EQUIP:
        qtd_itens = random.choice([0, 1, 1, 2, 2, 3]) if o["tipo"] == "C" else random.choice([0, 0, 1, 1, 2])
        for pid in random.sample(PECAS_POR_EQUIP[o["eq"]], min(qtd_itens, len(PECAS_POR_EQUIP[o["eq"]]))):
            un = next(p[3] for p in PECAS if p[0] == pid)
            qtd = random.randint(5, 20) if un == "L" else random.randint(1, 3)
            quando = o["inicio"] + timedelta(minutes=random.randint(10, 40))
            baixas.append((codigo, pid, qtd, quando))

# saldo final desejado por peca (4 pecas terminam no minimo ou abaixo dele); o estoque inicial
# e calculado para fechar a conta: inicial = saldo final + total baixado
SALDO_FINAL = {1: 22, 2: 9, 3: 35, 4: 12, 5: 2, 6: 9, 7: 4, 8: 7, 9: 8, 10: 18, 11: 1, 12: 16, 13: 14, 14: 2, 15: 2}
for pid in estoque:
    estoque[pid] = SALDO_FINAL[pid] + sum(b[2] for b in baixas if b[1] == pid)
for codigo, pid, qtd, quando in sorted(baixas, key=lambda b: b[3]):
    antes = estoque[pid]
    estoque[pid] -= qtd
    if antes > minimo[pid] >= estoque[pid]:  # alerta na baixa que fez a peca atingir o minimo (RF13)
        notifs.append(dict(tipo="ESTOQUE_MINIMO", quando=quando + timedelta(minutes=1), os=None, peca=pid,
                           qtd=estoque[pid]))
assert estoque == SALDO_FINAL

tecnicos_ocupados = {o["tec"] for o in ordens if o["status"] in ("EM_EXECUCAO", "REJEITADA")}

# ------------------------------------------------------------------ notificacoes
for o in ordens:
    if o["sup"]:
        notifs.append(dict(tipo="NOVA_OS", quando=o["abertura"] + timedelta(minutes=2), os=o["codigo"], peca=None))
    if o["status"] == "CONCLUIDA":
        notifs.append(dict(tipo="APROVACAO", quando=o["aval"], os=o["codigo"], peca=None))
    if o["status"] == "REJEITADA":
        notifs.append(dict(tipo="REJEICAO", quando=o["aval"], os=o["codigo"], peca=None))
    if o["tipo"] == "P" and o["status"] in ("PENDENTE", "PENDENTE_ATRASADA", "EM_EXECUCAO", "REJEITADA"):
        prox = datetime.combine(o["prazo"], datetime.min.time()) - timedelta(hours=20)
        if prox <= HOJE:
            notifs.append(dict(tipo="PROXIMIDADE", quando=prox, os=o["codigo"], peca=None))
        atraso = datetime.combine(o["prazo"], datetime.min.time()) + timedelta(hours=26)
        if atraso <= HOJE:
            notifs.append(dict(tipo="ATRASO", quando=atraso, os=o["codigo"], peca=None))
notifs = [n for n in notifs if n["quando"] <= HOJE]
notifs.sort(key=lambda n: n["quando"])

ord_by = {o["codigo"]: o for o in ordens}
eq_nome = {e[0]: (e[1], e[2]) for e in EQUIPAMENTOS}
peca_by = {p[0]: p for p in PECAS}
admins = [7, 8]
supervisores = [2, 3, 4]
notif_rows, dest_rows = [], []
for nid, n in enumerate(notifs, 1):
    if n["tipo"] == "ESTOQUE_MINIMO":
        p = peca_by[n["peca"]]
        msg = (f"Estoque minimo atingido: {p[2]} ({p[1]}) - quantidade atual {n['qtd']} {p[3]}, "
               f"estoque minimo {p[5]} {p[3]}")
        dest = [(u, "EMAIL") for u in admins] + [(u, "NAVEGADOR") for u in supervisores]
    else:
        o = ord_by[n["os"]]
        cod, nome = eq_nome[o["eq"]]
        tipo_os = "corretiva" if o["tipo"] == "C" else "preventiva"
        sup_eq = SUP_DA_EQUIPE[TECNICOS[o["tec"]][1]]
        msg = {
            "NOVA_OS": f"Nova OS {tipo_os} #{o['codigo']} atribuida: {nome} ({cod}), prioridade {o['prioridade']}",
            "APROVACAO": f"OS #{o['codigo']} ({nome}) aprovada pelo supervisor",
            "REJEICAO": f"OS #{o['codigo']} ({nome}) rejeitada: {o.get('just', '')}",
            "PROXIMIDADE": f"Preventiva OS #{o['codigo']} ({nome}) vence em menos de 24 horas ({o['prazo']:%d/%m/%Y})",
            "ATRASO": f"Preventiva OS #{o['codigo']} ({nome}) atrasada ha mais de 24 horas (prazo {o['prazo']:%d/%m/%Y})",
        }[n["tipo"]]
        if n["tipo"] in ("PROXIMIDADE", "ATRASO"):
            dest = [(o["tec"], "EMAIL"), (o["tec"], "NAVEGADOR"), (sup_eq, "NAVEGADOR")]
        else:
            dest = [(o["tec"], "NAVEGADOR")]
    notif_rows.append((nid, n["tipo"], msg, n["quando"], n["os"], n["peca"]))
    vistos = set()
    for u, canal in dest:
        if u in vistos:
            continue  # PK (id_notificacao, id_usuario): um canal por destinatario
        vistos.add(u)
        envio = n["quando"] + timedelta(seconds=random.randint(5, 50))
        leitura = None
        if HOJE - n["quando"] > timedelta(days=2) or random.random() < 0.5:
            leitura = envio + timedelta(minutes=random.randint(3, 600))
            if leitura > HOJE:
                leitura = None
        dest_rows.append((nid, u, canal, envio, leitura))

# ------------------------------------------------------------------ escreve o SQL
OUT += [
    "-- =====================================================================",
    "-- Gerir Manutencao (SGM) - Projeto Fisico (PostgreSQL)",
    "-- Script 02: insercao de dados (carga de exemplo)",
    "-- ARQUIVO GERADO por ferramentas/gen_carga.py (dados ficticios, data de referencia 19/10/2026)",
    "-- Executar depois do 01_criacao.sql",
    "-- =====================================================================",
    "",
    "SET search_path TO sgm;",
    "",
    "-- ---------------------------------------------------------- Pessoas",
    "",
]
ins("usuario", ["id_usuario", "nome", "login", "senha_hash", "email", "telefone", "status_2fa", "ativo",
                "data_cadastro", "tipo_usuario"],
    [(u[0], u[1], u[2], HASH, f"{u[2]}@gerirmanutencao.com.br", u[3], u[4], True, u[6], u[5]) for u in USUARIOS],
    "usuario (superclasse) - 1 administrador do sistema, 3 supervisores, 2 gestores, 2 administrativos, 12 tecnicos")
ins("supervisor", ["id_usuario", "registro_profissional"],
    [(2, "CREA-GO 1020304050"), (3, "CREA-GO 1020304777"), (4, None)])
ins("equipe", ["id_equipe", "nome", "turno", "id_supervisor"], EQUIPES)
ins("tecnico", ["id_usuario", "status_operacional", "especialidade", "id_equipe"],
    [(t, "OCUPADO" if t in tecnicos_ocupados else "DISPONIVEL", esp, e) for t, (esp, e) in TECNICOS.items()])
ins("gestor", ["id_usuario", "cargo"], [(5, "Gerente Industrial"), (6, "Diretora de Operacoes")])
ins("administrativo", ["id_usuario", "setor"], [(7, "Almoxarifado"), (8, "Planejamento e Controle da Manutencao")])
ins("administrador_sistema", ["id_usuario"], [(1,)])

OUT += ["-- ---------------------------------------------------------- Ativos", ""]
ins("linha_producao", ["id_linha", "nome", "setor"], LINHAS)
ins("equipamento", ["id_equipamento", "codigo", "nome", "fabricante", "modelo", "numero_serie", "localizacao",
                    "criticidade", "horimetro_atual", "data_aquisicao", "ativo", "id_linha"],
    [(e[0], e[1], e[2], e[3], e[4], e[5], e[6], e[7], round(float(horim[e[0]]), 1), e[8], e[9], e[10])
     for e in EQUIPAMENTOS])
ins("item_checklist", ["id_equipamento", "num_item", "descricao", "obrigatorio"], CHECKLIST,
    "item_checklist (entidade fraca: checklist proprio de cada equipamento)")

# proxima_data = prazo da proxima preventiva ainda nao concluida
prox = {}
for o in ordens:
    if o["tipo"] == "P" and o["status"] != "CONCLUIDA":
        prox.setdefault(o["plano"], o["prazo"])
for pid, pdesc, per, eq, ativo in PLANOS:
    if pid not in prox:
        ult = max((o["prazo"] for o in ordens if o.get("plano") == pid), default=date(2026, 4, 1))
        prox[pid] = ult + timedelta(days=PER_DIAS[per])
ins("plano_preventivo", ["id_plano", "descricao", "periodicidade", "proxima_data", "ativo", "id_equipamento"],
    [(p[0], p[1], p[2], prox[p[0]], p[4], p[3]) for p in PLANOS])

OUT += ["-- ---------------------------------------------------------- Estoque", ""]
ins("peca", ["id_peca", "codigo", "descricao", "unidade_medida", "fornecedor", "estoque_minimo", "quantidade_atual", "ativo"],
    [(p[0], p[1], p[2], p[3], p[4], p[5], estoque[p[0]], True) for p in PECAS],
    "peca (quantidade_atual = saldo apos as baixas registradas abaixo)")

OUT += ["-- ---------------------------------------------------------- Manutencao", ""]
os_rows, corr_rows, prev_rows = [], [], []
for o in ordens:
    st = o["status"]
    status = {"REJEITADA": "EM_EXECUCAO", "PENDENTE_ATRASADA": "PENDENTE"}.get(st, st)
    decisao = {"CONCLUIDA": "APROVADA", "REJEITADA": "REJEITADA"}.get(st)
    os_rows.append((o["codigo"], o["tipo"], o["desc"], o["abertura"], o["prioridade"], o["prazo"], status,
                    o["inicio"], o["fim"], o["horim"], decisao, o["aval"] if decisao else None, o.get("just"),
                    o["eq"], o["tec"], o["sup"], o["avaliador"] if decisao else None))
    if o["tipo"] == "C":
        corr_rows.append((o["codigo"], o["causa"] if o["inicio"] else None, o["impacto"], o["falha"]))
    else:
        obs = None
        if o["fim"] and random.random() < 0.3:
            obs = random.choice(["Equipamento em boas condicoes gerais.", "Recomendada troca de correia na proxima preventiva.",
                                 "Ruido leve observado, sem impacto na operacao.", "Limpeza geral realizada."])
        prev_rows.append((o["codigo"], obs, o["plano"]))
ins("ordem_servico", ["codigo_os", "tipo_os", "descricao", "data_abertura", "prioridade", "prazo", "status",
                      "data_inicio_execucao", "data_fim_execucao", "leitura_horimetro", "decisao_avaliacao",
                      "data_avaliacao", "justificativa", "id_equipamento", "id_tecnico", "id_supervisor",
                      "id_supervisor_avaliador"], os_rows, "ordem_servico (superclasse)")
ins("manutencao_corretiva", ["codigo_os", "causa_falha", "impacto_producao", "data_hora_falha"], corr_rows)
ins("manutencao_preventiva", ["codigo_os", "observacao_geral", "id_plano"], prev_rows)
ins("resultado_checklist", ["codigo_os", "id_equipamento", "num_item", "resultado", "observacao"], resultados,
    "resultado_checklist (itens verificados em cada preventiva)")
ins("baixa_peca", ["codigo_os", "id_peca", "quantidade", "data_baixa"], baixas)

OUT += ["-- ---------------------------------------------------------- Notificacao", ""]
ins("notificacao", ["id_notificacao", "tipo", "mensagem", "data_geracao", "codigo_os", "id_peca"], notif_rows)
ins("notificacao_usuario", ["id_notificacao", "id_usuario", "canal", "data_envio", "data_leitura"], dest_rows)

OUT += [
    "-- ---------------------------------------------------------- Sequencias",
    "-- as chaves foram informadas explicitamente; ajusta os SERIAL para os proximos INSERTs",
]
for t, c in [("usuario", "id_usuario"), ("equipe", "id_equipe"), ("linha_producao", "id_linha"),
             ("equipamento", "id_equipamento"), ("plano_preventivo", "id_plano"), ("ordem_servico", "codigo_os"),
             ("peca", "id_peca"), ("notificacao", "id_notificacao")]:
    OUT.append(f"SELECT setval(pg_get_serial_sequence('{t}', '{c}'), (SELECT MAX({c}) FROM {t}));")
OUT.append("")

open("sql/02_insercao.sql", "w", encoding="utf-8").write("\n".join(OUT))
print("carga ok:", len(ordens), "OS,", len(baixas), "baixas,", len(resultados), "itens de checklist,",
      len(notif_rows), "notificacoes")
