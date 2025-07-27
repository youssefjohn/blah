import React, { useState, useEffect, useRef } from 'react';
import MessagingAPI from '../services/MessagingAPI';
import MessageBubble from './MessageBubble';
import MessageInput from './MessageInput';

const ChatWindow = ({ conversation, currentUser, onMessageSent }) => {
    const [messages, setMessages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [sending, setSending] = useState(false);
    const messagesEndRef = useRef(null);
    const scrollContainerRef = useRef(null);

    useEffect(() => {
        if (conversation?.id) {
            loadMessages();
        }
    }, [conversation?.id]);

    useEffect(() => {
    if (scrollContainerRef.current) {
        scrollContainerRef.current.scrollTop = scrollContainerRef.current.scrollHeight;
    }
}, [messages, loading]);

    const loadMessages = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await MessagingAPI.getMessages(conversation.id);
            setMessages(response.messages || []);
        } catch (err) {
            console.error('Error loading messages:', err);
            setError('Failed to load messages. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleSendMessage = async (messageText) => {
        if (!messageText.trim() || sending) return;

        try {
            setSending(true);
            const response = await MessagingAPI.sendMessage(conversation.id, messageText.trim());
            setMessages(prev => [...prev, response.message]);
            onMessageSent();
        } catch (err) {
            console.error('Error sending message:', err);
            // Optionally show a toast notification for send errors
        } finally {
            setSending(false);
        }
    };

    const otherParticipant = conversation?.other_participant || { name: 'User', role: 'tenant' };

    const canSendMessages = () => {
        return conversation.status === 'active' &&
               ['pending', 'confirmed'].includes(conversation.booking_status);
    };

    return (
        <div className="flex flex-col h-full bg-white max-h-full overflow-hidden">
            {/* Chat Header */}
            <div className="flex items-center p-3 border-b border-gray-200 flex-shrink-0">
                <div className="relative flex-shrink-0 mr-3">
                    <div className="h-10 w-10 rounded-full bg-gray-300 flex items-center justify-center">
                        <span className="text-lg font-semibold text-gray-600">
                            {otherParticipant.name.charAt(0).toUpperCase()}
                        </span>
                    </div>
                </div>
                <div className="flex-grow">
                    <h3 className="font-semibold text-gray-800">{otherParticipant.name}</h3>
                    <p className="text-xs text-gray-500 truncate">
                        Regarding: {conversation.property_title}
                    </p>
                </div>
            </div>

            {/* Messages Area */}
            <div ref={scrollContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 min-h-0">
                {loading && (
                    <div className="flex justify-center items-center h-full">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                    </div>
                )}
                {error && (
                    <div className="text-center p-4">
                        <p className="text-red-500 mb-2">{error}</p>
                        <button onClick={loadMessages} className="px-3 py-1 bg-blue-500 text-white rounded text-sm">
                            Try Again
                        </button>
                    </div>
                )}
                {!loading && !error && messages.length === 0 && (
                     <div className="text-center p-4 text-gray-500">
                        <div className="text-5xl mb-2">💬</div>
                        <h4 className="font-semibold">Start the conversation</h4>
                        <p className="text-sm">Send a message to {otherParticipant.name}.</p>
                    </div>
                )}
                {!loading && !error && messages.length > 0 && (
                    messages.map((message) => (
                        <MessageBubble
                            key={message.id}
                            message={message}
                            isOwn={message.sender_id === currentUser?.id}
                        />
                    ))
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Message Input */}
            <div className="p-3 border-t border-gray-200 flex-shrink-0 bg-white">
                {canSendMessages() ? (
                    <MessageInput
                        onSendMessage={handleSendMessage}
                        disabled={sending}
                        placeholder={`Message ${otherParticipant.name}...`}
                    />
                ) : (
                    <div className="text-center text-sm text-gray-500 p-2 bg-gray-100 rounded-lg">
                        Messaging is disabled for this conversation.
                    </div>
                )}
            </div>
        </div>
    );
};

export default ChatWindow;