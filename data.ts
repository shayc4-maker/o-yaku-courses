import { pgFetch } from './supabase';
import type {
  ArticleBlockRow,
  ArticleRow,
  KnowledgeSegmentRow,
  KnowledgeTopicRow,
  SeasonalActionMonthRow,
  SeasonalActionRow,
  SpeciesRow,
} from '../types/db';

export const HE_MONTHS = [
  'ינואר', 'פברואר', 'מרץ', 'אפריל', 'מאי', 'יוני',
  'יולי', 'אוגוסט', 'ספטמבר', 'אוקטובר', 'נובמבר', 'דצמבר',
];

/** All active species, ordered the way the studio curated them. */
export function listSpecies() {
  return pgFetch<SpeciesRow[]>('species', {
    select: '*',
    is_active: 'eq.true',
    order: 'sort_order.asc,name_he.asc',
  });
}

/** A handful of species for a family/category card on the Knowledge Base page. */
export function listSpeciesByCategory(category: string, limit = 4) {
  return pgFetch<SpeciesRow[]>('species', {
    select: '*',
    is_active: 'eq.true',
    category: `eq.${category}`,
    order: 'sort_order.asc',
    limit: String(limit),
  });
}

export function getSpeciesBySlug(slug: string) {
  return pgFetch<SpeciesRow[]>('species', {
    select: '*',
    slug: `eq.${slug}`,
    limit: '1',
  }).then((rows) => rows[0]);
}

export function listKnowledgeTopics() {
  return pgFetch<KnowledgeTopicRow[]>('knowledge_topics', {
    select: '*',
    is_active: 'eq.true',
    order: 'sort_order.asc',
  });
}

/**
 * Pragmatic v1 keyword search over published knowledge segments.
 *
 * The prototype's "Ask" feature was backed by `canonical_answers` (an AI-curated Q&A cache),
 * but that table has no public/anon SELECT policy in the live database — it's admin-only. Full
 * question-answering would need either a public RPC the studio adds later, or a server-side
 * function. Until then, this does a straightforward ILIKE search over the fields of published
 * knowledge_segments and returns the best-matching rows as "sources", which mirrors the shape
 * of the prototype's search result (a short list of cited segments) without inventing an answer.
 */
export function searchKnowledgeSegments(query: string, limit = 6) {
  const term = query.trim().replace(/[%_]/g, '');
  if (!term) return Promise.resolve<KnowledgeSegmentRow[]>([]);
  const pattern = `*${term}*`;
  return pgFetch<KnowledgeSegmentRow[]>('knowledge_segments', {
    select: '*',
    status: 'eq.published',
    or: `(title.ilike.${pattern},summary.ilike.${pattern},content.ilike.${pattern})`,
    order: 'created_at.desc',
    limit: String(limit),
  });
}

export function listPublishedArticles(limit = 12) {
  return pgFetch<ArticleRow[]>('articles', {
    select: '*',
    status: 'eq.published',
    order: 'sort_order.asc.nullslast,created_at.desc',
    limit: String(limit),
  });
}

export function getArticleBySlug(slug: string) {
  return pgFetch<ArticleRow[]>('articles', {
    select: '*',
    slug: `eq.${slug}`,
    status: 'eq.published',
    limit: '1',
  }).then((rows) => rows[0]);
}

export function listArticleBlocks(articleId: string) {
  return pgFetch<ArticleBlockRow[]>('article_blocks', {
    select: '*',
    article_id: `eq.${articleId}`,
    is_visible: 'eq.true',
    order: 'sort_order.asc',
  });
}

/** Species-specific seasonal actions (falls back to none — category-general actions are separate). */
export function listSeasonalActionsForSpecies(speciesId: string) {
  return pgFetch<SeasonalActionRow[]>('seasonal_actions', {
    select: '*',
    is_active: 'eq.true',
    species_id: `eq.${speciesId}`,
    order: 'sort_order.asc',
  });
}

/** Category-general seasonal actions (species_id is null, scoped by category instead). */
export function listSeasonalActionsForCategory(category: string) {
  return pgFetch<SeasonalActionRow[]>('seasonal_actions', {
    select: '*',
    is_active: 'eq.true',
    species_id: 'is.null',
    category: `eq.${category}`,
    order: 'sort_order.asc',
  });
}

export function listActionMonths(actionIds: string[]) {
  if (actionIds.length === 0) return Promise.resolve<SeasonalActionMonthRow[]>([]);
  return pgFetch<SeasonalActionMonthRow[]>('seasonal_action_months', {
    select: '*',
    action_id: `in.(${actionIds.join(',')})`,
  });
}
