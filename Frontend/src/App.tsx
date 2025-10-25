import { Routes, Route } from "react-router-dom";
import { Header } from "./components/Header";
import { HomePage } from "./components/HomePage";
import { LoginPage } from "./components/LoginPage";
import { RegisterPage } from "./components/RegisterPage";
import { InstructorProfile } from "./components/InstructorProfile";
import { InstructorCourses } from "./components/InstructorCourses";
import { CoursePage } from "./components/CoursePage";

export default function App() {
  return (
    <div className="min-h-screen bg-background text-foreground transition-all duration-300">
      {/* Header visible on all routes */}
      <Header />

      {/* Main routed content */}
      <main className="w-full max-w-[1920px] mx-auto px-6 sm:px-8 py-10">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          
          <Route path="/instructors/:instructorId/profile" element={<InstructorProfile />} />
          <Route path="/instructors/:instructorId/courses" element={<InstructorCourses />} />

          <Route path="/courses/:courseId" element={<CoursePage />} />
        </Routes>
      </main>
    </div>
  );
}
