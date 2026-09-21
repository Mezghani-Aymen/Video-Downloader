import React from "react";
import { Badge } from "./badge";
import { Video } from "lucide-react";

export function BrandLogo() {

    return (
        <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-tr from-violet-600 to-indigo-500 shadow-md shadow-violet-500/20 text-white">
                <Video className="h-5 w-5" />
            </div>
            <div>
                <div className="flex items-center gap-2">
                    <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
                        OmniStream
                    </h1>
                    <Badge variant="accent" className="text-[10px] px-1.5 py-0">
                        FREE
                    </Badge>
                </div>
                <p className="text-xs text-muted-foreground hidden sm:block">
                    Powered Video Extractor
                </p>
            </div>
        </div>
    );
}
