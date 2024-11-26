import requests
import torch
from PIL import Image
from transformers import MllamaForConditionalGeneration, AutoProcessor

model_id = "/Users/ericmusa/Documents/Projects/GenAI/models/Llama-3.2-11B-Vision-Instruct"
# model_id = "meta-llama/Llama-3.2-11B-Vision-Instruct"

model = MllamaForConditionalGeneration.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,
    device_map="auto",
)
processor = AutoProcessor.from_pretrained(model_id)


# image = Image.open('data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1/picture-5.png')
image = Image.open('/Users/ericmusa/Documents/Projects/thoth-doc-processing/data/ingest/Fall red leaves pathway.jpeg')
# image = Image.open('/Users/ericmusa/Documents/Projects/thoth-doc-processing/data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1/picture-6.png')
# image = Image.open('/Users/ericmusa/Documents/Projects/thoth-doc-processing/data/converted/A review of the global climate change impacts, adaptation, and sustainable mitigation measures/table-1.png')

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        # {"type": "text", "text": "Please describe this image with dramatic, flowery poetic language."},
        # {"type": "text", "text": "Please summarize this image."},
        {"type": "text", "text": "Give a minimal filename (.jpeg) for this image."},
        # {"type": "text", "text": "How many floods occured in 2018?"},
    ]}
]
input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(image, input_text, return_tensors="pt").to(model.device)

output = model.generate(**inputs, max_new_tokens=150)
# output = model.generate(**inputs, max_new_tokens=25)
print(processor.decode(output[0]))