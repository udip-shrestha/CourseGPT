import { useState, useMemo } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "../components/ui/card";
import {
    Eye,
    EyeOff,
    CheckCircle2,
    Circle,
    AlertCircle,
    ShieldCheck
} from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

export function ResetPasswordPage() {
    const navigate = useNavigate();
    const [searchParams] = useSearchParams();
    const { authClient } = useApiClient();

    // Get email from URL (passed from RequestResetPage)
    const email = searchParams.get("email") || "";

    // Form State
    const [code, setCode] = useState("");
    const [newPassword, setNewPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    // UI State
    const [showPassword, setShowPassword] = useState(false);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [isSuccess, setIsSuccess] = useState(false);

    // --- PASSWORD STRENGTH LOGIC ---
    const passwordRequirements = useMemo(() => [
        { label: "At least 8 characters", test: (p: string) => p.length >= 8 },
        { label: "At least one uppercase letter", test: (p: string) => /[A-Z]/.test(p) },
        { label: "At least one lowercase letter", test: (p: string) => /[a-z]/.test(p) },
        { label: "At least one number", test: (p: string) => /[0-9]/.test(p) },
        { label: "At least one special character", test: (p: string) => /[^A-Za-z0-9]/.test(p) },
    ], []);

    const strengthScore = useMemo(() => {
        if (!newPassword) return 0;
        return passwordRequirements.filter(req => req.test(newPassword)).length;
    }, [newPassword, passwordRequirements]);

    const strengthColor = useMemo(() => {
        if (strengthScore <= 2) return "bg-destructive";
        if (strengthScore <= 4) return "bg-yellow-500";
        return "bg-emerald-500";
    }, [strengthScore]);

    const strengthLabel = useMemo(() => {
        if (strengthScore <= 1) return "Very Weak";
        if (strengthScore === 2) return "Weak";
        if (strengthScore === 3) return "Medium";
        if (strengthScore === 4) return "Strong";
        return "Very Strong";
    }, [strengthScore]);

    // Real-time Match Check
    const isMatching = confirmPassword.length > 0 && newPassword === confirmPassword;
    const showMatchError = confirmPassword.length > 0 && newPassword !== confirmPassword;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // 1. Validation
        if (!code || !newPassword || !confirmPassword) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }

        if (code.length !== 6) {
            setError("Please enter the 6-digit verification code.");
            setIsLoading(false);
            return;
        }

        if (strengthScore < 3) {
            setError("Your new password is too weak. Please meet more requirements.");
            setIsLoading(false);
            return;
        }

        if (newPassword !== confirmPassword) {
            setError("Passwords do not match.");
            setIsLoading(false);
            return;
        }

        try {
            // Calls POST /auth/confirm-password-reset
            const { errorMessage } = await authClient.confirmPasswordReset(
                email,
                code,
                newPassword
            );

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            setIsSuccess(true);
            setTimeout(() => navigate('/login'), 3000);

        } catch (err: any) {
            setError(err.message || "Failed to reset password. The code may be invalid or expired.");
        } finally {
            setIsLoading(false);
        }
    };

    if (isSuccess) {
        return (
            <div className="w-full flex items-center justify-center p-4">
                <Card className="w-full max-w-md shadow-md text-center py-8">
                    <CardContent className="space-y-4">
                        <div className="flex justify-center">
                            <ShieldCheck className="h-16 w-16 text-emerald-500" />
                        </div>
                        <h2 className="text-2xl font-bold tracking-tight">Success!</h2>
                        <p className="text-muted-foreground text-sm">
                            Your password has been updated successfully. Redirecting you to login...
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="w-full flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-md">
                <CardHeader>
                    <CardTitle>Reset Password</CardTitle>
                    <CardDescription>Enter the code sent to {email}</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        {/* 6-Digit Code */}
                        <div className="grid gap-2">
                            <Label htmlFor="code">Verification Code</Label>
                            <Input
                                id="code"
                                type="text"
                                maxLength={6}
                                placeholder="123456"
                                className="text-center tracking-[0.5em] font-mono text-lg"
                                value={code}
                                onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                                required
                            />
                        </div>

                        {/* New Password */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="newPassword">New Password</Label>
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="text-xs text-muted-foreground hover:text-primary transition-colors flex items-center gap-1"
                                >
                                    {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                                    {showPassword ? "Hide" : "Show"}
                                </button>
                            </div>
                            <Input
                                id="newPassword"
                                type={showPassword ? "text" : "password"}
                                placeholder="Min 8 characters"
                                value={newPassword}
                                onChange={(e) => setNewPassword(e.target.value)}
                                required
                            />

                            {/* Strength Meter */}
                            {newPassword.length > 0 && (
                                <div className="mt-1 space-y-2 animate-in fade-in duration-200">
                                    <div className="flex justify-between items-center text-[10px] uppercase font-bold tracking-wider">
                                        <span className="text-muted-foreground">Strength: {strengthLabel}</span>
                                        <span className={strengthScore >= 3 ? "text-emerald-600" : "text-muted-foreground"}>{strengthScore}/5</span>
                                    </div>
                                    <div className="h-1 w-full bg-muted rounded-full overflow-hidden">
                                        <div
                                            className={`h-full ${strengthColor} transition-all duration-300`}
                                            style={{ width: `${(strengthScore / 5) * 100}%` }}
                                        />
                                    </div>
                                    <div className="grid grid-cols-1 gap-1">
                                        {passwordRequirements.map((req, idx) => (
                                            <div key={idx} className={`flex items-center gap-2 text-[10px] uppercase font-bold transition-colors ${req.test(newPassword) ? 'text-emerald-600' : 'text-muted-foreground'}`}>
                                                {req.test(newPassword) ? <CheckCircle2 className="h-2.5 w-2.5" /> : <Circle className="h-2.5 w-2.5 opacity-20" />}
                                                {req.label}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Confirm New Password */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="confirmPassword">Confirm New Password</Label>
                                {isMatching && (
                                    <span className="text-[10px] font-bold text-emerald-600 flex items-center gap-1 uppercase tracking-wider">
                                        <CheckCircle2 className="h-2.5 w-2.5" /> Matches
                                    </span>
                                )}
                                {showMatchError && (
                                    <span className="text-[10px] font-bold text-destructive flex items-center gap-1 uppercase tracking-wider">
                                        <AlertCircle className="h-2.5 w-2.5" /> No Match
                                    </span>
                                )}
                            </div>
                            <Input
                                id="confirmPassword"
                                type={showPassword ? "text" : "password"}
                                placeholder="********"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                                className={showMatchError ? "border-destructive focus-visible:ring-destructive" : ""}
                            />
                        </div>

                        {error && <p className="text-sm text-destructive font-medium">{error}</p>}

                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Updating..." : "Reset Password"}
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}