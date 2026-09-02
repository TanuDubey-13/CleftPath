import React, { useState, useEffect } from 'react';
import { X, Send } from 'lucide-react';
import { VillageChannel, VillagePost } from '../../types';
import { Button } from '../ui/Button';

interface VillagePostComposerModalProps {
  isOpen: boolean;
  channels: VillageChannel[];
  selectedChannelId?: string | null;
  editingPost?: VillagePost | null;
  onClose: () => void;
  onSubmitPost: (data: {
    channel_id: string;
    title: string;
    content: string;
    author_alias?: string;
  }) => Promise<void>;
  isSubmitting?: boolean;
}

export const VillagePostComposerModal: React.FC<VillagePostComposerModalProps> = ({
  isOpen,
  channels,
  selectedChannelId,
  editingPost,
  onClose,
  onSubmitPost,
  isSubmitting = false,
}) => {
  const [channelId, setChannelId] = useState('');
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [authorAlias, setAuthorAlias] = useState('');

  useEffect(() => {
    if (editingPost) {
      setChannelId(editingPost.channel_id);
      setTitle(editingPost.title);
      setContent(editingPost.content);
      setAuthorAlias(editingPost.author_alias);
    } else {
      setChannelId(selectedChannelId || (channels[0]?.id ?? ''));
      setTitle('');
      setContent('');
      setAuthorAlias('');
    }
  }, [editingPost, selectedChannelId, channels, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim() || !content.trim() || !channelId) return;

    await onSubmitPost({
      channel_id: channelId,
      title: title.trim(),
      content: content.trim(),
      author_alias: authorAlias.trim() || undefined,
    });
    onClose();
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fadeIn"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-lg rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <h3 className="font-heading font-bold text-base text-teal-900">
            {editingPost ? 'Edit Community Post' : 'New Community Post'}
          </h3>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-5 space-y-4 text-xs">
          {/* Channel selector */}
          {!editingPost && (
            <div className="space-y-1">
              <label className="block font-bold text-charcoal-800">Choose Channel</label>
              <select
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                required
                className="w-full p-2.5 bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs text-charcoal-900"
              >
                {channels.map((ch) => (
                  <option key={ch.id} value={ch.id}>
                    #{ch.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Title */}
          <div className="space-y-1">
            <label className="block font-bold text-charcoal-800">Post Title</label>
            <input
              type="text"
              required
              minLength={3}
              maxLength={255}
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="e.g. Tips for keeping arm restraints comfortable?"
              className="w-full p-2.5 bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs text-charcoal-900"
            />
          </div>

          {/* Content */}
          <div className="space-y-1">
            <label className="block font-bold text-charcoal-800">Content / Question</label>
            <textarea
              required
              rows={5}
              minLength={5}
              maxLength={10000}
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="Share your practical experience, preparation questions, or family journey tips..."
              className="w-full p-2.5 bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs text-charcoal-900 leading-relaxed"
            />
          </div>

          {/* Display Alias */}
          <div className="space-y-1">
            <label className="block font-bold text-charcoal-800">
              Display Alias <span className="font-normal text-charcoal-500">(Optional)</span>
            </label>
            <input
              type="text"
              maxLength={100}
              value={authorAlias}
              onChange={(e) => setAuthorAlias(e.target.value)}
              placeholder="e.g. CleftMom_Sarah (defaults to your name)"
              className="w-full p-2.5 bg-stone-50 border border-stone-200 rounded-xl outline-none focus:border-teal-700 focus:ring-1 focus:ring-teal-700 text-xs text-charcoal-900"
            />
          </div>

          <div className="p-3 bg-teal-50/50 border border-teal-100 rounded-xl text-[11px] text-charcoal-600">
            Remember: Personal experiences are valued, but are not professional medical advice.
          </div>

          {/* Actions */}
          <div className="pt-2 border-t border-stone-100 flex items-center justify-end gap-2">
            <Button type="button" variant="outline" size="sm" onClick={onClose} disabled={isSubmitting}>
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              isLoading={isSubmitting}
              disabled={!title.trim() || !content.trim() || isSubmitting}
              rightIcon={<Send className="w-3.5 h-3.5" />}
            >
              {editingPost ? 'Update Post' : 'Publish Post'}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};
