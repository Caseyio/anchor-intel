import { useRef, useEffect, useState, MutableRefObject } from 'react';

export function useSmartSearchFocus(triggerRefocus: boolean): MutableRefObject<HTMLInputElement | null> {
  const searchRef = useRef<HTMLInputElement | null>(null);
  const [manualOverride, setManualOverride] = useState(false);

  // Auto-focus on mount
  useEffect(() => {
    if (searchRef.current && !manualOverride) {
      searchRef.current.focus();
    }
  }, []);

  // Focus when triggerRefocus changes
  useEffect(() => {
    if (triggerRefocus && searchRef.current && !manualOverride) {
      searchRef.current.focus();
    }
  }, [triggerRefocus, manualOverride]);

  // Detect manual interaction to suppress auto-focus
  useEffect(() => {
    const handleManual = () => setManualOverride(true);
    const el = searchRef.current;

    if (el) {
      el.addEventListener('mousedown', handleManual);
      el.addEventListener('touchstart', handleManual);
    }

    return () => {
      if (el) {
        el.removeEventListener('mousedown', handleManual);
        el.removeEventListener('touchstart', handleManual);
      }
    };
  }, []);

  return searchRef;
}
