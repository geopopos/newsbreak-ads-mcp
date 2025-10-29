#!/bin/bash
# Run NewsBreak Ads MCP Server locally

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check if access token is set
if [ -z "$NEWSBREAK_ACCESS_TOKEN" ]; then
    echo "Error: NEWSBREAK_ACCESS_TOKEN not set"
    echo "Please create a .env file with your access token or set it as an environment variable"
    exit 1
fi

# Run the server
python server.py
