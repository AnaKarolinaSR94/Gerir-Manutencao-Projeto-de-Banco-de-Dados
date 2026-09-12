# -*- coding: utf-8 -*-
"""Gera diagramas/02_der_relacional.puml a partir de schema.py."""
import sys
sys.path.insert(0, "ferramentas")
from schema import TABLES, is_pk, fk_target, fks

MODULOS = {"Pessoas": "#F3F8FF", "Ativos": "#F4FFF3", "Manutencao": "#FFF8EE", "Estoque": "#FFF2F2", "Notificacao": "#F8F2FF"}

out = ["@startuml", "title DER Relacional (Modelo Logico) - Gerir Manutencao (SGM)",
       "skinparam linetype ortho", "skinparam defaultFontName Arial", "skinparam defaultFontSize 11",
       "skinparam roundcorner 4", "skinparam nodesep 40", "skinparam ranksep 60",
       "hide circle", "hide empty methods", ""]
for mod, color in MODULOS.items():
    out.append(f'package "{mod}" {color} {{')
    for t in TABLES:
        if t["modulo"] != mod:
            continue
        out.append(f'  entity "{t["name"]}" as {t["name"]} {{')
        pks = [c for c in t["cols"] if is_pk(c)]
        others = [c for c in t["cols"] if not is_pk(c)]
        for c in pks:
            tag = "<<PK,FK>>" if fk_target(c) else "<<PK>>"
            out.append(f'    * {c[0]} : {c[1]} {tag}')
        out.append("    --")
        for c in others:
            star = "" if c[2] else "* "
            tag = " <<FK>>" if fk_target(c) else ""
            out.append(f'    {star}{c[0]} : {c[1]}{tag}')
        out.append("  }")
    out.append("}")
    out.append("")
for t in TABLES:
    for local, ref_t, ref_c in fks(t):
        nullable = any(c[0] in local and c[2] for c in t["cols"])
        left = "||" if not nullable else "|o"
        out.append(f'{ref_t} {left}--o{{ {t["name"]}')
out.append("@enduml")
open("diagramas/02_der_relacional.puml", "w", encoding="utf-8").write("\n".join(out))
print("puml ok")
