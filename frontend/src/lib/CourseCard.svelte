<script>
  import CourseOverlay from './CourseOverlay.svelte';
  
  export let course;
  export let selectCourseSearch;
  export let countsFor;
  
  let hovered = false;
  let hoverTimeout;

  function handleMouseEnter() {
    hoverTimeout = setTimeout(() => {
      hovered = true;
    }, 1000); 
  }

  function handleMouseLeave() {
    clearTimeout(hoverTimeout); 
    hovered = false;
  }
</script>

<div on:click={() => selectCourseSearch(course)}
     class="course-card relative">
  
  <!-- Course information displayed on the card -->
  {#each course.sections as section, i (section)}
    {#if i === 0}
      <div class="text-center">{course.course_code}</div>
      <div>{course.course_title}</div>
      <div>{course.units}</div>
    {:else}
      <div></div>
      <div></div>
      <div></div>
    {/if}
    <div>{section.section_id}</div>
    <div>{section.timings.days.join(', ')}</div>
    <div>{section.timings.begin}</div>
    <div>{section.timings.end}</div>
    <div>{section.timings.teaching_location}</div>
    <div>{section.timings.instructor.join(', ')}</div>
  {/each}
  
  <div class="col-span-full">
    <label class="text-gray-700 mr-2">Counts for:</label> 
    {#each countsFor as count (count)}
      <button class="text-black bg-yellow-100 rounded-full ml-2 p-1 px-2 hover:bg-red-200">
        {count}
      </button>
    {/each}
  </div>
  
  <!-- Overlay component displayed on hover -->
  {#if hovered}
    <CourseOverlay 
      description={course.description}
      prereqs={course.prereqs}
      coreqs={course.coreqs} />
  {/if}
</div>

<style>
  .course-card {
    display: contents;
    position: relative;
  }

  .course-card > div {
    padding: 8px;
  }
</style>

