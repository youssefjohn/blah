import React, { useState, useEffect, useRef } from 'react';
import MessagingAPI from '../services/MessagingAPI';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';
import './ChatWindow.css';

const ChatWindow = ({ conversation, currentUser, onBack, onMessageSent }) => {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef(null);

    useEffect(() => {
        if (conversation?.id) {
            loadMessages();
        }
    }, [conversation?.id]);

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const loadMessages = async () => {
        try {
            setLoading(true);
            const response = await MessagingAPI.getMessages(conversation.id);
            setMessages(response.messages || []);
            setError(null);
        } catch (error) {
            console.error('Error loading messages:', error);
            setError('Failed to load messages');
        } finally {
            setLoading(false);
        }
    };

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const handleSendMessage = async (messageText) => {
        if (!messageText.trim() || sending) return;

        try {
            setSending(true);
            const response = await MessagingAPI.sendMessage(conversation.id, messageText.trim());
            
            // Add the new message to the list
            setMessages(prev => [...prev, response.message]);
            
            // Notify parent component
            onMessageSent();
            
        } catch (error) {
            console.error('Error sending message:', error);
            alert('Failed to send message: ' + error.message);
        } finally {
            setSending(false);
        }
    };

    const getOtherParticipant = () => {
        if (currentUser?.role === 'landlord') {
            return {
                name: conversation.tenant_name || 'Tenant',
                role: 'tenant'
            };
        } else {
            return {
                name: conversation.landlord_name || 'Landlord',
                role: 'landlord'
            };
        }
    };

    const getConversationStatus = () => {
        return MessagingAPI.getStatusDisplay(conversation.status, conversation.booking_status);
    };

    const canSendMessages = () => {
        return conversation.status === 'active' && 
               ['pending', 'confirmed'].includes(conversation.booking_status);
    };

    const otherParticipant = getOtherParticipant();

    return (
        <div className="chat-window">
            {/* Chat Header */}
            <div className="chat-header">
                <button className="back-button" onClick={onBack}>
                    ← Back
                </button>
                
                <div className="chat-header-info">
                    <div className="participant-info">
                        <div className="participant-avatar">
                            {otherParticipant.name.charAt(0).toUpperCase()}
                        </div>
                        <div className="participant-details">
                            <h3 className="participant-name">{otherParticipant.name}</h3>
                            <p className="property-info">📍 {conversation.property_title}</p>
                        </div>
                    </div>
                    
                    <div className="conversation-status">
                        <span className={`status-badge status-${conversation.status}`}>
                            {getConversationStatus()}
                        </span>
                    </div>
                </div>
            </div>

            {/* Messages Area */}
            <div className="messages-container">
                {loading ? (
                    <div className="messages-loading">
                        <div className="loading-spinner"></div>
                        <p>Loading messages...</p>
                    </div>
                ) : error ? (
                    <div className="messages-error">
                        <p>❌ {error}</p>
                        <button onClick={loadMessages} className="retry-button">
                            Try Again
                        </button>
                    </div>
                ) : messages.length === 0 ? (
                    <div className="no-messages">
                        <div className="no-messages-icon">💬</div>
                        <h4>Start the conversation</h4>
                        <p>Send a message to {otherParticipant.name} about {conversation.property_title}</p>
                    </div>
                ) : (
                    <div className="messages-list">
                        {messages.map((message) => (
                            <MessageBubble
                                key={message.id}
                                message={message}
                                isOwn={message.sender_id === currentUser?.id}
                                currentUser={currentUser}
                            />
                        ))}
                        <div ref={messagesEndRef} />
                    </div>
                )}
            </div>

            {/* Message Input */}
            <div className="message-input-container">
                {canSendMessages() ? (
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        disabled={sending}
                        placeholder={`Message ${otherParticipant.name}...`}
                    />
                ) : (
                    <div className="messaging-disabled">
                        <p>
                            {conversation.status === 'read_only' 
                                ? `This conversation is read-only because the booking is ${conversation.booking_status}.`
                                : 'Messaging is not available for this conversation.'
                            }
                        </p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatWindow;

