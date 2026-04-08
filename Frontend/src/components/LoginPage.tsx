import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  Eye,
  EyeOff
} from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

export function LoginPage() {
  const navigate = useNavigate();
  const params = new URLSearchParams(window.location.search);
  const redirectTo = params.get("next");
  const { authClient } = useApiClient();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    // Basic email format validation
    if (!email.includes("@")) {
      setError("Please use your email address to log in.");
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
                  <div className="flex items-center gap-3">
                    <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1"
                    >
                      {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                      {showPassword ? "Hide" : "Show"}
                    </button>
                    <button
                        type="button"
                        onClick={() => navigate("/RequestResetPage")}
                        className="text-xs text-primary hover:underline font-medium"
                    >
                      Forgot password?
                    </button>
                  </div>
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