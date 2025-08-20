import Dexie, { type Table } from 'dexie';
import { Schedule, ScheduleCard, Audit } from '../types';


const DB_NAME = "schedule-genius";
const BASE_URL = "https://genius.systuner.com"

interface UserSettings {
  key: 'settings';
  selectedScheduleId?: string; // Change type to string
}

class MyDatabase extends Dexie {
  schedules!: Table<Schedule, string>;
  scheduleCards!: Table<ScheduleCard, number>;
  audits!: Table<Audit, number>;
  userSettings!: Table<UserSettings, string>;

  constructor() {
    super(DB_NAME);
    this.version(1).stores({
      schedules: 'ID, semester_shortcode, last_update',
      scheduleCards: '++id, major, entry_year, courses',
      audits: '++id, major, entry_year',
      userSettings: '&keys',
    });
  }
}

const db = new MyDatabase();

/* Interaction with schedules */
export async function getSelectedScheduleId(): Promise<string | undefined> {
  const settings = await db.userSettings.get('settings');
  return settings?.selectedScheduleId;
}

export async function setSelectedScheduleId(id: string) {
  await db.userSettings.put({ key: 'settings', selectedScheduleId: id });
}

export async function getAllSchedules() {
  const schedules = await db.schedules.toArray();
  // sort by latest ones first
  return schedules.sort((a, b) => new Date(a.last_update).getTime() - new Date(b.last_update).getTime())
}

export async function fetchAllSchedules() {
  const response = await fetch(`${BASE_URL}/schedules`);
  const schedules = await response.json();

  await Promise.all(schedules.schedules.map(async (sched: any) => {
    try {
      await saveSchedule(sched);
    } catch (error) {
      console.error("Failed to save schedule:", error);
    }
  }));
  return true;
}

async function saveSchedule(schedule: any) {
  const existingShortcode = await db.schedules
    .where('semester_shortcode')
    .equals(schedule.semester_shortcode)
    .first();

  const existingID = await db.schedules.where('ID').equals(schedule.ID).first();

  // If the shortcode matches, only keep the latest one
  if (existingShortcode && !((schedule.semester_shortcode[0] === 'T' ||
    schedule.semester_shortcode[0] === 'U'))) {
    if (new Date(schedule.last_update) > new Date(existingShortcode.last_update)) {
      // Delete the old version
      await db.schedules.delete(existingShortcode.ID);
      console.log("Deleted schedule with ID:", existingShortcode.ID);
    } else {
      console.log("Existing schedule is already the latest.");
      return true; // If existing one is newer or equal, skip saving
    }
  }

  // If a schedule with the same ID exists, dismiss saving it
  if (existingID) {
    console.log("Schedule with ID already exists:", schedule.ID);
    return true; // Dismiss saving
  }
  // Save the new schedule
  await db.schedules.put(schedule);
  console.log("Saved new schedule:", schedule.ID);
  return true;
}
