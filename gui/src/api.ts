import type { Project } from './types.ts';

export interface DataProvider {
  getProject(id: string): Promise<Project>;
  listProjects(): Promise<Project[]>;
}

class HTTPProvider implements DataProvider {
  async getProject(id: string): Promise<Project> {
    const res = await fetch(`/api/projects/${id}`);
    if (!res.ok) throw new Error(`Failed to fetch project: ${res.status} ${res.statusText}`);
    return res.json() as Promise<Project>;
  }

  async listProjects(): Promise<Project[]> {
    const res = await fetch('/api/projects');
    if (!res.ok) throw new Error(`Failed to fetch projects: ${res.status} ${res.statusText}`);
    return res.json() as Promise<Project[]>;
  }
}

export const provider: DataProvider = new HTTPProvider();
