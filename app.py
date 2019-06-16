import os
from flask import Flask, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
import pika
import uuid
import math
import json

ALLOWED_EXTENSIONS = set(['txt'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './temp_file'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024 #50MB
app.config['INSERTS_PER_WORKER'] = 10000




def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['POST'])
def upload_file():
    if not len(request.files):
        return jsonify({'error': 'no file found'})

    # TODO: remove extra loop
    for file_name in request.files:
        file = request.files[file_name]
        if allowed_file(file.filename):
            file_contents = file.read().split(b'\n')[1:]

            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host='localhost'))
            channel = connection.channel()
            channel.queue_declare(queue='insert_rows_queue', durable=True)

            message_id = str(uuid.uuid4())
            total_file_parts = math.ceil( len(file_contents)/app.config['INSERTS_PER_WORKER'])

            file_part = 1
            while len(file_contents):
                rows = file_contents[0 : app.config['INSERTS_PER_WORKER']]

                body_header = {
                    'part' : file_part,
                    'total_parts' : total_file_parts,
                    'message_id' : message_id
                }

                body_header_bytes = bytes( json.dumps(body_header), 'utf-8')

                channel.basic_publish(
                    exchange='',
                    routing_key='insert_rows_queue',
                    body=  body_header_bytes + b'\n' + b'\n'.join(rows),
                    mandatory=True,
                    properties=pika.BasicProperties(
                        delivery_mode=2,  # make message persistent
                    ))

                del file_contents[0 : app.config['INSERTS_PER_WORKER']]
                file_part += 1
            connection.close()







            # filename = secure_filename(file.filename)
            # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return jsonify({'info': 'Data sent to be inserted. Use the url in this JSON to check if upload is complete.',
                            'url' : 'http://localhost:5000/status/' + message_id })
        else:
            return jsonify({ 'error' : 'File extension not allowed.'})

@app.route('/status', methods=['GET'])
def check_status():
    return ''



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
# @app.route('/uploads/<filename>')
# def uploaded_file(filename):
#     return send_from_directory(app.config['UPLOAD_FOLDER'],
#                                filename)

