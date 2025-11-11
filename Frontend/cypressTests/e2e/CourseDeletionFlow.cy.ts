/// <reference types="cypress" />

describe('Course Deletion Flow', () => {
    // Test case 1: allows an instructor to delete a course after creating it
    it('allows an instructor to delete a course after creating it', () => {
        const instructor = {
            id: 'instructor-1',
            name: 'Dr. Johnny Smith',
            title: 'Professor',
            university: 'Perdue University',
            email: 'Jsmith@perdue.edu',
            password: 'van-dijk-420',
        };

        const existingCourses = [
            {
                id: 'course-001',
                instructor_id: instructor.id,
                name: 'Intro to AI',
                institution: 'Perdue University',
                semester_id: 4,
                year: 2024,
                created_at: '2024-08-15T12:00:00.000Z',
            },
        ];

        const newCourse = {
            id: 'course-100',
            name: 'Advanced Algorithms',
            institution: 'Perdue University',
            semesterLabel: 'Fall',
            semester_id: 4,
            year: 2025,
            created_at: '2025-02-01T10:00:00.000Z',
        };

        let courses = [...existingCourses];

        cy.window().then((win) => {
            win.localStorage.clear();
        });

        cy.intercept('POST', '**/auth/login', (req) => {
            const body = req.body as string;
            expect(body).to.include(`username=${encodeURIComponent(instructor.email)}`);
            expect(body).to.include(`password=${encodeURIComponent(instructor.password)}`);

            req.reply({
                statusCode: 200,
                body: {
                    access_token: 'login-token',
                    token_type: 'bearer',
                    instructor_id: instructor.id,
                },
            });
        }).as('loginInstructor');

        cy.intercept('GET', `**/instructors/${instructor.id}`, {
            statusCode: 200,
            body: {
                id: instructor.id,
                name: instructor.name,
                title: instructor.title,
                university: instructor.university,
                email: instructor.email,
                created_at: '2024-05-01T12:00:00.000Z',
            },
        }).as('getInstructorProfile');

        cy.intercept('GET', `**/instructors/${instructor.id}/courses*`, (req) => {
            req.reply({
                statusCode: 200,
                body: {
                    total: courses.length,
                    courses,
                },
            });
        }).as('getCourses');

        cy.intercept('POST', `**/instructors/${instructor.id}/courses*`, (req) => {
            const url = new URL(req.url);
            const name = url.searchParams.get('name') ?? '';
            const institution = url.searchParams.get('institution') ?? '';
            const semesterId = Number(url.searchParams.get('semester_id'));
            const year = Number(url.searchParams.get('year'));

            expect(name).to.eq(newCourse.name);
            expect(institution).to.eq(newCourse.institution);
            expect(semesterId).to.eq(newCourse.semester_id);
            expect(year).to.eq(newCourse.year);

            const createdCourse = {
                id: newCourse.id,
                instructor_id: instructor.id,
                name,
                institution,
                semester_id: semesterId,
                year,
                created_at: newCourse.created_at,
            };

            courses = [createdCourse, ...courses];

            req.reply({
                statusCode: 200,
                body: createdCourse,
            });
        }).as('createCourse');

        cy.intercept('DELETE', `**/courses/${newCourse.id}`, (req) => {
            courses = courses.filter((course) => course.id !== newCourse.id);
            req.reply({
                statusCode: 204,
                body: null,
            });
        }).as('deleteCourse');

        cy.visit('http://sdmay26-37.ece.iastate.edu/login');

        cy.get('input#email').type(instructor.email);
        cy.get('input#password').type(instructor.password, { log: false });
        cy.contains('button', 'Sign in').click();

        cy.wait('@loginInstructor');
        cy.wait('@getInstructorProfile');
        cy.url().should('include', `/instructors/${instructor.id}/profile`);

        cy.contains('button', 'Courses').click();

        cy.url().should('include', `/instructors/${instructor.id}/courses`);
        cy.wait('@getCourses');

        cy.contains('button', 'Register New Course').click();

        cy.get('#courseName-dialog').type(newCourse.name);
        cy.get('#institution-dialog').type(newCourse.institution);
        cy.get('#semester-dialog').click();
        cy.get('[data-radix-select-item]').contains('Fall').click();
        cy.contains('[data-radix-select-item]', newCourse.semesterLabel).click();
        cy.get('#year-dialog').clear().type(String(newCourse.year));

        cy.contains('button', 'Register Course').click();

        cy.wait('@createCourse');
        cy.wait('@getCourses');
        cy.contains('Enter the details for the new course.').should('not.exist');
        cy.contains('h3', newCourse.name).should('be.visible');

        cy.contains('h3', newCourse.name)
            .closest('.relative')
            .find('button[aria-label="Course Settings"]')
            .click();

        cy.contains('button', 'Delete Course').click();

        cy.contains(`Delete "${newCourse.name}"?`).should('be.visible');

        cy.contains('button', 'Confirm Delete').click();

        cy.contains('Final Confirmation').should('be.visible');

        cy.contains('button', 'Yes, Delete Permanently').click();

        cy.wait('@deleteCourse');
        cy.wait('@getCourses');

        cy.contains('h3', newCourse.name).should('not.exist');
    });
});