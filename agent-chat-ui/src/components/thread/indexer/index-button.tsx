"use client";

import { Button } from "@/components/ui/button";
import { LoaderCircle } from "lucide-react";

interface IndexButtonProps {
  onClick: () => void;
  disabled: boolean;
  isLoading: boolean;
}

export function IndexButton({ onClick, disabled, isLoading }: IndexButtonProps) {
  return (
    <Button
      onClick={onClick}
      disabled={disabled}
      className="w-full"
      size="default"
    >
      {isLoading ? (
        <>
          <LoaderCircle className="mr-2 h-4 w-4 animate-spin" />
          Indexing...
        </>
      ) : (
        "Index Documents"
      )}
    </Button>
  );
}
