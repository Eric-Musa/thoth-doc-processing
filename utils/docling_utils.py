import json
import mdpd 
import os
import pandas as pd
import re
import sys
import time
from docling_core.types.doc.document import *
from docling.datamodel.document import ConversionResult, InputDocument, _DocumentConversionInput
from docling.datamodel.base_models import FigureElement, InputFormat, Table
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption, _format_to_default_options
from pathlib import Path
from PIL import Image
from typing import Union, Optional, Tuple, Dict, Callable

IMAGE_RESOLUTION_SCALE = 2.0


def docling_parse(document_path: Union[str, Path], output_dir: Optional[str]=None, force_parse: bool=False, verbose: bool=False) -> tuple[DoclingDocument, ConversionResult]:
    start_time = time.time()

    document_path = Path(document_path)
    output_dir = Path(output_dir or document_path.with_suffix(''))
    if not output_dir.exists():
        output_dir.mkdir(parents=True)
    
    document_json_path = output_dir / 'document.json'
    full_output_json_path = output_dir / 'conversion_result.json'
    
    
    if not document_json_path.exists() or force_parse:
        if verbose: print(f"Converting document: {document_path}")
        
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
        with open(full_output_json_path, 'w') as f:
            f.write(conv_res.model_dump_json())

        document = conv_res.document
        document.save_to_json_file(document_json_path)
        # with open(document_json_path, 'w') as f:
        #     f.write(document.model_dump_json(indent=4))

        end_time = time.time() - start_time
        if verbose: print(f"Document converted and DoclingDocument exported to JSON in {end_time:.2f} seconds.")
    else:
        if verbose: print(f"Loading document from JSON: {document_json_path}")

        conv_res = None  # load_conversion_result(full_output_json_path)
        document = DoclingDocument.load_from_json_file(document_json_path)
        # with open(document_json_path, 'r') as f:
        #     document = DoclingDocument(**json.load(f))
    
    return document, conv_res


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
    

def docling_export(document_path: Union[str, Path], output_dir: Optional[str] = None, origin_in_md: bool = False) -> Tuple[Dict[str, list], list, list]:
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
            if not os.path.exists(element_image_filename):
                with open(element_image_filename, "wb") as fp:
                    table_image.save(fp, "PNG")

            element_md_filename = os.path.join(output_dir, f"table-{len(elements[element.label])}.md")
            if not os.path.exists(element_md_filename):
                with open(element_md_filename, "w") as fp:
                    fp.write(table_md_formatted)
            
            tables.append(table_df)

        if isinstance(element, PictureItem):
            # picture_counter += 1
            picture_image = _extract_picture(element)
            element_image_filename = os.path.join(output_dir, f"picture-{len(elements[element.label])}.png")
            if not os.path.exists(element_image_filename):
                with open(element_image_filename, "wb") as fp:
                    picture_image.save(fp, "PNG")
            
            images.append(picture_image)
        

    # Save markdown with embedded pictures
    # content_md = conv_res.document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)
    content_md = document.export_to_markdown(image_mode=ImageRefMode.EMBEDDED)  # , origin=origin_in_md)
    # content_md = document.export_to_markdown(image_mode=ImageRefMode.EXPORTED_TO_PNG)  # , image_dir=Path(output_dir) / 'images')  # , origin=origin_in_md)
    md_filename = os.path.join(output_dir, f"{doc_filename}-with-images.md")
    if not os.path.exists(md_filename):
        with open(md_filename, "w") as fp:
            fp.write(content_md)

    # Save markdown without embedded pictures
    # content_md_no_embed = conv_res.document.export_to_markdown()
    content_md_no_embed = document.export_to_markdown()  # origin=origin_in_md)
    md_filename_no_embed = os.path.join(output_dir, f"{doc_filename}.md")
    if not os.path.exists(md_filename_no_embed):
        with open(md_filename_no_embed, "w") as fp:
            fp.write(content_md_no_embed)

    end_time = time.time() - start_time

    print(f"Document converted and figures exported in {end_time:.2f} seconds.")
    for label, elements_list in elements.items():
        print(f"{label}: {len(elements_list)}")
    return elements, tables, images


class ModifiedExportDocument(DoclingDocument):

    def export_to_markdown(self, delim = "\n", from_element = 0, to_element = sys.maxsize, 
                           labels = DEFAULT_EXPORT_LABELS, strict_text = False, image_placeholder = "<!-- image -->", 
                           image_mode = ImageRefMode.PLACEHOLDER, indent = 4, text_width = -1, page_no = None,
                           postprocess: Optional[Callable[[str, "DoclingDocument", int], str]] = None) -> str:
        mdtexts: list[str] = []
        list_nesting_level = 0  # Track the current list nesting level
        previous_level = 0  # Track the previous item's level
        in_list = False  # Track if we're currently processing list items


        def apply_postprocess(text: str, item: DocItem, index: int):
            if postprocess is not None:
                text = postprocess(text, item, index) if text else text
            mdtexts.append(text)
        

        for ix, (item, level) in enumerate(
            self.iterate_items(self.body, with_groups=True, page_no=page_no)
        ):
            # If we've moved to a lower level, we're exiting one or more groups
            if level < previous_level:
                # Calculate how many levels we've exited
                level_difference = previous_level - level
                # Decrement list_nesting_level for each list group we've exited
                list_nesting_level = max(0, list_nesting_level - level_difference)

            previous_level = level  # Update previous_level for next iteration

            if ix < from_element or to_element <= ix:
                continue  # skip as many items as you want

            # Handle newlines between different types of content
            if (
                len(mdtexts) > 0
                and not isinstance(item, (ListItem, GroupItem))
                and in_list
            ):
                mdtexts[-1] += "\n"
                in_list = False

            if isinstance(item, GroupItem) and item.label in [
                GroupLabel.LIST,
                GroupLabel.ORDERED_LIST,
            ]:

                if list_nesting_level == 0:  # Check if we're on the top level.
                    # In that case a new list starts directly after another list.
                    mdtexts.append("\n")  # Add a blank line

                # Increment list nesting level when entering a new list
                list_nesting_level += 1
                in_list = True
                continue

            elif isinstance(item, GroupItem):
                continue

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.TITLE]:
                in_list = False
                marker = "" if strict_text else "#"
                text = f"{marker} {item.text}"
                # mdtexts.append(text.strip() + "\n")
                apply_postprocess(text.strip() + "\n", item, ix)

            elif (
                isinstance(item, TextItem)
                and item.label in [DocItemLabel.SECTION_HEADER]
            ) or isinstance(item, SectionHeaderItem):
                in_list = False
                marker = ""
                if not strict_text:
                    marker = "#" * level
                    if len(marker) < 2:
                        marker = "##"
                text = f"{marker} {item.text}\n"
                # mdtexts.append(text.strip() + "\n")
                apply_postprocess(text.strip() + "\n", item, ix)

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.CODE]:
                in_list = False
                text = f"```\n{item.text}\n```\n"
                # mdtexts.append(text)
                apply_postprocess(text, item, ix)

            elif isinstance(item, TextItem) and item.label in [DocItemLabel.CAPTION]:
                # captions are printed in picture and table ... skipping for now
                continue

            elif isinstance(item, ListItem) and item.label in [DocItemLabel.LIST_ITEM]:
                in_list = True
                # Calculate indent based on list_nesting_level
                # -1 because level 1 needs no indent
                list_indent = " " * (indent * (list_nesting_level - 1))

                marker = ""
                if strict_text:
                    marker = ""
                elif item.enumerated:
                    marker = item.marker
                else:
                    marker = "-"  # Markdown needs only dash as item marker.

                text = f"{list_indent}{marker} {item.text}"
                # mdtexts.append(text)
                apply_postprocess(text, item, ix)

            elif isinstance(item, TextItem) and item.label in labels:
                in_list = False
                if len(item.text) and text_width > 0:
                    wrapped_text = textwrap.fill(text, width=text_width)
                    # mdtexts.append(wrapped_text + "\n")
                    apply_postprocess(wrapped_text + "\n", item, ix)
                elif len(item.text):
                    text = f"{item.text}\n"
                    # mdtexts.append(text)
                    apply_postprocess(text, item, ix)

            elif isinstance(item, TableItem) and not strict_text:
                in_list = False
                # mdtexts.append(item.caption_text(self))
                apply_postprocess(item.caption_text(self), item, ix)
                md_table = item.export_to_markdown()
                # mdtexts.append("\n" + md_table + "\n")
                apply_postprocess("\n" + md_table + "\n", item, ix)

            elif isinstance(item, PictureItem) and not strict_text:
                in_list = False
                # mdtexts.append(item.caption_text(self))
                apply_postprocess(item.caption_text(self), item, ix)

                if image_mode == ImageRefMode.PLACEHOLDER:
                    # mdtexts.append("\n" + image_placeholder + "\n")
                    apply_postprocess("\n" + image_placeholder + "\n", item, ix)
                elif image_mode == ImageRefMode.EMBEDDED and isinstance(
                    item.image, ImageRef
                ):
                    text = f"![Local Image]({item.image.uri})\n"
                    # mdtexts.append(text)
                    apply_postprocess(text, item, ix)
                elif image_mode == ImageRefMode.EMBEDDED and not isinstance(
                    item.image, ImageRef
                ):
                    text = (
                        "<!-- 🖼️❌ Image not available. "
                        "Please use `PdfPipelineOptions(generate_picture_images=True)`"
                        " --> "
                    )
                    # mdtexts.append(text)
                    apply_postprocess(text, item, ix)

            elif isinstance(item, DocItem) and item.label in labels:
                in_list = False
                text = "<missing-text>"
                # mdtexts.append(text)
                apply_postprocess(text, item, ix)

        mdtext = (delim.join(mdtexts)).strip()
        mdtext = re.sub(
            r"\n\n\n+", "\n\n", mdtext
        )  # remove cases of double or more empty lines.

        # Our export markdown doesn't contain any emphasis styling:
        # Bold, Italic, or Bold-Italic
        # Hence, any underscore that we print into Markdown is coming from document text
        # That means we need to escape it, to properly reflect content in the markdown
        def escape_underscores(text):
            # Replace "_" with "\_" only if it's not already escaped
            escaped_text = re.sub(r"(?<!\\)_", r"\_", text)
            return escaped_text

        mdtext = escape_underscores(mdtext)

        return mdtext
    

if __name__ == "__main__":
    doc = DoclingDocument.load_from_json_file('../../data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1/document.json')
    modded_doc = ModifiedExportDocument(**doc.export_to_dict())

    def dummy_test(text: str, item: DocItem, ix: int) -> str:
        return f"""{ix} """

    print(modded_doc.export_to_markdown(postprocess=dummy_test))