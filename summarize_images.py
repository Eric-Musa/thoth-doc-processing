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


image = Image.open('data/converted/Accelerating the structure search of catalysts with machine learning - Curr Opin - 2021 -1/picture-5.png')

messages = [
    {"role": "user", "content": [
        {"type": "image"},
        {"type": "text", "text": "Please summarize this image."},
    ]}
]
input_text = processor.apply_chat_template(messages, add_generation_prompt=True)
inputs = processor(image, input_text, return_tensors="pt").to(model.device)

output = model.generate(**inputs, max_new_tokens=30)
print(processor.decode(output[0]))