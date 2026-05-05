/// <reference types="cypress" />

function seedCanvasLinkSession(win: Window) {
  win.localStorage.setItem("coursegpt_token", "cypress-token");
  win.localStorage.setItem("coursegpt_instructor_id", "instructor-canvas-1");
}

describe("CanvasLinkPage", () => {
  it("redirects to home when canvas_course_id is missing", () => {
    cy.visit("/register-course");

    cy.url().should("eq", `${Cypress.config("baseUrl")}/`);
  });

  it("redirects unauthenticated users to login with next param", () => {
    cy.visit("/register-course?canvas_course_id=canvas-123");

    cy.url().should("include", "/login");
    cy.url().should(
      "include",
      "next=%2Fregister-course%3Fcanvas_course_id%3Dcanvas-123",
    );
  });

  it("loads courses, links the selected course, and redirects", () => {
    const courses = [
      {
        id: "course-1",
        name: "Intro to Software Design",
        institution: "Iowa State University",
      },
      {
        id: "course-2",
        name: "Senior Design Studio",
        school: "College of Engineering",
      },
    ];

    cy.intercept("GET", "**/courses/list*", (req) => {
      const instructorId = req.query.instructor_id;
      expect(instructorId).to.eq("instructor-canvas-1");

      req.reply({
        statusCode: 200,
        body: { courses },
      });
    }).as("listCourses");

    cy.intercept("POST", "**/courses/link-canvas*", (req) => {
      const url = new URL(req.url);
      expect(url.searchParams.get("course_id")).to.eq("course-1");
      expect(url.searchParams.get("canvas_context_id")).to.eq("context-42");
      expect(url.searchParams.get("canvas_course_id")).to.eq("canvas-123");

      req.reply({
        statusCode: 200,
        body: { ok: true },
      });
    }).as("linkCanvas");

    cy.visit(
      "/register-course?canvas_course_id=canvas-123&canvas_context_id=context-42",
      {
        onBeforeLoad(win) {
          seedCanvasLinkSession(win);
        },
      },
    );

    cy.wait("@listCourses");

    cy.contains("h2", "Link a Course").should("be.visible");
    cy.contains("Intro to Software Design").click();

    cy.contains("h3", "Confirm Link").should("be.visible");
    cy.contains("button", "Link Course to Canvas").click();

    cy.wait("@linkCanvas");
    cy.contains("Course linked — redirecting...").should("be.visible");

    cy.url().should("include", "/courses/course-1");
  });

  it("shows API errors from failed link attempts", () => {
    cy.intercept("GET", "**/courses/list*", {
      statusCode: 200,
      body: {
        courses: [
          {
            id: "course-9",
            name: "Operating Systems",
            institution: "Iowa State University",
          },
        ],
      },
    }).as("listCoursesFailurePath");

    cy.intercept("POST", "**/courses/link-canvas*", {
      statusCode: 400,
      body: { detail: "Canvas course is already linked." },
    }).as("linkCanvasFailure");

    cy.visit(
      "/register-course?canvas_course_id=canvas-456&canvas_context_id=context-77",
      {
        onBeforeLoad(win) {
          seedCanvasLinkSession(win);
        },
      },
    );

    cy.wait("@listCoursesFailurePath");
    cy.contains("Operating Systems").click();
    cy.contains("button", "Link Course to Canvas").click();

    cy.wait("@linkCanvasFailure");
    cy.contains("Canvas course is already linked.").should("be.visible");
  });
});
