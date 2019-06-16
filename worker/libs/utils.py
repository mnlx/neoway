import re
import json

def verify_cpf(cpf):
    cpf = re.sub(r'\D', '', cpf)

    if len(cpf) != 11:
        return False

    # Início da verificação do primeiro dígito do CPF
    acumulator = 0
    for multiplier, digit in zip(range(10, 1, -1), cpf):
        acumulator += multiplier * int(digit)

    remainder = acumulator % 11
    valid_cpf = False

    if remainder <= 1 and int(cpf[9]) == 0:
        valid_cpf = True
    elif int(cpf[9]) == 11 - remainder:
        valid_cpf = True

    # Início da verificação do segundo digito do CPF
    if valid_cpf:
        acumulator = 0
        for multiplier, digit in zip(range(11, 1, -1), cpf):
            acumulator += multiplier * int(digit)

        remainder = acumulator % 11

        if remainder <= 1 and int(cpf[10]) == 0:
            valid_cpf = True
        elif int(cpf[10]) == 11 - remainder:
            valid_cpf = True
        else:
            valid_cpf = False

    return valid_cpf


def verify_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', cnpj)
    valid_cnpj = False

    if len(cnpj) != 14:
        return False

    # Início da verificação do primeiro dígito do CNPJ
    weights = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    acumulator = 0
    for weight, digit in zip(weights[1:], cnpj):
        acumulator += weight * int(digit)

    remainder = acumulator % 11

    if remainder <= 1 and int(cnpj[12]) == 0:
        valid_cnpj = True
    elif int(cnpj[12]) == 11 - remainder:
        valid_cnpj = True

    # Início da verificação do segundo digito do CNPJ
    if valid_cnpj:
        acumulator = 0
        for multiplier, digit in zip(weights, cnpj):
            acumulator += multiplier * int(digit)

        remainder = acumulator % 11

        if remainder <= 1 and int(cnpj[13]) == 0:
            valid_cnpj = True
        elif int(cnpj[13]) == 11 - remainder:
            valid_cnpj = True
        else:
            valid_cnpj = False

    return valid_cnpj


def clean_data(row, response_json):
    cpf_raw = row[0]
    private_raw = row[1]
    incompleto_raw = row[2]
    data_ultima_compra = row[3]
    ticket_medio_raw = row[4]
    ticket_ultima_compra_raw = row[5]
    loja_mais_frequente_raw = row[6]
    loja_ultima_compra_raw = row[7]

    cleaned_data = {}

    if cpf_raw != b'NULL':
        cleaned_data['cpf'] = cpf_raw.decode('utf-8')
        cleaned_data['cpf_valido'] = verify_cpf(cleaned_data['cpf'])
        if not cleaned_data['cpf_valido']:
            response_json['invalid_cpf_count'] += 1
    if private_raw != b'NULL':
        cleaned_data['private'] = not private_raw.find(b'1')
    if incompleto_raw != b'NULL':
        cleaned_data['incompleto'] = not incompleto_raw.find(b'1')
    if data_ultima_compra != b'NULL' and len(data_ultima_compra) == 10:
        # TODO: checkif datetime
        cleaned_data['data_ultima_compra'] = data_ultima_compra.decode('utf-8')
    if ticket_medio_raw != b'NULL':
        cleaned_data['ticket_medio'] = float(re.sub(b',', b'.', ticket_medio_raw))
    if ticket_ultima_compra_raw != b'NULL':
        cleaned_data['ticket_ultima_compra'] = float(re.sub(b',', b'.', ticket_ultima_compra_raw))
    if loja_mais_frequente_raw != b'NULL':
        cleaned_data['loja_mais_frequente'] = loja_mais_frequente_raw.decode('utf-8')
        cleaned_data['cnpj_loja_mais_frequente_valido'] = verify_cnpj(cleaned_data['loja_mais_frequente'])
        if not cleaned_data['cnpj_loja_mais_frequente_valido']:
            response_json['invalid_loja_mais_frequente'] += 1
    if loja_ultima_compra_raw != b'NULL':
        cleaned_data['loja_ultima_compra'] = loja_ultima_compra_raw.decode('utf-8')
        cleaned_data['cnpj_loja_ultima_compra_valido'] = verify_cnpj(cleaned_data['loja_ultima_compra'])
        if not cleaned_data['cnpj_loja_ultima_compra_valido']:
            response_json['invalid_loja_ultima_compra'] += 1
    return cleaned_data


def create_bulk_insert_sql(rows):
    insert_format_string = "('{0}', {1}, {2}, {3}, {4}, {5}, '{6}', '{7}', {8}, {9}, {10})"
    inserts_list = [
        insert_format_string.format('cpf' in row and row['cpf'] or 'NULL',
                                    'private' in row and row['private'] or 'NULL',
                                    'incompleto' in row and row['incompleto'] or 'NULL',
                                    'data_ultima_compra' in row and "'" + row[
                                        'data_ultima_compra'] + "'::timestamp" or 'NULL',
                                    'ticket_medio' in row and row['ticket_medio'] or 'NULL',
                                    'ticket_ultima_compra' in row and row['ticket_ultima_compra'] or 'NULL',
                                    'loja_mais_frequente' in row and row['loja_mais_frequente'] or 'NULL',
                                    'loja_ultima_compra' in row and row['loja_ultima_compra'] or 'NULL',
                                    'cpf_valido' in row and row['cpf_valido'],
                                    'cnpj_loja_mais_frequente_valido' in row and row[
                                        'cnpj_loja_mais_frequente_valido'] or 'NULL',
                                    'cnpj_loja_ultima_compra_valido' in row and row[
                                        'cnpj_loja_ultima_compra_valido'] or 'NULL').replace("'NULL'", 'NULL')
        for row in rows
    ]

    sql = '''INSERT INTO user_purchase (cpf, private, incompleto, data_ultima_compra, ticket_medio, 
    ticket_ultima_compra, loja_mais_frequente, loja_ultima_compra, cpf_valido, cnpj_loja_mais_frequente_valido, 
    cnpj_loja_ultima_compra_valido) VALUES ''' + ','.join(inserts_list)
    return sql


def create_log_sql(message_id, status, message, part, total_parts):
    # TODO: include transaction time
    sql = '''
      INSERT INTO logs  (message_id , completion_time , status, message, part, total_parts) VALUES 
      ('{0}', NOW() , '{1}', '{2}', '{3}', '{4}')
    
    '''.format(message_id, status, json.dumps(message), part, total_parts)


    return sql
