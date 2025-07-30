# Database Migration Notes

## Credit Check Field Addition - Schema Update Required

### Issue Encountered
When adding the `credit_check_path` field to the Application model, existing databases will not have this column, causing SQLAlchemy errors:

```
sqlalchemy.exc.OperationalError: (sqlite3.OperationalError) no such column: applications.credit_check_path
```

### Solution Applied
1. **Stop the backend server**
2. **Remove existing database**: `rm -f speedhome.db`
3. **Restart backend server** - Flask will recreate the database with the new schema

### For Production Deployment
In production environments, use proper database migrations instead of dropping the database:

```sql
ALTER TABLE applications ADD COLUMN credit_check_path VARCHAR(500);
```

### Files Modified for Credit Check Feature
- `src/models/application.py` - Added credit_check_path field
- `src/services/file_service.py` - Added credit_check to DOCUMENT_TYPES
- Frontend components updated to support Credit Check uploads

### Date
July 30, 2025

### Status
✅ Resolved - Database recreated with new schema
✅ Credit Check feature fully functional

