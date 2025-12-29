#!/bin/bash
set -e

echo "🚀 Starting MinIO with seed data initialization"
echo "==============================================="

# Start MinIO server in the background
echo "📦 Starting MinIO server..."
minio server /data --console-address ":9001" &
MINIO_PID=$!

# Wait for MinIO to be ready
echo "⏳ Waiting for MinIO to be ready..."
until mc alias set local http://localhost:9000 "${MINIO_ROOT_USER}" "${MINIO_ROOT_PASSWORD}" > /dev/null 2>&1; do
  echo "   MinIO not ready yet, retrying in 2 seconds..."
  sleep 2
done

echo "✅ MinIO is ready!"

# Define the bucket name for seed data
BUCKET_NAME="${MINIO_SEED_BUCKET:-documents}"

# Check if bucket exists
if mc ls "local/${BUCKET_NAME}" > /dev/null 2>&1; then
  echo "ℹ️  Bucket '${BUCKET_NAME}' already exists"
  
  # Check if bucket has any objects
  OBJECT_COUNT=$(mc ls "local/${BUCKET_NAME}" --recursive 2>/dev/null | wc -l)
  
  if [ "$OBJECT_COUNT" -gt 0 ]; then
    echo "ℹ️  Bucket contains ${OBJECT_COUNT} objects - skipping seed data load"
  else
    echo "📦 Bucket is empty - proceeding with seed data load"
    LOAD_SEED_DATA=true
  fi
else
  echo "📦 Creating bucket: ${BUCKET_NAME}"
  mc mb "local/${BUCKET_NAME}"
  LOAD_SEED_DATA=true
fi

# Load seed data if needed
if [ "$LOAD_SEED_DATA" = true ]; then
  SEED_DATA_DIR="/files"

  if [ ! -d "$SEED_DATA_DIR" ] || [ -z "$(ls -A $SEED_DATA_DIR 2>/dev/null)" ]; then
    echo "⚠️  No seed data found in ${SEED_DATA_DIR}"
    echo "   To add seed data, place files in: minio/"
  else
    echo "📤 Uploading seed data to bucket '${BUCKET_NAME}'..."

    # Upload all files from directory (excluding data/ and entrypoint.sh)
    FILE_COUNT=0
    for file in "$SEED_DATA_DIR"/*; do
      if [ -f "$file" ]; then
        filename=$(basename "$file")
        # Skip entrypoint.sh
        if [ "$filename" = "entrypoint.sh" ]; then
          continue
        fi
        echo "   Uploading: ${filename}"
        mc cp "$file" "local/${BUCKET_NAME}/${filename}"
        FILE_COUNT=$((FILE_COUNT + 1))
      fi
    done

    # Handle subdirectories recursively (excluding data/)
    for dir in "$SEED_DATA_DIR"/*/; do
      if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        # Skip data directory
        if [ "$dirname" = "data" ]; then
          continue
        fi
        echo "   Uploading directory: ${dirname}/"
        mc cp --recursive "$dir" "local/${BUCKET_NAME}/${dirname}/"
        FILE_COUNT=$((FILE_COUNT + $(find "$dir" -type f | wc -l)))
      fi
    done

    echo "✅ Seed data initialization complete!"
    echo "   📊 Uploaded ${FILE_COUNT} files to bucket '${BUCKET_NAME}'"
  fi
fi

echo ""
echo "🔗 MinIO is running"
echo "   Console: http://localhost:9001"
echo "   API: http://localhost:9000"
echo "   Bucket: ${BUCKET_NAME}"
echo ""

# Bring MinIO to foreground
wait $MINIO_PID
