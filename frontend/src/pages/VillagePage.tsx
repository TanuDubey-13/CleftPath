import React, { useState } from 'react';
import { Plus, Search } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import {
  useCreateVillageComment,
  useCreateVillagePost,
  useDeleteVillageComment,
  useDeleteVillagePost,
  useReportVillageComment,
  useReportVillagePost,
  useToggleVillageReaction,
  useUpdateVillagePost,
  useVillageChannels,
  useVillageComments,
  useVillagePost,
  useVillagePosts,
} from '../hooks/useVillage';
import { VillageSafetyNotice } from '../components/village/VillageSafetyNotice';
import { VillageChannelSidebar } from '../components/village/VillageChannelSidebar';
import { VillagePostCard } from '../components/village/VillagePostCard';
import { VillagePostComposerModal } from '../components/village/VillagePostComposerModal';
import { VillagePostModal } from '../components/village/VillagePostModal';
import { VillageReportModal } from '../components/village/VillageReportModal';
import { VillageSkeleton } from '../components/village/VillageSkeleton';
import { Button } from '../components/ui/Button';
import { VillagePost } from '../types';

export const VillagePage: React.FC = () => {
  const { user } = useAuth();

  const [selectedChannelId, setSelectedChannelId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [isComposerOpen, setIsComposerOpen] = useState(false);
  const [editingPost, setEditingPost] = useState<VillagePost | null>(null);
  const [activePostId, setActivePostId] = useState<string | null>(null);

  // Report modal state
  const [reportTarget, setReportTarget] = useState<{ type: 'post' | 'comment'; id: string } | null>(null);

  // Queries
  const { data: channelsData, isLoading: isChannelsLoading } = useVillageChannels();
  const { data: postsData, isLoading: isPostsLoading } = useVillagePosts(
    selectedChannelId || undefined,
    searchQuery || undefined
  );
  const { data: activePost } = useVillagePost(activePostId || undefined);
  const { data: commentsData, isLoading: isCommentsLoading } = useVillageComments(activePostId || undefined);

  // Mutations
  const createPostMutation = useCreateVillagePost();
  const updatePostMutation = useUpdateVillagePost();
  const deletePostMutation = useDeleteVillagePost();
  const createCommentMutation = useCreateVillageComment();
  const deleteCommentMutation = useDeleteVillageComment();
  const toggleReactionMutation = useToggleVillageReaction();
  const reportPostMutation = useReportVillagePost();
  const reportCommentMutation = useReportVillageComment();

  const handleCreateOrUpdatePost = async (data: {
    channel_id: string;
    title: string;
    content: string;
    author_alias?: string;
  }) => {
    if (editingPost) {
      await updatePostMutation.mutateAsync({
        postId: editingPost.id,
        payload: { title: data.title, content: data.content },
      });
      setEditingPost(null);
    } else {
      await createPostMutation.mutateAsync(data);
    }
  };

  const handleToggleReaction = async (postId: string, reactionType: string) => {
    await toggleReactionMutation.mutateAsync({
      postId,
      payload: { reaction_type: reactionType },
    });
  };

  const handleAddComment = async (postId: string, content: string) => {
    await createCommentMutation.mutateAsync({
      postId,
      payload: { content },
    });
  };

  const handleDeleteComment = async (commentId: string) => {
    await deleteCommentMutation.mutateAsync(commentId);
  };

  const handleSubmitReport = async (targetId: string, reason: string, details?: string) => {
    if (reportTarget?.type === 'post') {
      await reportPostMutation.mutateAsync({
        postId: targetId,
        payload: { reason, details },
      });
    } else if (reportTarget?.type === 'comment') {
      await reportCommentMutation.mutateAsync({
        commentId: targetId,
        payload: { reason, details },
      });
    }
  };

  const channels = channelsData?.items || [];
  const posts = postsData?.items || [];
  const comments = commentsData?.items || [];

  return (
    <div className="space-y-6 animate-fadeIn max-w-7xl mx-auto">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">The Village</h1>
          <p className="text-sm text-charcoal-600">
            A safe, supportive peer community for parents and individuals navigating cleft journeys.
          </p>
        </div>

        <Button
          variant="primary"
          size="md"
          onClick={() => {
            setEditingPost(null);
            setIsComposerOpen(true);
          }}
          leftIcon={<Plus className="w-4 h-4" />}
        >
          New Post
        </Button>
      </div>

      {/* Safety Notice */}
      <VillageSafetyNotice />

      {/* Main Two-Panel Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Column: Channels */}
        <div className="lg:col-span-1">
          <VillageChannelSidebar
            channels={channels}
            selectedChannelId={selectedChannelId}
            onSelectChannel={(id) => setSelectedChannelId(id)}
            isLoading={isChannelsLoading}
          />
        </div>

        {/* Right Column: Community Feed */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search bar */}
          <div className="relative">
            <Search className="w-4 h-4 text-charcoal-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search community experiences and discussions..."
              className="w-full pl-10 pr-4 py-2.5 bg-white border border-stone-200/90 rounded-2xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs sm:text-sm text-charcoal-900 shadow-warm-xs"
            />
          </div>

          {/* Feed Content */}
          {isPostsLoading ? (
            <VillageSkeleton />
          ) : posts.length === 0 ? (
            <div className="p-12 text-center bg-white rounded-3xl border border-stone-200 space-y-3">
              <h3 className="font-heading font-bold text-base text-teal-900">
                No discussions in this channel yet
              </h3>
              <p className="text-xs text-charcoal-600 max-w-md mx-auto">
                Be the first to share a question or helpful experience for other families on this pathway!
              </p>
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  setEditingPost(null);
                  setIsComposerOpen(true);
                }}
              >
                Start a Conversation
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {posts.map((post) => (
                <VillagePostCard
                  key={post.id}
                  post={post}
                  currentUserId={user?.id}
                  onOpenPost={(id) => setActivePostId(id)}
                  onToggleReaction={handleToggleReaction}
                  onEditPost={(p) => {
                    setEditingPost(p);
                    setIsComposerOpen(true);
                  }}
                  onDeletePost={(id) => deletePostMutation.mutate(id)}
                  onReportPost={(id) => setReportTarget({ type: 'post', id })}
                />
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Post Composer Modal (Create / Edit) */}
      <VillagePostComposerModal
        isOpen={isComposerOpen}
        channels={channels}
        selectedChannelId={selectedChannelId}
        editingPost={editingPost}
        onClose={() => {
          setIsComposerOpen(false);
          setEditingPost(null);
        }}
        onSubmitPost={handleCreateOrUpdatePost}
        isSubmitting={createPostMutation.isPending || updatePostMutation.isPending}
      />

      {/* Post Detail & Comments Modal */}
      <VillagePostModal
        post={activePost || null}
        comments={comments}
        currentUserId={user?.id}
        isOpen={!!activePostId}
        onClose={() => setActivePostId(null)}
        onToggleReaction={handleToggleReaction}
        onAddComment={handleAddComment}
        onDeleteComment={handleDeleteComment}
        onReportPost={(id) => setReportTarget({ type: 'post', id })}
        onReportComment={(id) => setReportTarget({ type: 'comment', id })}
        isLoadingComments={isCommentsLoading}
      />

      {/* Report Modal */}
      <VillageReportModal
        isOpen={!!reportTarget}
        targetType={reportTarget?.type || 'post'}
        targetId={reportTarget?.id || ''}
        onClose={() => setReportTarget(null)}
        onSubmitReport={handleSubmitReport}
      />
    </div>
  );
};
