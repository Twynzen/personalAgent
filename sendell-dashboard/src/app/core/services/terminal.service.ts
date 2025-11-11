import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TerminalService {
  // Track the currently open terminal (only one modal at a time)
  private _currentTerminalPid = signal<number | null>(null);

  openTerminal(projectPid: number) {
    this._currentTerminalPid.set(projectPid);
  }

  closeTerminal() {
    this._currentTerminalPid.set(null);
  }

  toggleTerminal(projectPid: number) {
    if (this._currentTerminalPid() === projectPid) {
      this.closeTerminal();
    } else {
      this.openTerminal(projectPid);
    }
  }

  currentTerminalPid() {
    return this._currentTerminalPid();
  }

  isTerminalOpen(projectPid: number): boolean {
    return this._currentTerminalPid() === projectPid;
  }
}
