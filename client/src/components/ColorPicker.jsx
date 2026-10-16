import { CHOOSABLE_COLORS, COLOR_NAMES } from "../cards";

export default function ColorPicker({ onPick, onCancel }) {
  return (
    <div className="overlay" role="dialog" aria-modal="true" aria-label="Choose a color">
      <div className="panel panel--glass color-picker">
        <h2>Choose the next color</h2>
        <div className="color-picker__options">
          {CHOOSABLE_COLORS.map((color) => (
            <button
              key={color}
              type="button"
              className={`swatch swatch--${color}`}
              onClick={() => onPick(color)}
            >
              {COLOR_NAMES[color]}
            </button>
          ))}
        </div>
        <button type="button" className="button button--quiet" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
}
