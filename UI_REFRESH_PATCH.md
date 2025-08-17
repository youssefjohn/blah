# UI Refresh Fix for Application Approval

## Problem
When landlords approve applications, the property status changes from Active to Pending in the backend, but the UI doesn't refresh immediately. Users need to manually refresh the page to see the status change.

## Solution
Add the following lines to the `handleApplicationResponse` function in `speedhome-frontend/src/pages/LandlordDashboard.jsx`:

**Location:** After line `await loadAgreements();` (around line 548)

**Add these lines:**
```javascript
await loadProperties();
window.dispatchEvent(new CustomEvent('propertyUpdated'));
```

**Complete function should look like:**
```javascript
const handleApplicationResponse = async (applicationId, response) => {
  const application = tenantApplications.find(app => app.id === applicationId);
  if (application && !application.is_seen_by_landlord) {
    handleMarkApplicationAsSeen(applicationId);
  }

  const newStatus = response === 'approved' ? 'approved' : 'rejected';

  try {
    const result = await ApplicationAPI.updateApplicationStatus(applicationId, newStatus);
    if (result.success) {
      alert(`Tenant application has been ${newStatus} successfully!`);
      // Refresh both lists to show the updated state
      await loadApplications();
      await loadAgreements();
      await loadProperties();  // ← ADD THIS LINE
      window.dispatchEvent(new CustomEvent('propertyUpdated'));  // ← ADD THIS LINE
    } else {
      alert(`Failed to update application: ${result.error}`);
    }
  } catch (error) {
    console.error('Error updating application status:', error);
    alert('An error occurred while updating the application.');
  }
};
```

## Expected Result
After applying this fix:
- When landlord approves an application
- Property status immediately changes from Active (green) to Pending (yellow)
- No manual page refresh needed
- UI updates instantly
