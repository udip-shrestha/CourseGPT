import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Alert, AlertDescription } from "./ui/alert";
import { AlertCircle, ExternalLink } from "lucide-react";

export function CourseIntegrationsPage({ course }: { course: any }) {
  const DISCORD_BOT_INVITE_URL =
    "https://discord.com/oauth2/authorize?client_id=1420791310109118595&permissions=2270639957077008&integration_type=0&scope=bot";

  const DISCORD_SERVER_GUIDE_URL =
    "https://support.discord.com/hc/en-us/articles/204849977-How-do-I-create-a-server";

  return (
    <div className="space-y-3">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-6">
        <h2 className="text-xl font-semibold">Course Integrations</h2>
        <p className="text-sm text-muted-foreground mt-2 sm:mt-0">
          Connect external tools to enhance your course
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Discord Integration Column */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>🤖</span> Discord Integration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Here is how to integrate our Discord CyCourseBot to your Discord
              server:
            </p>

            <ol className="space-y-4 list-decimal list-inside">
              <li className="text-sm">
                <span className="font-medium">
                  Download Discord on your PC.
                </span>
                <p className="text-xs text-muted-foreground mt-1 ml-4">
                  Visit{" "}
                  <a
                    href="https://discord.com/download"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    discord.com
                  </a>{" "}
                  to download the desktop or web version.
                </p>
              </li>

              <li className="text-sm">
                <span className="font-medium">
                  Ensure your Discord server is created.
                </span>
                <p className="text-xs text-muted-foreground mt-1 ml-4">
                  If you don't have one yet, follow{" "}
                  <a
                    href={DISCORD_SERVER_GUIDE_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline inline-flex items-center gap-1"
                  >
                    this guide <ExternalLink className="h-3 w-3" />
                  </a>
                  .
                </p>
                <Alert className="mt-2 ml-4 bg-amber-50 border-amber-200 dark:bg-slate-100 dark:text-slate-800 dark:border-slate-700">
                  <AlertCircle className="h-4 w-4 text-amber-600" />
                  <AlertDescription className="text-xs text-amber-800">
                    <span>
                      <strong>Important:</strong> Ensure your Discord server's
                      name matches the course name "
                      <strong>{course?.name}</strong>" for the bot to work
                      correctly.
                    </span>
                  </AlertDescription>
                </Alert>
              </li>

              <li className="text-sm">
                <span className="font-medium">
                  Click the link below to add the bot to your server:
                </span>
                <div className="mt-3 ml-4">
                  <a
                    href={DISCORD_BOT_INVITE_URL}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                  >
                    <span>Add CyCourseBot to Discord</span>
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </div>
              </li>

              <li className="text-sm">
                <span className="font-medium">
                  Select your server and authorize the bot.
                </span>
                <p className="text-xs text-muted-foreground mt-1 ml-4">
                  Discord will ask you to log in (if needed) and then show a
                  selection menu. Choose your server and click "Continue" to
                  authorize the bot with the necessary permissions.
                </p>
              </li>

              <li className="text-sm">
                <span className="font-medium">Start using the bot!</span>
                <p className="text-xs text-muted-foreground mt-1 ml-4">
                  Once added, students can use the following commands in your
                  Discord server:
                </p>
                <div className="mt-2 ml-4 space-y-1 bg-muted p-3 rounded-lg">
                  <p className="text-xs font-mono">
                    <span className="font-bold">/register</span> - Register for
                    the course
                  </p>
                  <p className="text-xs font-mono">
                    <span className="font-bold">/ask</span> - Ask our LLM model
                    a question about the course materials
                  </p>
                  <p className="text-xs font-mono">
                    <span className="font-bold">/help</span> - View available
                    commands
                  </p>
                  <Alert className="mt-10 bg-blue-50 border-blue-200 dark:bg-slate-100 dark:text-slate-800 dark:border-slate-700">
                    <AlertCircle className="h-4 w-4 text-blue-600" />
                    <AlertDescription className="text-xs text-blue-800">
                      <span>
                        The bot will automatically register students when they
                        join your Discord server. They can also manually
                        register using the{" "}
                        <span className="font-mono font-bold">/register</span>{" "}
                        command.
                      </span>
                    </AlertDescription>
                  </Alert>
                </div>
              </li>
            </ol>
          </CardContent>
        </Card>

        {/* Canvas Integration Column */}
        <Card className="lg:col-span-1">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <span>📚</span> Canvas Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col items-center justify-center py-20 text-center">
              <div className="text-6xl mb-4">🚀</div>
              <p className="text-lg font-semibold text-gray-800 dark:text-gray-200">
                Coming Soon!
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                Canvas integration is currently in development. Check back soon
                for direct Canvas course synchronization.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
