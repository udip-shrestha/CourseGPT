import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Mail, Settings, Trash2, AlertTriangle } from "lucide-react";
import { Button } from './ui/button';
import {
    Popover,
    PopoverContent,
    PopoverTrigger,
} from "./ui/popover";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "./ui/dialog";
import { useApiClient } from "../ApiClientContext";

// Define an interface for the expected API response data
interface Instructor {
    id: string;
    name: string;
    title: string;
    university: string;
    email: string;
    created_at: string;
}

export function InstructorProfile() {
    const { instructorId } = useParams<{ instructorId: string }>();
    const navigate = useNavigate();
    const apiClient = useApiClient();

    const [instructor, setInstructor] = useState<Instructor | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null); // For page load error

    // State for Popover and Dialogs
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isFinalDeleteDialogOpen, setIsFinalDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    // --- FIX: Added state for delete-specific errors ---
    const [deleteError, setDeleteError] = useState<string | null>(null);

    // --- 'useEffect' to fetch instructor (uses apiClient) ---
    useEffect(() => {
        if (!instructorId) {
            setError("Instructor ID not found in URL.");
            setIsLoading(false);
            return;
        }

        const fetchInstructor = async () => {
            setIsLoading(true);
            setError(null);
            try {
                const { data, errorStatus, errorMessage } = await apiClient.request<Instructor>(
                    "GET",
                    `/instructors/${instructorId}`
                );

                if (errorMessage) {
                    if (errorStatus === 404) {
                        throw new Error(`Instructor with ID ${instructorId} not found.`);
                    }
                    throw new Error(errorMessage);
                }

                setInstructor(data || null);
            } catch (err: any) {
                console.error("Failed to fetch instructor:", err);
                if (err instanceof TypeError && err.message === "Failed to fetch") {
                    setError("Could not connect to the server. Please ensure it's running.");
                } else {
                    setError(err.message || "An unexpected error occurred.");
                }
            } finally {
                setIsLoading(false);
            }
        };
        fetchInstructor();
    }, [instructorId, apiClient]);


    // --- 'handleDelete' (uses apiClient and setDeleteError) ---
    const handleDelete = async () => {
        if (!instructorId) return;

        setIsDeleting(true);
        // --- FIX: Use the 'deleteError' state setter ---
        setDeleteError(null);

        try {
            const { errorMessage } = await apiClient.request(
                "DELETE",
                `/instructors/${instructorId}`
            );

            if (errorMessage) {
                throw new Error(errorMessage);
            }

            console.log(`Instructor ${instructorId} deleted successfully.`);
            setIsFinalDeleteDialogOpen(false);
            setIsDeleteDialogOpen(false);
            setIsSettingsOpen(false);
            navigate('/login');

        } catch (err: any) {
            console.error("Failed to delete instructor:", err);
            let userError: string;
            if (err instanceof TypeError && err.message === "Failed to fetch") {
                userError = "Could not connect to the server. Please ensure it's running.";
            } else {
                userError = err.message || "An unexpected error occurred during deletion.";
            }
            // --- FIX: Use the 'deleteError' state setter ---
            setDeleteError(userError);
        } finally {
            setIsDeleting(false);
        }
    };

    // --- Render Loading State ---
    if (isLoading) {
        return <div className="text-center p-10">Loading instructor profile...</div>;
    }

    // --- Render Error State ---
    if (error && !instructor) {
        return <div className="text-center text-destructive p-10">Error: {error}</div>;
    }

    // --- Render Not Found State ---
    if (!instructor) {
        return <div className="text-center p-10">Instructor not found.</div>;
    }

    // --- Render Profile Data ---
    const getInitials = (name: string): string => {
        return name
            .split(' ')
            .map(n => n[0])
            .slice(0, 2)
            .join('')
            .toUpperCase();
    }

    return (
        <div className="space-y-8">
            <Card className="relative">
                <CardContent className="p-8">

                    {/* --- Settings Popover Button --- */}
                    <div className="absolute top-4 right-4 z-10">
                        <Popover open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                            <PopoverTrigger asChild>
                                <Button variant="ghost" size="icon" aria-label="Profile Settings">
                                    <Settings className="h-5 w-5" />
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-48 p-2">
                                <div className="grid gap-1">
                                    <Button
                                        variant="ghost"
                                        className="w-full justify-start text-sm h-8"
                                        disabled // Keep disabled for now
                                        onClick={() => {
                                            console.log("Update profile clicked");
                                            setIsSettingsOpen(false);
                                        }}
                                    >
                                        Update Profile
                                    </Button>

                                    {/* --- Delete Option (Triggers First Dialog) --- */}
                                    <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                                        <DialogTrigger asChild>
                                            <Button
                                                variant="ghost"
                                                className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10 text-sm h-8"
                                                // --- FIX: Clear old errors when opening ---
                                                onClick={() => setDeleteError(null)}
                                            >
                                                <Trash2 className="mr-2 h-4 w-4" />
                                                Delete Profile
                                            </Button>
                                        </DialogTrigger>
                                        {/* --- First Confirmation Dialog --- */}
                                        <DialogContent>
                                            <DialogHeader>
                                                <DialogTitle>Are you sure?</DialogTitle>
                                                <DialogDescription>
                                                    This action cannot be undone immediately. Do you want to proceed with deleting your profile?
                                                </DialogDescription>
                                            </DialogHeader>
                                            <DialogFooter className="gap-2 sm:justify-end">
                                                <DialogClose asChild>
                                                    <Button variant="outline">Cancel</Button>
                                                </DialogClose>
                                                {/* --- Second Confirmation Dialog (Nested Trigger) --- */}
                                                <Dialog open={isFinalDeleteDialogOpen} onOpenChange={setIsFinalDeleteDialogOpen}>
                                                    <DialogTrigger asChild>
                                                        <Button variant="destructive">Confirm Delete</Button>
                                                    </DialogTrigger>
                                                    <DialogContent>
                                                        <DialogHeader>
                                                            <DialogTitle className="flex items-center gap-2">
                                                                <AlertTriangle className="text-destructive h-5 w-5"/> Final Confirmation
                                                            </DialogTitle>
                                                            <DialogDescription>
                                                                Deleting your profile is permanent and will remove all associated data. This action cannot be recovered.
                                                                {/* --- FIX: Display the 'deleteError' state --- */}
                                                                {deleteError && <p className="text-sm text-destructive mt-4">Error: {deleteError}</p>}
                                                            </DialogDescription>
                                                        </DialogHeader>
                                                        <DialogFooter className="gap-2">
                                                            <Button
                                                                variant="outline"
                                                                onClick={() => setIsFinalDeleteDialogOpen(false)}
                                                                disabled={isDeleting}
                                                            >
                                                                Cancel
                                                            </Button>
                                                            <Button
                                                                variant="destructive"
                                                                onClick={handleDelete} // This calls the API
                                                                disabled={isDeleting}
                                                            >
                                                                {isDeleting ? "Deleting..." : "Yes, Delete Permanently"}
                                                            </Button>
                                                        </DialogFooter>
                                                    </DialogContent>
                                                </Dialog>
                                            </DialogFooter>
                                        </DialogContent>
                                    </Dialog>
                                </div>
                            </PopoverContent>
                        </Popover>
                    </div>
                    {/* --- End Settings Popover Button --- */}

                    {/* ... Rest of the Profile Card Content ... */}
                    <div className="flex flex-col md:flex-row gap-6 items-start">
                        <Avatar className="h-32 w-32">
                            <AvatarFallback className="text-4xl">
                                {getInitials(instructor.name)}
                            </AvatarFallback>
                        </Avatar>
                        <div className="flex-1 space-y-4">
                            <div>
                                <h1 className="text-3xl font-bold">{instructor.name}</h1>
                                <p className="text-xl text-muted-foreground">{instructor.title}</p>
                                <p className="text-lg text-muted-foreground">{instructor.university}</p>
                            </div>
                            <div className="flex flex-wrap gap-x-4 gap-y-2 text-sm text-muted-foreground">
                                <div className="flex items-center gap-1">
                                    <Mail className="h-4 w-4" />
                                    {instructor.email}
                                </div>
                            </div>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

