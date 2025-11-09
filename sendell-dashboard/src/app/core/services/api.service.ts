import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Fact } from '../models/fact.model';
import { Project, Metrics, Tool } from '../models/project.model';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private http = inject(HttpClient);
  private baseUrl = '/api';

  // ==================== FACTS ====================

  getFacts(): Observable<{ facts: Fact[] }> {
    return this.http.get<{ facts: Fact[] }>(`${this.baseUrl}/facts`);
  }

  addFact(fact: Fact): Observable<any> {
    return this.http.post(`${this.baseUrl}/facts`, fact);
  }

  deleteFact(index: number): Observable<any> {
    return this.http.delete(`${this.baseUrl}/facts/${index}`);
  }

  // ==================== PROMPTS ====================

  getPrompt(): Observable<{ prompt: string }> {
    return this.http.get<{ prompt: string }>(`${this.baseUrl}/prompts`);
  }

  updatePrompt(prompt: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/prompts`, { prompt });
  }

  // ==================== TOOLS ====================

  getTools(): Observable<{ tools: Tool[] }> {
    return this.http.get<{ tools: Tool[] }>(`${this.baseUrl}/tools`);
  }

  // ==================== PROJECTS ====================

  getProjects(): Observable<{ projects: Project[] }> {
    return this.http.get<{ projects: Project[] }>(`${this.baseUrl}/projects`);
  }

  // ==================== METRICS ====================

  getMetrics(): Observable<Metrics> {
    return this.http.get<Metrics>(`${this.baseUrl}/metrics`);
  }
}
