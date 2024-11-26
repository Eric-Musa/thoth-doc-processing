## use docling to ingest documents in data/ingest and output to data/processed

import os
from docling.document_converter import DocumentConverter
from tqdm import tqdm
import json

# Set up the paths
ingest_path = 'data/ingest'
converted_path = 'data/converted'

# Get the list of files in the ingest directory
files = os.listdir(ingest_path)

converter = DocumentConverter()

def write_json(doc, output_path, assembled_only=False):
    data = json.loads(doc.model_dump_json())

    # Export the processed text as JSON

    data = data['assembled'] if assembled_only else data

    with open(output_path, 'w') as f:
        f.write(json.dumps(data, indent=2))



def write_markdown(doc, output_path):
    with open(output_path, 'w') as f:
        f.write(doc.document.export_to_markdown())


from bbox import draw_bounding_boxes_on_pdf, crop_bounding_boxes_to_jpgs
from docling_core.types.doc import DocItemLabel

# Process each file
for file in tqdm(files):
    
    fname = f'{ingest_path}/{file}'
    # Process the text
    result = converter.convert(fname)
    document = result.document
    
    write_json(result, f'{converted_path}/{file}.json')
    write_markdown(result, f'{converted_path}/{file}.md')

    bboxes = []
    for element in result.assembled.elements:
        if element.label in [DocItemLabel.PICTURE, DocItemLabel.TABLE]:
            bbox = (
                element.cluster.bbox.l,
                element.cluster.bbox.t,
                element.cluster.bbox.r,
                element.cluster.bbox.b,
            )
            bboxes.append((element.page_no, bbox, element.label))
    
    draw_bounding_boxes_on_pdf(fname, f'{converted_path}/{file}_bbox.pdf', bboxes, convert_tl_to_bl=True)
    crop_bounding_boxes_to_jpgs(fname, f'{converted_path}/{file.replace('.pdf', '')}', bboxes, convert_tl_to_bl=True)
    
        
    
