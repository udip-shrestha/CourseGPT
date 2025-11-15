/// <reference types="cypress" />

describe('Instructor Registration & Login Flow', () => {
    // Test case 3: Allows a new instructor to register and sign in
    it('allows a new instructor to register and sign in', () => {
        // Define the instructor data
        const instructor = {
            id: 'instructor-1',
            name: 'Dr. Johnny Smith',
            title: 'Professor',
            university: 'Perdue University',
            email: `Jsmith@perdue.edu`,
            password: 'van-dijk-420',
        }
        // Define the instructor ID
        const instructorId = 'instructor-1'

        // Clear the local storage
        cy.window().then((win) => {
            win.localStorage.clear()
        })

        cy.intercept('POST', '**/auth/register', (req) => {
            const body = req.body as string
            expect(body).to.include(`email=${encodeURIComponent(instructor.email)}`)
            req.reply({
                statusCode: 200,
                body: {
                    access_token: 'register-token',
                    token_type: 'bearer',
                    instructor_id: instructorId,
                },
            })
        }).as('registerInstructor')

        cy.intercept('POST', '**/auth/login', (req) => {
            const body = req.body as string
            expect(body).to.include(`username=${encodeURIComponent(instructor.email)}`)
            req.reply({
                statusCode: 200,
                body: {
                    access_token: 'login-token',
                    token_type: 'bearer',
                    instructor_id: instructorId,
                },
            })
        }).as('loginInstructor')

        cy.intercept('GET', `**/instructors/${instructorId}`, {
            statusCode: 200,
            body: {
                id: instructor.id,
                name: instructor.name,
                title: instructor.title,
                university: instructor.university,
                email: instructor.email,
                created_at: '2024-05-01T12:00:00.000Z',
            },
        }).as('getInstructorProfile')

        cy.visit('http://sdmay26-37.ece.iastate.edu/register')

        cy.get('input#name').type(instructor.name)
        cy.get('input#title').type(instructor.title)
        cy.get('input#university').type(instructor.university)
        cy.get('input#email').type(instructor.email)
        cy.get('input#password').type(instructor.password, { log: false })
        cy.get('input#confirmPassword').type(instructor.password, { log: false })

        cy.contains('button', 'Create Account').click()

        cy.wait('@registerInstructor')
        cy.url().should('include', '/login')

        cy.get('input#email').clear().type(instructor.email)
        cy.get('input#password').clear().type(instructor.password, { log: false })
        cy.contains('button', 'Sign in').click()

        cy.wait('@loginInstructor')
        cy.url().should('include', `/instructors/${instructorId}/profile`)

        cy.wait('@getInstructorProfile')
        cy.contains('h1', instructor.name).should('be.visible')
    })
})