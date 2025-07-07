from fastapi import FastAPI
from pydantic import BaseModel
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

app = FastAPI()

# Load model and tokenizer once at startup
tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
model = AutoModelForCausalLM.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

class PromptRequest(BaseModel):
    prompt: str

@app.post("/parse")
def parse_prompt(req: PromptRequest):
    inputs = tokenizer(req.prompt, return_tensors="pt").to(device)
    outputs = model.generate(**inputs, max_new_tokens=50)
    result = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return {"result": result}
