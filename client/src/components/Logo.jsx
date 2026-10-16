export default function Logo({ size = "md" }) {
  return (
    <span className={`logo logo--${size}`} role="img" aria-label="UNO">
      <span className="logo__oval" aria-hidden="true">
        <span className="logo__word">UNO</span>
      </span>
    </span>
  );
}
