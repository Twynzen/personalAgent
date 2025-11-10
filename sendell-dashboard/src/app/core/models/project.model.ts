export type ProjectStatus = 'running' | 'idle' | 'offline';

export interface Project {
  pid: number;
  name: string;
  workspace_name: string;
  workspace_path: string;
  workspace_type: string;
  status: ProjectStatus;
  is_running?: boolean; // Keep for backward compatibility
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
