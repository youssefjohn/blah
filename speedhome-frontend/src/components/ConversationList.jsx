import React from 'react';
import MessagingAPI from '../services/MessagingAPI';
import './ConversationList.css';

const ConversationList = ({ conversations, onConversationSelect, currentUser }) => {
    const handleConversationClick = (conversation) => {
        onConversationSelect(conversation);
    };

    const getConversationTitle = (conversation) => {
        if (currentUser?.role === 'landlord') {
            return conversation.tenant_name || 'Tenant';
        } else {
            return conversation.landlord_name || 'Landlord';
        }
    };

    const getConversationSubtitle = (conversation) => {
        return conversation.property_title || 'Property';
    };

    const getLastMessagePreview = (conversation) => {
        if (!conversation.last_message_at) {
            return 'No messages yet';
        }
        
        // This would ideally come from the API, but for now we'll show a generic message
        return 'Tap to view conversation';
    };

    const getBookingStatusBadge = (bookingStatus) => {
        const statusConfig = {
            'pending': { color: '#f59e0b', text: 'Pending' },
            'confirmed': { color: '#10b981', text: 'Confirmed' },
            'completed': { color: '#6b7280', text: 'Completed' },
            'cancelled': { color: '#ef4444', text: 'Cancelled' },
            'declined': { color: '#ef4444', text: 'Declined' }
        };

        const config = statusConfig[bookingStatus] || { color: '#6b7280', text: bookingStatus };
        
        return (
            <span 
                className="booking-status-badge"
                style={{ backgroundColor: config.color }}
            >
                {config.text}
            </span>
        );
    };

    if (conversations.length === 0) {
        return (
            <div className="conversation-list-empty">
                <div className="empty-state-icon">💬</div>
                <h3>No conversations</h3>
                <p>Your conversations will appear here</p>
            </div>
        );
    }

    return (
        <div className="conversation-list">
            <div className="conversation-list-header">
                <h3>Conversations ({conversations.length})</h3>
            </div>
            
            <div className="conversation-list-items">
                {conversations.map((conversation) => (
                    <div
                        key={conversation.id}
                        className="conversation-item"
                        onClick={() => handleConversationClick(conversation)}
                    >
                        <div className="conversation-avatar">
                            <div className="avatar-circle">
                                {getConversationTitle(conversation).charAt(0).toUpperCase()}
                            </div>
                            {conversation.unread_count > 0 && (
                                <div className="unread-indicator">
                                    {conversation.unread_count}
                                </div>
                            )}
                        </div>
                        
                        <div className="conversation-content">
                            <div className="conversation-header">
                                <h4 className="conversation-title">
                                    {getConversationTitle(conversation)}
                                </h4>
                                <span className="conversation-time">
                                    {MessagingAPI.formatTimestamp(conversation.last_message_at || conversation.created_at)}
                                </span>
                            </div>
                            
                            <div className="conversation-subtitle">
                                <span className="property-name">
                                    📍 {getConversationSubtitle(conversation)}
                                </span>
                                {getBookingStatusBadge(conversation.booking_status)}
                            </div>
                            
                            <div className="conversation-preview">
                                {getLastMessagePreview(conversation)}
                            </div>
                        </div>
                        
                        <div className="conversation-arrow">
                            →
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default ConversationList;

