## use docling to ingest documents in data/ingest and output to data/processed

import os
from docling.document_converter import DocumentConverter
from tqdm import tqdm
import json

# Set up the paths
ingest_path = 'data/ingest'
processed_path = 'data/processed'

# Get the list of files in the ingest directory
files = os.listdir(ingest_path)

converter = DocumentConverter()

def write_json(doc, output_path):
    data = json.loads(doc.model_dump_json())

    # Export the processed text as JSON
    with open(output_path, 'w') as f:
        f.write(json.dumps(data, indent=2))


def write_markdown(doc, output_path):
    with open(output_path, 'w') as f:
        f.write(doc.document.export_to_markdown())


# Process each file
for file in tqdm(files):
    
    # Process the text
    result = converter.convert(f'{ingest_path}/{file}')
    result.document.export_to_markdown()
    write_json(result, f'{processed_path}/{file}.json')
    write_markdown(result, f'{processed_path}/{file}.md')

    
