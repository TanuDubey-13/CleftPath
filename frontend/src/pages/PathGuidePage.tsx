import React, { useState } from 'react';
import { Sparkles, Send, ShieldCheck } from 'lucide-react';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const PathGuidePage: React.FC = () => {
  const [messages, setMessages] = useState([
    {
      id: 1,
      role: 'assistant',
      content:
        'Hello Sarah! I am PathGuide, your AI care companion for CleftPath. I can help organize questions for Dr. Sterling, explain feeding bottle techniques, and guide you through upcoming milestones for Baby Leo.',
      citations: ['ACPA Family Guidelines 2024'],
    },
  ]);
  const [inputValue, setInputValue] = useState('');

  const handleSend = () => {
    if (!inputValue.trim()) return;
    const userMsg = { id: Date.now(), role: 'user', content: inputValue, citations: [] };
    setMessages((prev) => [
      ...prev,
      userMsg,
      {
        id: Date.now() + 1,
        role: 'assistant',
        content:
          'Thank you for your question. When preparing for primary lip repair at 3–6 months, families typically coordinate pre-op bloodwork and ensure specialized bottles are packed. Please note that I am an AI assistant and do not provide medical diagnoses or prescriptions.',
        citations: ['ACPA Primary Cheiloplasty Care Pathway, p. 12'],
      },
    ]);
    setInputValue('');
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto animate-fadeIn flex flex-col h-[calc(100vh-12rem)]">
      {/* Header Banner */}
      <div className="flex items-center justify-between pb-3 border-b border-stone-200">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl bg-teal-900 text-white flex items-center justify-center shadow-warm-sm">
            <Sparkles className="w-5 h-5 text-coral-400" />
          </div>
          <div>
            <h1 className="font-heading font-bold text-xl text-teal-900">PathGuide AI</h1>
            <p className="text-xs text-charcoal-600">Grounded in verified ACPA clinical resources</p>
          </div>
        </div>
        <Badge variant="sage" size="sm">
          <ShieldCheck className="w-3.5 h-3.5" /> Non-Diagnostic Guide
        </Badge>
      </div>

      {/* Chat Messages Area */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-2">
        {messages.map((m) => (
          <div
            key={m.id}
            className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
          >
            <div
              className={`max-w-xl rounded-2xl p-4 text-xs sm:text-sm leading-relaxed shadow-warm-sm ${
                m.role === 'user'
                  ? 'bg-teal-900 text-white rounded-br-none'
                  : 'bg-white border border-stone-200/90 text-charcoal-900 rounded-bl-none'
              }`}
            >
              {m.content}

              {m.citations && m.citations.length > 0 && (
                <div className="mt-2.5 pt-2 border-t border-stone-100 flex flex-wrap gap-1.5">
                  {m.citations.map((c, i) => (
                    <span
                      key={i}
                      className="text-[10px] font-semibold text-teal-900 bg-teal-50 px-2 py-0.5 rounded-md"
                    >
                      Source: {c}
                    </span>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Input Bar */}
      <div className="pt-2 border-t border-stone-200/80">
        <div className="flex gap-2">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask PathGuide about surgical preparation, feeding, or appointments..."
            className="flex-1 bg-white border border-stone-200 rounded-xl px-4 py-3 text-xs sm:text-sm text-charcoal-900 focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
          />
          <Button
            variant="primary"
            size="md"
            onClick={handleSend}
            rightIcon={<Send className="w-4 h-4" />}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
};
