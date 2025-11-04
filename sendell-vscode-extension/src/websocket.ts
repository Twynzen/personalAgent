/**
 * WebSocket Client for Sendell VS Code Extension
 *
 * Manages bidirectional communication with Sendell Python server
 * Handles connection lifecycle, reconnection, and message routing
 */

import * as vscode from 'vscode';
import WebSocket from 'ws';
import {
    SendellMessage,
    MessageType,
    MessageCategory,
    ConnectionStatus,
    HandshakePayload,
    WorkspaceInfo,
} from './types';
import { logger } from './logger';

export class SendellWebSocketClient {
    private ws?: WebSocket;
    private serverUrl: string;
    private reconnectTimeout?: NodeJS.Timeout;
    private reconnectAttempts: number = 0;
    private maxReconnectAttempts: number;
    private reconnectInterval: number;
    private status: ConnectionStatus = 'disconnected';

    // Event handlers
    private messageHandlers: Map<MessageCategory, (message: SendellMessage) => void> = new Map();
    private statusChangeCallbacks: ((status: ConnectionStatus) => void)[] = [];

    constructor(
        serverUrl: string,
        private context: vscode.ExtensionContext,
        maxReconnectAttempts: number = 10,
        reconnectInterval: number = 5000
    ) {
        this.serverUrl = serverUrl;
        this.maxReconnectAttempts = maxReconnectAttempts;
        this.reconnectInterval = reconnectInterval;
    }

    /**
     * Connect to Sendell Python server
     */
    async connect(): Promise<void> {
        if (this.status === 'connecting' || this.status === 'connected') {
            logger.warn('Already connected or connecting');
            return;
        }

        this.setStatus('connecting');
        logger.info(`Connecting to Sendell server: ${this.serverUrl}`);

        try {
            this.ws = new WebSocket(this.serverUrl);

            this.ws.on('open', () => {
                logger.info('Connected to Sendell server');
                this.reconnectAttempts = 0;
                this.setStatus('connected');
                this.sendHandshake();
            });

            this.ws.on('message', (data: Buffer) => {
                try {
                    const message: SendellMessage = JSON.parse(data.toString());
                    logger.debug('Received message', message);
                    this.handleMessage(message);
                } catch (error) {
                    logger.error('Failed to parse message', error as Error);
                }
            });

            this.ws.on('close', (code: number, reason: Buffer) => {
                const reasonStr = reason.toString() || 'Unknown reason';
                logger.warn(`Disconnected from Sendell server: ${code} - ${reasonStr}`);
                this.setStatus('disconnected');
                this.scheduleReconnect();
            });

            this.ws.on('error', (error: Error) => {
                logger.error('WebSocket error', error);
                this.setStatus('failed');
            });

        } catch (error) {
            logger.error('Failed to connect', error as Error);
            this.setStatus('failed');
            this.scheduleReconnect();
        }
    }

    /**
     * Disconnect from server
     */
    disconnect(): void {
        logger.info('Disconnecting from Sendell server');

        if (this.reconnectTimeout) {
            clearTimeout(this.reconnectTimeout);
            this.reconnectTimeout = undefined;
        }

        if (this.ws) {
            this.ws.close();
            this.ws = undefined;
        }

        this.setStatus('disconnected');
    }

    /**
     * Send message to server
     */
    send(message: Omit<SendellMessage, 'id' | 'timestamp'>): void {
        if (!this.isConnected()) {
            logger.warn('Cannot send message: not connected');
            return;
        }

        const fullMessage: SendellMessage = {
            ...message,
            id: this.generateId(),
            timestamp: Date.now(),
        };

        logger.debug('Sending message', fullMessage);

        try {
            this.ws!.send(JSON.stringify(fullMessage));
        } catch (error) {
            logger.error('Failed to send message', error as Error);
        }
    }

    /**
     * Register message handler for a category
     */
    on(category: MessageCategory, handler: (message: SendellMessage) => void): void {
        this.messageHandlers.set(category, handler);
        logger.debug(`Registered handler for category: ${category}`);
    }

    /**
     * Register status change callback
     */
    onStatusChange(callback: (status: ConnectionStatus) => void): void {
        this.statusChangeCallbacks.push(callback);
    }

    /**
     * Get current connection status
     */
    getStatus(): ConnectionStatus {
        return this.status;
    }

    /**
     * Check if connected
     */
    isConnected(): boolean {
        return this.status === 'connected' && this.ws?.readyState === WebSocket.OPEN;
    }

    /**
     * Dispose client (cleanup)
     */
    dispose(): void {
        this.disconnect();
        this.messageHandlers.clear();
        this.statusChangeCallbacks = [];
    }

    /**
     * Send handshake message on connection
     */
    private sendHandshake(): void {
        const workspaces: WorkspaceInfo[] = (vscode.workspace.workspaceFolders || []).map(folder => ({
            name: folder.name,
            path: folder.uri.fsPath,
            type: 'folder' as const,
        }));

        const payload: HandshakePayload = {
            extensionVersion: '0.3.0',
            vscodeVersion: vscode.version,
            workspaces,
            platform: process.platform,
        };

        this.send({
            type: 'event',
            category: 'system',
            payload,
        });

        logger.info(`Handshake sent: ${workspaces.length} workspace(s)`);
    }

    /**
     * Handle incoming message
     */
    private handleMessage(message: SendellMessage): void {
        const handler = this.messageHandlers.get(message.category);

        if (handler) {
            try {
                handler(message);
            } catch (error) {
                logger.error(`Error handling ${message.category} message`, error as Error);
            }
        } else {
            logger.debug(`No handler for category: ${message.category}`);
        }
    }

    /**
     * Schedule reconnection attempt
     */
    private scheduleReconnect(): void {
        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            logger.error(
                `Max reconnection attempts (${this.maxReconnectAttempts}) reached. Giving up.`
            );
            vscode.window.showErrorMessage(
                `Failed to connect to Sendell after ${this.maxReconnectAttempts} attempts. ` +
                `Please check if Sendell Python server is running on ${this.serverUrl}`
            );
            return;
        }

        this.reconnectAttempts++;
        const delay = Math.min(
            this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1),
            30000 // Max 30 seconds
        );

        logger.info(
            `Scheduling reconnect attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts} in ${delay}ms`
        );

        this.setStatus('reconnecting');

        this.reconnectTimeout = setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Set connection status and notify listeners
     */
    private setStatus(status: ConnectionStatus): void {
        if (this.status !== status) {
            this.status = status;
            logger.debug(`Status changed: ${status}`);

            // Notify all callbacks
            for (const callback of this.statusChangeCallbacks) {
                try {
                    callback(status);
                } catch (error) {
                    logger.error('Error in status change callback', error as Error);
                }
            }
        }
    }

    /**
     * Generate unique message ID
     */
    private generateId(): string {
        return `${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
