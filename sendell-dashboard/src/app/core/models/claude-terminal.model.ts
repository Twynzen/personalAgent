/**
 * Claude Terminal Models
 * Based on backend API from src/sendell/terminal_control/
 */

export interface ClaudeTerminal {
  pid: number;
  ppid: number;
  name: string;
  cmdline: string;
  cwd: string;
  cpu_percent: number;
  memory_mb: number;
  is_active: boolean;
  status: 'running' | 'idle';
}

export interface ClaudeSession {
  project: string;
  session_id: string;
  state: 'idle' | 'generating' | 'executing_tool' | 'processing_request' | 'error' | 'inactive' | 'unknown';
  last_event_type: string;
  timestamp: string;
  seconds_since_last_event?: number;
  event_count: number;
  token_usage?: {
    input: number;
    output: number;
    total: number;
  };
  file?: string;
  last_modified?: string;
  stop_reason?: string;
  model?: string;
  user_prompt?: string;
  error_message?: string;
  tool?: string;
  tool_params?: any;
}

export interface ClaudeTerminalsResponse {
  terminals: ClaudeTerminal[];
  count: number;
  timestamp: string;
}

export interface ClaudeSessionsResponse {
  sessions: ClaudeSession[];
  count: number;
  timestamp: string;
}

export interface CommandExecuteRequest {
  command: string;
  cwd?: string;
  timeout?: number;
}

export interface CommandExecuteResponse {
  success: boolean;
  stdout?: string;
  stderr?: string;
  returncode?: number;
  error?: string;
}

export interface TerminalOutputResponse {
  pid: number;
  lines: string[];
  count: number;
  is_running: boolean;
}
