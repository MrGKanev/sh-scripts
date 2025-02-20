#!/bin/bash

# podcast-downloader
# Version: 1.1.1
# Description: A tool to download podcasts from an RSS feed with metadata tagging

# Default configurations
PODCAST_DIR=~/Podcasts
RSS_FEED=""
ALBUM_NAME=""
TMP_DIR=$(mktemp -d)
VERBOSE=false
MAX_RETRIES=3
TIMEOUT=30

# Error handling
set -euo pipefail
trap cleanup EXIT

# Cleanup function
cleanup() {
    [ -d "$TMP_DIR" ] && rm -rf "$TMP_DIR"
}

# Function to print usage information
usage() {
    cat << EOF
Usage: $0 -u <RSS_FEED_URL> [-d <DOWNLOAD_DIR>] [-a <ALBUM_NAME>] [-v] [-t <TIMEOUT>]

Options:
  -u  Specify the RSS feed URL (required)
  -d  Specify the directory for downloads (default: ~/Podcasts)
  -a  Specify the album name for tagging (default: no album name)
  -v  Enable verbose output
  -t  Set download timeout in seconds (default: 30)
  -h  Show this help message
EOF
    exit 1
}

# Function to log messages
log() {
    local level=$1
    shift
    echo "[$level] $(date '+%Y-%m-%d %H:%M:%S') - $*"
}

# Function to download file with retries
download_with_retry() {
    local url=$1
    local output=$2
    local attempt=1

    while [ $attempt -le $MAX_RETRIES ]; do
        if wget --timeout="$TIMEOUT" -q -O "$output" "$url"; then
            return 0
        fi
        log "WARNING" "Download attempt $attempt failed, retrying..."
        attempt=$((attempt + 1))
        sleep 2
    done
    return 1
}

# Parse command-line arguments
while getopts ":u:d:a:t:vh" opt; do
    case $opt in
        u) RSS_FEED="$OPTARG" ;;
        d) PODCAST_DIR="$OPTARG" ;;
        a) ALBUM_NAME="$OPTARG" ;;
        t) TIMEOUT="$OPTARG" ;;
        v) VERBOSE=true ;;
        h) usage ;;
        \?) log "ERROR" "Invalid option: -$OPTARG"; usage ;;
        :) log "ERROR" "Option -$OPTARG requires an argument."; usage ;;
    esac
done

# Validate inputs
[ -z "$RSS_FEED" ] && { log "ERROR" "RSS feed URL is required."; usage; }

# Create download directory
mkdir -p "$PODCAST_DIR"

# Start process
log "INFO" "Starting podcast download from: $RSS_FEED"

# Check for required tools
for cmd in wget id3v2 date; do
    if ! command -v $cmd &> /dev/null; then
        log "WARNING" "$cmd is not installed. Some features may be limited."
    fi
done

# Download and process RSS feed
RSS_FILE="$TMP_DIR/rss_feed.xml"
if ! download_with_retry "$RSS_FEED" "$RSS_FILE"; then
    log "ERROR" "Failed to download RSS feed"
    exit 1
fi

# Process RSS feed entries
awk -F'enclosure[^>]*url="' '/<enclosure/ {split($2, arr, "\""); print arr[1]}' "$RSS_FILE" | while read -r URL; do
    # Extract metadata
    CONTEXT=$(grep -B 10 -A 10 "$URL" "$RSS_FILE")
    TITLE=$(echo "$CONTEXT" | awk -F'<title>|</title>' '/<title>/ {print $2; exit}')
    PUB_DATE=$(echo "$CONTEXT" | awk -F'<pubDate>|</pubDate>' '/<pubDate>/ {print $2; exit}')
    DATE=$(date -d "$PUB_DATE" +'%Y-%m-%d' 2>/dev/null || echo "unknown-date")

    # Clean filename
    ESCAPED_TITLE=$(echo "$TITLE" | sed -E 's/[^[:alnum:]._-]/_/g' | sed -E 's/_+/_/g' | sed 's/_$//')
    EXTENSION=$(echo "$URL" | grep -oP '\.\w+$' | sed 's/^\.//' || echo "mp3")
    FILENAME="${DATE}_${ESCAPED_TITLE}.${EXTENSION}"
    FILEPATH="$PODCAST_DIR/$FILENAME"

    # Skip if file exists
    if [ -f "$FILEPATH" ]; then
        $VERBOSE && log "INFO" "Already exists: $FILENAME"
        continue
    fi

    # Download episode
    log "INFO" "Downloading: $FILENAME"
    if download_with_retry "$URL" "$FILEPATH"; then
        log "INFO" "Download completed: $FILENAME"
        
        # Tag metadata if possible
        if [ -n "$ALBUM_NAME" ] && command -v id3v2 &> /dev/null; then
            if id3v2 -A "$ALBUM_NAME" "$FILEPATH"; then
                log "INFO" "Tagged album as '$ALBUM_NAME' for $FILENAME"
            else
                log "WARNING" "Failed to tag $FILENAME"
            fi
        fi
    else
        log "ERROR" "Failed to download: $URL"
        rm -f "$FILEPATH"
    fi
done

log "INFO" "Process completed successfully"