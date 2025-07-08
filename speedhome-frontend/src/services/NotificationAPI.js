/**
 * A service class for handling all API requests related to notifications.
 */
class NotificationAPI {

    /**
     * Fetches all unread notifications for the currently logged-in user.
     * @returns {Promise<object>} A promise that resolves to the API response.
     */
    static async getNotifications() {
      try {
        const response = await fetch('/api/notifications', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include', // Important for sending session cookies
        });
  
        if (!response.ok) {
          // Don't throw an error for 401, as it might just mean the user is logged out.
          // The UI will handle this gracefully.
          if (response.status === 401) {
            return { success: false, notifications: [] };
          }
          const data = await response.json();
          throw new Error(data.error || 'Failed to fetch notifications');
        }
  
        return await response.json();
      } catch (error) {
        console.error('Error fetching notifications:', error);
        // Return a default empty state on error to prevent UI crashes.
        return { success: false, notifications: [] };
      }
    }
  
    /**
     * Marks a list of notification IDs as read.
     * @param {number[]} ids - An array of notification IDs to mark as read.
     * @returns {Promise<object>} A promise that resolves to the API response.
     */
    static async markAsRead(ids) {
      try {
        const response = await fetch('/api/notifications/mark-as-read', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify({ ids }),
        });
  
        const data = await response.json();
        
        if (!response.ok) {
          throw new Error(data.error || 'Failed to mark notifications as read');
        }
  
        return data;
      } catch (error) {
        console.error('Error marking notifications as read:', error);
        throw error;
      }
    }
  }
  
  export default NotificationAPI;
  