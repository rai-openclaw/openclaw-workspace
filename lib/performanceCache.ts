/**
 * Performance Cache Library
 * 
 * Provides caching functionality for the performance-v2 API endpoint.
 * Cache key includes context + date range: weekly, monthly, yearly, custom-START-END
 */

import fs from 'fs';
import path from 'path';

interface CacheEntry {
  data: PerformanceData;
  timestamp: string;
}

interface PerformanceData {
  context: string;
  dateRange: {
    start: string | null;
    end: string | null;
  };
  summary: {
    totalRealizedPl: number;
    winRate: number;
    totalTrades: number;
  };
  tickerBreakdown: TickerBreakdown[];
  openPositions?: OpenPosition[];
  equityCurve?: EquityPoint[];
}

interface TickerBreakdown {
  ticker: string;
  realizedPl: number;
  wins: number;
  losses: number;
  winRate: number;
}

interface OpenPosition {
  ticker: string;
  // Add other position fields as needed
}

interface EquityPoint {
  date: string;
  value: number;
}

type CacheStore = Record<string, CacheEntry>;

const CACHE_DIR = path.join(process.cwd(), 'data');
const CACHE_FILE = path.join(CACHE_DIR, 'performance_cache.json');

// In-memory cache
let cache: CacheStore = {};

/**
 * Get Monday of the week containing the given date
 */
function getMonday(date: Date): Date {
  const d = new Date(date);
  const day = d.getDay();
  const diff = d.getDate() - day + (day === 0 ? -6 : 1); // Adjust when day is Sunday
  return new Date(d.setDate(diff));
}

/**
 * Generate cache key based on context and date range
 * 
 * Key formats:
 * - weekly → weekly context
 * - monthly-YYYY-MM → monthly context with offset
 * - yearly → yearly context
 * - custom-YYYY-MM-DD-YYYY-MM-DD → custom date range
 */
export function generateCacheKey(
  context: string, 
  startDate?: string, 
  endDate?: string, 
  monthOffset: number = 0,
  weekOffset: number = 0
): string {
  if (context === 'weekly') {
    if (weekOffset !== 0) {
      // Calculate the target week start date based on weekOffset
      const now = new Date();
      const currentWeekStart = getMonday(now);
      const targetWeekStart = new Date(currentWeekStart.getTime() - weekOffset * 7 * 24 * 60 * 60 * 1000);
      return `weekly-${targetWeekStart.toISOString().split('T')[0]}`;
    }
    return 'weekly';
  } else if (context === 'monthly') {
    const today = new Date();
    const targetMonth = today.getMonth() - monthOffset;
    const targetYear = today.getFullYear() + Math.floor(targetMonth / 12);
    const adjustedMonth = ((targetMonth % 12) + 12) % 12 + 1;
    return `monthly-${targetYear}-${adjustedMonth.toString().padStart(2, '0')}`;
  } else if (context === 'yearly') {
    return 'yearly';
  } else if (context === 'custom' && startDate && endDate) {
    return `custom-${startDate}-${endDate}`;
  }
  return context;
}

/**
 * Get cached performance data for the given key
 */
export function getPerformanceCache(key: string): PerformanceData | null {
  const entry = cache[key];
  if (entry) {
    return entry.data;
  }
  return null;
}

/**
 * Store performance data in cache
 */
export function setPerformanceCache(key: string, data: PerformanceData): void {
  cache[key] = {
    data,
    timestamp: new Date().toISOString()
  };
  saveCacheToFile();
}

/**
 * Clear all performance cache entries
 * Called when trade events are added/deleted
 */
export function clearPerformanceCache(): void {
  cache = {};
  saveCacheToFile();
}

/**
 * Load cache from persistent file if available
 */
export function loadCacheFromFile(): void {
  try {
    if (fs.existsSync(CACHE_FILE)) {
      const fileContent = fs.readFileSync(CACHE_FILE, 'utf-8');
      cache = JSON.parse(fileContent);
    }
  } catch (error) {
    console.error('Failed to load performance cache:', error);
    cache = {};
  }
}

/**
 * Save cache to persistent file
 */
function saveCacheToFile(): void {
  try {
    if (!fs.existsSync(CACHE_DIR)) {
      fs.mkdirSync(CACHE_DIR, { recursive: true });
    }
    fs.writeFileSync(CACHE_FILE, JSON.stringify(cache, null, 2));
  } catch (error) {
    console.error('Failed to save performance cache:', error);
  }
}

/**
 * Get the quote timestamp from quote cache
 */
export function getQuoteTimestamp(): string {
  const quoteCacheFile = path.join(CACHE_DIR, 'quote_cache.json');
  try {
    if (fs.existsSync(quoteCacheFile)) {
      const fileContent = fs.readFileSync(quoteCacheFile, 'utf-8');
      const quoteData = JSON.parse(fileContent);
      return quoteData.lastQuoteUpdate || new Date().toISOString();
    }
  } catch (error) {
    console.error('Failed to read quote cache:', error);
  }
  return new Date().toISOString();
}

// Initialize cache on module load
loadCacheFromFile();

export type { PerformanceData, CacheEntry, TickerBreakdown, OpenPosition, EquityPoint };
