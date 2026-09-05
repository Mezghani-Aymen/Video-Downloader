import React, { useMemo } from "react";
import { DownloadItem } from "@/types";
import { Download, CheckCircle2, ArrowDownCircle, HardDrive } from "lucide-react";
import { formatBytes } from "@/lib/utils";
import { StatConfig, StatItemCard } from "../ui/statItemCard";

interface StatsCardsProps {
  downloads: DownloadItem[];
}

export function StatsCards({ downloads }: StatsCardsProps) {
  const statsConfig = useMemo(() => {
    const totalCount = downloads.length;
    const activeCount = downloads.filter((d) => d.status === "downloading").length;
    const completedDownloads = downloads.filter((d) => d.status === "completed");
    const completedCount = completedDownloads.length;

    // Calculate actual total size from downloads if `size` exists, else fallback to average estimate
    const totalBytes = completedDownloads.reduce((acc, item) => {
      return acc + (item.sizeInBytes ?? 142 * 1024 * 1024);
    }, 0);

    const stats: StatConfig[] = [
      {
        id: "total",
        label: "Total Downloads",
        value: totalCount,
        icon: Download,
        iconBgColor: "bg-violet-500/10",
        iconTextColor: "text-violet-600 dark:text-violet-400",
      },
      {
        id: "active",
        label: "Active Queue",
        value: activeCount,
        valueColor: "text-indigo-500",
        icon: ArrowDownCircle,
        iconBgColor: "bg-indigo-500/10",
        iconTextColor: "text-indigo-600 dark:text-indigo-400",
        animateIcon: activeCount > 0, // Only animate bounce when active tasks exist
      },
      {
        id: "completed",
        label: "Completed Tasks",
        value: completedCount,
        valueColor: "text-emerald-500",
        icon: CheckCircle2,
        iconBgColor: "bg-emerald-500/10",
        iconTextColor: "text-emerald-600 dark:text-emerald-400",
      },
      {
        id: "storage",
        label: "Storage Saved",
        value: formatBytes(totalBytes),
        icon: HardDrive,
        iconBgColor: "bg-amber-500/10",
        iconTextColor: "text-amber-600 dark:text-amber-400",
      },
    ];

    return stats;
  }, [downloads]);

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {statsConfig.map((config) => (
        <StatItemCard key={config.id} config={config} />
      ))}
    </div>
  );
}