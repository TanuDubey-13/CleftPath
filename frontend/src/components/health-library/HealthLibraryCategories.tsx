import React from 'react';
import { HealthCategory } from '../../types';

interface HealthLibraryCategoriesProps {
  categories: HealthCategory[];
  selectedCategory: string;
  onSelectCategory: (category: string) => void;
}

export const HealthLibraryCategories: React.FC<HealthLibraryCategoriesProps> = ({
  categories,
  selectedCategory,
  onSelectCategory,
}) => {
  const totalCount = categories.reduce((sum, c) => sum + c.article_count, 0);

  return (
    <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none" role="tablist">
      {/* "All" category pill */}
      <button
        type="button"
        role="tab"
        aria-selected={selectedCategory === 'All'}
        onClick={() => onSelectCategory('All')}
        className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 flex-shrink-0 ${
          selectedCategory === 'All'
            ? 'bg-teal-900 text-white shadow-warm-xs'
            : 'bg-white text-charcoal-700 border border-stone-200 hover:bg-stone-50'
        }`}
      >
        <span>All Topics</span>
        <span
          className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
            selectedCategory === 'All'
              ? 'bg-teal-800 text-teal-100'
              : 'bg-stone-100 text-charcoal-500'
          }`}
        >
          {totalCount}
        </span>
      </button>

      {/* Dynamic categories */}
      {categories.map((cat) => {
        const isSelected = selectedCategory === cat.name;
        return (
          <button
            key={cat.name}
            type="button"
            role="tab"
            aria-selected={isSelected}
            onClick={() => onSelectCategory(cat.name)}
            className={`px-3.5 py-1.5 rounded-full text-xs font-semibold whitespace-nowrap transition flex items-center gap-1.5 flex-shrink-0 ${
              isSelected
                ? 'bg-teal-900 text-white shadow-warm-xs'
                : 'bg-white text-charcoal-700 border border-stone-200 hover:bg-stone-50'
            }`}
          >
            <span>{cat.name}</span>
            <span
              className={`text-[10px] px-1.5 py-0.2 rounded-full font-bold ${
                isSelected
                  ? 'bg-teal-800 text-teal-100'
                  : 'bg-stone-100 text-charcoal-500'
              }`}
            >
              {cat.article_count}
            </span>
          </button>
        );
      })}
    </div>
  );
};
