from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

SSH_HOST = os.getenv('SSH_HOST')
SSH_PORT = int(os.getenv('SSH_PORT', 22))
SSH_USER = os.getenv('SSH_USER')
SSH_PASS = os.getenv('SSH_PASS')
REMOTE_PATH = os.getenv('REMOTE_PATH')


def upload_to_ssh(local_filepath, remote_filepath):
    try:
        transport = paramiko.Transport((SSH_HOST, SSH_PORT))
        transport.connect(username=SSH_USER, password=SSH_PASS)

        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(local_filepath, remote_filepath)

        sftp.close()
        transport.close()

        print(f'Successfully uploaded {local_filepath} to {remote_filepath}')
    except Exception as e:
        print(f'Error uploading {local_filepath} via SSH: {e}')
        raise


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        local_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(local_filepath)
        print(f'File saved to {local_filepath}')

        remote_filepath = os.path.join(REMOTE_PATH, file.filename)

        upload_to_ssh(local_filepath, remote_filepath)

        return jsonify({"message": "File successfully uploaded and transferred"}), 200
    except Exception as e:
        print(f'Internal Server Error: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
