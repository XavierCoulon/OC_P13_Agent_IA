import { Component, inject, signal } from '@angular/core';
import { AgentPanel } from './components/agent-panel/agent-panel';
import { Chessboard } from './components/chessboard/chessboard';
import { ChessApiService } from './services/chess-api';
import { AgentResponse } from './models/chess.model';

@Component({
  selector: 'app-root',
  imports: [Chessboard, AgentPanel],
  templateUrl: './app.html',
  styleUrl: './app.css',
})
export class App {
  private api = inject(ChessApiService);

  currentFen = signal('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1');
  response = signal<AgentResponse | null>(null);
  loading = signal(false);
  error = signal<string | null>(null);

  onPositionChange(fen: string): void {
    this.currentFen.set(fen);
    this.response.set(null);
    this.error.set(null);
  }

  analyze(): void {
    this.loading.set(true);
    this.error.set(null);

    this.api.analyzePosition(this.currentFen()).subscribe({
      next: (res) => {
        this.response.set(res);
        this.loading.set(false);
      },
      error: (err) => {
        this.error.set(err.error?.detail ?? err.message ?? 'Erreur lors de l\'analyse');
        this.loading.set(false);
      },
    });
  }
}
