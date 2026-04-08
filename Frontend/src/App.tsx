import { Routes, Route, Outlet } from "react-router-dom";
import { Header } from "./components/Header.tsx";
import { HomePage } from "./components/HomePage.tsx";
import { LoginPage } from "./components/LoginPage.tsx";
import { RegisterPage } from "./components/RegisterPage.tsx";
import { InstructorProfile } from "./components/InstructorProfile.tsx";
import { InstructorCourses } from "./components/InstructorCourses.tsx";
import { NotFoundPage } from "./components/NotFoundPage.tsx";
import { CoursePage } from "./components/CoursePage.tsx";
import { CanvasLinkPage } from "./components/CanvasLinkPage.tsx";
import { RequestResetPage } from "./components/RequestResetPage.tsx";
//import { ResetPasswordPage } from "./components/ResetPasswordPage.tsx";

/**
 * The main Layout component.
 * This includes the Header (which is on every page)
 * and an <Outlet />.
 */
function Layout() {
    return (
        <div className="min-h-screen bg-background text-foreground transition-all duration-300">
            {/* Header is now part of the Layout, so it can read URL params */}
            <Header />

            {/* Main routed content will be rendered inside this <Outlet /> */}
            <main className="w-full max-w-[1920px] mx-auto px-6 sm:px-8 py-10">
                <Outlet />
            </main>
        </div>
    );
}

/**
 * The main App component.
 * It defines the routes for the application.
 */
export default function App() {
    return (
        <Routes>
            {/* All pages are rendered inside the <Layout /> component */}
            <Route element={<Layout />}>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/register-course" element={<CanvasLinkPage />} />

                {/* Password Reset Flow */}
                <Route path="/RequestResetPage" element={<RequestResetPage />} />


                {/* Instructor Routes */}
                <Route
                    path="/instructors/:instructorId/profile"
                    element={<InstructorProfile />}
                />
                <Route
                    path="/instructors/:instructorId/courses"
                    element={<InstructorCourses />}
                />

                {/* Course Route with Nested Routing */}
                <Route path="/courses/:courseId/*" element={<CoursePage />} />

                {/* 404 Not Found Page */}
                <Route path="*" element={<NotFoundPage />} />
            </Route>
        </Routes>
    );
}