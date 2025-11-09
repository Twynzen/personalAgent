export interface Project {
  pid: number;
  name: string;
  workspace_name: string;
  workspace_path: string;
  workspace_type: string;
  is_running?: boolean;
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
