/// <reference types="cypress" />

// Test the homepage
describe('Homepage', () => {
    // Test case 1: Display the homepage
    it('should display the homepage', () => {
        // Visit the homepage
        cy.visit('http://localhost:5173')
        // Check if the header exists
        cy.get('header').should('exist')
        // Check if the main content exists
        cy.get('main').should('exist')
        // Check if the header contains the title 'CourseGPT'
        cy.get('header').find('h1').first().should('have.text', 'CourseGPT')
    })
})

// Test the login page
describe('Login Page', () => {
    // Test case 1: Display the login page
    it('should display the login page', () => {
        // Visit the login page
        cy.visit('http://localhost:5173/login')
        // Check if the login page exists
        cy.get('login').should('exist')
        // Check if the login page contains the title 'Login'
        cy.get('login').find('h1').first().should('have.text', 'Login')
        // Check if the login page contains the email input
        cy.get('login').find('input[type="email"]').should('exist')
        // Check if the login page contains the password input
    //     cy.addListener('email', 'password').type('test@example.com', 'password')
    })
})