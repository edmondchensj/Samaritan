from __future__ import print_function
import time
import boto3
import argparse
import json
from pprint import pprint

from transcribe import transcribe
from comprehend import parse_transcription
from utils import get_transcription, upload_to_S3

def run_machine_learning(filename, bucket, save_output_to_S3=True, verbose=True):
    '''Run AWS machine learning services (Transcribe & Comprehend) on a given audiofile.

    Required arguments
    ==========
    filename -- S3 key for audiofile excluding .wav extension
    bucket -- S3 bucket containing the audiofile (region assumed to be ap-southeast-1)
    
    Optional arguments
    ==========
    save_output_to_s3 -- set True to upload output dictionary to S3 as a JSON file.
    verbose -- set True to display information in terminal

    Output
    ==========
    JSON object / Python dictionary with the following attributes
        'detected_organ_site': list
        'keywords': list
        'transcript': string
    '''

    transcribe(filename, 'wav', bucket, verbose)

    transcript = get_transcription(filename, bucket, verbose)

    output = parse_transcription(transcript, filename, verbose)

    if save_output_to_S3:
        upload_to_S3(output, filename, 'json', bucket, verbose)
    
    return output

def main():
    # Settings
    filename = 'removing_large_polyps' # sample audiofile
    bucket = 'team-arpc'

    output = run_machine_learning(filename, bucket)

if __name__ == '__main__':
    main()
