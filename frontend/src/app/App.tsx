import React from "react";
import { Header } from "@/components/layouts/Header";
import { Footer } from "@/components/layouts/Footer";
import Banner from "@/components/banner";
import { StatsCards } from "@/components/feature/StatsCards";
import { VideoPreviewCard } from "@/components/feature/VideoPreviewCard";
import { DownloadHistoryTable } from "@/components/feature/DownloadHistoryTable";
import { DownloadFormTabs } from "@/components/feature/DownloadFormTabs";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Toaster } from "@/components/ui/sonner";
import { useVideoDownloader } from "@/hooks/useVideoDownloader";
import { History } from "lucide-react";

export default function App() {
  const {
    downloads,
    analyzing,
    currentVideoInfo,
    analyzeVideo,
    startDownload,
    startBatchDownload,
    removeDownload,
    clearAll,
    retryDownload,
  } = useVideoDownloader();

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col font-sans selection:bg-purple-500 selection:text-white transition-colors duration-300">
      {/* Top Navigation */}
      <Header />

      {/* Main Container */}
      <main className="flex-1 container max-w-7xl mx-auto px-4 sm:px-6 py-8 space-y-8">
        {/* Hero Banner / Intro */}
        <Banner />

        {/* Dashboard Metrics */}
        <StatsCards downloads={downloads} />

        {/* Workstation Area (Forms & History) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-7 items-start">
          {/* Left Column: Interactive Forms Tabs */}
          <div className="lg:col-span-5 space-y-6">
            <DownloadFormTabs
              onAnalyze={analyzeVideo}
              onStartDownload={startDownload}
              onStartBatchDownload={startBatchDownload}
              isAnalyzing={analyzing}
              videoInfo={currentVideoInfo}
            />
          </div>

          {/* Right Column: Preview & History */}
          <div className="lg:col-span-7 space-y-6">
            {currentVideoInfo && (
              <div className="space-y-2">
                <h3 className="text-sm font-semibold text-muted-foreground uppercase tracking-wider">
                  Analyzed Media
                </h3>
                <VideoPreviewCard info={currentVideoInfo} />
              </div>
            )}

            <Card className="border-border/80 shadow-md">
              <CardHeader className="pb-4">
                <CardTitle className="text-lg flex items-center gap-2">
                  <History className="h-5 w-5 text-primary" />
                  Recent Queue
                </CardTitle>
              </CardHeader>
              <CardContent>
                <DownloadHistoryTable
                  downloads={downloads}
                  onRemove={removeDownload}
                  onClearAll={clearAll}
                  onRetry={retryDownload}
                />
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <Footer />

      {/* Toast Notification Container */}
      <Toaster position="bottom-right" richColors />
    </div>
  );
}