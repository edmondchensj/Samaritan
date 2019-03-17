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
  return jsonify(results=status)






def _fix_vocab(transcript):
  vocab_bank = {
    "kaleidoscope": "colonoscope",
    "Kaleidoscope.": "colonoscope",
    "kalanick": "colonic",
    "Kalanick": "colonic",
    "seaCome": "cecum",
    "sea. Come": "cecum",
    "sick,um": "cecum",
    "A sending": "ascending",
    "Elio sequel": "ileocecal",
    "Virg": "verge",
    "ilium": "ileum"}

  for original, new in vocab_bank.items():
    transcript = transcript.replace(original, new)
  return transcript

def _parse_comprehend_results(results):
  # Use sets to avoid duplicates
  organ = set()
  keywords = set()

  # Get results
  for entity in results['Entities']:
    if entity['Type'] == 'SYSTEM_ORGAN_SITE':
      organ.add(entity['Text'])

    keywords.add(entity['Text'])

  return list(organ), list(keywords)

def parse_transcription(transcript, filename, verbose=False, save_output_locally=False):
  if verbose:
    t = time.time()
    print('\nStarting AWS Comprehend Medical service ... ')

  # Fix common vocab errors
  transcript = _fix_vocab(transcript)

  # Use AWS Comprehend features
  # NOTE: AWS Comprehend is NOT available in Southeast Asia region. We set region to US.
  comprehend = boto3.client('comprehendmedical', region_name='us-east-2')
  results = comprehend.detect_entities(Text=transcript)
  organ, keywords = _parse_comprehend_results(results)

  output = {
    'detected_organ_site': organ,
    'keywords': keywords,
    'transcript': transcript}

  if save_output_locally:
    with open(filename + '-output.json', 'w') as f:
      json.dump(output, f)

  if verbose:
    print(f'AWS Comprehend Medical service completed in {time.time()-t:.2f}s. Output:')
    pprint(output)

  return output

@app.route('/comprehend', methods=['GET'])
def comprehend():
  filename = request.args.get('filename')
  print(f'Requesting comprehension for {filename} ..')

  s3 = boto3.client('s3')
  obj = s3.get_object(Bucket=BUCKET_NAME, Key=filename)
  transcribed_obj = obj['Body'].read().decode('utf-8')
  transcript = transcribed_obj['results']['transcripts'][0]['transcript']
  print(transcript)

  j = json.loads(transcribed_obj)
  return jsonify(results=j)

  # s3 = boto3.resource('s3')
  # response = s3.Bucket(BUCKET_NAME).get_object(Key=filename)
  # return jsonify(results=response)
  # parse_transcription()












