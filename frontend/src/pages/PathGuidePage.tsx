import React, { useState, useEffect, useRef } from 'react';
import { Sparkles, MessageSquare, ChevronLeft } from 'lucide-react';
import { PathGuideCitation } from '../types';
import {
  useCreatePathGuideThread,
  useDeletePathGuideThread,
  usePathGuideMessages,
  usePathGuideSuggestedPrompts,
  usePathGuideThread,
  usePathGuideThreads,
  useSendMessage,
} from '../hooks/usePathGuide';
import { PathGuideSafetyNotice } from '../components/pathguide/PathGuideSafetyNotice';
import { PathGuideThreadList } from '../components/pathguide/PathGuideThreadList';
import { PathGuideMessage } from '../components/pathguide/PathGuideMessage';
import { PathGuideMessageComposer } from '../components/pathguide/PathGuideMessageComposer';
import { PathGuideEmptyState } from '../components/pathguide/PathGuideEmptyState';
import { PathGuideSourceModal } from '../components/pathguide/PathGuideSourceModal';
import { PathGuideSkeleton } from '../components/pathguide/PathGuideSkeleton';
import { Button } from '../components/ui/Button';

export const PathGuidePage: React.FC = () => {
  const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
  const [selectedCitation, setSelectedCitation] = useState<PathGuideCitation | null>(null);
  const [showMobileSidebar, setShowMobileSidebar] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Queries
  const { data: threadsData, isLoading: isThreadsLoading } = usePathGuideThreads(1, 30);
  const { data: activeThread } = usePathGuideThread(activeThreadId || undefined);
  const { data: messagesData, isLoading: isMessagesLoading } = usePathGuideMessages(
    activeThreadId || undefined,
    1,
    100
  );
  const { data: suggestedPromptsData } = usePathGuideSuggestedPrompts();

  // Mutations
  const createThreadMutation = useCreatePathGuideThread();
  const deleteThreadMutation = useDeletePathGuideThread();
  const sendMessageMutation = useSendMessage();

  // Auto-select first thread if available and none selected
  useEffect(() => {
    if (!activeThreadId && threadsData?.items && threadsData.items.length > 0) {
      setActiveThreadId(threadsData.items[0].id);
    }
  }, [threadsData, activeThreadId]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messagesData?.items, sendMessageMutation.isPending]);

  const handleNewThread = async () => {
    const newThread = await createThreadMutation.mutateAsync({
      title: 'Care Conversation',
    });
    setActiveThreadId(newThread.id);
    setShowMobileSidebar(false);
  };

  const handleDeleteThread = async (threadId: string) => {
    await deleteThreadMutation.mutateAsync(threadId);
    if (activeThreadId === threadId) {
      setActiveThreadId(null);
    }
  };

  const handleSendMessage = async (content: string) => {
    let currentId = activeThreadId;

    // Create a new thread if none exists
    if (!currentId) {
      const newThread = await createThreadMutation.mutateAsync({
        title: (content.slice(0, 40) + '...') || 'Care Conversation',
      });
      currentId = newThread.id;
      setActiveThreadId(newThread.id);
    }

    await sendMessageMutation.mutateAsync({
      threadId: currentId,
      payload: { content },
    });
  };

  if (isThreadsLoading && !threadsData) {
    return <PathGuideSkeleton />;
  }

  const messages = messagesData?.items || [];
  const prompts = suggestedPromptsData?.prompts || [];
  const lastMessage = messages[messages.length - 1];
  const hasEmergency = lastMessage?.safety_flags?.emergency_trigger_detected;

  return (
    <div className="space-y-4 animate-fadeIn max-w-7xl mx-auto h-[calc(100vh-8.5rem)] flex flex-col">
      {/* Top Bar on Mobile for Thread Selection */}
      <div className="flex md:hidden items-center justify-between bg-white p-3 rounded-2xl border border-stone-200">
        <button
          type="button"
          onClick={() => setShowMobileSidebar(!showMobileSidebar)}
          className="text-xs font-bold text-teal-900 flex items-center gap-1"
        >
          <MessageSquare className="w-4 h-4" />
          <span>{activeThread ? activeThread.title : 'Select Conversation'}</span>
        </button>
        <Button variant="outline" size="sm" onClick={handleNewThread}>
          New Chat
        </Button>
      </div>

      {/* Main Two-Panel Layout */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 flex-1 min-h-0">
        {/* Left Sidebar: Threads */}
        <div
          className={`${
            showMobileSidebar ? 'fixed inset-0 z-40 bg-white p-4 m-4 rounded-3xl shadow-warm-lg' : 'hidden'
          } md:block md:relative md:inset-auto md:z-0 md:m-0 md:p-0 md:col-span-1 h-full`}
        >
          {showMobileSidebar && (
            <div className="flex justify-end pb-2 md:hidden">
              <Button variant="ghost" size="sm" onClick={() => setShowMobileSidebar(false)}>
                <ChevronLeft className="w-4 h-4 mr-1" /> Back to Chat
              </Button>
            </div>
          )}
          <PathGuideThreadList
            threads={threadsData?.items || []}
            activeThreadId={activeThreadId}
            onSelectThread={(id) => {
              setActiveThreadId(id);
              setShowMobileSidebar(false);
            }}
            onNewThread={handleNewThread}
            onDeleteThread={handleDeleteThread}
            isLoading={isThreadsLoading}
          />
        </div>

        {/* Right Panel: Conversation Area */}
        <div className="md:col-span-3 bg-white border border-stone-200/80 rounded-3xl p-4 sm:p-6 shadow-warm-xs flex flex-col justify-between h-full min-h-0 space-y-4">
          {/* Top Safety Banner */}
          <PathGuideSafetyNotice hasEmergencyTrigger={hasEmergency} />

          {/* Messages Stream */}
          <div className="flex-1 overflow-y-auto pr-2 space-y-4 min-h-0">
            {isMessagesLoading && messages.length === 0 ? (
              <div className="p-8 text-center text-charcoal-600 text-xs">
                Loading messages...
              </div>
            ) : messages.length === 0 ? (
              <PathGuideEmptyState
                prompts={prompts}
                onSelectPrompt={(text) => handleSendMessage(text)}
              />
            ) : (
              messages.map((m) => (
                <PathGuideMessage
                  key={m.id}
                  message={m}
                  onSelectCitation={(cit) => setSelectedCitation(cit)}
                />
              ))
            )}

            {/* In-Flight Sending Indicator */}
            {sendMessageMutation.isPending && (
              <div className="flex items-start gap-2.5 animate-fadeIn">
                <div className="w-8 h-8 rounded-xl bg-coral-500 text-white flex items-center justify-center shadow-warm-xs">
                  <Sparkles className="w-4 h-4 animate-spin" />
                </div>
                <div className="bg-ivory-50 border border-stone-200 rounded-3xl rounded-tl-none p-4 text-xs text-charcoal-600 flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-teal-900 animate-pulse" />
                  <span>Searching Health Library & formulating grounded explanation...</span>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Composer Input Bar */}
          <div className="pt-2 border-t border-stone-100">
            <PathGuideMessageComposer
              onSendMessage={handleSendMessage}
              isSending={sendMessageMutation.isPending}
            />
          </div>
        </div>
      </div>

      {/* Cited Source Modal */}
      <PathGuideSourceModal
        citation={selectedCitation}
        isOpen={!!selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />
    </div>
  );
};
