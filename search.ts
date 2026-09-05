import { searchKnowledgeSegments } from './data';
import type { KnowledgeSegmentRow } from '../types/db';

export interface SearchResult {
  kind: 'found' | 'notfound';
  query: string;
  segments: KnowledgeSegmentRow[];
}

/**
 * v1 search: keyword-matches published knowledge_segments (see searchKnowledgeSegments for why —
 * the prototype's canonical_answers table isn't publicly readable). Returns the matching segments
 * as "sources" rather than inventing a single synthesized answer paragraph, so the UI never shows
 * text that wasn't actually written by the studio.
 */
export async function runSearch(query: string): Promise<SearchResult> {
  const segments = await searchKnowledgeSegments(query, 6);
  return { kind: segments.length ? 'found' : 'notfound', query, segments };
}

export const SUGGESTED_QUESTIONS = ['מתי גוזמים זית?', 'איך מחווטים ענפים צעירים?', 'למה יש עלים צהובים בפיקוס?'];
