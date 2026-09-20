import React, { useState } from "react";
import { Download, Layers } from "lucide-react";
import { VideoInfo } from "@/types";
import { Tabs, TabsList } from "@/components/ui/tabs";
import { TabTriggerItem } from "@/components/ui/tabTriggerItem";
import { TabFormCard } from "@/components/ui/tabFormCard";
import { SingleVideoDownloadForm } from "@/components/forms/SingleVideoDownloadForm";
import { BatchDownloadForm } from "@/components/forms/BatchDownloadForm";

interface DownloadFormTabsProps {
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
  onStartBatchDownload: (urls: string[], format: string, downloadSubs: boolean) => void;
  isAnalyzing: boolean;
  videoInfo: VideoInfo | null;
}

export function DownloadFormTabs({
  onAnalyze,
  onStartDownload,
  onStartBatchDownload,
  isAnalyzing,
  videoInfo,
}: DownloadFormTabsProps) {
  const [activeTab, setActiveTab] = useState<string>("single");

  return (
    <Tabs
      defaultValue="single"
      value={activeTab}
      onValueChange={setActiveTab}
      className="w-full"
    >
      <TabsList className="grid w-full grid-cols-1 h-12 bg-muted/60 p-1 rounded-xl">
        <TabTriggerItem value="single" label="Single Download" Icon={Download} />
        {/* <TabTriggerItem value="batch" label="Batch Download" Icon={Layers} /> */}
      </TabsList>

      {/* Single Video Tab */}
      <TabFormCard
        value="single"
        title="Video Extractor Form"
        description="Extract and download videos from various platforms with ease."
      >
        <SingleVideoDownloadForm
          onAnalyze={onAnalyze}
          onStartDownload={onStartDownload}
          isAnalyzing={isAnalyzing}
          videoInfo={videoInfo}
        />
      </TabFormCard>

      {/* Batch Video Tab */}
      {/* <TabFormCard
        value="batch"
        title="Batch Download Form"
        description="Process multiple video URLs simultaneously with custom thread concurrency."
      >
        <BatchDownloadForm onStartBatchDownload={onStartBatchDownload} />
      </TabFormCard> */}
    </Tabs>
  );
}
