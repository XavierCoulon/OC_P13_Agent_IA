import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AgentResponse } from '../models/chess.model';

@Injectable({ providedIn: 'root' })
export class ChessApiService {
  private http = inject(HttpClient);
  private baseUrl = '/api/v1';

  analyzePosition(fen: string): Observable<AgentResponse> {
    return this.http.post<AgentResponse>(`${this.baseUrl}/agent`, { fen });
  }
}
