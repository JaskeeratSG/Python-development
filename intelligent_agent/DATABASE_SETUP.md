# Database Setup for Thread Persistence

This guide explains how to set up database persistence for thread resumption in the intelligent agent system.

## Overview

By default, the system uses in-memory storage (`MemorySaver`) which means threads are lost when the application restarts. To enable persistent thread storage across restarts, you need to configure a PostgreSQL database.

## Quick Start

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [PostgreSQL Downloads](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database
CREATE DATABASE intelligent_agent_db;

# Create user (optional, you can use default postgres user)
CREATE USER agent_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE intelligent_agent_db TO agent_user;

# Exit psql
\q
```

### 3. Configure Environment Variables

Create or update your `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/intelligent_agent_db

# Or with custom user:
# DATABASE_URL=postgresql://agent_user:your_password@localhost:5432/intelligent_agent_db
```

**Format:** `postgresql://username:password@host:port/database_name`

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `langgraph-checkpoint-postgres` - PostgreSQL checkpointer for LangGraph
- `sqlalchemy` - Database ORM
- `psycopg2-binary` - PostgreSQL adapter

### 5. Initialize Database Tables

Run the initialization script:

```bash
python scripts/init_database.py
```

This will:
- Connect to your PostgreSQL database
- Create the necessary tables for thread persistence
- Verify the setup

### 6. Verify Setup

When you start your application, you should see:

```
✅ Database checkpointer initialized with: localhost:5432/intelligent_agent_db
```

If you see:

```
⚠️  DATABASE_URL not set. Using in-memory checkpointer...
```

Then check your `.env` file and ensure `DATABASE_URL` is set correctly.

## Usage

Once configured, threads will automatically persist:

1. **API Usage:**
   ```python
   # First request
   POST /api/query
   {
     "text": "What is Python?",
     "thread_id": "user-123"
   }
   
   # Later request (even after restart)
   POST /api/query
   {
     "text": "Tell me more",
     "thread_id": "user-123"  # Same thread_id resumes conversation
   }
   ```

2. **Streamlit Usage:**
   - Thread persistence works automatically
   - Each session maintains its own thread
   - Threads persist across application restarts

## Fallback Behavior

If `DATABASE_URL` is not configured or database connection fails:
- The system automatically falls back to `MemorySaver` (in-memory storage)
- Threads will work within a session but won't persist across restarts
- You'll see a warning message in the logs

## Troubleshooting

### Connection Errors

**Error:** `could not connect to server`
- Ensure PostgreSQL is running: `pg_isready` or `brew services list`
- Check host and port in `DATABASE_URL`
- Verify firewall settings

**Error:** `database "intelligent_agent_db" does not exist`
- Create the database: `CREATE DATABASE intelligent_agent_db;`

**Error:** `password authentication failed`
- Verify username and password in `DATABASE_URL`
- Check PostgreSQL authentication settings in `pg_hba.conf`

### Table Creation Errors

**Error:** `relation "checkpoints" already exists`
- Tables already exist, this is normal
- The script will still succeed

### Performance

For production:
- Use connection pooling (already configured)
- Consider read replicas for high-traffic scenarios
- Monitor database size and clean up old threads periodically

## Database Schema

The checkpointer creates the following tables automatically:
- `checkpoints` - Stores thread checkpoints
- `checkpoint_blobs` - Stores large binary data
- `checkpoint_writes` - Write log for checkpointing

These tables are managed by LangGraph and should not be modified manually.

## Alternative: SQLite (Development Only)

For local development, you can use SQLite:

```bash
DATABASE_URL=sqlite:///./threads.db
```

**Note:** SQLite is not officially supported by `langgraph-checkpoint-postgres`. For production, use PostgreSQL.

## Environment Variables Reference

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://postgres:postgres@localhost:5432/intelligent_agent_db` |

## Next Steps

- Monitor thread storage usage
- Implement thread cleanup/archival for old conversations
- Consider adding thread metadata (user info, timestamps, etc.)





