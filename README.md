# 📄 PPTX to Arabic PDF: Intelligent Technical Translator

**An automated pipeline that converts English IT presentations into professionally formatted Arabic PDF reports.**

This tool ingests `.pptx` files, extracts the text, and processes it using a fine-tuned **Large Language Model (LLM)** equipped with LoRA adapters. The model acts as an expert Front-End Developer & Translator, converting content to Arabic while strictly preserving technical terminology and code snippets in their original English form. The final output is a clean, styled PDF.

## 🚀 Key Features

* **🛡️ Robust File Ingestion**
    * Validates input `.pptx` files.
    * **Concurrency Safety**: Assigns a **Unique Identifier (UUID)** to every uploaded file to prevent filename conflicts and data overwrites during processing.

* **🤖 Expert LLM Processing**
    * **Role**: Acts as an expert IT translator.
    * **Strict Terminology**: Preserves technical terms (e.g., "API Gateway", "Latency") in English, wrapped in `<span dir="ltr">`.
    * **Code Awareness**: Detects inline code and syntax, prevents translation/reordering, and applies monospace formatting with HTML escaping.

* **📚 Automated Glossary**
    * The model automatically identifies complex IT terms and generates a separate "Explaining" section with Arabic definitions.

* **📄 High-Fidelity PDF Generation**
    * Converts the model's structured JSON/HTML output into a PDF using **WeasyPrint**.
    * Supports Right-to-Left (RTL) layout and correct Arabic font rendering.

## 🛠️ Tech Stack

* **Core Logic**: Python 3.10+
* **AI/ML**: `transformers`, `peft` (LoRA), PyTorch
* **Document Processing**: `python-pptx` (Input), `pdfkit` (Output)
* **Utilities**: `time` (File safety), `json` (Data parsing)

## 📂 Project Structure

```text
|
├── inputs/                 # Temp storage for raw PPTX files (renamed with UUID)
├── outputs/                # Storage for generated PDFs
|── Model_Processing 
|   |
|   |──Model_Saved.py       # install the model and the adaptor then save them in the local pc
|   └──Model_Using.py       # use the adaptore that integrated in the main model to support the Project function
|───to_show                 # some figures and model result after and before finetunig which decleare the progress of the model
|   |
|   |──0.5b/                 # all what related with model 0.5b
|   |  |
|   |  |──0.5b_d1           # figure and model(0.5) result before and after while finetune in the first data (500 samples)
|   |  └──0.5B_d2           #figure and model(0.5) result before and after while finetune in the final data (1000 samples)
|   |──1.5b/
|   |  |
|   |  |──1.5b_d1           # figure and model(1.5) result before and after while finetune in the first data (500 samples)
|   |  └──1.5B_d2           #figure and model(1.5) result before and after while finetune in the final data (1000 samples)
|   |──Teacher_result.text  # the result of the Teacher model gemini 2.5 pro
|   └──Teacher_pdf
|── Processing_utils.py        # Extracts text from slides
|── app.py        # Loads model & handles the "Translator" Prompt
│── debug_app.py          # debug all steps in the workflow
├── workflow.py
└── Lora_Finetune.ipynb        # notebook for knowledge distilation and finetuning