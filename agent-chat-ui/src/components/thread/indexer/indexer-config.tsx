"use client";

interface IndexerConfigProps {
  userId: string;
  retrieverProvider: string;
}

export function IndexerConfig({ userId, retrieverProvider }: IndexerConfigProps) {
  return (
    <div className="rounded-md border border-gray-200 bg-gray-50 p-4">
      <div className="flex flex-col gap-2 text-xs text-gray-600">
        <div className="flex items-center justify-between">
          <span className="font-medium">User ID:</span>
          <span className="font-mono text-gray-800">{userId}</span>
        </div>
        <div className="flex items-center justify-between">
          <span className="font-medium">Retriever:</span>
          <span className="font-mono text-gray-800">{retrieverProvider}</span>
        </div>
      </div>
    </div>
  );
}
