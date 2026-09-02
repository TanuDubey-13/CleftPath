import React from 'react';
import { Clock, CheckCircle2, ChevronRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { HealthArticleCard as HealthArticleCardType } from '../../types';
import { Card } from '../ui/Card';
import { Badge } from '../ui/Badge';

interface HealthArticleCardProps {
  article: HealthArticleCardType;
}

export const HealthArticleCard: React.FC<HealthArticleCardProps> = ({ article }) => {
  return (
    <Link
      to={`/health-library/${article.slug || article.id}`}
      className="group block focus:outline-none focus-visible:ring-2 focus-visible:ring-teal-700/50 rounded-3xl"
    >
      <Card
        className="h-full p-5 sm:p-6 bg-white border border-stone-200/80 rounded-3xl transition-all duration-200 group-hover:border-teal-700/40 group-hover:shadow-warm-md flex flex-col justify-between gap-4"
      >
        <div className="space-y-3">
          {/* Badges: Category & Stage */}
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="teal" size="sm">
              {article.category}
            </Badge>
            {article.stage_title && (
              <Badge variant="stone" size="sm">
                {article.stage_title}
              </Badge>
            )}
          </div>

          {/* Article Title */}
          <h3 className="font-heading font-bold text-base sm:text-lg text-teal-900 group-hover:text-teal-700 transition line-clamp-2">
            {article.title}
          </h3>

          {/* Article Summary */}
          <p className="text-xs text-charcoal-600 leading-relaxed line-clamp-3">
            {article.summary}
          </p>
        </div>

        {/* Footer Meta Row */}
        <div className="pt-3 border-t border-stone-100 flex items-center justify-between text-[11px] text-charcoal-500">
          <div className="flex items-center gap-3">
            <div className="flex items-center gap-1 font-medium">
              <Clock className="w-3.5 h-3.5 text-coral-500" />
              <span>{article.reading_time_minutes} min read</span>
            </div>
            {article.clinical_verified_by && (
              <div
                className="hidden sm:flex items-center gap-1 text-sage-700 font-semibold"
                title={`Clinically verified by ${article.clinical_verified_by}`}
              >
                <CheckCircle2 className="w-3.5 h-3.5 text-sage-600" />
                <span className="truncate max-w-[120px]">Verified</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-1 font-bold text-teal-900 group-hover:text-coral-600 transition">
            <span>Read</span>
            <ChevronRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition" />
          </div>
        </div>
      </Card>
    </Link>
  );
};
