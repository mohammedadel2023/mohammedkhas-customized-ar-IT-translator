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
* **Document Processing**: `python-pptx` (Input), `WeasyPrint` (Output)
* **Utilities**: `uuid` (File safety), `json` (Data parsing)

## 📂 Project Structure

```text
├── models/
│   ├── base/               # The base Hugging Face model
│   └── adapter/            # Your fine-tuned LoRA files (adapter_model.safetensors)
├── inputs/                 # Temp storage for raw PPTX files (renamed with UUID)
├── outputs/                # Storage for generated PDFs
├── src/
│   ├── extractor.py        # Extracts text from slides
│   ├── inference.py        # Loads model & handles the "Translator" Prompt
│   ├── pdf_gen.py          # Converts JSON -> HTML -> PDF using WeasyPrint
│   └── utils.py            # UUID generation & file cleanup
├── main.py                 # Entry point
└── requirements.txt        # Dependency list