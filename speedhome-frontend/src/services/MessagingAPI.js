class MessagingAPI {
    constructor() {
        this.baseURL = 'http://localhost:5001/api';
    }

    /**
     * Get all conversations for the current user
     */
    async getConversations() {
        try {
            const response = await fetch(`${this.baseURL}/conversations`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch conversations');
            }

            return data;
        } catch (error) {
            console.error('Error fetching conversations:', error);
            throw error;
        }
    }

    /**
     * Get messages for a specific conversation
     * @param {number} conversationId - The conversation ID
     * @param {number} page - Page number for pagination (default: 1)
     * @param {number} perPage - Messages per page (default: 50)
     */
    async getMessages(conversationId, page = 1, perPage = 50) {
        try {
            const response = await fetch(`${this.baseURL}/conversations/${conversationId}/messages?page=${page}&per_page=${perPage}`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch messages');
            }

            return data;
        } catch (error) {
            console.error('Error fetching messages:', error);
            throw error;
        }
    }

    /**
     * Send a new message in a conversation
     * @param {number} conversationId - The conversation ID
     * @param {string} messageBody - The message content
     * @param {string} messageType - The message type (default: 'text')
     */
    async sendMessage(conversationId, messageBody, messageType = 'text') {
        try {
            const response = await fetch(`${this.baseURL}/conversations/${conversationId}/messages`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_body: messageBody,
                    message_type: messageType
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to send message');
            }

            return data;
        } catch (error) {
            console.error('Error sending message:', error);
            throw error;
        }
    }

    /**
     * Create a new conversation for a booking
     * @param {number} bookingId - The booking ID
     */
    async createConversation(bookingId) {
        try {
            const response = await fetch(`${this.baseURL}/conversations/create`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    booking_id: bookingId
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to create conversation');
            }

            return data;
        } catch (error) {
            console.error('Error creating conversation:', error);
            throw error;
        }
    }

    /**
     * Get or create a conversation for a booking
     * @param {number} bookingId - The booking ID
     */
    // In src/services/MessagingAPI.js

    async getOrCreateConversation(bookingId) {
        try {
            // --- THIS IS THE FIX ---
            // The URL has been changed to the correct backend endpoint.
            const response = await fetch(`${this.baseURL}/conversations/create`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    booking_id: bookingId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to get or create conversation');
            }

            return data;
        } catch (error) {
            console.error('Error getting or creating conversation:', error);
            throw error;
        }
    }

    /**
     * Get a specific conversation by ID
     * @param {number} conversationId - The conversation ID
     */
    async getConversation(conversationId) {
        try {
            const response = await fetch(`${this.baseURL}/conversations/${conversationId}`, {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch conversation');
            }

            return data;
        } catch (error) {
            console.error('Error fetching conversation:', error);
            throw error;
        }
    }

    /**
     * Edit an existing message
     * @param {number} messageId - The message ID
     * @param {string} messageBody - The new message content
     */
    async editMessage(messageId, messageBody) {
        try {
            const response = await fetch(`${this.baseURL}/messages/${messageId}`, {
                method: 'PUT',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message_body: messageBody
                })
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to edit message');
            }

            return data;
        } catch (error) {
            console.error('Error editing message:', error);
            throw error;
        }
    }

    /**
     * Delete a message
     * @param {number} messageId - The message ID
     */
    async deleteMessage(messageId) {
        try {
            const response = await fetch(`${this.baseURL}/messages/${messageId}`, {
                method: 'DELETE',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Failed to delete message');
            }

            return data;
        } catch (error) {
            console.error('Error deleting message:', error);
            throw error;
        }
    }

    /**
     * Format timestamp for display
     * @param {string} timestamp - ISO timestamp string
     */
    formatTimestamp(timestamp) {
        if (!timestamp) return '';
        
        const date = new Date(timestamp);
        const now = new Date();
        const diffInHours = (now - date) / (1000 * 60 * 60);
        
        if (diffInHours < 1) {
            const diffInMinutes = Math.floor((now - date) / (1000 * 60));
            return diffInMinutes <= 1 ? 'Just now' : `${diffInMinutes}m ago`;
        } else if (diffInHours < 24) {
            return `${Math.floor(diffInHours)}h ago`;
        } else if (diffInHours < 48) {
            return 'Yesterday';
        } else {
            return date.toLocaleDateString();
        }
    }

    /**
     * Get conversation status display text
     * @param {string} status - Conversation status
     * @param {string} bookingStatus - Associated booking status
     */
    getStatusDisplay(status, bookingStatus) {
        if (status === 'read_only') {
            return `Read Only (${bookingStatus})`;
        }
        if (status === 'closed') {
            return 'Closed';
        }
        return 'Active';
    }

    /**
     * Mark all messages in a conversation as read for the current user
     * @param {number} conversationId - The conversation ID
     */
    async markConversationAsRead(conversationId) {
        try {
            const response = await fetch(`${this.baseURL}/conversations/${conversationId}/mark-read`, {
                method: 'POST',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                },
            });

            // It's possible the backend sends no content on success, which is fine
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.error || 'Failed to mark conversation as read');
            }

            // Return a simple success object if there's no data
            return await response.json().catch(() => ({ success: true }));

        } catch (error) {
            console.error('Error marking conversation as read:', error);
            throw error;
        }
    }
}

// Export singleton instance
const messagingAPI = new MessagingAPI();
export default messagingAPI;

