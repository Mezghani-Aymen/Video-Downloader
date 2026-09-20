import { useState, useEffect, useRef } from "react";
import { getApiBaseUrl } from "@/services/config";

export type BackendStatus = "checking" | "connected" | "disconnected";

export function useBackendStatus(): BackendStatus {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const check = async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 4000);
      const res = await fetch(`${baseUrl}/api/video/settings`, {
        method: "GET",
        signal: controller.signal,
      });
      clearTimeout(timeout);
      setStatus(res.ok ? "connected" : "disconnected");
    } catch {
      setStatus("disconnected");
    }
  };

  useEffect(() => {
    check();
    timerRef.current = setInterval(check, 8000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  return status;
}
