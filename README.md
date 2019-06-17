

Abaixo seguem os passos necessarios para fazer o serviço rodar. Logo depois, faço um breve resumo justificando
algumas das escolhas feitas ao montar o serviço.
 
Step 1:
Clone git

git clone git@github.com:mnlx/neoway.git

Step 2:
Rode o ddl e gere as tabelas necessárias. 

nome arquivo: ddl.sql

Step 3:
Crie dois arquivos .env, e adiciona eles nas pastas dos containers web e worker.

Estrutura:
web/.env
worker/.env

O exemplo abaixo serve para os dois containers:
 
#mandatory
DB_NAME=userpurchase
DB_USER=neoway
DB_PASS=<PASSWORD>
DB_HOST=localhost


#optional
DB_PORT=5432 # Defaults to 5432
RABBIT_CONTAINER_DNS=localhost
RABBIT_CONTAINER_PORT=5672

Step 4:
Rode o docker-compose up com a flag build para construir e rodar os containers

Commando: docker-compose up -d --build 


Step 5:
Com os containers rodando, da para começar a utilizar o serviço. Na maneira que eu implementei, é necessário seguir
duas etapas. A primeira etapa consiste em enviar o arquivo que é para ser inserido no banco de dados para o servidor, 
o servidor distribuí o processamento para os worker containers que estiverem conectados através do RabbitMQ.
Estes trabalhadores limpam os dados e verificam qualquer inconsistência e depois inserem no banco de dados.

Abaixo segue um exemplo de como que pode ser feito esse upload, aqui eu uso curl, mas qualquer ferramenta que consiga 
fazer POST de arquivo deverá funcionar.

curl -F base_teste=@./base_teste.txt http://0.0.0.0

Exemplo reposta:

{"info":"Data sent to be inserted. Use the url in this JSON to check if upload is complete.",
"url":"http://0.0.0.0/status?message_id=520204c2-8a6f-44a6-bd26-42fe2b19515e"}


A segunda etapa consiste em ver o status do processamento, isso pode ser feito através de um outro serviço que checa
o status dos trabalhadores. O link desse serviço é retornado quando se upa o arquivo na primeira etapa (pode ser visto
no exemplo resposta acima).


O link pode ser acessado no browser ou qualquer ferramenta de requisação http. Abaixo eu utilizo o curl novamente.

curl http://0.0.0.0/status?message_id=520204c2-8a6f-44a6-bd26-42fe2b19515e

exemplo resposta: 
{"completed_parts":5,"failed":[{"message":{"error":"(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"user_purchase_cpf_key\"\nDETAIL:  Key (cpf)=(041.091.641-25) already exists.\n"},"part":1,"status":"fail"},{"message":{"error":"(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"user_purchase_cpf_key\"\nDETAIL:  Key (cpf)=(093.520.454-75) already exists.\n"},"part":2,"status":"fail"},{"message":{"error":"(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"user_purchase_cpf_key\"\nDETAIL:  Key (cpf)=(442.944.330-00) already exists.\n"},"part":3,"status":"fail"},{"message":{"error":"(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"user_purchase_cpf_key\"\nDETAIL:  Key (cpf)=(032.812.939-99) already exists.\n"},"part":4,"status":"fail"},{"message":{"error":"(psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint \"user_purchase_cpf_key\"\nDETAIL:  Key (cpf)=(059.147.058-60) already exists.\n"},"part":5,"status":"fail"}],"failed_count":5,"message_id":"520204c2-8a6f-44a6-bd26-42fe2b19515e","status":"completed","success":[],"success_count":0,"total_parts":5}

No exemplo retornado acima, todas as partes falharam. Neste caso o erro aconteceu porque a inserção do arquivo já tinha 
sido feita anteriormente.

A resposta do serviço de status retorna algumas informações importantes. Uma dessas informações é o número de partes
em que o arquivo foi divído. Eu configurei para dividir em 10 mil linhas por parte, esse número pode ser ajustado 
para qualquer valor. Como o arquivo teste tem 50 mil linhas, o serviço divide o arquivo em 5 partes e publica 5 mensagens
no RabbitMQ. 

Outras informações importantes são as contagens de sucesso e falha das execuções das partes. No exemplo
acima podemos ver que o failed_count é igual a 5 e o total de partes é 5, ou seja, todas as partes falharam.  

As arrays de falha e sucesso explicam o motivo dos dados terem sido inseridos ou não. No caso da array de falhas, como 
se pode notar pelo exemplo acima, têm-se o motivo da falha, neste caso o CPF é unique, portanto tentou-se inserir um CPF 
duplicado. No caso do array de sucesso há várias informações importantes. Segue abaixo um exemplo de um item no array 
de sucesso:

"success":[{"message":{"invalid_cpf_count":1,"invalid_date":0,"invalid_loja_mais_frequente":0,"invalid_loja_ultima_compra":0,"total_added":10000,"total_rows":10000,"wrong_columns_count":0},"part":1,"status":"success"}]

Como se pode notar, a array retorna o número de cpfs e cnpjs invalidos, o total de linhas recebidas e o total dessas que
foram inseridas, e as linhas que tinham colunas a mais ou a menos
.


Explicando algumas escolhas:

A biblioteca psycopg2-binary utilizada para conectar com o banco Postgres não é recomendada em produção, o ideal é
que o build da biblioteca seja feito na máquina na qual o serviço vai rodar. O não uso da biblioteca se deu por
causa de tempo.

O uso de um message broker, neste caso RabbitMQ, se deu por motivos de performance. Ele facilita a paralelização de
execução e por isso aumentar a velocidade de inserção de dados no banco. Apesar de que no teste o arquivo só tenha 
por volta de 50k linhas, se o serviço fosse utilizado com arquivos bem maiores, ele executaria em um tempo razoável.
A paralelização tem outra vantagem de reduzir os batch inserts, que quando demasiadamente grandes podem sobrecarregar 
o banco.

O arquivo docker-compose.yml foi simplificado para rodar com Postgres na máquina local. Por isso que o network mode está como
host. Se não o banco teria que ser configurado para aceitar conexões de fora. O ideal seria acessar o banco sem que
o localhost fosse compartilhado. Para isso poderia adicionar o script docker-entrypoint.sh que está de exemplo no 
repositório. Ele acrescento um dns padrão para o host, neste caso host.docker.internal.

Por último, a melhor escolha para rodar o serviço nos containers seria utilizar um swarm que ajustasse a quantidade dos 
de containers por serviço a medida que a utilização de um aumentasse. Por motivo de tempo, eu resolvi simplificar e deixar
os containers estáticos, e duplicar a criação dos containers de trabalho.