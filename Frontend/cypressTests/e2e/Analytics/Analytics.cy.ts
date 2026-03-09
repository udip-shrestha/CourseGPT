/// <reference types="cypress" />

describe('Analytics Page', () => {
    const courseId = 'course-analytics-test-001';
    const course = {
        id: courseId,
        name: 'Intro to Machine Learning',
        instructor_id: 'instructor-1',
    };

    const overviewResponse = {
        activeUsers: 45,
        totalEnrolled: 80,
        totalQueries: 1234,
        engagementRate: 56,
    };

    const usageTrendResponse = [
        { date: '2024-03-01', queries: 120, uniqueUsers: 25 },
        { date: '2024-03-02', queries: 145, uniqueUsers: 28 },
        { date: '2024-03-03', queries: 98, uniqueUsers: 22 },
    ];

    const topQuestionsResponse = [
        { queryText: 'What is gradient descent?', count: 42 },
        { queryText: 'How does backpropagation work?', count: 28 },
    ];

    const topKeywordsResponse = [
        { keyword: 'neural network', count: 65 },
        { keyword: 'optimization', count: 48 },
    ];

    beforeEach(() => {
        cy.intercept('GET', `**/courses/${courseId}`, {
            statusCode: 200,
            body: course,
        }).as('getCourse');

        cy.intercept('GET', `**/courses/${courseId}/analytics/overview*`, {
            statusCode: 200,
            body: overviewResponse,
        }).as('getOverview');

        cy.intercept('GET', `**/courses/${courseId}/analytics/usage-trend*`, {
            statusCode: 200,
            body: usageTrendResponse,
        }).as('getUsageTrend');

        cy.intercept('GET', `**/courses/${courseId}/analytics/top-questions*`, {
            statusCode: 200,
            body: topQuestionsResponse,
        }).as('getTopQuestions');

        cy.intercept('GET', `**/courses/${courseId}/analytics/top-keywords*`, {
            statusCode: 200,
            body: topKeywordsResponse,
        }).as('getTopKeywords');

        cy.intercept('GET', `**/instructors/*/analytics/query-distribution*`, {
            statusCode: 404,
        }).as('getQueryDistribution');
    });

    it('should display the analytics dashboard with all main sections', () => {
        cy.visit(`/courses/${courseId}/analytics`);

        cy.wait('@getCourse');
        cy.wait('@getOverview');

        // Page header
        cy.contains('h1', 'Analytics Dashboard').should('be.visible');
        cy.contains(course.name).should('be.visible');

        // Platform Engagement stat cards
        cy.contains('Platform Engagement').should('be.visible');
        cy.contains('Active Users').should('be.visible');
        cy.contains('Chatbot Queries').should('be.visible');
        cy.contains('Avg. Satisfaction').should('be.visible');
        cy.contains('Engagement Rate').should('be.visible');

        // Key sections
        cy.contains('Frequently Asked Questions').should('be.visible');
        cy.contains('Top Keywords').should('be.visible');
        cy.contains('Chatbot Usage Trend').should('be.visible');
        cy.contains('Chatbot Usage by Course').should('be.visible');
        cy.contains('Query Distribution').should('be.visible');
        cy.contains('Course Engagement Details').should('be.visible');
    });

    it('should display overview metrics and analytics data after loading', () => {
        cy.visit(`/courses/${courseId}/analytics`);

        cy.wait('@getCourse');
        cy.wait('@getOverview');
        cy.wait('@getTopQuestions');
        cy.wait('@getTopKeywords');

        // Stats should show real data (not loading placeholder)
        cy.contains(overviewResponse.activeUsers.toString()).should('be.visible');
        cy.contains(overviewResponse.totalQueries.toLocaleString()).should('be.visible');

        // FAQ items from API
        cy.contains(topQuestionsResponse[0].queryText).should('be.visible');
        cy.contains(topKeywordsResponse[0].keyword).should('be.visible');
    });

    it('should allow changing the time range via the selector', () => {
        cy.visit(`/courses/${courseId}/analytics`);

        cy.wait('@getCourse');

        // Open time range selector
        cy.get('[role="combobox"]').filter(':visible').first().click();

        // Select "Last 30 days"
        cy.contains('[role="option"]', 'Last 30 days').click();

        // API should be called with new time range (days=30 for Last 30 days)
        cy.wait('@getOverview');
        cy.get<Array<{ request: { url: string } }>>('@getOverview.all').then((interceptions) => {
            const lastCall = interceptions[interceptions.length - 1];
            expect(lastCall.request.url).to.include('days=30');
        });
    });
});
