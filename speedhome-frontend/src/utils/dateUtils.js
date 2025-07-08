// Date formatting utility functions
export const formatDate = (dateString) => {
  if (!dateString) return 'Invalid Date';
  
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  } catch (error) {
    console.error('Error formatting date:', error);
    return 'Invalid Date';
  }
};

export const formatTime = (timeString) => {
  if (!timeString) return 'Invalid Time';
  
  try {
    // Handle both "HH:MM" format and full datetime strings
    let time;
    if (timeString.includes('T')) {
      // Full datetime string
      time = new Date(timeString);
    } else {
      // Just time string "HH:MM"
      time = new Date(`1970-01-01T${timeString}:00`);
    }
    
    if (isNaN(time.getTime())) return 'Invalid Time';
    
    return time.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true
    });
  } catch (error) {
    console.error('Error formatting time:', error);
    return 'Invalid Time';
  }
};

export const formatDateTime = (dateString, timeString) => {
  const formattedDate = formatDate(dateString);
  const formattedTime = formatTime(timeString);
  
  if (formattedDate === 'Invalid Date' || formattedTime === 'Invalid Time') {
    return 'Invalid Date/Time';
  }
  
  return `${formattedDate} at ${formattedTime}`;
};

