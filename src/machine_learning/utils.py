from __future__ import print_function
import time
import boto3
import argparse
import json 

def get_transcription(filename, bucket, verbose, 
            delete_original_JSON=False, save_transcript_locally=False):
    '''Fetch the output JSON of Amazon Transcribe from S3 bucket and return transcript as string. 
    Then optionally delete the original JSON file on bucket.'''  
    if verbose: 
        t = time.time()
        print('\nFetching AWS Transcribe output from S3 bucket ... ')

    # Fetch JSON output of Amazon Transcribe 
    s3 = boto3.client('s3')
    obj = s3.get_object(Bucket=bucket, Key=filename + '-transcription.json')

    # Decode JSON to get transcript text 
    content = obj['Body'].read().decode('utf-8')
    json_content = json.loads(content)
    transcript = json_content['results']['transcripts'][0]['transcript']

    # Option to delete original JSON file
    if delete_original_JSON:
        s3.delete_object(Bucket=bucket, key=filename + '-transcription.json')

    # Option to save transcript locally
    if save_transcript_locally:
        with open(filename+'-transcription.txt', 'w') as f:
            f.write(transcript)

    if verbose:
        print(f'Transcription fetched in {time.time()-t:.2f}s.')
    return transcript

def upload_to_S3(output, filename, extension, bucket, verbose):
    if verbose:
        t = time.time()
        print('\nUploading to S3 ...')
    
    # Convert output dict to JSON object
    json_obj = json.dumps(output).encode('utf-8')

    # Upload to S3
    s3 = boto3.client('s3')
    s3.put_object(
        Body=json_obj, 
        Bucket=bucket, 
        Key=filename + '.' + extension)

    if verbose:
        print(f'Object uploaded to S3 in {time.time()-t:.2f}s.')
