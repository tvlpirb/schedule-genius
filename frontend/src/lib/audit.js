/**
 * @typedef {import('./types').RequirementAndCourseArray} RequirementAndCourseArray
 */

/**  
 * Extract what requirements a course satisfies
 *
 * @param {string} course_number
 * @param {RequirementAndCourseArray} audit 
 * @returns {Set} - Containing all the requirements that it satisfies for 
 * the given audit
 */
export function countsFor(course_number, audit) {
    // In the event that an audit isn't loaded, we should just return an empty set 
    if (!audit){
      return new Set([]);
    }
  
    let include_course = new Set(
        audit.filter(
            row => row.Type === "Course" && row["Course or code"] === course_number && row["Inclusion/Exclusion"] === "Inclusion"
        ).map(row => row.Requirement)
    );

    let include_code = new Set(
        audit.filter(
            row => row.Type === "Code" && row["Course or code"] === course_number.slice(0, 2) && row["Inclusion/Exclusion"] === "Inclusion"
        ).map(row => row.Requirement)
    );

    let exclude_course = new Set(
        audit.filter(
            row => row.Type === "Course" && row["Course or code"] === course_number && row["Inclusion/Exclusion"] === "Exclusion"
        ).map(row => row.Requirement)
    );

    let intersection = [...include_course].filter(req => exclude_course.has(req));
    if (intersection.length > 0) {
        throw new Error("Course cannot be included and excluded for the same requirement");
    }

    let counts_for = new Set([...include_course, ...include_code].filter(req => !exclude_course.has(req)));

    return counts_for;
}


/**  
 * Extract what requirements a course satisfies
 *
 * @param {RequirementAndCourseArray} audit 
 * @returns {Set} -
 * the given audit
 */
export function getUniqueRequirements(audit) {
  if (!audit || audit.length === 0) return [];
  return audit[0]; // The first element of the audit array is the list of unique requirements
}
