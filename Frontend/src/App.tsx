import { Routes, Route, Outlet } from "react-router-dom";
import { Header } from "./components/Header";
import { HomePage } from "./components/HomePage";
import { LoginPage } from "./components/LoginPage";
import { RegisterPage } from "./components/RegisterPage"; // This is your Instructor Registration page
import { InstructorProfile } from "./components/InstructorProfile";
import { InstructorCourses } from "./components/InstructorCourses";
import { NotFoundPage } from "./components/NotFoundPage";
import { CoursePage } from "./components/CoursePage";
import { CanvasLinkPage } from "./components/CanvasLinkPage";

/**
 * The main Layout component.
 * This includes the Header (which is on every page)
 * and an <Outlet />. The <Outlet /> is a placeholder where
 * React Router will render the correct page (e.g., HomePage, LoginPage, etc.).
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
 * It now *only* defines the routes.
 * The <Layout /> route acts as a wrapper for all other pages.
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
        {/* The "/*" at the end is critical for nested routes like /chat, /settings */}
        <Route path="/courses/:courseId/*" element={<CoursePage />} />

        {/* 404 Not Found Page */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
