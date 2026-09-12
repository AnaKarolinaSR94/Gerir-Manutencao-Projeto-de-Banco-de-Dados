# Gerir Manutenção (SGM) — Projeto de Banco de Dados

Projeto final da disciplina **Banco de Dados 1** (UFG/INF — Engenharia de Software).
Sistema web de gestão de manutenção industrial: equipamentos, ordens de serviço (corretivas e preventivas),
checklists, estoque de peças, alertas e indicadores (MTBF/MTTR).

**Grupo:** Ana Karolina da Silva Reges · Matheus Vaz Teixeira · Micael Henrique da Silva Fontes · Reginaldo Ribeiro

## Prazos
| Data | Entrega |
|---|---|
| 16/09/2026 | Validação dos modelos conceitual e lógico |
| 21/10/2026 e 18/11/2026 | Acompanhamentos |
| 02/12/2026 | Projeto final (conceitual, lógico e físico) |

## Estrutura do repositório
```
requisitos/   Descrição do Negócio, Escopo do Projeto e ERS (RF01–RF16, RNF01–RNF10) — revisão de 11/09/2026
entregas/     Projeto_BD_GM_Gerir_Manutencao.docx / .pdf — Entrega 1 (conceitual) + Entrega 2 (lógico relacional)
diagramas/    01_der_conceitual.png (notação Chen/Elmasri), 02_der_relacional.png (+ fonte .puml), prototipos/ (telas)
ferramentas/  scripts que geram os diagramas e o documento (ver abaixo)
GLOSSARIO.md  vocabulário do domínio usado em todos os artefatos
```

## Modelo em uma frase
USUARIO especializado em Técnico, Supervisor, Gestor, Administrativo e Administrador do Sistema; EQUIPAMENTO (com checklist
próprio e planos preventivos por periodicidade) sofre ORDENS DE SERVIÇO corretivas ou preventivas, executadas por um técnico,
distribuídas e avaliadas por um supervisor, que consomem PEÇAS do estoque e geram NOTIFICAÇÕES. Esquema relacional em 3FN com 19 relações.

## Como regenerar os artefatos
Pré-requisitos: Python 3, Java (para o PlantUML) e Graphviz (`dot`), além de `pip install python-docx pymupdf svglib reportlab`.
Rodar sempre a partir da raiz do repositório:
```
python ferramentas/der_conceitual.py     # DER conceitual -> diagramas/01_der_conceitual.png
python ferramentas/gen_relacional.py     # DER relacional -> diagramas/02_der_relacional.puml
java -jar plantuml.jar -tpng diagramas/02_der_relacional.puml                 # -> .png
java -jar plantuml.jar -tpng -o prototipos diagramas/prototipos.puml          # -> diagramas/prototipos/*.png
python ferramentas/build_docx.py         # -> entregas/Projeto_BD_GM_Gerir_Manutencao.docx (atualize o Sumário no Word)
```
- `ferramentas/schema.py` é a **fonte única do esquema relacional**: altere ali e regenere o DER relacional, a notação formal e o dicionário de dados.
- `ferramentas/der_conceitual.py` define as posições do DER conceitual (renderizado por `chen.py`); para mudar o desenho, edite as coordenadas.
- Intermediários (SVG/PDF/recortes) vão para `ferramentas/_build/`, que é ignorada pelo git.

## Próxima etapa
Entrega 3 — projeto físico em PostgreSQL: gerar o DDL a partir de `ferramentas/schema.py`, scripts de carga e de manipulação.
