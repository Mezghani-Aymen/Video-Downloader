import { SocialLink } from "@/components/ui/socialLink";
import React from "react";
import { FaGithub, FaLinkedin } from "react-icons/fa6";


export function Footer() {
    return (
        <footer className="border-t py-6 text-center text-xs text-muted-foreground bg-muted/20 mt-12">
            <div className="container max-w-7xl mx-auto px-4 flex flex-col sm:flex-row items-center justify-between gap-4">
                <p>© 2026 OmniStream Video Downloader. Created by <span className="text-purple-400">Mezghani Mohamed Aymen</span>.</p>

                <div className="flex items-center gap-4 text-muted-foreground font-medium">
                    <SocialLink
                        href="https://github.com/Mezghani-Aymen/"
                        aria="GitHub Profile"
                        iconComponentName={FaGithub}
                    />

                    <span>•</span>

                    <SocialLink
                        href="https://www.linkedin.com/in/mezghani-med-aymen"
                        aria="Linkedin Profile"
                        iconComponentName={FaLinkedin}
                    />
                </div>
            </div>
        </footer>)

}