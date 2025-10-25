import './login.css'


export default function HomePage() {
    const handleLogin = () => {
        console.log("Navigate to login page");
        // TODO: Add navigation to login page
    };

    const handleRegister = () => {
        console.log("Navigate to registration page");
        // TODO: Add navigation to registration page
    };

    const handleInstructorTest = () => {
        console.log("Navigate to instructor test page");
        // TODO: Add navigation to instructor test page
    };

    return (
        <div className="login-container">
            <header className="login-header">
                <div className="header-left">
                    <span className="logo" role="img" aria-label="graduation cap">🎓</span>
                    <span className="brand">CourseGPT</span>
                </div>
                <div className="header-buttons">
                    <button className="header-btn primary">Login</button>
                    <button className="header-btn primary">Register</button>
                </div>
            </header>
            <main className="login-main">
                <h1 className="main-title">CourseGPT</h1>
                <p className="welcome-text">Welcome! Use the buttons below to navigate for quick testing.</p>
                <div className="nav-buttons">
                    <button className="nav-btn primary" onClick={handleLogin}>Login</button>
                    <button className="nav-btn secondary" onClick={handleRegister}>Register</button>
                    <button className="nav-btn tertiary" onClick={handleInstructorTest}>Instructor (Test)</button>
                </div>
            </main>
        </div>
    );
}