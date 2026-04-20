import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Bot, RefreshCw, Trash2 } from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";
import {
  AlertDialog,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "./ui/alert-dialog";

interface DiscordAdminRow {
  id: string;
  discord_id: string;
  name: string;
  created_at: string;
}

const PAGE_SIZE = 100;

export function AdminDiscordAdminsPage() {
  const { adminClient } = useApiClient();

  const [admins, setAdmins] = useState<DiscordAdminRow[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [filterText, setFilterText] = useState("");
  const [newDiscordId, setNewDiscordId] = useState("");
  const [newName, setNewName] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [deletingDiscordId, setDeletingDiscordId] = useState<string | null>(
    null,
  );
  const [pendingDelete, setPendingDelete] = useState<DiscordAdminRow | null>(
    null,
  );

  const fetchAdmins = useCallback(
    async (nextOffset: number, showRefreshSpinner = false) => {
      if (showRefreshSpinner) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      const { data, errorMessage } = await adminClient.listDiscordAdmins({
        limit: PAGE_SIZE,
        offset: nextOffset,
      });

      if (errorMessage) {
        setError(errorMessage);
        setAdmins([]);
        setTotal(0);
      } else if (data) {
        setAdmins((data as { admins?: DiscordAdminRow[] }).admins ?? []);
        setTotal((data as { total?: number }).total ?? 0);
        setOffset(nextOffset);
      } else {
        setAdmins([]);
        setTotal(0);
      }

      setIsLoading(false);
      setIsRefreshing(false);
    },
    [adminClient],
  );

  useEffect(() => {
    fetchAdmins(0);
  }, [fetchAdmins]);

  async function handleCreate(e: FormEvent) {
    e.preventDefault();
    setIsCreating(true);
    setError(null);

    const { errorMessage } = await adminClient.createDiscordAdmin(
      newDiscordId.trim(),
      newName,
    );

    if (errorMessage) {
      setError(errorMessage);
      setIsCreating(false);
      return;
    }

    setNewDiscordId("");
    setNewName("");
    await fetchAdmins(0, true);
    setIsCreating(false);
  }

  async function confirmDelete() {
    if (!pendingDelete) return;

    const discordId = pendingDelete.discord_id;
    setPendingDelete(null);
    setDeletingDiscordId(discordId);
    setError(null);

    const { errorMessage } = await adminClient.deleteDiscordAdmin(discordId);

    if (errorMessage) {
      setError(errorMessage);
      setDeletingDiscordId(null);
      return;
    }

    await fetchAdmins(offset, true);
    setDeletingDiscordId(null);
  }

  const filteredAdmins = admins.filter((row) => {
    const q = filterText.trim().toLowerCase();
    if (!q) return true;
    return (
      row.name.toLowerCase().includes(q) ||
      row.discord_id.toLowerCase().includes(q)
    );
  });

  const canGoPrev = offset > 0;
  const canGoNext = offset + admins.length < total;

  function formatCreatedAt(value: string) {
    try {
      return new Date(value).toLocaleString();
    } catch {
      return value;
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Bot className="h-7 w-7" />
            Discord Bot Admins
          </h1>
          <p className="text-muted-foreground mt-1">
            Users listed here can use admin-only Discord bot commands (for
            example announcements and server management).
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => fetchAdmins(offset, true)}
          disabled={isLoading || isRefreshing}
        >
          <RefreshCw
            className={`h-4 w-4 mr-2 ${isRefreshing ? "animate-spin" : ""}`}
          />
          Refresh
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Add Discord admin</CardTitle>
          <CardDescription>
            Use the user&apos;s numeric Discord ID (Developer Mode → right-click
            user → Copy User ID).
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form
            onSubmit={handleCreate}
            className="flex flex-col gap-4 md:flex-row md:flex-wrap md:items-end"
          >
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-1 block">
                Discord ID
              </label>
              <input
                type="text"
                value={newDiscordId}
                onChange={(e) => setNewDiscordId(e.target.value)}
                placeholder="e.g. 851234567890123456"
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                autoComplete="off"
              />
            </div>
            <div className="flex-1 min-w-[200px]">
              <label className="text-sm font-medium mb-1 block">
                Display name
              </label>
              <input
                type="text"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                placeholder="Name for your records"
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
                autoComplete="off"
              />
            </div>
            <Button type="submit" disabled={isCreating}>
              {isCreating ? "Adding…" : "Add admin"}
            </Button>
          </form>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Registered admins</CardTitle>
          <CardDescription>
            {isLoading
              ? "Loading…"
              : total === 0
                ? "No Discord admins yet."
                : admins.length === 0
                  ? "No entries on this page."
                  : `Showing ${offset + 1}–${offset + admins.length} of ${total}.`}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-1 block">
              Filter this page
            </label>
            <input
              type="text"
              value={filterText}
              onChange={(e) => setFilterText(e.target.value)}
              placeholder="Filter by name or Discord ID…"
              className="w-full max-w-md border rounded-md px-3 py-2 text-sm bg-background"
            />
          </div>

          {total > PAGE_SIZE && (
            <div className="flex flex-wrap gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={!canGoPrev || isLoading || isRefreshing}
                onClick={() => fetchAdmins(Math.max(0, offset - PAGE_SIZE))}
              >
                Previous page
              </Button>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={!canGoNext || isLoading || isRefreshing}
                onClick={() => fetchAdmins(offset + PAGE_SIZE)}
              >
                Next page
              </Button>
            </div>
          )}

          {isLoading ? (
            <div className="py-16 text-center text-muted-foreground">
              Loading Discord admins…
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-destructive font-medium mb-2">
                Something went wrong.
              </p>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Button variant="outline" onClick={() => fetchAdmins(offset, true)}>
                Retry
              </Button>
            </div>
          ) : filteredAdmins.length === 0 ? (
            <div className="py-16 text-center">
              <p className="font-medium">No rows match your filter.</p>
              <p className="text-sm text-muted-foreground mt-1">
                Clear the filter or load another page.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredAdmins.map((row) => {
                const isDeleting = deletingDiscordId === row.discord_id;
                return (
                  <div
                    key={row.id}
                    className="border rounded-lg p-4 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
                  >
                    <div className="space-y-1 text-sm">
                      <h3 className="text-lg font-semibold">{row.name}</h3>
                      <p className="text-muted-foreground">
                        <span className="font-medium text-foreground">
                          Discord ID:
                        </span>{" "}
                        <span className="font-mono">{row.discord_id}</span>
                      </p>
                      <p className="text-muted-foreground">
                        <span className="font-medium text-foreground">
                          Added:
                        </span>{" "}
                        {formatCreatedAt(row.created_at)}
                      </p>
                    </div>
                    <Button
                      type="button"
                      variant="destructive"
                      onClick={() => setPendingDelete(row)}
                      disabled={isDeleting}
                      className="w-full lg:w-auto"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      {isDeleting ? "Removing…" : "Remove"}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      <AlertDialog
        open={!!pendingDelete}
        onOpenChange={(open) => {
          if (!open) setPendingDelete(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Remove Discord admin?</AlertDialogTitle>
            <AlertDialogDescription>
              {pendingDelete ? (
                <>
                  This will remove{" "}
                  <span className="font-medium text-foreground">
                    {pendingDelete.name}
                  </span>{" "}
                  (<span className="font-mono">{pendingDelete.discord_id}</span>)
                  from bot admins. They will lose access to admin-only Discord
                  bot commands.
                </>
              ) : null}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel type="button">Cancel</AlertDialogCancel>
            <Button
              type="button"
              variant="destructive"
              onClick={() => void confirmDelete()}
            >
              Remove admin
            </Button>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
