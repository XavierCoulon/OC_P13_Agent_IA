export interface TheoreticalMove {
  uci: string;
  san: string;
  white: number;
  draws: number;
  black: number;
}

export interface EvaluationResponse {
  fen: string;
  score_cp: number | null;
  mate_in: number | null;
  best_move_uci: string;
  best_move_san: string;
}

export interface VectorSearchResult {
  opening_name: string;
  chunk_text: string;
  chunk_index: number;
  score: number;
}

export interface VideoResult {
  videoId: string;
  title: string;
  description: string;
  channelTitle: string;
  publishedAt: string;
  thumbnailUrl: string;
  watchUrl: string;
  embedUrl: string;
}

export interface AgentResponse {
  fen: string;
  opening_name: string | null;
  is_theoretical: boolean;
  moves: TheoreticalMove[];
  evaluation: EvaluationResponse | null;
  rag_context: VectorSearchResult[];
  videos: VideoResult[];
}
