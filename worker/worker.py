import json
import pika
from sqlalchemy.exc import IntegrityError, ProgrammingError
from libs.utils import clean_data
from libs.models import StatusModel, UserPurchaseModel
from dotenv import load_dotenv
import os

load_dotenv()

RABBIT_DNS = os.getenv('RABBIT_CONTAINER_DNS')
RABBIT_PORT = int(os.getenv('RABBIT_CONTAINER_PORT'))

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBIT_DNS or 'localhost', port=RABBIT_PORT or 5672))
channel = connection.channel()
channel.queue_declare(queue='insert_rows_queue', durable=True)


def callback(ch, method, properties, file_chunk):
    rows = file_chunk.split(b'\n')
    status_object = {
        'wrong_columns_count': 0,
        'invalid_date': 0,
        'invalid_cpf_count': 0,
        'invalid_loja_mais_frequente': 0,
        'invalid_loja_ultima_compra': 0,
        'total_rows': len(rows) - 1,  # Minus header sent by rabbitmq
        'total_added': 0
    }
    cleaned_data = []
    message_id = ''
    part = 0
    total_parts = 0

    for i, row in enumerate(rows):
        if i == 0:
            body_header_raw = row.decode('utf-8')
            body_header = json.loads(body_header_raw)
            part = body_header['part']
            total_parts = body_header['total_parts']
            message_id = body_header['message_id']
            continue

        columns = row.split()

        # Linhas com mais ou menos 8 colunas não são adicionados
        if len(columns) != 8:
            status_object['wrong_column_count'] += 1
            continue

        cleaned_data.append(clean_data(columns, status_object))

        status_object['total_added'] += 1

    status_model = StatusModel()
    user_purchase = UserPurchaseModel()

    try:
        user_purchase.batch_insert(cleaned_data)
        status_model.add_status(message_id, 'success', status_object, part, total_parts)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except (IntegrityError, ProgrammingError) as e:
        status_model.add_status(message_id, 'fail', {'error': e.args[0]}, part, total_parts)
        ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='insert_rows_queue', on_message_callback=callback)
channel.start_consuming()
