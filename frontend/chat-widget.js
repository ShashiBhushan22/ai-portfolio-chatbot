/**
 * AI Portfolio Chatbot Widget
 * Embeddable chat widget for portfolio websites
 * Author: Shashi Bhushan Jha
 */

const ChatWidget = (function() {
    let config = {
        apiUrl: 'http://localhost:8000',
        theme: 'dark',
        position: 'bottom-right',
        greeting: "Hi! I'm Shashi's AI Assistant. How can I help you today?",
        placeholder: 'Type your message...',
        title: "Shashi's AI Assistant"
    };

    let conversationHistory = [];
    let isOpen = false;
    let isLoading = false;

    /**
     * Initialize the chat widget
     */
    function init(options = {}) {
        config = { ...config, ...options };
        createWidget();
        attachEventListeners();
        console.log('🤖 Chat Widget initialized');
    }

    /**
     * Create the widget HTML structure
     */
    function createWidget() {
        const container = document.getElementById('chat-widget-container') || document.body;
        
        const widgetHTML = `
            <div id="chat-widget" class="chat-widget ${config.theme} ${config.position}">
                <!-- Toggle Button -->
                <button id="chat-toggle" class="chat-toggle" aria-label="Open chat">
                    <svg class="chat-icon" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                    </svg>
                    <svg class="close-icon hidden" viewBox="0 0 24 24" fill="currentColor">
                        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                    </svg>
                    <span class="notification-dot hidden"></span>
                </button>

                <!-- Chat Window -->
                <div id="chat-window" class="chat-window hidden">
                    <!-- Header -->
                    <div class="chat-header">
                        <div class="header-info">
                            <div class="avatar">🤖</div>
                            <div class="header-text">
                                <h3>${config.title}</h3>
                                <span class="status">Online</span>
                            </div>
                        </div>
                        <button id="chat-minimize" class="minimize-btn" aria-label="Minimize chat">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 13H5v-2h14v2z"/>
                            </svg>
                        </button>
                    </div>

                    <!-- Messages Container -->
                    <div id="chat-messages" class="chat-messages">
                        <!-- Greeting message -->
                        <div class="message bot">
                            <div class="message-content">${config.greeting}</div>
                            <div class="message-time">${getCurrentTime()}</div>
                        </div>
                        
                        <!-- Quick Actions -->
                        <div class="quick-actions">
                            <button class="quick-action" data-message="What are your key technical skills?">
                                💡 Technical Skills
                            </button>
                            <button class="quick-action" data-message="Tell me about your projects">
                                🚀 Projects
                            </button>
                            <button class="quick-action" data-message="How can I contact you?">
                                📬 Contact Info
                            </button>
                        </div>
                    </div>

                    <!-- Input Area -->
                    <div class="chat-input-area">
                        <form id="chat-form" class="chat-form">
                            <input 
                                type="text" 
                                id="chat-input" 
                                class="chat-input" 
                                placeholder="${config.placeholder}"
                                autocomplete="off"
                            />
                            <button type="submit" id="chat-send" class="send-btn" disabled>
                                <svg viewBox="0 0 24 24" fill="currentColor">
                                    <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
                                </svg>
                            </button>
                        </form>
                        <div class="powered-by">
                            Powered by AI ✨
                        </div>
                    </div>
                </div>
            </div>
        `;

        if (container.id === 'chat-widget-container') {
            container.innerHTML = widgetHTML;
        } else {
            container.insertAdjacentHTML('beforeend', widgetHTML);
        }
    }

    /**
     * Attach event listeners
     */
    function attachEventListeners() {
        // Toggle button
        document.getElementById('chat-toggle').addEventListener('click', toggleChat);
        document.getElementById('chat-minimize').addEventListener('click', toggleChat);

        // Form submission
        document.getElementById('chat-form').addEventListener('submit', handleSubmit);

        // Input change
        const input = document.getElementById('chat-input');
        input.addEventListener('input', () => {
            document.getElementById('chat-send').disabled = !input.value.trim();
        });

        // Quick actions
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => {
                const message = btn.dataset.message;
                sendMessage(message);
                // Hide quick actions after first use
                document.querySelector('.quick-actions').style.display = 'none';
            });
        });

        // Enter key to send
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                if (input.value.trim()) {
                    handleSubmit(e);
                }
            }
        });
    }

    /**
     * Toggle chat window visibility
     */
    function toggleChat() {
        isOpen = !isOpen;
        const chatWindow = document.getElementById('chat-window');
        const chatIcon = document.querySelector('.chat-icon');
        const closeIcon = document.querySelector('.close-icon');
        const notificationDot = document.querySelector('.notification-dot');

        if (isOpen) {
            chatWindow.classList.remove('hidden');
            chatIcon.classList.add('hidden');
            closeIcon.classList.remove('hidden');
            notificationDot.classList.add('hidden');
            document.getElementById('chat-input').focus();
        } else {
            chatWindow.classList.add('hidden');
            chatIcon.classList.remove('hidden');
            closeIcon.classList.add('hidden');
        }
    }

    /**
     * Handle form submission
     */
    function handleSubmit(e) {
        e.preventDefault();
        const input = document.getElementById('chat-input');
        const message = input.value.trim();
        
        if (message && !isLoading) {
            sendMessage(message);
            input.value = '';
            document.getElementById('chat-send').disabled = true;
        }
    }

    /**
     * Send message to the API
     */
    async function sendMessage(message) {
        if (isLoading) return;
        
        // Add user message to UI
        addMessage(message, 'user');
        
        // Add to conversation history
        conversationHistory.push({ role: 'user', content: message });

        // Show loading indicator
        isLoading = true;
        const loadingId = showLoading();

        try {
            const response = await fetch(`${config.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    conversation_history: conversationHistory.slice(-10) // Keep last 10 messages
                })
            });

            removeLoading(loadingId);

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            
            // Add bot response to UI
            addMessage(data.response, 'bot');
            
            // Add to conversation history
            conversationHistory.push({ role: 'assistant', content: data.response });

        } catch (error) {
            console.error('Chat error:', error);
            removeLoading(loadingId);
            addMessage(
                "I'm sorry, I'm having trouble connecting right now. Please try again later.",
                'bot',
                true
            );
        } finally {
            isLoading = false;
        }
    }

    /**
     * Add a message to the chat UI
     */
    function addMessage(content, sender, isError = false) {
        const messagesContainer = document.getElementById('chat-messages');
        
        const messageHTML = `
            <div class="message ${sender} ${isError ? 'error' : ''}">
                <div class="message-content">${escapeHtml(content)}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
        
        messagesContainer.insertAdjacentHTML('beforeend', messageHTML);
        scrollToBottom();
    }

    /**
     * Show loading indicator
     */
    function showLoading() {
        const messagesContainer = document.getElementById('chat-messages');
        const loadingId = 'loading-' + Date.now();
        
        const loadingHTML = `
            <div id="${loadingId}" class="message bot loading">
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        `;
        
        messagesContainer.insertAdjacentHTML('beforeend', loadingHTML);
        scrollToBottom();
        
        return loadingId;
    }

    /**
     * Remove loading indicator
     */
    function removeLoading(loadingId) {
        const loadingElement = document.getElementById(loadingId);
        if (loadingElement) {
            loadingElement.remove();
        }
    }

    /**
     * Scroll chat to bottom
     */
    function scrollToBottom() {
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    /**
     * Get current time string
     */
    function getCurrentTime() {
        return new Date().toLocaleTimeString([], { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * Clear conversation history
     */
    function clearHistory() {
        conversationHistory = [];
        const messagesContainer = document.getElementById('chat-messages');
        messagesContainer.innerHTML = `
            <div class="message bot">
                <div class="message-content">${config.greeting}</div>
                <div class="message-time">${getCurrentTime()}</div>
            </div>
        `;
    }

    // Public API
    return {
        init,
        toggleChat,
        clearHistory,
        sendMessage
    };
})();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatWidget;
}
