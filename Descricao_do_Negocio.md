# Modelo de Negócio: Sistema Gerir Manutenção (SGM)

## 1. Identificação do Grupo e Participantes

**Instituição:** Universidade Federal de Goiás (UFG) — Instituto de Informática (INF)

**Curso / Disciplina:** Engenharia de Software — Banco de Dados

**Integrantes do Grupo:**

- Ana Karolina da Silva Reges
- Matheus Vaz Teixeira
- Micael Henrique da Silva Fontes
- Reginaldo Ribeiro

## 2. Identificação do Projeto

**Nome do Sistema:** Sistema Gerir Manutenção (SGM)

**Natureza da Aplicação:** Sistema Web de Gestão de Manutenção Industrial

## 3. Área de Negócio e Domínio de Aplicação

A área de negócio do projeto compreende a Gestão de Manutenção Industrial e Gestão de Ativos Físicos voltada para plantas de manufatura e indústrias com processos produtivos automatizados. O domínio envolve o gerenciamento do ciclo de vida operacional do maquinário industrial, contemplando rotinas de manutenção preventiva, intervenções corretivas, controle de inventário interno de peças de reposição e monitoramento de índices de desempenho operacional da fábrica.

## 4. Descrição Completa

### 4.1. Contexto e Problema Central do Domínio

No ambiente industrial contemporâneo, a disponibilidade contínua dos ativos físicos é determinante para a produtividade da planta. Contudo, diversas indústrias enfrentam severas perdas operacionais decorrentes da gestão manual e fragmentada da manutenção. Os principais problemas diagnosticados nesse cenário são:

- **Indisponibilidade não planejada:** Paradas repentinas de linhas de produção causadas pela ausência de um planejamento preventivo sistemático.
- **Burocracia e registros manuais:** Utilização de formulários em papel e planilhas dispersas para abertura e fechamento de serviços, gerando perda de tempo operacional e sobrecarga burocrática.
- **Perda e inconsistência de dados:** Informações rasuradas, ilegíveis ou não repassadas adequadamente nas trocas de turnos dos técnicos.
- **Descontrole no almoxarifado interno:** Falta de rastreabilidade do consumo de insumos, resultando no desabastecimento de peças críticas para reparos emergenciais.
- **Ausência de indicadores gerenciais:** Dificuldade dos gestores em mensurar a confiabilidade dos ativos (como tempos médios entre falhas e de reparo), impedindo decisões embasadas sobre reformas ou substituição de equipamentos.

### 4.2. Objetivos e Proposta de Valor

O Sistema Gerir Manutenção visa centralizar, digitalizar e padronizar toda a engenharia e operação de manutenção da fábrica em uma plataforma web integrada. Os objetivos estratégicos e impactos esperados compreendem:

- **Redução da indisponibilidade:** Mitigar quebras não programadas por meio da automação do agendamento de intervenções preventivas.
- **Digitalização de ponta a ponta:** Eliminar formulários físicos e garantir a coleta ágil de dados operacionais diretamente no chão de fábrica.
- **Rastreabilidade e histórico confiável:** Manter um histórico detalhado e imutável de todas as intervenções executadas em cada máquina.
- **Controle dinâmico de insumos:** Realizar a baixa automática de peças consumidas em serviços e emitir alertas preventivos de reposição de estoque mínimo.
- **Inteligência operacional e gerencial:** Fornecer painéis de indicadores em tempo real (Dashboards) e relatórios consolidados para direcionar investimentos industriais.

### 4.3. Ecossistema de Usuários

O sistema deve atender quatro perfis operacionais e estratégicos:

#### Técnico de Manutenção

- **Perfil:** Mecânico sênior que atua diretamente no chão de fábrica.
- **Atuação no Sistema:** Registra manutenções corretivas em campo via dispositivo móvel, preenche checklists de manutenções preventivas, anexa evidências de falhas e realiza a baixa das peças utilizadas.
- **Necessidade Central:** Agilidade no registro sem exigência de navegação burocrática, com histórico do ativo acessível na ponta dos dedos.

#### Supervisor de Manutenção

- **Perfil:** Engenheiro mecânico responsável pelo planejamento, distribuição de tarefas e cumprimento de cronogramas da equipe.
- **Atuação no Sistema:** Distribui ordens de serviço por prioridade, monitora a disponibilidade da equipe técnica, aprova/rejeita ordens executadas e agenda preventivas periódicas.
- **Necessidade Central:** Visibilidade sobre a operação em andamento, previsibilidade de paradas e garantia da qualidade dos dados técnicos.

#### Gestor / Gerente Industrial

- **Perfil:** Executivo focado em metas de volume fabril, redução de custos e disponibilidade global dos ativos.
- **Atuação no Sistema:** Acompanha dashboards com indicadores de confiabilidade (MTBF e MTTR), visualiza rankings de máquinas mais críticas e exporta relatórios executivos de produtividade.
- **Necessidade Central:** Dados consolidados e métricas precisas para embasar decisões estratégicas de aquisição e reforma de maquinário.

#### Equipe Administrativa

- **Perfil:** Assistente administrativa responsável pela interface entre documentação técnica, almoxarifado e cadastros-base.
- **Atuação no Sistema:** Realiza o cadastro de máquinas e insumos, executa importações em lote de dados via arquivos CSV/Excel e monitora alertas de estoque mínimo para encaminhar necessidades de reposição.
- **Necessidade Central:** Eliminação de redigitação manual e saneamento consistente da base de dados de ativos e peças.

### 4.4. Escopo Funcional da Solução

O sistema abrangerá os seguintes módulos funcionais:

- **Módulo de Gestão de Ativos:** Cadastro detalhado de máquinas industriais e classificação de criticidade.
- **Módulo de Ordens de Serviço (OS):** Registro digital de manutenções corretivas e preventivas.
- **Módulo de Agendamento Preventivo:** Planejamento automatizado de inspeções baseado em intervalos temporais fixos.
- **Módulo de Auditoria e Fluxo de Trabalho:** Mecanismo de distribuição de OS por prazo e criticidade, além de etapa de aprovação formal pelo supervisor antes da consolidação no histórico.
- **Módulo de Gestão de Estoque Interno:** Cadastro de peças de reposição, baixa automática do inventário na conclusão de reparos e disparo de alertas de estoque.
- **Módulo de Indicadores e Relatórios:** Dashboards analíticos atualizados com gráficos de MTBF (*Mean Time Between Failures*), MTTR (*Mean Time To Repair*).
- **Módulo de Gestão de Equipe:** Painel com o status operacional dos técnicos (Ocupado/Disponível).

### 4.5. Limites do Sistema (Fora de Escopo)

Para manter o escopo técnico enxuto, coeso e viável:

- **Módulo de Compras e Cotações:** O processo de compras, orçamentos com terceiros e seleção de fornecedores ocorrerá fora do sistema.
- **Gestão Financeira e Faturamento:** O sistema não realiza apuração de custos monetários das ordens, liquidação contábil ou emissão de notas fiscais (processos delegados aos sistemas ERP corporativos existentes).
- **Cálculo de Folha de Pagamento:** Não haverá processamento financeiro de horas trabalhadas de funcionários.
- **Telemetria IoT Direta:** Não contempla a integração direta com sensores físicos ou hardware embarcado nas máquinas para coleta telemétrica.

### 4.6. Requisitos de Qualidade e Não Funcionais Relevantes

O sistema contempla diretrizes arquiteturais e de qualidade:

- **Usabilidade e Responsividade:** Interface web responsiva acessível por navegadores móveis e desktops.
- **Desempenho e Disponibilidade:** Tempo de carregamento de páginas de até 3 segundos.
- **Conformidade Legal e Acessibilidade:** Tratamento de dados pessoais em estrita conformidade com a LGPD.
