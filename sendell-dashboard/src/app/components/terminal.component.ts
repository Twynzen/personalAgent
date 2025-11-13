import { Component, Input, OnInit, OnDestroy, AfterViewInit, ViewChild, ElementRef, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';

@Component({
  selector: 'app-terminal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <!-- Modal Backdrop -->
    <div class="modal-backdrop" (click)="onBackdropClick()">
      <!-- Modal Content (click no se propaga al backdrop) -->
      <div class="modal-content" (click)="$event.stopPropagation()">
        <div class="terminal-container">
          <div class="terminal-header">
            <span class="terminal-title">{{ projectName }} - Terminal</span>
            <button class="terminal-close" (click)="closeTerminal()">&times;</button>
          </div>
          <div class="terminal-body" #terminalElement></div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    /* MODAL STYLES */
    .modal-backdrop {
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background: rgba(0, 0, 0, 0.85);
      z-index: 9999;
      display: flex;
      align-items: center;
      justify-content: center;
      animation: fadeIn 0.2s ease-out;
    }

    .modal-content {
      width: 90vw;
      height: 80vh;
      max-width: 1400px;
      animation: slideUp 0.3s ease-out;
    }

    @keyframes fadeIn {
      from { opacity: 0; }
      to { opacity: 1; }
    }

    @keyframes slideUp {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    /* TERMINAL STYLES */
    .terminal-container {
      width: 100%;
      height: 100%;
      background: #0a0a0a;
      border: 2px solid #00ff00;
      box-shadow: 0 0 40px rgba(0, 255, 0, 0.5);
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }

    .terminal-header {
      background: #1a1a1a;
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #00ff00;
      flex-shrink: 0;
    }

    .terminal-title {
      color: #00ff00;
      font-family: 'Consolas', 'Courier New', monospace;
      font-size: 0.9rem;
      font-weight: bold;
    }

    .terminal-close {
      background: none;
      border: none;
      color: #ff0055;
      font-size: 1.5rem;
      cursor: pointer;
      padding: 0;
      width: 30px;
      height: 30px;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.2s;
    }

    .terminal-close:hover {
      color: #fff;
      background: #ff0055;
      border-radius: 4px;
    }

    .terminal-body {
      flex: 1;
      padding: 0.5rem;
      overflow: hidden;
    }
  `]
})
export class TerminalComponent implements OnInit, AfterViewInit, OnDestroy {
  @Input() projectPid!: number;
  @Input() workspacePath!: string;
  @Input({ required: true }) projectName!: string;
  @Output() close = new EventEmitter<void>();

  @ViewChild('terminalElement', { static: false }) terminalElement!: ElementRef;

  private terminal!: Terminal;
  private fitAddon!: FitAddon;
  private ws!: WebSocket;
  private inputBuffer: string[] = []; // Buffer commands while WebSocket connects
  private isConnected: boolean = false;
  private currentLine: string = ''; // Accumulate current line until Enter

  ngOnInit() {
    // Lifecycle hook - component initialized but view not ready yet
    console.log('TerminalComponent: ngOnInit called for project', this.projectName);
  }

  ngAfterViewInit() {
    // View is ready, now we can access ViewChild
    console.log('TerminalComponent: ngAfterViewInit called, terminalElement:', this.terminalElement);

    if (!this.terminalElement) {
      console.error('TerminalComponent: terminalElement is undefined!');
      return;
    }

    this.initializeTerminal();
    this.connectWebSocket();
  }

  ngOnDestroy() {
    if (this.ws) {
      this.ws.close();
    }
    if (this.terminal) {
      this.terminal.dispose();
    }
  }

  private initializeTerminal() {
    console.log('[Terminal] Initializing xterm.js for project:', this.projectName);

    this.terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: '"Cascadia Code", "Consolas", "Courier New", monospace',
      theme: {
        background: '#0a0a0a',
        foreground: '#00ff00',
        cursor: '#00ff00',
        cursorAccent: '#0a0a0a',
        selectionBackground: '#00ff0040',
        black: '#000000',
        red: '#ff0055',
        green: '#00ff00',
        yellow: '#ffff00',
        blue: '#00ffff',
        magenta: '#ff00ff',
        cyan: '#00ffff',
        white: '#ffffff',
        brightBlack: '#555555',
        brightRed: '#ff0055',
        brightGreen: '#00ff00',
        brightYellow: '#ffff00',
        brightBlue: '#00ffff',
        brightMagenta: '#ff00ff',
        brightCyan: '#00ffff',
        brightWhite: '#ffffff'
      },
      allowProposedApi: true
    });

    console.log('[Terminal] Terminal instance created');

    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    console.log('[Terminal] FitAddon loaded');

    this.terminal.open(this.terminalElement.nativeElement);
    console.log('[Terminal] Terminal opened in DOM');

    this.fitAddon.fit();
    console.log('[Terminal] Terminal fitted to container');

    // Handle user input - process character by character
    this.terminal.onData((data) => {
      console.log('[Terminal] 📝 User typed data:', JSON.stringify(data), 'char code:', data.charCodeAt(0));

      // Check for special characters
      const code = data.charCodeAt(0);

      if (code === 13) {
        // Enter key - send accumulated command
        console.log('[Terminal] ⏎ Enter pressed - Sending command:', JSON.stringify(this.currentLine));
        this.terminal.write('\r\n'); // Echo newline locally
        this.sendCommand(this.currentLine + '\r\n'); // Send complete line with newline
        this.currentLine = ''; // Reset line
      } else if (code === 127 || code === 8) {
        // Backspace or Delete - handle locally
        if (this.currentLine.length > 0) {
          this.currentLine = this.currentLine.slice(0, -1);
          this.terminal.write('\b \b'); // Visual backspace (move back, space, move back)
          console.log('[Terminal] ⌫ Backspace - Current line:', JSON.stringify(this.currentLine));
        }
      } else if (code >= 32) {
        // Printable character - accumulate and echo locally
        this.currentLine += data;
        this.terminal.write(data); // Echo character immediately (local feedback)
        console.log('[Terminal] Typed:', JSON.stringify(data), 'Current line:', JSON.stringify(this.currentLine));
      }
    });
    console.log('[Terminal] onData handler registered');

    // NO welcome message - terminal starts completely clean
    // The backend will send the actual cmd.exe prompt

    // Resize on window resize
    window.addEventListener('resize', () => {
      this.fitAddon.fit();
    });
    console.log('[Terminal] ✅ Initialization complete');
  }

  private connectWebSocket() {
    const wsUrl = `ws://localhost:8765/ws/terminal/${this.projectPid}`;
    console.log('[WebSocket] Connecting to:', wsUrl);
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`[WebSocket] ✅ Connected for project ${this.projectPid}`);
      this.isConnected = true;

      // Clear terminal to remove any garbage that came through before connection
      this.terminal.clear();
      console.log('[WebSocket] Terminal cleared - ready for cmd.exe output');

      // Send any buffered input
      if (this.inputBuffer.length > 0) {
        console.log('[WebSocket] Sending', this.inputBuffer.length, 'buffered commands');
        this.inputBuffer.forEach(cmd => {
          this.ws.send(JSON.stringify({ type: 'input', data: cmd }));
        });
        this.inputBuffer = [];
      }
    };

    this.ws.onmessage = (event) => {
      console.log('[WebSocket] ⬇️ Message received:', event.data);
      const message = JSON.parse(event.data);

      if (message.type === 'output') {
        console.log('[WebSocket] Output stream:', message.stream, 'data:', message.data);
        // Write output to terminal WITHOUT extra newline (server already includes it)
        this.terminal.write(message.data);
      } else if (message.type === 'error') {
        console.error('[WebSocket] ❌ Error from server:', message.message);
        this.terminal.writeln(`\x1b[1;31m[Error: ${message.message}]\x1b[0m`);
      } else {
        console.warn('[WebSocket] ⚠️ Unknown message type:', message.type);
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] ❌ Connection error:', error);
      this.terminal.writeln('\x1b[1;31m[WebSocket error]\x1b[0m');
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] ❌ Connection closed. Code:', event.code, 'Reason:', event.reason);
      this.isConnected = false;
      this.terminal.writeln('\x1b[1;33m[Disconnected from terminal]\x1b[0m');
    };
  }

  private sendCommand(data: string) {
    console.log('[Terminal] ⬆️ Sending command:', JSON.stringify(data), 'char codes:', Array.from(data).map(c => c.charCodeAt(0)));

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      const payload = {
        type: 'input',
        data: data
      };
      console.log('[Terminal] ⬆️ WebSocket payload:', JSON.stringify(payload));
      this.ws.send(JSON.stringify(payload));
    } else if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
      // Buffer input while connecting
      console.log('[Terminal] ⏳ WebSocket connecting - Buffering input');
      this.inputBuffer.push(data);
    } else {
      console.error('[Terminal] ❌ Cannot send - WebSocket not open. State:', this.ws?.readyState);
    }
  }

  closeTerminal() {
    this.close.emit();
  }

  onBackdropClick() {
    // Close modal when clicking outside
    this.closeTerminal();
  }
}
