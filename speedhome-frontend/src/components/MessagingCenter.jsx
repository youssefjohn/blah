import React, { useState, useEffect } from 'react';
import MessagingAPI from '../services/MessagingAPI';
import ConversationList from './ConversationList';
import ChatWindow from './ChatWindow';
import './MessagingCenter.css';

const MessagingCenter = ({ user, selectedConversationId, onConversationSelect }) => {
    const [conversations, setConversations] = useState([]);
    const [selectedConversation, setSelectedConversation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        loadConversations();
    }, []);

    // Handle external conversation selection
    useEffect(() => {
        if (selectedConversationId && conversations.length > 0) {
            const conversation = conversations.find(c => c.id === selectedConversationId);
            if (conversation) {
                setSelectedConversation(conversation);
            }
        }
    }, [selectedConversationId, conversations]);

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
        if (onConversationSelect) {
            onConversationSelect(conversation.id);
        }
    };

    const handleMessageSent = () => {
        // Refresh conversations to update last message info
        loadConversations();
    };

    if (loading) {
        return (
            <div className="messaging-center h-full flex items-center justify-center">
                <div className="text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading conversations...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="messaging-center h-full flex items-center justify-center">
                <div className="text-center">
                    <div className="text-red-500 text-4xl mb-4">❌</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Failed to load conversations</h3>
                    <p className="text-gray-500 mb-4">{error}</p>
                    <button 
                        onClick={loadConversations}
                        className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors"
                    >
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    if (conversations.length === 0) {
        return (
            <div className="messaging-center h-full flex items-center justify-center">
                <div className="text-center">
                    <div className="text-6xl text-gray-300 mb-4">💬</div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No conversations yet</h3>
                    <p className="text-gray-500 max-w-md">
                        {user?.role === 'landlord' 
                            ? 'Conversations will appear here when tenants book viewings for your properties.'
                            : 'Start a conversation by booking a property viewing. You can message the landlord once your booking is submitted.'
                        }
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="messaging-center h-full">
            <div className="messaging-layout h-full flex">
                {/* Conversation List - Left Side */}
                <div className="conversation-list-panel w-1/3 border-r border-gray-200">
                    <div className="p-4 border-b border-gray-200">
                        <h2 className="text-lg font-semibold text-gray-900">💬 Messages</h2>
                        <p className="text-sm text-gray-500 mt-1">
                            {user?.role === 'landlord' ? 'Chat with your tenants' : 'Chat with landlords'}
                        </p>
                    </div>
                    <ConversationList
                        conversations={conversations}
                        selectedConversation={selectedConversation}
                        onConversationSelect={handleConversationSelect}
                        currentUser={user}
                        loading={false}
                    />
                </div>

                {/* Chat Window - Right Side */}
                <div className="chat-window-panel w-2/3">
                    {selectedConversation ? (
                        <ChatWindow
                            conversation={selectedConversation}
                            currentUser={user}
                            onBack={null} // No back button in master-detail view
                            onMessageSent={handleMessageSent}
                        />
                    ) : (
                        <div className="no-conversation-selected h-full flex items-center justify-center bg-gray-50">
                            <div className="text-center">
                                <div className="text-6xl text-gray-300 mb-4">💬</div>
                                <h3 className="text-lg font-medium text-gray-900 mb-2">Select a conversation</h3>
                                <p className="text-gray-500">
                                    Choose a conversation from the list to start messaging
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessagingCenter;

