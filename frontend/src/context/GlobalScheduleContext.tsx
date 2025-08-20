import { createContext, ReactNode, useContext, useEffect, useState } from "react"
import { Schedule } from "../types";
import { fetchAllSchedules, getAllSchedules, setSelectedScheduleId } from "@/utils/db";

type GlobalScheduleContextType = {
  schedules: Schedule[] | undefined;
  isLoading: boolean;
  handleSelectScheduleId: (id: string) => Promise<void>;
} | undefined;

const GlobalScheduleContext = createContext<GlobalScheduleContextType | undefined>(undefined);

export const GlobalScheduleProvider = ({ children }: { children: ReactNode }) => {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      await fetchAllSchedules();
      const schedules = await getAllSchedules();
      setSchedules(schedules);
      setIsLoading(true);
      try {
      } catch (error) {
        console.error("Failed to load schedules:", error);
      } finally {
        setIsLoading(false);
      }
    };
    loadData();
  }, []);

  const handleSelectScheduleId = async (id: string) => {
    await setSelectedScheduleId(id);
  }

  const contextValue: GlobalScheduleContextType = {
    schedules,
    isLoading,
    handleSelectScheduleId,
  };

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
