import json
import os
import time
from pathlib import Path
from tqdm import tqdm
from typing import Union, Optional, Tuple, Dict
from PIL import Image
import pandas as pd
from docling_core.types.doc.document import DoclingDocument
from docling_core.types.doc import ImageRefMode, PictureItem, TableItem
from docling.datamodel.document import ConversionResult, InputDocument, _DocumentConversionInput
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, _format_to_default_options


def _read_json(json_path: Union[str, Path]) -> dict:
    # assert os.path.exists(json_path), f"Document JSON file not found: {json_path}"
    # assert json_path.endswith('.json'), f"Document JSON file must be .json: {json_path}"
    with open(json_path, 'r') as f:
        return json.load(f)


def load_document(document_json_path: Union[str, Path, dict]) -> DoclingDocument:
    if isinstance(document_json_path, (str, Path)):
        json_data = _read_json(document_json_path)
    elif isinstance(document_json_path, dict):
        json_data = document_json_path
    else:
        raise ValueError(f"Invalid document_json_path: {document_json_path} - must be file path or JSON dict")
    return DoclingDocument(**json_data)


def load_conversion_result(conversion_result_json_path: Union[str, Path, dict]) -> ConversionResult:
    if isinstance(conversion_result_json_path, (str, Path)):
        json_data = _read_json(conversion_result_json_path)
    elif isinstance(conversion_result_json_path, dict):
        json_data = conversion_result_json_path
    else:
        raise ValueError(f"Invalid conversion_result_json_path: {conversion_result_json_path} - must be file path str or JSON dict")
    # return ConversionResult(**json_data)

    ## Cannot instantiate InputDocument from existing data
    ## Needs to be created from _DocumentConversionInput

    # 1. get source(s) from json_data
    sources = [json_data['input']['file']]  # input must be iterable, wrap single element in list

    # 2. create _DocumentConversionInput from source(s)
    doc_conv_in = _DocumentConversionInput(path_or_stream_iterator=sources)

    # 3. generate InputDocument iterable from _DocumentConversionInput.docs()
    #    using default format options
    conv_input = list(doc_conv_in.docs(_format_to_default_options))
    assert len(conv_input) == 1, f"Expected 1 document, got {len(conv_input)}"
    in_doc = conv_input[0]

    # 4. update json_data with InputDocument, overwriting existing 'input' key
    json_data['input'] = in_doc
    
    return ConversionResult(**json_data)


IMAGE_RESOLUTION_SCALE = 2.0
def docling_parse(document_path: Union[str, Path], output_dir: Optional[str]=None, force_parse: bool=False) -> ConversionResult:
    start_time = time.time()

    document_path = Path(document_path)
    output_dir = Path(output_dir or document_path.with_suffix(''))
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    document_json_path = output_dir / 'document.json'
    # if full_output_json_path.exists():
        # conv_res = load_conversion_result(full_output_json_path)
    if not document_json_path.exists() or force_parse:
        
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
        conv_res = doc_converter.convert(document_path)
        full_output_json_path = output_dir / 'conversion_result.json'
        with open(full_output_json_path, 'w') as f:
            f.write(conv_res.model_dump_json())

        document = conv_res.document
        with open(document_json_path, 'w') as f:
            f.write(document.model_dump_json())
    else:
        document = load_document(document_json_path)
        conv_res = None
    
    end_time = time.time() - start_time
    # print(f"Document converted and ConversionResult exported to JSON in {end_time:.2f} seconds.")
    print(f"Document converted and DoclingDocument exported to JSON in {end_time:.2f} seconds.")
    # return conv_res
    return document, conv_res


import mdpd 
def _extract_table(table: TableItem, document: DoclingDocument) -> Tuple[Image.Image, pd.DataFrame, str, str, str]:
    table_image = table.image.pil_image
    table_md = table.export_to_markdown()
    table_df = mdpd.from_md(table_md)
    table_caption = table.caption_text(document)
    table_md_formatted = f"## {table_caption}\n\n---\n\n{table_md}\n"
    return table_image, table_df, table_md_formatted, table_md, table_caption


def _extract_picture(picture: PictureItem, document: Optional[DoclingDocument]=None) -> Image.Image:
    picture_image = picture.image.pil_image
    return picture_image
    

def docling_export(document_path: Union[str, Path], output_dir: Optional[str] = None) -> Tuple[Dict[str, list], list, list]:
    document_path = Path(document_path)
    output_dir = output_dir or document_path.with_suffix('')
    document, _ = docling_parse(document_path, output_dir)
    doc_filename = document_path.stem

    start_time = time.time()

    # Save images of figures and tables
    elements = {}
    texts = []
    tables = []
    images = []
    # for i, (element, _level) in enumerate(conv_res.document.iterate_items()):
    for i, (element, _level) in enumerate(document.iterate_items()):
        print(i, element.label)
        if element.label not in elements:
            elements[element.label] = [element]
        else:
            elements[element.label].append(element)
        
        if isinstance(element, TableItem):
            # table_image, table_df, table_md_formatted, table_md, table_caption = _extract_table(element, conv_res.document)
            table_image, table_df, table_md_formatted, table_md, table_caption = _extract_table(element, document)
            # table_counter += 1

            element_image_filename = os.path.join(output_dir, f"table-{len(elements[element.label])}.png")
            with open(element_image_filename, "wb") as fp:
                table_image.save(fp, "PNG")

            element_md_filename = os.path.join(output_dir, f"table-{len(elements[element.label])}.md")
            with open(element_md_filename, "w") as fp:
                fp.write(table_md_formatted)
            
            tables.append(table_df)

        if isinstance(element, PictureItem):
            # picture_counter += 1
            picture_image = _extract_picture(element)
            element_image_filename = os.path.join(output_dir, f"picture-{len(elements[element.label])}.png")
            with open(element_image_filename, "wb") as fp:
                picture_image.save(fp, "PNG")
            
            images.append(picture_image)
        

    # Save markdown with embedded pictures
    # content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    content_md = document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    md_filename = os.path.join(output_dir, f"{doc_filename}-with-images.md")
    with open(md_filename, "w") as fp:
        fp.write(content_md)

    # Save markdown without embedded pictures
    # content_md_no_embed = conv_res.document.export_to_markdown()
    content_md_no_embed = document.export_to_markdown()
    md_filename_no_embed = os.path.join(output_dir, f"{doc_filename}.md")
    with open(md_filename_no_embed, "w") as fp:
        fp.write(content_md_no_embed)

    end_time = time.time() - start_time

    print(f"Document converted and figures exported in {end_time:.2f} seconds.")
    for label, elements_list in elements.items():
        print(f"{label}: {len(elements_list)}")
    return elements, tables, images
