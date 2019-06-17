CREATE TABLE user_purchase
(
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(20) NOT NULL UNIQUE,
    private                         BOOLEAN,
    incompleto                      BOOLEAN,
    data_ultima_compra              DATE,
    ticket_medio                    DOUBLE PRECISION,
    ticket_ultima_compra            DOUBLE PRECISION,
    loja_mais_frequente             VARCHAR(20),
    loja_ultima_compra              VARCHAR(20),
    cpf_valido                      BOOLEAN,
    cnpj_loja_mais_frequente_valido BOOLEAN,
    cnpj_loja_ultima_compra_valido  BOOLEAN
);


CREATE TYPE queue_worker_status AS ENUM ('success', 'fail');

CREATE TABLE status (
    id SERIAL PRIMARY KEY ,
    message_id VARCHAR(36)  ,
    completion_time TIMESTAMP,
    status queue_worker_status,
    message JSONB,
    part INT,
    total_parts INT
);
