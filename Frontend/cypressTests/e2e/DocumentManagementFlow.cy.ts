/// <reference types="cypress" />

describe('Document Management Flow', () => {
    it('allows an instructor to upload and delete a course document', () => {
        const instructor = {
            id: 'instructor-1',
            name: 'Dr. Johnny Smith',
            title: 'Professor',
            university: 'Perdue University',
            email: 'Jsmith@perdue.edu',
            password: 'van-dijk-420',
        };

        const targetCourse = {
            id: 'course-100',
            instructor_id: instructor.id,
            name: 'Advanced Algorithms',
            institution: 'Perdue University',
            semester_id: 4,
            semester_name: 'Fall',
            year: 2025,
            created_at: '2025-01-10T15:30:00.000Z',
        };

        const existingCourses = [
            {
                ...targetCourse,
                semester_id: 4,
                created_at: '2025-01-10T15:30:00.000Z',
            },
        ];

        const uploadedDocument = {
            id: 'document-123',
            file_name: 'my-test.pdf',
            file_type: 'pdf',
            uploaded_at: '2025-02-01T10:00:00.000Z',
        };

        let documents: Array<typeof uploadedDocument> = [];

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
                    total: existingCourses.length,
                    courses: existingCourses,
                },
            });
        }).as('getCourses');

        cy.intercept('GET', `**/courses/${targetCourse.id}`, {
            statusCode: 200,
            body: {
                id: targetCourse.id,
                name: targetCourse.name,
                institution: targetCourse.institution,
                semester_id: targetCourse.semester_id,
                semester_name: targetCourse.semester_name,
                year: targetCourse.year,
                instructor_id: instructor.id,
                instructor_name: instructor.name,
                instructor_email: instructor.email,
                created_at: targetCourse.created_at,
            },
        }).as('getCourse');

        cy.intercept('GET', `**/courses/${targetCourse.id}/documents*`, (req) => {
            req.reply({
                statusCode: 200,
                body: {
                    total: documents.length,
                    documents,
                },
            });
        }).as('listDocuments');

        cy.intercept('POST', `**/courses/${targetCourse.id}/documents`, (req) => {
            expect(req.headers['content-type'] || '').to.contain('multipart/form-data');

            documents = [
                {
                    ...uploadedDocument,
                    uploaded_at: uploadedDocument.uploaded_at,
                },
                ...documents,
            ];

            req.reply({
                statusCode: 200,
                body: {
                    id: uploadedDocument.id,
                    file_name: uploadedDocument.file_name,
                    file_type: uploadedDocument.file_type,
                    uploaded_at: uploadedDocument.uploaded_at,
                },
            });
        }).as('uploadDocument');

        cy.intercept('DELETE', `**/courses/${targetCourse.id}/documents/${uploadedDocument.id}`, (req) => {
            documents = documents.filter((doc) => doc.id !== uploadedDocument.id);

            req.reply({
                statusCode: 204,
                body: null,
            });
        }).as('deleteDocument');

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

        cy.contains('h3', targetCourse.name).should('be.visible');

        cy.contains('h3', targetCourse.name)
            .closest('.relative')
            .find('button[aria-label="Course Settings"]')
            .click();

        cy.contains('button', 'View Course').click();

        cy.wait('@getCourse');
        cy.wait('@listDocuments');
        cy.url().should('include', `/courses/${targetCourse.id}`);

        cy.contains('button', 'Add Document').click();

        const fileName = uploadedDocument.file_name;
        const fileContent = 'Sample PDF content for Cypress test';

        cy.get('input[type="file"]').selectFile(
            {
                contents: Buffer.from(fileContent, 'utf-8'),
                fileName,
                mimeType: 'application/pdf',
            },
            { force: true },
        );

        cy.contains('button', 'Upload').click();

        cy.wait('@uploadDocument');
        cy.wait('@listDocuments');

        cy.contains('Upload Documents for').should('not.exist');
        cy.contains('p', fileName).should('be.visible');

        cy.contains('p', fileName)
            .closest('div.flex.items-center.justify-between')
            .within(() => {
                cy.get('button').last().click();
            });

        cy.contains('Delete Document').should('be.visible');
        cy.contains('button', 'Delete').click();

        cy.wait('@deleteDocument');
        cy.wait('@listDocuments');

        cy.contains('p', fileName).should('not.exist');
    });
});

