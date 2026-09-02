import { useQuery } from '@tanstack/react-query';
import { fetchHealth } from '../api/health';
import { HealthResponse } from '../types/health';

export const useHealth = () => {
  return useQuery<HealthResponse, Error>({
    queryKey: ['system', 'health'],
    queryFn: fetchHealth,
    refetchInterval: 30000, // Periodic check every 30 seconds
  });
};
