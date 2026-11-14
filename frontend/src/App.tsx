import { useEffect, useState } from 'react';
import { Navbar, type PageId } from './components/Navbar';
import { AboutPage } from './pages/AboutPage';
import { ComparePage } from './pages/ComparePage';
import { DiscoverPage } from './pages/DiscoverPage';
import { ExplorePage } from './pages/ExplorePage';
import { HomePage } from './pages/HomePage';
import { MethodologyPage } from './pages/MethodologyPage';
import { ProfilesPage } from './pages/ProfilesPage';
import { MissionProvider, useMission } from './state/MissionContext';

const PAGES: PageId[] = ['home', 'explore', 'profiles', 'compare', 'discover', 'methodology', 'about'];

function initialPage(): PageId {
  const v = new URLSearchParams(window.location.search).get('view') as PageId | null;
  return v && PAGES.includes(v) ? v : 'home';
}

function Shell() {
  const m = useMission();
  const [page, setPage] = useState<PageId>(initialPage);

  const navigate = (p: PageId) => {
    setPage(p);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Keep the URL reloadable: view + mission selection.
  useEffect(() => {
    const qs = new URLSearchParams();
    qs.set('view', page);
    if (m.body) qs.set('body', m.body);
    if (m.experimentId) qs.set('exp', m.experimentId);
    if (m.targetId) qs.set('target', m.targetId);
    window.history.replaceState(null, '', `${window.location.pathname}?${qs.toString()}`);
  }, [page, m.body, m.experimentId, m.targetId]);

  return (
    <div className="min-h-screen flex flex-col bg-[#F4F8FF] text-[#142B50]">
      <Navbar activePage={page} onNavigate={navigate} />
      <main className="flex-1">
        {page === 'home' && <HomePage onNavigate={navigate} />}
        {page === 'explore' && <ExplorePage onOpenProfile={() => navigate('profiles')} />}
        {page === 'profiles' && <ProfilesPage onNavigate={navigate} />}
        {page === 'compare' && <ComparePage onNavigate={navigate} />}
        {page === 'discover' && <DiscoverPage />}
        {page === 'methodology' && <MethodologyPage />}
        {page === 'about' && <AboutPage />}
      </main>
      <footer className="bg-[#FFFFFF] border-t border-[#E1E8F0] mt-12">
        <div className="max-w-[1440px] mx-auto px-4 sm:px-8 py-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-xs text-[#68788F]">
          <div>
            <strong className="text-[#142B50]">ASTRANOVUS</strong> · Developed by Team Astravant for NASA Space Apps Challenge 2026.
          </div>
          <div className="max-w-xl sm:text-right">
            Scores are team-generated, purpose-specific estimates from public Earth-observation data. They are not official NASA ratings or landing-site
            certification.
          </div>
        </div>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <MissionProvider>
      <Shell />
    </MissionProvider>
  );
}
