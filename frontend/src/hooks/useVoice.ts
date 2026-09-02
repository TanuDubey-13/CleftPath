import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createVoiceSession,
  deleteVoiceSession,
  fetchVoiceExerciseDetail,
  fetchVoiceExercises,
  fetchVoiceOverview,
  fetchVoiceSessionDetail,
  fetchVoiceSessions,
  updateVoiceSession,
} from '../api/voice';
import {
  VoiceQueryParams,
  VoiceSessionCreateRequest,
  VoiceSessionUpdateRequest,
} from '../types';

// ============================================================================
// Overview
// ============================================================================

export const useVoiceOverview = (patientId?: string) => {
  return useQuery({
    queryKey: ['voiceOverview', patientId || 'primary'],
    queryFn: () => fetchVoiceOverview(patientId),
    staleTime: 60 * 1000,
  });
};

// ============================================================================
// Exercises
// ============================================================================

export const useVoiceExercises = (params: VoiceQueryParams = {}) => {
  return useQuery({
    queryKey: ['voiceExercises', params],
    queryFn: () => fetchVoiceExercises(params),
    staleTime: 5 * 60 * 1000,
  });
};

export const useVoiceExercise = (exerciseId?: string) => {
  return useQuery({
    queryKey: ['voiceExercise', exerciseId],
    queryFn: () => {
      if (!exerciseId) throw new Error('Exercise ID is required');
      return fetchVoiceExerciseDetail(exerciseId);
    },
    enabled: !!exerciseId,
  });
};

// ============================================================================
// Sessions
// ============================================================================

export const useVoiceSessions = (params: VoiceQueryParams = {}) => {
  return useQuery({
    queryKey: ['voiceSessions', params],
    queryFn: () => fetchVoiceSessions(params),
    staleTime: 60 * 1000,
  });
};

export const useVoiceSession = (sessionId?: string) => {
  return useQuery({
    queryKey: ['voiceSession', sessionId],
    queryFn: () => {
      if (!sessionId) throw new Error('Session ID is required');
      return fetchVoiceSessionDetail(sessionId);
    },
    enabled: !!sessionId,
  });
};

export const useCreateVoiceSession = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: VoiceSessionCreateRequest) => createVoiceSession(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voiceSessions'] });
      queryClient.invalidateQueries({ queryKey: ['voiceOverview'] });
    },
  });
};

export const useUpdateVoiceSession = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ sessionId, payload }: { sessionId: string; payload: VoiceSessionUpdateRequest }) =>
      updateVoiceSession(sessionId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['voiceSessions'] });
      queryClient.invalidateQueries({ queryKey: ['voiceSession', variables.sessionId] });
      queryClient.invalidateQueries({ queryKey: ['voiceOverview'] });
    },
  });
};

export const useDeleteVoiceSession = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (sessionId: string) => deleteVoiceSession(sessionId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['voiceSessions'] });
      queryClient.invalidateQueries({ queryKey: ['voiceOverview'] });
    },
  });
};
