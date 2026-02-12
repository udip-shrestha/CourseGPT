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
  DialogClose, // Added DialogClose for convenience
} from "./ui/dialog";
import { Info, X } from "lucide-react"; // Kept Info, X
import { useApiClient } from "../clients/ApiClientContext";

export function HomePage() {
  // const navigate = useNavigate();
  const [showInstructions, setShowInstructions] = useState(true);
  // State for the second help dialog
  const [isHelpDialogOpen, setIsHelpDialogOpen] = useState(false);

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

  // Example user data - replace with actual auth context later
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
    setShowInstructions(false); // Close the first pop-up
    setIsHelpDialogOpen(true); // Open the dialog
  };

  const handleNoClick = () => {
    setShowInstructions(false); // Close the first pop-up
  };

  return (
    // Make the main container relative to position elements inside it
    <div className="relative w-full flex flex-col items-center justify-center py-16 sm:py-24 space-y-4 text-center">
      {/* Main Content (Centered) */}
      <div className="flex flex-col items-center justify-center pt-16 sm:pt-24 space-y-4 text-center">
        {/* Welcome Message (Top Middle) */}
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

      {/* Instruction Pop-up (Bottom Left) */}
      {showInstructions && (
        <div className="absolute bottom-4 left-4 w-full max-w-sm">
          <Card className="bg-card text-card-foreground border shadow-lg">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium flex items-center gap-2">
                <Info className="h-4 w-4 text-primary" />
                Quick Guide
              </CardTitle>
              {/* Use the "No" click handler for the X button as well */}
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
                {" "}
                {/* Added margin-bottom */}
                Here's some default information on how to integrate content. Use
                the header links to navigate between your profile and courses.
                Need more specific instructions?
              </p>
              {/* Yes/No Buttons */}
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

      {/* --- Help Dialog --- */}
      <Dialog open={isHelpDialogOpen} onOpenChange={setIsHelpDialogOpen}>
        <DialogContent className="max-w-md">
          {" "}
          {/* Adjust width as needed */}
          <DialogHeader>
            <DialogTitle>Detailed Instructions</DialogTitle>
            <DialogDescription>Here are some common tasks:</DialogDescription>
          </DialogHeader>
          <div className="space-y-3 py-4 max-h-[60vh] overflow-y-auto">
            {" "}
            {/* Added scroll */}
            {/* Instruction Items -> clickable buttons that open a dialog */}
            {instructions.map((instr) => (
              <button
                key={instr.id}
                onClick={() => {
                  setSelectedInstruction(instr);
                  setIsInstructionDialogOpen(true);
                }}
                className="w-full text-left border rounded-md p-3 text-sm hover:shadow-sm transition"
                aria-label={`Open instructions: ${instr.title}`}
              >
                <h4 className="font-medium mb-1">{instr.title}</h4>
                <p className="text-muted-foreground text-xs">{instr.excerpt}</p>
              </button>
            ))}
          </div>
          {/* Add a close button to the dialog footer */}
          <div className="flex justify-end">
            <DialogClose asChild>
              <Button variant="outline">Close</Button>
            </DialogClose>
          </div>
        </DialogContent>
      </Dialog>
      {/* Instruction detail dialog (re-used for any instruction) */}
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
          <div className="space-y-3 py-4 max-h-[60vh] overflow-y-auto text-sm whitespace-pre-wrap">
            {selectedInstruction?.content}
          </div>
          <div className="flex justify-end">
            <DialogClose asChild>
              <Button variant="outline">Close</Button>
            </DialogClose>
          </div>
        </DialogContent>
      </Dialog>
      {/* --- Help Dialog --- */}
    </div>
  );
}
