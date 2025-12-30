import os
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from peft import PeftModel

local_base_path = r"C:\Users\User\OneDrive\DA350P\models"
local_adapter_path = r"C:\Users\User\OneDrive\DA350P\models\0.5B_d1"

tokenizer = AutoTokenizer.from_pretrained(local_base_path, fix_mistral_regex=True)
base_model = AutoModelForCausalLM.from_pretrained(local_base_path).to("cuda")

Lora = PeftModel.from_pretrained(base_model, local_adapter_path)

Lora.eval()

system_instruction = """You are an expert English-to-Arabic technical translator and Front-End Developer.

Your task is to translate the given English text related to the IT field into Arabic, while STRICTLY preserving all technical IT terms and Code Snippets in their original English form.

========================
OUTPUT FORMAT (MANDATORY)
========================
Return a valid JSON object with EXACTLY two keys:
1. "translated"
2. "explaining"

No additional keys, comments, or text are allowed.

========================
RULES FOR "translated"
========================
1. Wrap the ENTIRE translated content inside ONE single HTML container:
   <div dir="rtl"> ... </div>

2. All non-technical text MUST be translated into Arabic.

3. Every technical IT term (that is NOT code) MUST:
   - Stay exactly as written (no spelling changes).
   - Be wrapped in: <span dir="ltr">TERM</span>

4. RULES FOR CODE SNIPPETS (Variables, Functions, Commands, Syntax):
   - IF the text contains inline code (e.g., function_name(), var x, print("hello")):
     a) Do NOT translate it.
     b) Do NOT change the order of characters.
     c) You MUST escape HTML special characters (e.g., convert < to &lt; and > to &gt;) to ensure the code renders visibly.
     d) Enclose the code in double quotes.
     e) Wrap the result in a span with LTR direction and monospace font.

     Format: <span dir="ltr" style="font-family: monospace;">"CODE_HERE"</span>

5. STRICT STRUCTURE PRESERVATION:
   - You MUST preserve the visual layout of the original text.
   - If the English input has a newline (or is a list of bullet points), you MUST insert a <br> tag in the Arabic translation at the exact same position.
   - Do NOT merge a list of items into a single paragraph.

========================
RULES FOR "explaining"
========================
1. Explain ONLY complex, domain-specific technical IT terms (e.g., "Polymorphism", "Latency", "API Gateway").
2. EXCLUSION LIST - Do NOT explain:
   - Basic computer terms (e.g., "File", "Folder", "Click", "Screen", "User").
   - Common verbs (e.g., "Save", "Open", "Run").
   - Code snippets, variable names, or syntax (e.g., "int x", "print()").
3. Each explanation MUST be wrapped in its own HTML block:
   <div dir="rtl">TERM: الشرح بالعربية</div>
4. Use the SAME English technical term exactly as it appears.
5. The output value of "explaining" MUST contain:
   - Raw HTML code only
   - No Markdown

========================
STRICT CONSTRAINTS
========================
- The final output MUST be a valid JSON object.
- Do NOT include code fences (like ```json).
- Do NOT add any text outside the JSON."""



def prepare_response(res):
    try:
        print("\n" + "="*50)
        print("DEBUG: MODEL OUTPUT RECEIVED:")
        print(res)
        print("="*50 + "\n")

        start_idx = res.find('{')
        end_idx = res.rfind('}') + 1 
        if start_idx == -1 or end_idx == 0:
            return "Error: No JSON found"

        json_str = res[start_idx:end_idx]
        result_text = json.loads(json_str) 
        
    except Exception as e:
        return f"Error parsing JSON: {e}"

    # 2. Inject the Dictionary values into the HTML String
    # NOTICE: We use result_text.get(), NOT html_text.get()
    html_text = f"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <style>
        @page {{ size: A4; margin: 1in; }}
        body {{ font-family: 'Arial', sans-serif; font-size: 14pt; line-height: 1.8; direction: rtl; text-align: right; }}
        .container {{ width: 100%; margin-bottom: 30px; }}
        .header {{ background-color: #2980b9; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-weight: bold; }}
        .content {{ text-align: justify; background-color: #f8f9fa; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        span[dir='ltr'] {{ direction: ltr; unicode-bidi: embed; font-family: sans-serif; font-weight: bold; color: #c0392b; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">الترجمة (Translation)</div>
        <div class="content">
            {result_text.get('translated', 'No translation')}
        </div>
    </div>
    <div class="container">
        <div class="header" style="background-color: #2c3e50;">المصطلحات (Key Terms)</div>
        <div class="content">
            {result_text.get('explaining', 'No explanation')}
        </div>
    </div>
</body>
</html>
"""
    # 3. CRITICAL: Return the HTML STRING, not the dictionary
    return html_text


def translate_and_generate_html(data_input):

    if isinstance(data_input, str):
        try:
            data = json.loads(data_input)
        except json.JSONDecodeError:
            return "Error: Invalid JSON input received from extractor."
    else:
        data = data_input

    messages = [
    {"role": "system","content":f"{system_instruction}"},
    {"role": "user", "content": f"{data['en']}"},
    ]

    inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
    ).to("cuda")

    with torch.no_grad():
        outputs = Lora.generate(
        **inputs,
        max_new_tokens=1024,
        do_sample=False,
        repetition_penalty=1.1
        )
    qwen_res = tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:])
    return prepare_response(qwen_res)


