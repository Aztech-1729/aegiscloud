import Link from "next/link";
import { Button } from "@/components/ui/button";
import { BookOpen } from "lucide-react";

export default function DocsPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center p-24 text-center">
      <BookOpen className="h-16 w-16 text-aegis-400 mb-6" />
      <h1 className="text-4xl font-bold mb-4">Documentation</h1>
      <p className="text-xl text-muted-foreground mb-8 max-w-2xl">
        We are currently writing the comprehensive documentation for Aegis Cloud and the Aegis OS Optimizer agent. Please check back soon!
      </p>
      <Link href="/">
        <Button variant="default">Return Home</Button>
      </Link>
    </div>
  );
}
