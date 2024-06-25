from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import zipfile
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


def unzip_file(local_filepath, extract_to):
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)
    with zipfile.ZipFile(local_filepath, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    print(f'Unzipped {local_filepath} to {extract_to}')


def upload_directory_to_ssh(local_directory, remote_directory):
    try:
        transport = paramiko.Transport((SSH_HOST, SSH_PORT))
        transport.connect(username=SSH_USER, password=SSH_PASS)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # Create remote directory if it does not exist
        try:
            sftp.stat(remote_directory)
        except FileNotFoundError:
            sftp.mkdir(remote_directory)

        for root, dirs, files in os.walk(local_directory):
            for dirname in dirs:
                local_path = os.path.join(root, dirname)
                relative_path = os.path.relpath(local_path, local_directory)
                remote_path = os.path.join(remote_directory, relative_path)
                try:
                    sftp.stat(remote_path)
                except FileNotFoundError:
                    sftp.mkdir(remote_path)

            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, local_directory)
                remote_path = os.path.join(remote_directory, relative_path)
                sftp.put(local_path, remote_path)
                print(f'Successfully uploaded {local_path} to {remote_path}')

        sftp.close()
        transport.close()
    except Exception as e:
        print(f'Error uploading directory {local_directory} via SSH: {e}')
        raise


@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files or 'serverPath' not in request.form:
            return jsonify({"error": "No file or server path in the request"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        server_path = request.form['serverPath']
        local_filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(local_filepath)
        print(f'File saved to {local_filepath}')

        extract_to = os.path.join(UPLOAD_FOLDER, os.path.splitext(file.filename)[0])
        unzip_file(local_filepath, extract_to)

        upload_directory_to_ssh(extract_to, server_path)

        return jsonify({"message": "File successfully uploaded, unzipped and transferred"}), 200
    except Exception as e:
        print(f'Internal Server Error: {e}')
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
