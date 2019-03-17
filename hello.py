import os
import time
import boto3

from flask import Flask, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename

BUCKET_NAME = 'aws-hackdays-samaritan-uploads'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

CORS(app)


def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # check if the post request has the file part
    print('here')
    if 'file' not in request.files:
      # flash('No file part')
      print('here2')
      return redirect(request.url)
    file = request.files['file']
    print('here3')
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
      print('here4')
      # flash('No selected file')
      return redirect(request.url)
    print('here5')
    if file and allowed_file(file.filename):
      print('here6')
      filename = secure_filename(file.filename)

      full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(full_filename)

      s3 = boto3.resource('s3')
      data = open(full_filename, 'rb')
      s3.Bucket(BUCKET_NAME).put_object(Key=filename, Body=data)
      print('here7')

      return f'File {file.filename} uploaded!'
  return '''
  <!doctype html>
  <title>Upload new File</title>
  <h1>Upload new File</h1>
  <form method=post enctype=multipart/form-data>
    <p><input type=file name=file>
       <input type=submit value=Upload>
  </form>
  '''


# @app.route('/transcribe', methods=['GET'])
# def transcribe_file():
#   transcribe = boto3.client('transcribe')






