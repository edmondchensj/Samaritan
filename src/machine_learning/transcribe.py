from __future__ import print_function
import time
import boto3

def transcribe(filename, extension, bucket, verbose=False):
    if verbose:
        t = time.time()
        print('\nStarting AWS Transcribe service ...')

    transcribe = boto3.client('transcribe')
    job_name = filename + '-transcription'
    job_uri = f"https://s3-ap-southeast-1.amazonaws.com/{bucket}/{filename}.{extension}"

    # Clear job with same name to avoid conflicts
    try:
        transcribe.delete_transcription_job(
            TranscriptionJobName=job_name
        )
        if verbose:
            print('Requested job name existed and deleted. Continuing ...')
    except:
        if verbose:
            print('No duplicate jobs found. Continuing ...')

    # Start job
    transcribe.start_transcription_job(
       TranscriptionJobName=job_name,     Media={'MediaFileUri': job_uri},
       MediaFormat=extension,
       LanguageCode='en-US', OutputBucketName=bucket
    )

    # Wait to finish
    while True:
       status = transcribe.get_transcription_job(TranscriptionJobName=job_name)
       if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
           break

    if status == 'FAILED':
        raise SystemExit('Transcription failed. Exiting ...')
    else:
        if verbose:
            print(f'AWS Transcribe service completed in {time.time()-t:.2f}s.')

    return status['TranscriptionJob']['TranscriptionJobStatus']
