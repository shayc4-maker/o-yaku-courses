/**
 * Minimal, read-only PostgREST client for the live O-YAKU Supabase project.
 *
 * Deliberately not using @supabase/supabase-js here: everything the "core" pages need is a
 * handful of read-only, RLS-filtered SELECTs, and a thin fetch wrapper keeps the dependency
 * footprint (and bundle size) small. The anon/publishable key below is safe to ship in client
 * code by Supabase design — it only ever reads what Row Level Security already allows the
 * public to see (e.g. species, published knowledge_segments, published articles).
 *
 * If the project later needs writes, auth, or realtime, swap this file for the real
 * @supabase/supabase-js client without touching call sites — they all go through `pgFetch`.
 */

const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL as string | undefined;
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY as string | undefined;

if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
  // eslint-disable-next-line no-console
  console.warn(
    '[supabase] VITE_SUPABASE_URL / VITE_SUPABASE_ANON_KEY are not set — copy .env.example to .env. ' +
      'Live-data pages (home/kb/species) will fail to load content until this is configured.'
  );
}

export class SupabaseQueryError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = 'SupabaseQueryError';
    this.status = status;
  }
}

/**
 * Query a table (or view) through PostgREST. `params` are passed straight through as query
 * string parameters, so use PostgREST's own filter syntax, e.g.:
 *   pgFetch('species', { select: '*', is_active: 'eq.true', order: 'sort_order.asc' })
 */
export async function pgFetch<T>(path: string, params: Record<string, string> = {}): Promise<T> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new SupabaseQueryError('Supabase is not configured (missing env vars)', 0);
  }
  const url = new URL(`${SUPABASE_URL}/rest/v1/${path}`);
  for (const [key, value] of Object.entries(params)) {
    url.searchParams.set(key, value);
  }
  const res = await fetch(url.toString(), {
    headers: {
      apikey: SUPABASE_ANON_KEY,
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
    },
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new SupabaseQueryError(`Supabase query failed for ${path}: ${res.status} ${body}`, res.status);
  }
  return res.json() as Promise<T>;
}

/** Call a Postgres RPC function exposed through PostgREST. */
export async function pgRpc<T>(fn: string, args: Record<string, unknown> = {}): Promise<T> {
  if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new SupabaseQueryError('Supabase is not configured (missing env vars)', 0);
  }
  const res = await fetch(`${SUPABASE_URL}/rest/v1/rpc/${fn}`, {
    method: 'POST',
    headers: {
      apikey: SUPABASE_ANON_KEY,
      Authorization: `Bearer ${SUPABASE_ANON_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(args),
  });
  if (!res.ok) {
    const body = await res.text().catch(() => '');
    throw new SupabaseQueryError(`Supabase RPC failed for ${fn}: ${res.status} ${body}`, res.status);
  }
  return res.json() as Promise<T>;
}
