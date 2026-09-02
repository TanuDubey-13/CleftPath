import React from 'react';
import { MessageSquare, Heart, Edit2, Trash2, ShieldAlert } from 'lucide-react';
import { VillagePost } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface VillagePostCardProps {
  post: VillagePost;
  currentUserId?: string;
  onOpenPost: (postId: string) => void;
  onToggleReaction: (postId: string, reactionType: string) => void;
  onEditPost?: (post: VillagePost) => void;
  onDeletePost?: (postId: string) => void;
  onReportPost?: (postId: string) => void;
}

export const VillagePostCard: React.FC<VillagePostCardProps> = ({
  post,
  currentUserId,
  onOpenPost,
  onToggleReaction,
  onEditPost,
  onDeletePost,
  onReportPost,
}) => {
  const isAuthor = currentUserId === post.user_id;
  const timeStr = new Date(post.created_at).toLocaleDateString([], {
    month: 'short',
    day: 'numeric',
  });

  return (
    <Card className="p-4 sm:p-5 bg-white border border-stone-200/80 rounded-3xl hover:border-teal-700/30 hover:shadow-warm-sm transition space-y-3.5">
      {/* Top Author & Metadata Row */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-full bg-teal-100 text-teal-900 flex items-center justify-center text-xs font-bold shadow-warm-xs">
            {post.author_alias.charAt(0).toUpperCase()}
          </div>
          <div className="space-y-0.5">
            <span className="font-bold text-xs text-charcoal-900 block leading-none">
              {post.author_alias}
            </span>
            <span className="text-[10px] text-charcoal-600 block leading-none">
              {timeStr}
            </span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {post.channel_name && (
            <Badge variant="teal" size="sm">
              #{post.channel_name}
            </Badge>
          )}

          {/* Author or Moderation Actions */}
          {isAuthor && onEditPost && onDeletePost && (
            <div className="flex items-center gap-1">
              <button
                type="button"
                onClick={() => onEditPost(post)}
                className="p-1 rounded-lg text-charcoal-400 hover:text-teal-900 hover:bg-stone-100 transition"
                aria-label="Edit post"
              >
                <Edit2 className="w-3.5 h-3.5" />
              </button>
              <button
                type="button"
                onClick={() => {
                  if (window.confirm('Delete this community post?')) {
                    onDeletePost(post.id);
                  }
                }}
                className="p-1 rounded-lg text-charcoal-400 hover:text-coral-600 hover:bg-coral-50 transition"
                aria-label="Delete post"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          {!isAuthor && onReportPost && (
            <button
              type="button"
              onClick={() => onReportPost(post.id)}
              className="p-1 rounded-lg text-charcoal-400 hover:text-coral-600 hover:bg-coral-50 transition"
              title="Report post"
              aria-label="Report post"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>

      {/* Post Title & Plain-Text Body */}
      <div
        className="space-y-1.5 cursor-pointer group"
        onClick={() => onOpenPost(post.id)}
      >
        <h4 className="font-heading font-bold text-sm sm:text-base text-teal-900 group-hover:text-coral-600 transition leading-snug">
          {post.title}
        </h4>
        <p className="text-xs sm:text-sm text-charcoal-700 leading-relaxed line-clamp-3 whitespace-pre-wrap">
          {post.content}
        </p>
      </div>

      {/* Bottom Engagement Row */}
      <div className="pt-2 border-t border-stone-100 flex items-center justify-between text-xs text-charcoal-500">
        <div className="flex items-center gap-3">
          {/* Reaction Button (Heart) */}
          <button
            type="button"
            onClick={() => onToggleReaction(post.id, 'heart')}
            className={`flex items-center gap-1 px-2 py-1 rounded-xl transition ${
              post.has_reacted
                ? 'bg-coral-50 text-coral-600 font-bold'
                : 'hover:bg-stone-50 text-charcoal-600 hover:text-coral-600'
            }`}
          >
            <Heart className={`w-3.5 h-3.5 ${post.has_reacted ? 'fill-coral-500 text-coral-500' : ''}`} />
            <span>{post.upvotes_count} {post.upvotes_count === 1 ? 'Support' : 'Supports'}</span>
          </button>

          {/* Comments Count / Trigger */}
          <button
            type="button"
            onClick={() => onOpenPost(post.id)}
            className="flex items-center gap-1 px-2 py-1 rounded-xl hover:bg-stone-50 text-charcoal-600 hover:text-teal-900 transition"
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>{post.comments_count} {post.comments_count === 1 ? 'Reply' : 'Replies'}</span>
          </button>
        </div>

        <button
          type="button"
          onClick={() => onOpenPost(post.id)}
          className="text-xs font-bold text-teal-900 hover:text-coral-600 transition"
        >
          View Discussion →
        </button>
      </div>
    </Card>
  );
};
