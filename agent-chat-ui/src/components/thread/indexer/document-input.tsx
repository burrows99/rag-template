"use client";

import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

interface DocumentInputProps {
  value: string;
  onChange: (value: string) => void;
  disabled?: boolean;
}

export function DocumentInput({ value, onChange, disabled }: DocumentInputProps) {
  return (
    <div className="flex flex-col gap-2">
      <Label htmlFor="documents" className="text-sm font-medium">
        Documents
      </Label>
      <Textarea
        id="documents"
        placeholder="Enter text to index..."
        value={value}
        onChange={(e) => onChange(e.target.value)}
        rows={10}
        disabled={disabled}
        className="resize-none"
      />
    </div>
  );
}
