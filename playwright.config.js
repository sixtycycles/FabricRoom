const { defineConfig } = require('@playwright/test');

const PYTHON_BIN = process.env.PYTHON_BIN || '/Users/rod/PycharmProjects/FabricRoom/venv/bin/python';

module.exports = defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: {
    timeout: 10_000,
  },
  fullyParallel: false,
  retries: 0,
  reporter: 'list',
  use: {
    baseURL: 'http://127.0.0.1:8000',
    trace: 'retain-on-failure',
  },
  globalSetup: require.resolve('./e2e/global-setup.js'),
  webServer: {
    command: `DEBUG=TRUE ${PYTHON_BIN} manage.py runserver 127.0.0.1:8000 --noreload`,
    url: 'http://127.0.0.1:8000/accounts/login/',
    reuseExistingServer: true,
    timeout: 120_000,
  },
});
