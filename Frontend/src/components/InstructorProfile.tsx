import { Mail, MapPin, Globe, BookOpen, Star } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { ImageWithFallback } from './figma/ImageWithFallback';

export function InstructorProfile() {
  const instructor = {
    name: "Dr. Sarah Johnson",
    title: "Associate Professor of Computer Science",
    university: "Tech University",
    email: "sarah.johnson@techuni.edu",
    location: "San Francisco, CA",
    website: "www.sarahjohnson.edu",
    bio: "Dr. Sarah Johnson is an Associate Professor specializing in Machine Learning and Data Science. She has over 10 years of teaching experience and has published numerous papers in top-tier conferences.",
    specializations: ["Machine Learning", "Data Science", "Python Programming", "Statistics", "Research Methods"],
    courses: 12,
    students: 450,
    rating: 4.8
  };

  return (
    // <div className="container mx-auto px-4 py-8">
      <div className="space-y-8">
        {/* Hero Section */}
        <Card>
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row gap-6 items-start">
              <Avatar className="h-32 w-32">
                <ImageWithFallback 
                  src="https://images.unsplash.com/photo-1559582935-b5b0a8bb19e0?w=300&h=300&fit=crop&crop=face"
                  alt={instructor.name}
                  className="w-full h-full object-cover"
                />
                <AvatarFallback className="text-2xl">SJ</AvatarFallback>
              </Avatar>
              
              <div className="flex-1 space-y-4">
                <div>
                  <h1 className="text-3xl font-bold">{instructor.name}</h1>
                  <p className="text-xl text-muted-foreground">{instructor.title}</p>
                  <p className="text-lg text-muted-foreground">{instructor.university}</p>
                </div>
                
                <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <Mail className="h-4 w-4" />
                    {instructor.email}
                  </div>
                  <div className="flex items-center gap-1">
                    <MapPin className="h-4 w-4" />
                    {instructor.location}
                  </div>
                  <div className="flex items-center gap-1">
                    <Globe className="h-4 w-4" />
                    {instructor.website}
                  </div>
                </div>
                
                <div className="flex gap-6">
                  <div className="text-center">
                    <div className="text-2xl font-bold">{instructor.courses}</div>
                    <div className="text-sm text-muted-foreground">Courses</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">{instructor.students}</div>
                    <div className="text-sm text-muted-foreground">Students</div>
                  </div>
                  <div className="text-center">
                    <div className="flex items-center gap-1">
                      <Star className="h-5 w-5 fill-yellow-400 text-yellow-400" />
                      <span className="text-2xl font-bold">{instructor.rating}</span>
                    </div>
                    <div className="text-sm text-muted-foreground">Rating</div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* About Section */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-4">About</h2>
            <p className="text-muted-foreground leading-relaxed">{instructor.bio}</p>
          </CardContent>
        </Card>

        {/* Specializations */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-4">Specializations</h2>
            <div className="flex flex-wrap gap-2">
              {instructor.specializations.map((spec) => (
                <Badge key={spec} variant="secondary" className="px-3 py-1">
                  {spec}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Featured Courses */}
        <Card>
          <CardContent className="p-6">
            <h2 className="text-xl font-bold mb-4">Featured Courses</h2>
            <div className="grid md:grid-cols-2 gap-4">
              <div className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  <h3 className="font-medium">Introduction to Machine Learning</h3>
                </div>
                <p className="text-sm text-muted-foreground">CS 480 • Fall 2024 • 85 students</p>
              </div>
              <div className="border rounded-lg p-4">
                <div className="flex items-center gap-2 mb-2">
                  <BookOpen className="h-5 w-5 text-primary" />
                  <h3 className="font-medium">Advanced Data Science</h3>
                </div>
                <p className="text-sm text-muted-foreground">CS 580 • Spring 2024 • 62 students</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    // </div>
  );
}