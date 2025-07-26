import React, { useState, useRef, useEffect } from 'react';
import './MessageInput.css';

const MessageInput = ({ onSendMessage, disabled, placeholder = "Type a message..." }) => {
    const [message, setMessage] = useState('');
    const textareaRef = useRef(null);

    useEffect(() => {
        // Auto-resize textarea
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
        }
    }, [message]);

    const handleSubmit = (e) => {
        e.preventDefault();
        
        if (!message.trim() || disabled) return;
        
        onSendMessage(message);
        setMessage('');
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }
    };

    const handleChange = (e) => {
        setMessage(e.target.value);
    };

    return (
        <div className="message-input">
            <form onSubmit={handleSubmit} className="message-form">
                <div className="input-container">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={handleChange}
                        onKeyPress={handleKeyPress}
                        placeholder={placeholder}
                        disabled={disabled}
                        className="message-textarea"
                        rows="1"
                        maxLength={1000}
                    />
                    
                    <button
                        type="submit"
                        disabled={!message.trim() || disabled}
                        className="send-button"
                        title="Send message"
                    >
                        {disabled ? (
                            <span className="sending-indicator">⏳</span>
                        ) : (
                            <span className="send-icon">➤</span>
                        )}
                    </button>
                </div>
                
                <div className="input-footer">
                    <span className="character-count">
                        {message.length}/1000
                    </span>
                    <span className="input-hint">
                        Press Enter to send, Shift+Enter for new line
                    </span>
                </div>
            </form>
        </div>
    );
};

export default MessageInput;

