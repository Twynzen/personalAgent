import { Component, Input, OnInit, OnDestroy, ViewChild, ElementRef, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Terminal } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';

@Component({
  selector: 'app-terminal',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="terminal-container">
      <div class="terminal-header">
        <span class="terminal-title">{{ projectName }} - Terminal</span>
        <button class="terminal-close" (click)="closeTerminal()">&times;</button>
      </div>
      <div class="terminal-body" #terminalElement></div>
    </div>
  `,
  styles: [`
    .terminal-container {
      background: #0a0a0a;
      border: 2px solid #00ff00;
      box-shadow: 0 0 20px rgba(0, 255, 0, 0.3);
      margin-top: 1rem;
      border-radius: 4px;
      overflow: hidden;
    }

    .terminal-header {
      background: #1a1a1a;
      padding: 0.75rem 1rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      border-bottom: 1px solid #00ff00;
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
      height: 400px;
      padding: 0.5rem;
    }
  `]
})
export class TerminalComponent implements OnInit, OnDestroy {
  @Input() projectPid!: number;
  @Input() workspacePath!: string;
  @Input({ required: true }) projectName!: string;

  @ViewChild('terminalElement', { static: true }) terminalElement!: ElementRef;

  private terminal!: Terminal;
  private fitAddon!: FitAddon;
  private ws!: WebSocket;

  ngOnInit() {
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

    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);

    this.terminal.open(this.terminalElement.nativeElement);
    this.fitAddon.fit();

    // Handle user input
    this.terminal.onData((data) => {
      this.sendCommand(data);
    });

    // Welcome message
    this.terminal.writeln('\x1b[1;32m=== Sendell Embedded Terminal ===\x1b[0m');
    this.terminal.writeln(`\x1b[1;36mProject:\x1b[0m ${this.projectName}`);
    this.terminal.writeln(`\x1b[1;36mPath:\x1b[0m ${this.workspacePath}`);
    this.terminal.writeln('\x1b[1;32m=================================\x1b[0m');
    this.terminal.writeln('');

    // Resize on window resize
    window.addEventListener('resize', () => {
      this.fitAddon.fit();
    });
  }

  private connectWebSocket() {
    const wsUrl = `ws://localhost:8765/ws/terminal/${this.projectPid}`;
    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log(`Terminal WebSocket connected for project ${this.projectPid}`);
      this.terminal.writeln('\x1b[1;32m[Connected to terminal]\x1b[0m');
    };

    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.type === 'output') {
        // Write output to terminal
        this.terminal.write(message.data + '\r\n');
      } else if (message.type === 'error') {
        this.terminal.writeln(`\x1b[1;31m[Error: ${message.message}]\x1b[0m`);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.terminal.writeln('\x1b[1;31m[WebSocket error]\x1b[0m');
    };

    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.terminal.writeln('\x1b[1;33m[Disconnected from terminal]\x1b[0m');
    };
  }

  private sendCommand(data: string) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'input',
        data: data
      }));
    }
  }

  closeTerminal() {
    // Emit close event to parent
    this.ngOnDestroy();
  }
}
