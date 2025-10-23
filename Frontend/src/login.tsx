// import {useState} from "react";
// import {Button} from "./components/ui/button";
// import {Input} from "./components/ui/input";
// import {Label} from "./components/ui/label";
 import './login.css'
// import {Card, CardContent, CardDescription, CardHeader, CardTitle} from "./components/ui/card";

export default function Login() {
    // const [email] = useState("");
    // const [password] = useState("");
    // const [ setIsLoading] = useState(false);
    //
    // const handleSubmit = async (e: React.FormEvent) => {
    //     e.preventDefault();
    //     setIsLoading(true);
    //
    //     // Simulate API call
    //     await new Promise(resolve => setTimeout(resolve, 1000));
    //
    //     console.log("Login attempt:", {email, password});
    //     setIsLoading(false);
    // };
    //
    // const handleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    //     console.log(event.currentTarget.name);
    // }
    //
    // const handleRegister = () => {
    //     console.log("Navigate to registration page");
    //     // TODO: Add navigation to registration page
    // };
    //
    // const handleForgotPassword = () => {
    //     console.log("Navigate to forgot password page");
    //     // TODO: Add navigation to forgot password page
    // };

    return (
        <div className="login-container">
            <header className="login-header">
                <span className="logo" role="img" aria-label="graduation cap">🎓</span>
                <span className="brand">CourseGPT</span>
                <div className="header-buttons">
                    <button className="header-btn">Login</button>
                    <button className="header-btn secondary">Register</button>
                </div>
            </header>
            <main className="login-main">
                <h1>Login</h1>
                <form className="login-form">
                    <input type="email" placeholder="Email" required />
                    <input type="password" placeholder="Password" required />
                    <button className="login-btn" type="submit">Login</button>
                    <button className="Register-btn" type="submit">Register</button>
                </form>
            </main>
        </div>
    );
}