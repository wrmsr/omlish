/**
 * Chat Application Module
 *
 * Main Alpine.js application logic for the chat interface.
 */

/**
 * Creates the main chat application Alpine.js component.
 */
window.chatApp = function() {
    return {
        messages: [],
        userInput: '',
        isLoading: false,
        abortController: null,
        pendingUserMessage: '',
        messageStartIndex: -1,

        /**
         * Initialize the application
         */
        init() {
            // Configure marked.js options
            if (window.marked) {
                marked.setOptions({
                    breaks: true,
                    gfm: true
                });
            }

            // Auto-resize textarea on input
            this.$watch('userInput', () => {
                this.autoResizeTextarea();
            });

            // Add keyboard shortcut for canceling (Escape key)
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isLoading) {
                    this.cancelRequest();
                }
            });

            // Load any saved messages from localStorage
            this.loadMessages();
        },

        /**
         * Render markdown content to HTML
         */
        renderMarkdown(content) {
            if (!content) return '';

            if (window.marked) {
                return marked.parse(content);
            }

            // Fallback if marked.js fails to load
            return content.replace(/\n/g, '<br>');
        },

        /**
         * Auto-resize the textarea based on content
         */
        autoResizeTextarea() {
            const textarea = this.$refs.input;
            if (!textarea) return;

            // Reset height to auto to get the correct scrollHeight
            textarea.style.height = 'auto';

            // Set height based on scrollHeight
            const newHeight = Math.min(textarea.scrollHeight, 200);
            textarea.style.height = newHeight + 'px';
        },

        /**
         * Handle Enter key press (send message on Enter, newline on Shift+Enter)
         */
        handleEnter(event) {
            if (event.shiftKey) {
                // Allow default behavior (newline)
                return;
            }

            // Send message on Enter without Shift
            event.preventDefault();
            this.sendMessage();
        },

        /**
         * Scroll to the bottom of the messages container
         */
        scrollToBottom() {
            this.$nextTick(() => {
                const container = this.$refs.messagesContainer;
                if (container) {
                    container.scrollTop = container.scrollHeight;
                }
            });
        },

        /**
         * Send a chat message
         */
        async sendMessage() {
            const message = this.userInput.trim();

            if (!message || this.isLoading) {
                return;
            }

            // Store the original message and starting index for potential cancellation
            this.pendingUserMessage = message;
            this.messageStartIndex = this.messages.length;

            // Add user message
            this.messages.push({
                role: 'user',
                content: message
            });

            // Clear input
            this.userInput = '';
            this.autoResizeTextarea();

            // Set loading state and create abort controller
            this.isLoading = true;
            this.abortController = new AbortController();

            // Scroll to bottom
            this.scrollToBottom();

            // Initialize assistant message
            const assistantMessage = {
                role: 'assistant',
                content: ''
            };

            this.messages.push(assistantMessage);
            const messageIndex = this.messages.length - 1;

            try {
                // Prepare messages for API (only role and content)
                const apiMessages = this.messages.map(msg => ({
                    role: msg.role,
                    content: msg.content
                }));

                // Scroll to show assistant message
                this.scrollToBottom();

                // Stream the response
                await window.fetchSSEStream(
                    '/v1/chat/completions',
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            messages: apiMessages,
                            model: 'gpt-3.5-turbo',
                            stream: true
                        }),
                        signal: this.abortController.signal
                    },
                    async (chunk) => {
                        // Handle error chunks
                        if (chunk.error) {
                            console.error('API Error:', chunk.error);
                            this.messages[messageIndex].content += '\n\n[Error: ' + chunk.error.message + ']';
                            // Trigger reactivity
                            this.messages = [...this.messages];
                            return;
                        }

                        // Extract content from chunk
                        if (chunk.choices && chunk.choices[0]) {
                            const delta = chunk.choices[0].delta;

                            if (delta && delta.content) {
                                this.messages[messageIndex].content += delta.content;
                                // Trigger reactivity by reassigning the array
                                this.messages = [...this.messages];

                                // Scroll to bottom as content arrives
                                this.scrollToBottom();
                            }
                        }
                    }
                );

                // Save messages to localStorage
                this.saveMessages();

            } catch (error) {
                // Check if this was an abort (cancellation)
                if (error.name === 'AbortError') {
                    console.log('Request cancelled by user');
                    // Cancellation is handled by the cancel() method
                    return;
                }

                console.error('Failed to send message:', error);

                // Add error message
                if (this.messages[messageIndex]) {
                    this.messages[messageIndex].content += '\n\n[Error: Failed to communicate with server]';
                    this.messages = [...this.messages];
                }
            } finally {
                this.isLoading = false;
                this.abortController = null;
                this.pendingUserMessage = '';
                this.messageStartIndex = -1;
                this.scrollToBottom();
            }
        },

        /**
         * Cancel the current streaming request
         */
        cancelRequest() {
            if (!this.isLoading || !this.abortController) {
                return;
            }

            // Abort the fetch request
            this.abortController.abort();

            // Remove the user and assistant messages that were just added
            if (this.messageStartIndex >= 0) {
                this.messages = this.messages.slice(0, this.messageStartIndex);
            }

            // Restore the original message to the input
            this.userInput = this.pendingUserMessage;
            this.autoResizeTextarea();

            // Reset state
            this.isLoading = false;
            this.abortController = null;
            this.pendingUserMessage = '';
            this.messageStartIndex = -1;

            // Focus the input
            this.$nextTick(() => {
                this.$refs.input.focus();
            });
        },

        /**
         * Save messages to localStorage
         */
        saveMessages() {
            try {
                localStorage.setItem('vibechat_messages', JSON.stringify(this.messages));
            } catch (e) {
                console.error('Failed to save messages:', e);
            }
        },

        /**
         * Load messages from localStorage
         */
        loadMessages() {
            try {
                const saved = localStorage.getItem('vibechat_messages');
                if (saved) {
                    this.messages = JSON.parse(saved);
                    this.scrollToBottom();
                }
            } catch (e) {
                console.error('Failed to load messages:', e);
            }
        },

        /**
         * Clear all messages
         */
        clearMessages() {
            this.messages = [];
            this.saveMessages();
        }
    };
};
