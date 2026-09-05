import { Download, Sparkles } from "lucide-react";
import React from "react";


function Banner() {
    return (
        <div className="relative overflow-hidden rounded-3xl bg-gradient-to-r from-violet-600/15 via-indigo-600/10 to-purple-600/15 border p-6 sm:p-8">
            <div className="relative z-10 max-w-2xl space-y-3">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-xs font-medium text-primary">
                    <Sparkles className="h-3.5 w-3.5" />
                    Video Downloader
                </div>
                <h2 className="text-2xl sm:text-3xl font-extrabold tracking-tight">
                    High-Speed Video Extractor & Converter
                </h2>
                <p className="text-sm sm:text-base text-muted-foreground leading-relaxed">
                    Paste any public media link to parse formats, download up to 4K Ultra HD streams, extract high-bitrate MP3 audio, and embed automated subtitles.
                </p>
            </div>
            <div className="absolute right-[-40px] bottom-[-40px] opacity-10 pointer-events-none hidden md:block">
                <Download className="w-80 h-80 text-primary" />
            </div>
        </div>)
}

export default Banner;