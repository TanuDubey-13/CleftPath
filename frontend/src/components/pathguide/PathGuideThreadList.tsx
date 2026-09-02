import React from 'react';
import { MessageSquare, Plus, Trash2, Clock } from 'lucide-react';
import { PathGuideThread } from '../../types';
import { Button } from '../ui/Button';

interface PathGuideThreadListProps {
  threads: PathGuideThread[];
  activeThreadId?: string | null;
  onSelectThread: (threadId: string) => void;
  onNewThread: () => void;
  onDeleteThread: (threadId: string) => void;
  isLoading?: boolean;
}

export const PathGuideThreadList: React.FC<PathGuideThreadListProps> = ({
  threads,
  activeThreadId,
  onSelectThread,
  onNewThread,
  onDeleteThread,
  isLoading = false,
}) => {
  return (
    <div className="flex flex-col h-full bg-white border border-stone-200/80 rounded-3xl p-4 shadow-warm-xs space-y-3">
      {/* Header */}
      <div className="flex items-center justify-between pb-2 border-b border-stone-100">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
            <MessageSquare className="w-4 h-4" />
          </div>
          <span className="font-heading font-bold text-sm text-teal-900">
            Conversations
          </span>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={onNewThread}
          leftIcon={<Plus className="w-3.5 h-3.5" />}
        >
          New Chat
        </Button>
      </div>

      {/* Threads Scroll List */}
      <div className="flex-1 overflow-y-auto space-y-1.5 pr-1 text-xs">
        {isLoading ? (
          <div className="p-4 text-center text-charcoal-600 text-xs">Loading conversations...</div>
        ) : threads.length === 0 ? (
          <div className="p-6 text-center text-charcoal-600 space-y-2">
            <p>No conversations yet.</p>
            <Button variant="ghost" size="sm" onClick={onNewThread}>
              Start a new conversation
            </Button>
          </div>
        ) : (
          threads.map((t) => {
            const isActive = t.id === activeThreadId;
            const updatedDate = new Date(t.updated_at).toLocaleDateString([], {
              month: 'short',
              day: 'numeric',
            });

            return (
              <div
                key={t.id}
                onClick={() => onSelectThread(t.id)}
                className={`group p-3 rounded-2xl cursor-pointer transition flex items-start justify-between gap-2 border ${
                  isActive
                    ? 'bg-teal-900 text-white border-teal-900 shadow-warm-xs'
                    : 'bg-white hover:bg-stone-50 text-charcoal-900 border-stone-100 hover:border-stone-200'
                }`}
              >
                <div className="space-y-1 flex-1 min-w-0">
                  <h4 className={`font-bold text-xs truncate ${isActive ? 'text-white' : 'text-teal-900'}`}>
                    {t.title}
                  </h4>
                  <div className="flex items-center gap-2 text-[10px]">
                    <span className={`flex items-center gap-1 ${isActive ? 'text-teal-200' : 'text-charcoal-600'}`}>
                      <Clock className="w-3 h-3" />
                      {updatedDate}
                    </span>
                    <span className={isActive ? 'text-teal-300' : 'text-charcoal-600'}>
                      • {t.message_count} {t.message_count === 1 ? 'msg' : 'msgs'}
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm('Delete this conversation thread?')) {
                      onDeleteThread(t.id);
                    }
                  }}
                  className={`opacity-0 group-hover:opacity-100 p-1.5 rounded-lg transition ${
                    isActive
                      ? 'text-teal-300 hover:text-white hover:bg-teal-800'
                      : 'text-charcoal-400 hover:text-coral-600 hover:bg-coral-50'
                  }`}
                  aria-label="Delete thread"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
