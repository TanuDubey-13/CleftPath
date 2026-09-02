export interface VillageChannel {
  id: string;
  name: string;
  slug: string;
  description: string;
  stage_id?: number | null;
  is_private: boolean;
  posts_count: number;
}

export interface PaginatedVillageChannels {
  items: VillageChannel[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface VillagePost {
  id: string;
  channel_id: string;
  channel_name?: string | null;
  channel_slug?: string | null;
  user_id: string;
  author_alias: string;
  author_avatar_seed: string;
  title: string;
  content: string;
  status: string;
  is_flagged: boolean;
  upvotes_count: number;
  comments_count: number;
  has_reacted: boolean;
  user_reaction?: string | null;
  created_at: string;
  updated_at: string;
}

export interface VillagePostCreateRequest {
  channel_id: string;
  title: string;
  content: string;
  author_alias?: string;
  author_avatar_seed?: string;
}

export interface VillagePostUpdateRequest {
  title?: string;
  content?: string;
}

export interface PaginatedVillagePosts {
  items: VillagePost[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface VillageComment {
  id: string;
  post_id: string;
  user_id: string;
  author_alias: string;
  content: string;
  status: string;
  created_at: string;
}

export interface VillageCommentCreateRequest {
  content: string;
  author_alias?: string;
}

export interface VillageCommentUpdateRequest {
  content: string;
}

export interface PaginatedVillageComments {
  items: VillageComment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface VillageReactionRequest {
  reaction_type: 'heart' | 'hug' | 'celebrate' | 'strength' | 'helpful' | string;
}

export interface VillageReactionResponse {
  post_id: string;
  reaction_type: string;
  action: 'added' | 'removed' | string;
  upvotes_count: number;
  has_reacted: boolean;
}

export interface VillageReportCreateRequest {
  reason: 'harassment' | 'medical_misinformation' | 'hate_or_abuse' | 'spam' | 'inappropriate_content' | 'privacy_violation' | 'other' | string;
  details?: string;
}

export interface VillageReportResponse {
  id: string;
  post_id?: string | null;
  comment_id?: string | null;
  reason: string;
  details?: string | null;
  status: string;
  created_at: string;
}
