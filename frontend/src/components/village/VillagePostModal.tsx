import React, { useState } from 'react';
import { X, Send, Heart, MessageSquare, Trash2, ShieldAlert } from 'lucide-react';
import { VillageComment, VillagePost } from '../../types';
import { Button } from '../ui/Button';
import { Badge } from '../ui/Badge';

interface VillagePostModalProps {
  post: VillagePost | null;
  comments: VillageComment[];
  currentUserId?: string;
  isOpen: boolean;
  onClose: () => void;
  onToggleReaction: (postId: string, reactionType: string) => void;
  onAddComment: (postId: string, content: string, alias?: string) => Promise<void>;
  onDeleteComment: (commentId: string) => Promise<void>;
  onReportPost?: (postId: string) => void;
  onReportComment?: (commentId: string) => void;
  isLoadingComments?: boolean;
}

export const VillagePostModal: React.FC<VillagePostModalProps> = ({
  post,
  comments,
  currentUserId,
  isOpen,
  onClose,
  onToggleReaction,
  onAddComment,
  onDeleteComment,
  onReportPost,
  onReportComment,
  isLoadingComments = false,
}) => {
  const [commentText, setCommentText] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen || !post) return null;

  const handleCommentSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || isSubmitting) return;

    setIsSubmitting(true);
    try {
      await onAddComment(post.id, commentText.trim());
      setCommentText('');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-2xl rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            {post.channel_name && (
              <Badge variant="teal" size="sm">
                #{post.channel_name}
              </Badge>
            )}
            <span className="text-[11px] text-charcoal-500">
              {new Date(post.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', year: 'numeric' })}
            </span>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Post Body & Scrollable Discussion */}
        <div className="p-5 overflow-y-auto space-y-6 flex-1 text-xs sm:text-sm">
          {/* Main Post */}
          <div className="space-y-3 pb-4 border-b border-stone-100">
            <div className="flex items-center gap-2.5">
              <div className="w-9 h-9 rounded-full bg-teal-100 text-teal-900 flex items-center justify-center text-sm font-bold shadow-warm-xs">
                {post.author_alias.charAt(0).toUpperCase()}
              </div>
              <div>
                <span className="font-bold text-xs text-charcoal-900 block">
                  {post.author_alias}
                </span>
                <span className="text-[10px] text-charcoal-500 block">Community Member</span>
              </div>
            </div>

            <h3 className="font-heading font-bold text-base sm:text-lg text-teal-900 leading-snug">
              {post.title}
            </h3>

            <p className="text-charcoal-700 leading-relaxed whitespace-pre-wrap">
              {post.content}
            </p>

            {/* Reactions & Report row */}
            <div className="pt-2 flex items-center justify-between">
              <button
                type="button"
                onClick={() => onToggleReaction(post.id, 'heart')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs transition ${
                  post.has_reacted
                    ? 'bg-coral-50 text-coral-600 font-bold'
                    : 'bg-stone-50 text-charcoal-600 hover:bg-stone-100 hover:text-coral-600'
                }`}
              >
                <Heart className={`w-4 h-4 ${post.has_reacted ? 'fill-coral-500 text-coral-500' : ''}`} />
                <span>{post.upvotes_count} Support</span>
              </button>

              {onReportPost && post.user_id !== currentUserId && (
                <button
                  type="button"
                  onClick={() => onReportPost(post.id)}
                  className="text-charcoal-400 hover:text-coral-600 text-xs flex items-center gap-1 transition"
                >
                  <ShieldAlert className="w-3.5 h-3.5" />
                  <span>Report</span>
                </button>
              )}
            </div>
          </div>

          {/* Comments Section */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-xs font-bold text-teal-900">
              <MessageSquare className="w-4 h-4" />
              <span>Responses ({comments.length})</span>
            </div>

            {isLoadingComments ? (
              <div className="p-4 text-center text-charcoal-500 text-xs">Loading replies...</div>
            ) : comments.length === 0 ? (
              <div className="p-6 text-center text-charcoal-500 text-xs bg-stone-50 rounded-2xl border border-stone-100">
                No replies yet. Be the first to share your experience!
              </div>
            ) : (
              <div className="space-y-3">
                {comments.map((c) => {
                  const isCommentAuthor = currentUserId === c.user_id;
                  const cTimeStr = new Date(c.created_at).toLocaleDateString([], {
                    month: 'short',
                    day: 'numeric',
                  });

                  return (
                    <div
                      key={c.id}
                      className="p-3.5 bg-stone-50 rounded-2xl border border-stone-100 space-y-1.5"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <div className="w-6 h-6 rounded-full bg-teal-100 text-teal-900 flex items-center justify-center text-[10px] font-bold">
                            {c.author_alias.charAt(0).toUpperCase()}
                          </div>
                          <span className="font-bold text-xs text-charcoal-900">
                            {c.author_alias}
                          </span>
                          <span className="text-[10px] text-charcoal-500">• {cTimeStr}</span>
                        </div>

                        <div className="flex items-center gap-1">
                          {isCommentAuthor && (
                            <button
                              type="button"
                              onClick={() => {
                                if (window.confirm('Delete your reply?')) {
                                  onDeleteComment(c.id);
                                }
                              }}
                              className="p-1 text-charcoal-400 hover:text-coral-600 rounded transition"
                              aria-label="Delete comment"
                            >
                              <Trash2 className="w-3.5 h-3.5" />
                            </button>
                          )}
                          {!isCommentAuthor && onReportComment && (
                            <button
                              type="button"
                              onClick={() => onReportComment(c.id)}
                              className="p-1 text-charcoal-400 hover:text-coral-600 rounded transition"
                              title="Report comment"
                              aria-label="Report comment"
                            >
                              <ShieldAlert className="w-3 h-3" />
                            </button>
                          )}
                        </div>
                      </div>

                      <p className="text-xs text-charcoal-800 leading-relaxed whitespace-pre-wrap pl-8">
                        {c.content}
                      </p>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Comment Input Composer */}
        <form onSubmit={handleCommentSubmit} className="p-4 border-t border-stone-100 bg-white">
          <div className="flex items-center gap-2">
            <input
              type="text"
              required
              maxLength={3000}
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Share supportive advice or your experience..."
              disabled={isSubmitting}
              className="flex-1 p-2.5 bg-stone-50 border border-stone-200 rounded-2xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs text-charcoal-900"
            />
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={isSubmitting}
              disabled={!commentText.trim() || isSubmitting}
              rightIcon={<Send className="w-3.5 h-3.5" />}
            >
              Reply
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
