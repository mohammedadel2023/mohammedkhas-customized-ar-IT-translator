import os
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel



base_model_id = "Qwen/Qwen2.5-0.5B-Instruct"
adapter_id = "mohammedkhas/customized-ar-translator"

local_base_path = r"C:\Users\User\OneDrive\DA350P\models"
local_adapter_path = r"C:\Users\User\OneDrive\DA350P\models\0.5B_d1"

tokenizer = AutoTokenizer.from_pretrained(base_model_id)
base_model = AutoModelForCausalLM.from_pretrained(base_model_id)


tokenizer.save_pretrained(local_base_path)
base_model.save_pretrained(local_base_path)

model = PeftModel.from_pretrained(base_model, adapter_id)
model.save_pretrained(local_adapter_path)