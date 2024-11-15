from utils.docling_utils import docling_export, docling_parse

# doc_path = 'test/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1 - page 1.pdf'
doc_path = 'test/MSU 2023 Potato Report - 25-27 pages.pdf'
document, conv_res = docling_parse(doc_path)  # , force_parse=True)
elements, tables, images = docling_export(doc_path)

doc_path = 'test/MSU 2023 Potato Report - 10 pages.pdf'
document, conv_res = docling_parse(doc_path)  # , force_parse=True)
elements, tables, images = docling_export(doc_path)

doc_path = 'test/MSU 2023 Potato Report - 15-24 pages.pdf'
document, conv_res = docling_parse(doc_path)  # , force_parse=True)
elements, tables, images = docling_export(doc_path)