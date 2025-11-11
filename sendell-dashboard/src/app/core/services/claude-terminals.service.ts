import { Injectable, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, interval, switchMap, tap, catchError, of } from 'rxjs';
import {
  ClaudeTerminal,
  ClaudeSession,
  ClaudeTerminalsResponse,
  ClaudeSessionsResponse,
  CommandExecuteRequest,
  CommandExecuteResponse,
  TerminalOutputResponse
} from '../models/claude-terminal.model';

@Injectable({ providedIn: 'root' })
export class ClaudeTerminalsService {
  private http = inject(HttpClient);
  private baseUrl = '/api/claude';

  // Signals for reactive state
  terminals = signal<ClaudeTerminal[]>([]);
  sessions = signal<ClaudeSession[]>([]);
  isLoading = signal<boolean>(false);
  error = signal<string | null>(null);
  lastUpdate = signal<string | null>(null);

  // Auto-refresh interval (30 seconds)
  private autoRefreshInterval = 30000;

  /**
   * Get list of Claude Code terminals
   * Detection takes ~16-20 seconds, so we show loading state
   */
  getTerminals(): Observable<ClaudeTerminalsResponse> {
    this.isLoading.set(true);
    this.error.set(null);

    return this.http.get<ClaudeTerminalsResponse>(`${this.baseUrl}/terminals`).pipe(
      tap(response => {
        this.terminals.set(response.terminals);
        this.lastUpdate.set(response.timestamp);
        this.isLoading.set(false);
      }),
      catchError(err => {
        this.error.set(`Error loading terminals: ${err.message}`);
        this.isLoading.set(false);
        return of({ terminals: [], count: 0, timestamp: new Date().toISOString() });
      })
    );
  }

  /**
   * Get active Claude Code sessions with state info
   */
  getSessions(): Observable<ClaudeSessionsResponse> {
    return this.http.get<ClaudeSessionsResponse>(`${this.baseUrl}/sessions`).pipe(
      tap(response => {
        this.sessions.set(response.sessions);
      }),
      catchError(err => {
        this.error.set(`Error loading sessions: ${err.message}`);
        return of({ sessions: [], count: 0, timestamp: new Date().toISOString() });
      })
    );
  }

  /**
   * Execute a command in a specific directory
   */
  executeCommand(request: CommandExecuteRequest): Observable<CommandExecuteResponse> {
    return this.http.post<CommandExecuteResponse>(`${this.baseUrl}/execute`, request);
  }

  /**
   * Get recent output from a specific Claude Code terminal
   */
  getTerminalOutput(pid: number, lines: number = 50): Observable<TerminalOutputResponse> {
    return this.http.get<TerminalOutputResponse>(`${this.baseUrl}/output/${pid}?lines=${lines}`);
  }

  /**
   * Start auto-refresh of terminals and sessions
   * Call this in ngOnInit of component
   */
  startAutoRefresh(): Observable<ClaudeTerminalsResponse> {
    return interval(this.autoRefreshInterval).pipe(
      switchMap(() => this.getTerminals())
    );
  }

  /**
   * Manual refresh - call when user clicks refresh button
   */
  refresh(): void {
    this.getTerminals().subscribe();
    this.getSessions().subscribe();
  }

  /**
   * Clear error
   */
  clearError(): void {
    this.error.set(null);
  }
}
