
import { useState, useEffect } from 'react';
import { NetworkRequestData } from '@/types/api';

const SESSION_KEY = 'lastSearch';

export const useSessionState = () => {
  const [lastSearch, setLastSearch] = useState<NetworkRequestData | null>(null);

  useEffect(() => {
    // Load from sessionStorage on mount
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        setLastSearch(parsed);
      }
    } catch (error) {
      console.error('Error loading session state:', error);
    }
  }, []);

  const saveSearch = (searchData: NetworkRequestData) => {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(searchData));
      setLastSearch(searchData);
    } catch (error) {
      console.error('Error saving session state:', error);
    }
  };

  const clearSearch = () => {
    try {
      sessionStorage.removeItem(SESSION_KEY);
      setLastSearch(null);
    } catch (error) {
      console.error('Error clearing session state:', error);
    }
  };

  return {
    lastSearch,
    saveSearch,
    clearSearch
  };
};
