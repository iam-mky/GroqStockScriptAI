import os
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50


def loadpdf_and_chunks(pdf_paths:list[str])->list[dict]:
    """
    Reads mulitple PDFs, extracts text page by page, splits each page's
    text into 500-char chunks (50-char overlap), and returns a list of
    dictionaries containing chunk text and metadata.
    """
    chunks = []
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)

    for path in pdf_paths:
        #skip if path doesnt exist
        if not os.path.exists(path) :
            print(f"Warning: File not found at  {path}")
            continue

        try:
            reader = PdfReader(path)
            file_name = os.path.basename(path)

            #process each page, then split its text into chunks
            for page_num, page in enumerate(reader.pages, start=1) :
                text = page.extract_text()

                #Clean whitespace and skip empty pages
                if not text or not text.strip():
                    continue

                page_chunks = splitter.split_text(text.strip())

                for chunk_index, chunk_text in enumerate(page_chunks):
                    chunks.append({
                        "text": chunk_text,
                        "metadata": {
                            "source": file_name,
                            "file_path": path,
                            "page": page_num,
                            "chunk_index": chunk_index
                        }
                    })
        except Exception as e:
            print(f"Error processing at {path}: {str(e)}")

    return chunks
