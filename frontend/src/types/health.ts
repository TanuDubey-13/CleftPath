export interface DatabaseHealth {
  connected: boolean;
  latency_ms: number | null;
  pgvector_available: boolean;
  error: string | null;
}

export interface HealthResponse {
  status: 'healthy' | 'degraded';
  service: string;
  version: string;
  environment: string;
  tagline: string;
  database: DatabaseHealth;
  timestamp: string;
}
