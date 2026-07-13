import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Code2 } from "lucide-react";

export default function ApiDocsPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
      <Code2 className="h-16 w-16 text-aegis-400 mb-6" />
      <h1 className="text-4xl font-bold mb-4">API Reference</h1>
      <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
        The public API documentation and OpenAPI specifications are currently being finalized. Please check back soon!
      </p>
      <Link href="/">
        <Button variant="default">Return Home</Button>
      </Link>
    </div>
  );
}
