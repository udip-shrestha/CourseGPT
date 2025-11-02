import { GraduationCap } from "lucide-react";

export function NotFoundPage() {

  return (
    <div className="relative flex flex-col items-center justify-center min-h-[80vh] text-center px-6 overflow-hidden">
      {/* Subtle background halo using Tailwind gradients + opacity pulse */}
      <div className="absolute inset-0 -z-10 bg-gradient-to-b from-primary/10 to-transparent animate-pulse" />

      {/* Logo + Branding */}
      <div className="flex items-center gap-2 mb-6">
        <div className="relative">
          <GraduationCap className="h-10 w-10 text-primary animate-bounce" />
          {/* A soft glowing dot */}
          <span className="absolute bottom-1 right-0 w-2 h-2 rounded-full bg-primary animate-ping" />
        </div>
        <h1 className="text-3xl font-bold text-primary">CourseGPT</h1>
      </div>

      {/* 404 Text */}
      <h2 className="text-5xl font-extrabold tracking-tight mb-3">404</h2>
      <p className="text-lg text-muted-foreground mb-8 max-w-md">
        Oops! The page you’re looking for doesn’t exist or has been moved.
      </p>
    </div>
  );
}
