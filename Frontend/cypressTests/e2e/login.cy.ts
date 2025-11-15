/// <reference types="cypress" />

describe('Homepage', () => {
    // Test case 1: Display the homepage
    it('should display the homepage', () => {
        cy.visit('http://sdmay26-37.ece.iastate.edu/')
        cy.get('header').should('exist')
        cy.get('main').should('exist')
        cy.get('header').find('h1').first().should('have.text', 'CourseGPT')
    })
})


describe('Login Page', () => {
    // Test case 2: Display the login page
    it('should display the login page', () => {
        // Visit the login page
        cy.visit('http://sdmay26-37.ece.iastate.edu/login')
        cy.contains('h4', 'Login').should('be.visible')
        cy.get('input#email').should('exist')
        cy.get('input#password').should('exist')
    })

    describe('Register Page', () => {
        // Test case 3: Display the register page
        it('should display the register page', () => {
            cy.visit('http://sdmay26-37.ece.iastate.edu/register')
            cy.contains('h4', 'Register as Instructor').should('be.visible')
            cy.get('input#name').should('exist')
            cy.get('input#email').should('exist')
            cy.contains('button', 'Create Account').should('exist')
        })
    })
})