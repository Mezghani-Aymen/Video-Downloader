import { VideoApiService } from "./videoService";
import { MockVideoService } from "./mockVideoService";
import { IVideoService } from "./types";

export * from "./types";
export * from "./apiClient";
export * from "./config";
export { VideoApiService, MockVideoService };

/**
 * Default singleton instance of the video API service adhering to IVideoService.
 */
export const videoApi: IVideoService = new VideoApiService();
