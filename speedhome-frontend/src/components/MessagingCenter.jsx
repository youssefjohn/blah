import React, { useState, useEffect } from 'react';
import MessagingAPI from '../services/MessagingAPI';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import './MessagingCenter.css';

const MessagingCenter = ({ user }) => {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadConversations();
    }, []);

    const loadConversations = async () => {
        try {
            setLoading(true);
            const response = await MessagingAPI.getConversations();
            setConversations(response.conversations || []);
            setError(null);
        } catch (error) {
            console.error('Error loading conversations:', error);
            setError('Failed to load conversations');
        } finally {
            setLoading(false);
        }
    };

    const handleConversationSelect = (conversation) => {
        setSelectedConversation(conversation);
    };

    const handleMessageSent = () => {
        // Refresh conversations to update last message info
        loadConversations();
        
        // If we have a selected conversation, we might want to refresh its messages
        // This will be handled by the ChatWindow component
    };

    const handleBackToList = () => {
        setSelectedConversation(null);
        loadConversations(); // Refresh the list when going back
    };

    if (loading) {
        return (
            <div className="messaging-center">
                <div className="messaging-loading">
                    <div className="loading-spinner"></div>
                    <p>Loading conversations...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="messaging-center">
                <div className="messaging-error">
                    <p>❌ {error}</p>
                    <button onClick={loadConversations} className="retry-button">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="messaging-center">
            <div className="messaging-header">
                <h2>💬 Messages</h2>
                <p className="messaging-subtitle">
                    {user?.role === 'landlord' ? 'Chat with your tenants' : 'Chat with landlords'}
                </p>
            </div>

            <div className="messaging-content">
                {!selectedConversation ? (
                    <ConversationList
                        conversations={conversations}
                        onConversationSelect={handleConversationSelect}
                        currentUser={user}
                    />
                ) : (
                    <ChatWindow
                        conversation={selectedConversation}
                        currentUser={user}
                        onBack={handleBackToList}
                        onMessageSent={handleMessageSent}
                    />
                )}
            </div>

            {conversations.length === 0 && !loading && (
                <div className="no-conversations">
                    <div className="no-conversations-icon">💬</div>
                    <h3>No conversations yet</h3>
                    <p>
                        {user?.role === 'landlord' 
                            ? 'Conversations will appear here when tenants book viewings for your properties.'
                            : 'Start a conversation by booking a property viewing. You can message the landlord once your booking is submitted.'
                        }
                    </p>
                </div>
            )}
        </div>
    );
};

export default MessagingCenter;

