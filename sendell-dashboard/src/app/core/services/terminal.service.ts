import { Injectable, signal } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class TerminalService {
  // Map of project PIDs to terminal visibility
  private openTerminals = signal<Map<number, boolean>>(new Map());

  openTerminal(projectPid: number) {
    this.openTerminals.update(map => {
      const newMap = new Map(map);
      newMap.set(projectPid, true);
      return newMap;
    });
  }

  closeTerminal(projectPid: number) {
    this.openTerminals.update(map => {
      const newMap = new Map(map);
      newMap.delete(projectPid);
      return newMap;
    });
  }

  isTerminalOpen(projectPid: number): boolean {
    return this.openTerminals().has(projectPid);
  }

  toggleTerminal(projectPid: number) {
    if (this.isTerminalOpen(projectPid)) {
      this.closeTerminal(projectPid);
    } else {
      this.openTerminal(projectPid);
    }
  }
}
