from flask import Flask, request, jsonify, render_template, send_from_directory
import os
from dotenv import load_dotenv
from pdf_qa import PDFQAModel
import uuid

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key from the .env file
openai_api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Dictionary to store active chat sessions
active_chats = {}

# Serve the HTML page
@app.route('/')
def index():
    return render_template('index.html')

# Endpoint to create a new chat session with a new PDF
@app.route('/upload', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"message": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400

    # Create a unique filename
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"./uploaded_files/{unique_filename}"
    
    # Debugging print to check file path
    print(f"Saving file to: {file_path}")
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    # Create a new chat session
    chat_id = str(uuid.uuid4())
    pdf_qa_model = PDFQAModel(file_path, openai_api_key)
    active_chats[chat_id] = {
        'pdf_qa_model': pdf_qa_model,
        'file_path': file_path,
        'chat_history': []
    }

    return jsonify({"message": "PDF uploaded and processed.", "chat_id": chat_id, "file_path": file_path}), 200

# Endpoint to switch to a different chat session
@app.route('/switch_chat/<chat_id>', methods=['GET'])
def switch_chat(chat_id):
    if chat_id not in active_chats:
        return jsonify({"message": "Chat session not found."}), 404
    
    return jsonify({"message": f"Switched to chat {chat_id}.", "file_path": active_chats[chat_id]['file_path']}), 200

# Endpoint to ask a question in the current chat session
@app.route('/ask', methods=['POST'])
def ask_question():
    chat_id = request.json.get("chat_id")
    if not chat_id or chat_id not in active_chats:
        return jsonify({"answer": "Please upload a PDF first.", "source": {}}), 400

    pdf_qa_model = active_chats[chat_id]['pdf_qa_model']
    question = request.json.get("question")
    response = pdf_qa_model.ask_question(question)
    
    # Save question and response to chat history
    active_chats[chat_id]['chat_history'].append({
        'question': question,
        'response': response
    })

    return jsonify(response), 200

# Endpoint to get the chat history
@app.route('/chat_history/<chat_id>', methods=['GET'])
def get_chat_history(chat_id):
    if chat_id not in active_chats:
        return jsonify({"message": "Chat session not found."}), 404
    
    return jsonify(active_chats[chat_id]['chat_history']), 200

# Serve uploaded files
@app.route('/uploaded_files/<filename>')
def uploaded_file(filename):
    # Debugging print to check file serving
    print(f"Serving file: {filename}")
    
    return send_from_directory('uploaded_files', filename)

if __name__ == '__main__':
    app.run(debug=True)
