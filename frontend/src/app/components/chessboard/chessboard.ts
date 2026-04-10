import { Component, EventEmitter, Output, ViewChild } from '@angular/core';
import { NgxChessBoardModule, NgxChessBoardView } from 'ngx-chess-board';

@Component({
  selector: 'app-chessboard',
  imports: [NgxChessBoardModule],
  templateUrl: './chessboard.html',
  styleUrl: './chessboard.css',
})
export class Chessboard {
  @ViewChild('board') board!: NgxChessBoardView;
  @Output() positionChange = new EventEmitter<string>();

  onMoveChange(): void {
    this.positionChange.emit(this.board.getFEN());
  }

  reset(): void {
    this.board.reset();
    this.positionChange.emit(this.board.getFEN());
  }
}
