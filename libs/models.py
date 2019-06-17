from sqlalchemy import create_engine
import json
import os


class Model:
    engine = ''

    def __init__(self):
        DB_NAME = os.getenv('DB_NAME')
        DB_USER = os.getenv('DB_USER')
        DB_PASS = os.getenv('DB_PASS')
        DB_HOST = os.getenv('DB_HOST')
        DB_PORT = os.getenv('DB_PORT') or '5432'

        connection_string = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME)
        self.engine = create_engine(connection_string)


class StatusModel(Model):

    def get_message_status(self, message_id):
        sql = '''SELECT * FROM status WHERE message_id='{0}';'''.format(message_id)

        return self.engine.execute(sql)

    def add_status(self, message_id, status, message, part, total_parts):
        # TODO: include transaction time
        sql = '''
          INSERT INTO status  (message_id , completion_time , status, message, part, total_parts) VALUES 
          ('{0}', NOW() , '{1}', '{2}', '{3}', '{4}')
    
        '''.format(message_id, status, json.dumps(message), part, total_parts)

        return self.engine.execute(sql)


class UserPurchaseModel(Model):

    def batch_insert(self, rows):
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

        return self.engine.execute(sql)
