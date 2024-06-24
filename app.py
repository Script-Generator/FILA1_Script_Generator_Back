from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from ftplib import FTP

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

FTP_HOST = ""
FTP_USER = ""
FTP_PASS = ""

def upload_to_ftp(local_filepath, remote_filename):
    try:
        ftp = FTP(FTP_HOST)
        ftp.login(FTP_USER, FTP_PASS)
        with open(local_filepath, 'rb') as file:
            ftp.storbinary(f'STOR {remote_filename}', file)
        ftp.quit()
        print(f'Successfully uploaded {local_filepath} to {remote_filename}')
    except Exception as e:
        print(f'Error uploading {local_filepath} to FTP: {e}')
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

        upload_to_ftp(local_filepath, file.filename)

        return jsonify({"message": "File successfully uploaded and transferred"}), 200
    except Exception as e:
        print(f'Internal Server Error: {e}')
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
