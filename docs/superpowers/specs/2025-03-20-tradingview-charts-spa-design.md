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
  height?: number;           // Fixed height in pixels (30px minimum)
  stretchFactor?: number;    // Relative size ratio (default: 1.0)
  series: SeriesConfig[];
}

// Pane height resolution (in chart-builder.ts):
// 1. If height is set, use exact pixel value
// 2. Else if stretchFactor is set, use ratio relative to other panes
// 3. Else use library default (equal distribution)

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

// Pane 0 (default, auto-created) - Price series
const priceSeries = chart.addSeries(CandlestickSeries, priceOptions);

// Pane 1 (auto-created when referenced) - ADX/DI series
// When paneIndex doesn't exist, the library creates it automatically
const adxSeries = chart.addSeries(LineSeries, adxOptions, 1);
const diPlusSeries = chart.addSeries(LineSeries, diPlusOptions, 1);
const diMinusSeries = chart.addSeries(LineSeries, diMinusOptions, 1);

// Adjust pane sizes after creation (optional)
const panes = chart.panes();

// Option 1: Set pixel heights (absolute)
panes[0].setHeight(400);  // Main pane: 400px

// Option 2: Set stretch factors (relative ratios)
// Stretch factors are ratios where 1.0 = default, 0.5 = half, 2.0 = double
// When multiple panes have stretch factors, sizes are proportional to the sum
panes[1].setStretchFactor(0.3);  // ADX pane: 30% of default size
```

**Important Notes:**
- Specifying a `paneIndex` that doesn't exist automatically creates that pane
- `stretchFactor` is a ratio, not a percentage. Values like 0.3 mean "30% of default size"
- If neither `height` nor `stretchFactor` is set, panes auto-size equally
- Minimum pane height is 30px (enforced by the library)

Key Lightweight Charts API methods (v5.1.0):
- `addSeries(definition, options?, paneIndex?)` - Add series to pane (auto-creates pane if needed)
- `panes()` - Get array of all panes
- `pane.setHeight(height)` - Set fixed pixel height (min 30px, overrides stretchFactor)
- `pane.setStretchFactor(factor)` - Set relative size ratio (default: 1.0)
- `removePane(index)` - Remove pane and all its series
- `chart.remove()` - Clean up chart (MUST call in Svelte onDestroy)

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

| Check | Description | Error Message |
|-------|-------------|---------------|
| File type | Only .csv and .json allowed | "Invalid file type. Please upload a CSV or JSON file." |
| File size | Max 10MB (configurable) | "File too large. Maximum size is 10MB." |
| Required columns | Date, Open, High, Low, Close must exist | "Missing required columns: [list]" |
| Data types | OHLCV columns must be numeric | "Invalid data type in column [name] at row [n]" |
| Sorting | Data must be chronologically sorted | Auto-sorted, warning shown if re-ordered |
| Minimum rows | Varies by template (200+ for SMA200) | "Insufficient data for [template]. Need [n] rows." |

### Error Handling

```typescript
interface ValidationResult {
  valid: boolean;
  errors: ErrorItem[];
  warnings: WarningItem[];
  presentIndicators: string[];
}

interface ErrorItem {
  type: 'file_type' | 'file_size' | 'missing_columns' | 'invalid_data' | 'insufficient_rows';
  message: string;
  details?: Record<string, unknown>;
}

// ErrorMessage.svelte displays errors with:
// - Severity indicator (error/warning)
// - Actionable fix suggestions
// - Link to sample data format
```

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

## Performance Considerations

| Metric | Target | Notes |
|--------|--------|-------|
| File size limit | 10MB | ~100K rows of OHLCV data |
| Initial render | <2s | For files up to 5MB |
| Chart interaction | <100ms | Zoom, pan responsiveness |
| Memory usage | <200MB | Browser heap limit consideration |

**Optimization Strategies:**
- Stream large file parsing (don't load entire file into memory)
- Lazy render indicators outside visible time range
- Debounce chart resize events
- Use Web Workers for data parsing (future enhancement)

## Component Interfaces

```typescript
// FileUploader.svelte
interface FileUploaderProps {
  onFileLoaded: (data: ChartData) => void;
  onError: (error: string) => void;
  maxSize?: number;  // Default: 10MB
}

// TemplateSelector.svelte
interface TemplateSelectorProps {
  templates: Template[];
  presentIndicators: string[];
  selectedTemplate: Template;
  onSelect: (template: Template) => void;
}

// ChartRenderer.svelte
interface ChartRendererProps {
  data: ChartData;
  template: Template;
  containerId: string;
  onLoad?: () => void;
}

// ShareButton.svelte
interface ShareButtonProps {
  data: ChartData;
  templateId: string;
  onShared?: (url: string) => void;
}
```

## Chart Lifecycle Management

**Critical:** Lightweight Charts requires proper cleanup to prevent memory leaks.

```svelte
<!-- ChartRenderer.svelte -->
<script lang="ts">
  import { createChart, type IChartApi } from 'lightweight-charts';
  import { onDestroy, onMount } from 'svelte';

  export let data: ChartData;
  export let template: Template;

  let chart: IChartApi | null = null;
  let container: HTMLDivElement;

  onMount(() => {
    chart = createChart(container, { /* options */ });
    // ... add series, set data ...
  });

  onDestroy(() => {
    // MUST call chart.remove() to prevent memory leaks
    chart?.remove();
    chart = null;
  });

  // Re-create chart when template changes
  $: if (template && chart) {
    chart.remove();
    chart = createChart(container, /* new options */);
  }
</script>

<div bind:this={container} class="chart-container"></div>
```

## Multi-Pane Creation Workflow

```typescript
// chart-builder.ts
function buildChart(
  container: HTMLElement,
  data: ChartData,
  template: Template
): IChartApi {
  const chart = createChart(container, {
    layout: {
      background: { type: 'solid', color: getBgColor(template.theme) },
      textColor: getTextColor(template.theme),
      panes: {
        separatorColor: '#333333',
        enableResize: true,
      },
    },
  });

  // Clean up any existing panes first
  while (chart.panes().length > 1) {
    chart.removePane(chart.panes().length - 1);
  }

  // Create panes and series from template
  template.panes.forEach((paneConfig, paneIndex) => {
    paneConfig.series.forEach(seriesConfig => {
      const series = chart.addSeries(
        getSeriesType(seriesConfig.type),
        seriesConfig.options || {},
        paneIndex  // Auto-creates pane if it doesn't exist
      );

      const seriesData = mapDataToSeries(data, seriesConfig.dataKey);
      series.setData(seriesData);
    });

    // Apply pane sizing after series are added
    const pane = chart.panes()[paneIndex];
    if (pane) {
      if (paneConfig.height) {
        pane.setHeight(paneConfig.height);
      } else if (paneConfig.stretchFactor) {
        pane.setStretchFactor(paneConfig.stretchFactor);
      }
    }
  });

  return chart;
}
```

## Browser Support

| Browser | Minimum Version | Notes |
|---------|----------------|-------|
| Chrome | 90+ | Full support |
| Firefox | 88+ | Full support |
| Safari | 14.1+ | Full support |
| Edge | 90+ | Full support |

**Required Features:**
- ES6+ (async/await, arrow functions, destructuring)
- Canvas API (for chart rendering)
- ResizeObserver (for responsive sizing)
- FileReader API (for file upload)
- Fetch API (for Blob Store)

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
- [Agent Skills Specification](https://agentskills.io/specification)

## Agent Skills Compliance

The tradingview-charts skill must follow the [Agent Skills specification](https://agentskills.io/specification).

### Skill Structure

```
skills/custom/tradingview-charts/
├── SKILL.md                    # Required: YAML frontmatter + instructions
├── skill.yaml                   # Preserved for backward compatibility
├── scripts/                     # Optional: executable code
│   └── setup.sh                # Setup and deployment script
├── references/                  # Optional: documentation
│   ├── panes.md                # Lightweight Charts panes API
│   ├── api-reference.md        # Complete API reference
│   └── agent-skills-compliance.md  # This specification
├── assets/                      # Optional: templates, resources
│   └── sample-data/            # Example CSV/JSON files
└── tradingview-charts-web/     # The Astro SPA application
    ├── src/
    ├── public/
    ├── netlify/
    └── package.json
```

### SKILL.md Requirements

**Frontmatter (YAML):**
```yaml
---
name: tradingview-charts
description: Generate interactive financial charts using TradingView Lightweight Charts library. Converts CSV/JSON OHLCV data with pre-calculated Messina Signals indicators (SMA200, VSTOP, ADX/DI) into multi-pane candlestick charts deployed as Astro SPA on Netlify.
license: MIT
compatibility: Node.js 18+, npm 10+, Netlify deployment
---

[Instructions body]
```

**Required Sections in SKILL.md:**

1. **Quick Start** - Setup commands
2. **Running Locally** - Dev server commands
3. **Deploying** - Netlify deployment steps
4. **Removing** - Uninstall/cleanup commands
5. **Data Format** - CSV/JSON schema requirements
6. **Templates** - Available chart templates

### Reference Files

The `references/` directory contains on-demand documentation:
- `panes.md` - Multi-pane chart implementation guide
- `api-reference.md` - Complete Lightweight Charts API reference
- `sample-data/` - Example files for testing

### Scripts Directory

The `scripts/` directory contains automation scripts:
- `setup.sh` - Installs dependencies, builds for production
- `deploy.sh` - Deploys to Netlify
- `clean.sh` - Removes built artifacts and dependencies
