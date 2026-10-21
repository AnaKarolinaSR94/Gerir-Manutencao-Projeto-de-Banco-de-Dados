# -*- coding: utf-8 -*-
"""Gera sql/01_criacao.sql (projeto fisico em PostgreSQL) a partir de schema.py.

Regras de ON DELETE adotadas:
  - FK que faz parte da PK (heranca, entidade fraca, relacionamento N:N) -> CASCADE
  - FK opcional (coluna aceita nulo)                                    -> SET NULL
  - demais FKs obrigatorias                                             -> RESTRICT
  - excecoes em ON_DELETE_OVERRIDE (preservar historico de manutencao)
Rodar a partir da raiz do repositorio:  python ferramentas/gen_ddl.py
"""
import sys
sys.path.insert(0, "ferramentas")
from schema import TABLES, is_pk, fks

SCHEMA = "sgm"

# historico de baixas e de checklists nao deve sumir se alguem apagar uma peca ou um item
ON_DELETE_OVERRIDE = {
    ("baixa_peca", "id_peca"): "RESTRICT",
    ("resultado_checklist", "id_equipamento"): "RESTRICT",
}

# regras de integridade do projeto fisico que nao estao no esquema logico
EXTRA_CHECKS = {
    "ordem_servico": [
        "data_fim_execucao IS NULL OR data_inicio_execucao IS NULL OR data_fim_execucao >= data_inicio_execucao",
        # CONCLUIDA <=> APROVADA (coalesce evita que decisao nula passe pelo CHECK como "desconhecido")
        "(status = 'CONCLUIDA') = (coalesce(decisao_avaliacao, '') = 'APROVADA')",
        "decisao_avaliacao IS NULL OR (data_avaliacao IS NOT NULL AND id_supervisor_avaliador IS NOT NULL)",
    ],
    "notificacao_usuario": [
        "data_leitura IS NULL OR (data_envio IS NOT NULL AND data_leitura >= data_envio)",
    ],
}

# indices para as consultas mais frequentes (historico, dashboard, relatorios)
INDEXES = [
    ("idx_os_equipamento", "ordem_servico", "id_equipamento, data_abertura"),
    ("idx_os_tecnico", "ordem_servico", "id_tecnico"),
    ("idx_os_status", "ordem_servico", "status"),
    ("idx_plano_proxima_data", "plano_preventivo", "proxima_data"),
    ("idx_baixa_peca", "baixa_peca", "id_peca, data_baixa"),
    ("idx_notificacao_data", "notificacao", "tipo, data_geracao"),
    ("idx_tecnico_equipe", "tecnico", "id_equipe"),
]


def ordem_topologica(tables):
    by_name = {t["name"]: t for t in tables}
    deps = {t["name"]: {ref for _, ref, _ in fks(t) if ref != t["name"]} for t in tables}
    out, done = [], set()
    while len(out) < len(tables):
        progress = False
        for t in tables:  # mantem a ordem do schema.py sempre que possivel
            n = t["name"]
            if n not in done and deps[n] <= done:
                out.append(by_name[n]); done.add(n); progress = True
                break
        if not progress:
            raise SystemExit("ciclo de FKs: " + str({n: deps[n] - done for n in deps if n not in done}))
    return out


def on_delete(table, local_cols):
    key = (table["name"], local_cols[0])
    if key in ON_DELETE_OVERRIDE:
        return ON_DELETE_OVERRIDE[key]
    cols = {c[0]: c for c in table["cols"]}
    if all(is_pk(cols[c]) for c in local_cols):
        return "CASCADE"
    if any(cols[c][2] for c in local_cols):
        return "SET NULL"
    return "RESTRICT"


def create_table(t):
    lines, checks = [], []
    pks = [c[0] for c in t["cols"] if is_pk(c)]
    single_pk = len(pks) == 1
    for name, typ, nullable, _desc, flags in t["cols"]:
        parts = [f"    {name}", typ]
        if not nullable:
            parts.append("NOT NULL")
        if single_pk and "PK" in flags:
            parts.append("PRIMARY KEY")
        if "UK" in flags:
            parts.append("UNIQUE")
        for f in flags:
            if f.startswith("DEF:"):
                parts.append("DEFAULT " + f[4:])
            elif f.startswith("CK:"):
                checks.append(f[3:])
        lines.append(" ".join(parts))
    if not single_pk:
        lines.append(f"    PRIMARY KEY ({', '.join(pks)})")
    for local, ref_t, ref_c in fks(t):
        lines.append(f"    FOREIGN KEY ({', '.join(local)}) REFERENCES {ref_t}({', '.join(ref_c)})"
                     f" ON DELETE {on_delete(t, local)}")
    for ck in checks + EXTRA_CHECKS.get(t["name"], []):
        lines.append(f"    CHECK ({ck})")
    return f"-- {t['origem']}\nCREATE TABLE {t['name']} (\n" + ",\n".join(lines) + "\n);\n"


def main():
    out = [
        "-- =====================================================================",
        "-- Gerir Manutencao (SGM) - Projeto Fisico (PostgreSQL)",
        "-- Script 01: criacao do banco de dados",
        "-- ARQUIVO GERADO por ferramentas/gen_ddl.py a partir de ferramentas/schema.py",
        "-- (altere o schema.py e regenere; nao edite este arquivo a mao)",
        "-- =====================================================================",
        "",
        "-- Passo opcional (executar uma vez, conectado ao banco postgres):",
        "-- CREATE DATABASE gerir_manutencao;",
        "-- Depois conecte-se ao banco gerir_manutencao e execute o restante.",
        "",
        f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE;",
        f"CREATE SCHEMA {SCHEMA};",
        f"SET search_path TO {SCHEMA};",
        "",
    ]
    modulo = None
    for t in ordem_topologica(TABLES):
        if t["modulo"] != modulo:
            modulo = t["modulo"]
            out.append(f"-- ---------------------------------------------------------- {modulo}")
            out.append("")
        out.append(create_table(t))
    out.append("-- ---------------------------------------------------------- Indices")
    out.append("")
    for name, table, cols in INDEXES:
        out.append(f"CREATE INDEX {name} ON {table} ({cols});")
    out.append("")
    open("sql/01_criacao.sql", "w", encoding="utf-8").write("\n".join(out))
    print("ddl ok:", len(TABLES), "tabelas")


if __name__ == "__main__":
    main()
