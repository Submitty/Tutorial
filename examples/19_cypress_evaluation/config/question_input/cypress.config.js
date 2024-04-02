const { defineConfig } = require('cypress');

module.exports = defineConfig({
  reporter: 'mochawesome',
  html: false,
  json: true,
  chromeWebSecurity: false,
  screenshotOnRunFailure: false,
  video: false,
  e2e: {
    // We've imported your old npm i -g npm-run-all plugins here.
    // You may want to clean this up later by importing these.
    setupNodeEvents(on, config) {},
  },
});
