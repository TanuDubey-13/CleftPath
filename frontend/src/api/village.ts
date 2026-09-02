import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  PaginatedVillageChannels,
  PaginatedVillageComments,
  PaginatedVillagePosts,
  VillageChannel,
  VillageComment,
  VillageCommentCreateRequest,
  VillageCommentUpdateRequest,
  VillagePost,
  VillagePostCreateRequest,
  VillagePostUpdateRequest,
  VillageReactionRequest,
  VillageReactionResponse,
  VillageReportCreateRequest,
  VillageReportResponse,
} from '../types';

// ============================================================================
// Channels
// ============================================================================

export const fetchChannels = async (
  page: number = 1,
  pageSize: number = 50
): Promise<PaginatedVillageChannels> => {
  const response = await apiClient.get<ApiResponse<PaginatedVillageChannels>>(
    `/village/channels?page=${page}&page_size=${pageSize}`
  );
  return response.data.data;
};

export const fetchChannelDetail = async (channelId: string): Promise<VillageChannel> => {
  const response = await apiClient.get<ApiResponse<VillageChannel>>(`/village/channels/${channelId}`);
  return response.data.data;
};

// ============================================================================
// Posts
// ============================================================================

export const fetchPosts = async (
  channelId?: string,
  search?: string,
  page: number = 1,
  pageSize: number = 20
): Promise<PaginatedVillagePosts> => {
  const params = new URLSearchParams({
    page: page.toString(),
    page_size: pageSize.toString(),
  });
  if (channelId) params.append('channel_id', channelId);
  if (search) params.append('search', search);

  const response = await apiClient.get<ApiResponse<PaginatedVillagePosts>>(
    `/village/posts?${params.toString()}`
  );
  return response.data.data;
};

export const fetchPostDetail = async (postId: string): Promise<VillagePost> => {
  const response = await apiClient.get<ApiResponse<VillagePost>>(`/village/posts/${postId}`);
  return response.data.data;
};

export const createPost = async (payload: VillagePostCreateRequest): Promise<VillagePost> => {
  const response = await apiClient.post<ApiResponse<VillagePost>>('/village/posts', payload);
  return response.data.data;
};

export const updatePost = async (
  postId: string,
  payload: VillagePostUpdateRequest
): Promise<VillagePost> => {
  const response = await apiClient.patch<ApiResponse<VillagePost>>(`/village/posts/${postId}`, payload);
  return response.data.data;
};

export const deletePost = async (postId: string): Promise<void> => {
  await apiClient.delete(`/village/posts/${postId}`);
};

// ============================================================================
// Comments
// ============================================================================

export const fetchPostComments = async (
  postId: string,
  page: number = 1,
  pageSize: number = 50
): Promise<PaginatedVillageComments> => {
  const response = await apiClient.get<ApiResponse<PaginatedVillageComments>>(
    `/village/posts/${postId}/comments?page=${page}&page_size=${pageSize}`
  );
  return response.data.data;
};

export const createComment = async (
  postId: string,
  payload: VillageCommentCreateRequest
): Promise<VillageComment> => {
  const response = await apiClient.post<ApiResponse<VillageComment>>(
    `/village/posts/${postId}/comments`,
    payload
  );
  return response.data.data;
};

export const updateComment = async (
  commentId: string,
  payload: VillageCommentUpdateRequest
): Promise<VillageComment> => {
  const response = await apiClient.patch<ApiResponse<VillageComment>>(
    `/village/comments/${commentId}`,
    payload
  );
  return response.data.data;
};

export const deleteComment = async (commentId: string): Promise<void> => {
  await apiClient.delete(`/village/comments/${commentId}`);
};

// ============================================================================
// Reactions & Reports
// ============================================================================

export const toggleReaction = async (
  postId: string,
  payload: VillageReactionRequest
): Promise<VillageReactionResponse> => {
  const response = await apiClient.post<ApiResponse<VillageReactionResponse>>(
    `/village/posts/${postId}/reactions`,
    payload
  );
  return response.data.data;
};

export const reportPost = async (
  postId: string,
  payload: VillageReportCreateRequest
): Promise<VillageReportResponse> => {
  const response = await apiClient.post<ApiResponse<VillageReportResponse>>(
    `/village/posts/${postId}/report`,
    payload
  );
  return response.data.data;
};

export const reportComment = async (
  commentId: string,
  payload: VillageReportCreateRequest
): Promise<VillageReportResponse> => {
  const response = await apiClient.post<ApiResponse<VillageReportResponse>>(
    `/village/comments/${commentId}/report`,
    payload
  );
  return response.data.data;
};
