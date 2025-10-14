// import { useState } from "react";
// import { Button } from "./components/ui/button";
// import { Input } from "./components/ui/input";
// import { Label } from "./components/ui/label";
// import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
//
// export default function Login() {
//   const [email, setEmail] = useState("");
//   const [password, setPassword] = useState("");
//   const [isLoading, setIsLoading] = useState(false);
//
//   const handleSubmit = async (e: React.FormEvent) => {
//     e.preventDefault();
//     setIsLoading(true);
//
//     // Simulate API call
//     await new Promise(resolve => setTimeout(resolve, 1000));
//
//     console.log("Login attempt:", { email, password });
//     setIsLoading(false);
//   };
// }