import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { VillagePostCard } from './VillagePostCard';
import { VillagePost } from '../../types';

const mockPost: VillagePost = {
  id: 'post-1',
  channel_id: 'ch-1',
  channel_name: 'Surgery Prep & Recovery',
  channel_slug: 'surgery-prep',
  user_id: 'user-1',
  author_alias: 'Parent Sarah',
  author_avatar_seed: 'avatar1',
  title: 'Tips for keeping soft arm restraints comfortable?',
  content: 'We are getting ready for lip repair. Any tips on making sleep more comfortable with arm restraints?',
  status: 'published',
  is_flagged: false,
  upvotes_count: 5,
  comments_count: 2,
  has_reacted: false,
  created_at: '2026-09-02T10:00:00Z',
  updated_at: '2026-09-02T10:00:00Z',
};

describe('VillagePostCard Component', () => {
  it('renders post title, author alias, channel name, and body safely', () => {
    render(
      <VillagePostCard
        post={mockPost}
        currentUserId="other-user"
        onOpenPost={vi.fn()}
        onToggleReaction={vi.fn()}
      />
    );

    expect(screen.getByText('Tips for keeping soft arm restraints comfortable?')).toBeInTheDocument();
    expect(screen.getByText('Parent Sarah')).toBeInTheDocument();
    expect(screen.getByText('#Surgery Prep & Recovery')).toBeInTheDocument();
    expect(screen.getByText(/We are getting ready for lip repair/i)).toBeInTheDocument();
  });

  it('triggers reaction toggle on click', () => {
    const handleToggleReaction = vi.fn();
    render(
      <VillagePostCard
        post={mockPost}
        currentUserId="other-user"
        onOpenPost={vi.fn()}
        onToggleReaction={handleToggleReaction}
      />
    );

    const reactionBtn = screen.getByText(/5 Supports/i);
    fireEvent.click(reactionBtn);

    expect(handleToggleReaction).toHaveBeenCalledWith('post-1', 'heart');
  });

  it('shows edit and delete buttons when current user is the author', () => {
    const handleEdit = vi.fn();
    const handleDelete = vi.fn();

    render(
      <VillagePostCard
        post={mockPost}
        currentUserId="user-1" // Author
        onOpenPost={vi.fn()}
        onToggleReaction={vi.fn()}
        onEditPost={handleEdit}
        onDeletePost={handleDelete}
      />
    );

    expect(screen.getByLabelText('Edit post')).toBeInTheDocument();
    expect(screen.getByLabelText('Delete post')).toBeInTheDocument();

    fireEvent.click(screen.getByLabelText('Edit post'));
    expect(handleEdit).toHaveBeenCalledWith(mockPost);
  });
});
