import React, { useState } from "react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { useYouTubeAuth } from "@/hooks/useYouTubeAuth";
import { Youtube, ExternalLink, Loader2 } from "lucide-react";

export function YouTubeAuthDialog() {
  const { authState, isAuthorized, isPolling, startAuth, logout } = useYouTubeAuth();
  const [isOpen, setIsOpen] = useState(false);

  const handleStartAuth = () => {
    startAuth();
  };

  const isWaiting = authState?.state === "waiting_for_user";

  return (
    <Dialog open={isOpen} onOpenChange={setIsOpen}>
      <DialogTrigger asChild>
        <Button variant={isAuthorized ? "outline" : "default"} size="sm" className="gap-2">
          <Youtube className="w-4 h-4" />
          {isAuthorized ? "YouTube Connected" : "Connect YouTube"}
        </Button>
      </DialogTrigger>
      
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Youtube className="w-5 h-5 text-red-500" />
            Connect to YouTube
          </DialogTitle>
          <DialogDescription>
            Authenticate to bypass YouTube's anti-bot protections and download videos reliably.
          </DialogDescription>
        </DialogHeader>

        <div className="flex flex-col space-y-4 py-4">
          {isAuthorized ? (
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-sm text-muted-foreground">
                Your YouTube account is successfully connected to this browser session.
              </p>
              <Button variant="destructive" onClick={logout} className="w-full">
                Disconnect Account
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {!authState && !isPolling && (
                <Button onClick={handleStartAuth} className="w-full">
                  Start Authentication
                </Button>
              )}
              
              {(isPolling && !isWaiting) && (
                <div className="flex flex-col items-center justify-center py-6 space-y-3">
                  <Loader2 className="w-8 h-8 animate-spin text-primary" />
                  <p className="text-sm text-muted-foreground">Requesting authorization code from YouTube...</p>
                </div>
              )}

              {isWaiting && authState && (
                <div className="flex flex-col space-y-4">
                  <div className="p-4 bg-muted/50 rounded-lg space-y-2 border">
                    <p className="text-sm font-medium">1. Open this link on any device:</p>
                    <a 
                      href={authState.verification_url} 
                      target="_blank" 
                      rel="noreferrer"
                      className="text-primary text-sm flex items-center gap-1 hover:underline break-all"
                    >
                      {authState.verification_url}
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                  
                  <div className="p-4 bg-muted/50 rounded-lg space-y-2 border">
                    <p className="text-sm font-medium">2. Enter this code:</p>
                    <div className="flex items-center justify-center p-3 bg-background border rounded-md">
                      <span className="text-2xl font-mono font-bold tracking-widest">{authState.user_code}</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground pt-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Waiting for you to authorize...
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
