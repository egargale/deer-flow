# TradingView Charts SPA Design

**Date:** 2025-03-20
**Status:** Design Approved
**Author:** Claude Code
**Type:** New Feature / Modernization

## Overview

Convert the existing Python-based TradingView Charts skill to a pure JavaScript/TypeScript stack using Astro and the official `lightweight-charts` npm package. Deploy as a single-page application on Netlify.

**Key Change from Python Version:**
- Python → TypeScript/JavaScript
- Server-side HTML generation → Client-side rendering
- Jinja2 templates → Astro + Svelte components
- Indicators calculated with pandas/numpy → Pre-calculated in uploaded data
- No backend → Static hosting on Netlify with optional Blob Store for sharing

## Architecture

### Tech Stack

| Component | Technology |
|-----------|------------|
| Framework | Astro (latest) |
| UI Library | Svelte (via @astrojs/svelte) |
| Styling | Tailwind CSS + daisyUI (from Netlify starter) |
| Charts | `lightweight-charts` v5.1.0 (npm) |
| File Parsing | Papa Parse (CSV), native JSON |
| Deployment | Netlify (static hosting) |
| Optional Features | Netlify Blob Store (chart sharing), Edge Functions |

### Project Structure

```
tradingview-charts-web/
├── src/
│   ├── pages/
│   │   ├── index.astro              # Main upload + chart page
│   │   └── view/[id].astro          # Shared chart view
│   ├── components/
│   │   ├── FileUploader.svelte      # Drag-drop file upload
│   │   ├── ChartRenderer.svelte     # Multi-pane chart wrapper
│   │   ├── TemplateSelector.svelte  # Template picker
│   │   ├── ErrorMessage.svelte      # Validation errors
│   │   └── ShareButton.svelte       # Share/save button
│   ├── lib/
│   │   ├── parsers.ts               # CSV + JSON parsers
│   │   ├── validators.ts            # Schema validation
│   │   ├── chart-builder.ts         # Multi-pane chart creation
│   │   ├── templates.ts             # Template definitions
│   │   └── blob-store.ts            # Blob Store helpers
│   └── styles/
│       └── global.css
├── netlify/
│   └── functions/
│       ├── save-chart.ts            # Store chart
│       └── load-chart.ts            # Retrieve chart
├── public/
│   └── samples/                     # Example data files
└── skills/custom/tradingview-charts/
    └── references/                  # API documentation
```

## Data Structures

### Input Data Format

**CSV/JSON Schema (Strict):**

| Column | Type | Required | Description |
|--------|------|----------|-------------|
| Date | string/number | Yes | ISO date (YYYY-MM-DD) or Unix timestamp |
| Open | number | Yes | Opening price |
| High | number | Yes | High price |
| Low | number | Yes | Low price |
| Close | number | Yes | Closing price |
| Volume | number | No | Trading volume |
| SMA200 | number | No | 200-day Simple Moving Average (pre-calculated) |
| VSTOP | number | No | Volatility Stop (pre-calculated) |
| ADX | number | No | Average Directional Index (pre-calculated) |
| DI_plus | number | No | Directional Index Plus (pre-calculated) |
| DI_minus | number | No | Directional Index Minus (pre-calculated) |

**TypeScript Interfaces:**

```typescript
interface ChartData {
  metadata: {
    symbol?: string;
    timeframe?: string;
    source: 'csv' | 'json';
  };
  columns: string[];
  rows: DataPoint[];
}

interface DataPoint {
  time: string | number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  volume?: number;
  sma200?: number;
  vstop?: number;
  adx?: number;
  di_plus?: number;
  di_minus?: number;
}
```

## Multi-Pane Template System

### Template Configuration

Templates define multi-pane chart layouts with series per pane.

```typescript
interface Template {
  id: string;
  name: string;
  description: string;
  theme: 'light' | 'dark';
  panes: PaneConfig[];
}

interface PaneConfig {
  name: string;
  height?: number;           // Fixed height in pixels
  stretchFactor?: number;    // Relative height (0-1)
  series: SeriesConfig[];
}

interface SeriesConfig {
  type: 'candlestick' | 'line' | 'area' | 'bar' | 'baseline' | 'histogram';
  dataKey: string;           // Column name in data
  options?: SeriesOptions;
}
```

### Pre-defined Templates

1. **Basic Candlestick** - Price + Volume panes
2. **Messina Trend (SMA200 + VSTOP)** - Single pane with overlays
3. **Messina Momentum (ADX/DI)** - Price pane + ADX/DI pane (30% height)
4. **Messina Complete** - Price (60%) + ADX/DI (25%) + Volume (15%)

### Multi-Pane Implementation

```typescript
// Creating series in separate panes
const chart = createChart(container, options);

// Pane 0 (default) - Price series
chart.addSeries(CandlestickSeries, priceOptions, 0);

// Pane 1 (creates new pane) - ADX/DI series
chart.addSeries(LineSeries, adxOptions, 1);
chart.addSeries(LineSeries, diPlusOptions, 1);
chart.addSeries(LineSeries, diMinusOptions, 1);
```

Key Lightweight Charts API methods:
- `addSeries(definition, options, paneIndex)` - Add to specific pane
- `panes()` - Get array of panes
- `pane.setHeight(height)` - Set pixel height
- `pane.setStretchFactor(factor)` - Set relative height

## Data Flow

```
User uploads file
    ↓
FileUploader.svelte (validate file type, show preview)
    ↓
parsers.ts (Papa Parse for CSV, native JSON)
    ↓
validators.ts (check columns, types, sort chronologically)
    ↓
TemplateSelector.svelte (show compatible templates)
    ↓
ChartRenderer.svelte (create multi-pane chart)
    ↓
[Optional] ShareButton → Blob Store → shareable URL
```

## Validation Rules

| Check | Description |
|-------|-------------|
| File type | Only .csv and .json allowed |
| File size | Max 10MB |
| Required columns | Date, Open, High, Low, Close must exist |
| Data types | OHLCV columns must be numeric |
| Sorting | Data must be chronologically sorted |
| Minimum rows | Varies by template (200+ for SMA200) |

## Chart Sharing (Optional)

**Netlify Blob Store Integration:**

```typescript
// Stored chart structure
interface StoredChart {
  id: string;
  metadata: {
    createdAt: string;
    expiresAt: string;  // 30 days TTL
  };
  templateId: string;
  data: ChartData;
}
```

**Sharing Flow:**
1. User clicks "Share Chart"
2. ChartRenderer calls `saveChart(data, templateId)`
3. Edge function stores in Blob Store
4. Returns blob ID
5. Generate shareable URL: `https://charts.example.com/view/[blob-id]`

## Dependencies

```json
{
  "dependencies": {
    "@astrojs/svelte": "^7.0.0",
    "astro": "^5.0.0",
    "daisyui": "^4.12.0",
    "lightweight-charts": "^5.1.0",
    "papaparse": "^5.4.1",
    "svelte": "^4.2.0"
  },
  "devDependencies": {
    "@astrojs/tailwind": "^6.0.0",
    "@types/papaparse": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0"
  }
}
```

## Testing Strategy

- Sample data files for each template
- Validation error scenarios
- Multi-pane rendering verification
- Blob Store save/load functionality
- Browser compatibility (Chrome, Firefox, Safari, Edge)

## Migration Notes

**Removed from Python version:**
- Server-side indicator calculations (now pre-calculated)
- Jinja2 HTML templates (now Astro/Svelte)
- Python pandas/numpy dependencies

**Preserved concepts:**
- Messina Signals indicators (now in data)
- Template-based configurations
- Theme support (light/dark)
- Chart types (candlestick, line, area, bar, baseline, histogram)

## References

- [Lightweight Charts Documentation](https://tradingview.github.io/lightweight-charts/)
- [Panes API](https://tradingview.github.io/lightweight-charts/docs/panes)
- [Netlify Astro Platform Starter](https://github.com/netlify-templates/astro-platform-starter)
- API reference stored in `skills/custom/tradingview-charts/references/`
