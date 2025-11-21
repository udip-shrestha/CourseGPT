import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent } from './ui/card';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Mail, Settings, Trash2 } from "lucide-react";
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
import { useApiClient } from "../clients/ApiClientContext";

// Interface for the instructor
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
    const { apiClient } = useApiClient();

    const [instructor, setInstructor] = useState<Instructor | null>(null);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    // Popover / Dialog state
    const [isSettingsOpen, setIsSettingsOpen] = useState(false);
    const [isDeleteDialogOpen, setIsDeleteDialogOpen] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);
    const [isUpdating, setIsUpdating] = useState(false);

    // Update form state
    const [updateName, setUpdateName] = useState('');
    const [updateTitle, setUpdateTitle] = useState('');
    const [updateUniversity, setUpdateUniversity] = useState('');
    const [updateEmail, setUpdateEmail] = useState('');
    const [updatePassword, setUpdatePassword] = useState('');

    // --- Fetch instructor on mount ---
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
                const { data, errorMessage } = await apiClient.request<Instructor>(
                    "GET",
                    `/instructors/${instructorId}`
                );

                if (errorMessage) throw new Error(errorMessage);
                if (data) {
                    setInstructor(data);
                    setUpdateName(data.name);
                    setUpdateTitle(data.title);
                    setUpdateUniversity(data.university);
                    setUpdateEmail(data.email);
                }
            } catch (err: any) {
                setError(err.message || "Failed to fetch instructor.");
            } finally {
                setIsLoading(false);
            }
        };
        fetchInstructor();
    }, [instructorId, apiClient]);

    // --- Delete Instructor ---
    const handleDelete = async () => {
        if (!instructorId) return;
        setIsDeleting(true);
        try {
            const { errorMessage } = await apiClient.request(
                "DELETE",
                `/instructors/${instructorId}`
            );
            if (errorMessage) throw new Error(errorMessage);
            navigate('/login');
        } catch (err: any) {
            console.error("Delete failed:", err);
        } finally {
            setIsDeleting(false);
        }
    };

    // --- Update Instructor (PUT request) ---
    const handleUpdate = async () => {
        if (!instructorId) return;
        setIsUpdating(true);
        try {
            const { data, errorMessage } = await apiClient.request<Instructor>(
                "PUT",
                `/instructors/${instructorId}`,
                {
                    query: {
                        name: updateName,
                        title: updateTitle,
                        university: updateUniversity,
                        email: updateEmail,
                        password: updatePassword || undefined
                    }
                }
            );

            if (errorMessage) throw new Error(errorMessage);

            if (data) {
                setInstructor(data); // update UI
                setUpdateName(data.name);
                setUpdateTitle(data.title);
                setUpdateUniversity(data.university);
                setUpdateEmail(data.email);
                setUpdatePassword("");
            }
            setIsSettingsOpen(false);
        } catch (err: any) {
            console.error("Update failed:", err);
        } finally {
            setIsUpdating(false);
        }
    };

    // --- Loading / Error states ---
    if (isLoading) return <div className="text-center p-10">Loading instructor profile...</div>;
    if (error && !instructor) return <div className="text-center text-destructive p-10">Error: {error}</div>;
    if (!instructor) return <div className="text-center p-10">Instructor not found.</div>;

    const getInitials = (name: string) =>
        name.split(' ').map(n => n[0]).slice(0, 2).join('').toUpperCase();

    return (
        <div className="space-y-8">
            <Card className="relative">
                <CardContent className="p-8">
                    {/* Settings Popover */}
                    <div className="absolute top-4 right-4 z-10">
                        <Popover open={isSettingsOpen} onOpenChange={setIsSettingsOpen}>
                            <PopoverTrigger asChild>
                                <Button variant="ghost" size="icon" aria-label="Profile Settings">
                                    <Settings className="h-5 w-5" />
                                </Button>
                            </PopoverTrigger>
                            <PopoverContent className="w-56 p-2">
                                <div className="grid gap-1">
                                    {/* Update Profile */}
                                    <div className="flex flex-col gap-2">
                                        <input
                                            className="border rounded p-1"
                                            placeholder="Full Name"
                                            value={updateName}
                                            onChange={e => setUpdateName(e.target.value)}
                                        />
                                        <input
                                            className="border rounded p-1"
                                            placeholder="Title"
                                            value={updateTitle}
                                            onChange={e => setUpdateTitle(e.target.value)}
                                        />
                                        <input
                                            className="border rounded p-1"
                                            placeholder="University"
                                            value={updateUniversity}
                                            onChange={e => setUpdateUniversity(e.target.value)}
                                        />
                                        <input
                                            className="border rounded p-1"
                                            placeholder="Email"
                                            value={updateEmail}
                                            onChange={e => setUpdateEmail(e.target.value)}
                                        />
                                        <input
                                            type="password"
                                            className="border rounded p-1"
                                            placeholder="Password (optional)"
                                            value={updatePassword}
                                            onChange={e => setUpdatePassword(e.target.value)}
                                        />
                                        <Button
                                            variant="default"
                                            onClick={handleUpdate}
                                            disabled={isUpdating}
                                        >
                                            {isUpdating ? "Updating..." : "Save Changes"}
                                        </Button>
                                    </div>

                                    {/* Delete Profile */}
                                    <Dialog open={isDeleteDialogOpen} onOpenChange={setIsDeleteDialogOpen}>
                                        <DialogTrigger asChild>
                                            <Button
                                                variant="destructive"
                                                className="w-full justify-start text-sm h-8"
                                            >
                                                <Trash2 className="mr-2 h-4 w-4" />
                                                Delete Profile
                                            </Button>
                                        </DialogTrigger>
                                        <DialogContent>
                                            <DialogHeader>
                                                <DialogTitle>Are you sure?</DialogTitle>
                                                <DialogDescription>
                                                    This action cannot be undone.
                                                </DialogDescription>
                                            </DialogHeader>
                                            <DialogFooter className="gap-2 sm:justify-end">
                                                <DialogClose asChild>
                                                    <Button variant="outline">Cancel</Button>
                                                </DialogClose>
                                                <Button
                                                    variant="destructive"
                                                    onClick={handleDelete}
                                                    disabled={isDeleting}
                                                >
                                                    {isDeleting ? "Deleting..." : "Yes, Delete"}
                                                </Button>
                                            </DialogFooter>
                                        </DialogContent>
                                    </Dialog>
                                </div>
                            </PopoverContent>
                        </Popover>
                    </div>

                    {/* Profile Content */}
                    <div className="flex flex-col md:flex-row gap-6 items-start">
                        <Avatar className="h-32 w-32">
                            <AvatarFallback className="text-4xl">{getInitials(instructor.name)}</AvatarFallback>
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
