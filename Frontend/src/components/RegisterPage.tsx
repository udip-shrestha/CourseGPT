import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Label } from "./ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";

export function UserRegisterPage() {
    const navigate = useNavigate();
    const [name, setName] = useState(""); // Or separate firstName, lastName if needed
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = useState("");

    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);
        setError(null);

        // --- Basic Validation ---
        if (!name || !email || !password || !confirmPassword) {
            setError("Please fill out all fields.");
            setIsLoading(false);
            return;
        }
        if (password !== confirmPassword) {
            setError("Passwords do not match.");
            setIsLoading(false);
            return;
        }
        // Add more validation (email format, password strength) as needed
        // --- End Validation ---

        const userData = {
            name: name,
            email: email,
            password: password, // Send plain password - backend should hash it
        };

        console.log("Submitting User Registration:", userData);

        // --- Replace with your actual User Registration API call ---
        try {
            // Example:
            // const response = await fetch('/api/users/register', {
            //   method: 'POST',
            //   headers: { 'Content-Type': 'application/json' },
            //   body: JSON.stringify(userData),
            // });
            // if (!response.ok) {
            //   const errorData = await response.json();
            //   throw new Error(errorData.detail || 'Registration failed');
            // }
            // console.log('User registration successful');
            // navigate('/login'); // Redirect to login page after successful registration

            // Simulate API call
            await new Promise(resolve => setTimeout(resolve, 1500));
            console.log("Simulated user registration successful");
            navigate('/login'); // Go to login after fake success

        } catch (err: any) {
            console.error("User registration failed:", err);
            setError(err.message || "An unexpected error occurred during registration.");
        } finally {
            setIsLoading(false);
        }
        // --- End of API call section ---
    };

    return (
        // Centering container
        <div className="w-full flex items-center justify-center p-4">
            {/* Responsive Card */}
            <Card className="w-full max-w-md shadow-md"> {/* Consistent width with login */}
                <CardHeader>
                    <CardTitle>Create Account</CardTitle>
                    <CardDescription>Enter your details to register.</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        {/* Name */}
                        <div className="grid gap-2">
                            <Label htmlFor="name">Full Name</Label>
                            <Input
                                id="name"
                                type="text"
                                placeholder="e.g., Ada Lovelace"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
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

                        {/* Password */}
                        <div className="grid gap-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                placeholder="********"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>

                        {/* Confirm Password */}
                        <div className="grid gap-2">
                            <Label htmlFor="confirmPassword">Confirm Password</Label>
                            <Input
                                id="confirmPassword"
                                type="password"
                                placeholder="********"
                                value={confirmPassword}
                                onChange={(e) => setConfirmPassword(e.target.value)}
                                required
                            />
                        </div>

                        {/* Error Message */}
                        {error && <p className="text-sm text-destructive">{error}</p>}

                        {/* Submit Button */}
                        <Button type="submit" className="w-full" disabled={isLoading}>
                            {isLoading ? "Creating Account..." : "Create Account"}
                        </Button>

                        {/* Link back to Login */}
                        <Button
                            type="button"
                            variant="link"
                            className="w-full text-sm"
                            onClick={() => navigate('/login')} // Navigate back to login
                        >
                            Already have an account? Sign In
                        </Button>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}



//
// ### 2. Update `LoginPage.tsx` (If Needed)
//
// Double-check your `LoginPage.tsx` file. Make sure the button intended for registration now correctly navigates to `/register` (or whatever path you choose for user registration in `App.tsx`). It should look like this:
//
// ```tsx
// // Inside LoginPage.tsx
//
// import { useNavigate } from "react-router-dom";
// // ... other imports
//
// export function LoginPage() {
//     const navigate = useNavigate();
//     // ... other state
//
//     return (
//         // ... wrapping divs and Card ...
//         <form onSubmit={handleSubmit} className="grid gap-4">
//             {/* ... email and password inputs ... */}
//             <Button type="submit" /* ... */>Sign in</Button>
//
//             {/* This button should navigate to user registration */}
//             <Button
//                 type="button"
//                 variant="outline"
//                 className="w-full"
//                 onClick={() => navigate('/register')} // MAKE SURE THIS PATH MATCHES App.tsx
//             >
//                 Register New Account
//             </Button>
//         </form>
//         // ... rest of component
//     );
// }
