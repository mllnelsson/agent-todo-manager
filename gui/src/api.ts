import type { Project } from './types.ts';
import projectData from '../examples/sample_project.json';

export interface DataProvider {
  getProject(id: string): Promise<Project>;
  listProjects(): Promise<Project[]>;
}

class StaticProvider implements DataProvider {
  async getProject(_id: string): Promise<Project> {
    return projectData as unknown as Project;
  }

  async listProjects(): Promise<Project[]> {
    return [projectData as unknown as Project];
  }
}

export const provider: DataProvider = new StaticProvider();
