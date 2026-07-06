"""
Built-in chatbot UI — a beautiful chat interface served at /.

Users can have multi-turn conversations with the AI Career Mentor
directly from their browser. No separate frontend needed.
"""

CHAT_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Career Mentor — Chat</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0e1a;
            --bg-secondary: #111827;
            --bg-chat: #0d1220;
            --bg-user-msg: #1e3a5f;
            --bg-bot-msg: #1a1f2e;
            --border: #1e293b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-muted: #64748b;
            --accent-blue: #3b82f6;
            --accent-purple: #8b5cf6;
            --accent-green: #10b981;
            --accent-cyan: #06b6d4;
            --gradient-blue: linear-gradient(135deg, #3b82f6, #8b5cf6);
            --gradient-send: linear-gradient(135deg, #3b82f6, #06b6d4);
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }

        /* ── Header ──────────────────────────────────── */
        .header {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 0.9rem 1.5rem;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-shrink: 0;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .header-logo {
            width: 40px;
            height: 40px;
            background: var(--gradient-blue);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.3rem;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .header-info h1 {
            font-size: 1rem;
            font-weight: 600;
            letter-spacing: -0.01em;
        }

        .header-info p {
            font-size: 0.72rem;
            color: var(--text-muted);
            margin-top: 0.1rem;
        }

        .header-right {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .header-btn {
            background: rgba(255,255,255,0.06);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.78rem;
            font-family: 'Inter', sans-serif;
            padding: 0.45rem 0.9rem;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .header-btn:hover {
            background: rgba(255,255,255,0.1);
            color: var(--text-primary);
            border-color: rgba(255,255,255,0.15);
        }

        .session-badge {
            font-size: 0.68rem;
            color: var(--accent-cyan);
            background: rgba(6, 182, 212, 0.1);
            border: 1px solid rgba(6, 182, 212, 0.2);
            padding: 0.3rem 0.65rem;
            border-radius: 14px;
            font-weight: 500;
        }

        /* ── Chat Area ───────────────────────────────── */
        .chat-area {
            flex: 1;
            overflow-y: auto;
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            scroll-behavior: smooth;
        }

        .chat-area::-webkit-scrollbar { width: 5px; }
        .chat-area::-webkit-scrollbar-track { background: transparent; }
        .chat-area::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

        /* ── Welcome Screen ──────────────────────────── */
        .welcome {
            flex: 1;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            gap: 1.25rem;
            padding: 2rem;
        }

        .welcome-icon {
            width: 72px;
            height: 72px;
            background: var(--gradient-blue);
            border-radius: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2rem;
            box-shadow: 0 8px 30px rgba(59, 130, 246, 0.25);
        }

        .welcome h2 {
            font-size: 1.35rem;
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        .welcome p {
            color: var(--text-secondary);
            font-size: 0.88rem;
            max-width: 420px;
            line-height: 1.6;
        }

        .suggestions {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            justify-content: center;
            margin-top: 0.5rem;
        }

        .suggestion {
            background: rgba(255,255,255,0.04);
            border: 1px solid var(--border);
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 0.8rem;
            padding: 0.55rem 1rem;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .suggestion:hover {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
            color: var(--accent-blue);
            transform: translateY(-1px);
        }

        /* ── Messages ────────────────────────────────── */
        .message {
            display: flex;
            gap: 0.75rem;
            max-width: 85%;
            animation: msgIn 0.3s ease-out;
        }

        @keyframes msgIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .message.user {
            align-self: flex-end;
            flex-direction: row-reverse;
        }

        .message.bot {
            align-self: flex-start;
        }

        .msg-avatar {
            width: 34px;
            height: 34px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.9rem;
            flex-shrink: 0;
            margin-top: 2px;
        }

        .message.user .msg-avatar {
            background: linear-gradient(135deg, #8b5cf6, #ec4899);
        }

        .message.bot .msg-avatar {
            background: var(--gradient-blue);
        }

        .msg-content {
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
        }

        .msg-bubble {
            padding: 0.85rem 1.1rem;
            border-radius: 16px;
            font-size: 0.88rem;
            line-height: 1.65;
            word-wrap: break-word;
        }

        .message.user .msg-bubble {
            background: var(--bg-user-msg);
            border-bottom-right-radius: 4px;
            color: var(--text-primary);
        }

        .message.bot .msg-bubble {
            background: var(--bg-bot-msg);
            border: 1px solid var(--border);
            border-bottom-left-radius: 4px;
            color: var(--text-primary);
        }

        .msg-meta {
            font-size: 0.68rem;
            color: var(--text-muted);
            display: flex;
            gap: 0.75rem;
            padding: 0 0.25rem;
        }

        .message.user .msg-meta {
            justify-content: flex-end;
        }

        .msg-meta .tag {
            background: rgba(255,255,255,0.05);
            padding: 0.1rem 0.4rem;
            border-radius: 4px;
        }

        /* ── Typing Indicator ────────────────────────── */
        .typing-indicator {
            display: none;
            align-self: flex-start;
            gap: 0.75rem;
            max-width: 85%;
        }

        .typing-indicator.active { display: flex; }

        .typing-dots {
            display: flex;
            gap: 4px;
            padding: 1rem 1.2rem;
            background: var(--bg-bot-msg);
            border: 1px solid var(--border);
            border-radius: 16px;
            border-bottom-left-radius: 4px;
        }

        .typing-dots span {
            width: 7px;
            height: 7px;
            background: var(--text-muted);
            border-radius: 50%;
            animation: bounce 1.4s infinite;
        }

        .typing-dots span:nth-child(2) { animation-delay: 0.2s; }
        .typing-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes bounce {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-6px); }
        }

        /* ── Input Area ──────────────────────────────── */
        .input-area {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 1rem 1.5rem;
            flex-shrink: 0;
        }

        .input-container {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 0.75rem;
            align-items: flex-end;
        }

        .input-wrapper {
            flex: 1;
            position: relative;
        }

        #message-input {
            width: 100%;
            padding: 0.85rem 1.1rem;
            background: var(--bg-primary);
            border: 1px solid var(--border);
            border-radius: 14px;
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 0.9rem;
            outline: none;
            resize: none;
            min-height: 48px;
            max-height: 150px;
            line-height: 1.5;
            transition: border-color 0.2s ease;
        }

        #message-input:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        #message-input::placeholder {
            color: var(--text-muted);
        }

        .send-btn {
            width: 48px;
            height: 48px;
            background: var(--gradient-send);
            border: none;
            border-radius: 14px;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
            flex-shrink: 0;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
        }

        .send-btn:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
        }

        .send-btn:active {
            transform: scale(0.95);
        }

        .send-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        .input-hint {
            text-align: center;
            font-size: 0.7rem;
            color: var(--text-muted);
            margin-top: 0.5rem;
        }

        /* ── Markdown in bot messages ────────────────── */
        .msg-bubble ul, .msg-bubble ol {
            padding-left: 1.25rem;
            margin: 0.5rem 0;
        }

        .msg-bubble li {
            margin-bottom: 0.3rem;
        }

        .msg-bubble strong {
            color: var(--accent-cyan);
            font-weight: 600;
        }

        .msg-bubble code {
            background: rgba(255,255,255,0.08);
            padding: 0.15rem 0.4rem;
            border-radius: 4px;
            font-size: 0.82rem;
        }

        .msg-bubble p {
            margin-bottom: 0.5rem;
        }

        .msg-bubble p:last-child {
            margin-bottom: 0;
        }

        /* ── Responsive ──────────────────────────────── */
        @media (max-width: 600px) {
            .message { max-width: 95%; }
            .header { padding: 0.75rem 1rem; }
            .chat-area { padding: 1rem; }
            .input-area { padding: 0.75rem 1rem; }
            .suggestions { flex-direction: column; align-items: center; }
            .header-right .header-btn span.btn-text { display: none; }
        }
    </style>
</head>
<body>
    <!-- Header -->
    <div class="header">
        <div class="header-left">
            <div class="header-logo">🤖</div>
            <div class="header-info">
                <h1>AI Career Mentor</h1>
                <p>Powered by DeepSeek · Traced by LangSmith</p>
            </div>
        </div>
        <div class="header-right">
            <span class="session-badge" id="session-info">New Session</span>
            <a href="/dashboard" class="header-btn" title="Monitoring Dashboard">
                📊 <span class="btn-text">Dashboard</span>
            </a>
            <button class="header-btn" onclick="newSession()" title="Start new conversation">
                ✨ <span class="btn-text">New Chat</span>
            </button>
        </div>
    </div>

    <!-- Chat Area -->
    <div class="chat-area" id="chat-area">
        <!-- Welcome Screen -->
        <div class="welcome" id="welcome-screen">
            <div class="welcome-icon">🎯</div>
            <h2>Your AI Career Mentor</h2>
            <p>I help you navigate your tech career — from choosing technologies to planning your growth path. Tell me about your background and I'll give personalized advice.</p>
            <div class="suggestions">
                <button class="suggestion" onclick="sendSuggestion(this)">I'm a Python developer with 2 years of experience</button>
                <button class="suggestion" onclick="sendSuggestion(this)">Help me plan my career in data science</button>
                <button class="suggestion" onclick="sendSuggestion(this)">What cloud certifications should I pursue?</button>
                <button class="suggestion" onclick="sendSuggestion(this)">I want to transition from frontend to backend</button>
            </div>
        </div>

        <!-- Typing Indicator -->
        <div class="typing-indicator" id="typing-indicator">
            <div class="msg-avatar" style="background:var(--gradient-blue)">🤖</div>
            <div class="typing-dots">
                <span></span><span></span><span></span>
            </div>
        </div>
    </div>

    <!-- Input Area -->
    <div class="input-area">
        <div class="input-container">
            <div class="input-wrapper">
                <textarea
                    id="message-input"
                    placeholder="Tell me about your background, skills, or career goals..."
                    rows="1"
                    onkeydown="handleKeydown(event)"
                    oninput="autoResize(this)"
                ></textarea>
            </div>
            <button class="send-btn" id="send-btn" onclick="sendMessage()" title="Send message">
                ➤
            </button>
        </div>
        <div class="input-hint">Press Enter to send · Shift+Enter for new line</div>
    </div>

    <script>
        let sessionId = null;
        let messageCount = 0;

        // ── Send Message ────────────────────────────────
        async function sendMessage() {
            console.log("sendMessage triggered!");
            const input = document.getElementById('message-input');
            const message = input.value.trim();
            console.log("Message extracted:", message);
            
            if (!message) {
                console.log("Message is empty, returning.");
                return;
            }

            try {
                // Hide welcome screen
                const welcome = document.getElementById('welcome-screen');
                if (welcome) welcome.remove();

                // Add user message to chat
                console.log("Adding user message to UI...");
                addMessage('user', message);
                input.value = '';
                autoResize(input);

                // Show typing indicator
                const typing = document.getElementById('typing-indicator');
                if(typing) typing.classList.add('active');
                scrollToBottom();

                // Disable input
                const sendBtn = document.getElementById('send-btn');
                if(sendBtn) sendBtn.disabled = true;
                if(input) input.disabled = true;

                const body = { message };
                if (sessionId) body.session_id = sessionId;

                console.log("Sending POST request to /chat/stream with body:", body);
                const res = await fetch('/chat/stream', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(body),
                });

                if (!res.ok) {
                    const data = await res.json();
                    throw new Error(data.detail || 'Request failed');
                }

                // Add empty bot message bubble to fill dynamically
                const msgId = 'msg-' + Date.now();
                addMessage('bot', '', null, false, msgId);
                const bubble = document.getElementById(msgId);
                let fullText = "";

                // Hide typing indicator once stream starts
                if(typing) typing.classList.remove('active');

                // Read stream chunks
                const reader = res.body.getReader();
                const decoder = new TextDecoder("utf-8");
                let buffer = "";

                while (true) {
                    const { done, value } = await reader.read();
                    if (done) break;
                    
                    buffer += decoder.decode(value, { stream: true });
                    const lines = buffer.split('\n');
                    buffer = lines.pop(); // Keep incomplete line in buffer

                    for (const line of lines) {
                        if (line.startsWith('data: ')) {
                            const data = JSON.parse(line.substring(6));
                            
                            if (data.type === 'chunk') {
                                fullText += data.text;
                                bubble.innerHTML = formatMarkdown(fullText);
                                scrollToBottom();
                            } else if (data.type === 'metadata') {
                                sessionId = data.session_id;
                                messageCount++;
                                updateSessionBadge();
                                
                                // Append metadata tags below bubble
                                const metaHtml = `
                                    <div class="msg-meta">
                                        <span class="tag">⏱ ${data.metadata.latency_seconds}s</span>
                                        <span class="tag">🔢 ${data.metadata.token_usage.total_tokens} tokens</span>
                                        <span class="tag">💰 $${data.metadata.estimated_cost_usd.toFixed(6)}</span>
                                    </div>`;
                                bubble.parentElement.insertAdjacentHTML('beforeend', metaHtml);
                            } else if (data.type === 'error') {
                                throw new Error(data.error);
                            }
                        }
                    }
                }

            } catch (err) {
                console.error("Error inside sendMessage:", err);
                const typing = document.getElementById('typing-indicator');
                if(typing) typing.classList.remove('active');
                addMessage('bot', `⚠️ Error: ${err.message}. Please try again.`, null, true);
            } finally {
                const sendBtn = document.getElementById('send-btn');
                const input = document.getElementById('message-input');
                if(sendBtn) sendBtn.disabled = false;
                if(input) input.disabled = false;
                if(input) input.focus();
                console.log("sendMessage finished cleanup.");
            }
        }

        // ── Add Message to Chat ─────────────────────────
        function addMessage(role, text, metadata = null, isError = false, msgId = null) {
            const chatArea = document.getElementById('chat-area');
            const typing = document.getElementById('typing-indicator');

            const msgDiv = document.createElement('div');
            msgDiv.className = `message ${role}`;

            const avatar = role === 'user' ? '👤' : '🤖';
            const formattedText = role === 'bot' ? formatMarkdown(text) : escapeHtml(text);

            let metaHtml = '';
            if (metadata && role === 'bot') {
                metaHtml = `
                    <div class="msg-meta">
                        <span class="tag">⏱ ${metadata.latency_seconds}s</span>
                        <span class="tag">🔢 ${metadata.token_usage.total_tokens} tokens</span>
                        <span class="tag">💰 $${metadata.estimated_cost_usd.toFixed(6)}</span>
                    </div>`;
            }

            msgDiv.innerHTML = `
                <div class="msg-avatar">${avatar}</div>
                <div class="msg-content">
                    <div class="msg-bubble${isError ? ' error' : ''}" ${msgId ? 'id="'+msgId+'"' : ''}>${formattedText}</div>
                    ${metaHtml}
                </div>
            `;

            chatArea.insertBefore(msgDiv, typing);
            scrollToBottom();
        }

        // ── Format Markdown (basic) ─────────────────────
        function formatMarkdown(text) {
            // Escape HTML first
            let html = escapeHtml(text);

            // Bold: **text**
            html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

            // Inline code: `text`
            html = html.replace(/`(.+?)`/g, '<code>$1</code>');

            // Unordered lists: - item or * item
            html = html.replace(/^[\-\*]\s+(.+)$/gm, '<li>$1</li>');

            // Numbered lists: 1. item
            html = html.replace(/^\d+\.\s+(.+)$/gm, '<li>$1</li>');

            // Wrap consecutive <li> in <ul>
            html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>');

            // Paragraphs: double newline
            html = html.replace(/\n\n/g, '</p><p>');
            html = '<p>' + html + '</p>';

            // Single newlines within paragraphs
            html = html.replace(/\n/g, '<br>');

            // Clean up empty paragraphs
            html = html.replace(/<p><\/p>/g, '');
            html = html.replace(/<p><br>/g, '<p>');

            return html;
        }

        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }

        // ── Helpers ─────────────────────────────────────
        function scrollToBottom() {
            const chatArea = document.getElementById('chat-area');
            setTimeout(() => {
                chatArea.scrollTop = chatArea.scrollHeight;
            }, 50);
        }

        function handleKeydown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        function autoResize(el) {
            el.style.height = 'auto';
            el.style.height = Math.min(el.scrollHeight, 150) + 'px';
        }

        function sendSuggestion(btn) {
            document.getElementById('message-input').value = btn.textContent;
            sendMessage();
        }

        function newSession() {
            sessionId = null;
            messageCount = 0;
            updateSessionBadge();

            const chatArea = document.getElementById('chat-area');
            const typing = document.getElementById('typing-indicator');

            // Remove all messages
            chatArea.innerHTML = '';

            // Re-add welcome screen
            chatArea.innerHTML = `
                <div class="welcome" id="welcome-screen">
                    <div class="welcome-icon">🎯</div>
                    <h2>Your AI Career Mentor</h2>
                    <p>I help you navigate your tech career — from choosing technologies to planning your growth path. Tell me about your background and I'll give personalized advice.</p>
                    <div class="suggestions">
                        <button class="suggestion" onclick="sendSuggestion(this)">I'm a Python developer with 2 years of experience</button>
                        <button class="suggestion" onclick="sendSuggestion(this)">Help me plan my career in data science</button>
                        <button class="suggestion" onclick="sendSuggestion(this)">What cloud certifications should I pursue?</button>
                        <button class="suggestion" onclick="sendSuggestion(this)">I want to transition from frontend to backend</button>
                    </div>
                </div>
                <div class="typing-indicator" id="typing-indicator">
                    <div class="msg-avatar" style="background:var(--gradient-blue)">🤖</div>
                    <div class="typing-dots">
                        <span></span><span></span><span></span>
                    </div>
                </div>
            `;

            document.getElementById('message-input').focus();
        }

        function updateSessionBadge() {
            const badge = document.getElementById('session-info');
            if (sessionId) {
                badge.textContent = `Session: ${sessionId.substring(0, 8)}... · ${messageCount} msg${messageCount !== 1 ? 's' : ''}`;
            } else {
                badge.textContent = 'New Session';
            }
        }

        // Focus input on load
        document.getElementById('message-input').focus();
    </script>
</body>
</html>"""
