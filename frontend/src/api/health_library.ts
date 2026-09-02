import { apiClient } from '../lib/apiClient';
import {
  ApiResponse,
  HealthArticleDetail,
  HealthArticleQueryParams,
  HealthCategory,
  PaginatedHealthArticles,
} from '../types';

export const fetchHealthArticles = async (
  params?: HealthArticleQueryParams
): Promise<PaginatedHealthArticles> => {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.set('page', params.page.toString());
  if (params?.page_size) queryParams.set('page_size', params.page_size.toString());
  if (params?.search) queryParams.set('search', params.search);
  if (params?.category && params.category !== 'All') queryParams.set('category', params.category);
  if (params?.stage_id !== undefined && params.stage_id !== null) {
    queryParams.set('stage_id', params.stage_id.toString());
  }

  const queryStr = queryParams.toString();
  const url = queryStr ? `/health-library/articles?${queryStr}` : '/health-library/articles';

  const response = await apiClient.get<ApiResponse<PaginatedHealthArticles>>(url);
  return response.data.data;
};

export const fetchHealthArticleDetail = async (
  articleId: string
): Promise<HealthArticleDetail> => {
  const response = await apiClient.get<ApiResponse<HealthArticleDetail>>(
    `/health-library/articles/${encodeURIComponent(articleId)}`
  );
  return response.data.data;
};

export const fetchHealthCategories = async (): Promise<HealthCategory[]> => {
  const response = await apiClient.get<ApiResponse<HealthCategory[]>>(
    '/health-library/categories'
  );
  return response.data.data;
};
