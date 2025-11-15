import { useState, useRef, useEffect } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Send, Loader2 } from "lucide-react";
import { useApiClient } from "../ApiClientContext.tsx";

interface Message {
  id?: string;
  role: "user" | "assistant";
  content: string;
  timestamp?: string;
  isStreaming?: boolean;
}

export function CourseChatPage({ course }: { course: any }) {
  const apiClient = useApiClient();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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

    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: inputValue,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue("");
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
      const { data, errorMessage } = await apiClient.queryCourse(
        course.id,
        userMessage.content
      );

      if (errorMessage) {
        throw new Error(errorMessage);
      }

      const answer = data?.answer || "No response received";

      // Start streaming animation
      await streamMessage(answer, assistantMessageId, 20);
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

  return (
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
        <form onSubmit={handleSendMessage} className="flex gap-2">
          <Input
            type="text"
            placeholder="Ask a question about the course..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            disabled={loading}
            className="flex-1"
          />
          <Button
            type="submit"
            disabled={loading || !inputValue.trim()}
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
  );
}
