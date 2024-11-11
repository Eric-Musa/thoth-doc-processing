# thoth-doc-processing


### TODO:
- stitch incomplet columns/clusters together
  - if last element on page is "incomplete" --> check delimiter
  - if first element on next page starts in the middle --> ? start with capital? LLM?
    - compare to other similar items
- when element (table, image) referenced, substitute in element's caption 
- feed table image + table markdown to vision model to revise markdown
- narrative analysis of long document
  - running "context" of what's important to move forward with --> LSTM in prompt engineering lol