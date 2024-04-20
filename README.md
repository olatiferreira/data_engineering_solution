# Solução para Atualização dos Dados de Forma Resiliente e Estável 🚀

## Objetivo 🎯

Tornar o processo de atualização dos dados através das camadas (bronze, silver e gold) mais resilientes e estável, garantindo os SLAs necessários para o negócio, prevenindo a introdução de más práticas e erros em produção, sejam de implementação ou de configuração. Em caso de detecção de problemas, o desenvolvedor deve ser notificado e orientado sobre como proceder. 

## Tecnologias e Ferramentas 💻

- **Armazenamento:** [AWS S3](https://aws.amazon.com/pt/s3/)
- **Processamento:** [Databricks](https://www.databricks.com/br)
- **Análise:** [ThoughtSpot](https://www.thoughtspot.com/)
- **Orquestração:** [Airflow](https://airflow.apache.org/)
- **Controle de versão:** [GitLab](https://about.gitlab.com/)

## Resumo 🔎

1. Pipeline de dados automatizado que extrai dados de fontes originais e os armazena no S3;

2. O Databricks será utilizado para processar e limpar os dados oriundos do S3, aplicando regras de validação, transformações e agregando dados de diferentes fontes;

3. Os dados refinados poderão ser integrados no ThoughtSpot para que os usuários de negócios possam explorá-los e analisá-los;

4. O Airflow irá orquestrar o fluxo de trabalho de todo o pipeline, agendando tarefas de extração, processamento, carregamento e análise, inclusive notificando e orientando o desenvolvedor em caso de falhas;

5. Testes de unidade e integração serão implementados para garantir a qualidade e confiabilidade do pipeline;

6. O pipeline de dados e a arquitetura do produto analítico deverá ser documentado de forma macro para facilitar a compreensão e a manutenção pelo próprio desenvolvedor e/ou de seus pares.

## Arquitetura 🎲

![App Screenshot](https://via.placeholder.com/468x300?text=App+Screenshot+Here)


## Etapas 📃

#### 1. Coleta de Dados

- Os dados brutos serão coletados de suas fontes originais e armazenados na camada bronze do S3, em formato parquet;

- Os metadados dos dados (fonte, data, schema, etc.) poderão ser armazenados em um banco de dados NoSQL, como por exemplo o DynamoDB, facilitando a consulta, gerenciamento e governança.

#### 2. Processamento

- O Databricks será utilizado como plataforma de processamento de dados em nuvem, que além de prover recursos de clusterização, também irá oferecer provisionamento automático para lidar com grandes volumes de dados para executar as tarefas de ETL (extração, transformação e carregamento), limpeza e preparação dos dados;

- Cada notebook será executado em um cluster Databricks dedicado, aproveitando a escalabilidade e o poder de processamento da plataforma.

#### 3. Controle de Versão e Colaboração

- O GitLab será utilizado como repositório central para armazenar o código do pipeline de dados, documentação e outros recursos relacionados (notebooks Python/SQL);

    - Ele facilitará a colaboração entre equipes, a revisão de código e o controle de versões.

#### 4. Validação dos Dados

- Antes dos dados serem carregados para as próximas camadas, os dados serão validados para garantir a qualidade, consistência e integridade;

- Regras de validação customizadas poderão ser implementadas para cada tipo de dado e etapa do pipeline;

- Em caso de inconsistências, o desenvolvedor responsável pelo notebook será notificado via e-mail e/ou Slack;
    - A notificação poderá incluir detalhes do erro, logs e instruções sobre como corrigi-lo.

    #### 4.1. Teste Unitário

    - Testes unitários automatizados serão implementados para garantir o funcionamento correto dos notebooks;

    - Os testes serão executados antes de cada execução do pipeline no Databricks;

    - Falhas nos testes unitários impedirão a execução do pipeline em produção, prevenindo a introdução de erros.

#### 5. Armazenamento dos Dados

- Para prover escalabilidade e durabilidade dos dados, eles serão armazenados em camadas no AWS S3, conforme abaixo:

    - **Bronze:** Dados brutos na forma original.
    - **Silver:** Dados transformados.
    - **Gold:** Dados validados e prontos para análise e uso pelas unidades de negócio, utilizando o ThoughtSpot por exemplo.

#### 6. Análise e Visualização

- O ThoughtSpot será utilizado como plataforma de análise de dados self-service, fornecendo aos usuários de negócio acesso interativo e visual aos dados da camada gold;

- Os usuários poderão explorar os dados, criar dashboards e relatórios personalizados, sem a necessidade de conhecimento técnico aprofundado.

#### 7. Orquestração, Monitoramento e Governança

- O Airflow irá monitorar a execução dos notebooks e pipelines, notificando os desenvolvedores via e-mail e/ou Slack, em caso de falhas ou atrasos;

- Logs detalhados de cada etapa do processo serão armazenados no AWS S3 para análise e investigação em caso de problemas;

- Políticas de acesso e segurança são implementadas no AWS S3, Databricks e ThoughtSpot para controlar o acesso aos dados e garantir a confidencialidade e integridade dos dados.

    #### 7.1 Monitoramento de Desempenho

    - Métricas de desempenho dos pipelines (tempo de execução, volume de dados processados, taxa de erros, etc) serão coletadas e armazenadas para fins de observabilidade;

    - Dashboards e alertas serão configurados para monitorar as métricas de desempenho e identificar gargalos ou anomalias;

     - Ações automatizadas poderão ser configuradas para escalar recursos ou reexecutar pipelines em caso de problemas de desempenho.

    #### 7.2 Governança de Dados

    - Um catálogo de dados será implementado para documentar as fontes de dados, pipelines, tabelas e outros artefatos relacionados à gestão de dados;

    - Políticas de qualidade de dados serão definidas e aplicadas para garantir a confiabilidade e a integridade dos dados;

    - Controles de acesso granular serão implementados para restringir o acesso aos dados com base nas funções e responsabilidades dos usuários.

## Trade-offs 🔄

- **Custo:** A utilização de ferramentas como Databricks e ThoughtSpot poderão gerar custos adicionais. No entanto, o retorno do investimento (ROI) da solução poderá ser significativo em termos de maior eficiência, produtividade e redução de riscos.

- **Complexidade:** A implementação da solução completa poderá exigir um investimento inicial em treinamento e familiarização das equipes com as novas ferramentas. No entanto, a longo prazo, a solução irá contribuir para a padronização dos processos, reduzindo o tempo de desenvolvimento e a necessidade de manutenção dos pipelines.

## Benefícios 🎁

- **Armazenamento centralizado e seguro de dados:** O S3 garante que seus dados estejam sempre disponíveis e protegidos.

- **Processamento de dados escalável e eficiente:** O Databricks permite lidar com grandes volumes de dados de forma eficiente e escalável.

- **Análise de dados self-service:** O ThoughtSpot capacita os usuários de negócios a explorar e analisar dados sem a necessidade de conhecimento técnico aprofundado.

- **Orquestração automatizada de tarefas:** O Airflow garante que o pipeline de dados seja executado de forma confiável e consistente.

- **Controle de versão e colaboração:** O GitLab facilita a colaboração entre equipes e o controle de versões do código do pipeline.

## Desenvolvido por ✨

- [Ítalo César Ferreira da Costa](https://www.olatiferreira.com)