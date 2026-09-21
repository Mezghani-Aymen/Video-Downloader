// src/components/ui/TabFormCard.tsx
import React, { ReactNode } from "react";
import { TabsContent } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { LucideIcon } from "lucide-react";

interface TabFormCardProps {
    value: string;
    title: string;
    description?: string;
    Icon?: LucideIcon;
    iconClassName?: string;
    iconPosition?: "left" | "right";
    children: ReactNode;
}

export function TabFormCard({
    value,
    title,
    description,
    children,
}: TabFormCardProps) {
    return (
        <TabsContent value={value} className="mt-6">
            <Card className="border-border/80 shadow-md">
                <CardHeader className="pb-4">
                    <CardTitle className="text-xl">{title}</CardTitle>
                    <CardDescription>
                        {description}
                    </CardDescription>
                </CardHeader>
                <CardContent>{children}</CardContent>
            </Card>
        </TabsContent>
    );
}