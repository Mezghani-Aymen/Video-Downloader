import { LucideIcon } from "lucide-react";
import { TabsTrigger } from "@/components/ui/tabs";
import React from "react";

interface TabTriggerItemProps {
  value: string;
  label: string;
  Icon: LucideIcon;
}

export function TabTriggerItem({ value, label, Icon }: TabTriggerItemProps) {
  return (
    <TabsTrigger value={value} className="rounded-lg gap-2 text-sm font-semibold">
      <Icon className="h-4 w-4" />
      {label}
    </TabsTrigger>
  );
}