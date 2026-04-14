import type { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Button({ className, ...props }: ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      className={cn(
        "rounded-full border border-bronze/50 bg-bronze/15 px-4 py-2 text-sm font-medium text-parchment transition hover:border-bronze hover:bg-bronze/25 disabled:opacity-50",
        className,
      )}
      {...props}
    />
  );
}

