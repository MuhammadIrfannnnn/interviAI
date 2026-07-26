import { useState, type ReactNode } from "react";
import { Link, useLocation } from "react-router-dom";
import { LayoutDashboard, FileText, History, User, LogOut, Menu, X } from "lucide-react";
import { useAuth } from "../hooks/useAuth";

interface AppLayoutProps {
  children: ReactNode;
}

const navItems = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/interview", label: "Interview", icon: FileText },
  { to: "/history", label: "History", icon: History },
  { to: "/profile", label: "Profile", icon: User },
];

export function AppLayout({ children }: AppLayoutProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  return (
    <div className="min-h-screen bg-bg">
      <header className="sticky top-0 z-10 border-b border-border-subtle bg-bg/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-6">
          <div className="flex items-center gap-8">
            <Link to="/dashboard" className="flex items-center gap-2">
              <div className="h-5 w-5 rounded-md bg-accent" />
              <span className="font-mono text-sm tracking-wide text-text-secondary">interviai</span>
            </Link>

            <nav className="hidden items-center gap-1 md:flex">
              {navItems.map(({ to, label, icon: Icon }) => {
                const isActive = location.pathname.startsWith(to);
                return (
                  <Link
                    key={to}
                    to={to}
                    className={`flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm transition-colors duration-150 ${
                      isActive
                        ? "bg-surface-raised text-text-primary"
                        : "text-text-secondary hover:text-text-primary"
                    }`}
                  >
                    <Icon className="h-4 w-4" />
                    {label}
                  </Link>
                );
              })}
            </nav>
          </div>

          <div className="hidden items-center gap-4 md:flex">
            <span className="text-sm text-text-secondary">{user?.full_name ?? user?.email}</span>
            <button
              onClick={logout}
              className="flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm text-text-secondary transition-colors duration-150 hover:text-text-primary"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </div>

          <button
            className="md:hidden"
            onClick={() => setMobileNavOpen((open) => !open)}
            aria-label="Toggle menu"
          >
            {mobileNavOpen ? (
              <X className="h-5 w-5 text-text-secondary" />
            ) : (
              <Menu className="h-5 w-5 text-text-secondary" />
            )}
          </button>
        </div>

        {mobileNavOpen && (
          <nav className="flex flex-col gap-1 border-t border-border-subtle px-6 py-3 md:hidden">
            {navItems.map(({ to, label, icon: Icon }) => (
              <Link
                key={to}
                to={to}
                onClick={() => setMobileNavOpen(false)}
                className="flex items-center gap-2 rounded-md px-3 py-2 text-sm text-text-secondary hover:text-text-primary"
              >
                <Icon className="h-4 w-4" />
                {label}
              </Link>
            ))}
            <button
              onClick={logout}
              className="flex items-center gap-2 rounded-md px-3 py-2 text-left text-sm text-text-secondary hover:text-text-primary"
            >
              <LogOut className="h-4 w-4" />
              Sign out
            </button>
          </nav>
        )}
      </header>

      <main className="mx-auto max-w-6xl px-6 py-10">{children}</main>
    </div>
  );
}