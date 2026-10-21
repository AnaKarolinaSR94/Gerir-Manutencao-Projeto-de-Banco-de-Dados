-- =====================================================================
-- Gerir Manutencao (SGM) - executa os quatro scripts em ordem (psql)
--
--   createdb gerir_manutencao
--   psql -d gerir_manutencao -f sql/00_executar_tudo.sql      (rodar da raiz do repositorio)
--
-- No pgAdmin/DBeaver: abra e execute 01, 02, 03 e 04 nessa ordem
-- (este arquivo usa \i, que e um comando exclusivo do psql).
-- =====================================================================
\set ON_ERROR_STOP on
\i sql/01_criacao.sql
\i sql/02_insercao.sql
\i sql/03_consultas.sql
\i sql/04_manipulacao.sql
