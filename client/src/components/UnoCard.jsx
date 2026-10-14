import { cardName, isWild } from "../cards";

function SkipIcon() {
  return (
    <svg viewBox="0 0 24 24" className="icon" aria-hidden="true">
      <circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" strokeWidth="3.2" />
      <line x1="6.3" y1="17.7" x2="17.7" y2="6.3" stroke="currentColor" strokeWidth="3.2" strokeLinecap="round" />
    </svg>
  );
}

function ReverseIcon() {
  return (
    <svg viewBox="0 0 24 24" className="icon" aria-hidden="true">
      <path d="M4 9h12l-3-3.2" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
      <path d="M20 15H8l3 3.2" fill="none" stroke="currentColor" strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function WildMark() {
  return (
    <svg viewBox="0 0 24 24" className="icon icon--wild" aria-hidden="true">
      <path d="M12 12V2.5a9.5 9.5 0 0 1 9.5 9.5z" fill="var(--red)" />
      <path d="M12 12h9.5A9.5 9.5 0 0 1 12 21.5z" fill="var(--blue)" />
      <path d="M12 12v9.5A9.5 9.5 0 0 1 2.5 12z" fill="var(--green)" />
      <path d="M12 12H2.5A9.5 9.5 0 0 1 12 2.5z" fill="var(--yellow)" />
    </svg>
  );
}

function face(card) {
  switch (card.card_type) {
    case "number":
      return { center: card.value, corner: card.value };
    case "skip":
      return { center: <SkipIcon />, corner: <SkipIcon /> };
    case "reverse":
      return { center: <ReverseIcon />, corner: <ReverseIcon /> };
    case "draw_two":
      return { center: "+2", corner: "+2" };
    case "wild":
      return { center: <WildMark />, corner: "W" };
    case "wild_draw_four":
      return { center: "+4", corner: "+4" };
    default:
      return { center: "?", corner: "?" };
  }
}

export default function UnoCard({
  card,
  back = false,
  playable = false,
  dimmed = false,
  onClick,
  size = "md",
  style,
  label,
}) {
  if (back) {
    return (
      <span className={`card card--back card--${size}`} style={style} aria-hidden="true">
        <span className="card__oval" />
      </span>
    );
  }

  const { center, corner } = face(card);
  const wild = isWild(card);
  const classes = [
    "card",
    `card--${size}`,
    `card--${wild ? "wild" : card.color}`,
    card.card_type === "wild_draw_four" ? "card--plus-four" : "",
    playable ? "card--playable" : "",
    dimmed ? "card--dimmed" : "",
  ]
    .filter(Boolean)
    .join(" ");

  const description = label || `${cardName(card)}${playable ? ", playable" : ""}`;
  const content = (
    <>
      <span className="card__corner card__corner--tl">{corner}</span>
      <span className="card__oval">
        <span className="card__center">{center}</span>
      </span>
      <span className="card__corner card__corner--br">{corner}</span>
    </>
  );

  if (onClick) {
    return (
      <button type="button" className={classes} style={style} onClick={onClick} aria-label={description}>
        {content}
      </button>
    );
  }
  return (
    <span className={classes} style={style} role="img" aria-label={description}>
      {content}
    </span>
  );
}
