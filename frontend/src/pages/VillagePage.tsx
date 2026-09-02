import React from 'react';
import { MessageSquare, Heart, Plus } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

export const VillagePage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">The Village</h1>
          <p className="text-sm text-charcoal-600">
            A safe, moderated peer community for parents and individuals navigating cleft journeys.
          </p>
        </div>
        <Button variant="primary" size="md" leftIcon={<Plus className="w-4 h-4" />}>
          New Community Post
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Channel List */}
        <div className="space-y-2">
          <h3 className="text-xs font-bold uppercase tracking-wider text-charcoal-500 px-1">Stage Channels</h3>
          <div className="bg-white rounded-2xl border border-stone-200 p-2 space-y-1">
            <button className="w-full text-left px-3 py-2 rounded-xl text-xs font-bold text-teal-900 bg-teal-50">
              #stage-2-lip-repair
            </button>
            <button className="w-full text-left px-3 py-2 rounded-xl text-xs font-medium text-charcoal-600 hover:bg-stone-50">
              #first-year-feeding
            </button>
            <button className="w-full text-left px-3 py-2 rounded-xl text-xs font-medium text-charcoal-600 hover:bg-stone-50">
              #expectant-parents
            </button>
            <button className="w-full text-left px-3 py-2 rounded-xl text-xs font-medium text-charcoal-600 hover:bg-stone-50">
              #speech-and-school
            </button>
          </div>
        </div>

        {/* Community Feed */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-full bg-teal-100 text-teal-900 flex items-center justify-center text-xs font-bold">
                  S
                </div>
                <span className="text-xs font-bold text-charcoal-900">ParentSarah42</span>
                <span className="text-[11px] text-charcoal-500">• 2 hours ago</span>
              </div>
              <Badge variant="teal" size="sm">#stage-2-lip-repair</Badge>
            </div>
            <h4 className="font-bold text-base text-charcoal-900">
              Tips for keeping soft arm restraints (No-Nos) comfortable during sleep?
            </h4>
            <p className="text-xs sm:text-sm text-charcoal-700 leading-relaxed">
              We are getting ready for Leo’s lip repair in 4 weeks. Any advice from parents who have gone through this on making sleep more comfortable with arm restraints?
            </p>
            <div className="pt-2 border-t border-stone-100 flex items-center gap-4 text-xs text-charcoal-500">
              <span className="flex items-center gap-1.5 hover:text-coral-600 cursor-pointer">
                <Heart className="w-4 h-4" /> 18 Hugs & Hearts
              </span>
              <span className="flex items-center gap-1.5 hover:text-teal-900 cursor-pointer">
                <MessageSquare className="w-4 h-4" /> 14 Responses
              </span>
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
};
