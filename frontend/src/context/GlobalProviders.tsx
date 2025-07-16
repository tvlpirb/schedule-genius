import React from 'react';
import { GlobalScheduleProvider } from './GlobalScheduleContext';

export const GlobalProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <GlobalScheduleProvider>
      {children}
    </GlobalScheduleProvider>
  );
};

