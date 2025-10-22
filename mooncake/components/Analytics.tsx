'use client';

import { useEffect } from 'react';
import { usePathname } from 'next/navigation';
import { analytics } from '@/lib/firebase';
import { logEvent } from 'firebase/analytics';

export default function Analytics() {
  const pathname = usePathname();

  useEffect(() => {
    const logAnalyticsEvent = async () => {
      const analyticsInstance = await analytics;
      if (analyticsInstance) {
        logEvent(analyticsInstance, 'page_view', {
          page_path: pathname,
        });
      }
    };
    logAnalyticsEvent();
  }, [pathname]);

  return null;
}
