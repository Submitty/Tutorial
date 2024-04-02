describe('template spec', () => {
    it('passes', () => {
      cy.visit('http://localhost:8080');
      cy.get('.btn').should('contain', '0');
      cy.get('.btn').click();
      cy.get('.btn').should('contain', '1');
      cy.get('.btn').click();
      cy.get('.btn').should('contain', '2');
      cy.get('.btn').click();
      cy.get('.btn').should('contain', '3');
    });
  });
  