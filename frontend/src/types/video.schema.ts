import { z } from "zod";

// Regular expression to check basic URL structure (HTTP/HTTPS)
export const URL_REGEX = /^(https?:\/\/)?([\w.-]+)+[\w\-_~:/?#[\]@!$&'()*+,;=.]+$/;

export const SUPPORTED_PLATFORMS = [
  "youtube.com",
  "youtu.be",
  "vimeo.com",
  "tiktok.com",
  "twitter.com",
  "x.com",
  "facebook.com",
  "instagram.com",
  "dailymotion.com",
] as const;

/**
 * Zod Schema for Single Video Info & Download Form
 */
export const singleVideoSchema = z.object({
  url: z
    .string()
    .min(1, { message: "Video URL is required." })
    .regex(URL_REGEX, { message: "Please enter a valid HTTP or HTTPS video URL." })
    .refine(
      (val) => {
        const lower = val.toLowerCase();
        return (
          SUPPORTED_PLATFORMS.some((domain) => lower.includes(domain)) ||
          lower.startsWith("http://") ||
          lower.startsWith("https://")
        );
      },
      { message: "Please provide a valid supported video URL." }
    ),
  formatId: z.string().min(1, { message: "Please select a download format/quality." }),
  downloadSubs: z.boolean().default(false),
  audioOnly: z.boolean().default(false),
  withAudio: z.boolean().optional(),
  customFilename: z
    .string()
    .max(100, { message: "Filename cannot exceed 100 characters." })
    .optional()
    .or(z.literal("")),
});

/**
 * Zod Schema for Batch Downloads Form
 */
export const batchVideoSchema = z.object({
  urlsText: z
    .string()
    .min(1, { message: "At least one URL is required." })
    .refine(
      (text) => {
        const lines = text
          .split("\n")
          .map((line) => line.trim())
          .filter((line) => line.length > 0);
        if (lines.length === 0) return false;
        return lines.every((line) => URL_REGEX.test(line));
      },
      { message: "One or more lines do not contain a valid video URL." }
    ),
  defaultFormat: z.enum(["best", "1080p", "720p", "480p"]),
  downloadSubs: z.boolean().default(false),
  concurrentDownloads: z.coerce
    .number()
    .min(1, { message: "Minimum 1 concurrent download." })
    .max(5, { message: "Maximum 5 concurrent downloads." }),
});

/**
 * Zod Schema for Application Settings Form
 */
export const settingsSchema = z.object({
  apiBaseUrl: z
    .string()
    .min(1, { message: "Backend API URL is required." })
    .regex(URL_REGEX, { message: "Must be a valid API URL endpoint." }),
  defaultQuality: z.enum(["best", "1080p", "720p"]),
  autoDownloadSubtitles: z.boolean().default(false),
  subtitlesLanguage: z.string().min(1, { message: "Subtitle language code required." }),
  downloadDirectory: z.string().min(1, { message: "Download folder path required." }),
  enableNotifications: z.boolean().default(true),
  themeMode: z.enum(["dark", "light", "system"]),
});

export type SingleVideoFormValues = z.infer<typeof singleVideoSchema>;
export type BatchVideoFormValues = z.infer<typeof batchVideoSchema>;
export type SettingsFormValues = z.infer<typeof settingsSchema>;
