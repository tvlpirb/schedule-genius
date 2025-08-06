import React, { useLayoutEffect, useRef, useState } from "react";


const ScheduleCard = () => {
  const [value, setValue] = useState("");
  const spanRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useLayoutEffect(() => {
    if (spanRef.current && inputRef.current) {
      const spanWidth = spanRef.current.offsetWidth;
      inputRef.current.style.width = `${Math.min(
        Math.max(spanWidth + 4, 100), // min width
        300 // max width
      )}px`;
    }
  }, [value])

  return (
    <div className="card bg-base-300 m-3 shadow">
      <div className="card-body">
        {/* Header row with title and close button */}
        <div className="flex justify-between items-center"> {/* Added flex container */}
          <label className="flex items-center px-1 py-2 border rounded-lg input-ghost card-title validator">
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                value={value}
                onChange={(e) => setValue(e.target.value)}
                required
                placeholder="No name"
                className="bg-transparent outline-none absolute top-0 left-0"
                style={{ minWidth: '100px', maxWidth: '300px' }}
              />
              {/* This span will mirror the input */}
              <span
                ref={spanRef}
                className="invisible whitespace-pre px-1"
                aria-hidden="true"
              >
                {value || 'No name'}
              </span>
            </div>
            <svg
              className="h-[1em] opacity-50 shrink-0"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 1024 1024"
            >
              <g
                strokeLinejoin="round"
                strokeLinecap="round"
                strokeWidth="60"
                fill="none"
                stroke="currentColor"
              >
                <path d="M0.1 1024l98.59-295.77 565.645-565.645 197.18 197.18-565.645 565.645L0.1 1024z m125.588-225.878l-38.596 116.188 22.798 22.798 117.188-37.596m33.197-11.399l9.799-4.4 523.949-523.948-33.725-33.726-523.949 523.949-2.6 11.599M882.314 337.367L686.733 141.786 828.419 0.1l195.581 195.581-141.686 141.686zM754.226 141.786l128.087 128.187 74.193-74.193-128.088-128.187-74.192 74.193z" />
                <path d="M183.213 766.736l460.914-460.913 33.725 33.726-460.914 460.913z" />
              </g>
            </svg>
          </label>
          <p className="validator-hint">
            Must be 1 character at least
          </p>
          <div className="card-actions">
            <button className="btn btn-square btn-sm">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-6 w-6"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>
        <p>We are using cookies for no reason.</p>
      </div>
    </div>
  );
}

export default ScheduleCard;
