import { Component, OnInit, OnDestroy, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './core/services/api.service';
import { WebSocketService } from './core/services/websocket.service';
import { ClaudeTerminalsService } from './core/services/claude-terminals.service';
import { TerminalService } from './core/services/terminal.service';
import { Fact } from './core/models/fact.model';
import { Project, Metrics, Tool, ProjectStatus } from './core/models/project.model';
import { ClaudeTerminal, ClaudeSession } from './core/models/claude-terminal.model';
import { ActivityGraphComponent } from './components/activity-graph.component';
import { TerminalComponent } from './components/terminal.component';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, ActivityGraphComponent, TerminalComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App implements OnInit, OnDestroy {
  private api = inject(ApiService);
  private ws = inject(WebSocketService);
  claudeService = inject(ClaudeTerminalsService);
  terminalService = inject(TerminalService);

  // Active tab
  activeTab = signal<string>('proyectos');

  // Memorias tab
  facts = signal<Fact[]>([]);
  newFactText = '';
  newFactCategory = 'general';

  // Prompts tab
  promptText = signal<string>('');

  // Tools tab
  tools = signal<Tool[]>([]);

  // Proyectos tab
  projects = signal<Project[]>([]);
  metrics = signal<Metrics>({ cpu: 0, ram: 0, terminals: 0 });
  currentTime = signal<string>(new Date().toLocaleTimeString());
  loadingProjectPid = signal<number | null>(null); // Track which project is loading

  private clockInterval: any;

  ngOnInit() {
    // Connect WebSocket
    this.ws.connect();

    // Subscribe to WebSocket updates
    this.ws.messages$.subscribe((message) => {
      if (message.type === 'update') {
        this.projects.set(message.data.projects);
        this.metrics.set(message.data.metrics);
      }
    });

    // Update clock every second
    this.clockInterval = setInterval(() => {
      this.currentTime.set(new Date().toLocaleTimeString());
    }, 1000);

    // Load initial data based on active tab
    this.loadTabData();
  }

  ngOnDestroy() {
    this.ws.disconnect();
    if (this.clockInterval) {
      clearInterval(this.clockInterval);
    }
  }

  setActiveTab(tab: string) {
    this.activeTab.set(tab);
    this.loadTabData();
  }

  private loadTabData() {
    const tab = this.activeTab();

    if (tab === 'memorias') {
      this.api.getFacts().subscribe(data => this.facts.set(data.facts));
    } else if (tab === 'prompts') {
      this.api.getPrompt().subscribe(data => this.promptText.set(data.prompt));
    } else if (tab === 'herramientas') {
      this.api.getTools().subscribe(data => this.tools.set(data.tools));
    } else if (tab === 'proyectos') {
      this.api.getProjects().subscribe(data => this.projects.set(data.projects));
      this.api.getMetrics().subscribe(data => this.metrics.set(data));
    } else if (tab === 'claude-terminals') {
      this.claudeService.getTerminals().subscribe();
      this.claudeService.getSessions().subscribe();
    }
  }

  // Projects methods
  onProjectClick(project: Project) {
    console.log('[App] 🖱️ Project clicked:', project.name, 'State:', project.state, 'PID:', project.pid);

    if (project.state === 'offline') {
      // ROJO: No hay terminal → Crear nueva terminal
      console.log('[App] 🔴 State is OFFLINE - Creating new terminal...');
      this.loadingProjectPid.set(project.pid);

      this.api.openTerminal(project.workspace_path, project.pid, project.name).subscribe({
        next: (result) => {
          console.log('[App] ✅ Terminal created successfully:', result);

          // Mostrar terminal embebida
          console.log('[App] Opening terminal modal for PID:', project.pid);
          this.terminalService.openTerminal(project.pid);

          // Reload projects
          console.log('[App] Reloading projects in 1 second...');
          setTimeout(() => {
            this.api.getProjects().subscribe(data => {
              console.log('[App] Projects reloaded:', data.projects.length, 'projects');
              this.projects.set(data.projects);
              this.loadingProjectPid.set(null);
            });
          }, 1000);
        },
        error: (err) => {
          console.error('[App] ❌ Error creating terminal:', err);
          alert('Error al crear terminal: ' + err.message);
          this.loadingProjectPid.set(null);
        }
      });
    } else if (project.state === 'ready' || project.state === 'working') {
      // AZUL/VERDE: Terminal existe → Mostrar/ocultar terminal existente
      console.log('[App] 🔵/🟢 State is', project.state.toUpperCase(), '- Toggling terminal visibility');
      this.terminalService.toggleTerminal(project.pid);
    } else {
      console.warn('[App] ⚠️ Unknown project state:', project.state);
    }
  }

  getCurrentProject() {
    const pid = this.terminalService.currentTerminalPid();
    if (!pid) return null;
    return this.projects().find(p => p.pid === pid) || null;
  }

  // Claude Terminals methods
  refreshClaudeTerminals() {
    this.claudeService.refresh();
  }

  // Memorias methods
  addFact() {
    if (!this.newFactText.trim()) return;

    const fact: Fact = {
      fact: this.newFactText,
      category: this.newFactCategory
    };

    this.api.addFact(fact).subscribe(() => {
      this.api.getFacts().subscribe(data => this.facts.set(data.facts));
      this.newFactText = '';
    });
  }

  deleteFact(index: number) {
    this.api.deleteFact(index).subscribe(() => {
      this.api.getFacts().subscribe(data => this.facts.set(data.facts));
    });
  }

  // Prompts methods
  savePrompt() {
    this.api.updatePrompt(this.promptText()).subscribe(() => {
      alert('Prompt guardado (requiere reiniciar agente)');
    });
  }
}
