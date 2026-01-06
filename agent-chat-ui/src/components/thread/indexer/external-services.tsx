"use client";

import { Button } from "@/components/ui/button";
import { Database } from "lucide-react";
import { Separator } from "@/components/ui/separator";

interface DataLoaderButtonsProps {
  disabled?: boolean;
}

export function DataLoaderButtons({ disabled = false }: DataLoaderButtonsProps) {
  const dataSources = [
    {
      name: "Adminer",
      description: "Manage Azure SQL data",
      icon: Database,
      url: "http://localhost:8080",
      color: "text-purple-600",
    },
  ];

  const openDataSource = (url: string) => {
    window.open(url, "_blank", "noopener,noreferrer");
  };

  return (
    <div className="space-y-3">
      <Separator />
      
      <div>
        <h3 className="text-sm font-medium mb-2">
          Data Source Loaders
        </h3>
        <p className="text-xs text-muted-foreground mb-3">
          Load documents from external sources for indexing
        </p>
      </div>

      <div className="grid grid-cols-1 gap-2">
        {dataSources.map((source) => {
          const Icon = source.icon;
          return (
            <Button
              key={source.name}
              variant="outline"
              size="sm"
              className="h-auto flex flex-col items-start p-3 gap-1"
              onClick={() => openDataSource(source.url)}
              disabled={disabled}
            >
              <div className="flex items-center gap-2 w-full">
                <Icon className={`h-4 w-4 ${source.color}`} />
                <span className="text-xs font-medium">{source.name}</span>
              </div>
              <span className="text-xs text-muted-foreground">
                {source.description}
              </span>
            </Button>
          );
        })}
      </div>

      <p className="text-xs text-muted-foreground mt-2">
        💡 Prepare data in these tools, then use indexer to load
      </p>
    </div>
  );
}
