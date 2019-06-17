import re
from datetime import datetime


def verify_cpf(cpf):
    """
    CPF numbers follow mathematical equations. This function checks if the numbers are valid.
    """
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
    """
    CNPJ numbers follow mathematical equations. This function checks if the numbers are valid.
    """
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


def valid_bool(number):
    valid = False
    if number.count(b'1') == 1 or number.count(b'0') == 1:
        valid = True

    return valid


def valid_date(date):
    valid = False
    if len(date) != 10:
        return False
    try:
        datetime.strptime(date.decode('utf-8'), '%Y-%m-%d')
        valid = True
    except ValueError as e:
        print(e.args[0])
    return valid


def valid_float(number):
    valid = False
    try:
        float(re.sub(b',', b'.', number))
        valid = True
    except ValueError as e:
        print(e.args[0])
    return valid


def clean_data(row, status_object):
    """
    Cleans and validates the data for each of the columns in the row.
    """
    cpf_raw = row[0]
    private_raw = row[1]
    incompleto_raw = row[2]
    data_ultima_compra = row[3]
    ticket_medio_raw = row[4]
    ticket_ultima_compra_raw = row[5]
    loja_mais_frequente_raw = row[6]
    loja_ultima_compra_raw = row[7]

    cleaned_data = {}

    # Verificação do CPF
    if cpf_raw != b'NULL':
        cleaned_data['cpf'] = cpf_raw.decode('utf-8')
        cleaned_data['cpf_valido'] = verify_cpf(cleaned_data['cpf'])
        if not cleaned_data['cpf_valido']:
            status_object['invalid_cpf_count'] += 1

    # Verificação dos booleanos
    if valid_bool(private_raw):
        cleaned_data['private'] = private_raw.count(b'1') == 1
    if valid_bool(incompleto_raw):
        cleaned_data['incompleto'] = incompleto_raw.count(b'1') == 1

    # Verificação da data da última compra
    if valid_date(data_ultima_compra):
        cleaned_data['data_ultima_compra'] = data_ultima_compra.decode('utf-8')

    # Verificação preço dos tickets
    if valid_float(ticket_medio_raw):
        cleaned_data['ticket_medio'] = float(re.sub(b',', b'.', ticket_medio_raw))
    if valid_float(ticket_ultima_compra_raw):
        cleaned_data['ticket_ultima_compra'] = float(re.sub(b',', b'.', ticket_ultima_compra_raw))

    # Verificação CNPJ das lojas
    if loja_mais_frequente_raw != b'NULL':
        cleaned_data['loja_mais_frequente'] = loja_mais_frequente_raw.decode('utf-8')
        cleaned_data['cnpj_loja_mais_frequente_valido'] = verify_cnpj(cleaned_data['loja_mais_frequente'])
        if not cleaned_data['cnpj_loja_mais_frequente_valido']:
            status_object['invalid_loja_mais_frequente'] += 1
    if loja_ultima_compra_raw != b'NULL':
        cleaned_data['loja_ultima_compra'] = loja_ultima_compra_raw.decode('utf-8')
        cleaned_data['cnpj_loja_ultima_compra_valido'] = verify_cnpj(cleaned_data['loja_ultima_compra'])
        if not cleaned_data['cnpj_loja_ultima_compra_valido']:
            status_object['invalid_loja_ultima_compra'] += 1

    return cleaned_data
