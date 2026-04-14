import type { InputHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Input({ className, ...props }: InputHTMLAttributes<HTMLInputElement>) {
  return (
    <input
      className={cn(
        "w-full rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment outline-none ring-0 placeholder:text-parchment/35 focus:border-bronze/60",
        className,
      )}
      {...props}
    />
  );
}

