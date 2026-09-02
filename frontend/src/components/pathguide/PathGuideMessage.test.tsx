import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { PathGuideMessage } from './PathGuideMessage';
import { PathGuideMessage as IPathGuideMessage } from '../../types';

const mockAssistantMessage: IPathGuideMessage = {
  id: 'msg-1',
  thread_id: 'thread-1',
  role: 'assistant',
  content: 'Here is an explanation of specialized cleft feeders.',
  citations: [
    {
      article_id: 'art-1',
      title: 'Understanding Specialized Cleft Feeders',
      category: 'Feeding & Nutrition',
      slug: 'specialized-feeders',
      summary: 'Comparison of unidirectional valves.',
    },
  ],
  safety_flags: { emergency_trigger_detected: false },
  tokens_used: 120,
  created_at: '2026-09-02T10:00:00Z',
};

const mockUserMessage: IPathGuideMessage = {
  id: 'msg-2',
  thread_id: 'thread-1',
  role: 'user',
  content: 'How does the Haberman feeder work?',
  citations: [],
  safety_flags: {},
  tokens_used: 0,
  created_at: '2026-09-02T09:59:00Z',
};

describe('PathGuideMessage Component', () => {
  it('renders user message properly', () => {
    render(
      <PathGuideMessage
        message={mockUserMessage}
        onSelectCitation={vi.fn()}
      />
    );

    expect(screen.getByText('How does the Haberman feeder work?')).toBeInTheDocument();
  });

  it('renders assistant message with citation badges', () => {
    const handleSelectCitation = vi.fn();
    render(
      <PathGuideMessage
        message={mockAssistantMessage}
        onSelectCitation={handleSelectCitation}
      />
    );

    expect(screen.getByText('Here is an explanation of specialized cleft feeders.')).toBeInTheDocument();
    expect(screen.getByText('Understanding Specialized Cleft Feeders')).toBeInTheDocument();

    fireEvent.click(screen.getByText('Understanding Specialized Cleft Feeders'));
    expect(handleSelectCitation).toHaveBeenCalledWith(mockAssistantMessage.citations[0]);
  });

  it('renders emergency triage note if flagged in assistant message', () => {
    const emergencyMsg: IPathGuideMessage = {
      ...mockAssistantMessage,
      safety_flags: { emergency_trigger_detected: true },
    };

    render(
      <PathGuideMessage
        message={emergencyMsg}
        onSelectCitation={vi.fn()}
      />
    );

    expect(screen.getByText(/Urgent symptom note/i)).toBeInTheDocument();
  });
});
