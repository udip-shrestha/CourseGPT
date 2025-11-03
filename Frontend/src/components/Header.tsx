import {
    GraduationCap,
    User,
    Upload,
    LogIn,
    UserPlus,
    FileText,
    Settings,
    MessageCircle,
    Plug,
} from "lucide-react";
import { useLocation, useParams, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";

export function Header() {
    const location = useLocation();
    const navigate = useNavigate();
    // This now works because Header is inside the Layout route in App.tsx
    const { instructorId, courseId } = useParams();

    // Clean the path for reliable matching
    const path = location.pathname.endsWith("/")
        ? location.pathname.slice(0, -1)
        : location.pathname;

    // --- Logic from 'main' branch ---
    const onInstructorRoute = path.startsWith("/instructors/");
    const onCourseRoute = path.startsWith("/courses/");
    const onLoginPage = path === "/login";
    const onRegisterPage = path === "/register";
    // Check for root path (which can be "/" or "")
    const onHomePage = path === "" || path === "/";
    // --- End of logic from 'main' ---

    return (
        <header className="border-b bg-card">
            <div className="container mx-auto px-4 py-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                    {/* Logo */}
                    <div
                        className="flex items-center justify-center sm:justify-start gap-2 cursor-pointer"
                        onClick={() => navigate("/")}
                    >
                        <GraduationCap className="h-8 w-8 text-primary" />
                        <h1 className="text-2xl font-bold text-primary">CourseGPT</h1>
                    </div>

                    {/* Navigation */}
                    <nav className="flex flex-wrap justify-center sm:justify-end gap-2 sm:gap-4">

                        {/* Instructor-level nav (Show on profile/courses list) */}
                        {onInstructorRoute && (
                            <>
                                <Button
                                    variant={path.endsWith("/profile") ? "default" : "ghost"}
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() =>
                                        navigate(`/instructors/${instructorId}/profile`)
                                    }
                                >
                                    <User className="h-4 w-4" />
                                    Profile
                                </Button>
                                <Button
                                    variant={path.endsWith("/courses") ? "default" : "ghost"}
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() =>
                                        navigate(`/instructors/${instructorId}/courses`)
                                    }
                                >
                                    <Upload className="h-4 w-4" />
                                    Courses
                                </Button>
                            </>
                        )}

                        {/* Course-level nav (Show when inside a specific course) */}
                        {onCourseRoute && (
                            <>
                                <Button
                                    variant={
                                        // Check if path is exactly /courses/:courseId
                                        path === `/courses/${courseId}` ? "default" : "ghost"
                                    }
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() => navigate(`/courses/${courseId}`)}
                                >
                                    <FileText className="h-4 w-4" />
                                    Docs
                                </Button>

                                <Button
                                    variant={
                                        path.includes(`/courses/${courseId}/chat`)
                                            ? "default"
                                            : "ghost"
                                    }
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() => navigate(`/courses/${courseId}/chat`)}
                                >
                                    <MessageCircle className="h-4 w-4" />
                                    Chat
                                </Button>

                                <Button
                                    variant={
                                        path.includes(`/courses/${courseId}/integrations`)
                                            ? "default"
                                            : "ghost"
                                    }
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() =>
                                        navigate(`/courses/${courseId}/integrations`)
                                    }
                                >
                                    <Plug className="h-4 w-4" />
                                    Integrations
                                </Button>

                                <Button
                                    variant={
                                        path.includes(`/courses/${courseId}/settings`)
                                            ? "default"
                                            : "ghost"
                                    }
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() => navigate(`/courses/${courseId}/settings`)}
                                >
                                    <Settings className="h-4 w-4" />
                                    Settings
                                </Button>
                            </>
                        )}

                        {/* Auth navigation: Login Page */}
                        {onLoginPage && (
                            <Button
                                variant="ghost"
                                className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                onClick={() => navigate("/register")}
                            >
                                <UserPlus className="h-4 w-4" />
                                Register
                            </Button>
                        )}

                        {/* Auth navigation: Register Page */}
                        {onRegisterPage && (
                            <Button
                                variant="ghost"
                                className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                onClick={() => navigate("/login")}
                            >
                                <LogIn className="h-4 w-4" />
                                Login
                            </Button>
                        )}

                        {/* Auth navigation: Home Page */}
                        {onHomePage && (
                            <>
                                <Button
                                    variant="ghost"
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() => navigate("/login")}
                                >
                                    <LogIn className="h-4 w-4" />
                                    Login
                                </Button>
                                <Button
                                    variant="ghost"
                                    className="flex items-center gap-2 w-full sm:w-auto justify-center"
                                    onClick={() => navigate("/register")}
                                >
                                    <UserPlus className="h-4 w-4" />
                                    Register
                                </Button>
                            </>
                        )}
                    </nav>
                </div>
            </div>
        </header>
    );
}

