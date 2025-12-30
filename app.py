import streamlit as st
import os
import streamlit.components.v1 as components

# Import the functions from your pipeline
from Process_funcs import validate_input_file, process_single_slide, render_pdf_from_html_strings, generate_unique_output_path
from Model_Processing.Model_Using import translate_and_generate_html

# --- 1. PAGE CONFIGURATION (Arabic Support) ---
st.set_page_config(
    page_title="المترجم التقني الذكي",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to force Right-to-Left (RTL) layout for Arabic
st.markdown("""
    <style>
        .main { direction: rtl; }
        h1, h2, h3, p, div, label, span { text-align: right; font-family: 'Arial', sans-serif; }
        .stButton button { float: right; }
        .stAlert { direction: rtl; text-align: right; }
        /* Fix for file uploader text alignment */
        [data-testid="stFileUploader"] { text-align: right; }
    </style>
""", unsafe_allow_html=True)

# --- 2. HEADER ---
st.title("📄 المترجم التقني الذكي (PPTX)")
st.markdown("### ترجمة الشرائح التقنية مع الحفاظ على المصطلحات والأكواد")
st.markdown("---")

# --- 3. SIDEBAR INPUTS ---
with st.sidebar:
    st.header("إعدادات الملف")
    uploaded_file = st.file_uploader("📂 اختر ملف العرض التقديمي (PPTX)", type=["pptx"])
    slide_number = st.number_input("🔢 رقم الشريحة المراد ترجمتها", min_value=1, value=1)
    
    st.info("💡 ملاحظة: تأكد من أن الشريحة تحتوي على نص تقني باللغة الإنجليزية.")

# --- 4. MAIN PROCESSING ---
if uploaded_file and st.button("🚀 بدء الترجمة"):
    
    # A. Save the file temporarily
    os.makedirs("inputs", exist_ok=True)
    temp_path = os.path.join("inputs", uploaded_file.name)
    with open(temp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # B. Validation
    with st.status("جاري معالجة البيانات...", expanded=True) as status:
        
        st.write("1️⃣ التحقق من الملف...")
        if not validate_input_file(temp_path, slide_number):
            status.update(label="خطأ في الملف!", state="error")
            st.error("❌ الملف غير صالح أو رقم الشريحة غير موجود.")
            st.stop()
            
        st.write("2️⃣ استخراج النصوص...")
        slides_text = process_single_slide(temp_path, slide_number)
        if slides_text == 0:
            status.update(label="فشل الاستخراج!", state="error")
            st.error("❌ لم يتم العثور على نص كافٍ في هذه الشريحة.")
            st.stop()

        st.write("3️⃣ الذكاء الاصطناعي يترجم ويشرح (قد يستغرق وقتاً)...")
        # Generate the HTML Content
        html_result = translate_and_generate_html(slides_text)
        
        # Check for errors in model output
        if not isinstance(html_result, str) or "Error" in html_result:
             status.update(label="خطأ في النموذج!", state="error")
             st.error("❌ حدث خطأ أثناء الترجمة.")
             st.stop()

        st.write("4️⃣ إنشاء ملف PDF...")
        output_pdf_path = generate_unique_output_path(temp_path, slide_number)
        pdf_success = render_pdf_from_html_strings(html_result, output_pdf_path)
        
        if pdf_success:
            status.update(label="✅ تمت العملية بنجاح!", state="complete")
        else:
            status.update(label="⚠️ تم العرض ولكن فشل حفظ PDF", state="warning")

    # --- 5. DISPLAY RESULTS (Show Translation & Explanation) ---
    st.divider()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.success("✅ تم إنشاء ملف PDF جاهز للتحميل")
        if os.path.exists(output_pdf_path):
            with open(output_pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 تحميل ملف PDF",
                    data=pdf_file,
                    file_name="Translated_Slide.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    with col2:
        st.info("ℹ️ يمكنك معاينة النتيجة مباشرة في الأسفل 👇")

    # --- 6. PREVIEW AREA (IFrame) ---
    st.subheader("👁️ معاينة الترجمة والشرح")
    
    # We display the HTML inside a container. 
    # Height is adjustable to fit the content.
    components.html(html_result, height=800, scrolling=True)

elif not uploaded_file:
    st.warning("👈 يرجى رفع ملف PPTX من القائمة الجانبية للبدء.")