import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import { PathGuidePage } from './PathGuidePage';
import * as pathguideHooks from '../hooks/usePathGuide';

vi.mock('../hooks/usePathGuide');

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  });

const renderWithProviders = (ui: React.ReactElement) => {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('PathGuidePage Component', () => {
  const mockThreads = {
    items: [
      {
        id: 'thread-1',
        user_id: 'user-1',
        title: 'Bottle Preparation Questions',
        created_at: '2026-09-02T10:00:00Z',
        updated_at: '2026-09-02T10:00:00Z',
        message_count: 2,
      },
    ],
    total: 1,
    page: 1,
    page_size: 20,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  };

  const mockMessages = {
    items: [
      {
        id: 'msg-1',
        thread_id: 'thread-1',
        role: 'user',
        content: 'How do I clean the Haberman valve?',
        citations: [],
        safety_flags: {},
        tokens_used: 0,
        created_at: '2026-09-02T10:00:00Z',
      },
      {
        id: 'msg-2',
        thread_id: 'thread-1',
        role: 'assistant',
        content: 'To clean the Haberman valve, wash with warm soapy water.',
        citations: [
          {
            article_id: 'art-1',
            title: 'Cleaning Specialized Feeders',
            category: 'Feeding & Nutrition',
            slug: 'cleaning-feeders',
          },
        ],
        safety_flags: { emergency_trigger_detected: false },
        tokens_used: 120,
        created_at: '2026-09-02T10:01:00Z',
      },
    ],
    total: 2,
    page: 1,
    page_size: 50,
    total_pages: 1,
    has_next: false,
    has_prev: false,
  };

  const mockPrompts = {
    prompts: [
      {
        id: 'sp_1',
        category: 'Feeding & Bottles',
        prompt: 'How do specialized cleft feeders work?',
        description: 'Understand unidirectional valves.',
      },
    ],
  };

  beforeEach(() => {
    vi.mocked(pathguideHooks.usePathGuideThreads).mockReturnValue({
      data: mockThreads,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(pathguideHooks.usePathGuideThread).mockReturnValue({
      data: mockThreads.items[0],
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(pathguideHooks.usePathGuideMessages).mockReturnValue({
      data: mockMessages,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(pathguideHooks.usePathGuideSuggestedPrompts).mockReturnValue({
      data: mockPrompts,
      isLoading: false,
      error: null,
    } as any);

    vi.mocked(pathguideHooks.useCreatePathGuideThread).mockReturnValue({
      mutateAsync: vi.fn().mockResolvedValue({ id: 'thread-2', title: 'Care Conversation' }),
      isPending: false,
    } as any);

    vi.mocked(pathguideHooks.useDeletePathGuideThread).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);

    vi.mocked(pathguideHooks.useSendMessage).mockReturnValue({
      mutateAsync: vi.fn(),
      isPending: false,
    } as any);
  });

  it('renders sidebar thread list and conversation messages', () => {
    renderWithProviders(<PathGuidePage />);

    expect(screen.getAllByText('Bottle Preparation Questions').length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText('How do I clean the Haberman valve?')).toBeInTheDocument();
    expect(screen.getByText('To clean the Haberman valve, wash with warm soapy water.')).toBeInTheDocument();
    expect(screen.getByText('Cleaning Specialized Feeders')).toBeInTheDocument();
  });

  it('renders safety notice at top of conversation', () => {
    renderWithProviders(<PathGuidePage />);

    expect(screen.getByText(/Educational Care Companion Notice/i)).toBeInTheDocument();
  });

  it('triggers send message on input submission', async () => {
    const mockSend = vi.fn().mockResolvedValue({});
    vi.mocked(pathguideHooks.useSendMessage).mockReturnValue({
      mutateAsync: mockSend,
      isPending: false,
    } as any);

    renderWithProviders(<PathGuidePage />);

    const input = screen.getByPlaceholderText(/Ask PathGuide about surgical preparation/i);
    fireEvent.change(input, { target: { value: 'What are post-op instructions?' } });

    const sendBtn = screen.getByRole('button', { name: /send message/i });
    fireEvent.click(sendBtn);

    expect(mockSend).toHaveBeenCalledWith({
      threadId: 'thread-1',
      payload: { content: 'What are post-op instructions?' },
    });
  });
});
