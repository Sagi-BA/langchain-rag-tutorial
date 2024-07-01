from dotenv import load_dotenv
import os
import shutil
import pdf2image
import streamlit as st
from src.pdf_converter import PDFConverter  # Import the PDFConverter class
from src.data_store_generator import DataStoreGenerator  # Import the DataStoreGenerator class
from src.data_query import DataQuery  # Import the DataQuery class
from datetime import datetime
import pytesseract

# Set the page configuration
st.set_page_config(
    page_title="Ask your PDF",
    page_icon="👋",
)

# Load environment variables. Assumes that project contains .env file with API keys
load_dotenv()

# Add poppler path to system PATH
poppler_path = os.path.join(os.path.dirname(__file__), 'poppler_binaries', 'bin')  # Update this path based on your directory structure
os.environ["PATH"] += os.pathsep + poppler_path
print(os.pathsep + poppler_path)

def check_dependencies():
    try:
        # Check if pdfinfo is accessible
        poppler_check = os.system("pdfinfo -v")
        if poppler_check != 0:
            st.error("Poppler is not installed or not found in the PATH. Please make sure poppler binaries are correctly installed and accessible.")
            return False
        # Check if tesseract is accessible
        tesseract_check = os.system("tesseract -v")
        if tesseract_check != 0:
            st.error("Tesseract is not installed or not found in the PATH. Please make sure tesseract binaries are correctly installed and accessible.")
            return False
        return True
    except Exception as e:
        st.error(f"Error checking dependencies: {e}")
        return False


# Verify if poppler is in the PATH and accessible
def check_poppler():
    try:
        result = os.system("pdfinfo -v")
        if result != 0:
            st.error("Poppler is not installed or not found in the PATH. Please make sure poppler binaries are correctly installed and accessible.")
            return False
        return True
    except Exception as e:
        st.error(f"Error checking Poppler installation: {e}")
        return False


# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

def main():
    if not check_dependencies():
        return
    
    if not check_poppler():
        return
     
    # Load the OpenAI API key from the environment variable
    if os.getenv("OPENAI_API_KEY") is None or os.getenv("OPENAI_API_KEY") == "":
        st.error("OPENAI_API_KEY is not set")
        exit(1)

    st.write("# Welcome to Book Questions! 👋")
    st.markdown(
        """        
        RAG + Langchain Python Project: Easy AI/Chat For **PDF Books** 👈.        
        Learn how to build a "retrieval augmented generation" (RAG) app with Langchain and OpenAI in Python.        
        join our [Whatsapp community](https://bit.ly/3TV0iuq)
        """
    )

    st.sidebar.markdown(
        """        
        By: Sagi bar on        
        """
    )

    # Add the Clear button
    if st.sidebar.button(label='Clear'):
        clear_all()

    # create_sidebar()
    pdf_file = step_1()
    step_2(pdf_file)
    step_3()
    step_4()

def step_1():
    st.sidebar.write("""
    <div style="color: green; font-size: 24px;">
        Step 1 - Upload Book
    </div>
    """, unsafe_allow_html=True)
    
    pdf_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")

    if pdf_file is not None:
        st.success('Book uploaded successfully!')
        
    return pdf_file

def select_language():
    languages = {
        'English': 'eng',
        'Hebrew': 'heb',
        'French': 'fra',
        'Spanish': 'spa',
        'German': 'deu',
        # Add more languages as needed
    }

    language_name = st.sidebar.selectbox("Select book language", list(languages.keys()), index=0)
    return languages[language_name]

def step_2(pdf_file):
    st.sidebar.write("""
    <div style="color: green; font-size: 24px;">
        Step 2 - Convert Book to text format
    </div>
    """, unsafe_allow_html=True)

    language_code = select_language()    
    
    if st.sidebar.button("Convert"):
        st.info('Start converting, please wait...')  
        # Paths for saving the converted Markdown file
        upload_dir = "uploads"
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        pdf_path = os.path.join(upload_dir, pdf_file.name)
        md_path = pdf_path.replace(".pdf", ".md")

        # Save the uploaded PDF file temporarily
        with open(pdf_path, "wb") as f:
            f.write(pdf_file.getbuffer())

        # Get the size of the PDF file
        pdf_size = os.path.getsize(pdf_path) / 1024  # size in KB
        pdf_size_str = f"{pdf_size:.2f} KB" if pdf_size < 1024 else f"{pdf_size / 1024:.2f} MB"

        # Create an instance of PDFConverter and convert the PDF to Markdown
        with st.spinner(text="In progress..."):
            converter = PDFConverter()
            try:
                converter.pdf_to_md(pdf_path, md_path, lang=language_code)
            except pdf2image.exceptions.PDFInfoNotInstalledError:
                st.error("Poppler is not installed. Please install Poppler to proceed.")
            except pytesseract.pytesseract.TesseractNotFoundError:
                st.error("Tesseract is not installed. Please install Tesseract to proceed.")

        # Read the converted Markdown file
        with open(md_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # Get the size of the Markdown text
        text_size = len(md_content.encode('utf-8')) / 1024  # size in KB
        text_size_str = f"{text_size:.2f} KB" if text_size < 1024 else f"{text_size / 1024:.2f} MB"

        # Display the converted Markdown content
        st.write(f"## Read the converted PDF file (PDF size: {pdf_size_str}, Text size: {text_size_str})")
        st.text_area("Converted Text", md_content, height=300)
        
        st.success('Book converted successfully!')

def step_3():
    st.sidebar.write("""
        <div style="color: green; font-size: 24px;">
            Step 3 - Create DataBase
        </div>
        """, unsafe_allow_html=True)
        
    if st.sidebar.button("Create Data Store"):  
        st.info('Start Create Data Store, please wait...')
        with st.spinner(text="In progress..."):
            data_store_generator = DataStoreGenerator()
            data_store_generator.generate_data_store()
        st.success('Data store created successfully!')    

def step_4():
    st.sidebar.write("""
        <div style="color: green; font-size: 24px;">
            Step 4 - Ask Question
        </div>
        """, unsafe_allow_html=True)
    
    user_question = st.sidebar.text_input("Ask a question about your book: ")

    if user_question is not None and user_question != "":
        with st.spinner(text="In progress..."):
            st.info(user_question)
            myQuery = DataQuery()
            response = myQuery.query(user_question)
            
            # Get the current time
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Append the question and response to the history
            st.session_state.history.append((timestamp, user_question, response))

            # Display the history
            for timestamp, question, response in st.session_state.history:
                st.markdown(
                    f"""
                    <div dir="rtl" style="text-align: right;">
                        <b>[{timestamp}]</b> <b>ש:</b> {question} <br/>
                        <b>ת:</b> {response}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.write("---")
        st.success('Done!')

def clear_all():
    st.info('Clearing all')
    chroma_dir = "chroma"
    uploads_dir = "uploads"

    def remove_readonly(func, path, excinfo):
        os.chmod(path, 0o777)
        func(path)

    if os.path.exists(chroma_dir):
        shutil.rmtree(chroma_dir, onerror=remove_readonly)
        os.makedirs(chroma_dir)

    if os.path.exists(uploads_dir):
        shutil.rmtree(uploads_dir, onerror=remove_readonly)
        os.makedirs(uploads_dir)

    st.session_state.history.clear()   
    st.rerun()

if __name__ == "__main__":
    main()