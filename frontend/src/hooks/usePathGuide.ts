import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createThread,
  deleteThread,
  fetchSuggestedPrompts,
  fetchThreadDetail,
  fetchThreadMessages,
  fetchThreads,
  sendMessage,
  updateThread,
} from '../api/pathguide';
import {
  PathGuideMessageCreateRequest,
  PathGuideThreadCreateRequest,
  PathGuideThreadUpdateRequest,
} from '../types';

// ============================================================================
// Queries
// ============================================================================

export const usePathGuideSuggestedPrompts = () => {
  return useQuery({
    queryKey: ['pathguideSuggestedPrompts'],
    queryFn: fetchSuggestedPrompts,
    staleTime: 10 * 60 * 1000,
  });
};

export const usePathGuideThreads = (page: number = 1, pageSize: number = 20) => {
  return useQuery({
    queryKey: ['pathguideThreads', page, pageSize],
    queryFn: () => fetchThreads(page, pageSize),
    staleTime: 30 * 1000,
  });
};

export const usePathGuideThread = (threadId?: string) => {
  return useQuery({
    queryKey: ['pathguideThread', threadId],
    queryFn: () => {
      if (!threadId) throw new Error('Thread ID required');
      return fetchThreadDetail(threadId);
    },
    enabled: !!threadId,
  });
};

export const usePathGuideMessages = (threadId?: string, page: number = 1, pageSize: number = 50) => {
  return useQuery({
    queryKey: ['pathguideMessages', threadId, page, pageSize],
    queryFn: () => {
      if (!threadId) throw new Error('Thread ID required');
      return fetchThreadMessages(threadId, page, pageSize);
    },
    enabled: !!threadId,
    staleTime: 10 * 1000,
  });
};

// ============================================================================
// Mutations
// ============================================================================

export const useCreatePathGuideThread = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: PathGuideThreadCreateRequest) => createThread(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pathguideThreads'] });
    },
  });
};

export const useUpdatePathGuideThread = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ threadId, payload }: { threadId: string; payload: PathGuideThreadUpdateRequest }) =>
      updateThread(threadId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['pathguideThreads'] });
      queryClient.invalidateQueries({ queryKey: ['pathguideThread', variables.threadId] });
    },
  });
};

export const useDeletePathGuideThread = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (threadId: string) => deleteThread(threadId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['pathguideThreads'] });
    },
  });
};

export const useSendMessage = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ threadId, payload }: { threadId: string; payload: PathGuideMessageCreateRequest }) =>
      sendMessage(threadId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['pathguideMessages', variables.threadId] });
      queryClient.invalidateQueries({ queryKey: ['pathguideThreads'] });
    },
  });
};
