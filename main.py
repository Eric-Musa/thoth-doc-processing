from utils.docling_utils import docling_export, docling_parse
from docling_core.types.doc.document import DocItem

# doc_path = 'data/ingest/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1.pdf'
# output_dir = 'data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1'

doc_path = 'test/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1.pdf'
output_dir = 'data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1'

# output_dir = '.'
# doc_path = 'test/MSU 2023 Potato Report - 25-27 pages.pdf'

document, conv_res = docling_parse(doc_path, output_dir, verbose=True)
# document2, conv_res2 = docling_parse(doc_path, output_dir, verbose=True, force_parse=True)
# assert document == document2

from utils.docling_utils import ModifiedExportDocument


def add_attribution(text: str, item: DocItem, ix: int) -> str:
    return \
f"""
### {item.self_ref} - {str(item.label)} - {ix}
```
{text}
```
---
"""
    

med = ModifiedExportDocument(**document.export_to_dict())

attributed_md = med.export_to_markdown(postprocess=add_attribution)
with open('test_attr.md', 'w') as f:
    f.write(attributed_md)

# document, conv_res = docling_parse(doc_path, output_dir, verbose=True)
# elements, tables, images = docling_export(doc_path, output_dir)  # , origin_in_md=True)  # , verbose=True)


# html_doc = document.export_to_html()



# def add_attribution(text: str, item: DocItem, ix: int) -> str:
#     return (
#         f"```{item.self_ref}: {str(item.label)}"
#         f"{text}"
#         "```"
#     )

# attributed_md = document.export_to_markdown(
#     # postprocess_text=add_attribution
# )
# with open('test_attr.md', 'w') as f:
#     f.write(attributed_md)

# # document.export_to_markdown()
# # page_elements: dict[int, list] = {}

# import re

# # page_elements = {}
# # for element, _level in document.iterate_items():
# #     if len(element.prov) == 1:
# #         page_number = element.prov[0].page_no
# #     elif len(element.prov) > 1:
# #         page_number = element.prov[0].page_no
# #         for prov in element.prov:
# #             if prov.page_no != page_number:
# #                 print(f'Different page numbers in prov, {page_number}, {prov.page_no}')
# #     else:
# #         location_str = element.get_location_tokens(document, '')
# #         page_number_str = re.search(r'<page_(\d+)>', location_str).group(1)
# #         page_number = int(page_number_str)
# #         # print(page_number)
# #     if page_number not in page_elements:
# #         page_elements[page_number] = [element]
# #     else:
# #         page_elements[page_number].append(element)

# # for page_number, elements in page_elements.items():
# #     print(page_number, len(elements))

# # doc_path = 'test/MSU 2023 Potato Report - 10 pages.pdf'
# # document, conv_res = docling_parse(doc_path)  # , force_parse=True)
# # elements, tables, images = docling_export(doc_path)

# # doc_path = 'test/MSU 2023 Potato Report - 15-24 pages.pdf'
# # document, conv_res = docling_parse(doc_path)  # , force_parse=True)
# # elements, tables, images = docling_export(doc_path)


# # from utils.docling_utils import docling_export, docling_parse

# # # doc_path = 'test/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1.pdf'
# # doc_path = 'test/Pdf scans rotated.pdf'
# # document, conv_res = docling_parse(doc_path, force_parse=True, verbose=True)
# # # elements, tables, images = docling_export(doc_path)

# # document2, conv_res2 = docling_parse(doc_path, force_parse=False, verbose=True)
# # print(conv_res == conv_res2)
# # print(document == document2)

# # # import json
# # # cr2_data = json.loads(conv_res2.model_dump_json())
# # # with open('test/conv_res2.json', 'w') as f:
# # #     json.dump(cr2_data, f, indent=4)


# # # ## write the .pages attribute of both conversion results to json
# # # with open('test/pages1.json', 'w') as f:
# # #     json.dump(conv_res.pages, f, indent=4)

# # # with open('test/pages2.json', 'w') as f:
# # #     json.dump(conv_res2.pages, f, indent=4)