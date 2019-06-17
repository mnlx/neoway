from flask import Flask, jsonify, request
import pika
import uuid
import math
import json
from libs.models import StatusModel
from dotenv import load_dotenv
import os

load_dotenv()

ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './temp_file'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB
app.config['INSERTS_PER_WORKER'] = 10000
app.config['RABBIT_DNS'] = os.getenv('RABBIT_CONTAINER_DNS')
app.config['RABBIT_PORT'] = int(os.getenv('RABBIT_CONTAINER_PORT'))

status_model = StatusModel()


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[-1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['POST'])
def upload_file():
    """
    Receives the uploaded file and then sends it to the RabbitMQ workers
    """
    if not len(request.files):
        return jsonify({'error': 'no file found'})

    for file_name in request.files:
        file = request.files[file_name]
        if allowed_file(file.filename):
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=app.config['RABBIT_DNS'] or 'rabbit',
                                          port=app.config['RABBIT_PORT'] or 5672))
            file_contents = file.read().split(b'\n')[1:]
            message_id = str(uuid.uuid4())
            total_file_parts = math.ceil(len(file_contents) / app.config['INSERTS_PER_WORKER'])
            file_part = 1

            while len(file_contents):
                rows = file_contents[0: app.config['INSERTS_PER_WORKER']]

                body_header = {
                    'part': file_part,
                    'total_parts': total_file_parts,
                    'message_id': message_id
                }

                body_header_bytes = bytes(json.dumps(body_header), 'utf-8')

                # Start publishing message to RabbitMQ server
                channel = connection.channel()
                channel.queue_declare(queue='insert_rows_queue', durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key='insert_rows_queue',
                    body=body_header_bytes + b'\n' + b'\n'.join(rows),
                    mandatory=True,
                    properties=pika.BasicProperties(
                        delivery_mode=2,
                    ))

                del file_contents[0: app.config['INSERTS_PER_WORKER']]
                file_part += 1
            connection.close()

            return jsonify(
                {'info': 'Data sent to be inserted. Use the url in this JSON to check if upload is complete.',
                 'url': request.base_url + 'status?message_id=' + message_id})
        else:
            return jsonify({'error': 'File extension not allowed.'})


@app.route('/status', methods=['GET'])
def check_status():
    """
    Checks the status of the RabbitMQ workers by the message_id associated to them
    """
    message_id = request.args.get('message_id')
    if not message_id:
        return jsonify({'error': 'message_id is empty'})

    status_model.get_message_status(message_id)
    results = status_model.get_message_status(message_id)
    response_json = {
        'message_id': message_id,
        'status': 'not_started',
        'success_count': 0,
        'failed_count': 0,
        'total_parts': 0,
        'completed_parts': 0,
        'failed': [],
        'success': []
    }

    for row in results:
        response_json['total_parts'] = row['total_parts']
        response_json['completed_parts'] += 1
        status_report = {
            'status': row['status'],
            'part': row['part'],
            'message': row['message']
        }

        if row['status'] == 'success':
            response_json['success_count'] += 1
            response_json['success'].append(status_report)
        elif row['status'] == 'fail':
            response_json['failed_count'] += 1
            response_json['failed'].append(status_report)

    if response_json['completed_parts'] == response_json['total_parts']:
        response_json['status'] = 'completed'
    else:
        response_json['status'] = 'incomplete'

    return jsonify(response_json)
