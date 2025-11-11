export type ProjectStatus = 'working' | 'ready' | 'offline';
export type BridgeStatus = 'idle' | 'working' | 'error';

export interface Project {
  pid: number;
  name: string;
  workspace_path: string;
  workspace_type: string;
  state: ProjectStatus;
  has_terminal: boolean;
  bridge_status: BridgeStatus;
  current_task: string | null;
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
