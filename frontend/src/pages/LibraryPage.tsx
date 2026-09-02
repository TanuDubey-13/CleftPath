import React from 'react';
import { Search, Filter, ExternalLink, ShieldCheck } from 'lucide-react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';

const ARTICLES = [
  {
    id: 1,
    title: 'Understanding Specialized Cleft Feeders: Dr. Brown’s vs Pigeon vs Haberman',
    category: 'Feeding & Nutrition',
    readTime: '4 min read',
    source: 'ACPA Family Resources',
    verified: true,
  },
  {
    id: 2,
    title: 'Preparing Your Home and Nursery for Primary Lip Repair Recovery',
    category: 'Surgical Preparation',
    readTime: '6 min read',
    source: 'Craniofacial Surgical Board',
    verified: true,
  },
  {
    id: 3,
    title: 'Pre-Speech Sound Exploration for Infants with Cleft Palate',
    category: 'Speech & Language',
    readTime: '5 min read',
    source: 'Pediatric SLP Association',
    verified: true,
  },
];

export const LibraryPage: React.FC = () => {
  return (
    <div className="space-y-6 animate-fadeIn">
      {/* Header and Search */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="font-heading font-bold text-2xl text-teal-900">Health Library</h1>
          <p className="text-sm text-charcoal-600">
            Medically verified, evidence-grounded cleft care guides vetted by ACPA guidelines.
          </p>
        </div>
      </div>

      {/* Search Bar */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-charcoal-400 absolute left-3.5 top-3" />
          <input
            type="text"
            placeholder="Search feeding guides, surgical recovery, speech exercises..."
            className="w-full pl-10 pr-4 py-2.5 bg-white border border-stone-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-teal-700/20 focus:border-teal-900"
          />
        </div>
        <Button variant="outline" size="md" leftIcon={<Filter className="w-4 h-4" />}>
          Filter
        </Button>
      </div>

      {/* Article Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {ARTICLES.map((article) => (
          <Card key={article.id} variant="interactive" className="flex flex-col justify-between space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <Badge variant="teal" size="sm">{article.category}</Badge>
                <span className="text-xs text-charcoal-500">{article.readTime}</span>
              </div>
              <h3 className="font-heading font-bold text-base text-charcoal-900 leading-snug">
                {article.title}
              </h3>
            </div>
            <div className="pt-3 border-t border-stone-100 flex items-center justify-between text-xs">
              <span className="flex items-center gap-1 text-sage-700 font-medium">
                <ShieldCheck className="w-3.5 h-3.5" /> {article.source}
              </span>
              <ExternalLink className="w-3.5 h-3.5 text-teal-900" />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
