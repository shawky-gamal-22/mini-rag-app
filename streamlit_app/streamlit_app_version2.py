import streamlit as st
import requests
import os
from typing import Optional
import json
from io import BytesIO
from pydantic import BaseModel

# تكوين عنوان API الأساسي
API_BASE_URL = "http://fastapi:8000"  

class ProcessRequest(BaseModel):
    file_id: Optional[int] = None
    chunk_size: Optional[int] = 100
    overlap_size: Optional[int] = 20
    do_reset: Optional[int] = 0

class SearchRequest(BaseModel):
    text: str
    limit: int = 5

class PushRequest(BaseModel):
    do_reset: int = 0

# وظائف مساعدة للاتصال بالـ API
def upload_file(project_id: int, file: BytesIO, filename: str):
    content_type = 'application/pdf' if filename.lower().endswith('.pdf') else file.type
    files = {'file': (filename, file, content_type)}
    url = f"{API_BASE_URL}/api/v1/data/upload/{project_id}"
    response = requests.post(url, files=files)
    return response.json()

def process_file(project_id: int, process_request:ProcessRequest):
    url = f"{API_BASE_URL}/api/v1/data/process/{project_id}"    
    response = requests.post(url, json=process_request.model_dump())
    return response.json()

def push_to_index(project_id: int, push_request: PushRequest):
    url = f"{API_BASE_URL}/api/v1/nlp/index/push/{project_id}"
    response = requests.post(url, json=push_request.model_dump())
    return response.json()

def get_index_info(project_id: int):
    url = f"{API_BASE_URL}/api/v1/nlp/index/info/{project_id}"
    response = requests.get(url)
    return response.json()

def search_index(project_id: int, search_request: SearchRequest):
    url = f"{API_BASE_URL}/api/v1/nlp/index/search/{project_id}"
    response = requests.post(url, json=search_request.model_dump())
    return response.json()

def ask_question(project_id: int, search_request: SearchRequest):
    url = f"{API_BASE_URL}/api/v1/nlp/index/answer/{project_id}"
    response = requests.post(url, json=search_request.model_dump())
    return response.json()

# واجهة Streamlit الرئيسية
def main():
    st.set_page_config(page_title="Mini RAG System", layout="wide")
    st.title("Mini RAG System")
    project_id=-1
    
    # شريط جانبي للتنقل
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Upload & Process", "Search & Query"])
    
    # قسم رفع الملفات ومعالجتها
    if page == "Upload & Process":
        st.header("Upload & Process Documents")
        
        # اختيار معرف المشروع
        project_id = st.number_input("Project ID", min_value=1, value=1)
        
        # رفع الملف
        uploaded_file = st.file_uploader("Choose a file", type=["txt", "pdf"])
        
        if uploaded_file is not None:
            # عرض معلومات الملف
            file_details = {
                "Filename": uploaded_file.name,
                "FileSize": f"{uploaded_file.size / 1024:.2f} KB",
                "FileType": uploaded_file.type
            }
            
            st.write(file_details)
            
            if st.button("Upload File"):
                with st.spinner("Uploading..."):
                    result = upload_file(project_id, uploaded_file, uploaded_file.name)
                    st.success("File uploaded successfully!")
                    st.json(result)
        
        # معالجة الملف
        st.subheader("Process Documents")
        with st.form("process_form"):
            col1, col2 = st.columns(2)
            with col1:
                chunk_size = st.number_input("Chunk Size", min_value=100, value=1000)
            with col2:
                overlap_size = st.number_input("Overlap Size", min_value=0, value=200)
            
            do_reset = st.checkbox("Reset existing chunks", value=False)
            file_id = st.number_input("Project ID", min_value=1, value=None)
            submitted = st.form_submit_button("Process Documents")
            if submitted:
                
                process_req = {
                    "chunk_size":chunk_size,
                    "overlap_size":overlap_size,
                    "do_reset": 1 if do_reset else 0,
                    "file_id":file_id if file_id else None
                }
                process_req = ProcessRequest(**process_req)
                with st.spinner("Processing documents..."):
                    result = process_file(project_id=project_id,process_request= process_req)
                    st.success("Processing completed!")
                    st.json(result)

                # indexing to vector database
                do_reset = 1 
                push_req = PushRequest(do_reset=1 if do_reset else 0)
                with st.spinner("Pushing to vector index..."):
                    result = push_to_index(project_id, push_req)
                    st.success("Indexing completed!")
                    st.json(result)

 
    # قسم البحث والاستعلام
    elif page == "Search & Query":
        # st.header("Search & Query Documents")
        
        # project_id = st.number_input("Project ID", min_value=1, value=1, key="search_project_id")
        
        # طرح سؤال على النظام
        st.header("Ask a Question")
        project_id = st.number_input("Project ID", min_value=1, value=1, key="ask_project_id")
        
        if project_id <= 0:
            st.warning("Please enter a valid Project ID")
            return
        
        question = st.text_area("Your Question")
        limit= 5
        st.write(project_id)
        if st.button("Get Answer"):
            if not question:
                st.warning("Please enter a question")
            else:
                search_req = SearchRequest(text=question, limit=limit)
                
                with st.spinner("Generating answer..."):
                    result = ask_question(project_id, search_req)
                    
                    if "answer" in result:
                        st.success("Answer:")
                        st.write(result["answer"])
                        
                        with st.expander("See details"):
                            st.write("**Full Prompt:**", result.get("full_prompt", ""))
                            st.write("**Chat History:**", result.get("chat_history", []))
                    else:
                        st.error("Failed to get answer")
                        st.json(result)

if __name__ == "__main__":
    main()