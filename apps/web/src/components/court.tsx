"use client";
// Programmatic motion illustration, never a claimed recording or MediaPipe result.
export function Court({
  time = 0,
  compact = false,
}: {
  time?: number;
  compact?: boolean;
}) {
  const phase = time * 2.2,
    armX = 356 + Math.sin(phase) * 65,
    armY = 182 + Math.cos(phase) * 23;
  return (
    <svg
      className="court-svg"
      viewBox="0 0 640 360"
      role="img"
      aria-label="Programmatic tennis movement illustration"
    >
      <defs>
        <linearGradient id="court-gradient" x1="0" y1="0" x2="1" y2="1">
          <stop stopColor="#183f39" />
          <stop offset="1" stopColor="#122723" />
        </linearGradient>
        <radialGradient id="court-glow">
          <stop stopColor="#62ddbe" stopOpacity=".13" />
          <stop offset="1" stopColor="#62ddbe" stopOpacity="0" />
        </radialGradient>
      </defs>
      <rect width="640" height="360" fill="#101a19" />
      <ellipse cx="350" cy="240" rx="280" ry="160" fill="url(#court-glow)" />
      <path
        d="M145 70H500L620 335H20Z"
        fill="url(#court-gradient)"
        stroke="#6a9e8c"
        strokeWidth="1.2"
      />
      <g fill="none" stroke="#8cbaaa" strokeOpacity=".4" strokeWidth="1">
        <path d="M180 70L82 335M465 70L552 335M95 170H545M58 250H582M320 70V335" />
        <path
          d="M170 90H477M158 115H488M142 145H502M106 205H530M86 230H550M52 280H581M37 307H601"
          strokeOpacity=".1"
        />
      </g>
      <path d="M98 169H544" stroke="#a9c3b6" strokeWidth="3" />
      <path d="M98 169V192M544 169V192" stroke="#729c88" />
      <ellipse cx="335" cy="300" rx="51" ry="12" fill="#000" opacity=".3" />
      <path
        d="M290 199Q370 98 441 198"
        fill="none"
        stroke="#edb66c"
        strokeWidth="1.3"
        strokeDasharray="4 6"
        opacity=".7"
      />
      <path
        d="M296 213Q360 137 413 202"
        fill="none"
        stroke="#5be0bf"
        strokeWidth="12"
        strokeLinecap="round"
        opacity=".06"
      />
      <g
        fill="none"
        stroke="#c3e7da"
        strokeWidth="8"
        strokeLinecap="round"
        strokeLinejoin="round"
      >
        <path d="M326 164L320 219L299 253L288 295M320 219L346 255L368 292" />
        <path d={`M326 173L350 194L${armX} ${armY}`} />
        <path d="M326 174L303 193L280 182" />
      </g>
      <circle cx="330" cy="144" r="14" fill="#c3e7da" />
      <g fill="#45d6b2" stroke="#0b2520" strokeWidth="2">
        {[
          [326, 174],
          [320, 219],
          [299, 253],
          [346, 255],
          [288, 295],
          [368, 292],
          [350, 194],
          [armX, armY],
          [303, 193],
          [280, 182],
        ].map(([x, y], i) => (
          <circle key={i} cx={x} cy={y} r="4" />
        ))}
      </g>
      <ellipse
        cx={armX + 18}
        cy={armY - 14}
        rx="11"
        ry="20"
        transform={`rotate(35 ${armX + 18} ${armY - 14})`}
        fill="none"
        stroke="#e9b66b"
        strokeWidth="2"
      />
      <path
        d={`M${armX} ${armY}L${armX + 10} ${armY - 5}`}
        stroke="#e9b66b"
        strokeWidth="3"
      />
      {!compact && (
        <g fontFamily="monospace" fontSize="9" fill="#7caaa0">
          <text x="22" y="28">
            ILLUSTRATED MOTION / NO RECORDED ATHLETE
          </text>
          <text x="22" y="344">
            RALLYSENSE LAB
          </text>
          <text x="508" y="344">
            LOCAL STUDY / 01
          </text>
        </g>
      )}
    </svg>
  );
}
