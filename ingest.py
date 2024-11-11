import logging
import time
from pathlib import Path

from docling_core.types.doc import ImageRefMode, PictureItem, TableItem

from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

IMAGE_RESOLUTION_SCALE = 2.0

import os
from tqdm import tqdm
import json

# Set up the paths
ingest_path = 'data/ingest'
converted_path = 'data/converted'

# Get the list of files in the ingest directory
files = os.listdir(ingest_path)

for file in tqdm(files):
    
    # Important: For operating with page images, we must keep them, otherwise the DocumentConverter
    # will destroy them for cleaning up memory.
    # This is done by setting PdfPipelineOptions.images_scale, which also defines the scale of images.
    # scale=1 correspond of a standard 72 DPI image
    # The PdfPipelineOptions.generate_* are the selectors for the document elements which will be enriched
    # with the image field
    pipeline_options = PdfPipelineOptions()
    pipeline_options.images_scale = IMAGE_RESOLUTION_SCALE
    pipeline_options.generate_page_images = True
    pipeline_options.generate_table_images = True
    pipeline_options.generate_picture_images = True

    doc_converter = DocumentConverter(
        format_options={
            InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
        }
    )

    start_time = time.time()

    conv_res = conv_res or doc_converter.convert(os.path.join(ingest_path, file))
    output_dir = os.path.join(converted_path, file.replace('.pdf', ''))
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    doc_filename = conv_res.input.file.stem

    # # Save page images
    # for page_no, page in conv_res.document.pages.items():
    #     page_no = page.page_no
    #     page_image_filename = os.path.join(output_dir, f"{doc_filename}-{page_no}.png")
    #     with open(page_image_filename, "wb") as fp:
    #         page.image.pil_image.save(fp, format="PNG")

    # Save images of figures and tables
    table_counter = 0
    picture_counter = 0
    for i, (element, _level) in enumerate(conv_res.document.iterate_items()):
        print(i, element.label)
        if isinstance(element, TableItem):
            table_counter += 1
            element_image_filename = (
                os.path.join(output_dir, f"table-{table_counter}.png")
            )
            with open(element_image_filename, "wb") as fp:
                element.image.pil_image.save(fp, "PNG")

            element_md_filename = (
                os.path.join(output_dir, f"table-{table_counter}.md")
            )
            with open(element_md_filename, "w") as fp:
                fp.write(f"## {element.caption_text(conv_res.document)}\n\n---\n\n{element.export_to_markdown()}\n")

        if isinstance(element, PictureItem):
            picture_counter += 1
            element_image_filename = (
                os.path.join(output_dir, f"picture-{picture_counter}.png")
            )
            with open(element_image_filename, "wb") as fp:
                element.image.pil_image.save(fp, "PNG")

    # Save markdown with embedded pictures
    content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    md_filename = os.path.join(output_dir, f"{doc_filename}-with-images.md")
    with open(md_filename, "w") as fp:
        fp.write(content_md)

    content_md_no_embed = conv_res.document.export_to_markdown()
    md_filename_no_embed = os.path.join(output_dir, f"{doc_filename}.md")
    with open(md_filename_no_embed, "w") as fp:
        fp.write(content_md_no_embed)

    end_time = time.time() - start_time

    print(f"Document converted and figures exported in {end_time:.2f} seconds.")

