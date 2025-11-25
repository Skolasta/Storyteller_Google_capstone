const API_URL = 'http://localhost:8000';
let sessionId = null;

const startBtn = document.getElementById('start-btn');
const sendBtn = document.getElementById('send-btn');
const userInput = document.getElementById('user-input');
const messagesContainer = document.getElementById('messages');
const chatTitle = document.getElementById('chat-title');

// Settings
const targetLangSelect = document.getElementById('target-lang');
const levelSelect = document.getElementById('level');
const nativeLangSelect = document.getElementById('native-lang');

startBtn.addEventListener('click', async () => {
    const targetLang = targetLangSelect.value;
    const level = levelSelect.value;
    const nativeLang = nativeLangSelect.value;

    setLoading(true);
    addMessage('system', 'Starting your adventure...');

    try {
        const response = await fetch(`${API_URL}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                target_language: targetLang,
                level: level,
                native_language: nativeLang
            }),
        });

        if (!response.ok) throw new Error('Failed to start adventure');

        const data = await response.json();
        sessionId = data.session_id;
        
        // Clear previous messages except the first system one? No, clear all.
        messagesContainer.innerHTML = '';
        addMessage('agent', data.response);
        
        enableChat();
        chatTitle.textContent = `${targetLang} Adventure (${level})`;

    } catch (error) {
        console.error(error);
        addMessage('system', 'Error starting adventure. Please check if the backend is running.');
    } finally {
        setLoading(false);
    }
});

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text || !sessionId) return;

    addMessage('user', text);
    userInput.value = '';
    setLoading(true);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: sessionId,
                message: text,
                target_language: targetLangSelect.value,
                level: levelSelect.value,
                native_language: nativeLangSelect.value
            }),
        });

        if (!response.ok) throw new Error('Failed to send message');

        const data = await response.json();
        addMessage('agent', data.response);

    } catch (error) {
        console.error(error);
        addMessage('system', 'Error sending message.');
    } finally {
        setLoading(false);
        userInput.focus();
    }
}

function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `message ${role}`;
    
    // Parse Markdown if available
    if (window.marked && (role === 'agent' || role === 'system')) {
        div.innerHTML = marked.parse(text);
    } else {
        div.textContent = text;
    }

    messagesContainer.appendChild(div);
    scrollToBottom();
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function setLoading(isLoading) {
    if (isLoading) {
        startBtn.disabled = true;
        sendBtn.disabled = true;
        userInput.disabled = true;
        startBtn.textContent = 'Loading...';
    } else {
        startBtn.disabled = false;
        // Only enable chat inputs if session exists
        if (sessionId) {
            sendBtn.disabled = false;
            userInput.disabled = false;
        }
        startBtn.textContent = 'Start Adventure';
    }
}

function enableChat() {
    userInput.disabled = false;
    sendBtn.disabled = false;
    userInput.focus();
}
