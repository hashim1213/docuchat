import pdfplumber
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema import Document  # Correct import

class PDFQAModel:
    def __init__(self, pdf_path, api_key):
        self.pdf_path = pdf_path
        self.api_key = api_key
        self._load_pdf()
        self._create_vectorstore()
        self._create_rag_chain()

    def _load_pdf(self):
        self.docs = []
        with pdfplumber.open(self.pdf_path) as pdf:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                if text:
                    doc = Document(page_content=text, metadata={"page": i + 1})
                    self.docs.append(doc)

    def _create_vectorstore(self):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(self.docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings(api_key=self.api_key))
        self.retriever = vectorstore.as_retriever()

    def _create_rag_chain(self):
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, say that you don't know. "
            "Use three sentences maximum and keep the answer concise."
            "\n\n"
            "{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        llm = ChatOpenAI(model="gpt-4o-mini", api_key=self.api_key)
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        self.rag_chain = create_retrieval_chain(self.retriever, question_answer_chain)

    def ask_question(self, question):
        result = self.rag_chain.invoke({"input": question})
        return {
            "answer": result['answer'],
            "source": result["context"][0].metadata if result["context"] else {}
        }
