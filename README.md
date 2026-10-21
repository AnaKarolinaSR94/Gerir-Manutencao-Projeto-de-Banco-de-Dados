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
entregas/     Projeto_BD_GM_Gerir_Manutencao.docx / .pdf — Entregas 1 (conceitual), 2 (lógico relacional) e 3 (físico)
diagramas/    01_der_conceitual.png (notação Chen/Elmasri), 02_der_relacional.png (+ fonte .puml), prototipos/ (telas)
sql/          Entrega 3 — projeto físico em PostgreSQL: criação, inserção, consultas e manipulação (+ resultados/)
ferramentas/  scripts que geram os diagramas, o documento e os scripts SQL (ver abaixo)
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
python ferramentas/gen_ddl.py            # DDL -> sql/01_criacao.sql
python ferramentas/gen_carga.py          # carga de exemplo -> sql/02_insercao.sql
python ferramentas/parte3_docx.py entregas/Projeto_BD_GM_Gerir_Manutencao.docx   # acrescenta só a Parte 3 a um .docx existente
```
- A Parte 3 do documento (`parte3_docx.py`, também chamada pelo `build_docx.py`) executa os scripts de `sql/` em um PostgreSQL
  local para colocar os resultados reais no documento; o banco `gerir_manutencao` (ou `PGDATABASE`) tem o schema `sgm` recriado.
- `ferramentas/schema.py` é a **fonte única do esquema relacional**: altere ali e regenere o DER relacional, a notação formal, o dicionário de dados e o DDL.
- `ferramentas/der_conceitual.py` define as posições do DER conceitual (renderizado por `chen.py`); para mudar o desenho, edite as coordenadas.
- Intermediários (SVG/PDF/recortes) vão para `ferramentas/_build/`, que é ignorada pelo git.

## Entrega 3 — projeto físico (PostgreSQL)
Segue a estrutura do modelo `07_Projeto_de_Banco` da disciplina: scripts de criação, scripts de inserção e consultas.

| Arquivo | Conteúdo |
|---|---|
| `sql/01_criacao.sql` | Schema `sgm` com as 19 tabelas, PK/FK, UNIQUE, CHECK, DEFAULT e índices (**gerado** por `gen_ddl.py`) |
| `sql/02_insercao.sql` | Carga de exemplo coerente: 20 usuários, 3 equipes, 15 equipamentos, 16 planos, 15 peças, 114 OS, baixas, checklists e notificações (**gerado** por `gen_carga.py`) |
| `sql/03_consultas.sql` | Parte 1: exemplos (WHERE, JOIN, GROUP BY, LEFT JOIN) · Parte 2: exercícios (IN/EXISTS/JOIN, divisão relacional, HAVING, UNION, anti-junção) · Parte 3: consultas dos requisitos (RF03, RF05–RF09, RF12–RF16) |
| `sql/04_manipulacao.sql` | INSERT/UPDATE/DELETE no fluxo real do sistema: cadastros, ciclo da OS corretiva (distribuir → executar → baixa de peça + alerta de estoque mínimo → rejeitar → aprovar), preventiva com checklist e reagendamento do plano, e testes das restrições |
| `sql/resultados/` | Saída de 03 e 04 (cada comando seguido do seu resultado) |
| `sql/00_executar_tudo.sql` | Roda os quatro scripts em ordem no `psql` |

Como executar (PostgreSQL 13+):
```
createdb gerir_manutencao
psql -d gerir_manutencao -f sql/00_executar_tudo.sql     # a partir da raiz do repositório
```
No pgAdmin/DBeaver: crie o banco `gerir_manutencao` e execute `01`, `02`, `03` e `04` nessa ordem.

Decisões do projeto físico:
- **ON DELETE**: FK que faz parte da PK (herança, entidade fraca, N:N) → `CASCADE`; FK opcional → `SET NULL`; demais → `RESTRICT`.
  Exceções para preservar o histórico: `baixa_peca → peca` e `resultado_checklist → item_checklist` são `RESTRICT`.
- **CHECKs além do modelo lógico**: fim da execução ≥ início; OS `CONCLUIDA` ⇔ decisão `APROVADA`; decisão exige data e supervisor
  avaliador; leitura da notificação ≥ envio.
- **Índices** nas colunas usadas pelo histórico (RF08), pelo dashboard e pelos relatórios (OS por equipamento/técnico/status,
  vencimento do plano, baixas por peça, notificações por tipo/data).
- A carga usa **19/10/2026 08:00** como "hoje"; as consultas que dependem da data usam esse valor fixo (comentado onde trocar por
  `now()`/`CURRENT_DATE`), para os resultados serem reproduzíveis.
- `04_manipulacao.sql` termina com `ROLLBACK`, então pode ser rodado várias vezes sem alterar a base; troque por `COMMIT` para gravar.

## Próximos passos
- Opcional: triggers para baixa de estoque (RF10), alerta de estoque mínimo (RF13) e status do técnico (RF14), hoje feitos
  pelas instruções de `04_manipulacao.sql`.
