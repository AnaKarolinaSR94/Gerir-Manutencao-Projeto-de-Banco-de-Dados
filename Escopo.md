# GERIR MANUTENÇÃO
## Escopo do Projeto

### 1.  Identificação e Contextualização do Projeto
#### 1.1 Descrição do Projeto
O projeto Gerir Manutenção consiste no desenvolvimento e implantação de um sistema web de gestão de manutenção industrial, concebido para atender às necessidades operacionais de uma indústria que enfrenta dificuldades sistemáticas no controle, registro e planejamento das manutenções de seus equipamentos de produção.

#### 1.2 Problema Central
A operação industrial apresenta as seguintes deficiências identificadas no levantamento inicial:
1. Ausência de controle sistematizado das manutenções realizadas, com registros feitos em papel ou planilhas não integradas;
2. Dificuldade em acompanhar o histórico de manutenção por equipamento, impedindo a análise de padrões de falha;
3. Inexistência de planejamento eficiente para manutenções preventivas, resultando em intervenções reativas e custosas;
4. Ocorrência frequente de falhas inesperadas nos equipamentos de produção, com impacto direto na disponibilidade e produtividade;
5. Baixa confiabilidade dos dados registrados manualmente, comprometendo a tomada de decisão gerencial;
6. Perda de tempo na busca de informações sobre histórico de equipamentos e localização de peças de reposição.

#### 1.3 Objetivo Principal
Desenvolver e implantar o Sistema web Gerir Manutenção capaz de atender 100% das funcionalidades essenciais definidas neste escopo, sendo adotado por ao menos 80% da equipe técnica nos primeiros noventa dias de operação. A meta de negócio é reduzir em 20% as falhas corretivas não planejadas nos primeiros três meses de uso, tendo como linha de base a média atual de horas de perda por equipamento parado.

#### 1.4 Justificativa 
A ausência de um sistema integrado de gestão de manutenção gera custos elevados com paradas não programadas, dificulta a rastreabilidade das intervenções realizadas e compromete a eficiência operacional da indústria. A implantação do Gerir Manutenção proporcionará controle centralizado, histórico auditável, planejamento baseado em dados e indicadores gerenciais confiáveis, viabilizando decisões mais assertivas e a extensão da vida útil dos equipamentos.

### 2. Escopo do Projeto
#### 2.1 Dentro do Escopo
O sistema Gerir Manutenção contempla o desenvolvimento das seguintes capacidades:
##### 2.1.1 Gestão de Equipamentos
- Cadastro de máquinas industriais com nome, modelo, número de série (único), localização na fábrica e nível de criticidade (Alta, Média ou Baixa);
##### 2.1.2 Gestão de Manutenções
- Registro de manutenção corretiva com seleção de máquina por código ou nome parcial, descrição da falha (até 500 caracteres), peças trocadas e data/hora automática;
- Registro de manutenção preventiva com checklist de itens específico por máquina, marcação de itens como verificado ou não aplicável, observações complementares e data/hora automática;
- Agendamento automatizado de manutenções preventivas com periodicidade Diária, Semanal, Mensal, Trimestral, Semestral ou Anual, calculada com base na última leitura de horímetro informada manualmente pelo técnico;

##### 2.1.3 Gestão de Ordens de Serviço
- Distribuição de ordens de serviço pelo supervisor a técnicos específicos, com definição de máquina, tipo (corretiva ou preventiva), descrição, prioridade (Alta, Média ou Baixa) e prazo de entrega;
- Aprovação ou rejeição de ordens de serviço pelos supervisores, com exigência de justificativa obrigatória em caso de rejeição;
- Consulta ao histórico completo de intervenções por equipamento, ordenado da mais recente para a mais antiga, com filtros por tipo e período;
- Visualização de tarefas preventivas da semana por técnico, ordenadas por data de vencimento, com destaques visuais para proximidade de prazo (menos de 24 horas) e atraso (mais de 24 horas).

##### 2.1.4 Gestão de Estoque de Peças
- Cadastro de peças de reposição com código único, descrição, fornecedor, estoque mínimo e quantidade atual;
- Baixa automática de peças no estoque interno no momento do registro de manutenção;
- Alerta automático ao perfil Administrativo e ao Supervisor quando a quantidade de uma peça atingir ou ficar abaixo do estoque mínimo, com supressão de alertas duplicados por 24 horas.

##### 2.1.5 Monitoramento e Indicadores
- Dashboard de indicadores de desempenho com MTBF (Mean Time Between Failures) e MTTR (Mean Time To Repair) por máquina, com filtros por período (30, 90 ou 180 dias) e linha de produção, atualizado automaticamente a cada 60 segundos;
- Painel de status da equipe técnica (Ocupado ou Disponível) com atualização automática a cada 60 segundos e possibilidade de alteração manual pelo supervisor;
- Ranking das 10 máquinas com maior número de falhas no período selecionado, com exibição do total de falhas e do MTBF atual, e acesso ao histórico detalhado de intervenções;
- Monitoramento de produtividade da equipe com gráfico comparativo entre tarefas planejadas e concluídas, com percentual de conclusão calculado automaticamente e filtros por período, equipe ou técnico individual;
- Calendário mensal e semanal de manutenções agendadas, com distinção visual entre corretivas e preventivas.

##### 2.1.6 Alertas e Notificações
- Envio automático de alertas ao técnico responsável e ao supervisor quando uma manutenção preventiva estiver a menos de 24 horas do prazo (alerta de proximidade) ou estiver atrasada há mais de 24 horas (alerta de atraso);
- Notificações via e-mail e interface web do sistema.

##### 2.1.7 Relatórios e Exportações
- Geração e exportação de relatório executivo mensal em PDF, consolidando MTBF, MTTR, ranking de máquinas críticas e produtividade da equipe;
- Relatório de consumo de peças por período e por máquina, exportável em PDF e planilha (XLS/CSV);
- Exportação de relatório de horas trabalhadas por técnico e por ordem de serviço, com filtros por período, em formato XLS/CSV;

#### 2.2 Fora do Escopo
Para manter a viabilidade do projeto dentro do prazo e do orçamento estabelecidos, as funcionalidades a seguir estão explicitamente excluídas desta versão:
- Integração completa com sistemas ERP (Enterprise Resource Planning);
- Controle financeiro detalhado dos custos de manutenção por centro de custo;
- Compra automática de peças ou gestão completa de cadeia de suprimentos;
- Aplicação mobile nativa para dispositivos iOS ou Android;
- Inteligência artificial para previsão preditiva de falhas — funcionalidade a ser avaliada em versões futuras do sistema.

### 3. Requisitos e Perfis de Acesso
#### 3.1 Perfis de Usuário
O sistema atenderá quatro perfis de negócio, cada um com permissões específicas controladas por RBAC (Role-Based Access Control), além de um perfil técnico de Administrador do Sistema:
| Perfil | Persona | Principais permissões |
|--------|---------|-----------------------|
| Técnico de Manutenção | Ricardo Santos | Registrar manutenções, consultar histórico, visualizar tarefas, dar baixa em peças, receber alertas |
| Supervisor de Manutenção | Sandra Oliveira | Distribuir e aprovar OS, agendar preventivas, monitorar equipe, visualizar calendário, gerar relatório de peças |
| Gestor / Gerente | Roberto Meireles | Visualizar dashboard de KPIs, acessar ranking de máquinas críticas, monitorar produtividade, exportar relatório executivo |
| Equipe Administrativa | Carla Mendes | Cadastrar equipamentos e peças, importar listas, exportar horas trabalhadas, receber alertas de estoque mínimo |
| Administrador do Sistema | Equipe de TI | Superusuário com acesso total; gerencia contas de usuário e corrige dados em caso de problema (perfil técnico, não de negócio) |

#### 3.2 Requisitos Funcionais - Síntese
O sistema contempla 17 requisitos funcionais (RF01 a RF17) distribuídos entre os quatro perfis, abrangendo cadastro de equipamentos, registro e agendamento de manutenções, anexo de evidências, controle de estoque, geração de alertas automáticos, emissão de relatórios, distribuição e aprovação de ordens de serviço, monitoramento de equipe e indicadores gerenciais.

#### 3.3 Requisitos Não Funcionais - Síntese
O sistema deve satisfazer 12 requisitos não funcionais (RNF01 a RNF12), que estabelecem:
- Responsividade nativa para tablets e smartphones, sem rolagem horizontal (RNF01);
- Fluxo de abertura de registro de falha concluído em no máximo 5 cliques a partir da tela inicial (RNF02);
- Autenticação de todos os usuários com login e senha; autenticação em dois fatores (2FA) obrigatória para os perfis de Supervisor e Gestor (RNF03, RNF09);
- Carregamento de qualquer página em até 3 segundos em conexões com velocidade mínima de 10 Mbps (RNF04);
- Suporte à importação de listas de peças e equipamentos via CSV e Excel (RNF05);
- Disponibilidade mínima de 99,5% no horário de produção (06h às 22h), exceto janelas de manutenção programada comunicadas com 48 horas de antecedência (RNF06);
- Compatibilidade com as versões atuais dos navegadores Chrome, Firefox, Edge e Safari (RNF07);
- Conformidade com as diretrizes WCAG 2.1 nível AA para contraste, navegação por teclado e leitores de tela (RNF08);
- Conformidade com a Lei Geral de Proteção de Dados — LGPD —, garantindo ao titular o direito de acesso, retificação e exclusão de dados pessoais (RNF10);
- Controle de acesso estritamente por perfil (RBAC), impedindo que um usuário acesse funcionalidades além das autorizadas ao seu papel (RNF11);
- Comunicação HTTPS com TLS 1.2 ou superior em todas as requisições;
- Dados sensíveis armazenados criptografados no banco de dados (RNF12).

### 4. Premissas e Restrições
#### 4.1 Premissas
- A infraestrutura de TI necessária para hospedagem e operação do sistema estará disponível no prazo adequado;
- A equipe de desenvolvimento estará integralmente alocada ao projeto durante todo o ciclo;
- Os usuários finais dos quatro perfis estarão disponíveis para participar do levantamento de requisitos, validações intermediárias e homologação;
- O escopo funcional permanecerá estável após a aprovação formal dos requisitos.

#### 4.2 Restrições
- Equipe de desenvolvimento limitada, sem possibilidade de ampliação sem aprovação do sponsor;
- Dependência da agenda dos usuários-chave para as etapas de validação e homologação.

### 5. Riscos Identificados
| Risco | Probabilidade | Impacto | Resposta planejada |
|-------------------|---------------|------|-----------|
| Atraso no cronograma | Média | Alta | Acompanhamento semanal do progresso com relatório de status ao gerente |
| Mudanças frequentes de escopo | Alta | Alta | Implementar controle formal de mudanças (change management) com aprovação do sponsor |
| Baixa adesão dos usuários | Média | Alta | Envolver usuários desde o levantamento de requisitos e capacitar todos os perfis antes do go-live |
| Indisponibilidade de membros da equipe | Média | Média | Documentar rigorosamente o projeto e o código para facilitar a substituição |
| Falha ou perda de dados na migração | Baixa | Alta | Realizar backup integral pré-migração e validar dados em ambiente de homologação antes do go-live |

### 6. Partes Interessadas
| Nome | Cargo | Interesse/Influência |
|-------------------|---------------|------|
| Maria de Oliveira | Patrocinadora (Sponsor) | Interesse e influência muito alto. Responsável pela aprovação macro e liberação da reserva de contingência de R$ 60.000,00. Assina o documento de escopo e o TAP |
| Roberto Lima | Gerente de Projetos | Interesse muito alto na empresa e influência alta. É o líder nomeado no TAP. Responsável por controlar o teto de R$ 480.000,00 e acionar a reserva de contingência somente com aprovação da Sponsor |
| João Silva | Gerente e Decisor de Negócios | Interesse e influência muito alto. Principal validador das regras de negócio do sistema. Deve participar ativamente da homologação prevista para 30/10/2026 |
| Técnicos de Manutenção | Usuários Finais-Execução | Interesse muito alto e baixa influência. Usuários mais frequentes do sistema. A meta de 80% de adoção nos primeiros 90 dias depende diretamente deste grupo. O treinamento específico para este perfil é crítico. |
| Supervisores de Manutenção | Usuários Finais-Supervisão | Interesse muito alto e média influência. Papel-chave no fluxo de aprovação de OS (UC12) — sem aprovação, nenhuma manutenção é consolidada no histórico. |
| Equipe Administrativa | Usuários Finais-Cadastros e Relatórios | Interesse alto e baixa influência. A qualidade dos dados cadastrais é pré-condição para o funcionamento correto de todos os 21 casos de uso. |
| Equipe de Desenvolvimento | Analistas e Desenvolvedores | Interesse muito alto e baixa influência. Time técnico responsável pelas fases de Construção e Testes da EAP. |
| Equipe de TI e Suporte | Sustentação e Infraestrutura | Médio interesse e influência. Responsável pela infraestrutura local e governança de dados. Deve ser envolvida a partir da fase de Testes para preparar o ambiente de produção. |
| Fornecedores de Peças de Reposição | Partes Afetadas Indiretamente/Externa a organização | Alto interesse e muito baixa influência. Impactados indiretamente pelos alertas de estoque mínimo e relatórios de consumo de peças. Não participam do projeto mas podem ser afetados por decisões de compra baseadas nos dados do sistema. |
| Autoridade Nacional de Proteção de Dados (ANPD) | Órgão Regulador | Muito baixo interesse e muito alta influência. Não participa ativamente do projeto mas tem poder regulatório. A conformidade com RNF10 e RNF12 deve ser verificada antes do go-live de fev/2027. |

### 7. Critérios de Aceitação do Projeto
O projeto será considerado concluído com sucesso quando todos os critérios abaixo forem atendidos:
- 100% dos 17 requisitos funcionais (RF01 a RF17) implementados e validados em ambiente de homologação;
- Todos os 12 requisitos não funcionais (RNF01 a RNF12) verificados por testes específicos documentados;
- Taxa de adoção igual ou superior a 80% da equipe técnica nos primeiros 90 dias de operação;
- Redução de no mínimo 20% nas falhas corretivas não planejadas nos primeiros 3 meses de uso em relação à linha de base;
- Homologação formal aprovada pelos representantes dos quatro perfis de usuário;
- Sistema operando com disponibilidade de 99,5% no horário de produção (06h às 22h) por trinta dias consecutivos após o go-live;
- Documentação técnica do sistema entregue e aprovada pela equipe de TI;
- Treinamento concluído para 100% dos usuários dos quatro perfis de acesso.

### 8. Aprovação do Escopo
A assinatura deste documento representa a aprovação formal do escopo do projeto Gerir Manutenção por parte dos responsáveis indicados, autorizando o início das atividades de análise, design e desenvolvimento conforme definido.
| Nome | Cargo | Assinatura | Data |
|------|-------|------------|------|
| Maria de Oliveira | Diretora de Operações (Sponsor) | | __ /__ /____ |
| Roberto Lima | Gerente de Projetos | | __ /__ /____ |
| João Silva | Gerente de Manutenção | | __ /__ /____ |


