/**
 * Type definitions for Sendell VS Code Extension
 *
 * Defines the message protocol for communication between
 * VS Code Extension (TypeScript) and Sendell Python server.
 */

/**
 * Message types for bidirectional communication
 */
export type MessageType = 'event' | 'request' | 'response';

/**
 * Message categories for routing
 */
export type MessageCategory =
    | 'system'      // System-level events (handshake, ping, pong)
    | 'terminal'    // Terminal-related events
    | 'file'        // File system events
    | 'git'         // Git-related events
    | 'diagnostic'  // LSP diagnostics
    | 'claude'      // Claude Code integration
    | 'project';    // Project context

/**
 * Base message structure
 */
export interface SendellMessage {
    id: string;
    type: MessageType;
    category: MessageCategory;
    payload: any;
    timestamp: number;
}

/**
 * Handshake payload sent on initial connection
 */
export interface HandshakePayload {
    extensionVersion: string;
    vscodeVersion: string;
    workspaces: WorkspaceInfo[];
    platform: string;
}

/**
 * Workspace information
 */
export interface WorkspaceInfo {
    name: string;
    path: string;
    type: 'folder' | 'workspace';
}

/**
 * Terminal event types
 */
export type TerminalEventType =
    | 'command_start'    // Command execution started
    | 'command_end'      // Command execution ended
    | 'output';          // Terminal output chunk

/**
 * Terminal event payload
 */
export interface TerminalEvent {
    type: TerminalEventType;
    terminal: string;        // Terminal name
    command?: string;        // Command being executed
    output?: string;         // Terminal output
    exitCode?: number;       // Exit code (only for command_end)
}

/**
 * File event types
 */
export type FileEventType = 'created' | 'modified' | 'deleted';

/**
 * File event payload
 */
export interface FileEvent {
    type: FileEventType;
    path: string;
    content?: string;   // Only for created/modified
}

/**
 * Diagnostic event payload
 */
export interface DiagnosticEvent {
    type: 'error' | 'warning';
    file: string;
    line: number;
    column: number;
    message: string;
    severity: number;
}

/**
 * Git event payload
 */
export interface GitEvent {
    branch: string;
    hasChanges: boolean;
    changedFiles?: string[];
}

/**
 * Claude Code event types
 */
export type ClaudeEventType = 'detected' | 'state_change' | 'output';

/**
 * Claude Code event payload
 */
export interface ClaudeEvent {
    type: ClaudeEventType;
    terminal: string;
    state?: 'ready' | 'thinking' | 'executing' | 'waiting_permission';
    output?: string;
}

/**
 * Project context payload
 */
export interface ProjectContext {
    name: string;
    type: 'nodejs' | 'python' | 'rust' | 'go' | 'unknown';
    summary: string;
    keyFiles: string[];
    recentChanges: string[];
    errors: string[];
    tokenCount: number;
}

/**
 * Connection status
 */
export type ConnectionStatus =
    | 'disconnected'
    | 'connecting'
    | 'connected'
    | 'reconnecting'
    | 'failed';

/**
 * Logger levels
 */
export type LogLevel = 'debug' | 'info' | 'warn' | 'error';

/**
 * Configuration interface
 */
export interface SendellConfig {
    serverUrl: string;
    autoConnect: boolean;
    reconnectInterval: number;
    maxReconnectAttempts: number;
    logLevel: LogLevel;
}
