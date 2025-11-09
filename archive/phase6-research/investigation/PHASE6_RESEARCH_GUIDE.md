# TECHNICAL RESEARCH GUIDE - Multi-Terminal & Multi-Project Management

**Version**: 2.0
**Date**: 2025-11-04
**Purpose**: Build robust system for managing multiple VS Code projects and terminals programmatically

---

## 🎯 RESEARCH OBJECTIVE

Build a **production-ready system** capable of:

1. **Managing multiple VS Code instances** - Detect, monitor, and control multiple VS Code windows
2. **Terminal orchestration** - Create, read, write, and close terminals programmatically
3. **Project intelligence** - Auto-detect project type, configuration, and run commands
4. **Process monitoring** - Detect running processes, ports in use, and application state
5. **Inter-process communication** - Coordinate between multiple CLI tools/agents
6. **Dynamic UI** - Build responsive dashboard with real-time updates

This guide focuses on **best practices**, **official documentation**, and **proven architectures** for these capabilities.

---

## 📚 RESEARCH AREAS

### 1. VS Code Extension Development
- WebSocket client implementation
- Extension lifecycle management
- Terminal API capabilities

### 2. Terminal Management
- Programmatic terminal control
- Shell integration
- Output buffering strategies

### 3. Project Configuration Parsing
- Detection algorithms
- Config file formats (package.json, pyproject.toml, Cargo.toml, etc.)
- Command extraction

### 4. Process & Port Detection
- Child process enumeration
- Port scanning techniques
- State detection heuristics

### 5. Inter-Process Communication
- Coordination patterns
- Message protocols
- File-based locking

### 6. GUI Development (Python)
- Tkinter advanced patterns
- Threading and async UI updates
- Responsive layouts

---

# AREA 1: VS CODE EXTENSION DEVELOPMENT

## 📖 TOPIC 1.1: WebSocket Client Implementation in Extensions

### Objective
Understand how to create **reliable WebSocket connections** from a VS Code extension to an external server.

### Research Questions

**1.1.1 WebSocket Libraries for Node.js/TypeScript**

Compare available libraries:

| Library | Pros | Cons | Use Case |
|---------|------|------|----------|
| `ws` | Popular, well-documented | Requires manual reconnect | Server + Client |
| `websocket` | Auto-reconnect built-in | Less popular | Client-focused |
| Native WebSocket API | Browser-compatible | Node.js needs polyfill | Browser extensions |

**Questions:**
- Which library is recommended for VS Code extensions specifically?
- Does VS Code environment affect WebSocket behavior?
- Are there VS Code extension samples using WebSocket?

**Example needed:**
```typescript
// Production-ready WebSocket client with:
// - Auto-reconnect with exponential backoff
// - Heartbeat/ping-pong
// - Error handling
// - Message queueing during disconnect

class RobustWebSocketClient {
    private ws: WebSocket;
    private reconnectAttempts: number;
    private messageQueue: any[];

    connect(url: string) {
        // Implementation details needed
    }

    private handleDisconnect() {
        // Exponential backoff logic needed
    }

    send(message: any) {
        // Queue if disconnected, send when reconnected
    }
}
```

**Documentation to consult:**
- `ws` npm package documentation
- VS Code Extension API: Network requests
- WebSocket RFC 6455 (protocol specification)

---

**1.1.2 Reconnection Strategies**

**Best practices for handling connection loss:**

Research:
- Exponential backoff algorithm (timing formula)
- Maximum retry attempts before giving up
- Message queue handling during disconnect
- User notification strategies

**Example needed:**
```typescript
// Exponential backoff implementation
function calculateBackoff(attempt: number): number {
    // Formula: min(maxDelay, baseDelay * 2^attempt)
    // Example: 1s, 2s, 4s, 8s, 16s, 32s, 60s (max)
    // Implementation needed
}
```

**Documentation:**
- Articles: "WebSocket reconnection patterns"
- AWS/Azure best practices for WebSocket clients
- Resilient network programming guides

---

**1.1.3 Heartbeat & Connection Monitoring**

**Keep-alive mechanisms:**

Research:
- Ping/pong frame protocol (WebSocket built-in)
- Application-level heartbeat (custom messages)
- Timeout detection (when to consider connection dead)

**Example needed:**
```typescript
// Heartbeat implementation
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.ping(); // or send custom heartbeat message
    }
}, 30000); // Every 30 seconds - is this optimal?

ws.on('pong', () => {
    // Reset timeout
});
```

**Questions:**
- What's the recommended heartbeat interval?
- Should heartbeat be ping/pong or custom message?
- How to handle missed heartbeats?

**Documentation:**
- WebSocket protocol specification (ping/pong frames)
- Load balancer timeouts (AWS ALB, nginx)

---

## 📖 TOPIC 1.2: Extension Activation & Lifecycle

### Objective
Understand VS Code extension lifecycle to ensure proper initialization and cleanup.

### Research Questions

**1.2.1 Activation Events**

VS Code extensions activate based on events:

```json
// package.json
"activationEvents": [
    "*",                    // Activate on startup (all windows)
    "onStartupFinished",   // After UI is ready
    "onLanguage:python",   // When Python file opened
    "onCommand:myCmd"      // When command executed
]
```

**Questions:**
- What's the difference between `"*"` and `"onStartupFinished"`?
- Performance implications of each activation event?
- When is the best time to initialize WebSocket connection?
- Can extension activate in multiple VS Code windows simultaneously?

**Documentation:**
- VS Code Extension API: Activation Events
- Extension Capabilities documentation

---

**1.2.2 Extension Context & Subscriptions**

```typescript
export function activate(context: vscode.ExtensionContext) {
    // context.subscriptions manages disposables
    // context.globalState for persistence
    // context.extensionPath for resources

    const disposable = vscode.commands.registerCommand('cmd', () => {});
    context.subscriptions.push(disposable);
}

export function deactivate() {
    // Cleanup: close connections, save state
}
```

**Questions:**
- What happens if `deactivate()` is not implemented?
- Does VS Code wait for async cleanup in `deactivate()`?
- How to ensure WebSocket closes gracefully?

**Documentation:**
- VS Code Extension API: Extension Context
- Disposables pattern documentation

---

**1.2.3 Multi-Window Scenarios**

**Question:** How do extensions behave with multiple VS Code windows?

Research:
- Does each window get its own extension instance?
- Can extensions share state across windows?
- How to coordinate between multiple instances?

**Example scenario:**
```
User has 3 VS Code windows open:
- Window A: Project "sendell"
- Window B: Project "GSIAF"
- Window C: Project "experimentos"

Does extension activate 3 times?
Can they all connect to the same WebSocket server?
```

**Documentation:**
- VS Code Extension Host architecture
- Multi-root workspaces guide

---

## 📖 TOPIC 1.3: Extension Debugging Best Practices

### Objective
Learn effective debugging techniques for VS Code extensions.

### Research Questions

**1.3.1 Output Channels**

```typescript
const outputChannel = vscode.window.createOutputChannel('MyExtension');
outputChannel.appendLine('Log message');
outputChannel.show(); // Make visible to user
```

**Best practices:**
- Logging levels (INFO, WARN, ERROR)
- When to show output channel automatically
- Performance impact of excessive logging

**Documentation:**
- VS Code Extension API: Output Channel
- Debugging extensions guide

---

**1.3.2 Common Extension Pitfalls**

Research common mistakes:

1. **Event listener leaks** - Not disposing listeners
2. **Async/await mistakes** - Race conditions, unhandled promises
3. **Module resolution** - ESM vs CommonJS issues
4. **Thread safety** - Extension Host vs UI process

**Questions:**
- What's the Extension Host process model?
- Can extensions block the UI thread?
- Best practices for async operations?

**Documentation:**
- VS Code Extension Samples (GitHub)
- Extension troubleshooting guide
- Node.js async best practices

---

# AREA 2: TERMINAL MANAGEMENT

## 📖 TOPIC 2.1: Terminal API Complete Reference

### Objective
Master programmatic terminal control in VS Code.

### Research Questions

**2.1.1 Creating Terminals**

```typescript
const terminal = vscode.window.createTerminal({
    name: string,
    cwd: string,           // Working directory
    env: Record<string, string>, // Environment variables
    shellPath?: string,    // Override default shell
    shellArgs?: string[],  // Shell arguments
    hideFromUser?: boolean // Create invisible terminal
});
```

**Questions:**
- Can terminals be created "invisibly" (no UI presence)?
- How to specify shell type (PowerShell, CMD, Bash)?
- Cross-platform considerations (Windows vs Linux/Mac)?
- Maximum number of terminals?

**Documentation:**
- VS Code API: `window.createTerminal()`
- Terminal options reference

---

**2.1.2 Sending Text to Terminals**

```typescript
terminal.sendText(text: string, addNewLine?: boolean);
```

**Questions:**
- Is `sendText()` synchronous or asynchronous?
- How to send multiple commands in sequence?
- How to detect when a command finishes?
- Can you send control characters (Ctrl+C, Ctrl+D)?

**Control characters:**
```typescript
terminal.sendText('\x03'); // Ctrl+C - Interrupt
terminal.sendText('\x04'); // Ctrl+D - EOF
terminal.sendText('\x1A'); // Ctrl+Z - Suspend (Unix)
```

**Questions:**
- Do control characters work cross-platform?
- Complete list of useful control characters?

**Documentation:**
- Terminal API: sendText()
- ASCII control characters table
- ANSI escape codes reference

---

**2.1.3 Closing & Disposing Terminals**

```typescript
terminal.dispose(); // Close terminal
```

**Questions:**
- What happens to running processes when terminal is disposed?
- Are processes killed automatically?
- How to force-kill a process?
- Can a disposed terminal be recovered?

**Documentation:**
- Terminal lifecycle documentation
- Process management in Node.js

---

**2.1.4 Reading Terminal Output**

VS Code provides **Shell Integration API** (v1.93+):

```typescript
vscode.window.onDidStartTerminalShellExecution((event) => {
    const execution = event.execution;
    const command = execution.commandLine.value;

    // Stream output
    const stream = execution.read();
    for await (const data of stream) {
        console.log(data);
    }
});

vscode.window.onDidEndTerminalShellExecution((event) => {
    const exitCode = event.exitCode;
});
```

**Questions:**
- Does Shell Integration work on all shells?
- How to enable Shell Integration?
- What if Shell Integration is not available?
- Can you read terminal history (lines before stream started)?
- Buffer size limitations?

**Documentation:**
- VS Code Shell Integration API (v1.93+)
- Terminal shell integration guide

---

## 📖 TOPIC 2.2: Shell Integration Deep Dive

### Objective
Understand capabilities and limitations of Shell Integration API.

### Research Questions

**2.2.1 Capabilities Matrix**

Research what Shell Integration provides:

| Feature | Available | API Method |
|---------|-----------|------------|
| Detect command start | ✅ | onDidStartTerminalShellExecution |
| Detect command end | ✅ | onDidEndTerminalShellExecution |
| Stream output | ✅ | execution.read() |
| Get exit code | ✅ | event.exitCode |
| Read history | ❓ | ? |
| Detect prompt | ❓ | ? |

**Questions:**
- Can you access terminal buffer before Shell Integration was enabled?
- Is there a way to read the entire terminal history?
- How to detect if terminal is waiting for input (showing prompt)?

---

**2.2.2 Output Buffering Strategies**

When reading terminal output, how to store it efficiently?

**Strategies:**

1. **Tail buffer** - Keep last N lines
   ```typescript
   const buffer = new Array<string>();
   const MAX_LINES = 100;

   for await (const data of stream) {
       buffer.push(data);
       if (buffer.length > MAX_LINES) {
           buffer.shift(); // Remove oldest
       }
   }
   ```

2. **Full buffer with rotation**
3. **Selective storage** (only errors, specific patterns)

**Questions:**
- What's a reasonable buffer size?
- Performance implications of large buffers?
- Best data structure (Array, LinkedList, Circular buffer)?

**Documentation:**
- Data structures for log buffering
- Memory-efficient stream processing

---

**2.2.3 Parsing Terminal Output**

Terminal output contains ANSI escape codes:

```
\x1b[32mGreen text\x1b[0m
\x1b[1mBold\x1b[22m
\x1b[2J\x1b[H - Clear screen
```

**Questions:**
- Should ANSI codes be stripped or preserved?
- Libraries for parsing ANSI codes?
- How to extract plain text from styled output?

**Documentation:**
- ANSI escape code specification
- npm packages: `ansi-regex`, `strip-ansi`, `ansi-parser`

---

## 📖 TOPIC 2.3: Terminal State Detection

### Objective
Detect the current state of a terminal (idle, executing, waiting input).

### Research Questions

**2.3.1 State Machine**

Define terminal states:

```typescript
enum TerminalState {
    IDLE,           // Showing prompt, no process running
    EXECUTING,      // Running a command
    WAITING_INPUT,  // Process waiting for user input (REPL, interactive CLI)
    PAUSED          // Process suspended (Ctrl+Z on Unix)
}
```

**Questions:**
- How to detect each state programmatically?
- Can Shell Integration API provide state?
- Heuristics for detection (e.g., no output for N seconds = idle)?

---

**2.3.2 Detecting "Waiting for Input"**

Some processes wait for input:
- Python REPL: `>>> `
- Node REPL: `> `
- Git commit: Opens editor
- npm init: Asks questions

**Questions:**
- How to detect interactive prompts?
- Common prompt patterns to recognize?
- Timeout-based detection (no output = waiting)?

**Regex patterns to research:**
```typescript
const PROMPT_PATTERNS = [
    />>> $/,        // Python REPL
    /> $/,          // Node REPL
    /\$ $/,         // Bash prompt
    /PS .+> $/,     // PowerShell prompt
];
```

---

# AREA 3: PROJECT CONFIGURATION PARSING

## 📖 TOPIC 3.1: Project Type Detection

### Objective
Automatically identify project type by analyzing files.

### Research Questions

**3.1.1 Signature Files**

Research file patterns for each project type:

| Project Type | Primary File | Secondary Files | Priority |
|--------------|-------------|-----------------|----------|
| Node.js | package.json | node_modules/ | 1 |
| Python (uv) | pyproject.toml | uv.lock | 1 |
| Python (poetry) | pyproject.toml | poetry.lock | 1 |
| Python (pip) | requirements.txt | - | 2 |
| Rust | Cargo.toml | Cargo.lock | 1 |
| Go | go.mod | go.sum | 1 |
| Java (Maven) | pom.xml | - | 1 |
| Java (Gradle) | build.gradle | - | 1 |
| .NET | *.csproj, *.sln | - | 1 |
| Ruby | Gemfile | Gemfile.lock | 1 |
| PHP | composer.json | composer.lock | 1 |

**Questions:**
- How to handle monorepos (multiple project types)?
- How to detect framework within project type (React vs Angular)?
- Subdirectory handling (ignore node_modules, .git, etc.)?

---

**3.1.2 Framework Detection**

Within Node.js, detect framework:

```json
// package.json dependencies can reveal framework
{
  "dependencies": {
    "react": "^18.0.0",      // React project
    "next": "^13.0.0",       // Next.js project
    "@angular/core": "^15",  // Angular project
    "vue": "^3.0.0",         // Vue project
    "express": "^4.0.0"      // Express backend
  }
}
```

**Questions:**
- Which dependencies are framework indicators?
- How to prioritize if multiple frameworks present?
- Does framework detection affect run commands?

**Documentation:**
- npm package registry
- Framework official documentation

---

## 📖 TOPIC 3.2: Configuration File Parsing

### Objective
Parse common configuration files to extract useful information.

### Research Questions

**3.2.1 package.json Structure**

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
    "dev": "vite",
    "start": "node server.js",
    "build": "tsc && vite build",
    "test": "jest"
  },
  "dependencies": {},
  "devDependencies": {},
  "workspaces": ["packages/*"]
}
```

**Questions:**
1. **Run command priority**: How to choose between `dev`, `start`, `serve`?
   - Logic: Check script content? Keywords like "vite", "webpack"?
   - Default priority order?

2. **Entry point**: How to find main file?
   - Check `"main"` field
   - Check `"module"` field
   - Default: `index.js`, `index.ts`

3. **Monorepo detection**: How to detect?
   - Presence of `"workspaces"` field
   - Multiple package.json in subdirectories

**Documentation:**
- npm package.json specification
- Yarn workspaces documentation
- npm workspaces documentation

---

**3.2.2 pyproject.toml Parsing**

```toml
[project]
name = "my-app"
version = "0.1.0"
requires-python = ">=3.10"

[project.scripts]
my-app = "my_app.__main__:main"

[tool.uv]
dev-dependencies = ["pytest"]

[tool.poetry]
# If using Poetry instead of uv
```

**Questions:**
1. **Detect package manager**: uv vs poetry vs pip
   - Check for `uv.lock`, `poetry.lock`, `requirements.txt`
   - Sections: `[tool.uv]`, `[tool.poetry]`

2. **Run command construction**:
   - With scripts: `uv run <script-name>`
   - Without scripts: `python -m <package-name>`

3. **Entry point**: Where defined?
   - `[project.scripts]` section
   - `[tool.poetry.scripts]` section

**Documentation:**
- PEP 518 (pyproject.toml specification)
- PEP 621 (Project metadata)
- uv documentation
- Poetry documentation

---

**3.2.3 Cargo.toml Parsing**

```toml
[package]
name = "my-app"
version = "0.1.0"
edition = "2021"

[[bin]]
name = "my-app"
path = "src/main.rs"

[dependencies]
tokio = "1.0"
```

**Questions:**
- Run command: Always `cargo run`?
- How to detect if binary vs library?
- Multiple binaries: `cargo run --bin <name>`?

**Documentation:**
- Cargo Book (official documentation)
- Cargo.toml manifest format

---

**3.2.4 Other Formats (Brief Overview)**

Research minimal info for:

**Go (go.mod):**
```go
module example.com/myapp

go 1.21
```
- Run: `go run .` or `go run main.go`

**Maven (pom.xml):**
- Run: `mvn spring-boot:run` or `mvn exec:java`

**Gradle (build.gradle):**
- Run: `gradle run` or `./gradlew run`

**Documentation links for each**

---

## 📖 TOPIC 3.3: Command Extraction

### Objective
Extract the "main command" to run each project type.

### Research Questions

**3.3.1 Default Commands per Project Type**

Create reference table:

| Project Type | Default Run Command | Alternatives |
|--------------|-------------------|--------------|
| Node.js (generic) | `npm start` | `node index.js` |
| Node.js (Vite) | `npm run dev` | `vite` |
| Node.js (Next.js) | `npm run dev` | `next dev` |
| Python (uv) | `uv run python -m <pkg>` | - |
| Rust | `cargo run` | - |
| Go | `go run .` | `go run main.go` |

**Questions:**
- How to prioritize between alternatives?
- When to use script command vs direct command?

---

**3.3.2 Script Selection Logic**

Algorithm to choose the best script:

```typescript
function selectMainScript(scripts: Record<string, string>): string {
    // Priority order
    const priority = ['dev', 'start', 'serve'];

    for (const key of priority) {
        if (scripts[key]) {
            return key;
        }
    }

    // Fallback: first script that looks like a dev server
    for (const [key, value] of Object.entries(scripts)) {
        if (value.includes('vite') || value.includes('webpack')) {
            return key;
        }
    }

    return 'start'; // Default fallback
}
```

**Questions:**
- Is this logic sound?
- Edge cases to consider?
- How to handle non-standard script names?

---

# AREA 4: PROCESS & PORT DETECTION

## 📖 TOPIC 4.1: Child Process Detection

### Objective
Detect processes spawned by terminals.

### Research Questions

**4.1.1 Getting Terminal Process ID**

```typescript
const terminal: vscode.Terminal = ...;
const pid = await terminal.processId; // Returns Promise<number | undefined>
```

**Questions:**
- Is `processId` always available?
- What if terminal is remote (SSH, WSL)?
- Does PID persist across terminal restarts?

**Documentation:**
- VS Code Terminal API: processId

---

**4.1.2 Enumerating Child Processes**

**Windows (PowerShell):**
```powershell
Get-CimInstance Win32_Process | Where-Object { $_.ParentProcessId -eq $pid }
```

**Linux/Mac:**
```bash
ps --ppid $pid
pgrep -P $pid
```

**Node.js approach:**

Option 1: Execute OS command
```typescript
import { execSync } from 'child_process';

function getChildProcesses(pid: number): Process[] {
    const cmd = process.platform === 'win32'
        ? `powershell "Get-CimInstance Win32_Process | Where ParentProcessId -eq ${pid}"`
        : `ps --ppid ${pid}`;

    const output = execSync(cmd).toString();
    // Parse output
}
```

Option 2: Use library
- Research: `ps-list`, `ps-tree`, `process-list` npm packages

**Questions:**
- Which approach is more reliable?
- Performance implications?
- Cross-platform compatibility?

**Documentation:**
- Node.js child_process module
- npm packages: ps-list, ps-tree

---

**4.1.3 Process Information Extraction**

What info to extract from each child process:

```typescript
interface ChildProcess {
    pid: number;
    name: string;        // Process name (node.exe, python.exe)
    command: string;     // Full command with arguments
    cpu: number;         // CPU usage percentage
    memory: number;      // Memory usage (MB)
    startTime: Date;     // When process started
}
```

**Questions:**
- How to get full command line with arguments?
- Cross-platform differences?
- Performance cost of getting detailed info?

**Documentation:**
- Windows: Get-Process cmdlet
- Linux: /proc/<pid>/cmdline

---

## 📖 TOPIC 4.2: Port Detection

### Objective
Detect which ports are in use and which processes use them.

### Research Questions

**4.2.1 Listing Ports in Use**

**Windows:**
```powershell
netstat -ano | findstr LISTENING
```

**Linux/Mac:**
```bash
lsof -i -P -n | grep LISTEN
netstat -tuln
ss -tuln
```

**Questions:**
- Which command is fastest?
- How to parse output reliably?
- Cross-platform solution?

---

**4.2.2 Node.js Libraries for Port Detection**

Research libraries:

| Library | Purpose | Method |
|---------|---------|--------|
| `get-port` | Find available port | Scan for free port |
| `tcp-port-used` | Check if port in use | Test connection |
| `port-pid` | Get PID using port | OS command wrapper |
| `detect-port` | Find port in use | Network scan |

**Questions:**
- Which library is most reliable?
- Performance comparison?
- Do they work cross-platform?

**Example needed:**
```typescript
import portUsed from 'tcp-port-used';

async function isPortInUse(port: number): Promise<boolean> {
    return await portUsed.check(port, 'localhost');
}

// Usage
if (await isPortInUse(3000)) {
    console.log('Dev server likely running on port 3000');
}
```

**Documentation:**
- npm: get-port, tcp-port-used, port-pid

---

**4.2.3 Extracting Port from Project Config**

Where ports are typically defined:

**Node.js (Vite):**
```javascript
// vite.config.js
export default {
    server: { port: 3000 }
}
```

**Node.js (Next.js):**
```javascript
// next.config.js
module.exports = {
    server: { port: 3000 }
}
```

**Environment variables:**
```
PORT=3000
VITE_PORT=5173
```

**package.json scripts:**
```json
"dev": "vite --port 3000"
```

**Questions:**
- How to parse each config format?
- Priorities when multiple sources?
- Default ports per framework?

**Default ports reference:**
- React (CRA): 3000
- Vite: 5173
- Angular: 4200
- Next.js: 3000
- FastAPI: 8000

---

## 📖 TOPIC 4.3: State Detection Heuristics

### Objective
Determine if a project is "running" (has active dev server or long-running process).

### Research Questions

**4.3.1 "Running" Definition**

A project is considered "running" if:

1. Has a port listening (dev server)
2. Has long-running child process (>30 seconds)
3. Terminal is in EXECUTING state

**Algorithm:**
```typescript
function isProjectRunning(project: Project): boolean {
    // Check 1: Port listening
    if (project.configuredPorts.some(p => isPortInUse(p))) {
        return true;
    }

    // Check 2: Long-running process
    const hasLongRunningProcess = project.terminals.some(t =>
        t.childProcesses.length > 0 &&
        (Date.now() - t.processStartTime) > 30_000
    );
    if (hasLongRunningProcess) {
        return true;
    }

    // Check 3: Terminal executing
    if (project.terminals.some(t => t.state === 'EXECUTING')) {
        return true;
    }

    return false;
}
```

**Questions:**
- Is 30 seconds a good threshold for "long-running"?
- Edge cases (build processes that run for 2 minutes)?
- False positives/negatives?

---

**4.3.2 Performance Optimization**

Detecting state is expensive (exec commands, network checks).

**Strategies:**

1. **Caching**: Cache results for N seconds
2. **Event-driven**: Only check when terminal event occurs
3. **Lazy evaluation**: Only check when user requests
4. **Prioritization**: Check ports first (fastest), then processes

**Questions:**
- Optimal cache duration?
- Trade-off between accuracy and performance?

**Example:**
```typescript
class ProjectStateCache {
    private cache = new Map<string, { state: boolean; timestamp: number }>();
    private CACHE_TTL = 10_000; // 10 seconds

    get(projectId: string): boolean | undefined {
        const entry = this.cache.get(projectId);
        if (!entry) return undefined;

        if (Date.now() - entry.timestamp > this.CACHE_TTL) {
            this.cache.delete(projectId);
            return undefined;
        }

        return entry.state;
    }
}
```

---

# AREA 5: INTER-PROCESS COMMUNICATION

## 📖 TOPIC 5.1: Message Protocols

### Objective
Design protocol for communication between processes/agents.

### Research Questions

**5.1.1 Protocol Design**

**Option A: JSON Messages**
```json
{
    "type": "command",
    "target": "agent_name",
    "payload": {
        "action": "run_command",
        "command": "npm run dev"
    }
}
```

**Option B: Structured Markers**
```
[AGENT:TARGET] Action: run_command
Command: npm run dev
```

**Questions:**
- Which format is easier to parse?
- Extensibility considerations?
- Human-readable vs machine-optimized?

---

**5.1.2 Coordination Patterns**

**File-based locking:**
```json
// coordination.json
{
    "locks": [
        {
            "resource": "src/main.py",
            "lockedBy": "agent_a",
            "lockedAt": "2025-11-04T10:00:00Z",
            "expiresAt": "2025-11-04T10:15:00Z"
        }
    ]
}
```

**Questions:**
- Is file-based locking reliable?
- Race condition handling?
- Lock timeout duration?

**Alternatives:**
- Database-based locking
- Redis for distributed locks
- OS-level file locks (flock)

**Documentation:**
- Distributed locking patterns
- File locking in Node.js (fs.flock)

---

## 📖 TOPIC 5.2: Task Queue Implementation

### Objective
Queue tasks for async execution.

### Research Questions

**5.2.1 Queue Design**

```typescript
interface Task {
    id: string;
    type: 'command' | 'file_edit' | 'analysis';
    priority: number;
    status: 'pending' | 'running' | 'completed' | 'failed';
    createdAt: Date;
    startedAt?: Date;
    completedAt?: Date;
}

class TaskQueue {
    private queue: Task[] = [];

    enqueue(task: Task) {
        // Insert by priority
    }

    dequeue(): Task | undefined {
        // Get highest priority task
    }

    getStatus(taskId: string): Task | undefined {
        // Query task status
    }
}
```

**Questions:**
- In-memory vs persistent queue?
- Priority algorithm?
- Concurrency handling?

**Documentation:**
- Data structures: Priority queue
- npm: bull, bee-queue (Redis-based queues)

---

# AREA 6: GUI DEVELOPMENT (Python/Tkinter)

## 📖 TOPIC 6.1: Advanced Tkinter Patterns

### Objective
Build responsive, dynamic UI in Tkinter.

### Research Questions

**6.1.1 Expandable/Collapsible Lists**

**Option A: Treeview**
```python
tree = ttk.Treeview(parent)
tree.insert('', 'end', 'project1', text='Project 1')
tree.insert('project1', 'end', text='  Terminal 1')
```

**Option B: Dynamic Frames**
```python
class ExpandableItem:
    def __init__(self, parent):
        self.header = tk.Button(parent, text="▶ Project", command=self.toggle)
        self.content = tk.Frame(parent)
        self.expanded = False

    def toggle(self):
        if self.expanded:
            self.content.pack_forget()
        else:
            self.content.pack()
```

**Questions:**
- Treeview vs custom frames: pros/cons?
- Can Treeview embed custom widgets (buttons, entries)?
- Performance with many items (100+ projects)?

**Documentation:**
- Tkinter Treeview documentation
- Dynamic widget creation patterns

---

**6.1.2 Visual Indicators**

**Colored circles for status:**

```python
# Option 1: Emoji
label = tk.Label(text="🟢 Running")

# Option 2: Canvas
canvas = tk.Canvas(width=20, height=20)
canvas.create_oval(5, 5, 15, 15, fill="green")

# Option 3: Unicode character
label = tk.Label(text="● Running", fg="green", font=("Arial", 14))
```

**Questions:**
- Which option is most cross-platform reliable?
- Can Tkinter do animated pulse effect?
- Color palette best practices?

**Documentation:**
- Tkinter Canvas widget
- Unicode symbols reference

---

**6.1.3 Input Validation**

```python
class ValidatedEntry(tk.Entry):
    def __init__(self, parent, validator):
        super().__init__(parent)
        self.validator = validator
        self.bind('<KeyRelease>', self.validate)

    def validate(self, event):
        value = self.get()
        if not self.validator(value):
            self.config(bg='#ffcccc')  # Light red
        else:
            self.config(bg='white')
```

**Questions:**
- Real-time validation vs on-submit?
- How to show validation errors?
- Async validation (checking if command is safe)?

---

## 📖 TOPIC 6.2: Threading & Async UI

### Objective
Keep UI responsive during long-running operations.

### Research Questions

**6.2.1 Threading Pattern**

```python
import threading
import queue

class Dashboard:
    def __init__(self):
        self.update_queue = queue.Queue()
        self.start_worker_thread()

    def start_worker_thread(self):
        thread = threading.Thread(target=self.worker)
        thread.daemon = True
        thread.start()

    def worker(self):
        while True:
            # Do expensive operation
            result = self.fetch_project_states()  # 2 seconds

            # Put result in queue
            self.update_queue.put(result)

    def process_queue(self):
        try:
            while True:
                result = self.update_queue.get_nowait()
                self.update_ui(result)
        except queue.Empty:
            pass

        # Schedule next check
        self.root.after(100, self.process_queue)
```

**Questions:**
- Is this the correct pattern for Tkinter?
- Thread safety concerns?
- Alternative: asyncio + tkinter?

**Documentation:**
- Python threading module
- Tkinter and threading best practices
- Queue module documentation

---

**6.2.2 Auto-Refresh Without Blocking**

```python
def auto_refresh(self):
    self.refresh()
    self.root.after(5000, self.auto_refresh)  # Every 5 seconds

def refresh(self):
    # This should not block UI
    # Use threading for expensive operations
    pass
```

**Questions:**
- Optimal refresh interval?
- How to cancel auto-refresh on window close?
- Memory leaks to watch for?

**Documentation:**
- Tkinter after() method
- Event loop in Tkinter

---

## 📖 TOPIC 6.3: Layout Best Practices

### Objective
Create responsive, professional layouts.

### Research Questions

**6.3.1 Grid vs Pack vs Place**

| Layout Manager | Use Case | Pros | Cons |
|----------------|----------|------|------|
| pack | Simple linear layouts | Easy | Limited control |
| grid | Table-like layouts | Flexible, powerful | Complex with many widgets |
| place | Absolute positioning | Pixel-perfect | Not responsive |

**Questions:**
- Can you mix layout managers?
- Best practices for responsive design?
- How to handle window resize?

---

**6.3.2 Scrollable Frames**

```python
canvas = tk.Canvas(parent)
scrollbar = ttk.Scrollbar(parent, command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

canvas.configure(yscrollcommand=scrollbar.set)
canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
```

**Questions:**
- Is there a simpler approach?
- Libraries that simplify scrollable frames?
- Mouse wheel scrolling support?

**Documentation:**
- Tkinter Canvas
- Scrollable frame implementations (GitHub gists)

---

# 📋 DELIVERABLE FORMAT

## Expected Structure: `PHASE6_RESEARCH_RESULTS.md`

```markdown
# RESEARCH RESULTS - Multi-Terminal Management

## AREA 1: VS CODE EXTENSION DEVELOPMENT

### TOPIC 1.1: WebSocket Client Implementation

#### Findings
[Your research findings]

#### Recommended Approach
[Technology/library recommendation with reasoning]

#### Code Example
```typescript
// Working implementation
[Your code]
```

#### Documentation Sources
- [URL 1]
- [URL 2]

#### Notes
[Additional observations, caveats, platform differences]

---

### TOPIC 1.2: Extension Activation

[Same structure...]

---

## AREA 2: TERMINAL MANAGEMENT

[Continue for all areas...]

```

---

# 🎯 RESEARCH PRIORITIZATION

## TIER 1: CRITICAL (Must have for any implementation)
1. WebSocket Client Implementation (1.1)
2. Terminal API Complete Reference (2.1)
3. Project Type Detection (3.1)
4. Child Process Detection (4.1)

## TIER 2: IMPORTANT (Core functionality)
5. Configuration File Parsing (3.2)
6. Port Detection (4.2)
7. Expandable Lists (6.1)
8. Threading & Async UI (6.2)

## TIER 3: VALUABLE (Enhanced features)
9. Shell Integration Deep Dive (2.2)
10. Command Extraction (3.3)
11. State Detection Heuristics (4.3)
12. Visual Indicators (6.1.2)

## TIER 4: OPTIONAL (Nice to have)
13. Message Protocols (5.1)
14. Task Queue (5.2)
15. Layout Best Practices (6.3)

---

# 📚 RECOMMENDED DOCUMENTATION SOURCES

## Official Documentation
- VS Code Extension API: https://code.visualstudio.com/api
- VS Code Extension Samples: https://github.com/microsoft/vscode-extension-samples
- Node.js Documentation: https://nodejs.org/docs/
- Python Tkinter: https://docs.python.org/3/library/tkinter.html

## Package Registries
- npm: https://www.npmjs.com/
- PyPI: https://pypi.org/

## Community Resources
- Stack Overflow
- GitHub repositories (search for similar projects)
- Medium/Dev.to articles on specific topics

## Specifications
- WebSocket Protocol (RFC 6455)
- ANSI Escape Codes
- package.json specification (npm docs)
- PEP 518, 621 (pyproject.toml)

---

**END OF RESEARCH GUIDE**

This guide is technology-agnostic and can be used for any project requiring multi-terminal and multi-project management capabilities.
