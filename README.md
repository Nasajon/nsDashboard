# FORK DO REDASH

Este repositório contém um fork do Redash (referências abaixo), criado com os seguintes propósitos:

1. Implementar suporte ao modelo de arquitetura multitenant utilizada pela Nasajon
2. Implementar um mecanismo de "portlet" que permita "colar" gráficos e tabelas do redash, em aplicações diversas da Nasajon (ocultando do cliente a edição da query, por exemplo).
3. Alterar o tema visual do redash, para refletir o padrão da Nasajon.

Além disto, outros benefícios podem ser pensados a longo prazo, como:

* Alterar interface de administração do redash, para ter suporte multitenant, ao ponto que se possa customizar queries para um único cliente.
* Adicionar suporte a um conjunto de variáveis (que façam sentido no contexto da Nasajon), de modo que se possa utilizar nas queries estas variáveis, sem se preocupar com o preenchimento de seus valores (ex: C_GRUPO_EMPRESARIAL, seria automaticamente trocado pelo grupo empresarial da sessão, ao se executar uma query).
* Permitir interação com as tabelas e gráficos do redash (drill down ou mesmo caixas de seleção que permitar não apenas ver, mas recuperar as linhas selecionadas).

Por fim, importa destacar que o fork tem por objetivo (ao menos inicialmente) de implementar mudanças que não impeçam posterior "rebase" com o repositório original (para que a Nasajon continue podendo utilizar as novidades do redash.

*Obs. 1: Futuramente será decidido se estaremos contribuindo para o projeto original da ferramenta.*

*Obs. 2: A saber, foi realizado um [estudo prévio](https://drive.google.com/open?id=1m7sSPUbGNAnSw18DBCB_SXfYpzTP7XnDRTFt9_epXsQ) antes da decisão por realizar um fork do Redash.*

## Montando ambiente de desenvolvimento (Com Docker)

Para preparar o ambiente de desenvolvimento, basta seguir a [documentação oficial do redash](https://redash.io/help/open-source/dev-guide/docker).

## Montando ambiente de desenvolvimento (Sem Docker)

* Tenha previamente instalado:
  * [PostgreSQL](https://www.postgresql.org/download/) .
  * [Npm](https://nodejs.org/en/download/) .
  * [Python](https://www.python.org/downloads/) .
* Clone o projeto do repositório para sua máquina.
* Navegue para dentro da pasta do projeto e execute os seguintes comandos.
```shell
# Instalando as dependências do front
> npm i

# Instalando as dependências do serviço
> py -m pip install -r requirements.txt

# Buildando o Front
> npm run build_windows

# Levantando o serviço. Troque os valores entre '<' e '>' para atender as suas configurações de banco.
> py main.py -u <usuario_banco> -s <senha_banco> -i <localhost> -p <porta_banco> -b <nome_banco>
```

## Suporte Multi-Tenant

A implementação do suporte ao multi-tenant de acordo com a arquitetura da Nasajon, se deu por meio da ideia da criação de uma variável chamada ```C_TENANT```, que passa a estar disponível na contrução das queries. Isto é, o programador pode simplemente adicionar uma condição ```and tenant = C_TENANT``` na cláusula _where_ de suas queries, sem se preocupar com o preenchimento desta variável.

Isto foi possível por meio da criação de novos executores de query, conforme [documentação](https://discuss.redash.io/t/creating-a-new-query-runner-data-source-in-redash/347) do redash.

---
Obs.: É importante observar que faltou na documentação do redash o passo abaixo, para que o novo executor de query fique de fato disponível para uso na interface do redash:

* Adicione o nome do módulo do novo executor de queries, no arquivo ```redash/settings/__init__.py```, como parte do vetor ```default_query_runners```.
---

Além disto (por hora) o tenant utilizado por cada usuário está sendo persistido no _Redis_, numa chave denominada ```USER_TENANT_<USER_ID>```, onde o id do usuário é a chave primária do redash, para um usuário do mesmo (que também pode ser identificado por seu e-mail).

Foram criados os seguintes artefatos:

* **multi_tenant_util.py:** Módulo que contém os métodos necessários para gravação e recuperação do tenant no *Redis*, além de um método para tratamento de uma query antes de sua execução (substituindo a contante do tenant na query).
* **pg_multi_tenant.py:** Extensão do executor de queries para PostgreSQL padrão do Redash, onde uma query é tratada (com relação ao tenant) antes de sua execução.
* **mysql_multi_tenant.py:** TODO

Para testar a solução, siga os passos a seguir:

1. Inicie o redash
2. Crie uma nova conexão a um banco de dados Postgre, utilizando o conector denominado *PostgreSQLMultiTenant*.
3. Construa uma query qualquer com uma condição filtrando por ```tenant = C_TENANT```
4. Execute a query

Para coletar o tenant de um usuário, decidimos alterar o método login para fazer login no keycloak e coletar o access_token do usuário. Com o token podemos fazer uma requisição para coletar os tenants do usuário e salvar no usuário do redash. Também alteramos o tempo máximo de sessão do usuário através de uma variável de ambiente, para podermos configurar para ser igual ao tempo de expiração do token.


## Mecanismo de Portlet

Para poder acessar uma query de fora do redash, basta acessar a rota http://xxxxx.nasajon.com.br/embed/query/{query_id}/visualization/{visualization_id}/tenant/{tenant}?api_key={api_key}. A query_id, visualization_id e api_key podem ser obtidos pelo redash na página da query. O tenant tem que ser obtido a partir do usuário logado no site que está usando o portlet.

Para esse suporte tivemos que criar um novo endereço no frontend e backend. O frontend fica na classe VisualizationEmbedTenant e o backend fica na classe QueryResultTenantResource.

##  Tema Visual

Por padrão o redash usa arquivos do tipo less para o tema, sendo less uma extensão do css. Para alterar o tema, o recomendado é criar ou alterar arquivos em cliente/app/assets/less/redash. Caso seja adicionado um novo arquivo, é necessário importá-lo no main.less.

## Adicionar Usuários por Query no Banco

Para adicionar um usuário usar o seguinte comando:

```
python3 create_user.py -u usuario_banco -s senha_banco -i localhost -p porta -b nome_banco --user_name nome --user_email email --user_tenant tenant --user_password senha_usuario --admin
```

O pârametro admin só precisa ser adicionado se o usuário precisar ser um admin do redash.

---

## README.MD ORIGINAL DO REDASH

<p align="center">
  <img title="Redash" src='https://redash.io/assets/images/logo.png' width="200px"/>
</p>

[![Documentation](https://img.shields.io/badge/docs-redash.io/help-brightgreen.svg)](https://redash.io/help/)
[![Datree](https://s3.amazonaws.com/catalog.static.datree.io/datree-badge-20px.svg)](https://datree.io/?src=badge)
[![Build Status](https://circleci.com/gh/getredash/redash.png?style=shield&circle-token=8a695aa5ec2cbfa89b48c275aea298318016f040)](https://circleci.com/gh/getredash/redash/tree/master)

**_Redash_** is our take on freeing the data within our company in a way that will better fit our culture and usage patterns.

Prior to **_Redash_**, we tried to use traditional BI suites and discovered a set of bloated, technically challenged and slow tools/flows. What we were looking for was a more hacker'ish way to look at data, so we built one.

**_Redash_** was built to allow fast and easy access to billions of records, that we process and collect using Amazon Redshift ("petabyte scale data warehouse" that "speaks" PostgreSQL).
Today **_Redash_** has support for querying multiple databases, including: Redshift, Google BigQuery, PostgreSQL, MySQL, Graphite, Presto, Google Spreadsheets, Cloudera Impala, Hive and custom scripts.

**_Redash_** consists of two parts:

1. **Query Editor**: think of [JS Fiddle](https://jsfiddle.net) for SQL queries. It's your way to share data in the organization in an open way, by sharing both the dataset and the query that generated it. This way everyone can peer review not only the resulting dataset but also the process that generated it. Also it's possible to fork it and generate new datasets and reach new insights.
2. **Visualizations and Dashboards**: once you have a dataset, you can create different visualizations out of it, and then combine several visualizations into a single dashboard. Currently Redash supports charts, pivot table, cohorts and [more](https://redash.io/help/user-guide/visualizations/visualization-types).

<img src="https://raw.githubusercontent.com/getredash/website/8e820cd02c73a8ddf4f946a9d293c54fd3fb08b9/website/_assets/images/redash-anim.gif" width="80%"/>

## Getting Started

* [Setting up Redash instance](https://redash.io/help/open-source/setup) (includes links to ready made AWS/GCE images).
* [Documentation](https://redash.io/help/).

## Supported Data Sources

Redash supports more than 35 [data sources](https://redash.io/help/data-sources/supported-data-sources). 

## Getting Help

* Issues: https://github.com/getredash/redash/issues
* Discussion Forum: https://discuss.redash.io/

## Reporting Bugs and Contributing Code

* Want to report a bug or request a feature? Please open [an issue](https://github.com/getredash/redash/issues/new).
* Want to help us build **_Redash_**? Fork the project, edit in a [dev environment](https://redash.io/help-onpremise/dev/guide.html), and make a pull request. We need all the help we can get!

## Security

Please email security@redash.io to report any security vulnerabilities. We will acknowledge receipt of your vulnerability and strive to send you regular updates about our progress. If you're curious about the status of your disclosure please feel free to email us again. If you want to encrypt your disclosure email, you can use [this PGP key](https://keybase.io/arikfr/key.asc).

## License

BSD-2-Clause.
