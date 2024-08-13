// Drag-and-drop functionality
const dropArea = document.getElementById('drop-area');
dropArea.addEventListener('dragover', (event) => {
    event.preventDefault();
    dropArea.classList.add('hover');
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('hover');
});

dropArea.addEventListener('drop', (event) => {
    event.preventDefault();
    dropArea.classList.remove('hover');
    const file = event.dataTransfer.files[0];
    handleFile(file);
});

function handleFile(file) {
    const fileInput = document.getElementById('pdfFile');
    fileInput.files = event.dataTransfer.files;
    uploadPDF();
}function uploadPDF() {
    const fileInput = document.getElementById('pdfFile');
    
    if (fileInput.files.length === 0) {
        alert('Please select a file to upload.');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    // Show the loading screen
    document.getElementById('loading').style.display = 'flex';

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // Hide the loading screen
        document.getElementById('loading').style.display = 'none';

        alert(data.message);

        // Add the new chat to the chat list
        const chatList = document.getElementById('chatList');
        const newChatItem = document.createElement('li');
        newChatItem.textContent = `Chat with ${fileInput.files[0].name}`;
        newChatItem.setAttribute('data-chat-id', data.chat_id);
        newChatItem.onclick = function() {
            switchChat(data.chat_id);
        };
        chatList.appendChild(newChatItem);

        // Hide the upload section
        document.getElementById('upload-section').style.display = 'none';

        // Reset PDF viewer with the correct URL
        const pdfViewer = document.getElementById('pdfViewer');
        pdfViewer.src = `/uploaded_files/${fileInput.files[0].name}`;
        
        // Store the current chat_id globally
        window.currentChatId = data.chat_id;

        // Clear chat window for the new PDF
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.innerHTML = '';

        // Show the chat section
        document.getElementById('chatSection').style.display = 'flex';
    })
    .catch(error => {
        // Hide the loading screen in case of an error
        document.getElementById('loading').style.display = 'none';
        console.error('Error uploading PDF:', error);
    });
}

function switchChat(chatId) {
    fetch(`/switch_chat/${chatId}`, {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);

        // Clear the chat window
        const chatWindow = document.getElementById('chatWindow');
        chatWindow.innerHTML = '';

        // Load the chat history
        fetch(`/chat_history/${chatId}`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(history => {
            history.forEach(chat => {
                const userMessage = document.createElement('p');
                userMessage.classList.add('user-message');
                userMessage.textContent = `You: ${chat.question}`;
                chatWindow.appendChild(userMessage);

                const botMessage = document.createElement('p');
                botMessage.textContent = chat.response.answer;
                chatWindow.appendChild(botMessage);
            });
            chatWindow.scrollTop = chatWindow.scrollHeight;
        });

        // Update the PDF viewer for the switched chat
        const pdfViewer = document.getElementById('pdfViewer');
        pdfViewer.src = data.file_path;

        // Store the current chat_id globally
        window.currentChatId = chatId;
    });
}

function askQuestion() {
    const userInput = document.getElementById('userInput').value;

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ question: userInput, chat_id: window.currentChatId })
    })
    .then(response => response.json())
    .then(data => {
        const chatWindow = document.getElementById('chatWindow');
        const userMessage = document.createElement('p');
        userMessage.classList.add('user-message');
        userMessage.textContent = `You: ${userInput}`;
        chatWindow.appendChild(userMessage);

        const botMessage = document.createElement('p');
        botMessage.textContent = data.answer;
        chatWindow.appendChild(botMessage);

        // Scroll chat to the bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;

        // Clear input field after sending
        document.getElementById('userInput').value = '';
    })
    .catch(error => {
        console.error('Error asking question:', error);
    });
}
