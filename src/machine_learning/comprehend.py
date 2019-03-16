from __future__ import print_function
import time
import boto3
import argparse
import json
from pprint import pprint
from utils import get_transcription

def _fix_vocab(transcript):
    vocab_bank = {"kaleidoscope": "colonoscope", "Kaleidoscope.": "colonoscope",
              "kalanick": "colonic", "Kalanick": "colonic",
              "seaCome": "cecum", "sea. Come": "cecum", "sick, um": "cecum",
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
    comprehend = boto3.client('comprehendmedical', 
                            region_name='us-east-2')
    results = comprehend.detect_entities(Text=transcript)
    organ, keywords = _parse_comprehend_results(results)

    output = {
            'detected_organ_site': organ, 
            'keywords':keywords,
            'transcript': transcript
            }
            
    if save_output_locally:
        with open(filename + '-output.json', 'w') as f:
            json.dump(output, f)

    if verbose:
        print(f'AWS Comprehend Medical service completed in {time.time()-t:.2f}s. Output:')
        pprint(output)

    return output