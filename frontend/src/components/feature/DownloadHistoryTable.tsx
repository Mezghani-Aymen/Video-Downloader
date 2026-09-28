import React from "react";
import { DownloadItem } from "@/types";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Button } from "@/components/ui/button";
import {
  Trash2,
  RefreshCw,
  Copy,
  CheckCircle2,
  AlertCircle,
  Loader2,
  Video,
  ListX,
} from "lucide-react";
import { toast } from "sonner";

interface DownloadHistoryTableProps {
  downloads: DownloadItem[];
  onRemove: (id: string) => void;
  onClearAll: () => void;
  onRetry: (id: string) => void;
}

export function DownloadHistoryTable({
  downloads,
  onRemove,
  onClearAll,
  onRetry,
}: DownloadHistoryTableProps) {
  const copyToClipboard = (url: string) => {
    navigator.clipboard.writeText(url);
    toast.success("Video URL copied to clipboard!");
  };

  if (downloads.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center border rounded-2xl bg-card/40 border-dashed space-y-3">
        <div className="h-12 w-12 rounded-2xl bg-muted/80 flex items-center justify-center text-muted-foreground">
          <Video className="h-6 w-6" />
        </div>
        <div className="space-y-1">
          <h4 className="font-semibold text-lg">No Active or Past Downloads</h4>
          <p className="text-sm text-muted-foreground max-w-sm">
            Enter a video URL in the form above to start downloading high quality videos and audio.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="font-bold text-lg">Downloads Task Queue</h3>
          <Badge variant="secondary" className="rounded-full">
            {downloads.length}
          </Badge>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={onClearAll}
          className="text-xs text-muted-foreground hover:text-destructive"
        >
          <ListX className="h-4 w-4 mr-1" />
          Clear Queue
        </Button>
      </div>

      <div className="border rounded-xl bg-card/60 backdrop-blur overflow-hidden shadow-xs">
        <Table>
          <TableHeader className="bg-muted/40">
            <TableRow>
              <TableHead className="w-[300px]">Video Title & Info</TableHead>
              <TableHead>Resolution</TableHead>
              <TableHead>Status & Progress</TableHead>
              <TableHead className="text-right">Speed / Time</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {downloads.map((item) => (
              <TableRow key={item.id} className="group">
                {/* Title & URL */}
                <TableCell className="font-medium">
                  <div className="flex items-center gap-3">
                    {item.thumbnail ? (
                      <img
                        src={item.thumbnail}
                        alt=""
                        className="w-12 h-8 rounded object-cover shrink-0 bg-muted"
                      />
                    ) : (
                      <div className="w-12 h-8 rounded bg-muted flex items-center justify-center shrink-0">
                        <Video className="h-4 w-4 text-muted-foreground" />
                      </div>
                    )}
                    <div className="space-y-0.5 max-w-[220px] sm:max-w-[280px]">
                      <p className="text-sm font-semibold truncate leading-tight" title={item.title}>
                        {item.title}
                      </p>
                      <p className="text-xs text-muted-foreground truncate font-mono" title={item.url}>
                        {item.url}
                      </p>
                    </div>
                  </div>
                </TableCell>

                {/* Format / Resolution */}
                <TableCell>
                  <Badge variant="outline" className="text-xs capitalize font-mono">
                    {item.resolution} ({item.ext})
                  </Badge>
                </TableCell>

                {/* Status & Progress */}
                <TableCell className="w-[200px]">
                  <div className="space-y-1.5">
                    <div className="flex items-center justify-between text-xs">
                      {item.status === "downloading" && (
                        <span className="flex items-center gap-1.5 text-indigo-500 font-semibold">
                          <Loader2 className="h-3.5 w-3.5 animate-spin" />
                          Downloading... {item.progress}%
                        </span>
                      )}
                      {item.status === "completed" && (
                        <span className="flex items-center gap-1.5 text-emerald-500 font-semibold">
                          <CheckCircle2 className="h-3.5 w-3.5" />
                          Completed
                        </span>
                      )}
                      {item.status === "failed" && (
                        <span className="flex items-center gap-1.5 text-destructive font-semibold">
                          <AlertCircle className="h-3.5 w-3.5" />
                          Failed
                        </span>
                      )}
                    </div>
                    {item.status === "downloading" && (
                      <Progress value={item.progress} className="h-2" />
                    )}
                  </div>
                </TableCell>

                {/* Speed / Added time */}
                <TableCell className="text-right text-xs font-mono text-muted-foreground">
                  <div>{item.status === "downloading" ? item.speed : item.addedAt}</div>
                </TableCell>

                {/* Actions */}
                <TableCell className="text-right">
                  <div className="flex items-center justify-end gap-1">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8"
                      title="Copy URL"
                      onClick={() => copyToClipboard(item.url)}
                    >
                      <Copy className="h-3.5 w-3.5" />
                    </Button>
                    {item.status === "failed" && (
                      <Button
                        variant="ghost"
                        size="icon"
                        className="h-8 w-8 text-amber-500"
                        title="Retry"
                        onClick={() => onRetry(item.id)}
                      >
                        <RefreshCw className="h-3.5 w-3.5" />
                      </Button>
                    )}
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 text-muted-foreground hover:text-destructive"
                      title="Remove"
                      onClick={() => onRemove(item.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
