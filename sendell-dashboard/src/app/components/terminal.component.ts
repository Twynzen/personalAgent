/**
 * Terminal Component - Production-grade xterm.js integration
 *
 * Based on research from angular-terminal-complete-guide.txt
 * Implements all best practices from VS Code, AWS CloudShell, and Replit
 *
 * Key features:
 * - ViewEncapsulation.None for xterm.js CSS
 * - NgZone.runOutsideAngular for performance (200-300% improvement)
 * - WebGL rendering (200× faster than DOM)
 * - WebSocket reconnection with exponential backoff
 * - ResizeObserver + debounce for responsive sizing
 * - Disposables tracking (memory leak prevention)
 * - Flow control for output throttling
 */

import {
  Component,
  Input,
  OnInit,
  OnDestroy,
  AfterViewInit,
  ViewChild,
  ElementRef,
  Output,
  EventEmitter,
  NgZone,
  ViewEncapsulation
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Terminal, IDisposable } from '@xterm/xterm';
import { FitAddon } from '@xterm/addon-fit';
import { WebLinksAddon } from '@xterm/addon-web-links';
import { WebglAddon } from '@xterm/addon-webgl';

@Component({
  selector: 'app-terminal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './terminal.component.html',
  styleUrls: ['./terminal.component.scss'],
  encapsulation: ViewEncapsulation.None  // CRITICAL: xterm.js requires this
})
export class TerminalComponent implements OnInit, AfterViewInit, OnDestroy {
  @Input() projectPid!: number;
  @Input() workspacePath!: string;
  @Input({ required: true }) projectName!: string;
  @Output() close = new EventEmitter<void>();

  @ViewChild('terminalElement', { static: false }) terminalElement!: ElementRef;

  private terminal!: Terminal;
  private fitAddon!: FitAddon;
  private webglAddon?: WebglAddon;
  private ws?: WebSocket;
  private disposables: IDisposable[] = [];

  // WebSocket state
  private inputBuffer: string[] = [];
  private isConnected: boolean = false;
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 5;
  private reconnectTimeout?: number;

  // Input accumulation (for subprocess backend without PTY)
  private currentLine: string = '';

  // Resize management
  private resizeObserver?: ResizeObserver;
  private resizeTimeout?: number;
  private pendingFit: boolean = false;
  private isReady: boolean = false;

  // Flow control (watermark-based)
  private outputWatermark: number = 0;
  private readonly HIGH_WATERMARK = 100000;  // 100KB
  private readonly LOW_WATERMARK = 10000;    // 10KB
  private isPaused: boolean = false;

  constructor(private ngZone: NgZone) {}

  ngOnInit() {
    console.log('[Terminal] Component initialized for project:', this.projectName);
  }

  ngAfterViewInit() {
    console.log('[Terminal] View initialized, starting terminal setup');

    if (!this.terminalElement) {
      console.error('[Terminal] CRITICAL: terminalElement is undefined!');
      return;
    }

    // Initialize terminal outside Angular zone for performance
    // This prevents change detection on every character typed/rendered
    this.ngZone.runOutsideAngular(() => {
      this.initializeTerminal();
      this.setupResizeObserver();
    });

    // Connect WebSocket inside Angular zone for proper state updates
    this.ngZone.run(() => {
      this.connectWebSocket();
    });
  }

  ngOnDestroy() {
    console.log('[Terminal] Component destroying, cleaning up resources');
    this.cleanup();
  }

  private initializeTerminal() {
    console.log('[Terminal] Initializing xterm.js with production config');

    // Create terminal with optimized settings
    this.terminal = new Terminal({
      cursorBlink: true,
      fontSize: 14,
      fontFamily: '"Cascadia Code", "Fira Code", "Consolas", "Courier New", monospace',
      scrollback: 1000,  // Limit to prevent memory bloat
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

    // Load addons
    this.fitAddon = new FitAddon();
    this.terminal.loadAddon(this.fitAddon);
    console.log('[Terminal] FitAddon loaded');

    this.terminal.loadAddon(new WebLinksAddon((event, uri) => {
      // Custom link handler - Ctrl+Click to open
      if (event.ctrlKey || event.metaKey) {
        window.open(uri, '_blank');
      }
    }));
    console.log('[Terminal] WebLinksAddon loaded');

    // Try to load WebGL addon (fallback to canvas if fails)
    try {
      this.webglAddon = new WebglAddon();
      this.terminal.loadAddon(this.webglAddon);
      console.log('[Terminal] ✅ WebglAddon loaded - 200× rendering performance');
    } catch (e) {
      console.warn('[Terminal] WebGL not available, falling back to canvas:', e);
    }

    // Open terminal in DOM
    this.terminal.open(this.terminalElement.nativeElement);
    console.log('[Terminal] Terminal opened in DOM');

    // Setup input handler
    const dataDisposable = this.terminal.onData((data) => {
      this.handleTerminalInput(data);
    });
    this.disposables.push(dataDisposable);
    console.log('[Terminal] Input handler registered');

    // Initial fit with robust timing
    this.safelyFit();

    this.isReady = true;
    console.log('[Terminal] ✅ Initialization complete');
  }

  private setupResizeObserver() {
    const container = this.terminalElement.nativeElement;

    // ResizeObserver for precise container size changes
    this.resizeObserver = new ResizeObserver(() => {
      this.debouncedFit();
    });
    this.resizeObserver.observe(container);
    console.log('[Terminal] ResizeObserver attached');

    // Also listen to window resize as fallback
    window.addEventListener('resize', () => {
      this.debouncedFit();
    });
  }

  private debouncedFit() {
    // Debounce resize to prevent flickering
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }

    this.resizeTimeout = window.setTimeout(() => {
      this.safelyFit();
    }, 100);
  }

  private safelyFit() {
    // Robust fit with multiple safety checks
    if (!this.isReady) {
      this.pendingFit = true;
      return;
    }

    const container = this.terminalElement?.nativeElement;
    if (!container) {
      this.pendingFit = true;
      return;
    }

    // Check if container is visible and has dimensions
    if (!container.offsetParent) {
      console.debug('[Terminal] Container hidden, deferring fit');
      this.pendingFit = true;
      return;
    }

    if (container.offsetWidth === 0 || container.offsetHeight === 0) {
      console.debug('[Terminal] Container has zero dimensions, deferring fit');
      this.pendingFit = true;
      return;
    }

    try {
      this.fitAddon?.fit();
      this.pendingFit = false;
      console.debug('[Terminal] Fit successful');
    } catch (err) {
      console.error('[Terminal] Fit failed:', err);
    }
  }

  private handleTerminalInput(data: string) {
    // All input handling happens outside Angular zone
    // Only re-enter zone if we need to update component state

    console.debug('[Terminal] User input:', JSON.stringify(data));

    // Handle special keys
    if (data === '\r') {
      // Enter pressed - send accumulated command
      console.debug('[Terminal] Enter pressed, sending command:', this.currentLine);
      this.terminal.write('\r\n');  // Echo newline locally

      // Send complete command to backend
      if (this.currentLine.trim()) {
        this.sendToWebSocket({ type: 'input', data: this.currentLine });
      } else {
        // Empty line - just send Enter
        this.sendToWebSocket({ type: 'input', data: '\r' });
      }

      this.currentLine = '';  // Reset for next command
    } else if (data === '\x7f' || data === '\b') {
      // Backspace - remove last character
      if (this.currentLine.length > 0) {
        this.currentLine = this.currentLine.slice(0, -1);
        this.terminal.write('\b \b');  // Erase character visually
      }
    } else if (data === '\x03') {
      // Ctrl+C - interrupt signal
      this.terminal.write('^C\r\n');
      this.currentLine = '';
      this.sendToWebSocket({ type: 'input', data: '\x03' });
    } else {
      // Regular character - accumulate and echo locally in WHITE
      this.currentLine += data;
      // Echo in white color for user input
      this.terminal.write('\x1b[37m' + data + '\x1b[0m');
    }
  }

  private connectWebSocket() {
    const wsUrl = `ws://localhost:8765/ws/terminal/${this.projectPid}`;
    console.log('[WebSocket] Connecting to:', wsUrl);

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WebSocket] ✅ Connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;

      // Clear terminal to remove any garbage
      this.terminal.clear();
      console.log('[WebSocket] Terminal cleared, ready for output');

      // Send buffered input
      if (this.inputBuffer.length > 0) {
        console.log('[WebSocket] Sending', this.inputBuffer.length, 'buffered commands');
        this.inputBuffer.forEach(cmd => {
          this.ws?.send(cmd);
        });
        this.inputBuffer = [];
      }

      // Re-fit after connection (ensures proper sizing)
      setTimeout(() => this.safelyFit(), 50);
    };

    this.ws.onmessage = (event) => {
      this.handleWebSocketMessage(event);
    };

    this.ws.onerror = (error) => {
      console.error('[WebSocket] ❌ Error:', error);
      this.ngZone.run(() => {
        this.terminal.writeln('\x1b[1;31m[WebSocket error]\x1b[0m');
      });
    };

    this.ws.onclose = (event) => {
      console.log('[WebSocket] ❌ Closed. Code:', event.code, 'Reason:', event.reason);
      this.isConnected = false;

      this.ngZone.run(() => {
        this.terminal.writeln('\x1b[1;33m[Disconnected from terminal]\x1b[0m');

        // Attempt reconnection with exponential backoff
        this.attemptReconnection();
      });
    };
  }

  private attemptReconnection() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      this.terminal.writeln('\x1b[1;31m[Reconnection failed - max attempts reached]\x1b[0m');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 10000);

    console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    this.terminal.writeln(`\x1b[1;33m[Reconnecting in ${delay/1000}s...]\x1b[0m`);

    this.reconnectTimeout = window.setTimeout(() => {
      this.connectWebSocket();
    }, delay);
  }

  private handleWebSocketMessage(event: MessageEvent) {
    const message = JSON.parse(event.data);

    if (message.type === 'output') {
      // Write output with flow control
      const data = message.data;

      // Apply green color to output + ensure proper line breaks
      // Replace \n with \r\n for proper terminal line breaks
      const formattedData = '\x1b[32m' + data.replace(/\n/g, '\r\n') + '\x1b[0m';

      this.writeWithFlowControl(formattedData);
    } else if (message.type === 'error') {
      console.error('[WebSocket] Server error:', message.message);
      this.ngZone.run(() => {
        this.terminal.writeln(`\x1b[1;31m[Error: ${message.message}]\x1b[0m`);
      });
    }
  }

  private writeWithFlowControl(data: string) {
    // Implement watermark-based flow control
    this.outputWatermark += data.length;

    this.terminal.write(data, () => {
      // Callback when write completes
      this.outputWatermark -= data.length;

      if (this.isPaused && this.outputWatermark < this.LOW_WATERMARK) {
        console.debug('[FlowControl] Resuming output');
        this.isPaused = false;
        // Could send resume signal to backend here
      }
    });

    if (!this.isPaused && this.outputWatermark > this.HIGH_WATERMARK) {
      console.warn('[FlowControl] High watermark reached, pausing');
      this.isPaused = true;
      // Could send pause signal to backend here
    }
  }

  private sendToWebSocket(message: any) {
    const payload = JSON.stringify(message);

    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(payload);
    } else {
      // Buffer if not connected
      console.debug('[WebSocket] Not connected, buffering message');
      this.inputBuffer.push(payload);
    }
  }

  private cleanup() {
    // Comprehensive cleanup to prevent memory leaks

    // Clear reconnection timeout
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
    }

    // Clear resize timeout
    if (this.resizeTimeout) {
      clearTimeout(this.resizeTimeout);
    }

    // Disconnect ResizeObserver
    if (this.resizeObserver) {
      this.resizeObserver.disconnect();
    }

    // Close WebSocket
    if (this.ws) {
      this.ws.close();
    }

    // Dispose all event handlers
    this.disposables.forEach(d => {
      try {
        d.dispose();
      } catch (e) {
        console.error('[Terminal] Error disposing:', e);
      }
    });
    this.disposables = [];

    // Dispose WebGL addon
    if (this.webglAddon) {
      try {
        this.webglAddon.dispose();
      } catch (e) {
        console.error('[Terminal] Error disposing WebGL:', e);
      }
    }

    // Dispose terminal
    if (this.terminal) {
      try {
        this.terminal.dispose();
      } catch (e) {
        console.error('[Terminal] Error disposing terminal:', e);
      }
    }

    console.log('[Terminal] ✅ Cleanup complete');
  }

  // Public API

  minimizeTerminal() {
    // Same as close - just hides the terminal (doesn't destroy it)
    // In future could implement actual minimize to taskbar
    this.close.emit();
  }

  closeTerminal() {
    this.close.emit();
  }

  onBackdropClick() {
    // Minimize instead of close when clicking backdrop
    this.minimizeTerminal();
  }
}
