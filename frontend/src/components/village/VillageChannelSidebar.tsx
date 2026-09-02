import React from 'react';
import { Hash, Layers } from 'lucide-react';
import { VillageChannel } from '../../types';

interface VillageChannelSidebarProps {
  channels: VillageChannel[];
  selectedChannelId: string | null;
  onSelectChannel: (channelId: string | null) => void;
  isLoading?: boolean;
}

export const VillageChannelSidebar: React.FC<VillageChannelSidebarProps> = ({
  channels,
  selectedChannelId,
  onSelectChannel,
  isLoading = false,
}) => {
  return (
    <div className="bg-white rounded-3xl border border-stone-200/80 p-4 shadow-warm-xs space-y-3">
      <div className="flex items-center gap-2 pb-2 border-b border-stone-100">
        <div className="w-7 h-7 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
          <Layers className="w-4 h-4" />
        </div>
        <span className="font-heading font-bold text-sm text-teal-900">
          Community Channels
        </span>
      </div>

      <div className="space-y-1">
        {/* All Channels option */}
        <button
          type="button"
          onClick={() => onSelectChannel(null)}
          className={`w-full text-left px-3 py-2 rounded-2xl text-xs font-semibold transition flex items-center justify-between ${
            selectedChannelId === null
              ? 'bg-teal-900 text-white shadow-warm-xs'
              : 'text-charcoal-700 hover:bg-stone-50'
          }`}
        >
          <div className="flex items-center gap-2">
            <Hash className="w-3.5 h-3.5" />
            <span>All Channels</span>
          </div>
        </button>

        {/* Channel list */}
        {isLoading ? (
          <div className="p-3 text-center text-charcoal-600 text-xs">Loading channels...</div>
        ) : (
          channels.map((ch) => {
            const isSelected = ch.id === selectedChannelId;
            return (
              <button
                key={ch.id}
                type="button"
                onClick={() => onSelectChannel(ch.id)}
                className={`w-full text-left px-3 py-2 rounded-2xl text-xs font-semibold transition flex items-center justify-between ${
                  isSelected
                    ? 'bg-teal-900 text-white shadow-warm-xs'
                    : 'text-charcoal-700 hover:bg-stone-50'
                }`}
              >
                <div className="flex items-center gap-2 truncate">
                  <Hash className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate">{ch.name}</span>
                </div>
                {ch.posts_count > 0 && (
                  <span
                    className={`text-[10px] px-1.5 py-0.5 rounded-full font-bold ${
                      isSelected
                        ? 'bg-teal-800 text-teal-100'
                        : 'bg-stone-100 text-charcoal-600'
                    }`}
                  >
                    {ch.posts_count}
                  </span>
                )}
              </button>
            );
          })
        )}
      </div>
    </div>
  );
};
