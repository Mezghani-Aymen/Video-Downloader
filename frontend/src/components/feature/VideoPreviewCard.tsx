import React from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { VideoInfo } from "@/types";
import { Clock, Eye, User, Film, CheckCircle } from "lucide-react";

interface VideoPreviewCardProps {
  info: VideoInfo;
}

export function VideoPreviewCard({ info }: VideoPreviewCardProps) {
  const formatDuration = (seconds?: number) => {
    if (!seconds) return "Unknown";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
  };

  return (
    <Card className="overflow-hidden border-primary/20 bg-card/70 backdrop-blur shadow-lg animate-in fade-in zoom-in-95 duration-300">
      <CardContent className="p-0">
        <div className="flex flex-col sm:flex-row">
          {/* Thumbnail Preview */}
          <div className="relative sm:w-64 h-44 sm:h-auto shrink-0 bg-muted overflow-hidden group">
            <img
              src={info.thumbnail || "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800"}
              alt={info.title}
              className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
            />
            <div className="absolute bottom-2 right-2 px-2 py-0.5 rounded bg-black/80 text-white text-xs font-mono flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {formatDuration(info.duration)}
            </div>
            <div className="absolute top-2 left-2">
              <Badge variant="accent" className="gap-1 bg-black/60 text-white backdrop-blur border-none">
                <Film className="h-3 w-3" />
                Preview Ready
              </Badge>
            </div>
          </div>

          {/* Details */}
          <div className="p-5 flex flex-col justify-between flex-1 space-y-4">
            <div>
              <h3 className="font-bold text-lg leading-snug line-clamp-2">{info.title}</h3>
              <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-muted-foreground">
                {info.uploader && (
                  <span className="flex items-center gap-1 font-medium">
                    <User className="h-3.5 w-3.5" />
                    {info.uploader}
                  </span>
                )}
                {info.views && (
                  <span className="flex items-center gap-1">
                    <Eye className="h-3.5 w-3.5" />
                    {info.views.toLocaleString()} views
                  </span>
                )}
              </div>
            </div>

            {/* Available Formats Badges */}
            <div className="space-y-1.5">
              <p className="text-xs font-semibold text-muted-foreground uppercase">Extracted Qualities:</p>
              <div className="flex flex-wrap gap-1.5">
                {info.formats.slice(0, 5).map((f, idx) => (
                  <Badge key={idx} variant="outline" className="text-xs bg-muted/30">
                    <CheckCircle className="h-3 w-3 text-emerald-500 mr-1" />
                    {f.resolution}
                  </Badge>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
