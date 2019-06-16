create table user_purchase
(
    id                              serial      not null
        constraint user_purchase_pkey
            primary key,
    cpf                             varchar(20) not null
        constraint user_purchase_cpf_key
            unique,
    private                         boolean,
    incompleto                      boolean,
    data_ultima_compra              date,
    ticket_medio                    double precision,
    ticket_ultima_compra            double precision,
    loja_mais_frequente             varchar(20),
    loja_ultima_compra              varchar(20),
    cpf_valido                      boolean,
    cnpj_loja_mais_frequente_valido boolean,
    cnpj_loja_ultima_compra_valido  boolean
);

alter table user_purchase
    owner to neoway;



CREATE TYPE queue_worker_status AS ENUM ('success', 'fail');



CREATE TABLE logs (
    id VARCHAR(36) UNIQUE PRIMARY KEY,
    completion_time TIMESTAMP,
    status queue_worker_status,
    message jsonb
)