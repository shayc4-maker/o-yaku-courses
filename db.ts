// Minimal row shapes for the live O-YAKU Supabase tables this app reads. Only the columns
// actually used by the UI are declared — the real tables have more columns than this.

export interface SpeciesRow {
  id: string;
  name_he: string;
  botanical_name: string | null;
  category: string | null;
  slug: string;
  description_he: string | null;
  sort_order: number;
  is_active: boolean;
  page_mode: string;
  answer_categories: string[] | null;
  classification_note_he: string | null;
}

export interface KnowledgeSegmentRow {
  id: string;
  lesson_id: string | null;
  title: string | null;
  content: string | null;
  summary: string | null;
  season: string | null;
  month: number | null;
  status: string;
  created_at: string;
  knowledge_scope: string | null;
}

export interface KnowledgeTopicRow {
  id: string;
  slug: string;
  name_he: string;
  description_he: string | null;
  sort_order: number;
  is_active: boolean;
}

export interface ArticleRow {
  id: string;
  slug: string;
  title_he: string;
  eyebrow_he: string | null;
  lead_he: string | null;
  author_he: string | null;
  date_label_he: string | null;
  footer_credit_he: string | null;
  species_href: string | null;
  cover_image_path: string | null;
  cover_alt_he: string | null;
  status: string;
  sort_order: number | null;
}

export interface ArticleBlockRow {
  id: string;
  article_id: string;
  block_type: string;
  heading_he: string | null;
  body_he: string | null;
  image_path: string | null;
  image_alt_he: string | null;
  caption_he: string | null;
  items_he: string[];
  sort_order: number;
  is_visible: boolean;
}

export interface SeasonalActionRow {
  id: string;
  species_id: string | null;
  slug: string;
  name_he: string;
  guidance_he: string | null;
  search_terms_he: string | null;
  sort_order: number | null;
  is_active: boolean;
  category: string | null;
}

export interface SeasonalActionMonthRow {
  action_id: string;
  month: number;
}
