import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  PaginatedPathGuideMessages,
  PaginatedPathGuideThreads,
  PathGuideMessage,
  PathGuideMessageCreateRequest,
  PathGuideSuggestedPromptsResponse,
  PathGuideThread,
  PathGuideThreadCreateRequest,
  PathGuideThreadUpdateRequest,
} from '../types';

// ============================================================================
// Suggested Prompts
// ============================================================================

export const fetchSuggestedPrompts = async (): Promise<PathGuideSuggestedPromptsResponse> => {
  const response = await apiClient.get<ApiResponse<PathGuideSuggestedPromptsResponse>>(
    '/pathguide/suggested-prompts'
  );
  return response.data.data;
};

// ============================================================================
// Threads
// ============================================================================

export const fetchThreads = async (
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedPathGuideThreads> => {
  const response = await apiClient.get<ApiResponse<PaginatedPathGuideThreads>>(
    `/pathguide/threads?page=${page}&page_size=${pageSize}`
  );
  return response.data.data;
};

export const fetchThreadDetail = async (threadId: string): Promise<PathGuideThread> => {
  const response = await apiClient.get<ApiResponse<PathGuideThread>>(`/pathguide/threads/${threadId}`);
  return response.data.data;
};

export const createThread = async (payload: PathGuideThreadCreateRequest): Promise<PathGuideThread> => {
  const response = await apiClient.post<ApiResponse<PathGuideThread>>('/pathguide/threads', payload);
  return response.data.data;
};

export const updateThread = async (
  threadId: string,
  payload: PathGuideThreadUpdateRequest
): Promise<PathGuideThread> => {
  const response = await apiClient.patch<ApiResponse<PathGuideThread>>(
    `/pathguide/threads/${threadId}`,
    payload
  );
  return response.data.data;
};

export const deleteThread = async (threadId: string): Promise<void> => {
  await apiClient.delete(`/pathguide/threads/${threadId}`);
};

// ============================================================================
// Messages
// ============================================================================

export const fetchThreadMessages = async (
  threadId: string,
  page: number = 1,
  pageSize: number = 50
): Promise<PaginatedPathGuideMessages> => {
  const response = await apiClient.get<ApiResponse<PaginatedPathGuideMessages>>(
    `/pathguide/threads/${threadId}/messages?page=${page}&page_size=${pageSize}`
  );
  return response.data.data;
};

export const sendMessage = async (
  threadId: string,
  payload: PathGuideMessageCreateRequest
): Promise<PathGuideMessage> => {
  const response = await apiClient.post<ApiResponse<PathGuideMessage>>(
    `/pathguide/threads/${threadId}/messages`,
    payload
  );
  return response.data.data;
};
