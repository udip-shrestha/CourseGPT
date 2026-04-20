import { useNavigate } from "react-router-dom";
import { Users, BookOpen, Shield, BarChart, Bot } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "./ui/card";

export function AdminPage() {
    const navigate = useNavigate();

    return (
        <div className="space-y-8">
            <div>
                <h1 className="text-3xl font-bold flex items-center gap-2">
                    <Shield className="h-7 w-7" />
                    Admin Dashboard
                </h1>
                <p className="text-muted-foreground mt-2">
                    Manage instructors, courses, and Discord bot admins.
                </p>
            </div>

            <div className="flex flex-col gap-6 w-full">
                <Card
                    className="cursor-pointer transition hover:shadow-md hover:border-primary"
                    onClick={() => navigate("instructors")}
                >
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Users className="h-5 w-5" />
                            Instructors
                        </CardTitle>
                        <CardDescription>
                            View and manage all instructors.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Open the instructors admin page.
                        </p>
                    </CardContent>
                </Card>

                <Card
                    className="cursor-pointer transition hover:shadow-md hover:border-primary"
                    onClick={() => navigate("courses")}
                >
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BookOpen className="h-5 w-5" />
                            Courses
                        </CardTitle>
                        <CardDescription>
                            View and manage all courses.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Open the courses admin page.
                        </p>
                    </CardContent>
                </Card>
                <Card
                    className="cursor-pointer transition hover:shadow-md hover:border-primary"
                    onClick={() => navigate("analytics")}
                >
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <BarChart className="h-5 w-5" />
                            Analytics
                        </CardTitle>
                        <CardDescription>
                            View system analytics and insights.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Open analytics dashboard.
                        </p>
                    </CardContent>
                </Card>

                <Card
                    className="cursor-pointer transition hover:shadow-md hover:border-primary"
                    onClick={() => navigate("discord-admins")}
                >
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <Bot className="h-5 w-5" />
                            Discord admins
                        </CardTitle>
                        <CardDescription>
                            Control who can use admin-only Discord bot commands.
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-muted-foreground">
                            Open the Discord admin page.
                        </p>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}