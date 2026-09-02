export interface HealthArticleCard {
  id: string;
  slug: string;
  title: string;
  category: string;
  stage_id?: number | null;
  stage_title?: string | null;
  summary: string;
  author_source: string;
  clinical_verified_by?: string | null;
  reading_time_minutes: number;
  created_at: string;
  updated_at: string;
}

export interface HealthArticleDetail extends HealthArticleCard {
  content_markdown: string;
}

export interface HealthCategory {
  name: string;
  article_count: number;
}

export interface PaginatedHealthArticles {
  items: HealthArticleCard[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface HealthArticleQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  category?: string;
  stage_id?: number;
}
