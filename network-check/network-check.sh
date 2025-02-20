#!/bin/bash

# network-check.sh
# A script to check DNS servers and website connectivity

# Default settings
TIMEOUT=2
MAX_RETRIES=2
CHECK_IPV6=false

# Default DNS servers to check
DNS_SERVERS=(
    "8.8.8.8"         # Google DNS
    "8.8.4.4"         # Google DNS Secondary
    "1.1.1.1"         # Cloudflare
    "9.9.9.9"         # Quad9
)

# Default websites to check
WEBSITES=(
    "google.com"
    "cloudflare.com"
    "github.com"
    ".com"
)

# Colors and formatting
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'
BOLD='\033[1m'

# Usage information
usage() {
    cat << EOF
Usage: $0 [options]

Options:
    -t SEC    Set timeout in seconds (default: 2)
    -r NUM    Set number of retries (default: 2)
    -6        Enable IPv6 checks
    -h        Show this help message
EOF
    exit 1
}

# Parse command line arguments
while getopts "t:r:6h" opt; do
    case $opt in
        t) TIMEOUT=$OPTARG ;;
        r) MAX_RETRIES=$OPTARG ;;
        6) CHECK_IPV6=true ;;
        h) usage ;;
        \?) echo "Invalid option: -$OPTARG" >&2; usage ;;
    esac
done

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check required commands
for cmd in ping dig curl; do
    if ! command_exists "$cmd"; then
        echo -e "${RED}Error: Required command '$cmd' not found.${NC}"
        exit 1
    fi
done

# Function to print status
print_status() {
    local status=$1
    local message=$2
    case $status in
        "OK")
            echo -e "[${GREEN}OK${NC}] $message"
            ;;
        "FAIL")
            echo -e "[${RED}FAIL${NC}] $message"
            ;;
        "INFO")
            echo -e "[${YELLOW}INFO${NC}] $message"
            ;;
    esac
}

# Function to check DNS server
check_dns() {
    local dns=$1
    local domain="google.com"
    
    # Try to resolve domain using specific DNS server
    if dig @"$dns" "$domain" +short +timeout="$TIMEOUT" > /dev/null 2>&1; then
        print_status "OK" "DNS Server $dns is responding"
        return 0
    else
        print_status "FAIL" "DNS Server $dns is not responding"
        return 1
    fi
}

# Function to check website
check_website() {
    local site=$1
    local retry=0
    
    while [ $retry -lt $MAX_RETRIES ]; do
        if ping -c 1 -W "$TIMEOUT" "$site" > /dev/null 2>&1; then
            print_status "OK" "Website $site is reachable"
            
            # Try HTTP connection
            if curl -s --max-time "$TIMEOUT" "https://$site" > /dev/null 2>&1; then
                print_status "OK" "HTTPS connection to $site successful"
            else
                print_status "FAIL" "HTTPS connection to $site failed"
            fi
            return 0
        fi
        retry=$((retry + 1))
    done
    
    print_status "FAIL" "Website $site is not reachable"
    return 1
}

# Function to check IPv6 connectivity
check_ipv6() {
    if ping6 -c 1 -W "$TIMEOUT" google.com > /dev/null 2>&1; then
        print_status "OK" "IPv6 connectivity is available"
        return 0
    else
        print_status "INFO" "IPv6 connectivity is not available"
        return 1
    fi
}

# Main execution
echo -e "\n${BOLD}Network Connectivity Check${NC}"
echo "================================"

# Check IPv6 if enabled
if [ "$CHECK_IPV6" = true ]; then
    echo -e "\n${BOLD}Checking IPv6 Connectivity:${NC}"
    check_ipv6
fi

# Check DNS servers
echo -e "\n${BOLD}Checking DNS Servers:${NC}"
dns_failures=0
for dns in "${DNS_SERVERS[@]}"; do
    check_dns "$dns" || ((dns_failures++))
done

# Check websites
echo -e "\n${BOLD}Checking Website Connectivity:${NC}"
web_failures=0
for site in "${WEBSITES[@]}"; do
    check_website "$site" || ((web_failures++))
done

# Print summary
echo -e "\n${BOLD}Summary:${NC}"
total_dns=${#DNS_SERVERS[@]}
total_web=${#WEBSITES[@]}
dns_success=$((total_dns - dns_failures))
web_success=$((total_web - web_failures))

echo "DNS Servers: $dns_success/$total_dns responding"
echo "Websites: $web_success/$total_web reachable"

# Exit with status code based on results
if [ $dns_failures -eq 0 ] && [ $web_failures -eq 0 ]; then
    echo -e "\n${GREEN}All checks passed successfully!${NC}"
    exit 0
else
    echo -e "\n${RED}Some checks failed. Please review the results above.${NC}"
    exit 1
fi