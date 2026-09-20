import React from "react";
import { useBackendStatus } from "@/hooks/useBackendStatus";
import { TooltipProvider, Tooltip, TooltipTrigger, TooltipContent } from "@radix-ui/react-tooltip";
import { Loader2, WifiOff, Wifi } from "lucide-react";


export function ServerStatusBadge() {
    const status = useBackendStatus();

    if (status === "checking") {
        return (
            <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-amber-500/10 text-amber-600 dark:text-amber-400 text-xs font-medium border border-amber-500/20 animate-pulse">
                <Loader2 className="h-3 w-3 animate-spin" />
                <span>Connecting…</span>
            </div>
        );
    }

    if (status === "disconnected") {
        return (
            <TooltipProvider delayDuration={200}>
                <Tooltip>
                    <TooltipTrigger asChild>
                        <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-red-500/10 text-red-600 dark:text-red-400 text-xs font-medium border border-red-500/20 cursor-default">
                            <span className="relative flex h-2 w-2">
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-red-500" />
                            </span>
                            <WifiOff className="h-3 w-3" />
                        </div>
                    </TooltipTrigger>
                    <TooltipContent side="bottom" className="text-xs">
                        Backend is unreachable. Check if the server is running.
                    </TooltipContent>
                </Tooltip>
            </TooltipProvider>
        );
    }

    return (
        <TooltipProvider delayDuration={200}>
            <Tooltip>
                <TooltipTrigger asChild>
                    <div className="hidden md:flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 text-xs font-medium border border-emerald-500/20 cursor-default">
                        <span className="relative flex h-2 w-2">
                            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500" />
                        </span>
                        <Wifi className="h-3 w-3" />
                        <span>Backend Online</span>
                    </div>
                </TooltipTrigger>
                <TooltipContent side="bottom" className="text-xs">
                    Connected to backend API.
                </TooltipContent>
            </Tooltip>
        </TooltipProvider>
    );
}
