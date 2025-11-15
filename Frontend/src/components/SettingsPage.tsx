import { useEffect, useMemo, useState } from "react";
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
import { useApiClient } from "../ApiClientContext";

export function SettingsPage() {
    const navigate = useNavigate();
    const apiClient = useApiClient();

    const [isLoggingOut, setIsLoggingOut] = useState(false);
    const [logoutError, setLogoutError] = useState<string | null>(null);

    const instructorId = useMemo(
        () => apiClient.getInstructorId?.() ?? "Unknown",
        [apiClient],
    );
    const isAuthenticated = apiClient.isAuthenticated?.() ?? false;

    useEffect(() => {
        if (!isAuthenticated) {
            navigate("/login", { replace: true });
        }
    }, [isAuthenticated, navigate]);

    const handleLogout = () => {
        setLogoutError(null);
        setIsLoggingOut(true);

        try {
            apiClient.logout?.();
            navigate("/login", { replace: true });
        } catch (error) {
            console.error("Failed to log out", error);
            setLogoutError("Something went wrong while logging out. Please try again.");
            setIsLoggingOut(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            <Card>
                <CardHeader>
                    <CardTitle>Account Details</CardTitle>
                    <CardDescription>
                        Review high-level details about the account you are currently signed
                        in with.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label>Instructor ID</Label>
                        <Input value={instructorId} readOnly />
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Security</CardTitle>
                    <CardDescription>
                        Sign out of CourseGPT on this browser. This will clear your saved
                        access token and stop any pending requests.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    {logoutError && (
                        <p className="text-sm text-destructive">{logoutError}</p>
                    )}
                    <Button
                        variant="destructive"
                        disabled={!isAuthenticated || isLoggingOut}
                        onClick={handleLogout}
                        className="w-full sm:w-auto"
                    >
                        {isLoggingOut ? "Signing out..." : "Sign Out"}
                    </Button>
                </CardContent>
            </Card>
        </div>
    );
}