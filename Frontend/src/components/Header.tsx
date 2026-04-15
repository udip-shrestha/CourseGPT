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
  UserCircle,
  Menu,
  Shield,
} from "lucide-react";
import { useLocation, useParams, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";
import { LayoutDashboard } from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "./ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "./ui/sheet";

export function Header() {
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const roleParam = searchParams.get("role");
  const isStudentRole = roleParam === "student";
  const navigate = useNavigate();
  const { apiClient } = useApiClient();

  // This now works because Header is inside the Layout route in App.tsx
  const { instructorId, courseId } = useParams();

  // Clean the path for reliable matching
  const path = location.pathname.endsWith("/")
    ? location.pathname.slice(0, -1)
    : location.pathname;

  const isAuthenticated = !!apiClient.getToken?.();
  const currentInstructorId = apiClient.getInstructorId?.();
  const handleLogout = () => {
    apiClient.logout?.();
  };

  // --- Logic from 'main' branch ---
  const onInstructorRoute = path.startsWith("/instructors/");
  const onCourseRoute = path.startsWith("/courses/");
  const onLoginPage = path === "/login";
  const onRegisterPage = path === "/register";
  // Check for root path (which can be "/" or "")
  const onHomePage = path === "" || path === "/";
  // --- End of logic from 'main' ---

  function NavItems({ isMobile }: { isMobile: boolean }) {
    return (
      <>
        {/* Uppermost Profile Icon Menu */}
        {isMobile && isAuthenticated && !isStudentRole && (
          <div className="w-full flex justify-center mb-4">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button className="p-1 rounded-full hover:bg-accent transition">
                  <UserCircle className="h-6 w-6 text-foreground/60" />
                </button>
              </DropdownMenuTrigger>

              <DropdownMenuContent
                align="center"
                sideOffset={8}
                className="w-48 rounded-lg border bg-popover shadow-lg"
              >
                <DropdownMenuItem
                  className="cursor-pointer px-3 py-2 text-sm hover:bg-accent rounded-md"
                  onClick={() =>
                    navigate(`/instructors/${currentInstructorId}/profile`)
                  }
                >
                  Profile
                </DropdownMenuItem>

                <DropdownMenuItem
                  className="cursor-pointer px-3 py-2 text-sm hover:bg-accent rounded-md"
                  onClick={() =>
                    navigate(`/instructors/${currentInstructorId}/courses`)
                  }
                >
                  Courses
                </DropdownMenuItem>

                <DropdownMenuSeparator />

                <DropdownMenuItem
                  className="cursor-pointer px-3 py-2 text-sm text-red-600 hover:bg-red-100 rounded-md"
                  onClick={handleLogout}
                >
                  Logout
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        )}

        {/* Instructor-level nav */}
        {onInstructorRoute && (
          <>
            <Button
              variant={path.endsWith("/profile") ? "default" : "ghost"}
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate(`/instructors/${instructorId}/profile`)}
            >
              <User className="h-4 w-4" />
              Profile
            </Button>

            <Button
              variant={path.endsWith("/courses") ? "default" : "ghost"}
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate(`/instructors/${instructorId}/courses`)}
            >
              <Upload className="h-4 w-4" />
              Courses
            </Button>
          </>
        )}

        {/* Course-level nav */}
        {onCourseRoute && !isStudentRole && (
          <>
            <Button
              variant={path === `/courses/${courseId}` ? "default" : "ghost"}
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate(`/courses/${courseId}`)}
            >
              <FileText className="h-4 w-4" />
              Docs
            </Button>

            <Button
              variant={
                path.includes(`/courses/${courseId}/chats`)
                  ? "default"
                  : "ghost"
              }
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate(`/courses/${courseId}/chats`)}
            >
              <MessageCircle className="h-4 w-4" />
              Chat
            </Button>

            <>
              <Button
                variant={
                  path.includes(`/courses/${courseId}/integrations`)
                    ? "default"
                    : "ghost"
                }
                className="flex items-center gap-2 w-full sm:w-auto justify-center"
                onClick={() => navigate(`/courses/${courseId}/integrations`)}
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

              <Button
                variant={
                  path.includes(`/courses/${courseId}/analytics`)
                    ? "default"
                    : "ghost"
                }
                className="flex items-center gap-2 w-full sm:w-auto justify-center"
                onClick={() => navigate(`/courses/${courseId}/analytics`)}
              >
                <LayoutDashboard className="h-4 w-4" />
                Analytics
              </Button>

              <Button
                variant={
                  path.includes(`/courses/${courseId}/admin`)
                    ? "default"
                    : "ghost"
                }
                className="flex items-center gap-2 w-full sm:w-auto justify-center"
                onClick={() => navigate(`/courses/${courseId}/admin`)}
              >
                <Shield className="h-4 w-4" />
                Admin
              </Button>
            </>
          </>
        )}

        {/* Auth navigation: Login Page */}
        {onLoginPage && (
          <>
            <Button
              variant={path === `/courses/${courseId}` ? "default" : "ghost"}
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate("/register")}
            >
              <FileText className="h-4 w-4" />
              Register
            </Button>
          </>
        )}

        {/* Auth navigation: Register Page */}
        {onRegisterPage && (
          <>
            <Button
              variant={path === `/courses/${courseId}` ? "default" : "ghost"}
              className="flex items-center gap-2 w-full sm:w-auto justify-center"
              onClick={() => navigate("/login")}
            >
              <FileText className="h-4 w-4" />
              Login
            </Button>
          </>
        )}

        {/* Home page auth nav */}
        {onHomePage && !isAuthenticated && (
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

        {/* Rightmost Profile Icon Menu on Desktop */}
        {!isMobile && isAuthenticated && !isStudentRole && (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <button className="p-1 rounded-full hover:bg-accent transition">
                <UserCircle className="h-6 w-6 text-foreground/60" />
              </button>
            </DropdownMenuTrigger>

            <DropdownMenuContent
              align="end"
              sideOffset={8}
              className="w-48 rounded-lg border bg-popover shadow-lg"
            >
              <DropdownMenuItem
                className="cursor-pointer px-3 py-2 text-sm hover:bg-accent rounded-md"
                onClick={() =>
                  navigate(`/instructors/${currentInstructorId}/profile`)
                }
              >
                Profile
              </DropdownMenuItem>

              <DropdownMenuItem
                className="cursor-pointer px-3 py-2 text-sm hover:bg-accent rounded-md"
                onClick={() =>
                  navigate(`/instructors/${currentInstructorId}/courses`)
                }
              >
                Courses
              </DropdownMenuItem>

              <DropdownMenuSeparator />

              <DropdownMenuItem
                className="cursor-pointer px-3 py-2 text-sm text-red-600 hover:bg-red-100 rounded-md"
                onClick={handleLogout}
              >
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )}
      </>
    );
  }

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        <div className="flex flex-row items-center justify-between gap-3">
          {/* Logo */}
          <div
            className="flex items-center justify-center sm:justify-start gap-2 cursor-pointer"
            onClick={() => {
              if (!isStudentRole) navigate("/");
            }}
          >
            <GraduationCap className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-primary">CourseGPT</h1>
          </div>

          {/* Navigation */}
          <nav className="flex w-full items-center justify-end">
            {/* MOBILE: Hamburger (visible only on small screens) */}
            <div className="sm:hidden">
              <Sheet>
                <SheetTrigger asChild>
                  <button className="p-2 rounded-md hover:bg-accent">
                    <Menu className="h-6 w-6" />
                  </button>
                </SheetTrigger>

                <SheetContent side="right" className="w-64 p-4">
                  <div className="flex flex-col gap-3">
                    <NavItems isMobile={true} />
                  </div>
                </SheetContent>
              </Sheet>
            </div>

            {/* DESKTOP NAVIGATION (hidden on mobile) */}
            <div className="hidden sm:flex flex-wrap justify-end gap-4">
              <NavItems isMobile={false} />
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}
