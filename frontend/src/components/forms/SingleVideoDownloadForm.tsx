import React, { useMemo } from "react";
import { useForm, Controller } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import {
  singleVideoSchema,
  SingleVideoFormValues,
  VideoInfo,
  VideoFormat,
} from "@/types";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Link2, Search, Download, FileText, Sparkles, Film } from "lucide-react";

interface SingleVideoDownloadFormProps {
  onAnalyze: (url: string) => Promise<VideoInfo | null | undefined>;
  onStartDownload: (
    url: string,
    formatId: string,
    options?: {
      downloadSubs?: boolean;
      customTitle?: string;
      resolution?: string;
      ext?: string;
      filesize?: number | null;
    }
  ) => void;
  isAnalyzing: boolean;
  videoInfo: VideoInfo | null;
}

/** Derive the unique container format types available from extracted formats. */
function getAvailableTypes(formats: VideoFormat[]): string[] {
  const seen = new Set<string>();
  for (const f of formats) {
    if (f.ext) seen.add(f.ext.toLowerCase());
  }
  return Array.from(seen).sort();
}

/** Filter formats matching the chosen type, excluding pure audio-only streams. */
function getFormatsForType(formats: VideoFormat[], ext: string): VideoFormat[] {
  return formats.filter(
    (f) =>
      f.ext?.toLowerCase() === ext &&
      // exclude audio-only streams (vcodec === "none")
      f.vcodec !== "none" &&
      f.resolution !== "audio only"
  );
}

/** Friendly label for a format entry shown in the resolution dropdown. */
function formatLabel(f: VideoFormat): string {
  const parts: string[] = [f.resolution];
  if (f.note) parts.push(`• ${f.note}`);
  if (f.filesize) {
    const mb = (f.filesize / (1024 * 1024)).toFixed(0);
    parts.push(`(~${mb} MB)`);
  }
  return parts.join(" ");
}

export function SingleVideoDownloadForm({
  onAnalyze,
  onStartDownload,
  isAnalyzing,
  videoInfo,
}: SingleVideoDownloadFormProps) {
  const form = useForm<SingleVideoFormValues>({
    resolver: zodResolver(singleVideoSchema),
    defaultValues: {
      url: "",
      formatId: "",
      downloadSubs: false,
      audioOnly: false,
      customFilename: "",
    },
  });

  const watchUrl = form.watch("url");
  const watchFormatId = form.watch("formatId");

  // ── Derived selections ──────────────────────────────────────────────────────
  // Selected type is tracked separately to drive the resolution list
  const [selectedType, setSelectedType] = React.useState<string>("");

  const allFormats = videoInfo?.formats ?? [];
  const availableTypes = useMemo(() => getAvailableTypes(allFormats), [allFormats]);
  const filteredFormats = useMemo(
    () => (selectedType ? getFormatsForType(allFormats, selectedType) : []),
    [allFormats, selectedType]
  );

  // When videoInfo arrives, auto-select mp4 if available
  React.useEffect(() => {
    if (!videoInfo) {
      setSelectedType("");
      form.setValue("formatId", "");
      return;
    }
    const types = getAvailableTypes(videoInfo.formats);
    const defaultType = types.includes("mp4") ? "mp4" : types[0] ?? "";
    setSelectedType(defaultType);
    // auto-pick first resolution for that type
    const firstFormat = getFormatsForType(videoInfo.formats, defaultType)[0];
    if (firstFormat) form.setValue("formatId", firstFormat.format_id);
  }, [videoInfo]);

  // When type changes, reset the resolution selection
  const handleTypeChange = (ext: string) => {
    setSelectedType(ext);
    const firstFormat = getFormatsForType(allFormats, ext)[0];
    form.setValue("formatId", firstFormat?.format_id ?? "");
  };

  const handleAnalyzeClick = async () => {
    const isValid = await form.trigger("url");
    if (isValid && watchUrl) {
      await onAnalyze(watchUrl);
    }
  };

  const onSubmit = (values: SingleVideoFormValues) => {
    const selectedFormat = allFormats.find((f) => f.format_id === values.formatId);

    onStartDownload(values.url, values.formatId, {
      downloadSubs: values.downloadSubs,
      customTitle: values.customFilename || videoInfo?.title,
      resolution: selectedFormat?.resolution ?? "1080p",
      ext: selectedFormat?.ext ?? selectedType ?? "mp4",
      filesize: selectedFormat?.filesize,
    });
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* URL Input */}
        <div className="space-y-4">
          <FormField
            control={form.control}
            name="url"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-base font-semibold flex items-center gap-2">
                  <Link2 className="h-4 w-4 text-primary" />
                  Video URL
                </FormLabel>
                <div className="flex flex-col sm:flex-row gap-2">
                  <FormControl>
                    <div className="relative flex-1">
                      <Input
                        placeholder="Paste YouTube, Vimeo, TikTok, or any video link…"
                        className="pl-10 h-12 text-base transition-all focus:ring-2"
                        {...field}
                      />
                      <Search className="absolute left-3.5 top-3.5 h-5 w-5 text-muted-foreground" />
                    </div>
                  </FormControl>
                  <Button
                    type="button"
                    variant="secondary"
                    size="lg"
                    disabled={isAnalyzing || !watchUrl}
                    onClick={handleAnalyzeClick}
                    className="h-12 px-6 font-medium shrink-0"
                  >
                    {isAnalyzing ? (
                      <span className="flex items-center gap-2">
                        <span className="animate-spin h-4 w-4 border-2 border-primary border-t-transparent rounded-full" />
                        Analyzing…
                      </span>
                    ) : (
                      <span className="flex items-center gap-2">
                        <Sparkles className="h-4 w-4 text-purple-500" />
                        Fetch Details
                      </span>
                    )}
                  </Button>
                </div>
                <FormDescription>
                  Supports YouTube, Vimeo, TikTok, Instagram, Twitter/X, Dailymotion and more.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Format Type + Resolution — two-step selection */}
        <div className="grid grid-cols-1 md:grid-cols-1 gap-6 pt-2 border-t">
          {/* Step 1 — Container type (mp4, webm, etc.) */}
          <div className="space-y-2">
            <label className="text-sm font-semibold flex items-center gap-2">
              <Film className="h-4 w-4 text-violet-500" />
              Format Type
            </label>
            {availableTypes.length > 0 ? (
              <Select value={selectedType} onValueChange={handleTypeChange}>
                <SelectTrigger className="h-11">
                  <SelectValue placeholder="Select type…" />
                </SelectTrigger>
                <SelectContent>
                  {availableTypes.map((ext) => (
                    <SelectItem key={ext} value={ext}>
                      <span className="uppercase font-mono font-semibold">{ext}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Select value="" disabled>
                <SelectTrigger className="h-11 opacity-60">
                  <SelectValue placeholder="Fetch details first…" />
                </SelectTrigger>
              </Select>
            )}
            <p className="text-xs text-muted-foreground">
              Container format (e.g. mp4, webm). Fetch details first to populate.
            </p>
          </div>

          {/* Step 2 — Resolution for selected type */}
          <FormField
            control={form.control}
            name="formatId"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="font-semibold">Resolution / Quality</FormLabel>
                <Select
                  onValueChange={field.onChange}
                  value={field.value}
                  disabled={filteredFormats.length === 0}
                >
                  <FormControl>
                    <SelectTrigger className="h-11">
                      <SelectValue
                        placeholder={
                          filteredFormats.length === 0
                            ? selectedType
                              ? "No video formats for this type"
                              : "Select a type first…"
                            : "Select quality…"
                        }
                      />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    {filteredFormats.map((f) => (
                      <SelectItem key={f.format_id} value={f.format_id}>
                        {formatLabel(f)}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <FormDescription>
                  All available resolutions for the selected format type.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        {/* Custom Filename */}
        <FormField
          control={form.control}
          name="customFilename"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="font-semibold">Custom Output Name (Optional)</FormLabel>
              <FormControl>
                <Input
                  placeholder="e.g. MyFavoriteTutorial"
                  className="h-11"
                  {...field}
                />
              </FormControl>
              <FormDescription>
                Leave empty to use the original video title automatically.
              </FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Subtitles Toggle */}
        <div className="p-4 rounded-xl bg-muted/40 border">
          <FormField
            control={form.control}
            name="downloadSubs"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between rounded-lg">
                <div className="space-y-0.5">
                  <FormLabel className="text-sm font-semibold flex items-center gap-1.5 cursor-pointer">
                    <FileText className="h-4 w-4 text-blue-500" />
                    Embed Subtitles / Captions
                  </FormLabel>
                  <FormDescription className="text-xs">
                    Download and embed available captions into the video file (requires ffmpeg).
                  </FormDescription>
                </div>
                <FormControl>
                  <Switch
                    checked={field.value}
                    onCheckedChange={field.onChange}
                  />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        {/* Submit */}
        <Button
          type="submit"
          size="lg"
          disabled={!watchFormatId}
          className="w-full h-12 text-base font-semibold shadow-md bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white transition-all transform hover:-translate-y-0.5"
        >
          <Download className="h-5 w-5 mr-2" />
          Download Now
        </Button>
      </form>
    </Form>
  );
}