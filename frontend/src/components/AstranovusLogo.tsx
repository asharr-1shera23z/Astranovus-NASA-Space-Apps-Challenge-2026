interface AstranovusLogoProps {
  compact?: boolean;
}

export function AstranovusLogo({ compact = false }: AstranovusLogoProps) {
  return (
    <span className="inline-flex items-center gap-2.5 select-none">
      <svg
        width="38"
        height="38"
        viewBox="0 0 64 64"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        aria-hidden="true"
        className="shrink-0"
      >
        <defs>
          <linearGradient id="an-delta-grad" x1="12" y1="10" x2="52" y2="52" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#1E4B8F" />
            <stop offset="55%" stopColor="#142B50" />
            <stop offset="100%" stopColor="#0F2242" />
          </linearGradient>
          <linearGradient id="an-ocean-grad" x1="20" y1="32" x2="37" y2="50" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#38BDF8" />
            <stop offset="55%" stopColor="#0B5ED7" />
            <stop offset="100%" stopColor="#1E3A8A" />
          </linearGradient>
          <linearGradient id="an-orbit-grad" x1="10" y1="49" x2="54" y2="21" gradientUnits="userSpaceOnUse">
            <stop offset="0%" stopColor="#0B5ED7" />
            <stop offset="50%" stopColor="#38BDF8" />
            <stop offset="100%" stopColor="#0EA5E9" />
          </linearGradient>
          <clipPath id="an-earth-clip">
            <circle cx="29" cy="40.5" r="8.8" />
          </clipPath>
        </defs>

        {/* Back orbital arc passing behind the A-delta */}
        <path
          d="M 6 36 A 26 7.5 0 0 1 58 36"
          transform="rotate(-31 32 36)"
          stroke="#54B9F5"
          strokeWidth="2"
          strokeLinecap="round"
          opacity="0.72"
        />

        {/* Geometric aerospace A-delta with continuous legs */}
        <path
          d="M 11 51 L 29.3 11.8 C 30.6 9.0 33.4 9.0 34.7 11.8 L 53 51 L 45.8 51 L 32 21.2 L 18.2 51 Z"
          fill="url(#an-delta-grad)"
        />

        {/* Earth sphere nestled cleanly inside the A-delta */}
        <circle cx="29" cy="40.5" r="10" fill="#FFFFFF" />
        <g clipPath="url(#an-earth-clip)">
          <circle cx="29" cy="40.5" r="8.8" fill="url(#an-ocean-grad)" />
          <path
            d="M 22.5 36.2 C 24.5 34.6 27 35.4 27.8 37.2 C 28.4 38.6 26.4 40.4 27.1 42.4 C 27.8 44.2 29.6 45.6 29.1 47.8 C 25 47.8 21.4 44.4 21.1 39.8 C 21 38.4 21.6 37 22.5 36.2 Z"
            fill="#4ADE80"
          />
          <path
            d="M 31.8 34.2 C 34.4 34.8 36.6 37 37.1 39.8 C 35.6 40.6 33.8 40.3 32.8 39 C 31.8 37.6 31.1 35.7 31.8 34.2 Z"
            fill="#4ADE80"
          />
          <path
            d="M 32.2 42.6 C 33.9 42.1 35.4 43.1 35.6 44.8 C 34.2 46.2 32.6 46.9 31.2 46.1 C 30.9 44.8 31.2 43.3 32.2 42.6 Z"
            fill="#86EFAC"
          />
        </g>

        {/* Front orbital trajectory arc sweeping cleanly across Earth and A-delta */}
        <path
          d="M 58 36 A 26 7.5 0 0 1 6 36"
          transform="rotate(-31 32 36)"
          stroke="#FFFFFF"
          strokeWidth="4.2"
          strokeLinecap="round"
          opacity="0.88"
        />
        <path
          d="M 58 36 A 26 7.5 0 0 1 6 36"
          transform="rotate(-31 32 36)"
          stroke="url(#an-orbit-grad)"
          strokeWidth="2.5"
          strokeLinecap="round"
        />

        {/* Crisp 4-point orbital beacon star anchored on the upper-right orbit */}
        <path
          d="M 53 18.1 L 53.8 20.8 L 56.5 21.6 L 53.8 22.4 L 53 25.1 L 52.2 22.4 L 49.5 21.6 L 52.2 20.8 Z"
          fill="#0B5ED7"
        />
      </svg>
      {!compact && (
        <span className="font-display font-extrabold tracking-[0.05em] text-[17px] text-[#142B50] whitespace-nowrap">
          ASTRANOVUS
        </span>
      )}
    </span>
  );
}
