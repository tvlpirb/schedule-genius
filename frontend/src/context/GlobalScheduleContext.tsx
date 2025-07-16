import { createContext, ReactNode, useContext } from "react"

type GlobalScheduleContextType = any;

const GlobalScheduleContext = createContext<GlobalScheduleContextType | undefined>(undefined);

export const GlobalScheduleProvider = ({ children }: { children: ReactNode }) => {

  const contextValue: GlobalScheduleContextType = undefined;

  return (
    <GlobalScheduleContext.Provider value={contextValue}>
      {children}
    </GlobalScheduleContext.Provider>
  )
}

export const useGlobalSchedule = () => {
  const context = useContext(GlobalScheduleContext);

  if (!context) {
    throw new Error('useGlobalSchedule must be used within a GlobalScheduleProvider');
  }

  return context;
}
