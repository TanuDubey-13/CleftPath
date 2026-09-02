import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import {
  createComment,
  createPost,
  deleteComment,
  deletePost,
  fetchChannelDetail,
  fetchChannels,
  fetchPostComments,
  fetchPostDetail,
  fetchPosts,
  reportComment,
  reportPost,
  toggleReaction,
  updateComment,
  updatePost,
} from '../api/village';
import {
  VillageCommentCreateRequest,
  VillageCommentUpdateRequest,
  VillagePostCreateRequest,
  VillagePostUpdateRequest,
  VillageReactionRequest,
  VillageReportCreateRequest,
} from '../types';

// ============================================================================
// Queries
// ============================================================================

export const useVillageChannels = (page: number = 1, pageSize: number = 50) => {
  return useQuery({
    queryKey: ['villageChannels', page, pageSize],
    queryFn: () => fetchChannels(page, pageSize),
    staleTime: 60 * 1000,
  });
};

export const useVillageChannel = (channelId?: string) => {
  return useQuery({
    queryKey: ['villageChannel', channelId],
    queryFn: () => {
      if (!channelId) throw new Error('Channel ID required');
      return fetchChannelDetail(channelId);
    },
    enabled: !!channelId,
  });
};

export const useVillagePosts = (
  channelId?: string,
  search?: string,
  page: number = 1,
  pageSize: number = 20
) => {
  return useQuery({
    queryKey: ['villagePosts', channelId, search, page, pageSize],
    queryFn: () => fetchPosts(channelId, search, page, pageSize),
    staleTime: 30 * 1000,
  });
};

export const useVillagePost = (postId?: string) => {
  return useQuery({
    queryKey: ['villagePost', postId],
    queryFn: () => {
      if (!postId) throw new Error('Post ID required');
      return fetchPostDetail(postId);
    },
    enabled: !!postId,
  });
};

export const useVillageComments = (postId?: string, page: number = 1, pageSize: number = 50) => {
  return useQuery({
    queryKey: ['villageComments', postId, page, pageSize],
    queryFn: () => {
      if (!postId) throw new Error('Post ID required');
      return fetchPostComments(postId, page, pageSize);
    },
    enabled: !!postId,
    staleTime: 15 * 1000,
  });
};

// ============================================================================
// Mutations
// ============================================================================

export const useCreateVillagePost = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: VillagePostCreateRequest) => createPost(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
      queryClient.invalidateQueries({ queryKey: ['villageChannels'] });
    },
  });
};

export const useUpdateVillagePost = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ postId, payload }: { postId: string; payload: VillagePostUpdateRequest }) =>
      updatePost(postId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
      queryClient.invalidateQueries({ queryKey: ['villagePost', variables.postId] });
    },
  });
};

export const useDeleteVillagePost = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (postId: string) => deletePost(postId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
      queryClient.invalidateQueries({ queryKey: ['villageChannels'] });
    },
  });
};

export const useCreateVillageComment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ postId, payload }: { postId: string; payload: VillageCommentCreateRequest }) =>
      createComment(postId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['villageComments', variables.postId] });
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
      queryClient.invalidateQueries({ queryKey: ['villagePost', variables.postId] });
    },
  });
};

export const useUpdateVillageComment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ commentId, payload }: { commentId: string; payload: VillageCommentUpdateRequest }) =>
      updateComment(commentId, payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['villageComments'] });
    },
  });
};

export const useDeleteVillageComment = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (commentId: string) => deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['villageComments'] });
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
    },
  });
};

export const useToggleVillageReaction = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ postId, payload }: { postId: string; payload: VillageReactionRequest }) =>
      toggleReaction(postId, payload),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['villagePosts'] });
      queryClient.invalidateQueries({ queryKey: ['villagePost', variables.postId] });
    },
  });
};

export const useReportVillagePost = () => {
  return useMutation({
    mutationFn: ({ postId, payload }: { postId: string; payload: VillageReportCreateRequest }) =>
      reportPost(postId, payload),
  });
};

export const useReportVillageComment = () => {
  return useMutation({
    mutationFn: ({ commentId, payload }: { commentId: string; payload: VillageReportCreateRequest }) =>
      reportComment(commentId, payload),
  });
};
