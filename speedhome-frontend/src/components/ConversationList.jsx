import React from 'react';

// Note: Assuming MessagingAPI.formatTimestamp is available, otherwise replace with a date formatting library.
// import { format } from 'date-fns';

const ConversationList = ({ conversations, selectedConversation, onConversationSelect, currentUser }) => {

    const getOtherParticipant = (conversation) => {
        if (!currentUser) return { name: 'Unknown', avatarInitial: '?' };

        if (currentUser.role === 'landlord') {
            return {
                name: conversation.other_participant?.name || 'Tenant',
                avatarInitial: (conversation.other_participant?.name || 'T').charAt(0).toUpperCase()
            };
        } else {
            return {
                name: conversation.other_participant?.name || 'Landlord',
                avatarInitial: (conversation.other_participant?.name || 'L').charAt(0).toUpperCase()
            };
        }
    };

    const getLastMessagePreview = (conversation) => {
        if (conversation.last_message_body) {
            return conversation.last_message_body;
        }
        return 'No messages yet';
    };

    // A simplified timestamp formatter. Replace with a robust one if needed.
    const formatTimestamp = (timestamp) => {
        if (!timestamp) return '';
        const date = new Date(timestamp);
        // Simple logic: if it's today, show time, else show date.
        if (new Date().toDateString() === date.toDateString()) {
            return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        }
        return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
    };


    if (!conversations || conversations.length === 0) {
        // This part can be simplified or kept as is.
        // For this example, we assume the parent handles the "no conversations" state.
        return null;
    }

    return (
        <div className="h-full overflow-y-auto">
            {conversations.map((conversation) => {
                const otherParticipant = getOtherParticipant(conversation);
                const isSelected = selectedConversation?.id === conversation.id;

                return (
                    <div
                        key={conversation.id}
                        onClick={() => onConversationSelect(conversation)}
                        // ✅ This is the key for the active state and hover effects
                        className={`
                            flex items-center p-3 space-x-3 cursor-pointer border-b border-gray-200
                            transition-colors duration-150
                            ${isSelected ? 'bg-blue-50' : 'hover:bg-gray-50'}
                        `}
                    >
                        {/* Avatar */}
                        <div className="relative flex-shrink-0">
                            <div className="h-12 w-12 rounded-full bg-gray-300 flex items-center justify-center">
                                <span className="text-xl font-semibold text-gray-600">
                                    {otherParticipant.avatarInitial}
                                </span>
                            </div>
                            {conversation.unread_count > 0 && (
                                <span className="absolute top-0 right-0 block h-4 w-4 rounded-full bg-red-500 text-white text-xs flex items-center justify-center border-2 border-white">
                                    {conversation.unread_count}
                                </span>
                            )}
                        </div>

                        {/* Content */}
                        <div className="flex-grow overflow-hidden">
                            <div className="flex justify-between items-baseline">
                                {/* ✅ Name is now bold for hierarchy */}
                                <h4 className="font-semibold text-sm text-gray-800 truncate">
                                    {otherParticipant.name}
                                </h4>
                                {/* ✅ Timestamp is smaller and lighter */}
                                <span className="text-xs text-gray-400 flex-shrink-0">
                                    {formatTimestamp(conversation.last_message_at || conversation.created_at)}
                                </span>
                            </div>

                            {/* ✅ Property title is prominent but secondary */}
                            <p className="text-xs text-gray-500 truncate mt-0.5">
                                {conversation.property_title || 'Property Details'}
                            </p>

                            {/* ✅ Message preview is lighter and truncates */}
                            <p className="text-sm text-gray-500 truncate mt-1">
                                {getLastMessagePreview(conversation)}
                            </p>
                        </div>
                    </div>
                );
            })}
        </div>
    );
};

export default ConversationList;