import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}


export function formatBytes(totalBytes: number): string {
  if (totalBytes <= 0) return "0 MB";
  const megabytes = totalBytes / (1024 * 1024);
  if (megabytes >= 1024) {
    return `${(megabytes / 1024).toFixed(1)} GB`;
  }
  return `${Math.round(megabytes)} MB`;
}