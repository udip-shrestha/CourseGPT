import { useNavigate } from 'react-router-dom';

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center min-h-[70vh] space-y-6">
      <h1 className="text-4xl font-bold mb-6">CourseGPT</h1>
      <p className="text-muted-foreground mb-10">
        Welcome! Use the buttons below to navigate for quick testing.
      </p>

      <div className="flex flex-col sm:flex-row gap-4">
        <button
          onClick={() => navigate('/login')}
          className="bg-primary text-white px-6 py-2 rounded-lg hover:opacity-90"
        >
          Login
        </button>

        <button
          onClick={() => navigate('/register')}
          className="bg-secondary text-foreground px-6 py-2 rounded-lg hover:opacity-90"
        >
          Register
        </button>

        <button
          onClick={() => navigate('/instructors/123/profile')}
          className="bg-accent text-white px-6 py-2 rounded-lg hover:opacity-90"
        >
          Instructor (Test)
        </button>
      </div>
    </div>
  );
}
