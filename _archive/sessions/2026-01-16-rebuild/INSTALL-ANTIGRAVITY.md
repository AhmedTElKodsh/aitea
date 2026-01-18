# OpenCode Antigravity Auth Plugin Installation Guide

## Overview

This guide will help you install and configure the `opencode-antigravity-auth` plugin to use Google Antigravity models (including Claude Opus 4.5, Sonnet 4.5, and Gemini 3 Pro) with OpenCode.

## What You Get

- **Claude Opus 4.5, Sonnet 4.5** and **Gemini 3 Pro/Flash** via Google OAuth
- **Multi-account support** - add multiple Google accounts, auto-rotates when rate-limited
- **Dual quota system** - access both Antigravity and Gemini CLI quotas
- **Thinking models** - extended thinking for Claude and Gemini 3
- **Google Search grounding** - enable web search for Gemini models

## Installation Steps

### Step 1: Create Config Directory

Open PowerShell or Command Prompt and run:

```powershell
# Create the config directory if it doesn't exist
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.config\opencode"
```

Or in CMD:

```cmd
mkdir "%USERPROFILE%\.config\opencode" 2>nul
```

### Step 2: Copy Configuration File

Copy the `opencode-antigravity-setup.json` file from this directory to:

```
C:\Users\Ahmed\.config\opencode\opencode.json
```

You can do this with PowerShell:

```powershell
Copy-Item "opencode-antigravity-setup.json" "$env:USERPROFILE\.config\opencode\opencode.json"
```

Or manually copy the file using File Explorer.

### Step 3: Authenticate with Google

Run the following command to authenticate:

```bash
opencode auth login
```

This will:

1. Open your browser for Google OAuth
2. Ask you to authenticate with your Google account
3. Store your credentials in `~/.config/opencode/antigravity-accounts.json`

### Step 4: (Optional) Add Multiple Accounts

For higher quotas and automatic rotation when rate-limited, you can add multiple Google accounts:

```bash
opencode auth login
# Run this command again to add more accounts
```

### Step 5: Test the Installation

Test with a simple command:

```bash
opencode run "Hello" --model=google/antigravity-claude-sonnet-4-5-thinking --variant=max
```

Or test with Gemini:

```bash
opencode run "Hello" --model=google/antigravity-gemini-3-pro --variant=high
```

## Available Models

### Antigravity Quota (Claude + Gemini 3)

- `antigravity-gemini-3-pro` - Gemini 3 Pro with thinking (variants: low, high)
- `antigravity-gemini-3-flash` - Gemini 3 Flash with thinking (variants: minimal, low, medium, high)
- `antigravity-claude-sonnet-4-5` - Claude Sonnet 4.5
- `antigravity-claude-sonnet-4-5-thinking` - Claude Sonnet with extended thinking (variants: low, max)
- `antigravity-claude-opus-4-5-thinking` - Claude Opus with extended thinking (variants: low, max)

### Gemini CLI Quota (Separate from Antigravity)

- `gemini-2.5-flash` - Gemini 2.5 Flash
- `gemini-2.5-pro` - Gemini 2.5 Pro
- `gemini-3-flash-preview` - Gemini 3 Flash (preview)
- `gemini-3-pro-preview` - Gemini 3 Pro (preview)

## Using Variants

Variants control thinking levels and budgets:

```bash
# Low thinking budget (8192 tokens)
opencode run "Solve this problem" --model=google/antigravity-claude-sonnet-4-5-thinking --variant=low

# Max thinking budget (32768 tokens)
opencode run "Complex problem" --model=google/antigravity-claude-opus-4-5-thinking --variant=max

# Gemini with high thinking
opencode run "Analyze this" --model=google/antigravity-gemini-3-pro --variant=high
```

## Troubleshooting

### Issue: "Model not found"

Make sure you've copied the configuration file to the correct location:

```
C:\Users\Ahmed\.config\opencode\opencode.json
```

### Issue: Authentication fails

1. Delete the accounts file:
   ```powershell
   Remove-Item "$env:USERPROFILE\.config\opencode\antigravity-accounts.json"
   ```
2. Re-authenticate:
   ```bash
   opencode auth login
   ```

### Issue: Safari OAuth callback fails (macOS)

Use Chrome or Firefox instead, or disable Safari's HTTPS-Only Mode temporarily.

### Issue: Port conflict (Address already in use)

On Windows PowerShell:

```powershell
netstat -ano | findstr :51121
taskkill /PID <PID> /F
opencode auth login
```

### Issue: Rate limiting

Add multiple Google accounts for automatic rotation:

```bash
opencode auth login
# Add as many accounts as needed
```

## Configuration Files Location

All configuration files are stored in `~/.config/opencode/`:

- Main config: `~/.config/opencode/opencode.json`
- Accounts: `~/.config/opencode/antigravity-accounts.json`
- Plugin config: `~/.config/opencode/antigravity.json`
- Debug logs: `~/.config/opencode/antigravity-logs/`

On Windows, `~` resolves to `C:\Users\YourName`.

## Advanced Configuration

### Enable Debug Logging

```bash
set OPENCODE_ANTIGRAVITY_DEBUG=1
opencode
```

### Multi-Account Load Balancing

Create `~/.config/opencode/antigravity.json`:

```json
{
  "$schema": "https://raw.githubusercontent.com/NoeFabris/opencode-antigravity-auth/main/assets/antigravity.schema.json",
  "account_selection_strategy": "hybrid",
  "pid_offset_enabled": false,
  "quiet_mode": false,
  "debug": false
}
```

Strategies:

- `"sticky"` - Use same account until rate-limited (best for 1 account)
- `"hybrid"` - Default, works great for 2-5 accounts
- `"round-robin"` - Best for 5+ accounts

## Resources

- GitHub Repository: https://github.com/NoeFabris/opencode-antigravity-auth
- Documentation: https://github.com/NoeFabris/opencode-antigravity-auth/tree/main/docs
- Issues: https://github.com/NoeFabris/opencode-antigravity-auth/issues

## Legal Notice

This plugin is for personal/internal development only. By using it, you acknowledge:

- May violate ToS of AI model providers
- Providers may suspend or ban accounts
- No guarantees - APIs may change without notice
- You assume all legal, financial, and technical risks

Not affiliated with Google. "Antigravity", "Gemini", and "Google" are trademarks of Google LLC.

## License

MIT License
