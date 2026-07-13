export default function Loading() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-4 animate-fade-in">
        <div className="relative">
          <div className="h-12 w-12 rounded-full border-2 border-aegis-400/30 border-t-aegis-400 animate-spin" />
          <div className="absolute inset-0 bg-aegis-400/20 blur-xl rounded-full" />
        </div>
        <p className="text-sm text-muted-foreground">Loading...</p>
      </div>
    </div>
  );
}
