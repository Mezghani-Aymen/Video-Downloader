export interface VideoFormat {
  format_id: string;
  ext: string;
  resolution: string;
  vcodec?: string | null;
  acodec?: string | null;
  filesize?: number | null;
  note?: string | null;
}

export interface VideoInfo {
  title: string;
  thumbnail?: string | null;
  duration?: number | null;
  uploader?: string | null;
  views?: number | null;
  formats: VideoFormat[];
  url: string;
}

export interface VideoRequestPayload {
  url: string;
}

export interface DownloadRequestPayload {
  url: string;
  format_id: string;
  download_subs: boolean;
  subs_lang?: string;
  custom_filename?: string | null;
  download_dir?: string | null;
}

export type DownloadStatus = "queued" | "downloading" | "completed" | "failed";

export interface DownloadTaskResponse {
  message: string;
  task_id: string;
  status: DownloadStatus;
}

export interface TaskStatusResponse {
  task_id: string;
  url: string;
  format_id: string;
  status: DownloadStatus;
  progress: number;
  title?: string | null;
  filename?: string | null;
  error?: string | null;
}

export interface DownloadItem {
  id: string;
  title: string;
  url: string;
  thumbnail?: string | null;
  formatId: string;
  resolution: string;
  ext: string;
  status: DownloadStatus;
  progress: number;
  speed?: string;
  downloadedSize?: string;
  totalSize?: string;
  sizeInBytes?: number;
  addedAt: string;
  error?: string;
}
