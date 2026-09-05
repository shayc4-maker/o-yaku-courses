import { useCallback, useEffect, useState } from 'react';
import { SiteFooter } from './components/chrome/SiteFooter';
import { SiteHeader } from './components/chrome/SiteHeader';
import { StubPage } from './components/chrome/StubPage';
import { Home } from './pages/Home';
import { Knowledge } from './pages/Knowledge';
import { Species } from './pages/Species';
import { Articles, Article } from './pages/Articles';
import { Studio } from './pages/Studio';
import { Shop } from './pages/Shop';
import { Ceramics } from './pages/Ceramics';
import { About, Contact } from './pages/About';
import type { Navigate, PageId, Route, RouteParams } from './types/route';

const STORAGE_KEY = 'oy-route';

function loadRoute(): Route {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw) as Route;
      if (parsed && parsed.page) return { page: parsed.page, params: parsed.params || {} };
    }
  } catch {
    // ignore malformed/unavailable storage
  }
  return { page: 'home', params: {} };
}

export function App() {
  const [route, setRoute] = useState<Route>(loadRoute);

  useEffect(() => {
    window.scrollTo(0, 0);
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(route));
    } catch {
      // ignore unavailable storage
    }
  }, [route]);

  const go: Navigate = useCallback((page: PageId, params: RouteParams = {}) => {
    setRoute({ page, params });
  }, []);

  return (
    <div dir="rtl">
      <SiteHeader page={route.page} onNavigate={go} />
      <Page route={route} onNavigate={go} />
      <SiteFooter onNavigate={go} />
    </div>
  );
}

function Page({ route, onNavigate }: { route: Route; onNavigate: Navigate }) {
  switch (route.page) {
    case 'home':
      return <Home onNavigate={onNavigate} />;
    case 'kb':
      return <Knowledge params={route.params} onNavigate={onNavigate} />;
    case 'species':
      return <Species params={route.params} onNavigate={onNavigate} />;
    case 'articles':
      return <Articles onNavigate={onNavigate} params={route.params} />;
    case 'article':
      return <Article params={route.params} onNavigate={onNavigate} />;
    case 'studio':
      return <Studio />;
    case 'shop':
      return <Shop onNavigate={onNavigate} />;
    case 'ceramics':
      return <Ceramics />;
    case 'about':
      return <About onNavigate={onNavigate} />;
    case 'contact':
      return <Contact onNavigate={onNavigate} />;
    default:
      return <StubPage title="עמוד לא נמצא" onNavigate={onNavigate} />;
  }
}
