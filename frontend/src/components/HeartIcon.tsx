type Props = {
  filled?: boolean;
};

export function HeartIcon({ filled = false }: Props) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 20.5s-6.4-4.1-8.8-7.7C1.2 10.2 1.7 6.8 4.4 5.4c2-.9 4.1-.4 5.6 1.4L12 9.2l2-2.4c1.5-1.8 3.6-2.3 5.6-1.4 2.7 1.4 3.2 4.8 1.2 7.4-2.4 3.6-8.8 7.7-8.8 7.7z"
        fill={filled ? "currentColor" : "none"}
        stroke="currentColor"
        strokeWidth="1.8"
        strokeLinejoin="round"
      />
    </svg>
  );
}
