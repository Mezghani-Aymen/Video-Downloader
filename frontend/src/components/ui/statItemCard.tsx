import { LucideIcon } from "lucide-react";
import { Card, CardContent } from "./card";
import React from "react";

export interface StatConfig {
    id: string;
    label: string;
    value: string | number;
    valueColor?: string;
    icon: LucideIcon;
    iconBgColor: string;
    iconTextColor: string;
    animateIcon?: boolean;
}

export function StatItemCard({ config }: { config: StatConfig }) {
    const Icon = config.icon;

    return (
        <Card className="bg-card/50 backdrop-blur border-muted/80 shadow-xs hover:shadow-md transition-shadow">
            <CardContent className="p-5 flex items-center justify-between">
                <div>
                    <p className="text-xs font-medium text-muted-foreground uppercase tracking-wider">
                        {config.label}
                    </p>
                    <h3 className={`text-2xl font-bold mt-1 ${config.valueColor ?? ""}`}>
                        {config.value}
                    </h3>
                </div>
                <div className={`h-10 w-10 rounded-xl flex items-center justify-center ${config.iconBgColor} ${config.iconTextColor}`}>
                    <Icon className={`h-5 w-5 ${config.animateIcon ? "animate-bounce" : ""}`} />
                </div>
            </CardContent>
        </Card>
    );
}