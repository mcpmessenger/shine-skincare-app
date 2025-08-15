'use client';

import { useState, useEffect } from 'react';
import { Sun } from 'lucide-react';

export default function ThemeToggle() {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    // Check for dark mode preference and localStorage
    const savedDarkMode = localStorage.getItem('darkMode');
    const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const isDark = savedDarkMode !== null ? JSON.parse(savedDarkMode) : systemDarkMode;
    setIsDarkMode(isDark);
    
    // Apply theme to body
    if (isDark) {
      document.body.setAttribute('data-theme', 'dark');
    } else {
      document.body.removeAttribute('data-theme');
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    localStorage.setItem('darkMode', JSON.stringify(newDarkMode));
    
    // Apply theme to body
    if (newDarkMode) {
      document.body.setAttribute('data-theme', 'dark');
    } else {
      document.body.removeAttribute('data-theme');
    }
  };

  return (
    <button
      onClick={toggleDarkMode}
      className="p-2 rounded-xl bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors border border-gray-200 dark:border-gray-700"
      aria-label="Toggle dark mode"
    >
      <Sun className="w-5 h-5 text-gray-600 dark:text-gray-300" />
    </button>
  );
} 