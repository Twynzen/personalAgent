import { Component, OnInit, OnDestroy, signal, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './core/services/api.service';
import { WebSocketService } from './core/services/websocket.service';
import { Fact } from './core/models/fact.model';
import { Project, Metrics, Tool, ProjectStatus } from './core/models/project.model';
import { ActivityGraphComponent } from './components/activity-graph.component';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, ActivityGraphComponent],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App implements OnInit, OnDestroy {
  private api = inject(ApiService);
  private ws = inject(WebSocketService);

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

  private clockInterval: any;

  ngOnInit() {
    // Connect WebSocket
    this.ws.connect();

    // Subscribe to WebSocket updates
    this.ws.messages$.subscribe((message) => {
      if (message.type === 'update') {
        const projectsWithStatus = this.mapProjectsWithStatus(message.data.projects);
        this.projects.set(projectsWithStatus);
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

  private mapProjectsWithStatus(projects: Project[]): Project[] {
    // For now, assign mock statuses for visual testing
    // TODO: Replace with real detection logic
    return projects.map((project, index) => {
      let status: ProjectStatus = 'offline';

      // Mock logic for testing:
      // - First project: running
      // - Second project: idle
      // - Rest: offline
      if (index === 0) {
        status = 'running';
      } else if (index === 1) {
        status = 'idle';
      }

      return { ...project, status };
    });
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
    }
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
