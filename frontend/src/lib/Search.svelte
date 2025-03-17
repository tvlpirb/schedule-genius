<script>
  import { onMount } from 'svelte';
  import { flip } from 'svelte/animate';
  import { selectedScheduleID } from "../store.js";
  import CourseCard from "$lib/CourseCard.svelte";
  import { filterCourses, filterConflictingCourses } from "$lib/search";
  import { countsFor, getUniqueRequirements } from "$lib/audit.js";

  export let selectCourse;
  export let card;
  export let audit;
  export let courses;
  export let loadSchedule;

  let filteredCourses = [];
  let groupedCourses = new Map();

  let searchTerm = "";
  let searchTimeout;
  let showOverlay = false;
  let cacheCourses = courses;

  let filters = {
    keyword: [],
    countsFor: [],
    instructor: [],
    department: [],
    coursesTaken: new Set(card.courses_taken),
    units: [1, 18],
    clearedPreReqs: false,
    noConflicts: false // TODO Enabled for testing purposes only
  };

  async function refilterSchedule(selectedScheduleID) {
    try {
      courses = null;
      await loadSchedule(selectedScheduleID);
      refreshCache();
    } catch (error) {
      console.error("Error fetching schedule:", error);
    }
  }

  function groupCoursesByRequirement(coursesToGroup) {
    const uniqueRequirements = getUniqueRequirements(audit);
    const newGroupedCourses = new Map();

    // Get the set of selected course codes
    const selectedCourseCodes = getSelectedCourse();

    // Filter out selected courses
    const unselectedCourses = coursesToGroup.filter(course => !selectedCourseCodes.has(course.course_code));

    // Initialize the map with empty arrays for each requirement
    uniqueRequirements.forEach(requirement => {
      newGroupedCourses.set(requirement, []);
    });

    // Group unselected courses by their requirements
    unselectedCourses.forEach(course => {
      const requirements = countsFor(course.course_code, audit);
      requirements.forEach(requirement => {
        if (newGroupedCourses.has(requirement)) {
          newGroupedCourses.get(requirement).push(course);
        }
      });
    });

    // Filter out requirements with no courses
    groupedCourses = new Map([...newGroupedCourses.entries()].filter(([_, courses]) => courses.length > 0));
  }

  function orderedCourses(allCourses, selectedOnly = false) {
    const selectedCourseCodes = getSelectedCourse();
    const selected = courses.filter(course => selectedCourseCodes.has(course.course_code));
    const unselected = allCourses.filter(course => !selectedCourseCodes.has(course.course_code));
    if (selectedOnly) {
      return selected;
    }
    return unselected;
  }

  function selectCourseSearch(course) {
    selectCourse(course);
    refreshCache();
  }

  function refreshCache() {
    if (filters.noConflicts) {
      cacheCourses = filterConflictingCourses(courses, card.courses);
    } else {
      cacheCourses = courses;
    }
    filteredCourses = filterCourses(cacheCourses, filters, audit, card.courses);
    groupCoursesByRequirement(filteredCourses);
  }

  function toggleNoConflicts() {
    filters.noConflicts = !filters.noConflicts;
    refreshCache();
  }

  function searchCourses() {
    if (cacheCourses == null) {
      cacheCourses = courses;
    }
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      if (filters.keyword.length > 0) {
        filters.keyword[0] = searchTerm;
      } else {
        filters.keyword.push(searchTerm);
      }
      refreshCache();
    }, 100);
  }

  function getSelectedCourse() {
    return new Set(card.courses.map(course => course.course_code));
  }

  function courseSelected(course_code) {
    return card.courses.find(c => c.course_code === course_code);
  }

  function handleSearch(event) {
    searchTerm = event.target.value;
    searchCourses();
  }

  function clearSearch() {
    searchTerm = "";
    searchCourses();
    showOverlay = true;
  }

  let showRequirementsDropdown = false;

  function toggleRequirementFilter(requirement) {
    if (filters.countsFor.includes(requirement)) {
      filters.countsFor = filters.countsFor.filter(req => req !== requirement);
    } else {
      filters.countsFor = [...filters.countsFor, requirement];
    }
    refreshCache(); // Trigger search after updating filters
  }

  // Close dropdown when clicking outside
  function handleClickOutside(event) {
    if (!event.target.closest('.dropdown')) {
      showRequirementsDropdown = false;
    }
  }

  // Attach and detach the outside click handler
  if (typeof window !== 'undefined') {
    onMount(() => {
      window.addEventListener('click', handleClickOutside);
      return () => window.removeEventListener('click', handleClickOutside);
    });
  }

  $: refilterSchedule($selectedScheduleID);
</script>

<button
  class="btn btn-outline rounded-full border-gray-200 text-black min-h-2 h-9 text-bold text-base"
  on:click={clearSearch}>
  Search Courses
</button>

{#if showOverlay}
  <div class="modal modal-middle modal-open">
    <div class="modal-box max-w-7xl w-[90vw] relative">

      <button class="btn btn-sm btn-circle absolute top-4 right-4 z-20" on:click={() => showOverlay = false}>
        ✕
      </button>

      <!-- Two Pane Wrapper -->
      <div class="flex w-full gap-6">

        <!-- Left Pane: Searchable Courses -->
        <div class="w-1/2 flex flex-col">
          <div class="sticky top-0 z-10 bg-white w-full">
            {#if courses}
              <div class="filter-controls m-4 w-full">
                <input type="text" id="search-field" placeholder="Keywords, title, etc..."
                  autocomplete="off"
                  on:input={handleSearch}
                  class="input input-bordered w-full mb-4"
                />

                <div class="flex items-center gap-4">
                  <!-- Dropdown Menu for Requirements Filter -->
                  <div class="dropdown">
                    <button class="btn btn-outline" on:click={() => showRequirementsDropdown = !showRequirementsDropdown}>
                      Filter by Requirements
                    </button>
                    {#if showRequirementsDropdown}
                      <div class="dropdown-content bg-white shadow-lg rounded-lg p-4 mt-2 w-64 max-h-64 overflow-y-auto"
                        on:click|stopPropagation>
                        {#each getUniqueRequirements(audit) as requirement}
                          <label class="flex items-center gap-2 mb-2">
                            <input
                              type="checkbox"
                              checked={filters.countsFor.includes(requirement)}
                              on:change={() => toggleRequirementFilter(requirement)}
                              class="checkbox"
                            />
                            {requirement}
                          </label>
                        {/each}
                      </div>
                    {/if}
                  </div>

                  <!-- Hide Conflicts Checkbox -->
                  <label class="flex items-center gap-2">
                    <input type="checkbox" on:change={toggleNoConflicts}
                      bind:checked={filters.noConflicts} class="checkbox" />
                    Hide courses which conflict with current schedule
                  </label>
                </div>
              </div>

              <div class="header bg-sky-600 w-full border-b-2 border-gray-200">
                <div class="text-center">Course Code</div>
                <div>Title</div>
                <div>Units</div>
                <div>Section</div>
                <div>Day</div>
                <div>Begin</div>
                <div>End</div>
                <div>Room</div>
                <div>Instructor</div>
              </div>
            {/if}
          </div>

          <!-- Scrollable Course List -->
          <div class="overflow-y-auto pr-2" style="max-height: 60vh;">
            {#if courses}
              {#if filteredCourses.length > 0}
                {#each Array.from(groupedCourses.entries()) as [requirement, courses], index (requirement)}
                  <div class="requirement-card mt-3 px-2 py-2 rounded-lg shadow-md bg-lime-100">
                    <h3 class="text-lg font-bold mb-2">{requirement}</h3>
                    {#each courses as course, i (course.course_code)}
                      <div class="course-card-wrapper mt-3 px-2 py-2 rounded-lg shadow-md
                        {i % 2 === 0 ? 'bg-gray-300' : 'bg-white'}"
                        animate:flip={{ duration: 300 }}>
                        <CourseCard {course} {selectCourseSearch} countsFor={countsFor(course.course_code, audit)} />
                      </div>
                    {/each}
                  </div>
                {/each}
              {:else}
                <div class="text-center text-gray-500 mt-4">No courses match your search.</div>
              {/if}
            {:else}
              Please select a schedule at the top before proceeding...
            {/if}
          </div>
        </div>

        <!-- Right Pane: Selected Courses -->
        <div class="w-1/2 flex flex-col border-l border-gray-300 pl-6">
          <h3 class="text-lg font-bold text-center mb-4">Selected Courses</h3>
          <div class="overflow-y-auto pr-2" style="max-height: 70vh;">
            {#if filteredCourses.length > 0}
              {#each orderedCourses(filteredCourses, true) as course, index (course.course_code)}
                <div class="course-card-wrapper mt-3 px-2 py-2 rounded-lg shadow-md
                  {index % 2 === 0 ? 'bg-gray-300' : 'bg-white'}"
                  animate:flip={{ duration: 300 }}>
                  <CourseCard {course} {selectCourseSearch} countsFor={countsFor(course.course_code, audit)} />
                </div>
              {/each}
            {/if}
          </div>
        </div>

      </div>
    </div>
  </div>
{/if}

<style>
  .header, .course-card-wrapper {
    display: grid;
    grid-template-columns: repeat(9, 1fr);
    gap: 0;
    width: 100%;
    border: 1px solid black;
    border-radius: 8px;
    overflow: hidden;
    font-size: 0.85em;
  }

  .header > div {
    border: 1px solid #ccc;
    padding: 8px;
  }

  .selected {
    background-color: #3b82f6;
  }
  
  .dropdown {
    position: relative;
    display: inline-block;
  }

  .dropdown-content {
    position: absolute;
    z-index: 1000;
    border: 1px solid #ccc;
  }

  .dropdown-content {
    max-height: 30rem; /* Adjust height as needed */
    overflow-y: auto;
    scrollbar-width: thin; /* For better scrollbar styling */
    scrollbar-color: #ccc #f1f1f1; /* For better scrollbar styling */
  }

  .dropdown-content label {
    display: block;
    padding: 8px;
    cursor: pointer;
  }

  .dropdown-content label:hover {
    background-color: #f1f1f1;
  }
</style>
