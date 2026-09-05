import React, { ElementType } from "react";
import { IconType } from "react-icons";

interface SocialLinkProps {
  href: string;
  aria: string;
  iconComponentName: IconType | ElementType;
}

export function SocialLink({ href, aria, iconComponentName: Icon }: SocialLinkProps) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={aria}
      className="transition-colors duration-200 hover:text-purple-500"
    >
      <Icon className="h-5 w-5" />
    </a>
  );
}