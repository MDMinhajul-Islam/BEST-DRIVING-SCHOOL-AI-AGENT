export function RoadVisual() {
  return (
    <svg
      className="road-visual"
      viewBox="0 0 1200 800"
      fill="none"
      aria-hidden="true"
    >
      <defs>
        <linearGradient
          id="road"
          x1="200"
          y1="800"
          x2="900"
          y2="200"
          gradientUnits="userSpaceOnUse"
        >
          <stop stopColor="#1c496b" stopOpacity=".5" />
          <stop offset="1" stopColor="#173653" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path
        d="M50 850C140 400 880 780 820 360S1100 280 1250 100"
        stroke="url(#road)"
        strokeWidth="150"
      />
      <path
        d="M50 850C140 400 880 780 820 360S1100 280 1250 100"
        stroke="#85a4bd"
        strokeOpacity=".18"
        strokeWidth="2"
        strokeDasharray="18 24"
      />
      <path
        d="M-25 850C80 350 790 710 750 360"
        stroke="#b9cbd9"
        strokeOpacity=".12"
      />
      <path
        d="M125 850C230 440 960 860 895 380"
        stroke="#b9cbd9"
        strokeOpacity=".12"
      />
      <path d="M240 662l26-5M290 655l26-3" stroke="#D92F3D" strokeWidth="3" />
    </svg>
  );
}
