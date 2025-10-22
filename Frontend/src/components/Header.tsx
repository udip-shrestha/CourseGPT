import { GraduationCap, User, Upload, LogIn, UserPlus } from "lucide-react";
import { useLocation, useParams, useNavigate } from "react-router-dom";
import { Button } from "./ui/button";

export function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { instructorId } = useParams();

  const path = location.pathname;

  const onInstructorRoute = path.startsWith("/instructors/");
  const onLoginPage = path === "/login";
  const onRegisterPage = path === "/register";
  const onHomePage = path === "/";

  return (
    <header className="border-b bg-card">
      <div className="container mx-auto px-4 py-4">
        {/* Stack content on mobile, side-by-side on larger screens */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
          {/* Logo */}
          <div className="flex items-center justify-center sm:justify-start gap-2">
            <GraduationCap className="h-8 w-8 text-primary" />
            <h1 className="text-2xl font-bold text-primary">CourseGPT</h1>
          </div>

          {/* Conditional Navigation */}
          <nav className="flex flex-wrap justify-center sm:justify-end gap-2 sm:gap-4">
            {/* Instructor route: Profile + Courses */}
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

            {/* Login page: show Register */}
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

            {/* Register page: show Login */}
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

            {/* Home page: show both Login + Register */}
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
