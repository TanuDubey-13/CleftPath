import React, { useState, useEffect } from 'react';
import { RefreshCw, SearchX, ChevronLeft, ChevronRight } from 'lucide-react';
import { useHealthArticles, useHealthCategories } from '../hooks/useHealthLibrary';
import { HealthLibraryHeader } from '../components/health-library/HealthLibraryHeader';
import { HealthLibrarySearch } from '../components/health-library/HealthLibrarySearch';
import { HealthLibraryCategories } from '../components/health-library/HealthLibraryCategories';
import { HealthArticleCard } from '../components/health-library/HealthArticleCard';
import { HealthLibrarySkeleton } from '../components/health-library/HealthLibrarySkeleton';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';

export const HealthLibraryPage: React.FC = () => {
  const [searchInput, setSearchInput] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [page, setPage] = useState(1);
  const pageSize = 12;

  // Debounce search input (~300ms)
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchInput);
      setPage(1); // reset to page 1 on new search
    }, 300);
    return () => clearTimeout(timer);
  }, [searchInput]);

  const { data: categoriesData } = useHealthCategories();
  const categories = categoriesData || [];

  const {
    data: articlesData,
    isLoading,
    isError,
    error,
    refetch,
  } = useHealthArticles({
    page,
    page_size: pageSize,
    search: debouncedSearch || undefined,
    category: selectedCategory !== 'All' ? selectedCategory : undefined,
  });

  const handleCategorySelect = (category: string) => {
    setSelectedCategory(category);
    setPage(1);
  };

  const handleClearFilters = () => {
    setSearchInput('');
    setDebouncedSearch('');
    setSelectedCategory('All');
    setPage(1);
  };

  return (
    <div className="space-y-6 pb-12 animate-fade-in">
      {/* Header Banner */}
      <HealthLibraryHeader />

      {/* Search & Category Filter Controls */}
      <div className="space-y-3 bg-white p-4 sm:p-5 rounded-3xl border border-stone-200/80 shadow-warm-xs">
        <HealthLibrarySearch
          value={searchInput}
          onChange={setSearchInput}
          onClear={() => setSearchInput('')}
        />

        <HealthLibraryCategories
          categories={categories}
          selectedCategory={selectedCategory}
          onSelectCategory={handleCategorySelect}
        />
      </div>

      {/* Main Content Area */}
      {isLoading ? (
        <HealthLibrarySkeleton count={6} />
      ) : isError ? (
        <div className="max-w-2xl mx-auto py-12 space-y-4">
          <Alert variant="danger" title="Unable to Load Health Articles">
            {error instanceof Error ? error.message : 'An error occurred while fetching articles.'}
          </Alert>
          <div className="text-center">
            <Button
              variant="outline"
              size="md"
              onClick={() => refetch()}
              leftIcon={<RefreshCw className="w-4 h-4" />}
            >
              Retry Loading
            </Button>
          </div>
        </div>
      ) : !articlesData || articlesData.items.length === 0 ? (
        <div className="bg-white rounded-3xl border border-stone-200 p-8 sm:p-12 text-center max-w-xl mx-auto space-y-4 shadow-warm-sm">
          <div className="w-14 h-14 rounded-2xl bg-coral-50 text-coral-600 mx-auto flex items-center justify-center">
            <SearchX className="w-7 h-7" />
          </div>
          <h2 className="font-heading font-bold text-lg text-teal-900">
            No Educational Articles Found
          </h2>
          <p className="text-xs text-charcoal-600 leading-relaxed">
            {debouncedSearch || selectedCategory !== 'All'
              ? 'Try adjusting your search terms or clearing category filters to find relevant cleft guides.'
              : 'There are currently no published health articles available in the library.'}
          </p>
          {(debouncedSearch || selectedCategory !== 'All') && (
            <Button variant="outline" size="sm" onClick={handleClearFilters}>
              Reset Filters
            </Button>
          )}
        </div>
      ) : (
        <div className="space-y-6">
          {/* Article Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {articlesData.items.map((article) => (
              <HealthArticleCard key={article.id} article={article} />
            ))}
          </div>

          {/* Pagination Controls */}
          {articlesData.total_pages > 1 && (
            <div className="flex items-center justify-between pt-4 border-t border-stone-200/80">
              <div className="text-xs text-charcoal-500 font-medium">
                Showing page <strong className="text-charcoal-800">{articlesData.page}</strong> of{' '}
                <strong className="text-charcoal-800">{articlesData.total_pages}</strong> (
                {articlesData.total} articles)
              </div>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                  disabled={!articlesData.has_prev}
                  leftIcon={<ChevronLeft className="w-4 h-4" />}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setPage((p) => p + 1)}
                  disabled={!articlesData.has_next}
                  rightIcon={<ChevronRight className="w-4 h-4" />}
                >
                  Next
                </Button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
