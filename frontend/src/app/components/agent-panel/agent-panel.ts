import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AgentResponse } from '../../models/chess.model';

@Component({
  selector: 'app-agent-panel',
  imports: [CommonModule],
  templateUrl: './agent-panel.html',
  styleUrl: './agent-panel.css',
})
export class AgentPanel {
  @Input() response: AgentResponse | null = null;
  @Input() loading = false;
  @Input() error: string | null = null;

  formatScore(scoreCp: number | null, mateIn: number | null): string {
    if (mateIn !== null) {
      return mateIn > 0 ? `Mat en ${mateIn}` : `Mat reçu en ${Math.abs(mateIn)}`;
    }
    if (scoreCp === null) return '—';
    const pawns = scoreCp / 100;
    return pawns >= 0 ? `+${pawns.toFixed(2)}` : pawns.toFixed(2);
  }

  winPercent(white: number, draws: number, black: number): number {
    const total = white + draws + black;
    return total > 0 ? Math.round((white / total) * 100) : 0;
  }

  drawPercent(white: number, draws: number, black: number): number {
    const total = white + draws + black;
    return total > 0 ? Math.round((draws / total) * 100) : 0;
  }

  blackPercent(white: number, draws: number, black: number): number {
    const total = white + draws + black;
    return total > 0 ? Math.round((black / total) * 100) : 0;
  }
}
