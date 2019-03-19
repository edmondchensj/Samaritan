# Samaritan: Voice-controlled Assistant for Endoscopy Surgeons (Backend)

## Overview
The Samaritan Endoscopy Backend works with the [Samaritan UI](https://github.com/TimothySeahGit/samaritan-ui) for use in endoscopic clinical settings. It allows endoscopists to capture screenshots during an endoscopic examination as per their normal workflow, but optionally add on voice recorded notes. The recordings are immediately sent to Amazon Transcribe and Amazon Comprehend Medical for transcription and keyword extraction. The Samaritan UI then generates suitable captions for the screenshots. It is able to detect organ sites, medical conditions, and negation.
