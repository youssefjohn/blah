import React, { useState } from 'react';
import MessagingAPI from '../services/MessagingAPI';
import './MessageBubble.css';

const MessageBubble = ({ message, isOwn, currentUser }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editText, setEditText] = useState(message.message_body);
    const [isDeleting, setIsDeleting] = useState(false);

    const handleEdit = async () => {
        if (!editText.trim()) return;

        try {
            await MessagingAPI.editMessage(message.id, editText.trim());
            setIsEditing(false);
            // In a real app, you'd want to update the message in the parent component
            // For now, we'll just close the edit mode
        } catch (error) {
            console.error('Error editing message:', error);
            alert('Failed to edit message: ' + error.message);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this message?')) {
            return;
        }

        try {
            setIsDeleting(true);
            await MessagingAPI.deleteMessage(message.id);
            // In a real app, you'd want to remove the message from the parent component
            // For now, we'll just show a visual indication
        } catch (error) {
            console.error('Error deleting message:', error);
            alert('Failed to delete message: ' + error.message);
            setIsDeleting(false);
        }
    };

    const canEdit = () => {
        if (!isOwn) return false;
        
        // Check if message is recent enough to edit (15 minutes)
        const messageTime = new Date(message.created_at);
        const now = new Date();
        const diffInMinutes = (now - messageTime) / (1000 * 60);
        
        return diffInMinutes < 15;
    };

    const canDelete = () => {
        return isOwn;
    };

    const formatMessageTime = (timestamp) => {
        const date = new Date(timestamp);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    if (isDeleting) {
        return (
            <div className={`message-bubble ${isOwn ? 'own' : 'other'} deleted`}>
                <div className="message-content">
                    <em>Message deleted</em>
                </div>
            </div>
        );
    }

    return (
        <div className={`message-bubble ${isOwn ? 'own' : 'other'}`}>
            <div className="message-content">
                {!isOwn && (
                    <div className="sender-name">
                        {message.sender_name} ({message.sender_role})
                    </div>
                )}
                
                {isEditing ? (
                    <div className="message-edit">
                        <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="edit-textarea"
                            rows="3"
                        />
                        <div className="edit-actions">
                            <button onClick={handleEdit} className="save-button">
                                Save
                            </button>
                            <button 
                                onClick={() => {
                                    setIsEditing(false);
                                    setEditText(message.message_body);
                                }} 
                                className="cancel-button"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                ) : (
                    <div className="message-text">
                        {message.message_body}
                        {message.is_edited && (
                            <span className="edited-indicator"> (edited)</span>
                        )}
                    </div>
                )}
                
                <div className="message-footer">
                    <span className="message-time">
                        {formatMessageTime(message.created_at)}
                    </span>
                    
                    {isOwn && !isEditing && (
                        <div className="message-actions">
                            {canEdit() && (
                                <button 
                                    onClick={() => setIsEditing(true)}
                                    className="action-button edit-button"
                                    title="Edit message"
                                >
                                    ✏️
                                </button>
                            )}
                            {canDelete() && (
                                <button 
                                    onClick={handleDelete}
                                    className="action-button delete-button"
                                    title="Delete message"
                                >
                                    🗑️
                                </button>
                            )}
                        </div>
                    )}
                    
                    {isOwn && message.is_read && (
                        <span className="read-indicator" title="Read">
                            ✓✓
                        </span>
                    )}
                </div>
            </div>
        </div>
    );
};

export default MessageBubble;

