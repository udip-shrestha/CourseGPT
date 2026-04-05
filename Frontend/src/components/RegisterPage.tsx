import { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import {
    Card,
    CardContent,
    CardDescription,
    CardHeader,
    CardTitle
} from "./ui/card";
import {
    Eye,
    EyeOff,
    CheckCircle2,
    Circle,
    AlertCircle
} from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

export function RegisterPage() {
    const navigate = useNavigate();
    const { authClient } = useApiClient();

    // Form State
    const [name, setName] = useState("");
    const [title, setTitle] = useState("");
    const [university, setUniversity] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    // UI State
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

    const strengthLabel = useMemo(() => {
        if (strengthScore <= 1) return "Very Weak";
        if (strengthScore === 2) return "Weak";
        if (strengthScore === 3) return "Medium";
        if (strengthScore === 4) return "Strong";
        return "Very Strong";
    }, [strengthScore]);

    // --- REAL-TIME MATCH CHECK ---
    const isMatching = confirmPassword.length > 0 && password === confirmPassword;
    const showMatchError = confirmPassword.length > 0 && password !== confirmPassword;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        if (!name || !title || !university || !email || !password || !confirmPassword) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }

        if (strengthScore < 3) {
            setError("Your password is too weak. Please meet at least 3 security requirements.");
            setIsLoading(false);
            return;
        }

        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setIsLoading(false);
            return;
        }

        try {
            // Removed 'data' from destructuring to solve TS6133 unused variable error
            const { errorMessage } = await authClient.register(
                name,
                title,
                university,
                email,
                password
            );

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            // Navigate to login after successful registration
            navigate('/login');
        } catch (err: any) {
            setError(err.message || "An unexpected error occurred.");
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="w-full flex items-center justify-center p-4">
            <Card className="w-full max-w-md shadow-md">
                <CardHeader>
                    <CardTitle>Register as Instructor</CardTitle>
                    <CardDescription>Enter your professional details.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        <div className="grid gap-2">
                            <Label htmlFor="name">Full Name</Label>
                            <Input id="name" placeholder="Dr. Jordan Smith" value={name} onChange={(e) => setName(e.target.value)} required />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input id="title" placeholder="Associate Professor" value={title} onChange={(e) => setTitle(e.target.value)} required />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="university">University</Label>
                            <Input id="university" placeholder="State University" value={university} onChange={(e) => setUniversity(e.target.value)} required />
                        </div>
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input id="email" type="email" placeholder="j.smith@university.edu" value={email} onChange={(e) => setEmail(e.target.value)} required />
                        </div>

                        {/* Password Section */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <button type="button" onClick={() => setShowPassword(!showPassword)} className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1">
                                    {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                                    {showPassword ? "Hide" : "Show"}
                                </button>
                            </div>
                            <Input id="password" type={showPassword ? "text" : "password"} placeholder="********" value={password} onChange={(e) => setPassword(e.target.value)} required />

                            {password.length > 0 && (
                                <div className="mt-1 space-y-2">
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
                                            <div key={idx} className={`flex items-center gap-2 text-[10px] uppercase font-bold ${req.test(password) ? 'text-emerald-600' : 'text-muted-foreground'}`}>
                                                {req.test(password) ? <CheckCircle2 className="h-2.5 w-2.5" /> : <Circle className="h-2.5 w-2.5 opacity-20" />}
                                                {req.label}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>

                        {/* Confirm Password Section with Real-time feedback */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="confirmPassword">Confirm Password</Label>
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
                            {isLoading ? "Registering..." : "Create Account"}
                        </Button>

                        <div className="text-center pt-2">
                            <button
                                type="button"
                                className="text-sm font-bold text-muted-foreground hover:text-primary transition-colors uppercase tracking-widest underline underline-offset-4"
                                onClick={() => navigate('/login')}
                            >
                                Already registered?
                            </button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}