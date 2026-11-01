export interface Citation {
  chunk_id: string;
  snippet: string;
}

export interface Answer {
  text: string;
  citations: Citation[];
  confidence: number;
  is_sufficient: boolean;
}

export interface DocumentSummary {
  filename: string;
  total_chunks: number;
  metadata: Record<string, any>;
}

export interface HealthResponse {
  status: string;
  version: string;
}
