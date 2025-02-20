# Network Checker

A bash script to quickly check network connectivity by testing both DNS servers and website accessibility. Perfect for diagnosing network issues or monitoring connectivity.

## Features

- Checks multiple DNS servers simultaneously
- Tests website connectivity and HTTPS access
- Optional IPv6 connectivity testing
- Configurable timeouts and retry attempts
- Color-coded output for easy reading
- Summary report of all checks

## Requirements

- `bash`
- `ping`
- `dig` (from dnsutils or bind-utils package)
- `curl`

## Installation

1. Install dependencies (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install dnsutils curl
```

2. Make the script executable:

```bash
chmod +x network-check.sh
```

## Usage

Basic usage with default settings:

```bash
./network-check.sh
```

With custom timeout and retries:

```bash
./network-check.sh -t 3 -r 3
```

Enable IPv6 checks:

```bash
./network-check.sh -6
```

### Options

- `-t SEC` : Set timeout in seconds (default: 2)
- `-r NUM` : Set number of retries (default: 2)
- `-6`     : Enable IPv6 checks
- `-h`     : Show help message

## Example Output

```
Network Connectivity Check
================================

Checking DNS Servers:
[OK] DNS Server 8.8.8.8 is responding
[OK] DNS Server 1.1.1.1 is responding
[FAIL] DNS Server 9.9.9.9 is not responding

Checking Website Connectivity:
[OK] Website google.com is reachable
[OK] HTTPS connection to google.com successful
[OK] Website github.com is reachable
[OK] HTTPS connection to github.com successful

Summary:
DNS Servers: 2/3 responding
Websites: 2/2 reachable

All checks passed successfully!
```

## Customization

You can modify the script to:

- Add or remove DNS servers to check
- Change the list of websites to test
- Adjust timeout and retry values
- Add additional connectivity tests
