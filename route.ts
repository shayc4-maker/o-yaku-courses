export type PageId =
  | 'home'
  | 'kb'
  | 'species'
  | 'articles'
  | 'article'
  | 'studio'
  | 'shop'
  | 'ceramics'
  | 'about'
  | 'contact';

export interface RouteParams {
  slug?: string;
  key?: string;
  [key: string]: string | undefined;
}

export interface Route {
  page: PageId;
  params: RouteParams;
}

export type Navigate = (page: PageId, params?: RouteParams) => void;
