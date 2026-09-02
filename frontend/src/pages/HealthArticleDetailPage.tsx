import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Clock, CheckCircle2, ShieldAlert, BookOpen, RefreshCw } from 'lucide-react';
import { useHealthArticle } from '../hooks/useHealthLibrary';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { Card } from '../components/ui/Card';
import { Skeleton } from '../components/ui/Skeleton';
import { Alert } from '../components/ui/Alert';

export const HealthArticleDetailPage: React.FC = () => {
  const { articleId } = useParams<{ articleId: string }>();
  const { data: article, isLoading, isError, error, refetch } = useHealthArticle(articleId);

  if (isLoading) {
    return (
      <div className="max-w-3xl mx-auto py-8 space-y-6 animate-fade-in">
        <Skeleton variant="text" className="w-32 h-5" />
        <Skeleton variant="rectangular" className="w-full h-10 rounded-2xl" />
        <div className="flex gap-3">
          <Skeleton variant="rectangular" className="w-24 h-6 rounded-full" />
          <Skeleton variant="rectangular" className="w-32 h-6 rounded-full" />
        </div>
        <Skeleton variant="rectangular" className="w-full h-72 rounded-3xl" />
      </div>
    );
  }

  if (isError || !article) {
    return (
      <div className="max-w-2xl mx-auto py-12 space-y-4">
        <Alert variant="danger" title="Article Not Found">
          {error instanceof Error ? error.message : 'The requested health article could not be loaded.'}
        </Alert>
        <div className="text-center space-x-3">
          <Link to="/health-library">
            <Button variant="outline" size="sm" leftIcon={<ArrowLeft className="w-4 h-4" />}>
              Back to Health Library
            </Button>
          </Link>
          <Button variant="primary" size="sm" onClick={() => refetch()} leftIcon={<RefreshCw className="w-4 h-4" />}>
            Retry
          </Button>
        </div>
      </div>
    );
  }

  // Line-by-line Markdown parsing
  const renderMarkdown = (content: string) => {
    const lines = content.split('\n');
    const elements: React.ReactNode[] = [];
    let currentList: string[] = [];
    let listType: 'ul' | 'ol' | null = null;

    const flushList = (keyPrefix: string) => {
      if (currentList.length > 0 && listType) {
        if (listType === 'ul') {
          elements.push(
            <ul key={`${keyPrefix}-ul`} className="list-disc list-inside space-y-1.5 my-3 text-sm text-charcoal-800 leading-relaxed">
              {currentList.map((item, idx) => (
                <li key={idx} dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
              ))}
            </ul>
          );
        } else {
          elements.push(
            <ol key={`${keyPrefix}-ol`} className="list-decimal list-inside space-y-1.5 my-3 text-sm text-charcoal-800 leading-relaxed">
              {currentList.map((item, idx) => (
                <li key={idx} dangerouslySetInnerHTML={{ __html: item.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }} />
              ))}
            </ol>
          );
        }
        currentList = [];
        listType = null;
      }
    };

    lines.forEach((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) {
        flushList(`line-${idx}`);
        return;
      }

      if (trimmed.startsWith('# ')) {
        flushList(`line-${idx}`);
        elements.push(
          <h1 key={`h1-${idx}`} className="font-heading font-bold text-2xl sm:text-3xl text-teal-900 mt-6 mb-3">
            {trimmed.replace('# ', '')}
          </h1>
        );
      } else if (trimmed.startsWith('### ')) {
        flushList(`line-${idx}`);
        elements.push(
          <h3 key={`h3-${idx}`} className="font-heading font-bold text-lg text-teal-900 mt-5 mb-2">
            {trimmed.replace('### ', '')}
          </h3>
        );
      } else if (trimmed.startsWith('## ')) {
        flushList(`line-${idx}`);
        elements.push(
          <h2 key={`h2-${idx}`} className="font-heading font-bold text-xl text-teal-900 mt-5 mb-2">
            {trimmed.replace('## ', '')}
          </h2>
        );
      } else if (trimmed.startsWith('* ') || trimmed.startsWith('- ')) {
        if (listType !== 'ul') flushList(`line-${idx}`);
        listType = 'ul';
        currentList.push(trimmed.replace(/^[\*\-]\s+/, ''));
      } else if (/^\d+\.\s+/.test(trimmed)) {
        if (listType !== 'ol') flushList(`line-${idx}`);
        listType = 'ol';
        currentList.push(trimmed.replace(/^\d+\.\s+/, ''));
      } else {
        flushList(`line-${idx}`);
        elements.push(
          <p
            key={`p-${idx}`}
            className="text-sm text-charcoal-800 leading-relaxed my-3"
            dangerouslySetInnerHTML={{ __html: trimmed.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>') }}
          />
        );
      }
    });

    flushList('final');
    return elements;
  };

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-16 animate-fade-in">
      {/* Back to Library Navigation */}
      <div>
        <Link
          to="/health-library"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-teal-900 hover:text-coral-600 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to Health Library</span>
        </Link>
      </div>

      {/* Article Header Card */}
      <div className="bg-white rounded-3xl border border-stone-200/80 p-6 sm:p-8 space-y-4 shadow-warm-sm">
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

        <h1 className="font-heading font-bold text-2xl sm:text-3xl text-teal-900 leading-tight">
          {article.title}
        </h1>

        <p className="text-sm text-charcoal-700 leading-relaxed bg-ivory-50 p-4 rounded-2xl border border-stone-100 italic">
          {article.summary}
        </p>

        {/* Metadata Badges */}
        <div className="pt-2 flex flex-wrap items-center gap-4 text-xs text-charcoal-500 border-t border-stone-100">
          <div className="flex items-center gap-1">
            <Clock className="w-4 h-4 text-coral-500" />
            <span>{article.reading_time_minutes} min read</span>
          </div>

          <div className="flex items-center gap-1">
            <BookOpen className="w-4 h-4 text-teal-900" />
            <span>Source: {article.author_source}</span>
          </div>

          {article.clinical_verified_by && (
            <div className="flex items-center gap-1 text-sage-700 font-medium">
              <CheckCircle2 className="w-4 h-4 text-sage-600" />
              <span>Verified by {article.clinical_verified_by}</span>
            </div>
          )}
        </div>
      </div>

      {/* Article Body */}
      <Card className="p-6 sm:p-10 bg-white border border-stone-200/80 rounded-3xl shadow-warm-xs">
        <div className="prose prose-stone max-w-none text-charcoal-900">
          {renderMarkdown(article.content_markdown)}
        </div>
      </Card>

      {/* Clinical Disclaimer & Consultation Footer */}
      <Card className="p-5 bg-ivory-50 border border-stone-200 rounded-2xl shadow-warm-xs">
        <div className="flex items-start gap-3">
          <ShieldAlert className="w-5 h-5 text-coral-500 flex-shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="font-bold text-xs text-charcoal-900">Medical Safety & Care Team Notice</h4>
            <p className="text-xs text-charcoal-700 leading-relaxed">
              This educational guide is provided for general informational purposes and does not formulate an individualized medical diagnosis, surgical prescription, or direct treatment regimen. Always consult your cleft and craniofacial care team for clinical evaluations tailored to your child’s anatomy.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
};
