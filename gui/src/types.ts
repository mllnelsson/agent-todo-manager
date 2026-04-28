export type Status = 'todo' | 'in_progress' | 'completed';
export type Action = 'started' | 'completed';
export type EntityType = 'story' | 'task' | 'step';

export interface Step {
  id: string;
  seq: number;
  title: string;
  description: string;
  created_at: string;
  updated_at: string;
}

export interface Task {
  id: string;
  seq: number;
  prefix: string | null;
  title: string;
  description: string;
  status: Status;
  created_at: string;
  updated_at: string;
  steps: Step[];
}

export interface Story {
  id: string;
  seq: number;
  title: string;
  description: string;
  status: Status;
  created_at: string;
  updated_at: string;
  tasks: Task[];
}

export interface Completion {
  id: string;
  entity_type: EntityType;
  entity_id: string;
  action: Action;
  agent_name: string;
  session_id: string;
  branch: string | null;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: string;
  title: string;
  description: string;
  status: Status;
  created_at: string;
  updated_at: string;
  stories: Story[];
  bugs: Task[];
  hotfixes: Task[];
  completions: Completion[];
}
