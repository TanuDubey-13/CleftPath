import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createFeedingLog,
  createGrowthRecord,
  createNAMLog,
  deleteFeedingLog,
  deleteGrowthRecord,
  deleteNAMLog,
  fetchCareOverview,
  fetchFeedingLogDetail,
  fetchFeedingLogs,
  fetchGrowthRecordDetail,
  fetchGrowthRecords,
  fetchNAMLogDetail,
  fetchNAMLogs,
  updateFeedingLog,
  updateGrowthRecord,
  updateNAMLog,
} from '../api/care';
import {
  CareQueryParams,
  FeedingLogCreateRequest,
  FeedingLogUpdateRequest,
  GrowthRecordCreateRequest,
  GrowthRecordUpdateRequest,
  NAMTapingLogCreateRequest,
  NAMTapingLogUpdateRequest,
} from '../types';

// ============================================================================
// Care Overview Hook
// ============================================================================

export const useCareOverview = (patientId?: string) => {
  return useQuery({
    queryKey: ['careOverview', patientId || 'primary'],
    queryFn: () => fetchCareOverview(patientId),
    staleTime: 60 * 1000,
  });
};

// ============================================================================
// Feeding Hooks
// ============================================================================

export const useFeedingLogs = (params: CareQueryParams = {}) => {
  return useQuery({
    queryKey: ['feedingLogs', params],
    queryFn: () => fetchFeedingLogs(params),
    staleTime: 60 * 1000,
  });
};

export const useFeedingLog = (logId?: string) => {
  return useQuery({
    queryKey: ['feedingLog', logId],
    queryFn: () => {
      if (!logId) throw new Error('Log ID is required');
      return fetchFeedingLogDetail(logId);
    },
    enabled: !!logId,
  });
};

export const useCreateFeedingLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: FeedingLogCreateRequest) => createFeedingLog(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedingLogs'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useUpdateFeedingLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ logId, payload }: { logId: string; payload: FeedingLogUpdateRequest }) =>
      updateFeedingLog(logId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['feedingLogs'] });
      queryClient.invalidateQueries({ queryKey: ['feedingLog', variables.logId] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useDeleteFeedingLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (logId: string) => deleteFeedingLog(logId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['feedingLogs'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

// ============================================================================
// Growth Hooks
// ============================================================================

export const useGrowthRecords = (params: CareQueryParams = {}) => {
  return useQuery({
    queryKey: ['growthRecords', params],
    queryFn: () => fetchGrowthRecords(params),
    staleTime: 60 * 1000,
  });
};

export const useGrowthRecord = (recordId?: string) => {
  return useQuery({
    queryKey: ['growthRecord', recordId],
    queryFn: () => {
      if (!recordId) throw new Error('Record ID is required');
      return fetchGrowthRecordDetail(recordId);
    },
    enabled: !!recordId,
  });
};

export const useCreateGrowthRecord = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: GrowthRecordCreateRequest) => createGrowthRecord(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['growthRecords'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useUpdateGrowthRecord = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({
      recordId,
      payload,
    }: {
      recordId: string;
      payload: GrowthRecordUpdateRequest;
    }) => updateGrowthRecord(recordId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['growthRecords'] });
      queryClient.invalidateQueries({ queryKey: ['growthRecord', variables.recordId] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useDeleteGrowthRecord = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (recordId: string) => deleteGrowthRecord(recordId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['growthRecords'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

// ============================================================================
// NAM / Taping Hooks
// ============================================================================

export const useNAMLogs = (params: CareQueryParams = {}) => {
  return useQuery({
    queryKey: ['namLogs', params],
    queryFn: () => fetchNAMLogs(params),
    staleTime: 60 * 1000,
  });
};

export const useNAMLog = (logId?: string) => {
  return useQuery({
    queryKey: ['namLog', logId],
    queryFn: () => {
      if (!logId) throw new Error('Log ID is required');
      return fetchNAMLogDetail(logId);
    },
    enabled: !!logId,
  });
};

export const useCreateNAMLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: NAMTapingLogCreateRequest) => createNAMLog(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['namLogs'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useUpdateNAMLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ logId, payload }: { logId: string; payload: NAMTapingLogUpdateRequest }) =>
      updateNAMLog(logId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['namLogs'] });
      queryClient.invalidateQueries({ queryKey: ['namLog', variables.logId] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};

export const useDeleteNAMLog = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (logId: string) => deleteNAMLog(logId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['namLogs'] });
      queryClient.invalidateQueries({ queryKey: ['careOverview'] });
    },
  });
};
