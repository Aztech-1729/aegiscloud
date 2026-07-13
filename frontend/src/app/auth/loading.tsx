export default function AuthLoading() {
  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="flex flex-col items-center gap-4 animate-fade-in">
        <div className="relative">
          <div className="h-10 w-10 rounded-full border-2 border-aegis-400/30 border-t-aegis-400 animate-spin" />
          <div className="absolute inset-0 bg-aegis-400/20 blur-xl rounded-full" />
        </div>
      </div>
    </div>
  );
}
