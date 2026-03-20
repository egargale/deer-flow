# TradingView Charts SPA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an Astro SPA that converts CSV/JSON OHLCV financial data with pre-calculated Messina Signals indicators into interactive multi-pane TradingView Lightweight Charts, deployable to Netlify.

**Architecture:** Client-side only SPA using Astro + Svelte for the UI, lightweight-charts npm package for rendering, Papa Parse for CSV parsing. File upload → parse → validate → template selection → multi-pane chart rendering. Optional Netlify Blob Store for chart sharing.

**Tech Stack:** Astro 5.0+, Svelte 4.2+, TypeScript 5.3+, lightweight-charts 5.1.0, Papa Parse 5.4.1, Tailwind CSS + daisyUI, Netlify deployment

---

## File Structure

```
skills/custom/tradingview-charts/
├── SKILL.md                          # Agent Skills spec (already created)
├── skill.yaml                        # Backward compatibility (already exists)
├── tradingview-charts-web/           # NEW: Astro SPA application
│   ├── package.json                  # Dependencies
│   ├── astro.config.mjs              # Astro config with Svelte integration
│   ├── tailwind.config.mjs           # Tailwind + daisyUI config
│   ├── tsconfig.json                 # TypeScript config
│   ├── svelte.config.js              # Svelte preprocess config
│   ├── src/
│   │   ├── pages/
│   │   │   ├── index.astro           # Main page
│   │   │   └── view/
│   │   │       └── [id].astro       # Shared chart view
│   │   ├── components/
│   │   │   ├── FileUploader.svelte   # File upload component
│   │   │   ├── ChartRenderer.svelte  # Chart wrapper with lifecycle
│   │   │   ├── TemplateSelector.svelte # Template picker
│   │   │   ├── ErrorMessage.svelte   # Error display
│   │   │   └── ShareButton.svelte    # Share functionality
│   │   ├── lib/
│   │   │   ├── types.ts              # TypeScript interfaces
│   │   │   ├── parsers.ts            # CSV/JSON parsers
│   │   │   ├── validators.ts         # Schema validation
│   │   │   ├── chart-builder.ts      # Chart creation logic
│   │   │   ├── templates.ts          # Template definitions
│   │   │   └── blob-store.ts         # Netlify helpers (optional)
│   │   └── styles/
│   │       └── global.css            # Global styles
│   ├── public/
│   │   └── samples/                  # Example data files
│   │       ├── basic.csv             # OHLCV only
│   │       ├── with-indicators.csv   # Full indicators
│   │       └── sample.json           # JSON example
│   └── netlify/
│       └── functions/
│           ├── save-chart.ts        # Store chart (optional)
│           └── load-chart.ts        # Load chart (optional)
├── scripts/                          # NEW: Setup scripts
│   ├── setup.sh                     # Install + build
│   └── deploy.sh                    # Deploy to Netlify
└── references/                       # Already created
    ├── panes.md
    └── api-reference.md
```

---

## Task 1: Initialize Astro Project

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/package.json`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/astro.config.mjs`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/tsconfig.json`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/svelte.config.js`

- [ ] **Step 1: Create package.json with dependencies**

```bash
mkdir -p skills/custom/tradingview-charts/tradingview-charts-web
cd skills/custom/tradingview-charts/tradingview-charts-web
```

Create `package.json`:
```json
{
  "name": "tradingview-charts-web",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "astro dev",
    "build": "astro build",
    "preview": "astro preview"
  },
  "dependencies": {
    "@astrojs/svelte": "^7.0.0",
    "@astrojs/tailwind": "^6.0.0",
    "astro": "^5.0.0",
    "daisyui": "^4.12.0",
    "lightweight-charts": "^5.1.0",
    "papaparse": "^5.4.1",
    "svelte": "^4.2.0"
  },
  "devDependencies": {
    "@types/papaparse": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.3.0"
  }
}
```

- [ ] **Step 2: Create Astro configuration**

Create `astro.config.mjs`:
```javascript
import { defineConfig } from 'astro/config';
import svelte from '@astrojs/svelte';
import tailwind from '@astrojs/tailwind';

export default defineConfig({
  integrations: [
    svelte(),
    tailwind({
      applyBaseStyles: false,
    }),
  ],
  output: 'static',
});
```

- [ ] **Step 3: Create TypeScript configuration**

Create `tsconfig.json`:
```json
{
  "extends": "astro/tsconfigs/strict",
  "compilerOptions": {
    "jsx": "react-jsx",
    "jsxImportSource": "svelte"
  }
}
```

- [ ] **Step 4: Create Svelte configuration**

Create `svelte.config.js`:
```javascript
import { vitePreprocess } from '@astrojs/svelte';

export default {
  preprocess: vitePreprocess(),
};
```

- [ ] **Step 5: Commit**

```bash
cd skills/custom/tradingview-charts
git add tradingview-charts-web/
git commit -m "feat: initialize Astro project with dependencies"
```

---

## Task 2: Setup Tailwind + daisyUI

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/tailwind.config.mjs`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/styles/global.css`

- [ ] **Step 1: Create Tailwind configuration**

Create `tailwind.config.mjs`:
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: ['./src/**/*.{astro,html,js,jsx,md,mdx,svelte,ts,tsx}'],
  theme: {
    extend: {},
  },
  plugins: [require('daisyui')],
  daisyui: {
    themes: ['light', 'dark'],
  },
};
```

- [ ] **Step 2: Create global styles**

Create `src/styles/global.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;

html, body {
  margin: 0;
  padding: 0;
  height: 100%;
}

body {
  @apply bg-base-100 text-base-content;
}
```

- [ ] **Step 3: Commit**

```bash
git add tradingview-charts-web/
git commit -m "feat: add Tailwind CSS + daisyUI styling"
```

---

## Task 3: Define TypeScript Types

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/types.ts`

- [ ] **Step 1: Create type definitions**

Create `src/lib/types.ts`:
```typescript
// Chart data structures
export interface ChartData {
  metadata: {
    symbol?: string;
    timeframe?: string;
    source: 'csv' | 'json';
    indicators?: string[];  // Detected indicator columns
  };
  columns: string[];
  rows: DataPoint[];
}

export interface DataPoint {
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

// Template system
export type SeriesType = 'candlestick' | 'line' | 'area' | 'bar' | 'baseline' | 'histogram';

export interface Template {
  id: string;
  name: string;
  description: string;
  theme: 'light' | 'dark';
  panes: PaneConfig[];
}

export interface PaneConfig {
  name: string;
  height?: number;
  stretchFactor?: number;
  series: SeriesConfig[];
}

export interface SeriesConfig {
  type: SeriesType;
  dataKey: string;
  options?: Record<string, unknown>;
}

// Validation
export interface ValidationResult {
  valid: boolean;
  errors: ErrorItem[];
  warnings: WarningItem[];
  presentIndicators: string[];
}

export interface ErrorItem {
  type: 'file_type' | 'file_size' | 'missing_columns' | 'invalid_data' | 'insufficient_rows';
  message: string;
  details?: Record<string, unknown>;
}

export interface WarningItem {
  type: 'data_sorted' | 'missing_optional';
  message: string;
}

// Blob Store (optional)
export interface StoredChart {
  id: string;
  metadata: {
    createdAt: string;
    expiresAt: string;
  };
  templateId: string;
  data: ChartData;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/types.ts
git commit -m "feat: add TypeScript type definitions"
```

---

## Task 4: Create Template Definitions

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/templates.ts`

- [ ] **Step 1: Create template definitions**

Create `src/lib/templates.ts`:
```typescript
import type { Template } from './types';

export const TEMPLATES: Template[] = [
  {
    id: 'basic-candlestick',
    name: 'Basic Candlestick',
    description: 'Simple candlestick chart with volume',
    theme: 'light',
    panes: [
      {
        name: 'Price',
        stretchFactor: 0.8,
        series: [
          { type: 'candlestick', dataKey: 'close' }
        ]
      },
      {
        name: 'Volume',
        stretchFactor: 0.2,
        series: [
          { type: 'histogram', dataKey: 'volume', options: { priceFormat: { type: 'volume' } } }
        ]
      }
    ]
  },
  {
    id: 'messina-sma-vstop',
    name: 'Messina Trend (SMA200 + VSTOP)',
    description: 'Trend following with SMA200 and volatility stop',
    theme: 'dark',
    panes: [
      {
        name: 'Price',
        stretchFactor: 1.0,
        series: [
          { type: 'candlestick', dataKey: 'close' },
          { type: 'line', dataKey: 'sma200', options: { color: '#FF6D00', lineWidth: 2, title: 'SMA200' } },
          { type: 'line', dataKey: 'vstop', options: { color: '#4CAF50', lineStyle: 2, lineWidth: 2, title: 'VSTOP' } }
        ]
      }
    ]
  },
  {
    id: 'messina-adx-momentum',
    name: 'Messina Momentum (ADX/DI)',
    description: 'Trend strength with ADX and directional indicators in separate pane',
    theme: 'dark',
    panes: [
      {
        name: 'Price',
        stretchFactor: 0.7,
        series: [
          { type: 'candlestick', dataKey: 'close' },
          { type: 'line', dataKey: 'sma200', options: { color: '#FF6D00', lineWidth: 2, title: 'SMA200' } }
        ]
      },
      {
        name: 'ADX/DI',
        stretchFactor: 0.3,
        series: [
          { type: 'line', dataKey: 'adx', options: { color: '#2196F3', lineWidth: 2, title: 'ADX' } },
          { type: 'line', dataKey: 'di_plus', options: { color: '#4CAF50', lineWidth: 1, title: 'DI+' } },
          { type: 'line', dataKey: 'di_minus', options: { color: '#F44336', lineWidth: 1, title: 'DI-' } }
        ]
      }
    ]
  },
  {
    id: 'messina-complete',
    name: 'Messina Complete',
    description: 'Full Messina Signals: SMA200, VSTOP, ADX/DI',
    theme: 'dark',
    panes: [
      {
        name: 'Price',
        stretchFactor: 0.6,
        series: [
          { type: 'candlestick', dataKey: 'close' },
          { type: 'line', dataKey: 'sma200', options: { color: '#FF6D00', lineWidth: 2, title: 'SMA200' } },
          { type: 'line', dataKey: 'vstop', options: { color: '#4CAF50', lineStyle: 2, lineWidth: 2, title: 'VSTOP' } }
        ]
      },
      {
        name: 'ADX/DI',
        stretchFactor: 0.25,
        series: [
          { type: 'line', dataKey: 'adx', options: { color: '#2196F3', lineWidth: 2, title: 'ADX' } },
          { type: 'line', dataKey: 'di_plus', options: { color: '#4CAF50', lineWidth: 1, title: 'DI+' } },
          { type: 'line', dataKey: 'di_minus', options: { color: '#F44336', lineWidth: 1, title: 'DI-' } }
        ]
      },
      {
        name: 'Volume',
        stretchFactor: 0.15,
        series: [
          { type: 'histogram', dataKey: 'volume', options: { priceFormat: { type: 'volume' } } }
        ]
      }
    ]
  }
];

export function getTemplateById(id: string): Template | undefined {
  return TEMPLATES.find(t => t.id === id);
}

export function getCompatibleTemplates(presentIndicators: string[]): Template[] {
  const indicatorMap = new Map(
    presentIndicators.map(i => [i.toLowerCase(), i])
  );

  return TEMPLATES.filter(template => {
    const requiredIndicators = new Set<string>();
    template.panes.forEach(pane => {
      pane.series.forEach(series => {
        if (series.dataKey !== 'close' && series.dataKey !== 'volume') {
          requiredIndicators.add(series.dataKey.toLowerCase());
        }
      });
    });

    return Array.from(requiredIndicators).every(ind =>
      indicatorMap.has(ind)
    );
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/templates.ts
git commit -m "feat: add chart template definitions"
```

---

## Task 5: Create CSV Parser

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/parsers.ts`

- [ ] **Step 1: Create parsers module**

Create `src/lib/parsers.ts`:
```typescript
import Papa from 'papaparse';
import type { ChartData, DataPoint } from './types';

export async function parseCSV(file: File): Promise<ChartData> {
  return new Promise((resolve, reject) => {
    Papa.parse(file, {
      header: true,
      dynamicTyping: true,
      skipEmptyLines: true,
      complete: (results) => {
        try {
          const data = normalizeData(results.data as Record<string, unknown>[]);
          resolve(data);
        } catch (error) {
          reject(error);
        }
      },
      error: (error) => {
        reject(new Error(`CSV parsing failed: ${error.message}`));
      }
    });
  });
}

export async function parseJSON(file: File): Promise<ChartData> {
  try {
    const text = await file.text();
    const data = JSON.parse(text);
    return normalizeData(data);
  } catch (error) {
    throw new Error(`JSON parsing failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }
}

function normalizeData(rows: Record<string, unknown>[]): ChartData {
  if (rows.length === 0) {
    throw new Error('File contains no data rows');
  }

  // Standardize column names
  const columnMap: Record<string, string> = {
    'Date': 'date',
    'date': 'date',
    'Time': 'time',
    'time': 'time',
    'Open': 'open',
    'open': 'open',
    'High': 'high',
    'high': 'high',
    'Low': 'low',
    'low': 'low',
    'Close': 'close',
    'close': 'close',
    'Adj Close': 'close',
    'Volume': 'volume',
    'volume': 'volume',
    'SMA200': 'sma200',
    'sma200': 'sma200',
    'VSTOP': 'vstop',
    'vstop': 'vstop',
    'ADX': 'adx',
    'adx': 'adx',
    'DI_plus': 'di_plus',
    'DI_minus': 'di_minus',
  };

  const normalizedRows: DataPoint[] = rows.map(row => {
    const normalized: Record<string, unknown> = {};

    for (const [key, value] of Object.entries(row)) {
      const mappedKey = columnMap[key] || key.toLowerCase();
      normalized[mappedKey] = value;
    }

    // Convert date/time to time field
    if (normalized.date) {
      normalized.time = normalized.date;
      delete normalized.date;
    } else if (normalized.time) {
      // Keep as is
    } else {
      throw new Error('Missing date/time column');
    }

    return normalized as DataPoint;
  });

  // Get columns from first row
  const columns = Object.keys(rows[0]).map(k => columnMap[k] || k.toLowerCase());

  // Detect present indicators
  const presentIndicators = columns.filter(c =>
    ['sma200', 'vstop', 'adx', 'di_plus', 'di_minus'].includes(c)
  );

  return {
    metadata: {
      source: 'csv',
      indicators: presentIndicators,
    },
    columns,
    rows: normalizedRows,
  };
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/parsers.ts
git commit -m "feat: add CSV and JSON parsers"
```

---

## Task 6: Create Validator

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/validators.ts`

- [ ] **Step 1: Create validation module**

Create `src/lib/validators.ts`:
```typescript
import type { ChartData, ValidationResult, ErrorItem } from './types';

const REQUIRED_COLUMNS = ['date', 'open', 'high', 'low', 'close'];
const OPTIONAL_COLUMNS = ['volume', 'sma200', 'vstop', 'adx', 'di_plus', 'di_minus'];
const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

export function validateFile(file: File): ErrorItem[] {
  const errors: ErrorItem[] = [];

  // Check file type
  if (!file.name.endsWith('.csv') && !file.name.endsWith('.json')) {
    errors.push({
      type: 'file_type',
      message: 'Invalid file type. Please upload a CSV or JSON file.',
    });
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE) {
    errors.push({
      type: 'file_size',
      message: `File too large. Maximum size is ${MAX_FILE_SIZE / 1024 / 1024}MB.`,
      details: { fileSize: file.size, maxSize: MAX_FILE_SIZE },
    });
  }

  return errors;
}

export function validateChartData(data: ChartData): ValidationResult {
  const errors: ErrorItem[] = [];
  const warnings: ErrorItem[] = [];
  const columns = data.columns.map(c => c.toLowerCase());

  // Check required columns
  const missing = REQUIRED_COLUMNS.filter(col => !columns.includes(col));
  if (missing.length > 0) {
    errors.push({
      type: 'missing_columns',
      message: `Missing required columns: ${missing.join(', ')}`,
      details: { missing, required: REQUIRED_COLUMNS },
    });
  }

  // Check data types in first few rows
  const checkRows = Math.min(data.rows.length, 10);
  for (let i = 0; i < checkRows; i++) {
    const row = data.rows[i];

    if (row.open !== undefined && typeof row.open !== 'number') {
      errors.push({
        type: 'invalid_data',
        message: `Invalid data type in 'open' column at row ${i + 1}. Expected number.`,
        details: { row: i + 1, column: 'open', actualType: typeof row.open },
      });
    }

    if (row.close !== undefined && typeof row.close !== 'number') {
      errors.push({
        type: 'invalid_data',
        message: `Invalid data type in 'close' column at row ${i + 1}. Expected number.`,
        details: { row: i + 1, column: 'close', actualType: typeof row.close },
      });
    }
  }

  // Check minimum rows for SMA200
  if (data.rows.length < 200) {
    errors.push({
      type: 'insufficient_rows',
      message: `Insufficient data for templates with SMA200. Need 200+ rows, got ${data.rows.length}.`,
      details: { rowCount: data.rows.length, required: 200 },
    });
  }

  // Sort data chronologically and warn if re-ordered
  const wasSorted = checkIfSorted(data.rows);
  if (!wasSorted) {
    data.rows.sort((a, b) => {
      const aTime = typeof a.time === 'string' ? new Date(a.time).getTime() : a.time;
      const bTime = typeof b.time === 'string' ? new Date(b.time).getTime() : b.time;
      return aTime - bTime;
    });
    warnings.push({
      type: 'data_sorted',
      message: 'Data was not in chronological order and has been auto-sorted.',
    });
  }

  // Detect present indicators (from metadata if available, or scan columns)
  const presentIndicators = data.metadata.indicators || [];
  if (presentIndicators.length === 0) {
    OPTIONAL_COLUMNS.forEach(col => {
      if (columns.includes(col)) {
        presentIndicators.push(col);
      }
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    presentIndicators,
  };
}

function checkIfSorted(rows: DataPoint[]): boolean {
  for (let i = 1; i < rows.length; i++) {
    const prevTime = typeof rows[i - 1].time === 'string' ? new Date(rows[i - 1].time).getTime() : rows[i - 1].time;
    const currTime = typeof rows[i].time === 'string' ? new Date(rows[i].time).getTime() : rows[i].time;
    if (currTime < prevTime) {
      return false;
    }
  }
  return true;
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/validators.ts
git commit -m "feat: add data validation module"
```

---

## Task 7: Create Chart Builder

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/chart-builder.ts`

- [ ] **Step 1: Create chart builder module**

Create `src/lib/chart-builder.ts`:
```typescript
import {
  createChart,
  type IChartApi,
  type CandlestickSeriesPartialOptions,
  type LineSeriesPartialOptions,
  type HistogramSeriesPartialOptions,
  CandlestickSeries,
  LineSeries,
  HistogramSeries,
} from 'lightweight-charts';
import type { ChartData, Template, SeriesType } from './types';

export function buildChart(
  container: HTMLElement,
  data: ChartData,
  template: Template
): IChartApi {
  // Create chart with theme colors
  const bgColor = template.theme === 'dark' ? '#131722' : '#FFFFFF';
  const textColor = template.theme === 'dark' ? '#D9D9D9' : '#333333';
  const gridColor = template.theme === 'dark' ? '#2B2B43' : '#E0E0E0';

  const chart = createChart(container, {
    layout: {
      background: { type: 'solid', color: bgColor },
      textColor,
      panes: {
        separatorColor: '#333333',
        enableResize: true,
      },
    },
    grid: {
      vertLines: { color: gridColor },
      horzLines: { color: gridColor },
    },
  });

  // Build each pane from template
  template.panes.forEach((paneConfig, paneIndex) => {
    paneConfig.series.forEach(seriesConfig => {
      const series = chart.addSeries(
        getSeriesDefinition(seriesConfig.type),
        seriesConfig.options || {},
        paneIndex
      );

      // Map and set data
      const seriesData = mapDataToSeries(data, seriesConfig.type, seriesConfig.dataKey);
      series.setData(seriesData);
    });

    // Apply pane sizing after series are added
    const panes = chart.panes();
    if (paneIndex < panes.length) {
      const pane = panes[paneIndex];
      if (paneConfig.height) {
        pane.setHeight(paneConfig.height);
      } else if (paneConfig.stretchFactor) {
        pane.setStretchFactor(paneConfig.stretchFactor);
      }
    }
  });

  // Fit content to show all data
  chart.timeScale().fitContent();

  return chart;
}

function getSeriesDefinition(type: SeriesType) {
  switch (type) {
    case 'candlestick':
      return CandlestickSeries;
    case 'line':
      return LineSeries;
    case 'histogram':
      return HistogramSeries;
    default:
      return CandlestickSeries;
  }
}

interface ChartDataPoint {
  time: string | number;
  open?: number;
  high?: number;
  low?: number;
  close?: number;
  value?: number;
}

function mapDataToSeries(
  data: ChartData,
  seriesType: SeriesType,
  dataKey: string
): ChartDataPoint[] {
  const isCandlestick = seriesType === 'candlestick' || seriesType === 'bar';

  return data.rows.map(row => {
    const point: ChartDataPoint = {
      time: row.time,
    };

    if (isCandlestick && dataKey === 'close') {
      // Candlestick needs OHLC
      point.open = row.open;
      point.high = row.high;
      point.low = row.low;
      point.close = row.close;
    } else if (dataKey === 'volume') {
      point.value = row.volume;
      point.close = row.close; // For volume color
    } else {
      // Line series - get the specific indicator value
      const value = (row as Record<string, unknown>)[dataKey] as number | undefined;
      point.value = value;
    }

    return point;
  }).filter(p => {
    // Filter out points with missing required data
    if (isCandlestick) {
      return p.open !== undefined && p.high !== undefined &&
             p.low !== undefined && p.close !== undefined;
    }
    return p.value !== undefined;
  });
}
```

- [ ] **Step 2: Commit**

```bash
git add src/lib/chart-builder.ts
git commit -m "feat: add multi-pane chart builder"
```

---

## Task 8: Create FileUploader Component

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/components/FileUploader.svelte`

- [ ] **Step 1: Create FileUploader component**

Create `src/components/FileUploader.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import type { ChartData } from '../lib/types';

  export let maxSize = 10 * 1024 * 1024; // 10MB
  export let disabled = false;

  const dispatch = createEventDispatcher<{
    fileLoaded: ChartData;
    error: string;
  }>();

  let fileInput: HTMLInputElement;
  let isDragging = false;

  async function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
      await processFile(file);
    }
  }

  async function handleDrop(event: DragEvent) {
    event.preventDefault();
    isDragging = false;

    const file = event.dataTransfer?.files[0];
    if (file) {
      await processFile(file);
    }
  }

  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    isDragging = true;
  }

  function handleDragLeave(event: DragEvent) {
    event.preventDefault();
    isDragging = false;
  }

  async function processFile(file: File) {
    try {
      const { parseCSV, parseJSON } = await import('../lib/parsers');
      const { validateFile, validateChartData } = await import('../lib/validators');

      // Validate file
      const fileErrors = validateFile(file);
      if (fileErrors.length > 0) {
        dispatch('error', fileErrors[0].message);
        return;
      }

      // Parse file
      let data: ChartData;
      if (file.name.endsWith('.csv')) {
        data = await parseCSV(file);
      } else {
        data = await parseJSON(file);
      }

      // Validate data
      const validation = validateChartData(data);
      if (!validation.valid) {
        dispatch('error', validation.errors[0].message);
        return;
      }

      dispatch('fileLoaded', data);
    } catch (error) {
      dispatch('error', error instanceof Error ? error.message : 'Failed to process file');
    }
  }

  function triggerFileInput() {
    fileInput.click();
  }
</script>

<div class="file-updater">
  <div
    class="dropzone {isDragging ? 'dragging' : ''} {disabled ? 'disabled' : ''}"
    on:click={triggerFileInput}
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
    role="button"
    tabindex="0"
    on:keydown={(e) => e.key === 'Enter' && triggerFileInput()}
  >
    <input
      bind:this={fileInput}
      type="file"
      accept=".csv,.json"
      on:change={handleFileSelect}
      hidden
      {disabled}
    />

    <div class="dropzone-content">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-12 h-12">
        <path stroke-linecap="round" stroke-linejoin="round" d="M3 16.5v2.25A2.25 2.25 0 0 0 5.25 21h13.5A2.25 2.25 0 0 0 21 18.75V16.5m-13.5-9L12 3m0 0 4.5 4.5M12 3v13.5" />
      </svg>
      <p class="text-lg font-medium">Drop CSV or JSON file here</p>
      <p class="text-sm opacity-70">or click to browse</p>
      <p class="text-xs opacity-50 mt-2">Max file size: {maxSize / 1024 / 1024}MB</p>
    </div>
  </div>
</div>

<style>
  .dropzone {
    @apply border-2 border-dashed border-base-300 rounded-lg p-8 text-center cursor-pointer transition-all;
  }

  .dropzone:hover:not(.disabled) {
    @apply border-primary bg-base-200;
  }

  .dropzone.dragging {
    @apply border-primary bg-primary/10;
  }

  .dropzone.disabled {
    @apply opacity-50 cursor-not-allowed;
  }

  .dropzone-content {
    @apply flex flex-col items-center gap-2;
  }
</style>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/FileUploader.svelte
git commit -m "feat: add FileUploader component"
```

---

## Task 9: Create TemplateSelector Component

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/components/TemplateSelector.svelte`

- [ ] **Step 1: Create TemplateSelector component**

Create `src/components/TemplateSelector.svelte`:
```svelte
<script lang="ts">
  import { createEventDispatcher } from 'svelte';
  import { TEMPLATES, getCompatibleTemplates } from '../lib/templates';
  import type { Template } from '../lib/types';

  export let presentIndicators: string[] = [];
  export let selectedTemplate: Template = TEMPLATES[0];

  const dispatch = createEventDispatcher<{
    select: Template;
  }>();

  $: compatibleTemplates = getCompatibleTemplates(presentIndicators);
  $: availableTemplates = compatibleTemplates.length > 0 ? compatibleTemplates : TEMPLATES;

  function selectTemplate(template: Template) {
    selectedTemplate = template;
    dispatch('select', template);
  }
</script>

<div class="template-selector">
  <h2 class="text-xl font-bold mb-4">Select Chart Template</h2>

  {#if compatibleTemplates.length === 0 && presentIndicators.length > 0}
    <div class="alert alert-warning mb-4">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0zm-9 3.75h.008v.008H12v-.008z" />
      </svg>
      <span>No templates match your data indicators. Available templates require: {presentIndicators.join(', ')}.</span>
    </div>
  {/if}

  <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
    {#each availableTemplates as template (template.id)}
      <div
        class="card cursor-pointer transition-all {selectedTemplate.id === template.id ? 'ring-2 ring-primary' : ''}"
        class:opacity-50={!compatibleTemplates.includes(template) && presentIndicators.length > 0}
        on:click={() => selectTemplate(template)}
        role="button"
        tabindex="0"
        on:keydown={(e) => e.key === 'Enter' && selectTemplate(template)}
      >
        <div class="card-body">
          <h3 class="card-title">{template.name}</h3>
          <p class="text-sm opacity-70">{template.description}</p>
          <div class="badge badge-neutral mt-2">
            {template.theme} theme
          </div>
          {!compatibleTemplates.includes(template) && presentIndicators.length > 0 && (
            <div class="badge badge-warning mt-2">
              Missing indicators
            </div>
          )}
        </div>
      </div>
    {/each}
  </div>
</div>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/TemplateSelector.svelte
git commit -m "feat: add TemplateSelector component"
```

---

## Task 10: Create ChartRenderer Component

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/components/ChartRenderer.svelte`

- [ ] **Step 1: Create ChartRenderer component with lifecycle management**

Create `src/components/ChartRenderer.svelte`:
```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import type { IChartApi } from 'lightweight-charts';
  import type { ChartData, Template } from '../lib/types';
  import { buildChart } from '../lib/chart-builder';

  export let data: ChartData;
  export let template: Template;
  export let onLoad: () => void = () => {};

  let container: HTMLDivElement;
  let chart: IChartApi | null = null;
  let previousTemplate: Template | null = null;

  // Rebuild chart when template or data changes
  $: if (data && template && template !== previousTemplate) {
    rebuildChart();
  }

  async function rebuildChart() {
    if (chart) {
      chart.remove();
      chart = null;
    }

    if (container && data && template) {
      chart = buildChart(container, data, template);
      previousTemplate = template;
      onLoad();
    }
  }

  onMount(() => {
    if (container && data && template) {
      chart = buildChart(container, data, template);
      previousTemplate = template;
      onLoad();
    }
  });

  onDestroy(() => {
    // MUST call chart.remove() to prevent memory leaks
    if (chart) {
      chart.remove();
      chart = null;
    }
  });
</script>

<div bind:this={container} class="chart-container" style="width: 100%; height: 600px;"></div>
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ChartRenderer.svelte
git commit -m "feat: add ChartRenderer component with lifecycle management"
```

---

## Task 11: Create ErrorMessage Component

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/components/ErrorMessage.svelte`

- [ ] **Step 1: Create ErrorMessage component**

Create `src/components/ErrorMessage.svelte`:
```svelte
<script lang="ts">
  export let message = '';
  export let type: 'error' | 'warning' = 'error';
  export let dismissible = true;

  let visible = true;

  function dismiss() {
    visible = false;
  }
</script>

{#if visible}
  <div class="alert alert-{type} mb-4" class:alert-dismissible={dismissible}>
    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
      {#if type === 'error'}
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z" />
      {:else}
        <path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3.75m9-.75a9 9 0 1 1-18 0 9 9 0 0 1 18 0zm-9 3.75h.008v.008H12v-.008z" />
      {/if}
    </svg>
    <span>{message}</span>
    {#if dismissible}
      <button on:click={dismiss} class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
    {/if}
  </div>
{/if}
```

- [ ] **Step 2: Commit**

```bash
git add src/components/ErrorMessage.svelte
git commit -m "feat: add ErrorMessage component"
```

---

## Task 12: Create Main Index Page

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/pages/index.astro`

- [ ] **Step 1: Create main page**

Create `src/pages/index.astro`:
```astro
---
import '../styles/global.css';
import FileUploader from '../components/FileUploader.svelte';
import TemplateSelector from '../components/TemplateSelector.svelte';
import ChartRenderer from '../components/ChartRenderer.svelte';
import ErrorMessage from '../components/ErrorMessage.svelte';
import type { ChartData, Template } from '../lib/types';
import { TEMPLATES } from '../lib/templates';

let currentData: ChartData | null = null;
let currentTemplate: Template = TEMPLATES[0];
let errorMessage = '';
let presentIndicators: string[] = [];
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>TradingView Charts</title>
  </head>
  <body class="min-h-screen p-4">
    <div class="max-w-7xl mx-auto">
      <header class="mb-8">
        <h1 class="text-4xl font-bold">TradingView Charts</h1>
        <p class="opacity-70">Upload financial data and generate interactive multi-pane charts</p>
      </header>

      {#if errorMessage}
        <ErrorMessage message={errorMessage} on:dismiss={() => errorMessage = ''} />
      {/if}

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-1">
          <div class="card bg-base-200">
            <div class="card-body">
              <h2 class="card-title">1. Upload Data</h2>
              <FileUploader
                on:fileLoaded={(e) => {
                  currentData = e.detail;
                  presentIndicators = e.detail.metadata.indicators || [];
                  errorMessage = '';
                }}
                on:error={(e) => {
                  errorMessage = e.detail;
                }}
              />
            </div>
          </div>

          {#if currentData}
            <div class="card bg-base-200 mt-4">
              <div class="card-body">
                <h2 class="card-title">2. Select Template</h2>
                <TemplateSelector
                  presentIndicators={presentIndicators}
                  selectedTemplate={currentTemplate}
                  on:select={(e) => {
                    currentTemplate = e.detail;
                  }}
                />
              </div>
            </div>
          {/if}
        </div>

        <div class="lg:col-span-2">
          <div class="card bg-base-200">
            <div class="card-body">
              <h2 class="card-title">3. View Chart</h2>
              {#if currentData}
                <ChartRenderer
                  data={currentData}
                  template={currentTemplate}
                />
              {:else}
                <div class="flex items-center justify-center h-96 opacity-50">
                  <p class="text-lg">Upload a CSV or JSON file to get started</p>
                </div>
              {/if}
            </div>
          </div>
        </div>
      </div>

      <footer class="mt-8 text-center opacity-50 text-sm">
        <p>Built with Astro + Svelte + TradingView Lightweight Charts</p>
      </footer>
    </div>
  </body>
</html>
```

- [ ] **Step 2: Commit**

```bash
git add src/pages/index.astro
git commit -m "feat: add main index page"
```

---

## Task 13: Create Sample Data Files

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/public/samples/basic.csv`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/public/samples/with-indicators.csv`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/public/samples/sample.json`

- [ ] **Step 1: Create basic sample CSV**

Create `public/samples/basic.csv`:
```csv
Date,Open,High,Low,Close,Volume
2024-01-01,150.0,155.0,148.0,153.5,1000000
2024-01-02,153.5,158.0,152.0,157.0,1200000
2024-01-03,157.0,160.0,155.0,158.5,1100000
2024-01-04,158.5,162.0,157.0,161.0,1300000
2024-01-05,161.0,164.0,159.0,163.5,1400000
```

- [ ] **Step 2: Create full indicators sample CSV**

Create `public/samples/with-indicators.csv`:
```csv
Date,Open,High,Low,Close,Volume,SMA200,VSTOP,ADX,DI_plus,DI_minus
2024-01-01,150.0,155.0,148.0,153.5,1000000,148.5,147.2,25.3,18.5,12.1
2024-01-02,153.5,158.0,152.0,157.0,1200000,148.6,147.5,26.1,19.2,11.8
2024-01-03,157.0,160.0,155.0,158.5,1100000,148.7,147.8,26.8,20.1,11.5
2024-01-04,158.5,162.0,157.0,161.0,1300000,148.9,148.1,27.2,21.0,11.2
2024-01-05,161.0,164.0,159.0,163.5,1400000,149.1,148.4,27.8,22.5,10.8
```

- [ ] **Step 3: Create sample JSON**

Create `public/samples/sample.json`:
```json
[
  {
    "Date": "2024-01-01",
    "Open": 150.0,
    "High": 155.0,
    "Low": 148.0,
    "Close": 153.5,
    "Volume": 1000000,
    "SMA200": 148.5,
    "VSTOP": 147.2,
    "ADX": 25.3,
    "DI_plus": 18.5,
    "DI_minus": 12.1
  },
  {
    "Date": "2024-01-02",
    "Open": 153.5,
    "High": 158.0,
    "Low": 152.0,
    "Close": 157.0,
    "Volume": 1200000,
    "SMA200": 148.6,
    "VSTOP": 147.5,
    "ADX": 26.1,
    "DI_plus": 19.2,
    "DI_minus": 11.8
  }
]
```

- [ ] **Step 4: Commit**

```bash
git add public/samples/
git commit -m "feat: add sample data files for testing"
```

---

## Task 14: Install Dependencies and Test

**Files:**
- Modify: `skills/custom/tradingview-charts/tradingview-charts-web/package.json` (lockfile after install)

- [ ] **Step 1: Install dependencies**

```bash
cd skills/custom/tradingview-charts/tradingview-charts-web
npm install
```

Expected: Dependencies installed successfully, `node_modules` and `package-lock.json` created.

- [ ] **Step 2: Run dev server**

```bash
npm run dev
```

Expected: Server starts at `http://localhost:4321`

- [ ] **Step 3: Manual testing checklist**

Open `http://localhost:4321` in browser:

1. ✅ Page loads without errors
2. ✅ Upload `public/samples/basic.csv`
3. ✅ File parses successfully
4. ✅ Template selector shows compatible templates
5. ✅ Chart renders with candlestick data
6. ✅ Upload `public/samples/with-indicators.csv`
7. ✅ All templates available
8. ✅ Select "Messina Momentum" template
9. ✅ ADX/DI pane appears below price pane
10. ✅ Panes can be resized by dragging separator

- [ ] **Step 4: Check browser console**

Expected: No errors in console

- [ ] **Step 5: Commit lockfile**

```bash
git add package-lock.json
git commit -m "chore: add dependency lockfile"
```

---

## Task 15: Update SKILL.md

**Files:**
- Create: `skills/custom/tradingview-charts/SKILL.md` (already exists, verify and update if needed)

- [ ] **Step 1: Verify SKILL.md exists and matches specification**

The SKILL.md file should already exist at `skills/custom/tradingview-charts/SKILL.md` with the following content:

```markdown
---
name: tradingview-charts
description: Generate interactive financial charts using TradingView Lightweight Charts library. Converts CSV/JSON OHLCV data with pre-calculated Messina Signals indicators (SMA200, VSTOP, ADX/DI) into multi-pane candlestick charts. Use with @finance-analysis skill to fetch stock data and calculate indicators, then visualize results here.
license: MIT
compatibility: Node.js 18+, npm 10+, Netlify deployment, modern browser with Canvas support
metadata:
  version: "2.0.0"
  type: "web-application"
  runtime: "astro-spa"
  depends_on: "finance-analysis"
---

# TradingView Charts Skill

Generate professional, interactive financial charts with multi-pane layouts for Messina Signals technical indicators.

## Data Source

**IMPORTANT:** This skill requires pre-calculated OHLCV data with technical indicators. Use the @finance-analysis skill to:

1. Fetch stock data (Yahoo Finance, Alpha Vantage, etc.)
2. Calculate Messina Signals indicators (SMA200, VSTOP, ADX/DI)
3. Export data to CSV/JSON format

Then upload the exported file to this chart application for visualization.

## Quick Start

### Installation

```bash
cd skills/custom/tradingview-charts/tradingview-charts-web
npm install
```

### First Time Setup

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Open http://localhost:4321
```

## Running Locally

### Development Mode

```bash
# Start Astro dev server with hot-reload
npm run dev

# Access at http://localhost:4321
```

### Production Preview

```bash
# Build for production
npm run build

# Preview production build locally
npm run preview

# Access at http://localhost:4321
```

## Deploying

### Deploy to Netlify

```bash
# Using Netlify CLI (recommended)
npm install -g netlify-cli
netlify login
netlify link
npm run build
netlify deploy --prod
```

### Environment Variables

No environment variables required for basic functionality.

Optional (for Blob Store sharing):
- `NETLIFY_BLOB_STORE_URL` - Auto-configured in Netlify

## Removing

### Uninstall Skill

```bash
# From skill root
cd skills/custom/tradingview-charts

# Remove dependencies and build artifacts
rm -rf tradingview-charts-web/node_modules
rm -rf tradingview-charts-web/.astro
rm -rf tradingview-charts-web/dist

# Remove from Netlify (if deployed)
netlify sites:delete
```

## Data Format

### CSV Schema

```csv
Date,Open,High,Low,Close,Volume,SMA200,VSTOP,ADX,DI_plus,DI_minus
2024-01-01,150.0,155.0,148.0,153.5,1000000,148.5,147.2,25.3,18.5,12.1
```

### JSON Schema

```json
[
  {
    "Date": "2024-01-01",
    "Open": 150.0,
    "High": 155.0,
    "Low": 148.0,
    "Close": 153.5,
    "Volume": 1000000,
    "SMA200": 148.5,
    "VSTOP": 147.2,
    "ADX": 25.3,
    "DI_plus": 18.5,
    "DI_minus": 12.1
  }
]
```

**Required Columns:** Date, Open, High, Low, Close
**Optional Columns:** Volume, SMA200, VSTOP, ADX, DI_plus, DI_minus

## Chart Templates

| Template | Description | Required Data |
|----------|-------------|---------------|
| Basic Candlestick | Price + Volume | OHLCV |
| Messina Trend | SMA200 + VSTOP overlays | OHLC + SMA200 + VSTOP |
| Messina Momentum | ADX/DI in separate pane | OHLC + SMA200 + ADX + DI_plus + DI_minus |
| Messina Complete | All indicators in 3 panes | All columns |

## Multi-Pane Layouts

Templates use multi-pane layouts to separate price data from indicators:

- **Main Pane (60-70%)**: Price candlesticks + overlay indicators (SMA200, VSTOP)
- **ADX Pane (25-30%)**: ADX, DI_plus, DI_minus lines
- **Volume Pane (15-20%)**: Volume histogram

Panes auto-resize and can be adjusted by dragging separators.

## Chart Sharing

Charts can be shared via Netlify Blob Store:

1. Create chart from uploaded data
2. Click "Share Chart" button
3. Receive shareable URL: `https://your-site.netlify.app/view/[blob-id]`
4. Charts expire after 30 days

## References

- [Multi-Pane Implementation](references/panes.md) - Detailed panes API guide
- [Complete API Reference](references/api-reference.md) - All Lightweight Charts methods
- [Agent Skills Spec](https://agentskills.io/specification) - Skill structure requirements

## Troubleshooting

**Chart not rendering:**
- Verify CSV has Date, Open, High, Low, Close columns
- Check browser console for errors
- Ensure data is sorted chronologically

**Panes not displaying:**
- Verify indicator columns exist in data (ADX, DI_plus, DI_minus)
- Check template matches available data columns
```

- [ ] **Step 2: If SKILL.md is missing or incomplete, create it with the content above**

- [ ] **Step 3: Commit**

```bash
git add skills/custom/tradingview-charts/SKILL.md
git commit -m "docs: ensure SKILL.md is complete with finance-analysis integration"
```

---

## Task 16: Create Setup Scripts

**Files:**
- Create: `skills/custom/tradingview-charts/scripts/setup.sh`
- Create: `skills/custom/tradingview-charts/scripts/deploy.sh`

- [ ] **Step 1: Create setup script**

Create `scripts/setup.sh`:
```bash
#!/bin/bash
set -e

echo "Setting up TradingView Charts SPA..."

cd tradingview-charts-web

echo "Installing dependencies..."
npm install

echo "Building for production..."
npm run build

echo "Setup complete!"
echo "Run 'npm run dev' to start development server"
```

- [ ] **Step 2: Create deploy script**

Create `scripts/deploy.sh`:
```bash
#!/bin/bash
set -e

echo "Deploying TradingView Charts SPA to Netlify..."

cd tradingview-charts-web

# Check if Netlify CLI is installed
if ! command -v netlify &> /dev/null; then
    echo "Netlify CLI not found. Installing..."
    npm install -g netlify-cli
fi

# Build for production
echo "Building for production..."
npm run build

# Deploy to Netlify
echo "Deploying to Netlify..."
cd dist
netlify deploy --prod

echo "Deployment complete!"
echo "Check your Netlify dashboard for the deployed URL."
```

- [ ] **Step 3: Make scripts executable**

```bash
chmod +x skills/custom/tradingview-charts/scripts/setup.sh
chmod +x skills/custom/tradingview-charts/scripts/deploy.sh
```

- [ ] **Step 4: Commit**

```bash
git add scripts/
git commit -m "feat: add setup and deploy scripts"
```

---

## Optional Task 17: Add Blob Store Integration (Optional)

**Files:**
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/lib/blob-store.ts`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/components/ShareButton.svelte`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/src/pages/view/[id].astro`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/netlify/functions/save-chart.ts`
- Create: `skills/custom/tradingview-charts/tradingview-charts-web/netlify/functions/load-chart.ts`

> **Note:** This task is optional. The basic chart functionality works without sharing. Implement only if chart sharing is required.

---

## Testing Strategy

### Manual Testing Checklist

1. **File Upload**
   - [ ] Upload valid CSV file
   - [ ] Upload valid JSON file
   - [ ] Upload invalid file type (error shown)
   - [ ] Upload oversized file (error shown)
   - [ ] Upload file with missing columns (error shown)

2. **Template Selection**
   - [ ] Templates shown match data indicators
   - [ ] Selecting template updates chart
   - [ ] Incompatible templates are grayed out

3. **Chart Rendering**
   - [ ] Candlestick chart renders correctly
   - [ ] Volume histogram renders in separate pane
   - [ ] SMA200 overlay renders on price
   - [ ] VSTOP overlay renders on price
   - [ ] ADX/DI pane appears below price
   - [ ] All three panes render for "Complete" template

4. **Interactions**
   - [ ] Panes can be resized by dragging
   - [ ] Chart zooms on scroll
   - [ ] Chart pans on drag
   - [ ] Crosshair follows mouse
   - [ ] Time scale can be scrolled

5. **Lifecycle**
   - [ ] No memory leaks when switching templates
   - [ ] Chart cleans up on page navigation
   - [ ] Multiple file uploads work correctly

### Browser Testing

Test on:
- [ ] Chrome 90+
- [ ] Firefox 88+
- [ ] Safari 14.1+
- [ ] Edge 90+

---

## Deployment to Netlify

### Manual Deployment

1. **Build for production**
```bash
cd skills/custom/tradingview-charts/tradingview-charts-web
npm run build
```

2. **Deploy to Netlify**
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Initialize new site
cd dist
netlify deploy --prod

# Or link to existing site
netlify link
netlify deploy --prod
```

3. **Configure Netlify**
- Build command: `npm run build`
- Publish directory: `dist`
- Node version: 18

---

## Troubleshooting

### Common Issues

**Issue:** Chart doesn't render
- Check browser console for errors
- Verify data has required columns (Date, Open, High, Low, Close)
- Ensure data is sorted chronologically

**Issue:** Panes don't appear
- Verify indicator columns exist in data (ADX, DI_plus, DI_minus)
- Check template has paneIndex > 0 for additional panes

**Issue:** Memory leak warnings
- Ensure `chart.remove()` is called in onDestroy
- Check that chart is properly cleaned up on template change

**Issue:** Build fails
- Ensure all dependencies installed: `npm install`
- Check Node.js version is 18+: `node --version`
