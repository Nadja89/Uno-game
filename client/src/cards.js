export const COLOR_NAMES = {
  red: "Red",
  yellow: "Yellow",
  green: "Green",
  blue: "Blue",
  wild: "Wild",
};

export const CHOOSABLE_COLORS = ["red", "yellow", "green", "blue"];

export function sameCard(a, b) {
  return a.color === b.color && a.card_type === b.card_type && a.value === b.value;
}

export function isWild(card) {
  return card.card_type === "wild" || card.card_type === "wild_draw_four";
}

export function cardLabel(card) {
  switch (card.card_type) {
    case "number":
      return String(card.value);
    case "skip":
      return "Skip";
    case "reverse":
      return "Reverse";
    case "draw_two":
      return "Draw two";
    case "wild":
      return "Wild";
    case "wild_draw_four":
      return "Wild draw four";
    default:
      return card.card_type;
  }
}

export function cardName(card) {
  if (isWild(card)) return cardLabel(card);
  return `${COLOR_NAMES[card.color]} ${cardLabel(card)}`.toLowerCase().replace(/^./, (c) => c.toUpperCase());
}
