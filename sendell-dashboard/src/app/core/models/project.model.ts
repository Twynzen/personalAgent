export type ProjectStatus = 'working' | 'ready' | 'offline';

export interface Project {
  pid: number;
  name: string;
  workspace_path: string;
  workspace_type: string;
  state: ProjectStatus;
  has_terminal: boolean;
  claude_active: boolean;
  claude_working: boolean;
}

export interface Metrics {
  cpu: number;
  ram: number;
  terminals: number;
}

export interface Tool {
  name: string;
  description: string;
}
