import React from 'react';
import { X, BookOpen, ExternalLink, ShieldCheck } from 'lucide-react';
import { Link } from 'react-router-dom';
import { PathGuideCitation } from '../../types';
import { Button } from '../ui/Button';

interface PathGuideSourceModalProps {
  citation: PathGuideCitation | null;
  isOpen: boolean;
  onClose: () => void;
}

export const PathGuideSourceModal: React.FC<PathGuideSourceModalProps> = ({
  citation,
  isOpen,
  onClose,
}) => {
  if (!isOpen || !citation) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 bg-charcoal-900/50 backdrop-blur-sm animate-fade-in"
      onClick={onClose}
    >
      <div
        className="bg-white w-full max-w-lg rounded-3xl shadow-warm-lg border border-stone-200 overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-5 border-b border-stone-100 flex items-center justify-between bg-ivory-50/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-xl bg-teal-50 text-teal-900 flex items-center justify-center">
              <BookOpen className="w-4 h-4" />
            </div>
            <div>
              <span className="text-[10px] font-bold text-teal-800 uppercase tracking-wider">
                {citation.category}
              </span>
              <h3 className="font-heading font-bold text-base text-teal-900 leading-snug">
                {citation.title}
              </h3>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-charcoal-400 hover:text-charcoal-800 hover:bg-stone-100 transition"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Body */}
        <div className="p-5 space-y-4 overflow-y-auto flex-1 text-xs">
          <div>
            <span className="block font-bold text-charcoal-700 mb-1">
              Source Overview / Summary:
            </span>
            <p className="text-charcoal-700 bg-stone-50 p-3.5 rounded-2xl border border-stone-100 leading-relaxed">
              {citation.summary || 'Verified educational article from the CleftPath Health Library.'}
            </p>
          </div>

          <div className="p-3 bg-teal-50/40 rounded-2xl border border-teal-100 flex items-start gap-2 text-[11px] text-charcoal-600">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-900 flex-shrink-0 mt-0.5" />
            <span>
              This educational material is grounded in cleft care guidelines. It does not replace clinical instructions from your surgical, pediatric, or SLP team.
            </span>
          </div>

          {/* Actions */}
          <div className="pt-3 border-t border-stone-100 flex items-center justify-between">
            {citation.slug ? (
              <Link
                to={`/health-library/${citation.slug}`}
                onClick={onClose}
                className="text-xs font-bold text-teal-900 hover:text-coral-600 flex items-center gap-1 transition"
              >
                <span>Read Full Article in Library</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </Link>
            ) : (
              <div />
            )}

            <Button variant="outline" size="sm" onClick={onClose}>
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
