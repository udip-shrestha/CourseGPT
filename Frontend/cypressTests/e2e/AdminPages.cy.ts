/// <reference types="cypress" />

/**
 * Admin routes live under `/instructors/:instructorId/admin/*` and require
 * `coursegpt_token` plus `coursegpt_instructor_role` === "ADMIN" (see App.tsx AdminLayout).
 */

const ADMIN_INSTRUCTOR_ID = "cypress-admin-instructor";

function seedAdminSession(win: Window) {
  win.localStorage.setItem("coursegpt_token", "cypress-admin-token");
  win.localStorage.setItem("coursegpt_instructor_role", "ADMIN");
}

function visitAdmin(path: string) {
  cy.visit("/", {
    onBeforeLoad(win) {
      seedAdminSession(win);
    },
  });

  if (path !== "/") {
    cy.window().then((win) => {
      win.history.pushState({}, "", path);
      win.dispatchEvent(new PopStateEvent("popstate"));
    });
  }
}

/** Avoids failed network calls when smoke-testing dashboard navigation. */
function stubAdminDashboardNavigationApis() {
  cy.intercept("GET", "**/discord-admins*", {
    statusCode: 200,
    body: { admins: [], total: 0 },
  });

  const overview = {
    totalDocuments: 0,
    totalCourses: 0,
    totalInstructors: 0,
    totalStudents: 0,
    totalQueries: 0,
    totalFeedback: 0,
    averageDocumentsPerCourse: 0,
    averageCoursesPerInstructor: 0,
    averageQueriesPerCourse: 0,
  };

  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/system-overview`,
    { statusCode: 200, body: overview },
  );
  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/system-query-trend*`,
    { statusCode: 200, body: [] },
  );
  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/documents-by-course`,
    { statusCode: 200, body: [] },
  );
  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/documents-by-instructor`,
    { statusCode: 200, body: [] },
  );
  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/courses-by-instructor`,
    { statusCode: 200, body: [] },
  );
  cy.intercept(
    "GET",
    `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/queries-by-course*`,
    { statusCode: 200, body: [] },
  );
}

describe("Admin dashboard (AdminPage)", () => {
  it("shows the dashboard title and section cards", () => {
    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin`);

    cy.contains("h1", "Admin Dashboard").should("be.visible");
    cy.contains("Manage instructors, courses, and Discord bot admins.").should(
      "be.visible",
    );

    cy.contains("Instructors").should("be.visible");
    cy.contains("Courses").should("be.visible");
    cy.contains("Analytics").should("be.visible");
    cy.contains("Discord admins").should("be.visible");
  });

  it("navigates from the dashboard to nested admin routes", () => {
    stubAdminDashboardNavigationApis();

    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin`);

    cy.contains("Instructors").click();
    cy.url().should(
      "include",
      `/instructors/${ADMIN_INSTRUCTOR_ID}/admin/instructors`,
    );
    cy.go("back");

    cy.contains("Analytics").click();
    cy.url().should(
      "include",
      `/instructors/${ADMIN_INSTRUCTOR_ID}/admin/analytics`,
    );
    cy.go("back");

    cy.contains("Discord admins").click();
    cy.url().should(
      "include",
      `/instructors/${ADMIN_INSTRUCTOR_ID}/admin/discord-admins`,
    );
  });
});

describe("Admin analytics (AdminAnalyticsPage → SystemAnalyticsPage)", () => {
  beforeEach(() => {
    const overview = {
      totalDocuments: 1,
      totalCourses: 2,
      totalInstructors: 3,
      totalStudents: 4,
      totalQueries: 5,
      totalFeedback: 6,
      averageDocumentsPerCourse: 0.5,
      averageCoursesPerInstructor: 1.2,
      averageQueriesPerCourse: 2.5,
    };

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/system-overview`,
      { statusCode: 200, body: overview },
    ).as("systemOverview");

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/system-query-trend*`,
      { statusCode: 200, body: [] },
    ).as("systemQueryTrend");

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/documents-by-course`,
      { statusCode: 200, body: [] },
    ).as("documentsByCourse");

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/documents-by-instructor`,
      { statusCode: 200, body: [] },
    ).as("documentsByInstructor");

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/courses-by-instructor`,
      { statusCode: 200, body: [] },
    ).as("coursesByInstructor");

    cy.intercept(
      "GET",
      `**/instructors/${ADMIN_INSTRUCTOR_ID}/analytics/queries-by-course*`,
      { statusCode: 200, body: [] },
    ).as("queriesByCourse");
  });

  it("loads system analytics after API calls succeed", () => {
    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin/analytics`);

    cy.wait([
      "@systemOverview",
      "@systemQueryTrend",
      "@documentsByCourse",
      "@documentsByInstructor",
      "@coursesByInstructor",
      "@queriesByCourse",
    ]);

    cy.contains("h1", "CourseGPT Platform Overview").should("be.visible");
    cy.contains("Platform Snapshot").should("be.visible");
  });
});

describe("Discord bot admins (AdminDiscordAdminsPage)", () => {
  it("shows empty state when the API returns no admins", () => {
    cy.intercept("GET", "**/discord-admins*", {
      statusCode: 200,
      body: { admins: [], total: 0 },
    }).as("listDiscordAdminsEmpty");

    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin/discord-admins`);

    cy.wait("@listDiscordAdminsEmpty");

    cy.contains("h1", "Discord Bot Admins").should("be.visible");
    cy.contains("No Discord admins yet.").should("be.visible");
  });

  it("renders admins returned by the API", () => {
    cy.intercept("GET", "**/discord-admins*", {
      statusCode: 200,
      body: {
        admins: [
          {
            id: "row-1",
            discord_id: "851234567890123456",
            name: "Cypress Bot Admin",
            created_at: "2025-06-01T12:00:00.000Z",
          },
        ],
        total: 1,
      },
    }).as("listDiscordAdmins");

    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin/discord-admins`);

    cy.wait("@listDiscordAdmins");

    cy.contains("h3", "Cypress Bot Admin").should("be.visible");
    cy.contains("851234567890123456").should("be.visible");
  });

  it("filters the displayed rows by name or Discord ID", () => {
    cy.intercept("GET", "**/discord-admins*", {
      statusCode: 200,
      body: {
        admins: [
          {
            id: "a",
            discord_id: "111",
            name: "Alpha",
            created_at: "2025-06-01T12:00:00.000Z",
          },
          {
            id: "b",
            discord_id: "222",
            name: "Beta",
            created_at: "2025-06-01T12:00:00.000Z",
          },
        ],
        total: 2,
      },
    }).as("listDiscordAdminsFilter");

    visitAdmin(`/instructors/${ADMIN_INSTRUCTOR_ID}/admin/discord-admins`);

    cy.wait("@listDiscordAdminsFilter");

    cy.get('input[placeholder*="Filter by name"]').clear().type("Beta");

    cy.contains("h3", "Beta").should("be.visible");
    cy.contains("h3", "Alpha").should("not.exist");
  });
});
