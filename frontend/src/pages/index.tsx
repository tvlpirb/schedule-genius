import Navbar from '@/components/Navbar';
import ScheduleCard from '@/components/ScheduleCard';
import React from 'react';

export default function Home() {
  return (
    <div className="app-body">
      <header>
        <Navbar></Navbar>
      </header>
      <main>
        <div className='cards-container'>
          <ScheduleCard></ScheduleCard>
        </div>
      </main >
      <footer className="app-footer">
        <p>Made with ❤️ for <a href="https://github.com/open-cmuq">Open-CMUQ</a></p>
        <p>
          <span>&copy; {new Date().getFullYear()} MIT License</span>
          <a href="https://github.com/open-cmuq/schedule-genius" target="_blank">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" aria-label="GitHub">
              <path d="M12 .5C5.73.5.5 5.73.5 12c0 5.08 3.29 9.39 7.86 10.92.58.1.79-.25.79-.56v-2.17c-3.2.7-3.87-1.42-3.87-1.42-.52-1.32-1.28-1.67-1.28-1.67-1.05-.72.08-.71.08-.71 1.16.08 1.78 1.2 1.78 1.2 1.03 1.77 2.7 1.26 3.36.97.1-.74.4-1.26.72-1.55-2.56-.29-5.26-1.28-5.26-5.67 0-1.25.44-2.27 1.16-3.07-.12-.29-.5-1.46.1-3.04 0 0 .96-.31 3.15 1.18.91-.25 1.89-.37 2.86-.37s1.95.12 2.86.37c2.18-1.5 3.15-1.18 3.15-1.18.6 1.58.22 2.75.1 3.04.72.8 1.16 1.82 1.16 3.07 0 4.4-2.7 5.38-5.26 5.67.42.36.76 1.08.76 2.17v3.22c0 .31.21.66.8.56A10.51 10.51 0 0023.5 12c0-6.27-5.23-11.5-11.5-11.5z" />
            </svg>
          </a>
        </p>
      </footer>
    </div >
  );
}
