from .BaseController import BaseController
from .ProjectController import ProjectController
import os
from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from models import ProcessingEnum




class ProcessController(BaseController):
    def __init__(self, project_id: str):
        super().__init__()
        self.project_id = project_id
        self.project_path= ProjectController().get_project_path(project_id)

    def get_file_extension(self, file_id: str):

       return os.path.splitext(file_id)[-1]


    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id)
        file_path = os.path.join(self.project_path, file_id)
        if file_ext == ProcessingEnum.TXT.value:
            return TextLoader(file_path, encoding='utf-8')
        
        if file_ext == ProcessingEnum.PDF.value:
            return PyMuPDFLoader(file_path)
        

        return None
    

    def get_file_content(self, file_id: str):
        
        loader = self.get_file_loader(file_id)
        return loader.load() if loader else None


    def process_file_content(self, file_content:list, file_id: str,
                             chunk_size: int = 100, overlap: int = 20):
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            length_function=len
        )


        file_content_texts = [
            doc.page_content 
            for doc in file_content
        ]

        file_content_metadata = [
            doc.metadata
            for doc in file_content
        ]

        chunks = text_splitter.create_documents(
            file_content_texts,
            metadatas=file_content_metadata,
            #id=[f"{file_id}_{i}" for i in range(len(file_content_texts))],
        )

        return chunks 



    