import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "./ui/dialog";
import { Send, Loader2, Paperclip, X } from "lucide-react";
import { useApiClient } from "../clients/ApiClientContext";

interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
  imageName?: string;
  imagePreviewUrl?: string;
}

export function CourseChatPage({
  course,
  studentId,
}: {
  course: any;
  studentId?: string | null;
}) {
  const { queryClient } = useApiClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [selectedImagePreviewUrl, setSelectedImagePreviewUrl] = useState<string | null>(null);
  const [retainedImage, setRetainedImage] = useState<File | null>(null);
  const [retainedImagePreviewUrl, setRetainedImagePreviewUrl] = useState<string | null>(null);
  const [previewImage, setPreviewImage] = useState<{ url: string; name: string } | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const imageUrlsRef = useRef<string[]>([]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    return () => {
      imageUrlsRef.current.forEach((url) => URL.revokeObjectURL(url));
    };
  }, []);

  const clearPendingImage = () => {
    if (selectedImagePreviewUrl && selectedImagePreviewUrl !== retainedImagePreviewUrl) {
      URL.revokeObjectURL(selectedImagePreviewUrl);
      imageUrlsRef.current = imageUrlsRef.current.filter((url) => url !== selectedImagePreviewUrl);
    }
    setSelectedImage(null);
    setSelectedImagePreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const clearRetainedImage = () => {
    if (retainedImagePreviewUrl) {
      URL.revokeObjectURL(retainedImagePreviewUrl);
      imageUrlsRef.current = imageUrlsRef.current.filter((url) => url !== retainedImagePreviewUrl);
    }
    setRetainedImage(null);
    setRetainedImagePreviewUrl(null);
  };

  const formatSources = (raw: unknown): string => {
    // Normalize input into tokens
    const tokens: string[] = Array.isArray(raw)
      ? (raw as any[]).flatMap((x) =>
          typeof x === "string" ? x.split(/\s*;\s*/).map((s) => s.trim()) : []
        )
      : typeof raw === "string"
      ? raw.split(/\s*;\s*/).map((s) => s.trim())
      : [];

    const map = new Map<string, Set<number>>();

    for (const t of tokens) {
      if (!t) continue;

      // Extract page number if present, and filename without the parentheses part
      const pageMatch = t.match(/\(.*?(\d+).*?\)/);
      const pageNum = pageMatch ? parseInt(pageMatch[1], 10) : NaN;

      // Remove any parenthetical content to get filename, then trim
      const filename = t.replace(/\(.*\)/g, "").trim();

      if (!filename) continue;
      if (!map.has(filename)) map.set(filename, new Set<number>());
      if (!Number.isNaN(pageNum)) {
        map.get(filename)!.add(pageNum);
      }
    }

    // Build formatted lines with pages sorted numerically
    const lines: string[] = [];
    for (const [filename, pagesSet] of map) {
      const pagesArr = Array.from(pagesSet);
      pagesArr.sort((a, b) => a - b);
      const pagesStr = pagesArr.length
        ? " " + pagesArr.map((n) => `(page ${n})`).join(" ")
        : "";
      lines.push(filename + pagesStr);
    }

    return lines.join("\n");
  };

  const streamMessage = async (
    fullContent: string,
    messageId: string,
    speed: number = 20
  ) => {
    let currentIndex = 0;

    const interval = setInterval(() => {
      currentIndex++;
      const displayedContent = fullContent.slice(0, currentIndex);

      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === messageId
            ? { ...msg, content: displayedContent, isStreaming: true }
            : msg
        )
      );

      if (currentIndex >= fullContent.length) {
        clearInterval(interval);
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === messageId ? { ...msg, isStreaming: false } : msg
          )
        );
      }
    }, speed);
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputValue.trim() && !selectedImage && !retainedImage) return;

    const questionText = inputValue.trim() || "Please explain the uploaded image in detail.";
    const imageToSend = selectedImage ?? retainedImage;
    const imagePreviewUrl = selectedImagePreviewUrl ?? retainedImagePreviewUrl;
    const isUsingRetainedImage = !selectedImage && !!retainedImage;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: imageToSend
        ? `${questionText}\n\n[${isUsingRetainedImage ? "Using previous image" : "Attached image"}: ${imageToSend.name}]`
        : questionText,
      timestamp: new Date().toISOString(),
      imageName: imageToSend?.name,
      imagePreviewUrl: imagePreviewUrl ?? undefined,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
    if (selectedImage && selectedImagePreviewUrl) {
      if (retainedImagePreviewUrl && retainedImagePreviewUrl !== selectedImagePreviewUrl) {
        URL.revokeObjectURL(retainedImagePreviewUrl);
        imageUrlsRef.current = imageUrlsRef.current.filter((url) => url !== retainedImagePreviewUrl);
      }
      setRetainedImage(selectedImage);
      setRetainedImagePreviewUrl(selectedImagePreviewUrl);
    }
    setSelectedImage(null);
    setSelectedImagePreviewUrl(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    setLoading(true);
    setError(null);

    try {
      const assistantMessageId = `assistant-${Date.now()}`;
      const placeholderMessage: Message = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        timestamp: new Date().toISOString(),
        isStreaming: true,
      };

      setMessages((prev) => [...prev, placeholderMessage]);

      // Use ApiClient to query the course
      const { data, errorMessage } = await queryClient.queryCourse(
        course.id,
        questionText,
        imageToSend,
        studentId
      );

      if (errorMessage) {
        throw new Error(errorMessage);
      }

      const answer = data?.answer || "No response received";
      const sources = data?.sources || "No sources retrieved";
      const sourcesContent = "\n📚 Sources:\n" + formatSources(sources ?? []);
      // Start streaming animation for message
      await streamMessage(answer + sourcesContent, assistantMessageId, 20);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Failed to get response";
      setError(errorMessage);

      const errorMessageObj: Message = {
        id: `error-${Date.now()}`,
        role: "assistant",
        content: `⚠️ Error: ${errorMessage}`,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessageObj]);
    } finally {
      setLoading(false);
    }
  };

  const handleImageSelection = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] ?? null;
    if (!file) {
      setSelectedImage(null);
      return;
    }

    if (!["image/png", "image/jpeg"].includes(file.type)) {
      setError("Please upload a PNG or JPEG image.");
      clearPendingImage();
      e.target.value = "";
      return;
    }

    clearPendingImage();

    const nextPreviewUrl = URL.createObjectURL(file);
    imageUrlsRef.current.push(nextPreviewUrl);
    setError(null);
    setSelectedImage(file);
    setSelectedImagePreviewUrl(nextPreviewUrl);
  };

  return (
    <>
      <div className="chat-container">
        {/* Chat Header */}
        <div className="chat-header">
          <h2 className="text-lg font-semibold">Course AI Assistant</h2>
          <p className="text-xs sm:text-sm text-muted-foreground mt-1">
            Ask questions about {course.name}
          </p>
        </div>

        {/* Messages Container */}
        <div className="chat-messages">
          {messages.length === 0 ? (
            <div className="chat-empty-state">
              <div className="text-5xl mb-4">💬</div>
              <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                Ask questions about the course material and get instant answers
                powered by AI.
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${
                  message.role === "user" ? "justify-end" : "justify-start"
                } animate-fadeIn`}
              >
                <div
                  className={`chat-message ${
                    message.role === "user"
                      ? "chat-message-user"
                      : "chat-message-assistant"
                  }`}
                >
                  {message.imagePreviewUrl && (
                    <button
                      type="button"
                      className="mb-3 block overflow-hidden rounded-lg border bg-background/30 text-left"
                      onClick={() =>
                        setPreviewImage({
                          url: message.imagePreviewUrl!,
                          name: message.imageName || "Uploaded image",
                        })
                      }
                    >
                      <img
                        src={message.imagePreviewUrl}
                        alt={message.imageName || "Uploaded image"}
                        className="max-h-44 w-auto object-cover"
                      />
                      <div className="px-3 py-2 text-xs opacity-80">
                        {message.imageName || "Uploaded image"} - Click to preview
                      </div>
                    </button>
                  )}
                  <p className="chat-content">
                    {message.content}
                    {message.isStreaming && (
                      <span className="inline-block w-2 h-5 ml-1 bg-current animate-streamingCursor" />
                    )}
                  </p>
                  {message.timestamp && (
                    <p className="chat-timestamp">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </p>
                  )}
                </div>
              </div>
            ))
          )}
          {messages.length === 0 ? null : <div ref={messagesEndRef} />}
        </div>

        {/* Input Area */}
        <div className="chat-input-area">
          {error && (
            <div className="mb-3 p-2 rounded bg-destructive/10 text-destructive text-xs">
              {error}
            </div>
          )}
          {!selectedImage && retainedImage && retainedImagePreviewUrl && (
            <div className="mb-3 rounded border bg-primary/5 px-3 py-3 text-sm">
              <div className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                Using previous image for follow-up questions
              </div>
              <div className="relative inline-block overflow-hidden rounded-lg border bg-background">
                <button
                  type="button"
                  className="block"
                  onClick={() =>
                    setPreviewImage({
                      url: retainedImagePreviewUrl,
                      name: retainedImage.name,
                    })
                  }
                >
                  <img
                    src={retainedImagePreviewUrl}
                    alt={retainedImage.name}
                    className="max-h-28 w-auto object-cover"
                  />
                </button>
                <Button
                  type="button"
                  variant="secondary"
                  size="icon"
                  className="absolute right-2 top-2 h-7 w-7 rounded-full shadow-sm"
                  onClick={clearRetainedImage}
                  title="Clear follow-up image context"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
              <div className="mt-2 flex items-center justify-between gap-3">
                <span className="truncate">{retainedImage.name}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  onClick={clearRetainedImage}
                >
                  Clear image context
                </Button>
              </div>
            </div>
          )}
          {selectedImage && (
            <div className="mb-3 rounded border bg-muted/40 px-3 py-3 text-sm">
              {selectedImagePreviewUrl && (
                <div className="relative mb-3 inline-block overflow-hidden rounded-lg border bg-background">
                  <button
                    type="button"
                    className="block"
                    onClick={() =>
                      setPreviewImage({
                        url: selectedImagePreviewUrl,
                        name: selectedImage.name,
                      })
                    }
                  >
                    <img
                      src={selectedImagePreviewUrl}
                      alt={selectedImage.name}
                      className="max-h-36 w-auto object-cover"
                    />
                  </button>
                  <Button
                    type="button"
                    variant="secondary"
                    size="icon"
                    className="absolute right-2 top-2 h-7 w-7 rounded-full shadow-sm"
                    onClick={clearPendingImage}
                    title="Remove attached image"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                </div>
              )}
              <div className="flex items-center justify-between gap-3">
                <span className="truncate">Attached image: {selectedImage.name}</span>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="h-7 w-7"
                  onClick={clearPendingImage}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
          <form onSubmit={handleSendMessage} className="flex gap-2">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/png,image/jpeg"
              className="hidden"
              onChange={handleImageSelection}
            />
            <Button
              type="button"
              variant="outline"
              size="icon"
              disabled={loading}
              onClick={() => fileInputRef.current?.click()}
              title="Attach PNG or JPEG image"
            >
              <Paperclip className="h-4 w-4" />
            </Button>
            <Input
              type="text"
              placeholder="Ask a question about the course or an attached image..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={loading}
              className="flex-1"
            />
            <Button
              type="submit"
              disabled={loading || (!inputValue.trim() && !selectedImage && !retainedImage)}
              size="icon"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </form>
        </div>
      </div>
      <Dialog open={!!previewImage} onOpenChange={(open) => !open && setPreviewImage(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{previewImage?.name || "Image preview"}</DialogTitle>
          </DialogHeader>
          {previewImage && (
            <div className="flex justify-center">
              <img
                src={previewImage.url}
                alt={previewImage.name}
                className="max-h-[70vh] w-auto rounded-lg object-contain"
              />
            </div>
          )}
        </DialogContent>
      </Dialog>
    </>
  );
}
