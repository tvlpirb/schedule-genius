export type Audit = RequirementCategories | Requirement[];

export type RequirementCategories = string[];

export type Requirement = {
  "Course or code": string;
  Requirement: string;
  "Inclusion/Exclusion": string;
  Type: string;
};

export type ScheduleCard = {
  id: number;
  name: string;
  courses: Course[];
  courses_taken: string[];
  major: string;
  entry_year: number;
};

export type Course = {
  course_code: string;
  course_title: string;
  units: string;
  description: string;
  prereqs: string;
  coreqs: string;
  sections: Section[];
};

export type Section = {
  section_type: string;
  section_id: string;
  timings: Timings;
  selected?: number[];
};

export type Timings = {
  days: string[];
  begin: string;
  end: string;
  teaching_location: string;
  delivery_mode: string;
  instructor: string[];
};

export type Schedule = {
  semester_name: string;
  semester_shortcode: string;
  last_update: string;
  ID: string;
  courses: Course[];
};
