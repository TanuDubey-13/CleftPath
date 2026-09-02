import { apiClient } from '../lib/apiClient';
import { HealthResponse } from '../types/health';

export const fetchHealth = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>('/health');
  return response.data;
};
