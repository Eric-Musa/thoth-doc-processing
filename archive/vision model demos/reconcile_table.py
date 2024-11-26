import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor

# model_id = "/Users/ericmusa/Documents/Projects/GenAI/models/Llama-3.2-11B-Vision-Instruct-Q8_gguf"
model_id = "/Users/ericmusa/Documents/Projects/GenAI/models/Llama-3.2-11B-Vision-Instruct"
# model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)


# image = Image.open('data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1/picture-5.png')
# image = Image.open('data/ingest/Fall red leaves pathway.jpeg')
# image = Image.open('data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1/picture-6.png')
# image = Image.open('data/converted/A review of the global climate change impacts, adaptation, and sustainable mitigation measures/table-1.png')
image = Image.open('test/MSU 2023 Potato Report - 25-27 pages/table-1.png')

with open('test/MSU 2023 Potato Report - 25-27 pages/table-1.md', 'r') as f:
    table_md = f.read()

prompt = f'''
A table is shown in the image above. A cursory table processing has been performed and a first-pass at a Markdown conversion of the table is presented below:
```markdown
{table_md}
```

Please do your best to revise the table for accuracy and clarity.'''

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        # {"type": "text", "text": "Please describe this image with dramatic, flowery poetic language."},
        # {"type": "text", "text": "Please summarize this image."},
        # {"type": "text", "text": "Give a minimal filename (.jpeg) for this image."},
        {"type": "text", "text": prompt},
        # {"type": "text", "text": "How many floods occured in 2018?"},
    ]}
]
input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(image, input_text, return_tensors="pt").to(model.device)

output = model.generate(**inputs, max_new_tokens=2000)
# output = model.generate(**inputs, max_new_tokens=25)
print(processor.decode(output[0]))