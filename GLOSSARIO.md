# Glossário do domínio — Gerir Manutenção (SGM)

Vocabulário canônico usado em todos os artefatos do projeto de banco de dados.
Sem detalhes de implementação: só termos e o que significam.
Revisado em 11/09/2026 após alinhamento com os documentos de escopo do grupo .

## Pessoas e organização

- **Usuário**: qualquer pessoa autenticada no sistema. Todo usuário tem exatamente um perfil.
- **Técnico (de Manutenção)**: usuário que executa Ordens de Serviço no chão de fábrica. Tem um *status operacional* (Disponível ou Ocupado).
- **Supervisor (de Manutenção)**: usuário que distribui OS, avalia (aprova ou rejeita) OS executadas e lidera uma Equipe.
- **Gestor (Industrial)**: usuário que consome indicadores (MTBF, MTTR, ranking, produtividade). Não altera dados operacionais.
- **Administrativo**: usuário que mantém cadastros-base (equipamentos, checklists, peças).
- **Administrador do Sistema**: perfil técnico de TI, superusuário que gerencia contas e corrige dados. Não é um perfil de negócio.
- **Equipe**: grupo de técnicos liderado por um supervisor. Um técnico pertence a uma única equipe.

## Ativos

- **Equipamento**: máquina industrial sob manutenção, identificada por número de série único e por um código interno usado nas buscas. Também chamada de "máquina" ou "ativo"; o termo canônico é Equipamento. Fabricante e modelo são apenas informações descritivas do equipamento.
- **Linha de Produção**: agrupamento produtivo de equipamentos, usado como filtro no dashboard.
- **Criticidade**: classificação do equipamento (Alta, Média, Baixa) para priorização.
- **Horímetro**: contador de horas de operação do equipamento, informado manualmente pelo técnico a cada manutenção. Serve ao histórico; não dispara agendamento.
- **Item de Checklist**: passo de inspeção padrão de um equipamento específico. Na execução, cada item recebe um *resultado* (Verificado ou Não aplicável) e observação opcional.

## Manutenção

- **Ordem de Serviço (OS)**: registro formal de uma intervenção técnica em um equipamento. Toda OS é *corretiva* ou *preventiva* (nunca ambas). Tem um técnico responsável, prioridade, prazo e status.
- **Manutenção Corretiva**: OS aberta em resposta a uma falha. Registra a causa da falha e se houve impacto na produção.
- **Manutenção Preventiva**: OS programada a partir de um Plano Preventivo. Exige preenchimento do checklist do equipamento.
- **Plano Preventivo**: regra de recorrência de preventiva para um equipamento, com periodicidade Diária, Semanal, Mensal, Trimestral, Semestral ou Anual. Gera OS preventivas.
- **Avaliação da OS**: decisão do supervisor sobre uma OS concluída pelo técnico: Aprovada ou Rejeitada (com justificativa obrigatória). A OS guarda apenas a decisão vigente; uma OS rejeitada volta ao técnico e é avaliada de novo. Só é *consolidada no histórico* após aprovação.
- **Status da OS**: Pendente → Em Execução → Aguardando Aprovação → Concluída (aprovada) ou de volta a Em Execução (rejeitada).

## Estoque

- **Peça (de reposição)**: insumo com código único, nome do fornecedor homologado, estoque mínimo e quantidade atual. O fornecedor é só um dado descritivo; compras ficam fora do sistema.
- **Baixa (de estoque)**: consumo de uma quantidade de uma peça em uma OS. Reduz a quantidade atual.
- **Alerta de estoque mínimo**: notificação disparada quando a quantidade atual fica igual ou abaixo do estoque mínimo, no máximo uma por peça a cada 24 horas.

## Comunicação e indicadores

- **Notificação**: aviso gerado pelo sistema (tipos: Proximidade de prazo, Atraso, Estoque mínimo, Nova OS, Aprovação, Rejeição) e entregue a um ou mais usuários por e-mail ou pela interface web.
- **MTBF**: tempo médio entre falhas de um equipamento (derivado das OS corretivas).
- **MTTR**: tempo médio de reparo (derivado de início/fim de execução das OS corretivas).
