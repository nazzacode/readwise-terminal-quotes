#!/usr/bin/env bash

# Add to shell startup (bash/zsh)
QUOTE_CMD="python3 ~/Documents/readwise-terminal-quotes/quote.py"

echo "Add this line to your shell config:"
echo
echo "# Readwise quote on startup"
echo "$QUOTE_CMD"
echo 

# Check current shell
if [ -n "$ZSH_VERSION" ]; then
    CONFIG_FILE="~/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    CONFIG_FILE="~/.bashrc"
else
    CONFIG_FILE="~/.profile"
fi

echo "For your shell, add to: $CONFIG_FILE"
echo
echo "Don't forget to set READWISE_TOKEN:"
echo "export READWISE_TOKEN='your_token_here'"