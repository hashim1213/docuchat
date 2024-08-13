from langchain_community.document_loaders import PyPDFLoader

file_path = "bluebook.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

print(len(docs))  # Check the number of pages loaded
print(docs[0].page_content[0:100])  # Preview the content
print(docs[0].metadata)  # View metadata
