#!/bin/bash

# Remaining internal plugins to install
PLUGINS=(
    "clangd-lsp"
    "claude-md-management"
    "code-simplifier"
    "csharp-lsp"
    "frontend-design"
    "gopls-lsp"
    "hookify"
    "jdtls-lsp"
    "kotlin-lsp"
    "learning-output-style"
    "lua-lsp"
    "php-lsp"
    "plugin-dev"
    "pr-review-toolkit"
    "pyright-lsp"
    "rust-analyzer-lsp"
    "security-guidance"
    "swift-lsp"
    "typescript-lsp"
)

echo "Installing ${#PLUGINS[@]} remaining internal plugins..."
echo ""

for plugin in "${PLUGINS[@]}"; do
    echo "Installing $plugin..."
    claude plugin install "$plugin@claude-plugins-official"
    echo ""
done

echo "Installation complete!"
echo "Run 'claude plugin list' to verify."
