import React from 'react'
import { FiSun, FiMoon } from 'react-icons/fi'
import { useTheme } from '../../context/ThemeContext'

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme()
  return (
    <button
      onClick={toggleTheme}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-md text-xs font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
      title="Toggle dark / light mode"
    >
      {theme === 'dark' ? <FiSun size={15} /> : <FiMoon size={15} />}
      {theme === 'dark' ? 'Light' : 'Dark'}
    </button>
  )
}
