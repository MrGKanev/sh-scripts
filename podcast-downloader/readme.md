# Podcast Downloader

A robust bash script for downloading and organizing podcast episodes from RSS feeds. The script automatically downloads episodes, organizes them by date, and optionally adds album metadata tags.

## Features

- Downloads podcast episodes from any RSS feed
- Organizes files by date and episode title
- Supports metadata tagging (album name)
- Handles network interruptions with retry mechanism
- Comprehensive error handling and logging
- Skips existing episodes to avoid duplicates
- Supports various audio formats (mp3, m4a, etc.)

## Prerequisites

- `wget` for downloading files
- `id3v2` (optional) for metadata tagging
- Bash shell (version 4.0 or later recommended)

## Installation

1. Download the script:

   ```bash
   curl -O https://raw.githubusercontent.com/mrgkanev/sh-scripts/main/podcast-downloader/podcast-downloader.sh
   ```

2. Make it executable:

   ```bash
   chmod +x podcast-downloader.sh
   ```

## Usage

Basic usage:

```bash
podcast-downloader.sh -u "https://example.com/podcast.xml"
```

With all options:

```bash
podcast-downloader.sh -u "https://example.com/podcast.xml" \
                       -d "/path/to/downloads" \
                       -a "My Favorite Podcast" \
                       -t 60 \
                       -v
```

### Options

- `-u` RSS feed URL (required)
- `-d` Download directory (default: ~/Podcasts)
- `-a` Album name for metadata tagging
- `-t` Download timeout in seconds (default: 30)
- `-v` Enable verbose output
- `-h` Show help message

## Output Format

Downloaded files are named using the following format:

```
YYYY-MM-DD_Episode_Title.extension
```

## Error Handling

The script includes:

- Network retry mechanism (3 attempts)
- Timeout protection
- Comprehensive logging
- Temporary file cleanup
- Input validation

## Contributing

Feel free to submit issues and enhancement requests!

## Troubleshooting

1. If downloads fail:
   - Check your internet connection
   - Verify the RSS feed URL
   - Increase timeout with `-t` option
   - Enable verbose mode with `-v`

2. If metadata tagging fails:
   - Ensure id3v2 is installed
   - Check file permissions
   - Verify the audio file format supports ID3 tags

## License

This script is available under the MIT license. Feel free to modify and distribute it.
