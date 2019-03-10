import os
import boto3
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename

BUCKET_NAME = 'aws-hackdays-samaritan-uploads'
UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = set(['wav'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@app.route('/')
def hello():
    return 'Hello, World!'


@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
  if request.method == 'POST':
    # check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part')
      return redirect(request.url)
    file = request.files['file']
    # if user does not select file, browser also
    # submit a empty part without filename
    if file.filename == '':
      flash('No selected file')
      return redirect(request.url)
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)

      full_filename = os.path.join(app.config['UPLOAD_FOLDER'], filename)
      file.save(full_filename)

      s3 = boto3.resource('s3')
      data = open(full_filename, 'rb')
      s3.Bucket(BUCKET_NAME).put_object(Key=filename, Body=data)

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

