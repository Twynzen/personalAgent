/**
 * Terminal Manager for Sendell VS Code Extension
 *
 * Monitors terminal activity using Shell Integration API (v1.93+)
 * Captures command execution, output, and exit codes
 * Optimizes memory usage with tail buffering
 */

import * as vscode from 'vscode';
import { SendellWebSocketClient } from './websocket';
import { TerminalEvent, TerminalEventType } from './types';
import { logger } from './logger';

/**
 * Tail buffer for efficient terminal output storage
 * Keeps only last N lines to prevent memory bloat
 */
export class TailBuffer {
    private lines: string[] = [];
    private readonly maxLines: number;
    private totalLinesReceived: number = 0;

    constructor(maxLines: number = 100) {
        this.maxLines = maxLines;
    }

    /**
     * Append chunk of text (may contain multiple lines)
     */
    append(chunk: string): void {
        if (!chunk) return;

        const newLines = chunk.split('\n');
        this.totalLinesReceived += newLines.length;

        this.lines.push(...newLines);

        // Trim to max size (keep most recent)
        if (this.lines.length > this.maxLines) {
            const excess = this.lines.length - this.maxLines;
            this.lines.splice(0, excess);
        }
    }

    /**
     * Get current buffer content
     */
    getContent(): string {
        return this.lines.join('\n');
    }

    /**
     * Get last N lines
     */
    getLastLines(count: number): string {
        const startIndex = Math.max(0, this.lines.length - count);
        return this.lines.slice(startIndex).join('\n');
    }

    /**
     * Clear buffer
     */
    clear(): void {
        this.lines = [];
        this.totalLinesReceived = 0;
    }

    /**
     * Get statistics
     */
    getStats(): { linesInBuffer: number; totalLinesReceived: number } {
        return {
            linesInBuffer: this.lines.length,
            totalLinesReceived: this.totalLinesReceived,
        };
    }

    /**
     * Filter buffer for error lines only
     */
    getErrors(): string[] {
        const errorPattern = /error|exception|fail|fatal|critical/i;
        return this.lines.filter(line => errorPattern.test(line));
    }
}

/**
 * Terminal information tracking
 */
interface TerminalInfo {
    terminal: vscode.Terminal;
    buffer: TailBuffer;
    lastCommand?: string;
    isMonitored: boolean;
    createdAt: number;
}

/**
 * Terminal Manager
 * Monitors all terminal activity in VS Code
 */
export class TerminalManager {
    private terminals: Map<string, TerminalInfo> = new Map();
    private disposables: vscode.Disposable[] = [];

    constructor(
        private wsClient: SendellWebSocketClient,
        private context: vscode.ExtensionContext
    ) {}

    /**
     * Initialize terminal monitoring
     */
    initialize(): void {
        logger.info('Initializing Terminal Manager...');

        // Monitor existing terminals
        for (const terminal of vscode.window.terminals) {
            this.registerTerminal(terminal);
        }

        // Monitor new terminals
        this.disposables.push(
            vscode.window.onDidOpenTerminal((terminal) => {
                logger.info(`New terminal opened: ${terminal.name}`);
                this.registerTerminal(terminal);
            })
        );

        // Monitor terminal closures
        this.disposables.push(
            vscode.window.onDidCloseTerminal((terminal) => {
                logger.info(`Terminal closed: ${terminal.name}`);
                this.unregisterTerminal(terminal);
            })
        );

        // Shell Integration: Command execution started
        this.disposables.push(
            vscode.window.onDidStartTerminalShellExecution(async (event) => {
                await this.handleCommandStart(event);
            })
        );

        // Shell Integration: Command execution ended
        this.disposables.push(
            vscode.window.onDidEndTerminalShellExecution(async (event) => {
                await this.handleCommandEnd(event);
            })
        );

        logger.info(
            `Terminal Manager initialized. Monitoring ${this.terminals.size} terminal(s)`
        );
    }

    /**
     * Register a terminal for monitoring
     */
    private registerTerminal(terminal: vscode.Terminal): void {
        const terminalId = this.getTerminalId(terminal);

        if (this.terminals.has(terminalId)) {
            logger.debug(`Terminal already registered: ${terminal.name}`);
            return;
        }

        const info: TerminalInfo = {
            terminal,
            buffer: new TailBuffer(100), // Keep last 100 lines
            isMonitored: true,
            createdAt: Date.now(),
        };

        this.terminals.set(terminalId, info);
        logger.debug(`Registered terminal: ${terminal.name} (ID: ${terminalId})`);

        // Send terminal creation event
        this.sendTerminalEvent({
            type: 'output',
            terminal: terminal.name,
            output: `[Terminal created: ${terminal.name}]`,
        });
    }

    /**
     * Unregister a terminal
     */
    private unregisterTerminal(terminal: vscode.Terminal): void {
        const terminalId = this.getTerminalId(terminal);
        const info = this.terminals.get(terminalId);

        if (info) {
            // Send final stats before removal
            const stats = info.buffer.getStats();
            logger.debug(
                `Terminal ${terminal.name} stats: ${stats.linesInBuffer} lines in buffer, ` +
                `${stats.totalLinesReceived} total lines received`
            );

            this.terminals.delete(terminalId);
        }
    }

    /**
     * Handle command execution start
     */
    private async handleCommandStart(
        event: vscode.TerminalShellExecutionStartEvent
    ): Promise<void> {
        const terminal = event.terminal;
        const command = event.execution.commandLine.value;
        const terminalId = this.getTerminalId(terminal);

        logger.debug(`Command started in ${terminal.name}: ${command}`);

        // Update terminal info
        const info = this.terminals.get(terminalId);
        if (info) {
            info.lastCommand = command;
        }

        // Send command start event
        this.sendTerminalEvent({
            type: 'command_start',
            terminal: terminal.name,
            command,
        });

        // Start reading output stream
        this.readOutputStream(event.execution, terminal);
    }

    /**
     * Handle command execution end
     */
    private async handleCommandEnd(
        event: vscode.TerminalShellExecutionEndEvent
    ): Promise<void> {
        const terminal = event.terminal;
        const exitCode = event.exitCode;
        const terminalId = this.getTerminalId(terminal);

        logger.debug(`Command ended in ${terminal.name}: exit code ${exitCode}`);

        const info = this.terminals.get(terminalId);
        const command = info?.lastCommand || 'unknown';

        // Send command end event
        this.sendTerminalEvent({
            type: 'command_end',
            terminal: terminal.name,
            command,
            exitCode,
        });

        // If command failed, send error summary
        if (exitCode !== undefined && exitCode !== 0 && info) {
            const errors = info.buffer.getErrors();
            if (errors.length > 0) {
                logger.warn(`Command failed in ${terminal.name} with ${errors.length} error(s)`);

                this.sendTerminalEvent({
                    type: 'output',
                    terminal: terminal.name,
                    output: `[ERRORS DETECTED]\n${errors.join('\n')}`,
                });
            }
        }
    }

    /**
     * Read output stream from command execution
     */
    private async readOutputStream(
        execution: vscode.TerminalShellExecution,
        terminal: vscode.Terminal
    ): Promise<void> {
        const terminalId = this.getTerminalId(terminal);
        const info = this.terminals.get(terminalId);

        if (!info) {
            logger.warn(`Terminal not found: ${terminal.name}`);
            return;
        }

        try {
            // Read output chunks as they arrive
            const stream = execution.read();

            for await (const chunk of stream) {
                // Store in buffer
                info.buffer.append(chunk);

                // Send to Sendell (throttled - only last 20 lines to save bandwidth)
                const recentOutput = info.buffer.getLastLines(20);

                this.sendTerminalEvent({
                    type: 'output',
                    terminal: terminal.name,
                    command: info.lastCommand,
                    output: recentOutput,
                });

                logger.debug(
                    `Output chunk received from ${terminal.name}: ${chunk.length} chars`
                );
            }
        } catch (error) {
            logger.error(`Error reading terminal output for ${terminal.name}`, error as Error);
        }
    }

    /**
     * Send terminal event to Sendell server
     */
    private sendTerminalEvent(event: TerminalEvent): void {
        if (!this.wsClient.isConnected()) {
            logger.debug('Skipping terminal event: not connected to Sendell');
            return;
        }

        this.wsClient.send({
            type: 'event',
            category: 'terminal',
            payload: event,
        });
    }

    /**
     * Get unique terminal identifier
     */
    private getTerminalId(terminal: vscode.Terminal): string {
        // Use processId if available (more stable)
        // Otherwise fall back to name + creation time
        return terminal.processId?.toString() || `${terminal.name}_${Date.now()}`;
    }

    /**
     * Get terminal by name
     */
    getTerminalByName(name: string): vscode.Terminal | undefined {
        for (const info of this.terminals.values()) {
            if (info.terminal.name === name) {
                return info.terminal;
            }
        }
        return undefined;
    }

    /**
     * Get buffer content for a terminal
     */
    getTerminalBuffer(terminalName: string): string | undefined {
        for (const info of this.terminals.values()) {
            if (info.terminal.name === terminalName) {
                return info.buffer.getContent();
            }
        }
        return undefined;
    }

    /**
     * Get all monitored terminals
     */
    getMonitoredTerminals(): string[] {
        return Array.from(this.terminals.values())
            .filter(info => info.isMonitored)
            .map(info => info.terminal.name);
    }

    /**
     * Get statistics for all terminals
     */
    getStatistics(): any {
        const stats: any[] = [];

        for (const [id, info] of this.terminals.entries()) {
            const bufferStats = info.buffer.getStats();
            stats.push({
                name: info.terminal.name,
                id,
                lastCommand: info.lastCommand || 'none',
                linesInBuffer: bufferStats.linesInBuffer,
                totalLinesReceived: bufferStats.totalLinesReceived,
                errorsDetected: info.buffer.getErrors().length,
                createdAt: new Date(info.createdAt).toISOString(),
            });
        }

        return {
            totalTerminals: this.terminals.size,
            monitoredTerminals: this.getMonitoredTerminals().length,
            terminals: stats,
        };
    }

    /**
     * Dispose manager (cleanup)
     */
    dispose(): void {
        logger.info('Disposing Terminal Manager...');

        for (const disposable of this.disposables) {
            disposable.dispose();
        }

        this.disposables = [];
        this.terminals.clear();

        logger.info('Terminal Manager disposed');
    }
}
