#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Chatbot Templates Demo Setup...${NC}"

# Check for Doppler
if command -v doppler &> /dev/null; then
    echo -e "${GREEN}Doppler found! Configuring environment...${NC}"
    
    # Check if logged in (basic check)
    if doppler me &> /dev/null; then
        echo -e "${GREEN}Doppler logged in.${NC}"
        
        # Setup project config (assuming user has 'chatbot-templates' project and 'dev_rag' config)
        # We'll try to setup, but if it fails (e.g. project doesn't exist), we warn.
        if doppler setup --project chatbot-templates --config dev_rag --no-interactive; then
             echo -e "${GREEN}Doppler configured to 'chatbot-templates' / 'dev_rag'.${NC}"
        else
             echo -e "${YELLOW}Could not auto-configure Doppler project/config. Please ensure 'chatbot-templates' project exists.${NC}"
             echo -e "${YELLOW}Falling back to local .env check...${NC}"
        fi
    else
        echo -e "${YELLOW}Doppler not logged in. Run 'doppler login' to use secrets management.${NC}"
    fi
else
    echo -e "${YELLOW}Doppler CLI not found.${NC}"
fi

# Check for .env
if [ ! -f .env ]; then
    echo -e "${YELLOW}.env file not found.${NC}"
    if [ -f .env.example ]; then
        echo -e "${GREEN}Creating .env from .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}IMPORTANT: Please edit .env and add your API keys!${NC}"
    else
        echo -e "${RED}Error: .env.example not found! Cannot setup environment.${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}.env file exists.${NC}"
fi

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo -e "${RED}requirements.txt not found!${NC}"
fi

echo -e "${GREEN}Setup complete!${NC}"
echo -e "To run the server:"
echo -e "  ${YELLOW}uvicorn server:app --reload${NC}"
echo -e "Or with Doppler:"
echo -e "  ${YELLOW}doppler run -- uvicorn server:app --reload${NC}"
