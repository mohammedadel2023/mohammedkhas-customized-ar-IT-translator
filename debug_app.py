import streamlit as st
import os
import json
import time
# Import your functions individually
from Processing_utils import validate_input_file, process_single_slide, render_pdf_from_html_strings, generate_unique_output_path
from Model_Processing.Model_Using import translate_and_generate_html

st.set_page_config(page_title="Pipeline Debugger", layout="wide")
st.title("🕵️ Pipeline Component Tester")

# 1. File Upload
uploaded_file = st.file_uploader("Upload a PPTX file to test", type=["pptx"])
slide_number = st.number_input("Slide Number", min_value=1, value=1)

# Checkbox to skip AI if you just want to test PDF generation quickly
skip_ai = st.checkbox("⚡ Skip AI Model (Use Dummy Data)", value=False)

if uploaded_file and st.button("▶️ Start Step-by-Step Test"):
    
    # Save file locally first (Streamlit requirement)
    os.makedirs("inputs", exist_ok=True)
    temp_path = os.path.join("inputs", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.write("---")

    # ==========================================
    # STEP 1: TEST VALIDATION
    # ==========================================
    st.subheader("Step 1: Validate Input File")
    status = validate_input_file(temp_path, slide_number)
    
    st.write(f"**Return Value:** `{status}`")
    st.write(f"**Type:** `{type(status)}`")
    
    if not status:
        st.error("❌ Validation Failed. Stopping here.")
        st.stop()
    else:
        st.success("✅ Validation Passed")

    # ==========================================
    # STEP 2: TEST PATH GENERATION
    # ==========================================
    st.subheader("Step 2: Generate Output Path")
    output_path = generate_unique_output_path(temp_path, slide_number)
    st.write(f"**Return Value:** `{output_path}`")
    
    if not output_path:
        st.error("❌ Path Generation Failed.")
        st.stop()
    else:
        st.success("✅ Path Generated")

    # ==========================================
    # STEP 3: TEST SLIDE EXTRACTION
    # ==========================================
    st.subheader("Step 3: Extract Slide Text")
    slides_text = process_single_slide(temp_path, slide_number)
    
    # Show strict type checking
    st.write(f"**Type:** `{type(slides_text)}`")
    
    if slides_text == 0:
        st.error("❌ Extraction Failed (Returned 0). Slide might be empty.")
        st.stop()
    
    # Try to pretty print the JSON
    try:
        parsed_json = json.loads(slides_text)
        st.success("✅ Text Extracted & Valid JSON")
        with st.expander("View Extracted JSON Data"):
            st.json(parsed_json)
    except:
        st.warning("⚠️ Extracted text is not valid JSON, showing raw string:")
        st.text(slides_text)

    # ==========================================
    # STEP 4: TEST AI MODEL (Translation)
    # ==========================================
    st.subheader("Step 4: AI Translation")
    
    html_slides = ""
    
    if skip_ai:
        st.warning("⏩ Using Dummy Data (Skipping Model)")
        html_slides = "<html><body><h1>Test PDF</h1><p>This is a test.</p></body></html>"
        time.sleep(1)
    else:
        with st.spinner("Running Model... (This takes time)"):
            # This returns the result of prepare_response(qwen_res)
            html_slides = translate_and_generate_html(slides_text)
    
    # --- HERE IS THE RESULT YOU WANTED TO SEE ---
    st.write(f"**Return Type:** `{type(html_slides)}` (Must be <class 'str'>)")
    
    if not html_slides or "Error" in html_slides:
        st.error("❌ Translation Failed or returned Error.")
        st.error(f"Raw Output: {html_slides}")
        st.stop()
    else:
        st.success("✅ Translation Complete (HTML String Received)")
        
        st.markdown("### 📄 Returned HTML Content:")
        st.code(html_slides, language='html')
        
        # Option to download the raw HTML for debugging
        st.download_button(
            label="Download HTML as .txt",
            data=html_slides,
            file_name="debug_html_output.html",
            mime="text/html"
        )

    # ==========================================
    # STEP 5: TEST PDF GENERATION
    # ==========================================
    st.subheader("Step 5: PDF Rendering")
    
    # Pass the HTML string (html_slides) to the renderer
    pdf_status = render_pdf_from_html_strings(html_slides, output_path)
    
    st.write(f"**Return Value:** `{pdf_status}`")
    
    if pdf_status:
        st.success(f"✅ PDF Created Successfully at `{output_path}`")
        
        if os.path.exists(output_path):
            with open(output_path, "rb") as f:
                st.download_button("Download Generated PDF", f, file_name="debug_test.pdf")
        else:
            st.error("❌ Function returned True, but file was not found on disk.")
    else:
        st.error("❌ PDF Generation Failed (WeasyPrint error).")