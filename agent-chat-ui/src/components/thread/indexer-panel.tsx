"use client";

import { useState } from "react";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
} from "@/components/ui/sheet";
import { toast } from "sonner";
import { createClient } from "@/providers/client";
import { getApiKey } from "@/lib/api-key";
import { Database } from "lucide-react";
import { DocumentInput } from "./indexer/document-input";
import { IndexerConfig } from "./indexer/indexer-config";
import { IndexButton } from "./indexer/index-button";

interface IndexerPanelProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  apiUrl: string | null;
  userId: string;
  retrieverProvider: string;
}

export function IndexerPanel({
  open,
  onOpenChange,
  apiUrl,
  userId,
  retrieverProvider,
}: IndexerPanelProps) {
  const [documents, setDocuments] = useState("");
  const [isIndexing, setIsIndexing] = useState(false);

  const handleIndex = async () => {
    if (!documents.trim()) {
      toast.error("Please enter documents to index");
      return;
    }

    if (!apiUrl) {
      toast.error("API URL not configured");
      return;
    }

    setIsIndexing(true);

    try {
      const client = createClient(apiUrl, getApiKey() ?? undefined);

      await client.runs.create(null, "indexer", {
        input: { docs: documents },
        config: {
          configurable: {
            user_id: userId,
            retriever_provider: retrieverProvider,
          },
        },
      });

      toast.success("Documents indexed successfully", {
        description: `Indexed for user: ${userId}`,
      });

      setDocuments("");
      onOpenChange(false);
    } catch (error) {
      console.error("Indexing error:", error);
      toast.error("Failed to index documents", {
        description: error instanceof Error ? error.message : "Unknown error",
      });
    } finally {
      setIsIndexing(false);
    }
  };

  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent side="right" className="w-full sm:max-w-md">
        <SheetHeader>
          <SheetTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Index Documents
          </SheetTitle>
          <SheetDescription>
            Add documents to your knowledge base for retrieval.
          </SheetDescription>
        </SheetHeader>

        <div className="flex flex-col gap-4 p-4">
          <DocumentInput
            value={documents}
            onChange={setDocuments}
            disabled={isIndexing}
          />

          <IndexerConfig
            userId={userId}
            retrieverProvider={retrieverProvider}
          />

          <IndexButton
            onClick={handleIndex}
            disabled={isIndexing || !documents.trim()}
            isLoading={isIndexing}
          />
        </div>
      </SheetContent>
    </Sheet>
  );
}
