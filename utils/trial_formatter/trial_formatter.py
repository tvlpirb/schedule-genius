# ACKNOWLEDGEMENT:
# CODE BETWEEN ###### ACK ######## is written by
# Giselle Reis <giselle@cmu.edu>
# Ryan Riley <rileyrd@cmu.edu>
# The only addition I've made is converting it to conform to the proposed schedule.json format

import hashlib
import pandas as pd
import json
from typing import *
from pandas.io.excel._openpyxl import OpenpyxlReader
from pandas._typing import Scalar
from datetime import datetime
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

############### ACK #################

def formatCourseNumber (n: int) -> str:
    """
    Adds a trailing zero and dash after department code to format
    course numbers.

    Args:
        n (e.g. 2251)

    Returns:
        the formatted course number as a string (e.g. "02-251")
    """

    n = str(n)
    if len(n) == 4:
        n = "0" + n
    code = n[:2]
    num = n[2:]
    return code + "-" + num

# A map of the long counts_for string to something more readable.
# This doesn't cover everything, but we'll handle others manually.
countsfor_map = {
    # CS Electives
    "BS in Computer Science---Computer Science---Logics & Languages Elective": "Logics & Languages Elective",
    "BS in Computer Science---Computer Science---Software Systems Elective": "Software Systems Elective",
    "BS in Computer Science---Computer Science---Domains Elective": "Domains Elective",
    "BS in Computer Science---Computer Science---Artificial Intelligence Elective": "Artificial Intelligence Elective",
    "BS in Computer Science---2 SCS Electives": "2 SCS Electives",
    # Math
    "BS in Computer Science---Mathematics and Probability---Calculus": "Mathematics and Probability",
    "BS in Computer Science---Mathematics and Probability---Mathematical Foundations for CS": "Mathematics and Probability",
    "BS in Computer Science---Mathematics and Probability---Matrix/Linear Algebra": "Mathematics and Probability",
    "BS in Computer Science---Mathematics and Probability---Calculus---3d Calculus": "Mathematics and Probability",
    # CS Core
    "BS in Computer Science---Computer Science---xx-213 Introduction to Computer Systems": "Computer Science Core",
    "BS in Computer Science---First-year Immigration Course": "Computer Science Core",
    "BS in Computer Science---Computer Science": "Computer Science Core",
    # Core Other
    "EY2023 Qatar CS - General Education---First Year Writing": "Writing",
    "BS in Computer Science---Technical Communication": "Writing",
    "BS in Computer Science---Computing @ Carnegie Mellon": "Core@CMU",
    # Humanities Electives
    "EY2023 Qatar CS - General Education---Humanities/Arts Electives": "Humanities/Arts Electives",
    "EY2023 Qatar CS - General Education---Category 1---Category 1: Cognition, Choice, and Behavior (CS, CB, & HCI)": "Cognition, Choice, and Behavior",
    "EY2023 Qatar CS - General Education---Category 2: Economic, Political, and Social Institutions": "Economic, Political, and Social Institutions",
    "EY2023 Qatar CS - General Education---Category 3: Cultural Analysis": "Cultural Analysis",
    #"Humanities and Arts": "Humanities and Arts",
    # Science
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CS, AI, & HCI)---Science/Engineering, Same Department (2 courses)---Option 2---Biology Course": "Science and Engineering",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CS, AI, & HCI)---Science/Engineering, Any Department (4 courses)": "Science and Engineering",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CS, AI, & HCI)---Science/Engineering, Same Department (2 courses)---Option 1": "Science and Engineering",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CS, AI, & HCI)---Science/Engineering, Same Department (2 courses)---Option 2": "Science and Engineering",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CS, AI, & HCI)---Lab Requirement": "Lab Requirement",
    #"Science and Engineering":"Science and Engineering",
}

# Requirements to kill from the list because they aren't relevant to the CS major
countsfor_kill = {
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Any Department (4 courses)---Modern Biology",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Same Department (2 courses)---Modern Biology",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Same Department (2 courses)---Molecular Biology",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Lab Requirement",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Any Department (4 courses)---Molecular Biology",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Any Department (4 courses)---Chemistry",
    "EY2023 Qatar CS - General Education---Science and Engineering---Science and Engineering (CB)---Science/Engineering, Any Department (4 courses)---Physics",
    "EY2023 Qatar CS - General Education---Category 1---Category 1A: Cognitive Studies (AI)",
}

def countsFor (course_number: str, audit: pd.DataFrame) -> Set[str]:
    """
    Given a course number and an audit, returns a set of
    sub-requirements the course counts for in the audit.

    Args:
        course_number: e.g. "15-150"
        audit: a DataFrame with the following columns:
               - Course or code
               - Requirement (e.g. "Humanities and Arts")
               - Inclusion/Exclusion
               - Type

    Returns:
        a set of the requirements the course fulfills
    """

    # Requirements that include the course explicitly.
    matched = audit[(audit["Type"] == "Course") & 
                    (audit["Course or code"] == course_number) & 
                    (audit["Inclusion/Exclusion"] == "Inclusion")]
    include_course = set(matched["Requirement"].values)
       
    # Requirements that include the course because of its code
    matched_code = audit[(audit["Type"] == "Code") & 
                         (audit["Course or code"] == course_number[0:2]) & 
                         (audit["Inclusion/Exclusion"] == "Inclusion")]
    include_code = set(matched_code["Requirement"].values)

    # Requirements that exclude the course explicitly
    excluded = audit[(audit["Type"] == "Course") & 
                     (audit["Course or code"] == course_number) & 
                     (audit["Inclusion/Exclusion"] == "Exclusion")]
    exclude_course = set(excluded["Requirement"].values)

    # Course cannot be included and excluded for the same requirement
    assert(include_course.intersection(exclude_course) == set())

    counts_for = (include_course | include_code) - exclude_course

    return counts_for

def countsForCS (course_number: str, audit: pd.DataFrame) -> Set[str]:
    """
    Given a course number and an audit, returns a set of
    sub-requirements the course counts for in the audit.

    Args:
        course_number: e.g. "15-150"
        audit: a DataFrame with the following columns:
               - Course or code
               - Requirement (e.g. "Humanities and Arts")
               - Inclusion/Exclusion
               - Type

    Returns:
        a set of the requirements the course fulfills, in which the
        CS requirements are simplified.
    """
    counts_for = countsFor(course_number, audit)
    print(course_number, counts_for)

    # Filter the categories through the translation map above.
    new_set = set()
    for item in counts_for:
        if item in countsfor_kill:
            continue;
        
        if item in countsfor_map:
            new_set.add(countsfor_map[item])
        else:
            new_set.add(item)
            print("Warning: Unknown requirement: ", course_number, item)

    return new_set

def getCourseTitle(course_number: str) -> str:
    """
    Given a course number, return the course title.
    The json files used to get this information are obtained from
    Stellic using a script written by Prof. Ryan Riley.
    """
    try:
        path = os.path.join(base_dir, '../data/course-details', f'{course_number}.json')
        file = open(path)
    except FileNotFoundError:
        print("No file for course: " + course_number)
        return "<Unknown>"
    else:
        data = json.load(file)
        return data["name"]

def getCourseUnits(course_number: str) -> str:
    """
    Given a course number, return the number of units
    The json files used to get this information are obtained from
    Stellic using a script written by Prof. Ryan Riley.
    """
    try:
        path = os.path.join(base_dir, '../data/course-details', f'{course_number}.json')
        file = open(path)
    except FileNotFoundError:
        print("No file for course: " + course_number)
        return "??"
    else:
        data = json.load(file)
        return data["units"]

def getPreReqs(course_number: str) -> str:
    """
    Given a course number, return the pre-requisites as listed in
    Stellic.
    The json files used to get this information are obtained from
    Stellic using a script written by Prof. Ryan Riley.

    To do: If the pre-reqs were listed in a more structured way, we
    could make a dependency graph of courses.
    """

    try:
        path = os.path.join(base_dir, '../data/course-details', f'{course_number}.json')
        file = open(path)       
    except FileNotFoundError:
        print("No file for course: " + course_number)
        return "NO FILE"
    else:
        data = json.load(file)
        prereqs = data['prereqs']['text']
        #if data['prereqs']['raw_pre_req'] != '':
        #    print(data['prereqs']['raw_pre_req'])
        return prereqs

def cmpSemester(s1: str, s2: str) -> int:
    """
    Function to pass to sorted for sorting semesters.
    Usage: sorted(s, key=functools.cmp_to_key(cmpSemester))
    where s is a list of strings in the format {S,M,F}XX.

    Returns:
        negative int if s1 is before      s2
        zero         if s1 is the same as s2
        positive int if s1 is after       s2 
    """

    if s1[1:] < s2[1:]:
        return -1
    elif s1[1:] > s2[1:]:
        return 1
    else:
        # S < M < F
        d = {'S': 0, 'M': 1, 'F': 2}
        s1 = d[s1[0]]
        s2 = d[s2[0]]
        return s1 - s2

class CustomReader(OpenpyxlReader):
    """
    A custom class to read from a spreadsheet, but skip rows that are strikethrough.

    This just simplifies working with Jarrin's excel files.

    Idea for code from https://stackoverflow.com/questions/59525171/pandas-read-excel-and-skip-cells-with-strikethrough

    get_sheet_data code copied from <Python base directory>/lib/python3.10/site-packages/pandas/io/excel/_openpyxl.py from pandas 2.1.0
    """
    def get_sheet_data(
        self, sheet, file_rows_needed: int | None = None
    ) -> list[list[Scalar]]:
        if self.book.read_only:
            sheet.reset_dimensions()

        data: list[list[Scalar]] = []
        last_row_with_data = -1
        for row_number, row in enumerate(sheet.rows):
            #########################################################
            # Custom code to not read row if row[1] item is strikethrough
            if len(row) > 1:
                first = row[1]
                if first.font == None or first.font.strike:
                    continue
            #########################################################

            converted_row = [self._convert_cell(cell) for cell in row]
            while converted_row and converted_row[-1] == "":
                # trim trailing empty elements
                converted_row.pop()
            if converted_row:
                last_row_with_data = row_number
            data.append(converted_row)
            if file_rows_needed is not None and len(data) >= file_rows_needed:
                break

        # Trim trailing empty rows
        data = data[: last_row_with_data + 1]

        if len(data) > 0:
            # extend rows to max width
            max_width = max(len(data_row) for data_row in data)
            if min(len(data_row) for data_row in data) < max_width:
                empty_cell: list[Scalar] = [""]
                data = [
                    data_row + (max_width - len(data_row)) * empty_cell
                    for data_row in data
                ]

        return data

class CustomExcelFile(pd.ExcelFile):
    _engines = {"openpyxl": CustomReader,}


def read_old_format(filename: str):
    """
    Read in the schedule if it is in the "old" (pre-Fall 2024) format.
    An example is: data/schedules/2023b-fall.xlsx
    """

    # Read in the excel file, but exclude strikethrow rows
    # This code is potentially brittle and tied to a specific pandas version.
    # If it stops working, replace these next two lines with
    # schedule = pd.read_excel('data/schedules/2024a-spring.xlsx')
    schedule = CustomExcelFile(filename, engine="openpyxl")
    schedule = schedule.parse()

    # Transforms 3121 into "03-121"
    schedule["COURSE"] = schedule["COURSE"].map(formatCourseNumber)

    # Selects only relevant columns
    schedule = schedule[
        [
            "COURSE",
            "SECTION",
            "COURSE TITLE",
            "UNITS",
            "MINI",
            "DAY",
            "BEGIN TIME",
            "END TIME",
            "INSTRUCTORS",
        ]
    ]

    # Adds column with pre-reqs
    schedule["Pre-reqs"] = schedule.apply(
        lambda row: getPreReqs(row["COURSE"]), axis=1
    )

    # Figure out what it counts for
    audit = pd.read_excel(
        "../data/audits-xlsx/cs-audit.xlsx", dtype={"Course or code": str}
    )
    schedule["counts-for"] = schedule.apply(
        lambda row: countsForCS(row["COURSE"], audit), axis=1
    )

    schedule.sample(n=5)
    return schedule, audit


def read_infosilem_format(filename: str):
    """
    Read in the schedule that is in the "new" (Fall 2024) format that is output by infosilem.

    Example: data/schedules/2024b-fall-trial-mar18.xlsx
    """
    schedule = CustomExcelFile(filename, engine="openpyxl")
    schedule = schedule.parse()

    # Transforms 3121 into "03-121"
    schedule["COURSE"] = schedule["Course - ID"].map(formatCourseNumber)

    schedule["SECTION"] = schedule["Section"]

    # Some of these cells contain single times, others contain a multiline string of times.  Who does that?  Seriously.
    from datetime import datetime

    def map_time(s):
        if type(s) == str:
            return datetime.strptime(s.split("\n")[0], "%H:%M").time()
        else:
            return s

    schedule["BEGIN TIME"] = schedule["Delivery times - Start time"].map(map_time)
    schedule["END TIME"] = schedule["Delivery times - End time"].map(map_time)

    schedule["INSTRUCTORS"] = schedule["Professor - Last name"]

    # Maps the days from full names to UTR style.
    def map_day(day_string):
        if type(day_string) != str:
            return ""
        day_dict = {
            "Sunday": "U",
            "Monday": "M",
            "Tuesday": "T",
            "Wednesday": "W",
            "Thursday": "R",
            "Friday": "F",
            "Saturday": "S",
        }
        days = day_string.split("\n")
        res = ""
        for day in days:
            res += day_dict.get(day, "")
        return res

    schedule["DAY"] = schedule["Delivery times - Day"].map(map_day)

    # Get the course titles
    schedule["COURSE TITLE"] = schedule.apply(
        lambda row: getCourseTitle(row["COURSE"]), axis=1
    )

    schedule["UNITS"] = schedule.apply(
        lambda row: getCourseUnits(row["COURSE"]), axis=1
    )

    schedule = schedule[
        [
            "COURSE",
            "SECTION",
            "COURSE TITLE",
            "UNITS",
            #'MINI',
            "DAY",
            "BEGIN TIME",
            "END TIME",
            "INSTRUCTORS",
        ]
    ]

    # Adds column with pre-reqs
    schedule["Pre-reqs"] = schedule.apply(
        lambda row: getPreReqs(row["COURSE"]), axis=1
    )

    # Figure out what it counts for
    path = os.path.join(base_dir, "../data/audits-xlsx/cs-audit.xlsx")
    audit = pd.read_excel(
        path, dtype={"Course or code": str}
    )
    schedule["counts-for"] = schedule.apply(
        lambda row: countsForCS(row["COURSE"], audit), axis=1
    )
   
    return schedule, audit
############### ACK #################

def stdCode(s):
    if isinstance(s,str):
        department = s[:2]
        course = s[3:]
        return department + course

    else:
        print("Got an invalid course number at conversion!")
        return "Invalid Course Number"

def stdTime(s):
    s_type = type(s)
    if s_type == str:
        time_obj = datetime.strptime(s.split("\n")[0], "%H:%M").time()
    else:
        if str(s) == "nan":
            return "NAN"
        time_obj = datetime.strptime(str(s), "%H:%M:%S").time()

    # Convert to AM/PM format
    formatted_time = time_obj.strftime("%I:%M%p").lstrip('0')
    return formatted_time

def stdSec(section):
    if isinstance(section,str):
        pass
    elif isinstance(section,int):
        section = "Lec " + str(section)
    return section

def stdIns(instructors):
    return instructors.split("\n") if isinstance(instructors, str) else []

def stdReqs(requirements):
    return requirements.replace("-","")

def stdDays(days):
    order = {
        'U': 0,
        'M': 1,
        'T': 2,
        'W': 3,
        'R': 4,
        'F': 5,
        'S': 6
    }
    
    return ''.join(sorted(days, key=lambda day: order[day]))

"""
  Generates a short ID based on a name and a Python list.

  Args:
      name: The name to use for generating the ID (string).
      data_list: The list to include in the ID generation (any list).

  Returns:
      A short string representing a unique ID.
  """
def generateShortID(data_str):
  hashed_data = hashlib.sha1(str(data_str).encode("utf-8")).hexdigest()
  # Shorten the hash by taking the first few characters.
  short_id = hashed_data[:5]
  return short_id

def convertScheduleToJson (df: pd.DataFrame, semName: str, semCode: str, path: str):
    courses = []
    prev_section = ""
    prev_course = ""

    for _, row in df.iterrows():
        # We're in a case where we have multiple sections (including recitations)
        if row["COURSE"] == prev_course:
            # Linked to the last course seen above
            section = {
                "section_type": "Recitation" if "Lec" in prev_section else "Lecture",
                "section_id": stdSec(row["SECTION"]),
                "timings": {
                    "days": [stdDays(row["DAY"])],
                    "begin": stdTime(row["BEGIN TIME"]),
                    "end": stdTime(row["END TIME"]),
                    "teaching_location": "Doha, Qatar",
                    "delivery_mode": "UNK",
                    "instructor": stdIns(row["INSTRUCTORS"])
                }
            }
            if  isinstance(row["SECTION"],int) and ("Lec" not in prev_section):
                courses[-1]["sections"][-1]["section_type"] = "Recitation"
                courses[-1]["sections"].insert(-1,section)
            else: 
                courses[-1]["sections"].append(section)
        else:
            # New course
            prev_section = stdSec(row["SECTION"])
            prev_course = row["COURSE"]
            course = {
                "course_code": stdCode(row["COURSE"]),
                "course_title": row["COURSE TITLE"],
                "units": str(row["UNITS"]),
                "description": "UNK",
                "prereqs": stdReqs(row["Pre-reqs"]),
                "coreqs": "UNK",
                "sections": [{
                    "section_type": "Lecture",
                    "section_id": stdSec(row["SECTION"]),
                    "timings": {
                        "days": [stdDays(row["DAY"])],
                        "begin": stdTime(row["BEGIN TIME"]),
                        "end": stdTime(row["END TIME"]),
                        "teaching_location": "Doha, Qatar",
                        "delivery_mode": "UNK",
                        "instructor": stdIns(row["INSTRUCTORS"])
                    }
                }]
            }
            courses.append(course)
    
    import datetime
    # Get the current date and time with timezone info
    now = datetime.datetime.now(datetime.timezone.utc)
    # Format the date and time as a string in ISO 8601 format with timezone
    formatted_now = now.isoformat()

    schedule_json = {
                "semester_name": semName, 
                "semester_shortcode": semCode,
                "last_update": formatted_now,
                "ID": generateShortID(semName+str(courses)+formatted_now),
                "courses": courses
                }
    json_data = json.dumps(schedule_json, indent=2)
    if path != None:
        with open(path, "w") as f:
            f.write(json_data)
    return schedule_json

if __name__ == "__main__":
    schedule, audit = read_infosilem_format("../data/schedules/2024b-fall-trial-mar15.xlsx")
    convertScheduleToJson(schedule,"Fall 2024b Trial","F24","../data/2024b-trial-schedule.json")
