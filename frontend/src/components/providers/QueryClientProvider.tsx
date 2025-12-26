'use client';

import { QueryClient, QueryClientProvider as RQProvider } from 'react-query';
import { ReactNode } from 'react';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export function QueryClientProvider({ children }: { children: ReactNode }) {
  return <RQProvider client={queryClient}>{children}</RQProvider>;
}
