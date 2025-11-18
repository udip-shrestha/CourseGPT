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

interface Instructor {
    id: string;
    name: string;
    title: string;
    university: string;
    email: string;
    created_at?: string;
}

export function SettingsPage() {
    const navigate = useNavigate();
    const apiClient = useApiClient();

    const [isLoggingOut, setIsLoggingOut] = useState(false);
    const [logoutError, setLogoutError] = useState<string | null>(null);

    // Instructor data state
    const [isLoading, setIsLoading] = useState(true);
    const [loadError, setLoadError] = useState<string | null>(null);

    // Form state
    const [formData, setFormData] = useState({
        name: "",
        title: "",
        university: "",
        email: "",
    });
    const [isSaving, setIsSaving] = useState(false);
    const [saveError, setSaveError] = useState<string | null>(null);
    const [saveSuccess, setSaveSuccess] = useState(false);

    // Password change state
    const [passwordData, setPasswordData] = useState({
        currentPassword: "",
        newPassword: "",
        confirmPassword: "",
    });
    const [isChangingPassword, setIsChangingPassword] = useState(false);
    const [passwordError, setPasswordError] = useState<string | null>(null);
    const [passwordSuccess, setPasswordSuccess] = useState(false);

    const instructorId = useMemo(
        () => apiClient.getInstructorId?.() ?? null,
        [apiClient],
    );
    const isAuthenticated = apiClient.isAuthenticated?.() ?? false;

    // Fetch instructor data on mount
    useEffect(() => {
        if (!isAuthenticated || !instructorId) {
            navigate("/login", { replace: true });
            return;
        }

        const fetchInstructor = async () => {
            setIsLoading(true);
            setLoadError(null);
            try {
                const { data, errorMessage } = await apiClient.getInstructor(
                    instructorId,
                );
                const instructorData = data as Instructor | undefined;

                if (errorMessage) {
                    setLoadError(errorMessage);
                    return;
                }

                if (instructorData) {
                    setFormData({
                        name: instructorData.name || "",
                        title: instructorData.title || "",
                        university: instructorData.university || "",
                        email: instructorData.email || "",
                    });
                }
            } catch (error) {
                console.error("Failed to fetch instructor:", error);
                setLoadError("Failed to load instructor data.");
            } finally {
                setIsLoading(false);
            }
        };

        fetchInstructor();
    }, [isAuthenticated, instructorId, navigate, apiClient]);

    const handleInputChange = (field: keyof typeof formData, value: string) => {
        setFormData((prev) => ({ ...prev, [field]: value }));
        setSaveError(null);
        setSaveSuccess(false);
    };

    const handleSaveProfile = async () => {
        if (!instructorId) return;

        setIsSaving(true);
        setSaveError(null);
        setSaveSuccess(false);

        try {
            const { errorMessage } = await apiClient.updateInstructor(
                instructorId,
                {
                    name: formData.name,
                    title: formData.title,
                    university: formData.university,
                    email: formData.email,
                },
            );

            if (errorMessage) {
                setSaveError(errorMessage);
                return;
            }

            setSaveSuccess(true);
            // Refresh instructor data to get updated values
            const { data } = await apiClient.getInstructor(instructorId);
            const updatedData = data as Instructor | undefined;
            if (updatedData) {
                setFormData({
                    name: updatedData.name || "",
                    title: updatedData.title || "",
                    university: updatedData.university || "",
                    email: updatedData.email || "",
                });
            }
            // Clear success message after 3 seconds
            setTimeout(() => setSaveSuccess(false), 3000);
        } catch (error) {
            console.error("Failed to update profile:", error);
            setSaveError("Failed to update profile. Please try again.");
        } finally {
            setIsSaving(false);
        }
    };

    const handlePasswordChange = async () => {
        if (!instructorId) return;

        // Validation
        if (!passwordData.newPassword || !passwordData.confirmPassword) {
            setPasswordError("Please fill in all password fields.");
            return;
        }

        if (passwordData.newPassword !== passwordData.confirmPassword) {
            setPasswordError("New passwords do not match.");
            return;
        }

        if (passwordData.newPassword.length < 6) {
            setPasswordError("Password must be at least 6 characters long.");
            return;
        }

        setIsChangingPassword(true);
        setPasswordError(null);
        setPasswordSuccess(false);

        try {
            const { errorMessage } = await apiClient.updateInstructor(
                instructorId,
                {
                    password: passwordData.newPassword,
                },
            );

            if (errorMessage) {
                setPasswordError(errorMessage);
                return;
            }

            setPasswordSuccess(true);
            setPasswordData({
                currentPassword: "",
                newPassword: "",
                confirmPassword: "",
            });
            // Clear success message after 3 seconds
            setTimeout(() => setPasswordSuccess(false), 3000);
        } catch (error) {
            console.error("Failed to change password:", error);
            setPasswordError("Failed to change password. Please try again.");
        } finally {
            setIsChangingPassword(false);
        }
    };

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

    if (isLoading) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <Card>
                    <CardContent className="py-10">
                        <p className="text-center text-muted-foreground">
                            Loading account information...
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    if (loadError) {
        return (
            <div className="max-w-3xl mx-auto space-y-6">
                <Card>
                    <CardContent className="py-10">
                        <p className="text-center text-destructive">
                            {loadError}
                        </p>
                    </CardContent>
                </Card>
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Account Details Card */}
            <Card>
                <CardHeader>
                    <CardTitle>Account Details</CardTitle>
                    <CardDescription>
                        Update your account information. Changes will be saved to your
                        profile.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="instructor-id">Instructor ID</Label>
                        <Input
                            id="instructor-id"
                            value={instructorId || "Unknown"}
                            readOnly
                            className="bg-muted"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="name">Full Name</Label>
                        <Input
                            id="name"
                            value={formData.name}
                            onChange={(e) =>
                                handleInputChange("name", e.target.value)
                            }
                            placeholder="Enter your full name"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="title">Job Title</Label>
                        <Input
                            id="title"
                            value={formData.title}
                            onChange={(e) =>
                                handleInputChange("title", e.target.value)
                            }
                            placeholder="Enter your job title"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="university">University</Label>
                        <Input
                            id="university"
                            value={formData.university}
                            onChange={(e) =>
                                handleInputChange("university", e.target.value)
                            }
                            placeholder="Enter your university"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="email">Email</Label>
                        <Input
                            id="email"
                            type="email"
                            value={formData.email}
                            onChange={(e) =>
                                handleInputChange("email", e.target.value)
                            }
                            placeholder="Enter your email address"
                        />
                    </div>

                    {saveError && (
                        <p className="text-sm text-destructive">{saveError}</p>
                    )}
                    {saveSuccess && (
                        <p className="text-sm text-green-600">
                            Profile updated successfully!
                        </p>
                    )}

                    <Button
                        onClick={handleSaveProfile}
                        disabled={isSaving}
                        className="w-full sm:w-auto"
                    >
                        {isSaving ? "Saving..." : "Save Changes"}
                    </Button>
                </CardContent>
            </Card>

            {/* Password Change Card */}
            <Card>
                <CardHeader>
                    <CardTitle>Change Password</CardTitle>
                    <CardDescription>
                        Update your password to keep your account secure.
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="new-password">New Password</Label>
                        <Input
                            id="new-password"
                            type="password"
                            value={passwordData.newPassword}
                            onChange={(e) =>
                                setPasswordData((prev) => ({
                                    ...prev,
                                    newPassword: e.target.value,
                                }))
                            }
                            placeholder="Enter new password"
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="confirm-password">Confirm New Password</Label>
                        <Input
                            id="confirm-password"
                            type="password"
                            value={passwordData.confirmPassword}
                            onChange={(e) =>
                                setPasswordData((prev) => ({
                                    ...prev,
                                    confirmPassword: e.target.value,
                                }))
                            }
                            placeholder="Confirm new password"
                        />
                    </div>

                    {passwordError && (
                        <p className="text-sm text-destructive">{passwordError}</p>
                    )}
                    {passwordSuccess && (
                        <p className="text-sm text-green-600">
                            Password changed successfully!
                        </p>
                    )}

                    <Button
                        onClick={handlePasswordChange}
                        disabled={isChangingPassword}
                        className="w-full sm:w-auto"
                    >
                        {isChangingPassword ? "Changing..." : "Change Password"}
                    </Button>
                </CardContent>
            </Card>

            {/* Security Card */}
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