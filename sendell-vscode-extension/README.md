# Sendell VS Code Extension

Deep integration between Sendell AI agent and VS Code for multi-project management and Claude Code collaboration.

## Features

- **WebSocket Connection**: Real-time bidirectional communication with Sendell Python server
- **Terminal Monitoring**: Capture terminal output and execution events (coming in Phase 2)
- **Claude Code Detection**: Identify and interact with Claude Code sessions (coming in Phase 3)
- **Project Context**: Extract and cache project information efficiently (coming in Phase 4)
- **Multi-Agent Coordination**: Collaborate with Claude Code sessions (coming in Phase 6)

## Requirements

- VS Code 1.93.0 or higher
- Sendell Python agent running on `ws://localhost:7000`
- Node.js 20.x LTS (for development)

## Installation

### From VSIX File

1. Download `sendell-extension-0.3.0.vsix`
2. Open VS Code
3. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
4. Type `Install from VSIX...`
5. Select the downloaded `.vsix` file
6. Reload VS Code when prompted

### From Command Line

```bash
code --install-extension sendell-extension-0.3.0.vsix
```

## Configuration

Open VS Code settings (`Ctrl+,`) and search for "Sendell":

| Setting | Description | Default |
|---------|-------------|---------|
| `sendell.serverUrl` | Sendell Python server WebSocket URL | `ws://localhost:7000` |
| `sendell.autoConnect` | Automatically connect on startup | `true` |
| `sendell.reconnectInterval` | Reconnection interval in milliseconds | `5000` |
| `sendell.maxReconnectAttempts` | Max reconnection attempts before giving up | `10` |
| `sendell.logLevel` | Logging level (debug/info/warn/error) | `info` |

## Commands

Press `Ctrl+Shift+P` and type:

- **Sendell: Connect to Server** - Manually connect to Sendell Python server
- **Sendell: Disconnect from Server** - Disconnect from server
- **Sendell: Show Connection Status** - Display current connection status
- **Sendell: Show Logs** - Open Sendell extension logs

## Status Bar

The Sendell status bar item (bottom-right) shows connection status:

- 🔌 Connected
- 🔄 Connecting/Reconnecting
- ⚡ Disconnected
- ❌ Connection failed

Click the status bar item to see detailed status.

## Usage

### Phase 1: Basic Connection (Current)

1. Start Sendell Python server with WebSocket support
2. Open VS Code with Sendell extension installed
3. Extension auto-connects to `ws://localhost:7000`
4. Check status bar for connection confirmation

### Phase 2+: Advanced Features (Coming Soon)

- Terminal monitoring and command execution
- Claude Code session detection
- Project context extraction
- Multi-agent task delegation

## Development

### Building from Source

```bash
cd sendell-vscode-extension
npm install
npm run compile
```

### Packaging

```bash
npm run package
# Output: sendell-extension-0.3.0.vsix
```

### Debugging

1. Open `sendell-vscode-extension` folder in VS Code
2. Press `F5` to launch Extension Development Host
3. Check Debug Console for logs

## Troubleshooting

### Extension won't connect

1. Verify Sendell Python server is running:
   ```bash
   # Check if port 7000 is listening
   netstat -an | grep 7000
   ```

2. Check extension logs:
   - Command: `Sendell: Show Logs`
   - Look for connection errors

3. Verify server URL in settings matches your setup

### Connection keeps dropping

- Increase `sendell.maxReconnectAttempts` in settings
- Check network firewall settings
- Ensure Sendell Python server is stable

### No logs appearing

- Set `sendell.logLevel` to `debug` for verbose logging
- Reload VS Code after changing log level

## Architecture

```
VS Code Extension (TypeScript)
    ├── WebSocket Client (connects to Python server)
    ├── Logger (OutputChannel)
    ├── Status Bar (connection indicator)
    └── Command Palette (user commands)
        ↓
    ws://localhost:7000
        ↓
Sendell Python Server
```

## Version

Current version: **0.3.0** (Phase 1 - Scaffold)

## License

Private extension for personal use only.

## Support

For issues or questions, check:
- Extension logs: `Sendell: Show Logs`
- Sendell Python logs: Check Python console output
- GitHub Issues: [Project repository]
