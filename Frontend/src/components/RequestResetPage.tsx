import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { useApiClient } from "../clients/ApiClientContext.tsx";
import { ArrowLeft } from "lucide-react";

export function RequestResetPage() {
    const navigate = useNavigate();
    const { authClient } = useApiClient();

    const [email, setEmail] = useState("");
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);
        setMessage(null);

        try {
            // Calls the POST /auth/request-password-reset endpoint
            const { errorMessage } = await authClient.requestPasswordReset(email);

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            setMessage("If this email is registered, you will receive a 6-digit code shortly.");

            // Navigate to the verification page after a short delay
            setTimeout(() => {
                navigate(`/reset-password?email=${encodeURIComponent(email)}`);
            }, 3000);

        } catch (err: any) {
            setError(err.message || "Failed to send reset code. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-md">
                <CardHeader>
                    <CardTitle>Forgot Password?</CardTitle>
                    <CardDescription>Enter your email to receive a reset code.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email Address</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="name@university.edu"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        {error && <p className="text-sm text-destructive font-medium">{error}</p>}
                        {message && <p className="text-sm text-emerald-600 font-medium">{message}</p>}

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Sending Code..." : "Send Reset Code"}
                        </Button>

                        <Button
                            type="button"
                            variant="ghost"
                            className="w-full flex items-center gap-2 text-muted-foreground"
                            onClick={() => navigate("/login")}
                        >
                            <ArrowLeft className="h-4 w-4" /> Back to Login
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}