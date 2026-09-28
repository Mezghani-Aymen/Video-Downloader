import React, { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { settingsSchema, SettingsFormValues } from "@/types";
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
import { Server, Folder, Bell, Save, FolderOpen, HardDrive } from "lucide-react";
import { toast } from "sonner";
import { getApiBaseUrl } from "@/services/config";

const SETTINGS_STORAGE_KEY = "video_downloader_settings_v1";

const DEFAULT_SETTINGS: SettingsFormValues = {
  apiBaseUrl: "http://localhost:8000",
  defaultQuality: "1080p",
  autoDownloadSubtitles: false,
  subtitlesLanguage: "en",
  downloadDirectory: "",
  enableNotifications: true,
  themeMode: "dark",
};

interface SettingsFormProps {
  onSave?: (settings: SettingsFormValues) => void;
}

export function SettingsForm({ onSave }: SettingsFormProps) {
  const [loadingBackendDir, setLoadingBackendDir] = useState(false);
  const [systemDownloadsDir, setSystemDownloadsDir] = useState<string>("");

  const getInitialValues = (): SettingsFormValues => {
    try {
      const saved = localStorage.getItem(SETTINGS_STORAGE_KEY);
      if (saved) return { ...DEFAULT_SETTINGS, ...JSON.parse(saved) };
    } catch {
      // fallback
    }
    return DEFAULT_SETTINGS;
  };

  const form = useForm<SettingsFormValues>({
    resolver: zodResolver(settingsSchema),
    defaultValues: getInitialValues(),
  });

  // On mount: fetch the current server-side directory and system Downloads path
  useEffect(() => {
    const fetchBackendSettings = async () => {
      try {
        setLoadingBackendDir(true);
        const baseUrl = getApiBaseUrl();
        const res = await fetch(`${baseUrl}/api/video/settings`, { method: "GET" });
        if (res.ok) {
          const data = await res.json();
          setSystemDownloadsDir(data.system_downloads_dir || "");
          // Only pre-fill if the field is blank
          if (!form.getValues("downloadDirectory")) {
            form.setValue("downloadDirectory", data.default_download_dir || "");
          }
        }
      } catch {
        // Backend not reachable — use stored value
      } finally {
        setLoadingBackendDir(false);
      }
    };
    fetchBackendSettings();
  }, []);

  /**
   * OS-native folder picker using the File System Access API.
   * Falls back to a plain text prompt on unsupported browsers.
   */
  const handleBrowseFolder = async () => {
    // @ts-ignore — showDirectoryPicker is a modern browser API
    if (typeof window !== "undefined" && "showDirectoryPicker" in window) {
      try {
        // @ts-ignore
        const dirHandle = await window.showDirectoryPicker({ mode: "readwrite" });
        form.setValue("downloadDirectory", dirHandle.name, { shouldValidate: true });
        toast.info(
          `Folder "${dirHandle.name}" selected. The server will save files there if it has access to the same path.`
        );
      } catch (err: any) {
        if (err?.name !== "AbortError") {
          toast.error("Could not open folder picker: " + err.message);
        }
      }
    } else {
      // Fallback: prompt for a manual path
      const path = window.prompt(
        "Folder picker is not supported in this browser.\nPlease enter the full directory path manually:"
      );
      if (path && path.trim()) {
        form.setValue("downloadDirectory", path.trim(), { shouldValidate: true });
      }
    }
  };

  const handleUseSystemDownloads = () => {
    if (systemDownloadsDir) {
      form.setValue("downloadDirectory", systemDownloadsDir, { shouldValidate: true });
      toast.success("Using system Downloads folder.");
    }
  };

  const onSubmit = async (values: SettingsFormValues) => {
    try {
      localStorage.setItem(SETTINGS_STORAGE_KEY, JSON.stringify(values));

      // Push download directory preference to backend
      if (values.downloadDirectory) {
        try {
          const baseUrl = values.apiBaseUrl.replace(/\/+$/, "");
          await fetch(`${baseUrl}/api/video/settings`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ download_dir: values.downloadDirectory }),
          });
        } catch {
          // Non-fatal — saved locally regardless
        }
      }

      toast.success("Settings saved successfully!");
      if (onSave) onSave(values);
    } catch (e: any) {
      toast.error("Failed to save settings: " + e.message);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <div className="space-y-4">
          {/* Backend URL */}
          <FormField
            control={form.control}
            name="apiBaseUrl"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="font-semibold flex items-center gap-2">
                  <Server className="h-4 w-4 text-emerald-500" />
                  Backend API Endpoint
                </FormLabel>
                <FormControl>
                  <Input placeholder="https://video-downloader-ru4k.onrender.com" {...field} />
                </FormControl>
                <FormDescription>
                  FastAPI server URL for extraction &amp; processing backend tasks.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />

          {/* Download Directory with OS Folder Picker */}
          <FormField
            control={form.control}
            name="downloadDirectory"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="font-semibold flex items-center gap-2">
                  <Folder className="h-4 w-4 text-amber-500" />
                  Default Save Location
                </FormLabel>
                <div className="flex gap-2">
                  <FormControl>
                    <Input
                      placeholder={loadingBackendDir ? "Loading…" : "e.g. C:\\Users\\You\\Downloads"}
                      className="flex-1"
                      {...field}
                    />
                  </FormControl>
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    className="shrink-0 gap-1.5"
                    onClick={handleBrowseFolder}
                    title="Browse for folder"
                  >
                    <FolderOpen className="h-4 w-4" />
                    Browse
                  </Button>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  {systemDownloadsDir && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      className="h-7 text-xs gap-1 text-muted-foreground hover:text-foreground"
                      onClick={handleUseSystemDownloads}
                    >
                      <HardDrive className="h-3.5 w-3.5" />
                      Use system Downloads ({systemDownloadsDir.split(/[/\\]/).pop()})
                    </Button>
                  )}
                </div>
                <FormDescription>
                  Server path where downloaded media files will be saved. Click <strong>Browse</strong> to select a folder using your OS dialog.
                </FormDescription>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t pt-4">
          <FormField
            control={form.control}
            name="defaultQuality"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="font-semibold">Default Quality</FormLabel>
                <Select onValueChange={field.onChange} defaultValue={field.value}>
                  <FormControl>
                    <SelectTrigger>
                      <SelectValue placeholder="Select default" />
                    </SelectTrigger>
                  </FormControl>
                  <SelectContent>
                    <SelectItem value="best">Best Quality</SelectItem>
                    <SelectItem value="1080p">1080p Full HD</SelectItem>
                    <SelectItem value="720p">720p HD</SelectItem>
                  </SelectContent>
                </Select>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="subtitlesLanguage"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="font-semibold">Subtitle Language Code</FormLabel>
                <FormControl>
                  <Input placeholder="en, es, fr…" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <div className="space-y-3 p-4 rounded-xl bg-muted/40 border">
          <FormField
            control={form.control}
            name="enableNotifications"
            render={({ field }) => (
              <FormItem className="flex flex-row items-center justify-between">
                <div className="space-y-0.5">
                  <FormLabel className="text-sm font-semibold flex items-center gap-1.5 cursor-pointer">
                    <Bell className="h-4 w-4 text-indigo-500" />
                    Toast Notifications
                  </FormLabel>
                  <FormDescription className="text-xs">
                    Show desktop alerts on download completion
                  </FormDescription>
                </div>
                <FormControl>
                  <Switch checked={field.value} onCheckedChange={field.onChange} />
                </FormControl>
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" className="w-full h-11 text-base font-medium">
          <Save className="h-4 w-4 mr-2" />
          Save Configuration
        </Button>
      </form>
    </Form>
  );
}
