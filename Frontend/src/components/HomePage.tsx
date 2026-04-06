import { useState, useEffect } from "react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
// Import Dialog components
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "./ui/dialog";
import { Info, X, Play, FileText } from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

export function HomePage() {
  const [showInstructions, setShowInstructions] = useState(true);
  const [isHelpDialogOpen, setIsHelpDialogOpen] = useState(false);
  const [isYoutubeDialogOpen, setIsYoutubeDialogOpen] = useState(false);

  // Instruction dialog state
  const [selectedInstruction, setSelectedInstruction] = useState<{
    title: string;
    excerpt?: string;
    content: string;
  } | null>(null);
  const [isInstructionDialogOpen, setIsInstructionDialogOpen] = useState(false);

  const instructions = [
    {
      id: "discord-chat",
      title: "How to use ChatBot in Discord",
      excerpt:
          "Detailed steps on integrating and using the CourseGPT bot within Discord channels...",
      content:
          "1) Invite the bot to your server.\n\n2) Ensure your server name matches the course name.\n\n3) Students can ask the bot using /ask and instructors can use /ask for course-specific queries.",
    },
    {
      id: "discord-register",
      title: "How students are registered on Discord",
      excerpt:
          "Instructions for students on joining the Discord server and verifying their accounts...",
      content:
          "Students must simply join the server. Our Discord bot automatically registers them! However, they can verify their registration status by using the /status bot command\n\nIf unregistered, they will receive a prompt to manually register using the /register command.",
    },
    {
      id: "upload-materials",
      title: "Uploading Course Materials",
      excerpt:
          "Detailed instructions on how to upload course documents for your courses...",
      content:
          "1) Go to the Dashboard\n\n2) Navigate to the Courses menu.\n\n3) Under 'My Courses', click on your preferred course.\n\n4) To add a new course material, click 'Add Document', select the file(s) then confirm.\n\nOnce your course materials are uploaded, our AI model is ready to answer questions related to those materials!",
    },
  ];

  const { apiClient } = useApiClient();
  const [user, setUser] = useState<{ name?: string } | null>(null);
  const [loadingUser, setLoadingUser] = useState<boolean>(false);

  useEffect(() => {
    const loadInstructor = async () => {
      if (!apiClient?.isAuthenticated()) {
        setUser({ name: "to" });
        return;
      }
      const instructorId = apiClient.getInstructorId?.();
      if (!instructorId) {
        setUser(null);
        return;
      }
      setLoadingUser(true);
      try {
        const { data } = await apiClient.request(
            "GET",
            `/instructors/${instructorId}`,
            { operationId: "get-instructor" }
        );
        const name = data?.name || "";
        setUser({ name });
      } catch {
        setUser(null);
      } finally {
        setLoadingUser(false);
      }
    };
    loadInstructor();
  }, [apiClient]);

  const handleYesClick = () => {
    setShowInstructions(false);
    setIsHelpDialogOpen(true);
  };

  const handleNoClick = () => {
    setShowInstructions(false);
  };

  return (
      <div className="relative w-full flex flex-col items-center justify-center py-16 sm:py-24 space-y-4 text-center">
        <div className="flex flex-col items-center justify-center pt-16 sm:pt-24 space-y-4 text-center">
          <h2 className="text-3xl font-semibold tracking-tight">
            Welcome {loadingUser ? "" : user?.name ?? ""}
          </h2>

          <h1 className="text-4xl font-bold md:text-5xl lg:text-6xl text-primary">
            CourseGPT
          </h1>
          <p className="max-w-xl text-lg text-muted-foreground">
            Your AI assistant for managing course materials and generating
            insights.
          </p>
        </div>

        {showInstructions && (
            <div className="absolute bottom-4 left-4 w-full max-w-sm">
              <Card className="bg-card text-card-foreground border shadow-lg">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <Info className="h-4 w-4 text-primary" />
                    Quick Guide
                  </CardTitle>
                  <Button
                      variant="ghost"
                      size="sm"
                      className="h-6 w-6 p-0"
                      onClick={handleNoClick}
                      aria-label="Close instructions"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </CardHeader>
                <CardContent>
                  <p className="text-xs text-muted-foreground mb-3">
                    Here's some default information on how to integrate content. Use
                    the header links to navigate between your profile and courses.
                    Need more specific instructions?
                  </p>
                  <div className="flex justify-end gap-2">
                    <Button variant="outline" size="sm" onClick={handleNoClick}>
                      No
                    </Button>
                    <Button variant="default" size="sm" onClick={handleYesClick}>
                      Yes
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
        )}

        {/* Help Dialog */}
        <Dialog open={isHelpDialogOpen} onOpenChange={setIsHelpDialogOpen}>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Detailed Instructions</DialogTitle>
              <DialogDescription>Choose a guide to help you get started:</DialogDescription>
            </DialogHeader>

            <div className="space-y-3 py-4 max-h-[60vh] overflow-y-auto">
              {/* Video Guide Option */}
              <button
                  onClick={() => setIsYoutubeDialogOpen(true)}
                  className="w-full text-left border border-primary/20 bg-primary/5 rounded-md p-3 text-sm hover:bg-primary/10 transition flex items-center gap-3"
                  aria-label="Watch Video Guide"
              >
                <div className="bg-primary text-primary-foreground p-2 rounded-full">
                  <Play className="h-4 w-4 fill-current" />
                </div>
                <div>
                  <h4 className="font-bold text-primary">Video Guide</h4>
                  <p className="text-muted-foreground text-xs italic">Step-by-step walkthrough</p>
                </div>
              </button>

              <div className="relative py-2">
                <div className="absolute inset-0 flex items-center"><span className="w-full border-t" /></div>
                <div className="relative flex justify-center text-[10px] uppercase font-bold text-muted-foreground"><span className="bg-background px-2">Written Documentation</span></div>
              </div>

              {instructions.map((instr) => (
                  <button
                      key={instr.id}
                      onClick={() => {
                        setSelectedInstruction(instr);
                        setIsInstructionDialogOpen(true);
                      }}
                      className="w-full text-left border rounded-md p-3 text-sm hover:bg-muted/50 transition flex items-start gap-3"
                      aria-label={`Open instructions: ${instr.title}`}
                  >
                    <FileText className="h-4 w-4 text-muted-foreground mt-0.5" />
                    <div>
                      <h4 className="font-medium mb-1">{instr.title}</h4>
                      <p className="text-muted-foreground text-xs line-clamp-1">{instr.excerpt}</p>
                    </div>
                  </button>
              ))}
            </div>
            <div className="flex justify-end">
              <DialogClose asChild>
                <Button variant="outline">Close</Button>
              </DialogClose>
            </div>
          </DialogContent>
        </Dialog>

        {/* YouTube Video Dialog */}
        <Dialog open={isYoutubeDialogOpen} onOpenChange={setIsYoutubeDialogOpen}>
          <DialogContent className="max-w-3xl p-0 overflow-hidden bg-black border-none">
            <div className="aspect-video w-full bg-black flex items-center justify-center">
              <iframe
                  width="100%"
                  height="100%"
                  src="https://www.youtube.com/embed/Xjzdd_Ogdqo?autoplay=1"
                  title="CourseGPT Video Guide"
                  frameBorder="0"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
              ></iframe>
            </div>
            <div className="p-2 bg-background flex justify-end">
              <DialogClose asChild>
                <Button variant="ghost" size="sm" className="text-xs font-bold uppercase tracking-tighter">Exit Video</Button>
              </DialogClose>
            </div>
          </DialogContent>
        </Dialog>

        {/* Instruction detail dialog */}
        <Dialog
            open={isInstructionDialogOpen}
            onOpenChange={setIsInstructionDialogOpen}
        >
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>{selectedInstruction?.title}</DialogTitle>
              {selectedInstruction?.excerpt && (
                  <DialogDescription>
                    {selectedInstruction.excerpt}
                  </DialogDescription>
              )}
            </DialogHeader>
            <div className="space-y-3 py-4 max-h-[60vh] overflow-y-auto text-sm whitespace-pre-wrap leading-relaxed">
              {selectedInstruction?.content}
            </div>
            <div className="flex justify-end">
              <DialogClose asChild>
                <Button variant="outline">Close</Button>
              </DialogClose>
            </div>
          </DialogContent>
        </Dialog>
      </div>
  );
}