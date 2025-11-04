/**
 * Sendell VS Code Extension
 *
 * Entry point for the extension
 * Manages lifecycle, commands, and integration with Sendell Python server
 */

import * as vscode from 'vscode';
import { SendellWebSocketClient } from './websocket';
import { TerminalManager } from './terminal';
import { initLogger, logger } from './logger';
import { SendellConfig, ConnectionStatus } from './types';

let wsClient: SendellWebSocketClient | undefined;
let terminalManager: TerminalManager | undefined;
let statusBarItem: vscode.StatusBarItem | undefined;

/**
 * Extension activation
 * Called when extension is first activated
 */
export function activate(context: vscode.ExtensionContext) {
    console.log('Sendell extension is activating...');

    // Read configuration
    const config = getConfig();

    // Initialize logger
    initLogger(config.logLevel);
    logger.info('===================================');
    logger.info('Sendell Extension Activated');
    logger.info('===================================');
    logger.info(`Version: 0.3.0`);
    logger.info(`VS Code: ${vscode.version}`);
    logger.info(`Server URL: ${config.serverUrl}`);
    logger.info(`Auto-connect: ${config.autoConnect}`);

    // Create status bar item
    statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command = 'sendell.showStatus';
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Initialize WebSocket client
    wsClient = new SendellWebSocketClient(
        config.serverUrl,
        context,
        config.maxReconnectAttempts,
        config.reconnectInterval
    );

    // Update status bar on connection status change
    wsClient.onStatusChange((status: ConnectionStatus) => {
        updateStatusBar(status);
    });

    // Register message handlers
    registerMessageHandlers(wsClient);

    // Initialize Terminal Manager
    terminalManager = new TerminalManager(wsClient, context);
    terminalManager.initialize();
    logger.info('Terminal Manager ready');

    // Auto-connect if configured
    if (config.autoConnect) {
        logger.info('Auto-connecting to Sendell server...');
        wsClient.connect().catch((error) => {
            logger.error('Auto-connect failed', error);
        });
    } else {
        updateStatusBar('disconnected');
    }

    // Register commands
    registerCommands(context, wsClient);

    // Register configuration change listener
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration('sendell')) {
                handleConfigChange();
            }
        })
    );

    logger.info('Extension activation complete');
}

/**
 * Extension deactivation
 * Called when extension is deactivated
 */
export function deactivate() {
    logger.info('Deactivating Sendell extension...');

    if (terminalManager) {
        terminalManager.dispose();
        terminalManager = undefined;
    }

    if (wsClient) {
        wsClient.dispose();
        wsClient = undefined;
    }

    if (statusBarItem) {
        statusBarItem.dispose();
        statusBarItem = undefined;
    }

    logger.info('Extension deactivated');
}

/**
 * Register all commands
 */
function registerCommands(
    context: vscode.ExtensionContext,
    client: SendellWebSocketClient
): void {
    // Connect command
    context.subscriptions.push(
        vscode.commands.registerCommand('sendell.connect', async () => {
            logger.info('Manual connect triggered');
            try {
                await client.connect();
                vscode.window.showInformationMessage('Connecting to Sendell server...');
            } catch (error) {
                logger.error('Connect command failed', error as Error);
                vscode.window.showErrorMessage(`Failed to connect: ${error}`);
            }
        })
    );

    // Disconnect command
    context.subscriptions.push(
        vscode.commands.registerCommand('sendell.disconnect', () => {
            logger.info('Manual disconnect triggered');
            client.disconnect();
            vscode.window.showInformationMessage('Disconnected from Sendell server');
        })
    );

    // Show status command
    context.subscriptions.push(
        vscode.commands.registerCommand('sendell.showStatus', () => {
            const status = client.getStatus();
            const config = getConfig();

            const statusMessage = [
                `Connection Status: ${status}`,
                `Server URL: ${config.serverUrl}`,
                `Auto-connect: ${config.autoConnect}`,
                '',
                'Available commands:',
                '- Sendell: Connect to Server',
                '- Sendell: Disconnect from Server',
                '- Sendell: Show Logs',
            ].join('\n');

            vscode.window.showInformationMessage(statusMessage, 'Show Logs').then((choice) => {
                if (choice === 'Show Logs') {
                    logger.show();
                }
            });
        })
    );

    // Show logs command
    context.subscriptions.push(
        vscode.commands.registerCommand('sendell.showLogs', () => {
            logger.show();
        })
    );

    // Show terminal statistics command
    context.subscriptions.push(
        vscode.commands.registerCommand('sendell.showTerminalStats', () => {
            if (!terminalManager) {
                vscode.window.showWarningMessage('Terminal Manager not initialized');
                return;
            }

            const stats = terminalManager.getStatistics();
            const statsMessage = [
                `Terminal Statistics:`,
                `Total Terminals: ${stats.totalTerminals}`,
                `Monitored: ${stats.monitoredTerminals}`,
                '',
                'Terminals:',
                ...stats.terminals.map((t: any) =>
                    `  ${t.name}: ${t.linesInBuffer} lines, ${t.errorsDetected} errors`
                ),
            ].join('\n');

            vscode.window.showInformationMessage(statsMessage, 'Show Logs').then((choice) => {
                if (choice === 'Show Logs') {
                    logger.show();
                }
            });
        })
    );

    logger.info('Commands registered');
}

/**
 * Register WebSocket message handlers
 */
function registerMessageHandlers(client: SendellWebSocketClient): void {
    // System messages
    client.on('system', (message) => {
        logger.debug('System message received', message);
    });

    // Terminal messages
    client.on('terminal', (message) => {
        logger.debug('Terminal message received', message);
    });

    // File messages
    client.on('file', (message) => {
        logger.debug('File message received', message);
    });

    // Claude Code messages
    client.on('claude', (message) => {
        logger.debug('Claude message received', message);
    });

    logger.info('Message handlers registered');
}

/**
 * Update status bar item
 */
function updateStatusBar(status: ConnectionStatus): void {
    if (!statusBarItem) {
        return;
    }

    let icon: string;
    let tooltip: string;
    let backgroundColor: vscode.ThemeColor | undefined;

    switch (status) {
        case 'connected':
            icon = '$(plug)';
            tooltip = 'Sendell: Connected';
            backgroundColor = undefined;
            break;
        case 'connecting':
            icon = '$(sync~spin)';
            tooltip = 'Sendell: Connecting...';
            backgroundColor = undefined;
            break;
        case 'reconnecting':
            icon = '$(sync~spin)';
            tooltip = 'Sendell: Reconnecting...';
            backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
            break;
        case 'disconnected':
            icon = '$(debug-disconnect)';
            tooltip = 'Sendell: Disconnected (click to connect)';
            backgroundColor = undefined;
            break;
        case 'failed':
            icon = '$(error)';
            tooltip = 'Sendell: Connection failed';
            backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
            break;
    }

    statusBarItem.text = `${icon} Sendell`;
    statusBarItem.tooltip = tooltip;
    statusBarItem.backgroundColor = backgroundColor;

    logger.debug(`Status bar updated: ${status}`);
}

/**
 * Get current configuration
 */
function getConfig(): SendellConfig {
    const config = vscode.workspace.getConfiguration('sendell');

    return {
        serverUrl: config.get('serverUrl', 'ws://localhost:7000'),
        autoConnect: config.get('autoConnect', true),
        reconnectInterval: config.get('reconnectInterval', 5000),
        maxReconnectAttempts: config.get('maxReconnectAttempts', 10),
        logLevel: config.get('logLevel', 'info'),
    };
}

/**
 * Handle configuration changes
 */
function handleConfigChange(): void {
    const config = getConfig();

    logger.info('Configuration changed');
    logger.setLogLevel(config.logLevel);

    // Show warning that reconnection is needed
    vscode.window
        .showWarningMessage(
            'Sendell configuration changed. Reconnection required to apply changes.',
            'Reconnect Now',
            'Later'
        )
        .then((choice) => {
            if (choice === 'Reconnect Now' && wsClient) {
                wsClient.disconnect();
                setTimeout(() => {
                    wsClient!.connect();
                }, 1000);
            }
        });
}
