#!/bin/bash
set -e

echo "🚀 Starting SQL Server with seed data initialization"
echo "===================================================="

# Start SQL Server in the background
echo "📦 Starting SQL Server..."
/opt/mssql/bin/sqlservr &
SQL_PID=$!

# Configuration
SEED_DATA_DIR="/sql-scripts"
DB_NAME="${MSSQL_SEED_DB:-CompanyDB}"
MARKER_DB="${DB_NAME}_SEED_LOADED"

# Wait for SQL Server to be ready
echo "⏳ Waiting for SQL Server to be ready..."
for i in {1..60}; do
  if /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${MSSQL_SA_PASSWORD}" -C -Q "SELECT 1" > /dev/null 2>&1; then
    echo "✅ SQL Server is ready!"
    break
  fi
  if [ $i -eq 60 ]; then
    echo "❌ SQL Server failed to start within 60 seconds"
    exit 1
  fi
  echo "   SQL Server not ready yet, retrying in 2 seconds... ($i/60)"
  sleep 2
done

# Check if seed data has already been loaded (using marker database)
if /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${MSSQL_SA_PASSWORD}" -C -Q "SELECT name FROM sys.databases WHERE name = '${MARKER_DB}'" -h -1 | grep -q "${MARKER_DB}"; then
  echo "ℹ️  Seed data already loaded (marker database '${MARKER_DB}' exists)"
  echo "   To reload, drop the marker database: DROP DATABASE ${MARKER_DB};"
else
  echo "📦 Seed data not found - proceeding with initialization"

  # Check if seed data directory exists and has SQL files
  if [ ! -d "$SEED_DATA_DIR" ]; then
    echo "⚠️  SQL scripts directory not found: ${SEED_DATA_DIR}"
    echo "   To add SQL scripts, place .sql files in: azure-sql-server/"
  else
    SQL_FILES=$(find "$SEED_DATA_DIR" -name "*.sql" -type f | sort)

    if [ -z "$SQL_FILES" ]; then
      echo "⚠️  No .sql files found in ${SEED_DATA_DIR}"
      echo "   To add SQL scripts, place .sql files in: azure-sql-server/"
    else
      echo "📤 Loading seed data into SQL Server..."

      # Create the target database if it doesn't exist
      echo "   Creating database: ${DB_NAME}"
      /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${MSSQL_SA_PASSWORD}" -C -Q "
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = '${DB_NAME}')
BEGIN
    CREATE DATABASE [${DB_NAME}];
    PRINT 'Database ${DB_NAME} created successfully';
END
ELSE
BEGIN
    PRINT 'Database ${DB_NAME} already exists';
END
" || echo "   Database already exists or error creating database"

      # Execute each SQL file
      FILE_COUNT=0
      for sql_file in $SQL_FILES; do
        filename=$(basename "$sql_file")
        echo "   Executing: ${filename}"
        
        # Execute SQL file against the target database
        /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${MSSQL_SA_PASSWORD}" -d "${DB_NAME}" -C -i "$sql_file"
        
        if [ $? -eq 0 ]; then
          echo "   ✅ Successfully executed: ${filename}"
          FILE_COUNT=$((FILE_COUNT + 1))
        else
          echo "   ❌ Error executing: ${filename}"
        fi
      done

      # Create marker database to indicate seed data has been loaded
      echo "   Creating marker database: ${MARKER_DB}"
      /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P "${MSSQL_SA_PASSWORD}" -C -Q "
CREATE DATABASE [${MARKER_DB}];
" > /dev/null 2>&1

      echo "✅ Seed data initialization complete!"
      echo "   📊 Executed ${FILE_COUNT} SQL files"
      echo "   🗄️  Target database: ${DB_NAME}"
    fi
  fi
fi

echo ""
echo "🔗 SQL Server is running"
echo "   Server: localhost,1433"
echo "   Username: sa"
echo "   Database: ${DB_NAME}"
echo "   Web UI: http://localhost:8080 (via Adminer)"
echo ""

# Bring SQL Server to foreground
wait $SQL_PID
