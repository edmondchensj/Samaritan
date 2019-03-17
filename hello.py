import os
import time
import boto3
import json
from flask import jsonify

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


def upload_file_get():
  return '''
  <!doctype html>
  <title>Upload new File</title>
  <h1>Upload new File</h1>
  <form method=post enctype=multipart/form-data>
    <p><input type=file name=file>
       <input type=submit value=Upload>
  </form>
  '''

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'GET':
    return upload_file_get()

  # check if the post request has the file part
  if 'file' not in request.files:
    print('No file in request.files')
    return redirect(request.url)

  file = request.files['file']
  # if user does not select file, browser also submit a empty part without filename
  if file.filename == '':
    print('Empty file name')
    return redirect(request.url)

  print(f'Checking file ({file}) and filename ({file.filename})')
  if file and allowed_file(file.filename):
    filename = secure_filename(file.filename)

    full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(full_filename)

    print(f'Uploading {file.filename} to S3 ..')
    s3 = boto3.resource('s3')
    data = open(full_filename, 'rb')
    s3.Bucket(BUCKET_NAME).put_object(Key=filename, Body=data)
    print('Upload complete!')

    return f'File {file.filename} uploaded!'

  return redirect(request.url)




@app.route('/transcribe', methods=['GET'])
def transcribe_file():
  filename = request.args.get('filename')
  print(f'Transcribing {filename} ..')

  job_name = f'transcribe_job_{filename}'
  job_uri = f'https://s3-ap-southeast-1.amazonaws.com/{BUCKET_NAME}/{filename}'

  transcribe = boto3.client('transcribe', region_name='ap-southeast-1')
  transcribe.start_transcription_job(
    TranscriptionJobName=job_name,
    Media={'MediaFileUri': job_uri},
    MediaFormat='wav',
    LanguageCode='en-US',
    OutputBucketName=BUCKET_NAME
  )

  return f'File {filename} transcription in progress!'


@app.route('/transcribe/progress', methods=['GET'])
def transcribe_progress():
  filename = request.args.get('filename')
  print(f'Checking transcription progress for {filename} ..')
  job_name = f'transcribe_job_{filename}'

  transcribe = boto3.client('transcribe', region_name='ap-southeast-1')
  status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
  print(status['TranscriptionJob']['TranscriptionJobStatus'])
  # return json.dumps(status)
  return jsonify(results=status)







