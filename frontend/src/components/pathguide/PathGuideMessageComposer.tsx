import React, { useState, useRef, useEffect } from 'react';
import { Send } from 'lucide-react';
import { Button } from '../ui/Button';

interface PathGuideMessageComposerProps {
  onSendMessage: (content: string) => Promise<void>;
  isSending: boolean;
  placeholder?: string;
}

export const PathGuideMessageComposer: React.FC<PathGuideMessageComposerProps> = ({
  onSendMessage,
  isSending,
  placeholder = 'Ask PathGuide about surgical preparation, feeding, or appointments...',
}) => {
  const [content, setContent] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement | null>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 140)}px`;
    }
  }, [content]);

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    const trimmed = content.trim();
    if (!trimmed || isSending) return;

    try {
      setContent('');
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
      await onSendMessage(trimmed);
    } catch (err) {
      // Re-fill on error so user doesn't lose input
      setContent(trimmed);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative bg-white border border-stone-200/90 rounded-3xl p-2.5 shadow-warm-sm focus-within:border-teal-700/50 focus-within:ring-2 focus-within:ring-teal-700/10 transition">
      <div className="flex items-end gap-2">
        <textarea
          ref={textareaRef}
          rows={1}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          maxLength={4000}
          disabled={isSending}
          className="flex-1 bg-transparent border-none outline-none resize-none px-3 py-2 text-xs sm:text-sm text-charcoal-900 placeholder:text-charcoal-400 max-h-36 min-h-[38px] leading-relaxed"
        />

        <div className="flex items-center gap-2 pb-1 pr-1">
          <Button
            type="submit"
            variant="primary"
            size="sm"
            isLoading={isSending}
            disabled={!content.trim() || isSending}
            aria-label="Send message"
            className="rounded-2xl"
            rightIcon={<Send className="w-3.5 h-3.5" />}
          >
            Send
          </Button>
        </div>
      </div>
    </form>
  );
};
