import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import {
  Eye,
  EyeOff,
  CheckCircle2,
  Circle
} from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

export function LoginPage() {
  const navigate = useNavigate();
  // read optional redirect target (e.g. ?next=/register-course?canvas_course_id=...)
  const params = new URLSearchParams(window.location.search);
  const redirectTo = params.get("next");
  const { authClient } = useApiClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // --- PASSWORD STRENGTH LOGIC ---
  const passwordRequirements = useMemo(() => [
    { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
    { label: "At least one uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
    { label: "At least one lowercase letter", test: (p: string) => /[a-z]/.test(p) },
    { label: "At least one number", test: (p: string) => /[0-9]/.test(p) },
    { label: "At least one special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
  ], []);

  const strengthScore = useMemo(() => {
    if (!password) return 0;
    return passwordRequirements.filter(req => req.test(password)).length;
  }, [password, passwordRequirements]);

  const strengthColor = useMemo(() => {
    if (strengthScore <= 2) return "bg-destructive";
    if (strengthScore <= 4) return "bg-yellow-500";
    return "bg-emerald-500";
  }, [strengthScore]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Basic validation
    if (!email.includes("@")) {
      setError("Please use your email address to log in, not your name.");
      setIsLoading(false);
      return;
    }

    // --- STRENGTH VALIDATION ---
    // Prevent login attempt if the password doesn't meet minimum complexity
    // (Blocking submission for scores below 3 to ensure account security)
    if (password.length > 0 && strengthScore < 3) {
      setError("Your password does not meet the minimum security requirements.");
      setIsLoading(false);
      return;
    }

    try {
      console.log("Login attempt for:", email);
      const { data, errorMessage } = await authClient.login(email, password);

      if (errorMessage) {
        throw new Error(errorMessage);
      }

      const instructorId = data.instructor_id;
      console.log("Login successful for instructor:", instructorId);

      if (redirectTo) {
        navigate(redirectTo);
      } else {
        navigate(`/instructors/${instructorId}/profile`);
      }
    } catch (err: any) {
      console.error("Login failed:", err);
      if (err instanceof TypeError && err.message === "Failed to fetch") {
        setError("Could not connect to the server. Please ensure it's running.");
      } else {
        setError(err.message || "Login failed. Please check your email and password.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
      // Restricted background and layout to match your original design
      <div className="w-full flex items-center justify-center p-4">
        <Card className="w-full max-w-md shadow-md">
          <CardHeader>
            <CardTitle>Login</CardTitle>
            <CardDescription>Sign in to your CourseGPT account</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="grid gap-4">
              {/* Email Input */}
              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input
                    id="email"
                    type="email"
                    placeholder="m@example.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    aria-invalid={!!error}
                />
              </div>

              {/* Password Input */}
              <div className="grid gap-2">
                <div className="flex items-center justify-between">
                  <Label htmlFor="password">Password</Label>
                  <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1"
                  >
                    {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                    {showPassword ? "Show" : "Hide"}
                  </button>
                </div>
                <Input
                    id="password"
                    type={showPassword ? "text" : "password"}
                    placeholder="********"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    aria-invalid={!!error}
                />

                {/* Password Strength Indicator (Integrated into the existing layout) */}
                {password.length > 0 && (
                    <div className="mt-1 space-y-2 animate-in fade-in duration-200">
                      <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
                        <div
                            className={`h-full ${strengthColor} transition-all duration-300`}
                            style={{ width: `${(strengthScore / 5) * 100}%` }}
                        />
                      </div>
                      <div className="grid grid-cols-1 gap-1">
                        {passwordRequirements.map((req, idx) => {
                          const met = req.test(password);
                          return (
                              <div key={idx} className={`flex items-center gap-2 text-[10px] uppercase font-bold transition-colors ${met ? 'text-emerald-600' : 'text-muted-foreground'}`}>
                                {met ? <CheckCircle2 className="h-2.5 w-2.5" /> : <Circle className="h-2.5 w-2.5 opacity-20" />}
                                {req.label}
                              </div>
                          );
                        })}
                      </div>
                    </div>
                )}
              </div>

              {/* Error Message Display */}
              {error && <p className="text-sm text-destructive font-medium">{error}</p>}

              {/* Sign In Button */}
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign in"}
              </Button>

              {/* Register Button */}
              <Button
                  type="button"
                  variant="outline"
                  className="w-full"
                  onClick={() => navigate("/register")}
                  disabled={isLoading}
              >
                Create New Account
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
  );
}