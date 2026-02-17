import os
import tempfile
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from config import KB_PDF_PATH

class KnowledgeBase:
    def __init__(self, embeddings):
        self.embeddings = embeddings
        self.kb_db = None
        self.user_db = None
        
    def build_kb_vector_db(self):
        if self.embeddings is None:
            return None
        
        docs = []
        # Check if directory exists and has PDFs
        if os.path.exists(KB_PDF_PATH):
            for file in os.listdir(KB_PDF_PATH):
                if file.endswith(".pdf"):
                    file_path = os.path.join(KB_PDF_PATH, file)
                    try:
                        loader = PyPDFLoader(file_path)
                        docs.extend(loader.load())
                    except Exception as e:
                        print(f"Error loading {file}: {e}")
                        continue
        
        if not docs:
            return None
            
        splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        self.kb_db = FAISS.from_documents(chunks, self.embeddings)
        return self.kb_db

    def process_uploaded_file(self, uploaded_file):
        if self.embeddings is None:
            return None
        
        # Use tempfile with proper cleanup
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf", dir=tempfile.gettempdir()) as tmp:
                tmp.write(uploaded_file.getvalue())
                tmp_path = tmp.name

            loader = PyPDFLoader(tmp_path)
            docs = loader.load()
            
            if not docs:
                return None
                
            splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
            chunks = splitter.split_documents(docs)
            self.user_db = FAISS.from_documents(chunks, self.embeddings)
            return self.user_db
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return None
            
        finally:
            # Clean up temp file
            if tmp_path and os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except:
                    pass