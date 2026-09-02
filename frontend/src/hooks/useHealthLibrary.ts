import { useQuery } from '@tanstack/react-query';
import {
  fetchHealthArticleDetail,
  fetchHealthArticles,
  fetchHealthCategories,
} from '../api/health_library';
import { HealthArticleQueryParams } from '../types';

export const useHealthArticles = (params: HealthArticleQueryParams = {}) => {
  return useQuery({
    queryKey: ['healthArticles', params],
    queryFn: () => fetchHealthArticles(params),
    staleTime: 5 * 60 * 1000,
  });
};

export const useHealthArticle = (articleId?: string) => {
  return useQuery({
    queryKey: ['healthArticle', articleId],
    queryFn: () => {
      if (!articleId) throw new Error('Article ID is required');
      return fetchHealthArticleDetail(articleId);
    },
    enabled: !!articleId,
    staleTime: 10 * 60 * 1000,
  });
};

export const useHealthCategories = () => {
  return useQuery({
    queryKey: ['healthCategories'],
    queryFn: fetchHealthCategories,
    staleTime: 15 * 60 * 1000,
  });
};
