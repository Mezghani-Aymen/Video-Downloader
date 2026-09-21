import React from "react";
import { Button } from "@/components/ui/button";
import { BrandLogo } from "@/components/ui/brandLogo";
import { useTheme } from "@/hooks/useTheme";
import { Sun, Moon } from "lucide-react";
import { ServerStatusBadge } from "../ui/serverStatusBadge";


export function Header() {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="sticky top-0 z-40 w-full border-b bg-background/80 backdrop-blur-md transition-all">
      <div className="container max-w-7xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6">
        {/* Brand Logo & Title */}
        <BrandLogo />

        {/* Right side actions */}
        <div className="flex items-center gap-3">
          {/* Live Server Status Badge */}
          <ServerStatusBadge />

          {/* Theme Toggle Button */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="rounded-xl h-9 w-9"
            title="Toggle theme"
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4 text-amber-400" />
            ) : (
              <Moon className="h-4 w-4 text-slate-700" />
            )}
          </Button>

          {/* Settings Modal */}
          {/* <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" className="rounded-xl gap-1.5 text-xs font-medium">
                <SettingsIcon className="h-3.5 w-3.5" />
                Settings
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-lg">
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <SettingsIcon className="h-5 w-5 text-primary" />
                  Preferences &amp; Configuration
                </DialogTitle>
              </DialogHeader>
              <SettingsForm />
            </DialogContent>
          </Dialog> */}
        </div>
      </div>
    </header>
  );
}
