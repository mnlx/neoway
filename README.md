sudo apt install postgresql libpq-dev   (talvez n"ao precisa do postgres)



Instalar Docker CE (https://docs.docker.com/ explica como)
Instalar docker e docker compose

docker build --tag=neoway-test .
docker build --tag=neoway-worker .


docker-compose up -d --build



Explicar oporque utilizo o psycopg2-binary

sudo apt install curl


 curl -F base_teste=@/home/monolux/Downloads/basetest/base_teste.txt http://0.0.0.0:8000/parsedata/
 
 
 Ao trabalhar com dados, especialmente em situações de ETL, parece haver dois tipos de problemas principais que 
 precisam ser resolvidos. O primeiro é em relação a formatação do dos dados. Ao inserir novos dados em um banco relacional,
 por exemplo, é necessário verificar se o número de colunas por linhas é igual para todas as linhas, e se o total de linhas
 inseridas é igual a quantidade de linhas presente no código fonte. 
 
 
 Steps 1:
 Clone git
 
 git clone git@github.com:mnlx/neoway.git
 
 Step 2:
 Rode o ddl e gere as tabelas necessárias
 
 nome arquivo: ddl.sql