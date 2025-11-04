/**
 * Logging utility for Sendell VS Code Extension
 *
 * Provides structured logging to VS Code Output Channel
 * with configurable log levels.
 */

import * as vscode from 'vscode';
import { LogLevel } from './types';

export class Logger {
    private outputChannel: vscode.OutputChannel;
    private logLevel: LogLevel;

    // Log level hierarchy (higher = more severe)
    private static readonly LOG_LEVELS: Record<LogLevel, number> = {
        debug: 0,
        info: 1,
        warn: 2,
        error: 3,
    };

    constructor(channelName: string = 'Sendell', logLevel: LogLevel = 'info') {
        this.outputChannel = vscode.window.createOutputChannel(channelName);
        this.logLevel = logLevel;
    }

    /**
     * Set logging level
     */
    setLogLevel(level: LogLevel): void {
        this.logLevel = level;
        this.info(`Log level set to: ${level}`);
    }

    /**
     * Log debug message
     */
    debug(message: string, ...args: any[]): void {
        this.log('debug', message, args);
    }

    /**
     * Log info message
     */
    info(message: string, ...args: any[]): void {
        this.log('info', message, args);
    }

    /**
     * Log warning message
     */
    warn(message: string, ...args: any[]): void {
        this.log('warn', message, args);
    }

    /**
     * Log error message
     */
    error(message: string, error?: Error, ...args: any[]): void {
        this.log('error', message, args);
        if (error) {
            this.log('error', `Stack: ${error.stack || error.message}`, []);
        }
    }

    /**
     * Show output channel
     */
    show(): void {
        this.outputChannel.show();
    }

    /**
     * Clear output channel
     */
    clear(): void {
        this.outputChannel.clear();
    }

    /**
     * Dispose output channel
     */
    dispose(): void {
        this.outputChannel.dispose();
    }

    /**
     * Internal logging method
     */
    private log(level: LogLevel, message: string, args: any[]): void {
        // Check if this log level should be shown
        if (Logger.LOG_LEVELS[level] < Logger.LOG_LEVELS[this.logLevel]) {
            return;
        }

        const timestamp = new Date().toISOString();
        const levelStr = level.toUpperCase().padEnd(5);
        const argsStr = args.length > 0 ? ` ${JSON.stringify(args)}` : '';

        const logLine = `[${timestamp}] ${levelStr}: ${message}${argsStr}`;

        this.outputChannel.appendLine(logLine);

        // Also show errors as VS Code notifications
        if (level === 'error') {
            vscode.window.showErrorMessage(`Sendell: ${message}`);
        }
    }
}

/**
 * Global logger instance
 * Will be initialized in extension.ts
 */
export let logger: Logger;

/**
 * Initialize global logger
 */
export function initLogger(logLevel: LogLevel = 'info'): Logger {
    logger = new Logger('Sendell', logLevel);
    return logger;
}
