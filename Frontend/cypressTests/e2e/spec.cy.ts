/// <reference types="cypress" />

// Test the homepage

describe('Homepage', () => {
    it('should display the homepage', () => {
        cy.visit('http://localhost:5173')
        cy.get('header').should('exist')
        cy.get('main').should('exist')
        cy.get('header').find('h1').first().should('have.text', 'CourseGPT')
    })
})

// Test the login page
describe('Login Page', () => {
    it('should display the login page', () => {
        cy.visit('http://localhost:5173/login')
    //     cy.addListener('email', 'password').type('test@example.com', 'password')
    })
})