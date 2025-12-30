from Process_funcs import validate_input_file ,process_single_slide, render_pdf_from_html_strings , generate_unique_output_path
from Model_Processing.Model_Using import translate_and_generate_html


def process_translation_pipeline(file_path: str,slide_nubmer:int) -> str:

    # 0. Validate input
    status=validate_input_file(file_path,slide_nubmer)
    #>>>>return 1 or 0
    if not (status):
        return False
    # 1. Create unique output path
    output_pdf_path = generate_unique_output_path(file_path,slide_nubmer)
    #>>>>return a new path for pdf file we will create

    # 2. Extract text from PPTX
    slides_text = process_single_slide(file_path,slide_nubmer)
    #extract all text from slides as [slide_x_text_as_json({key:value)}]
    if (slides_text == 0):
        return False

    # 3. Translate text and generate HTML per slide (in-memory)
    html_slides = translate_and_generate_html(slides_text)
    #it will return the same structure of the slides_text put it will include an html text as a translated for extract text

    # 4. Render PDF directly from HTML strings
    render_pdf_from_html_strings(html_slides, output_pdf_path)
    #convert all html text we have into pdf file and save it in the path we generate 

    return output_pdf_path



#run by --streamlit run app.py --server.fileWatcherType none 