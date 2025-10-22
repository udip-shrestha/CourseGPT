import {useState} from "react";
import {Button} from "./components/ui/button";
import {Input} from "./components/ui/input";
import {Label} from "./components/ui/label";
import './login.css'
import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "./components/ui/card";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoading, setIsLoading] = useState(false);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setIsLoading(true);

        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000));

        console.log("Login attempt:", {email, password});
        setIsLoading(false);
    };

    const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
        console.log(event.currentTarget.name);
    }

    const handleRegister = () => {
        console.log("Navigate to registration page");
        // TODO: Add navigation to registration page
    };

    const handleForgotPassword = () => {
        console.log("Navigate to forgot password page");
        // TODO: Add navigation to forgot password page
    };

    return (
        <div className="min-h-screen w-full flex items-center justify-center bg-gray-50 p-4">
            <Card className="w-1/2 shadow-md">
                <header>
                    <h1 id="title">CourseGPT</h1>
                </header>
                <CardHeader>
                    <CardTitle>Login</CardTitle>
                    <CardDescription>Sign in to your account</CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit} className="grid gap-4">
                        <div className="grid gap-2 text-white">
                            <Label htmlFor="email">Email</Label>
                            <Input
                                id="email"
                                type="email"
                                placeholder="Enter email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                required
                            />
                        </div>
                        <div className="grid gap">
                            <div className="flex items-center justify-between">
                                <Label htmlFor="password">Password</Label>
                                <button
                                    type="button"
                                    onClick={handleForgotPassword}
                                    className="text-sm text-black-600 hover:text-black-800"
                                >
                                    Forgot password?
                                </button>
                            </div>
                            <Input
                                id="password"
                                type="password"
                                placeholder="Enter password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                required
                            />
                        </div>
                        <Button onSubmit={handleClick} type="submit"
                            name="signin"
                            className="w-full"
                            disabled={isLoading}
                        >
                            {isLoading ? "Signing in..." : "Sign in"}
                        </Button>
                        <div className="text-center text-sm">
                            <span className="text-gray-600">Don't have an account? </span>
                            <button
                                type="button"
                                onClick={handleRegister}
                                className="text-black-600 hover:text-blue-800 hover:underline font-medium"
                            >
                                Register
                            </button>
                        </div>
                    </form>
                </CardContent>
            </Card>
        </div>
    );
}