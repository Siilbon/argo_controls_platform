import { NavLink, Link } from 'react-router'
import { Moon, Sun, User } from 'lucide-react'

// Top bar shown on every page.
//
// Props:
//   links         - [{ to, label }] pages to link to
//   user          - signed-in account name (e.g. "CORP\ksiil"), or null
//   theme         - 'light' or 'dark', picks which icon the theme button shows
//   onToggleTheme - function called when the theme button is clicked
function NavBar({ links, user, theme, onToggleTheme }) {
  const themeLabel = theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'
  // Show "ksiil" rather than "CORP\ksiil"; the full name is in the tooltip
  const shortUser = user?.split('\\').pop()

  return (
    <nav className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-800">
      {/* Same max width as the page content (App.jsx), so the bar lines up with it */}
      <div className="max-w-7xl mx-auto px-6 py-3 flex items-start gap-4">
        {/* Title and links wrap within this group, keeping the right-hand buttons top right */}
        <div className="flex-1 min-w-0 flex flex-wrap items-center gap-x-6 gap-y-2">
          <Link
            to="/"
            className="text-lg font-bold text-gray-800 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400"
          >
            Argo Controls Platform
          </Link>

          <ul className="flex flex-wrap gap-1">
            {links.map(link => (
              <li key={link.to}>
                <NavLink
                  to={link.to}
                  // `end` keeps Home from matching every page
                  end={link.to === '/'}
                  className={({ isActive }) => `block px-3 py-1.5 rounded-lg text-sm transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-700 dark:bg-blue-950 dark:text-blue-300 font-medium'
                      : 'text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800'
                  }`}
                >
                  {link.label}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>

        <div className="shrink-0 flex items-center gap-2">
          {user && (
            <span title={user} className="hidden sm:flex items-center gap-1 text-sm text-gray-500 dark:text-gray-400">
              <User className="w-4 h-4" aria-hidden="true" />
              {shortUser}
            </span>
          )}
          <button
            onClick={onToggleTheme}
            title={themeLabel}
            aria-label={themeLabel}
            className="p-2 rounded-lg text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-800"
          >
            {theme === 'dark'
              ? <Sun className="w-5 h-5" aria-hidden="true" />
              : <Moon className="w-5 h-5" aria-hidden="true" />}
          </button>
        </div>
      </div>
    </nav>
  )
}

export default NavBar
