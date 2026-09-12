# -*- coding: utf-8 -*-
"""Layout do DER conceitual completo (Gerir Manutencao - SGM), revisao de 11/09/2026."""
import sys
sys.path.insert(0, "ferramentas")
from chen import Chen

K, M, D, P = "key", "multi", "derived", "pkey"
c = Chen(2750, 1420, "DER Conceitual (MER Estendido) - Gerir Manutencao (SGM)")

# ---------- PESSOAS ----------
c.entity("USUARIO", 520, 230, [("id_usuario", K), ("nome",), ("login",), ("senha_hash",), ("email",),
                               ("telefone",), ("status_2fa",), ("ativo",), ("data_cadastro",)], spread=700)
c.spec("USUARIO", 520, 340, ["ADMINISTRATIVO", "GESTOR", "SUPERVISOR", "TECNICO", "ADMINISTRADOR_SISTEMA"], "d", total=True)
c.entity("ADMINISTRATIVO", 170, 450, [("setor",)], side="bottom")
c.entity("GESTOR", 300, 450, [("cargo",)], side="bottom")
c.entity("SUPERVISOR", 620, 450)
c.attrs.append(dict(owner="SUPERVISOR", name="registro_profissional", kind="", x=760, y=505, w=7.6 * 21 + 26))
c.entity("TECNICO", 880, 450, [("status_operacional",), ("especialidade",)], side="top", spread=220)
c.entity("ADMINISTRADOR_SISTEMA", 1130, 450)
c.entity("EQUIPE", 620, 760, [("id_equipe", K), ("nome",), ("turno",)], side="left", rows=1, spread=110)
c.rel("lidera", 620, 600)
c.rel("pertence", 880, 620)
c.edge("SUPERVISOR", "lidera", "1")
c.edge("EQUIPE", "lidera", "N")
c.edge("TECNICO", "pertence", "N", total=True)
c.edge("EQUIPE", "pertence", "1")

# ---------- ORDEM DE SERVICO ----------
c.entity("ORDEM_SERVICO", 1500, 660, [("codigo_os", K), ("descricao",), ("data_abertura",), ("prioridade",),
                                      ("prazo",), ("status",), ("data_inicio_execucao",), ("data_fim_execucao",),
                                      ("duracao_execucao", D), ("leitura_horimetro",)], spread=520, dist=85, off=50, rows=4)
c.rel("executa", 1110, 580)
c.rel("distribui", 1150, 730)
c.edge("TECNICO", "executa", "1")
c.edge("ORDEM_SERVICO", "executa", "N", total=True)
c.edge("SUPERVISOR", "distribui", "1", via=[(700, 560), (1000, 560)])
c.edge("ORDEM_SERVICO", "distribui", "N")
c.rel("avalia", 900, 980, [("decisao",), ("data_avaliacao",), ("justificativa",)], side="bottom", spread=320, rows=2)
c.edge("SUPERVISOR", "avalia", "1", via=[(470, 520), (470, 900)])
c.edge("ORDEM_SERVICO", "avalia", "N")
c.spec("ORDEM_SERVICO", 1680, 790, ["MANUTENCAO_CORRETIVA", "MANUTENCAO_PREVENTIVA"], "d", total=True)
c.entity("MANUTENCAO_CORRETIVA", 1640, 900, [("causa_falha",), ("impacto_producao",), ("data_hora_falha",)],
         side="bottom", spread=200)
c.entity("MANUTENCAO_PREVENTIVA", 2000, 900, [("observacao_geral",)], side="bottom", off=120)

# ---------- ATIVOS ----------
c.entity("EQUIPAMENTO", 2000, 300, [("id_equipamento", K), ("codigo",), ("nome",), ("fabricante",), ("modelo",),
                                    ("numero_serie",), ("localizacao",), ("criticidade",), ("horimetro_atual",),
                                    ("data_aquisicao",), ("ativo",)], spread=760)
c.rel("sofre", 1800, 660)
c.edge("EQUIPAMENTO", "sofre", "1")
c.edge("ORDEM_SERVICO", "sofre", "N", total=True)
c.rel("fica_na_linha", 1620, 320)
c.entity("LINHA_PRODUCAO", 1330, 320, [("id_linha", K), ("nome",), ("setor",)], side="left", rows=1, spread=110)
c.edge("EQUIPAMENTO", "fica_na_linha", "N", total=True)
c.edge("LINHA_PRODUCAO", "fica_na_linha", "1")
c.rel("possui_item", 2300, 430, identifying=True)
c.entity("ITEM_CHECKLIST", 2500, 560, [("num_item", P), ("descricao",), ("obrigatorio",)], side="right", rows=1,
         spread=110, weak=True)
c.edge("EQUIPAMENTO", "possui_item", "1")
c.edge("ITEM_CHECKLIST", "possui_item", "N", total=True)
c.rel("tem_plano", 2000, 470)
c.entity("PLANO_PREVENTIVO", 2000, 660, [("id_plano", K), ("descricao",), ("periodicidade",), ("proxima_data",),
                                         ("ativo",)], side="right", rows=2, spread=180)
c.edge("EQUIPAMENTO", "tem_plano", "1")
c.edge("PLANO_PREVENTIVO", "tem_plano", "N", total=True)
c.rel("gera", 1990, 790)
c.edge("PLANO_PREVENTIVO", "gera", "1")
c.edge("MANUTENCAO_PREVENTIVA", "gera", "N")
c.rel("verifica", 2320, 900, [("resultado",), ("observacao",)], side="bottom", rows=1)
c.edge("MANUTENCAO_PREVENTIVA", "verifica", "N")
c.edge("ITEM_CHECKLIST", "verifica", "M")

# ---------- ESTOQUE ----------
c.rel("consome", 1860, 1020, [("quantidade",), ("data_baixa",)], side="right", rows=1, spread=60)
c.edge("ORDEM_SERVICO", "consome", "N", via=[(1760, 700)])
c.entity("PECA", 1800, 1200, [("id_peca", K), ("codigo",), ("descricao",), ("unidade_medida",), ("fornecedor",),
                              ("estoque_minimo",), ("quantidade_atual",), ("ativo",)], side="bottom", spread=620, off=60)
c.edge("PECA", "consome", "M")

# ---------- NOTIFICACAO ----------
c.entity("NOTIFICACAO", 1300, 1240, [("id_notificacao", K), ("tipo",), ("mensagem",), ("data_geracao",)],
         side="bottom", spread=330)
c.rel("refere_os", 1440, 1100)
c.rel("refere_peca", 1550, 1200)
c.edge("NOTIFICACAO", "refere_os", "N")
c.edge("ORDEM_SERVICO", "refere_os", "1", via=[(1440, 760)])
c.edge("NOTIFICACAO", "refere_peca", "N")
c.edge("PECA", "refere_peca", "1")
c.rel("recebe", 900, 1240, [("canal",), ("data_envio",), ("data_leitura",)], side="top", spread=280)
c.edge("NOTIFICACAO", "recebe", "N", total=True)
c.edge("USUARIO", "recebe", "M", via=[(40, 230), (40, 1240)])

c.note(30, 1395, "Notacao Chen (Elmasri & Navathe): linha dupla = participacao total; retangulo duplo = entidade fraca; "
                 "losango duplo = relacionamento identificador; sublinhado = chave; sublinhado tracejado = chave parcial; "
                 "elipse tracejada = atributo derivado; (d) = especializacao disjunta; 1, N, M = cardinalidades.", 13)
import os
os.makedirs("ferramentas/_build", exist_ok=True)
c.save("ferramentas/_build/01_der_conceitual.svg", "diagramas/01_der_conceitual.png", scale=1.6)  # SVG e PDF intermediarios ficam em .scratch
print("ok")
