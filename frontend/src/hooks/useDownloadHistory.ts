import { useState, useEffect, useCallback } from "react";
import { DownloadItem, DownloadStatus } from "@/types";
import { toast } from "sonner";

const STORAGE_KEY = "video_downloader_history_v1";

export function useDownloadHistory() {
  const [downloads, setDownloads] = useState<DownloadItem[]>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : [];
    } catch {
      return [];
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(downloads));
    } catch (e) {
      console.error("Failed to save downloads to localStorage", e);
    }
  }, [downloads]);

  const addDownload = useCallback((item: DownloadItem) => {
    setDownloads((prev) => [item, ...prev]);
  }, []);

  const updateDownload = useCallback(
    (id: string, updates: Partial<DownloadItem>) => {
      setDownloads((prev) =>
        prev.map((item) => (item.id === id ? { ...item, ...updates } : item))
      );
    },
    []
  );

  const removeDownload = useCallback((id: string) => {
    setDownloads((prev) => prev.filter((d) => d.id !== id));
    toast.info("Item removed from list.");
  }, []);

  const clearAll = useCallback(() => {
    setDownloads([]);
    toast.info("Download history cleared.");
  }, []);

  const retryDownload = useCallback((id: string) => {
    setDownloads((prev) =>
      prev.map((item) =>
        item.id === id
          ? {
              ...item,
              status: "downloading" as DownloadStatus,
              progress: 0,
              error: undefined,
            }
          : item
      )
    );
    toast.info("Retrying download...");
  }, []);

  return {
    downloads,
    setDownloads,
    addDownload,
    updateDownload,
    removeDownload,
    clearAll,
    retryDownload,
  };
}
