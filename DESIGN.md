---
name: Crypto Narrative Report
description: A central-bank policy report for crypto news narratives and sentiment, read point-in-time against price.
colors:
  bar: "#0b2545"
  bar-ink: "#ffffff"
  bar-muted: "#b9c8d9"
  ink: "#0b2545"
  ink-2: "#3d5675"
  muted: "#5b708a"
  accent: "#13315c"
  focus: "#2a78d6"
  page: "#ffffff"
  panel: "#f5f8fb"
  surface: "#ffffff"
  rule: "#d6dee7"
  grid: "#e8edf2"
  band-valid: "rgba(141, 169, 196, 0.16)"
  band-test: "rgba(141, 169, 196, 0.32)"
  neg: "#c0392b"
  pos: "#1f7a3a"
  st-good: "#0ca30c"
  st-serious: "#ec835a"
  st-critical: "#d03b3b"
  s1: "#2a78d6"
  s2: "#eb6834"
  s3: "#1baf7a"
  s4: "#eda100"
  s5: "#e87ba4"
  s6: "#008300"
  s7: "#6250d6"
  s8: "#0f8fa8"
  page-dark: "#0f1b2d"
  panel-dark: "#16263d"
  surface-dark: "#0f1b2d"
  bar-dark: "#13315c"
  bar-ink-dark: "#e6edf5"
  bar-muted-dark: "#8ea3bb"
  ink-dark: "#e6edf5"
  ink-2-dark: "#c1cfdf"
  muted-dark: "#93a6bd"
  rule-dark: "#23344b"
  grid-dark: "#1a2a40"
  accent-dark: "#8db4e2"
  focus-dark: "#6aa6ef"
  neg-dark: "#ef7b6d"
  pos-dark: "#5cc27a"
  band-valid-dark: "rgba(141, 169, 196, 0.14)"
  band-test-dark: "rgba(141, 169, 196, 0.28)"
  s1-dark: "#3987e5"
  s2-dark: "#d95926"
  s3-dark: "#199e70"
  s4-dark: "#c98500"
  s5-dark: "#d55181"
  s6-dark: "#008300"
  s7-dark: "#9085e9"
  s8-dark: "#1aa3bd"
typography:
  display:
    fontFamily: "'Source Serif 4', Georgia, serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: 1.25
    letterSpacing: "-0.01em"
  brand:
    fontFamily: "'Source Serif 4', Georgia, serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.2
  headline:
    fontFamily: "'Source Serif 4', Georgia, serif"
    fontSize: "17px"
    fontWeight: 600
    lineHeight: 1.3
  title:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "20px"
    fontWeight: 600
    lineHeight: 1.15
    fontFeature: "tnum"
  body:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  judgement:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: 1.5
  label:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: 1.5
  caption:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.5
  axis:
    fontFamily: "'Source Sans 3', system-ui, -apple-system, 'Segoe UI', sans-serif"
    fontSize: "11px"
    fontWeight: 400
    fontFeature: "tnum"
rounded:
  hairline: "2px"
  control: "4px"
  float: "6px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "16px"
  xl: "24px"
  gutter: "28px"
  page: "32px"
  end: "64px"
components:
  topbar:
    backgroundColor: "{colors.bar}"
    textColor: "{colors.bar-ink}"
    typography: "{typography.brand}"
    height: "60px"
    padding: "0 32px"
  section-tab:
    textColor: "{colors.bar-muted}"
    typography: "{typography.body}"
    padding: "18px 10px 16px"
  section-tab-current:
    textColor: "{colors.bar-ink}"
  bar-toggle:
    textColor: "{colors.bar-muted}"
    rounded: "{rounded.control}"
    padding: "5px 10px"
  bar-toggle-pressed:
    backgroundColor: "{colors.bar-ink}"
    textColor: "{colors.bar}"
  range-chip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.control}"
    padding: "6px 12px"
  range-chip-hover:
    backgroundColor: "{colors.panel}"
  range-chip-pressed:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.page}"
  judgements-column:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
    width: "320px"
    padding: "28px"
  metric:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.title}"
    padding: "12px"
  exhibit-title:
    textColor: "{colors.ink}"
    typography: "{typography.headline}"
  exhibit-judgement:
    textColor: "{colors.ink-2}"
    typography: "{typography.judgement}"
  exhibit-source:
    textColor: "{colors.muted}"
    typography: "{typography.caption}"
  view-toggle:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "3px 9px"
  view-toggle-pressed:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink}"
  tooltip:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.caption}"
    rounded: "{rounded.float}"
    padding: "8px 10px"
  table-header:
    backgroundColor: "{colors.panel}"
    textColor: "{colors.ink-2}"
    padding: "6px 10px"
  table-cell:
    textColor: "{colors.ink}"
    typography: "{typography.label}"
    padding: "6px 10px"
  empty-state:
    textColor: "{colors.muted}"
    rounded: "{rounded.control}"
    padding: "24px"
---

# Design System: Crypto Narrative Report

## Overview

**Creative North Star: "The Monetary Policy Report"**

The dashboard reads like a central bank's quarterly report, not a trading terminal. A navy masthead carries the report name, the section contents as tabs, and the language and theme switches. Below it, white report paper holds numbered exhibits. Each exhibit has a heavy rule on top, a serif title prefixed with its number ("Exhibit 1.2"), a one-line method subtitle, the figure, one sentence of judgement on what the figure means, and a small source line. The landing view leads with a 320px "Key judgements" column: plain sentences first, the supporting metrics stacked under them.

Density is moderate and document-like. Exhibits sit in a two-column grid with generous gutters and no boxes around them; separation comes from the top rule and white space, not from cards. The one recurring piece of chart furniture is the projection band: every time axis shades the validation period and, darker, the out-of-sample test period in pale mist, the way a policy report shades its forecast horizon. Colour lives in the data. The chrome stays navy, white, and grey.

The system rejects the crypto-dashboard default of a KPI tile grid with unexplained charts. A figure never ships without its sentence and its source.

**Key Characteristics:**
- Navy masthead, white paper, navy ink; dark mode turns to night navy with pale ink.
- Numbered exhibits with a 3px ink top rule, serif title, judgement sentence, source line.
- A Figure/Table switch on every exhibit, so every chart has a table behind it.
- Valid/test projection bands on every time axis.
- Eight fixed categorical series slots, re-tuned for dark mode.
- Flat paper: one shadow in the whole system, on the floating tooltip.

## Colors

The palette is a restrained navy-and-paper report with a separate, saturated data palette that appears only inside figures.

### Primary
- **Report Navy** (#0b2545): the masthead background and the body ink. In dark mode the masthead lifts to **Policy Navy** (#13315c) and the page drops to **Night Navy** (#0f1b2d).
- **Deep Ink Navy** (#13315c): the accent. It fills pressed range chips, colours links and text selection, and draws the forecast line and fan bands. Dark mode swaps it to **Pale Signal Blue** (#8db4e2).
- **Focus Blue** (#2a78d6): the 2px keyboard focus outline, offset 2px. It is never used as decoration.

### Secondary (data series)
- **Series slots s1 to s8**: Clear Blue (#2a78d6), Ember Orange (#eb6834), Jade (#1baf7a), Amber (#eda100), Rose (#e87ba4), Field Green (#008300), Violet (#6250d6), Teal (#0f8fa8). Each slot has its own dark-mode value (the `-dark` tokens). Narratives take slots in the fixed order of the narrative list, so a narrative keeps its colour in every exhibit, legend, snippet tag, and tooltip.

### Tertiary (signal)
- **Risk Red** (#c0392b, dark #ef7b6d): negative sentiment scores and the dashed neg_sent line.
- **Gain Green** (#1f7a3a, dark #5cc27a): positive sentiment scores.
- **Status scale**: good (#0ca30c), serious (#ec835a), critical (#d03b3b). These colour the BTC volatility-risk marker only.

### Neutral
- **Paper** (#ffffff): page and surface in light mode.
- **Mist Panel** (#f5f8fb, dark #16263d): the Key judgements column, table headers, hover fills, the pressed Figure/Table button.
- **Slate Ink** (#3d5675): secondary text, judgement sentences, legend labels.
- **Steel Muted** (#5b708a): subtitles, sources, axis labels, metric labels, exhibit numbers.
- **Hairline Rule** (#d6dee7): borders, dividers, chart baselines.
- **Grid Whisper** (#e8edf2): chart gridlines and table row dividers. It is lighter than the rule on purpose.
- **Mist bands** (mist #8da9c4 at 16% for valid and 32% for test; 14% and 28% in dark mode): the projection-band shading.

### Named Rules
**The Red Means Bad News Rule.** Red is used only for negative sentiment and critical risk. No series slot is red, and the volatility series is drawn in Ember Orange, not red.

**The Fixed Slot Rule.** Series colours are assigned by stable index (s1 to s8), never by rank or by what happens to be on screen. A ninth category goes to muted grey, not to a new hue.

**The Ink Chrome Rule.** Chrome (masthead, rules, chips, toggles) uses only navy, paper, and neutrals. Saturated colour appears only inside figures, legends, and the tags that point to them.

## Typography

**Display Font:** Source Serif 4 (with Georgia, serif), weight 600 only
**Body Font:** Source Sans 3 (with system-ui, -apple-system, Segoe UI, sans-serif), weights 400 and 600
Both are self-hosted through Fontsource.

**Character:** The serif carries the report's voice: the masthead name, the Key judgements heading, and the exhibit titles. The sans carries every number, label, and control, in tabular figures, so columns of numbers line up on a projector.

### Hierarchy
- **Display** (600, 24px, 1.25, -0.01em, serif): the Key judgements heading. Prose pages use the same face at 26px.
- **Brand** (600, 18px, 1.2, serif): the masthead name, with a 12px sans subline in bar-muted.
- **Headline** (600, 17px, 1.3, serif): exhibit titles. The exhibit number before the title is sans 600 14px in muted.
- **Title** (600, 20px, 1.15, sans, tabular): metric values in the judgements column, with a 12px muted note below.
- **Body** (400, 15px, 1.5, sans): judgement bullets, tabs, and running text. Prose is capped at 75ch.
- **Judgement** (400, 14px, sans, ink-2): the one-sentence reading under each figure, capped at 75ch.
- **Label** (400, 13px, sans): exhibit subtitles, filter labels, table cells, coverage text.
- **Caption** (400, 12px, sans): source lines, legends, metric labels, tooltips, snippet timestamps.
- **Axis** (400, 11px, sans, tabular): chart tick labels and end-of-line value labels.

### Named Rules
**The Serif Speaks, Sans Counts Rule.** Use the serif only for titles that name a part of the report. Every number, label, and control is in sans.

**The Tabular Figures Rule.** All numbers (metrics, axes, tables, timestamps) use `font-variant-numeric: tabular-nums`.

## Layout

The page is a centred 1440px column with 32px side padding and 64px of bottom padding. Under the masthead, a filter row (range chips, band legend, data-coverage count pushed to the right) sits on a hairline bottom rule.

The landing view is a two-column report grid: a 320px Mist Panel judgements column on the left, with a hairline right border and 28px padding, and the exhibits on the right. Exhibits use a two-column grid with a 32px row gap and a 28px column gap. Wide exhibits span both columns. Section pages drop the judgements column and run the exhibits full width.

Responsive behaviour has two steps. At 1100px or narrower, the judgements column stacks above the exhibits and gets a bottom rule instead of a side rule. At 760px or narrower, gutters shrink to 16px, the section tabs wrap onto their own scrolling row, and exhibits go to one column.

Spacing follows a 4px base (4, 8, 12, 16, 24) plus the report steps of 28px (gutter), 32px (page edge), and 64px (page end).

### Named Rules
**The Exhibit Rule.** Every figure lives in an exhibit, in this order: number, title, method subtitle, Figure/Table switch, legend, figure, judgement sentence, source. Leave out a part only when it has no content. Never add a frame.

**The Projection Band Rule.** Every time axis shades the validation period and the test period with the mist bands, labelled "Valid" and "Test" above the plot. Days with no collected data are drawn as gaps, never as zero.

## Elevation & Depth

The system is flat. Depth comes from tonal layering (Paper, then Mist Panel) and from rules: a 3px ink rule on top of each exhibit, and 1px hairlines elsewhere. The masthead is sticky but casts no shadow.

### Shadow Vocabulary
- **Tooltip float** (`box-shadow: 0 6px 18px rgba(11, 37, 69, 0.14)`): only on the chart hover tooltip, which floats over the plot.

### Named Rules
**The Flat Paper Rule.** Surfaces never cast shadows. The tooltip is the only element that floats, so it is the only element with a shadow.

## Shapes

Corners are nearly square. Exhibits have no corners because they have no box: only a top rule. Controls (range chips, segmented toggles, the Figure/Table switch, table frames, empty states) use a 4px radius. Legend keys and the focus ring use 2px. The tooltip alone uses 6px. Horizontal bars are flat at the baseline, with a 4px rounded cap at the value end. Segmented controls are joined groups with 1px internal dividers and clipped corners, not separate pills.

## Components

### Masthead and section tabs
- **Character:** a navy masthead that works as the report's table of contents.
- **Style:** Report Navy background, 60px minimum height, sticky. The serif brand sits on the left.
- **Tabs:** bar-muted text. On hover the text turns bar-ink. The current page gets bar-ink text and a 2px bar-ink underline.
- **Toggles:** language (VI/EN) and theme (light/dark) are joined segmented groups with a translucent bar-muted border. The pressed segment inverts to bar-ink fill with navy 600 text.
- **Mobile:** the tabs move to their own full-width row, which scrolls horizontally.

### Range chips
- **Style:** a joined group with a hairline border and 4px radius. Segments are Paper with 6px 12px padding and 14px text.
- **State:** hover fills Mist Panel. The pressed segment fills with the accent, uses page-colour text, and goes to weight 600. Options: 30, 90, 365 days, full sample.

### Exhibit
- **Corner Style:** none. The exhibit is defined by a 3px ink top rule and 12px of top padding.
- **Background:** the page itself; no container fill.
- **Internal order:** see The Exhibit Rule. The judgement is ink-2 at 14px; the source is muted at 12px.
- **Figure/Table switch:** a small joined toggle at the top right of the header, 12px text. The pressed segment is Mist Panel with ink 600 text.

### Key judgements column
- **Style:** Mist Panel background, 28px padding. It holds the serif Display heading, a muted as-of line in UTC with a document count, four bulleted sentences, then a stack of metrics.
- **Metric stack:** a one-column definition list with 1px hairline gaps. Each cell is Paper with 12px padding: a 12px muted label, a 20px value at weight 600, and a 12px muted note.
- **Risk marker:** shape and colour both encode the level: a circle for normal or low, a triangle for elevated or high.

### Time chart
- **Lines:** 2px, round joins and caps. Dashed lines (6 4) mark a second reading of the same quantity (neg_sent, forecast).
- **Stacks:** stacked attention areas leave gaps on missing days.
- **Fan bands:** accent fill at 12% opacity (90% band) and 22% (50% band).
- **End labels:** when there are four series or fewer, each line ends in a 4px dot with a surface-coloured halo and an 11px value label.
- **Hover:** a muted vertical crosshair, halo dots on each series, and the tooltip. Left and right arrow keys move the crosshair.

### Tooltip
- **Style:** Paper surface, hairline border, 6px radius, tooltip shadow, 8px 10px padding, 12px text, at least 160px wide.
- **Content:** the date in UTC (muted), then one row per series with a key line and a tabular value in 600 weight.

### Data table
- **Style:** inside a hairline frame with a 4px radius, 420px maximum height, scrolling. Cells are 13px with 6px 10px padding and Grid Whisper row dividers.
- **Header:** sticky, Mist Panel background, ink-2 text at 600. Each column sorts on click.
- **Numbers:** right-aligned and tabular.

### Legend and tags
- **Legend:** a wrapping row of 12px ink-2 labels with a 10px square key (or a 14×2px line key for line charts). When a legend toggles series, hidden series show at 45% opacity.
- **Snippet tag:** a series-coloured square key, a 12px narrative label, and a FinBERT score coloured Risk Red or Gain Green at 600.

### Empty state
- **Style:** a dashed hairline border, 4px radius, 24px padding, muted 14px text. It takes the place of a chart or table when there is no data.

## Do's and Don'ts

### Do:
- **Do** give every figure an exhibit number, a judgement sentence, and a source line (The Exhibit Rule).
- **Do** shade validation (16% mist) and test (32% mist) periods on every time axis, and label them "Valid" and "Test".
- **Do** assign series colours by fixed slot s1 to s8, and use each slot's `-dark` value in dark mode.
- **Do** pair colour with a second channel: shape for risk level, dash for the second reading of a quantity, a direct label at the line end.
- **Do** set every number in Source Sans 3 with tabular figures, and label every date as UTC.
- **Do** keep chrome navy, paper, and neutral; colour belongs to the data.

### Don't:
- **Don't** build a grid of KPI tiles without sentences. Metrics appear only under the Key judgements sentences, as a stacked list.
- **Don't** use red for anything other than negative sentiment or critical risk.
- **Don't** draw days with no collected data as zero; leave a gap.
- **Don't** box exhibits in cards or give surfaces shadows. Only the tooltip floats.
- **Don't** use the serif for numbers, labels, or controls.
- **Don't** round controls past 4px, or the tooltip past 6px.
