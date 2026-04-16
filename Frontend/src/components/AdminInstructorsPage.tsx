import { useCallback, useEffect, useState } from "react";
import { RefreshCw, ShieldCheck, ShieldOff, Users } from "lucide-react";

import { useApiClient } from "../clients/ApiClientContext";
import { Button } from "./ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "./ui/card";

interface InstructorSummary {
  id: string;
  name: string;
  email: string;
  university?: string;
  role?: string;
}

export function AdminInstructorsPage() {
  const { instructorClient, adminClient } = useApiClient();

  const [instructors, setInstructors] = useState<InstructorSummary[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [nameFilter, setNameFilter] = useState("");
  const [emailFilter, setEmailFilter] = useState("");
  const [universityFilter, setUniversityFilter] = useState("");
  const [roleFilter, setRoleFilter] = useState<"ALL" | "ADMIN" | "INSTRUCTOR">(
    "ALL",
  );

  const [updatingId, setUpdatingId] = useState<string | null>(null);

  const fetchInstructors = useCallback(
    async (showRefreshSpinner = false) => {
      if (showRefreshSpinner) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }

      setError(null);

      const { data, errorMessage } = await instructorClient.listInstructors({
        order_by: "name",
        order_dir: "asc",
        limit: 500,
        offset: 0,
      });

      if (errorMessage) {
        setError(errorMessage);
        setInstructors([]);
      } else {
        setInstructors(data?.instructors ?? data ?? []);
      }

      setIsLoading(false);
      setIsRefreshing(false);
    },
    [instructorClient],
  );

  useEffect(() => {
    fetchInstructors();
  }, [fetchInstructors]);

  async function handleToggleAdmin(instructor: InstructorSummary) {
    const isCurrentlyAdmin = instructor.role === "ADMIN";

    setUpdatingId(instructor.id);
    setError(null);

    const { errorMessage } = await adminClient.updateInstructorAdmin(
      instructor.id,
      !isCurrentlyAdmin,
    );

    if (errorMessage) {
      setError(errorMessage);
      setUpdatingId(null);
      return;
    }

    await fetchInstructors(true);
    setUpdatingId(null);
  }

  function getRoleClasses(roleName?: string) {
    return roleName === "ADMIN"
      ? "bg-green-100 text-green-700 border-green-200"
      : "bg-gray-100 text-gray-700 border-gray-200";
  }

  const filteredInstructors = instructors.filter((instructor) => {
    const matchesName = instructor.name
      ?.toLowerCase()
      .includes(nameFilter.trim().toLowerCase());

    const matchesEmail = instructor.email
      ?.toLowerCase()
      .includes(emailFilter.trim().toLowerCase());

    const matchesUniversity = (instructor.university || "")
      .toLowerCase()
      .includes(universityFilter.trim().toLowerCase());

    const matchesRole =
      roleFilter === "ALL" ? true : instructor.role === roleFilter;

    return matchesName && matchesEmail && matchesUniversity && matchesRole;
  });

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <Users className="h-7 w-7" />
            Admin Instructors
          </h1>
          <p className="text-muted-foreground mt-1">
            View all instructors and manage admin access.
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => fetchInstructors(true)}
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
          <CardTitle>Filters</CardTitle>
          <CardDescription>
            Filter instructors by role, name, email, or university.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="text-sm font-medium mb-1 block">Role</label>
              <select
                value={roleFilter}
                onChange={(e) =>
                  setRoleFilter(
                    e.target.value as "ALL" | "ADMIN" | "INSTRUCTOR",
                  )
                }
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              >
                <option value="ALL">All roles</option>
                <option value="ADMIN">Admin</option>
                <option value="INSTRUCTOR">Instructor</option>
              </select>
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Name</label>
              <input
                type="text"
                value={nameFilter}
                onChange={(e) => setNameFilter(e.target.value)}
                placeholder="Filter by name..."
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">Email</label>
              <input
                type="text"
                value={emailFilter}
                onChange={(e) => setEmailFilter(e.target.value)}
                placeholder="Filter by email..."
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>

            <div>
              <label className="text-sm font-medium mb-1 block">
                University
              </label>
              <input
                type="text"
                value={universityFilter}
                onChange={(e) => setUniversityFilter(e.target.value)}
                placeholder="Filter by university..."
                className="w-full border rounded-md px-3 py-2 text-sm bg-background"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          {isLoading ? (
            <div className="py-16 text-center text-muted-foreground">
              Loading instructors...
            </div>
          ) : error ? (
            <div className="py-12 text-center">
              <p className="text-destructive font-medium mb-2">
                Failed to load instructors.
              </p>
              <p className="text-sm text-muted-foreground mb-4">{error}</p>
              <Button variant="outline" onClick={() => fetchInstructors(true)}>
                Retry
              </Button>
            </div>
          ) : filteredInstructors.length === 0 ? (
            <div className="py-16 text-center">
              <p className="font-medium">No instructors found.</p>
              <p className="text-sm text-muted-foreground mt-1">
                Try changing your filters.
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredInstructors.map((instructor) => {
                const isAdmin = instructor.role === "ADMIN";
                const isUpdating = updatingId === instructor.id;

                return (
                  <div
                    key={instructor.id}
                    className="border rounded-lg p-4 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between"
                  >
                    <div className="space-y-2">
                      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
                        <h3 className="text-lg font-semibold">
                          {instructor.name}
                        </h3>
                        <span
                          className={`inline-flex w-fit items-center rounded-full border px-2.5 py-0.5 text-xs font-medium ${getRoleClasses(
                            instructor.role,
                          )}`}
                        >
                          {isAdmin ? "Admin" : "Instructor"}
                        </span>
                      </div>

                      <div className="text-sm text-muted-foreground space-y-1">
                        <p>
                          <span className="font-medium text-foreground">
                            Email:
                          </span>{" "}
                          {instructor.email}
                        </p>
                        <p>
                          <span className="font-medium text-foreground">
                            University:
                          </span>{" "}
                          {instructor.university || "No university"}
                        </p>
                      </div>
                    </div>

                    <Button
                      type="button"
                      variant={isAdmin ? "destructive" : "default"}
                      onClick={() => handleToggleAdmin(instructor)}
                      disabled={isUpdating}
                      className="w-full lg:w-auto"
                    >
                      {isAdmin ? (
                        <>
                          <ShieldOff className="h-4 w-4 mr-2" />
                          {isUpdating ? "Updating..." : "Revoke Admin"}
                        </>
                      ) : (
                        <>
                          <ShieldCheck className="h-4 w-4 mr-2" />
                          {isUpdating ? "Updating..." : "Make Admin"}
                        </>
                      )}
                    </Button>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}