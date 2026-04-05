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
    CardTitle
} from "../components/ui/card";
import {
    Eye,
    EyeOff,
    CheckCircle2,
    Circle
} from "lucide-react";
// --- 1. Import the ApiClient hook ---
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
    // Enforcing security requirements to prevent weak passwords
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

        // 1. Basic Validation
        if (!name || !title || !university || !email || !password || !confirmPassword) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }

        // 2. Security Strength Check (Enforcing minimum 3/5 requirements)
        if (strengthScore < 3) {
            setError("Your password is too weak. Please meet at least 3 security requirements.");
            setIsLoading(false);
            return;
        }

        // 3. Password Match Check
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setIsLoading(false);
            return;
        }

        try {
            const { data, errorMessage } = await authClient.register(
                name,
                title,
                university,
                email,
                password
            );

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            console.log('Instructor registration successful:', data.instructor_id);
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
                        {/* Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="name">Full Name</Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="e.g., Dr. Ada Lovelace"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                required
                            />
                        </div>
                        {/* Title Field */}
                        <div className="grid gap-2">
                            <Label htmlFor="title">Title</Label>
                            <Input
                                id="title"
                                type="text"
                                placeholder="e.g., Associate Professor"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                required
                            />
                        </div>
                        {/* University Field */}
                        <div className="grid gap-2">
                            <Label htmlFor="university">University</Label>
                            <Input
                                id="university"
                                type="text"
                                placeholder="e.g., Tech University"
                                value={university}
                                onChange={(e) => setUniversity(e.target.value)}
                                required
                            />
                        </div>
                        {/* Email */}
                        <div className="grid gap-2">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="ada@example.com"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>

                        {/* Password Section with Strength Meter */}
                        <div className="grid gap-2">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <button
                                    type="button"
                                    onClick={() => setShowPassword(!showPassword)}
                                    className="text-xs text-muted-foreground hover:text-primary flex items-center gap-1"
                                >
                                    {showPassword ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                                    {showPassword ? "Hide" : "Show"}
                                </button>
                            </div>
                            <Input
                                id="password"
                                type={showPassword ? "text" : "password"}
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />

                            {/* Strength Indicator Overlay */}
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

                        <div className="grid gap-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input
                                id="confirmPassword"
                                type={showPassword ? "text" : "password"}
                                placeholder="********"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>

                        {/* Error Message */}
                        {error && <p className="text-sm text-destructive font-medium">{error}</p>}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Registering..." : "Create Account"}
                        </Button>

                        {/* Link back to Login */}
                        <Button
                            type="button"
                            variant="link"
                            className="w-full text-sm font-bold uppercase tracking-widest text-muted-foreground"
                            onClick={() => navigate('/login')}
                        >
                            Already registered? <span className="text-primary ml-1.5 underline">Sign In</span>
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}