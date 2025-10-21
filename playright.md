Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
IntegrationsContinuous Integration
Continuous Integration
Introduction
Playwright tests can be executed in CI environments. We have created sample configurations for common CI providers.

3 steps to get your tests running on CI:

Ensure CI agent can run browsers: Use our Docker image in Linux agents or install your dependencies using the CLI.

Install Playwright:

# Install NPM packages
npm ci

# Install Playwright browsers and dependencies
npx playwright install --with-deps

Run your tests:

npx playwright test

Workers
We recommend setting workers to "1" in CI environments to prioritize stability and reproducibility. Running tests sequentially ensures each test gets the full system resources, avoiding potential conflicts. However, if you have a powerful self-hosted CI system, you may enable parallel tests. For wider parallelization, consider sharding - distributing tests across multiple CI jobs.

playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  // Opt out of parallel tests on CI.
  workers: process.env.CI ? 1 : undefined,
});

CI configurations
The Command line tools can be used to install all operating system dependencies in CI.

GitHub Actions
On push/pull_request
Tests will run on push or pull request on branches main/master. The workflow will install all dependencies, install Playwright and then run the tests. It will also create the HTML report.

.github/workflows/playwright.yml
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v5
    - uses: actions/setup-node@v5
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30

On push/pull_request (sharded)
GitHub Actions supports sharding tests between multiple jobs. Check out our sharding doc to learn more about sharding and to see a GitHub actions example of how to configure a job to run your tests on multiple machines as well as how to merge the HTML reports.

Via Containers
GitHub Actions support running jobs in a container by using the jobs.<job_id>.container option. This is useful to not pollute the host environment with dependencies and to have a consistent environment for e.g. screenshots/visual regression testing across different operating systems.

.github/workflows/playwright.yml
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  playwright:
    name: 'Playwright Tests'
    runs-on: ubuntu-latest
    container:
      image: mcr.microsoft.com/playwright:v1.56.1-noble
      options: --user 1001
    steps:
      - uses: actions/checkout@v5
      - uses: actions/setup-node@v5
        with:
          node-version: lts/*
      - name: Install dependencies
        run: npm ci
      - name: Run your tests
        run: npx playwright test

On deployment
This will start the tests after a GitHub Deployment went into the success state. Services like Vercel use this pattern so you can run your end-to-end tests on their deployed environment.

.github/workflows/playwright.yml
name: Playwright Tests
on:
  deployment_status:
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    if: github.event.deployment_status.state == 'success'
    steps:
    - uses: actions/checkout@v5
    - uses: actions/setup-node@v5
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
      env:
        PLAYWRIGHT_TEST_BASE_URL: ${{ github.event.deployment_status.target_url }}

Fail-Fast
Large test suites can take very long to execute. By executing a preliminary test run with the --only-changed flag, you can run test files that are likely to fail first. This will give you a faster feedback loop and slightly lower CI consumption while working on Pull Requests. To detect test files affected by your changeset, --only-changed analyses your suites' dependency graph. This is a heuristic and might miss tests, so it's important that you always run the full test suite after the preliminary test run.

.github/workflows/playwright.yml
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v5
      with:
        # Force a non-shallow checkout, so that we can reference $GITHUB_BASE_REF.
        # See https://github.com/actions/checkout for more details.
        fetch-depth: 0
    - uses: actions/setup-node@v5
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run changed Playwright tests
      run: npx playwright test --only-changed=$GITHUB_BASE_REF
      if: github.event_name == 'pull_request'
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30

Docker
We have a pre-built Docker image which can either be used directly or as a reference to update your existing Docker definitions. Make sure to follow the Recommended Docker Configuration to ensure the best performance.

Azure Pipelines
For Windows or macOS agents, no additional configuration is required, just install Playwright and run your tests.

For Linux agents, you can use our Docker container with Azure Pipelines support running containerized jobs. Alternatively, you can use Command line tools to install all necessary dependencies.

For running the Playwright tests use this pipeline task:

trigger:
- main

pool:
  vmImage: ubuntu-latest

steps:
- task: UseNode@1
  inputs:
    version: '22'
  displayName: 'Install Node.js'
- script: npm ci
  displayName: 'npm ci'
- script: npx playwright install --with-deps
  displayName: 'Install Playwright browsers'
- script: npx playwright test
  displayName: 'Run Playwright tests'
  env:
    CI: 'true'

Uploading playwright-report folder with Azure Pipelines
This will make the pipeline run fail if any of the playwright tests fails. If you also want to integrate the test results with Azure DevOps, use the task PublishTestResults task like so:

trigger:
- main

pool:
  vmImage: ubuntu-latest

steps:
- task: UseNode@1
  inputs:
    version: '22'
  displayName: 'Install Node.js'

- script: npm ci
  displayName: 'npm ci'
- script: npx playwright install --with-deps
  displayName: 'Install Playwright browsers'
- script: npx playwright test
  displayName: 'Run Playwright tests'
  env:
    CI: 'true'
- task: PublishTestResults@2
  displayName: 'Publish test results'
  inputs:
    searchFolder: 'test-results'
    testResultsFormat: 'JUnit'
    testResultsFiles: 'e2e-junit-results.xml'
    mergeTestResults: true
    failTaskOnFailedTests: true
    testRunTitle: 'My End-To-End Tests'
  condition: succeededOrFailed()
- task: PublishPipelineArtifact@1
  inputs:
    targetPath: playwright-report
    artifact: playwright-report
    publishLocation: 'pipeline'
  condition: succeededOrFailed()


Note: The JUnit reporter needs to be configured accordingly via

import { defineConfig } from '@playwright/test';

export default defineConfig({
  reporter: [['junit', { outputFile: 'test-results/e2e-junit-results.xml' }]],
});

in playwright.config.ts.

Azure Pipelines (sharded)
trigger:
- main

pool:
  vmImage: ubuntu-latest

strategy:
  matrix:
    chromium-1:
      project: chromium
      shard: 1/3
    chromium-2:
      project: chromium
      shard: 2/3
    chromium-3:
      project: chromium
      shard: 3/3
    firefox-1:
      project: firefox
      shard: 1/3
    firefox-2:
      project: firefox
      shard: 2/3
    firefox-3:
      project: firefox
      shard: 3/3
    webkit-1:
      project: webkit
      shard: 1/3
    webkit-2:
      project: webkit
      shard: 2/3
    webkit-3:
      project: webkit
      shard: 3/3
steps:
- task: UseNode@1
  inputs:
    version: '22'
  displayName: 'Install Node.js'

- script: npm ci
  displayName: 'npm ci'
- script: npx playwright install --with-deps
  displayName: 'Install Playwright browsers'
- script: npx playwright test --project=$(project) --shard=$(shard)
  displayName: 'Run Playwright tests'
  env:
    CI: 'true'

Azure Pipelines (containerized)
trigger:
- main

pool:
  vmImage: ubuntu-latest
container: mcr.microsoft.com/playwright:v1.56.1-noble

steps:
- task: UseNode@1
  inputs:
    version: '22'
  displayName: 'Install Node.js'

- script: npm ci
  displayName: 'npm ci'
- script: npx playwright test
  displayName: 'Run Playwright tests'
  env:
    CI: 'true'

CircleCI
Running Playwright on CircleCI is very similar to running on GitHub Actions. In order to specify the pre-built Playwright Docker image, simply modify the agent definition with docker: in your config like so:

executors:
  pw-noble-development:
    docker:
      - image: mcr.microsoft.com/playwright:v1.56.1-noble

Note: When using the docker agent definition, you are specifying the resource class of where playwright runs to the 'medium' tier here. The default behavior of Playwright is to set the number of workers to the detected core count (2 in the case of the medium tier). Overriding the number of workers to greater than this number will cause unnecessary timeouts and failures.

Sharding in CircleCI
Sharding in CircleCI is indexed with 0 which means that you will need to override the default parallelism ENV VARS. The following example demonstrates how to run Playwright with a CircleCI Parallelism of 4 by adding 1 to the CIRCLE_NODE_INDEX to pass into the --shard cli arg.

  playwright-job-name:
    executor: pw-noble-development
    parallelism: 4
    steps:
      - run: SHARD="$((${CIRCLE_NODE_INDEX}+1))"; npx playwright test --shard=${SHARD}/${CIRCLE_NODE_TOTAL}


Jenkins
Jenkins supports Docker agents for pipelines. Use the Playwright Docker image to run tests on Jenkins.

pipeline {
   agent { docker { image 'mcr.microsoft.com/playwright:v1.56.1-noble' } }
   stages {
      stage('e2e-tests') {
         steps {
            sh 'npm ci'
            sh 'npx playwright test'
         }
      }
   }
}

Bitbucket Pipelines
Bitbucket Pipelines can use public Docker images as build environments. To run Playwright tests on Bitbucket, use our public Docker image (see Dockerfile).

image: mcr.microsoft.com/playwright:v1.56.1-noble

GitLab CI
To run Playwright tests on GitLab, use our public Docker image (see Dockerfile).

stages:
  - test

tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.56.1-noble
  script:
  ...

Sharding
GitLab CI supports sharding tests between multiple jobs using the parallel keyword. The test job will be split into multiple smaller jobs that run in parallel. Parallel jobs are named sequentially from job_name 1/N to job_name N/N.

stages:
  - test

tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.56.1-noble
  parallel: 7
  script:
    - npm ci
    - npx playwright test --shard=$CI_NODE_INDEX/$CI_NODE_TOTAL

GitLab CI also supports sharding tests between multiple jobs using the parallel:matrix option. The test job will run multiple times in parallel in a single pipeline, but with different variable values for each instance of the job. In the example below, we have 2 PROJECT values and 10 SHARD values, resulting in a total of 20 jobs to be run.

stages:
  - test

tests:
  stage: test
  image: mcr.microsoft.com/playwright:v1.56.1-noble
  parallel:
    matrix:
      - PROJECT: ['chromium', 'webkit']
        SHARD: ['1/10', '2/10', '3/10', '4/10', '5/10', '6/10', '7/10', '8/10', '9/10', '10/10']
  script:
    - npm ci
    - npx playwright test --project=$PROJECT --shard=$SHARD

Google Cloud Build
To run Playwright tests on Google Cloud Build, use our public Docker image (see Dockerfile).

steps:
- name: mcr.microsoft.com/playwright:v1.56.1-noble
  script: 
  ...
  env:
  - 'CI=true'

Drone
To run Playwright tests on Drone, use our public Docker image (see Dockerfile).

kind: pipeline
name: default
type: docker

steps:
  - name: test
    image: mcr.microsoft.com/playwright:v1.56.1-noble
    commands:
      - npx playwright test

Caching browsers
Caching browser binaries is not recommended, since the amount of time it takes to restore the cache is comparable to the time it takes to download the binaries. Especially under Linux, operating system dependencies need to be installed, which are not cacheable.

If you still want to cache the browser binaries between CI runs, cache these directories in your CI configuration, against a hash of the Playwright version.

Debugging browser launches
Playwright supports the DEBUG environment variable to output debug logs during execution. Setting it to pw:browser is helpful while debugging Error: Failed to launch browser errors.

DEBUG=pw:browser npx playwright test

Running headed
By default, Playwright launches browsers in headless mode. See in our Running tests guide how to run tests in headed mode.

On Linux agents, headed execution requires Xvfb to be installed. Our Docker image and GitHub Action have Xvfb pre-installed. To run browsers in headed mode with Xvfb, add xvfb-run before the actual command.

xvfb-run npx playwright test

Previous
Docker
Next
Selenium Grid (experimental)
Introduction
Workers
CI configurations
GitHub Actions
Docker
Azure Pipelines
CircleCI
Jenkins
Bitbucket Pipelines
GitLab CI
Google Cloud Build
Drone
Caching browsers
Debugging browser launches
Running headed
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft


Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community


Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedInstallation
Installation
Introduction
Playwright Test is an end-to-end test framework for modern web apps. It bundles test runner, assertions, isolation, parallelization and rich tooling. Playwright supports Chromium, WebKit and Firefox on Windows, Linux and macOS, locally or in CI, headless or headed, with native mobile emulation for Chrome (Android) and Mobile Safari.

You will learn

How to install Playwright
What's installed
How to run the example test
How to open the HTML test report
Installing Playwright
Get started by installing Playwright using one of the following methods.

Using npm, yarn or pnpm
The command below either initializes a new project or adds Playwright to an existing one.

npm
yarn
pnpm
npm init playwright@latest

When prompted, choose / confirm:

TypeScript or JavaScript (default: TypeScript)
Tests folder name (default: tests, or e2e if tests already exists)
Add a GitHub Actions workflow (recommended for CI)
Install Playwright browsers (default: yes)
You can re-run the command later; it does not overwrite existing tests.

Using the VS Code Extension
You can also create and run tests with the VS Code Extension.

What's Installed
Playwright downloads required browser binaries and creates the scaffold below.

playwright.config.ts         # Test configuration
package.json
package-lock.json            # Or yarn.lock / pnpm-lock.yaml
tests/
  example.spec.ts            # Minimal example test
tests-examples/
  demo-todo-app.spec.ts      # Richer example tests

The playwright.config centralizes configuration: target browsers, timeouts, retries, projects, reporters and more. In existing projects dependencies are added to your current package.json.

tests/ contains a minimal starter test. tests-examples/ provides richer samples (e.g. a todo app) to explore patterns.

Running the Example Test
By default tests run headless in parallel across Chromium, Firefox and WebKit (configurable in playwright.config). Output and aggregated results display in the terminal.

npm
yarn
pnpm
npx playwright test

tests running in command line

Tips:

See the browser window: add --headed.
Run a single project/browser: --project=chromium.
Run one file: npx playwright test tests/example.spec.ts.
Open testing UI: --ui.
See Running Tests for details on filtering, headed mode, sharding and retries.

HTML Test Reports
After a test run, the HTML Reporter provides a dashboard filterable by the browser, passed, failed, skipped, flaky and more. Click a test to inspect errors, attachments and steps. It auto-opens only when failures occur; open manually with the command below.

npm
yarn
pnpm
npx playwright show-report

HTML Report

Running the Example Test in UI Mode
Run tests with UI Mode for watch mode, live step view, time travel debugging and more.

npm
yarn
pnpm
npx playwright test --ui

UI Mode

See the detailed guide on UI Mode for watch filters, step details and trace integration.

Updating Playwright
Update Playwright and download new browser binaries and their dependencies:

npm
yarn
pnpm
npm install -D @playwright/test@latest
npx playwright install --with-deps

Check your installed version:

npm
yarn
pnpm
npx playwright --version

System requirements
Node.js: latest 20.x, 22.x or 24.x.
Windows 11+, Windows Server 2019+ or Windows Subsystem for Linux (WSL).
macOS 14 (Ventura) or later.
Debian 12 / 13, Ubuntu 22.04 / 24.04 (x86-64 or arm64).
What's next
Write tests using web-first assertions, fixtures and locators
Run single or multiple tests; headed mode
Generate tests with Codegen
View a trace of your tests
Next
Writing tests
Introduction
Installing Playwright
Using npm, yarn or pnpm
Using the VS Code Extension
What's Installed
Running the Example Test
HTML Test Reports
Running the Example Test in UI Mode
Updating Playwright
System requirements
What's next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft


Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedWriting tests
Writing tests
Introduction
Playwright tests are simple: they perform actions and assert the state against expectations.

Playwright automatically waits for actionability checks to pass before performing each action. You don't need to add manual waits or deal with race conditions. Playwright assertions are designed to describe expectations that will eventually be met, eliminating flaky timeouts and racy checks.

You will learn

How to write the first test
How to perform actions
How to use assertions
How tests run in isolation
How to use test hooks
First test
Take a look at the following example to see how to write a test.

tests/example.spec.ts
import { test, expect } from '@playwright/test';

test('has title', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Expect a title "to contain" a substring.
  await expect(page).toHaveTitle(/Playwright/);
});

test('get started link', async ({ page }) => {
  await page.goto('https://playwright.dev/');

  // Click the get started link.
  await page.getByRole('link', { name: 'Get started' }).click();

  // Expects page to have a heading with the name of Installation.
  await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
});

note
Add // @ts-check at the start of each test file when using JavaScript in VS Code to get automatic type checking.

Actions
Navigation
Most tests start by navigating to a URL. After that, the test interacts with page elements.

await page.goto('https://playwright.dev/');

Playwright waits for the page to reach the load state before continuing. Learn more about page.goto() options.

Interactions
Performing actions starts with locating elements. Playwright uses Locators API for that. Locators represent a way to find element(s) on the page at any moment. Learn more about the different types of locators available.

Playwright waits for the element to be actionable before performing the action, so you don't need to wait for it to become available.

// Create a locator.
const getStarted = page.getByRole('link', { name: 'Get started' });

// Click it.
await getStarted.click();

In most cases, it'll be written in one line:

await page.getByRole('link', { name: 'Get started' }).click();

Basic actions
Here are the most popular Playwright actions. For the complete list, check the Locator API section.

Action	Description
locator.check()	Check the input checkbox
locator.click()	Click the element
locator.uncheck()	Uncheck the input checkbox
locator.hover()	Hover mouse over the element
locator.fill()	Fill the form field, input text
locator.focus()	Focus the element
locator.press()	Press single key
locator.setInputFiles()	Pick files to upload
locator.selectOption()	Select option in the drop down
Assertions
Playwright includes test assertions in the form of expect function. To make an assertion, call expect(value) and choose a matcher that reflects the expectation.

Playwright includes async matchers that wait until the expected condition is met. Using these matchers makes tests non-flaky and resilient. For example, this code waits until the page gets the title containing "Playwright":

await expect(page).toHaveTitle(/Playwright/);

Here are the most popular async assertions. For the complete list, see assertions guide:

Assertion	Description
expect(locator).toBeChecked()	Checkbox is checked
expect(locator).toBeEnabled()	Control is enabled
expect(locator).toBeVisible()	Element is visible
expect(locator).toContainText()	Element contains text
expect(locator).toHaveAttribute()	Element has attribute
expect(locator).toHaveCount()	List of elements has given length
expect(locator).toHaveText()	Element matches text
expect(locator).toHaveValue()	Input element has value
expect(page).toHaveTitle()	Page has title
expect(page).toHaveURL()	Page has URL
Playwright also includes generic matchers like toEqual, toContain, toBeTruthy that can be used to assert any conditions. These assertions do not use the await keyword as they perform immediate synchronous checks on already available values.

expect(success).toBeTruthy();

Test Isolation
Playwright Test is based on the concept of test fixtures such as the built in page fixture, which is passed into your test. Pages are isolated between tests due to the Browser Context, which is equivalent to a brand new browser profile. Every test gets a fresh environment, even when multiple tests run in a single browser.

tests/example.spec.ts
import { test } from '@playwright/test';

test('example test', async ({ page }) => {
  // "page" belongs to an isolated BrowserContext, created for this specific test.
});

test('another test', async ({ page }) => {
  // "page" in this second test is completely isolated from the first test.
});

Using Test Hooks
You can use various test hooks such as test.describe to declare a group of tests and test.beforeEach and test.afterEach which are executed before/after each test. Other hooks include the test.beforeAll and test.afterAll which are executed once per worker before/after all tests.

tests/example.spec.ts
import { test, expect } from '@playwright/test';

test.describe('navigation', () => {
  test.beforeEach(async ({ page }) => {
    // Go to the starting url before each test.
    await page.goto('https://playwright.dev/');
  });

  test('main navigation', async ({ page }) => {
    // Assertions use the expect API.
    await expect(page).toHaveURL('https://playwright.dev/');
  });
});

What's Next
Run single test, multiple tests, headed mode
Generate tests with Codegen
See a trace of your tests
Explore UI Mode
Run tests on CI with GitHub Actions
Previous
Installation
Next
Generating tests
Introduction
First test
Actions
Navigation
Interactions
Basic actions
Assertions
Test Isolation
Using Test Hooks
What's Next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft


Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedGenerating tests
Generating tests
Introduction
Playwright can generate tests automatically, providing a quick way to get started with testing. Codegen opens a browser window for interaction and the Playwright Inspector for recording, copying, and managing your generated tests.

You will learn

How to record a test
How to generate locators
Running Codegen
Use the codegen command to run the test generator followed by the URL of the website you want to generate tests for. The URL is optional and can be added directly in the browser window if omitted.

npx playwright codegen demo.playwright.dev/todomvc

Recording a test
Run codegen and perform actions in the browser. Playwright generates code for your interactions automatically. Codegen analyzes the rendered page and recommends the best locator, prioritizing role, text, and test id locators. When multiple elements match a locator, the generator improves it to uniquely identify the target element, reducing test failures and flakiness.

With the test generator you can record:

Actions like click or fill by interacting with the page
Assertions by clicking a toolbar icon, then clicking a page element to assert against. You can choose:
'assert visibility' to assert that an element is visible
'assert text' to assert that an element contains specific text
'assert value' to assert that an element has a specific value
Recording a test

When you finish interacting with the page, press the 'record' button to stop recording and use the 'copy' button to copy the generated code to your editor.

Use the 'clear' button to clear the code and start recording again. Once finished, close the Playwright Inspector window or stop the terminal command.

To learn more about generating tests, check out our detailed guide on Codegen.

Generating locators
You can generate locators with the test generator.

Press the 'Record' button to stop recording and the 'Pick Locator' button will appear
Click the 'Pick Locator' button and hover over elements in the browser window to see the locator highlighted underneath each element
Click the element you want to locate and the code for that locator will appear in the locator playground next to the Pick Locator button
Edit the locator in the locator playground to fine-tune it and see the matching element highlighted in the browser window
Use the copy button to copy the locator and paste it into your code
picking a locator

Emulation
You can generate tests using emulation for specific viewports, devices, color schemes, geolocation, language, or timezone. The test generator can also preserve authenticated state. Check out the Test Generator guide to learn more.

What's Next
See a trace of your tests
Previous
Writing tests
Next
Running and debugging tests
Introduction
Running Codegen
Recording a test
Generating locators
Emulation
What's Next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft

Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedRunning and debugging tests
Running and debugging tests
Introduction
With Playwright you can run a single test, a set of tests, or all tests. Tests can be run on one browser or multiple browsers using the --project flag. Tests run in parallel by default and in headless mode, meaning no browser window opens while running the tests and results appear in the terminal. You can run tests in headed mode using the --headed CLI argument, or run your tests in UI mode using the --ui flag to see a full trace of your tests.

You will learn

How to run tests from the command line
How to debug tests
How to open the HTML test reporter
Running tests
Command line
You can run your tests with the playwright test command. This runs your tests on all browsers as configured in the playwright.config file, and results appear in the terminal. Tests run in headless mode by default, meaning no browser window opens while running the tests.

npx playwright test

tests running in command line

Run tests in UI mode
We highly recommend running your tests with UI Mode for a better developer experience where you can easily walk through each step of the test and visually see what was happening before, during and after each step. UI mode also comes with many other features such as the locator picker, watch mode and more.

npx playwright test --ui

UI Mode

Check out our detailed guide on UI Mode to learn more about its features.

Run tests in headed mode
To run your tests in headed mode, use the --headed flag. This gives you the ability to visually see how Playwright interacts with the website.

npx playwright test --headed

Run tests on different browsers
To specify which browser you would like to run your tests on, use the --project flag followed by the browser name.

npx playwright test --project webkit

To specify multiple browsers to run your tests on, use the --project flag multiple times followed by each browser name.

npx playwright test --project webkit --project firefox

Run specific tests
To run a single test file, pass in the test file name that you want to run.

npx playwright test landing-page.spec.ts

To run a set of test files from different directories, pass in the directory names that you want to run the tests in.

npx playwright test tests/todo-page/ tests/landing-page/

To run files that have landing or login in the file name, simply pass in these keywords to the CLI.

npx playwright test landing login

To run a test with a specific title, use the -g flag followed by the title of the test.

npx playwright test -g "add a todo item"

Run last failed tests
To run only the tests that failed in the last test run, first run your tests and then run them again with the --last-failed flag.

npx playwright test --last-failed

Run tests in VS Code
Tests can be run right from VS Code using the VS Code extension. Once installed you can simply click the green triangle next to the test you want to run or run all tests from the testing sidebar. Check out our Getting Started with VS Code guide for more details.

install playwright extension

Debugging tests
Since Playwright runs in Node.js, you can debug it with your debugger of choice, e.g. using console.log, inside your IDE, or directly in VS Code with the VS Code Extension. Playwright comes with UI Mode, where you can easily walk through each step of the test, see logs, errors, network requests, inspect the DOM snapshot, and more. You can also use the Playwright Inspector, which allows you to step through Playwright API calls, see their debug logs, and explore locators.

Debug tests in UI mode
We highly recommend debugging your tests with UI Mode for a better developer experience where you can easily walk through each step of the test and visually see what was happening before, during, and after each step. UI mode also comes with many other features such as the locator picker, watch mode, and more.

npx playwright test --ui

showing errors in ui mode

While debugging you can use the Pick Locator button to select an element on the page and see the locator that Playwright would use to find that element. You can also edit the locator in the locator playground and see it highlighting live in the browser window. Use the Copy Locator button to copy the locator to your clipboard and then paste it into your test.

pick locator in ui mode

Check out our detailed guide on UI Mode to learn more about its features.

Debug tests with the Playwright Inspector
To debug all tests, run the Playwright test command followed by the --debug flag.

npx playwright test --debug

Debugging Tests with the Playwright inspector

This command opens a browser window as well as the Playwright Inspector. You can use the step over button at the top of the inspector to step through your test. Or, press the play button to run your test from start to finish. Once the test finishes, the browser window closes.

To debug one test file, run the Playwright test command with the test file name that you want to debug followed by the --debug flag.

npx playwright test example.spec.ts --debug

To debug a specific test from the line number where the test(.. is defined, add a colon followed by the line number at the end of the test file name, followed by the --debug flag.

npx playwright test example.spec.ts:10 --debug

While debugging you can use the Pick Locator button to select an element on the page and see the locator that Playwright would use to find that element. You can also edit the locator and see it highlighting live in the browser window. Use the Copy Locator button to copy the locator to your clipboard and then paste it into your test.

Locator picker in the Playwright Inspector

Check out our debugging guide to learn more about debugging with the VS Code debugger, UI Mode, and the Playwright Inspector as well as debugging with Browser Developer tools.

Test reports
The HTML Reporter shows you a full report of your tests allowing you to filter the report by browsers, passed tests, failed tests, skipped tests, and flaky tests. By default, the HTML report opens automatically if some tests failed, otherwise you can open it with the following command.

npx playwright show-report

HTML Report

You can filter and search for tests as well as click on each test to see the test errors and explore each step of the test.

HTML Reporter detail view

What's next
Generate tests with Codegen
See a trace of your tests
Explore all the features of UI Mode
Run your tests on CI with GitHub Actions
Previous
Generating tests
Next
Trace viewer
Introduction
Running tests
Command line
Run tests in UI mode
Run tests in headed mode
Run tests on different browsers
Run specific tests
Run last failed tests
Run tests in VS Code
Debugging tests
Debug tests in UI mode
Debug tests with the Playwright Inspector
Test reports
What's next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft

Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community


Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedTrace viewer
Trace viewer
Introduction
Playwright Trace Viewer is a GUI tool that lets you explore recorded Playwright traces of your tests, meaning you can go back and forward through each action of your test and visually see what was happening during each action.

You will learn

How to record a trace
How to open the HTML report
How to open and view the trace

Recording a Trace
By default the playwright.config file contains the configuration needed to create a trace.zip file for each test. Traces are setup to run on-first-retry, meaning they run on the first retry of a failed test. Also retries are set to 2 when running on CI and 0 locally. This means the traces are recorded on the first retry of a failed test but not on the first run and not on the second retry.

playwright.config.ts
import { defineConfig } from '@playwright/test';
export default defineConfig({
  retries: process.env.CI ? 2 : 0, // set to 2 when running on CI
  // ...
  use: {
    trace: 'on-first-retry', // record traces on first retry of each test
  },
});

To learn more about available options to record a trace check out our detailed guide on Trace Viewer.

Traces are normally run in a Continuous Integration (CI) environment, because locally you can use UI Mode for developing and debugging tests. However, if you want to run traces locally without using UI Mode, you can force tracing to be on with --trace on.

npx playwright test --trace on

Opening the HTML report
The HTML report shows you a report of all your tests that have been run and on which browsers as well as how long they took. Tests can be filtered by passed tests, failed, flaky, or skipped tests. You can also search for a particular test. Clicking on a test opens the detailed view where you can see more information on your tests such as the errors, the test steps, and the trace.

npx playwright show-report

Opening the trace
In the HTML report, click on the trace icon next to the test file name to directly open the trace for the required test.

playwright html report

You can also click to open the detailed view of the test and scroll down to the 'Traces' tab and open the trace by clicking on the trace screenshot.

playwright html report detailed view

To learn more about reporters, check out our detailed guide on reporters including the HTML Reporter.

Viewing the trace
View traces of your test by clicking through each action or hovering using the timeline and see the state of the page before and after the action. Inspect the log, source and network, errors, and console during each step of the test. The trace viewer creates a DOM snapshot so you can fully interact with it and open the browser DevTools to inspect the HTML, CSS, etc.

playwright trace viewer

To learn more about traces, check out our detailed guide on Trace Viewer.

What's next
Run tests on CI with GitHub Actions
Learn more about Trace Viewer
Previous
Running and debugging tests
Next
Setting up CI
Introduction
Recording a Trace
Opening the HTML report
Opening the trace
Viewing the trace
What's next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft

Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
Getting StartedSetting up CI
Setting up CI
Introduction
Playwright tests can be run on any CI provider. This guide covers one way of running tests on GitHub using GitHub Actions. If you would like to learn more, or how to configure other CI providers, check out our detailed doc on Continuous Integration.

You will learn
How to set up GitHub Actions
How to view test logs
How to view the HTML report
How to view the trace
How to publish report on the web
Setting up GitHub Actions
When installing Playwright using the VS Code extension or with npm init playwright@latest, you are given the option to add a GitHub Actions workflow. This creates a playwright.yml file inside a .github/workflows folder containing everything you need so that your tests run on each push and pull request into the main/master branch. Here's how that file looks:

.github/workflows/playwright.yml
name: Playwright Tests
on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]
jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v5
    - uses: actions/setup-node@v5
      with:
        node-version: lts/*
    - name: Install dependencies
      run: npm ci
    - name: Install Playwright Browsers
      run: npx playwright install --with-deps
    - name: Run Playwright tests
      run: npx playwright test
    - uses: actions/upload-artifact@v4
      if: ${{ !cancelled() }}
      with:
        name: playwright-report
        path: playwright-report/
        retention-days: 30

The workflow performs these steps:

Clone your repository
Install Node.js
Install NPM Dependencies
Install Playwright Browsers
Run Playwright tests
Upload HTML report to the GitHub UI
To learn more about this, see "Understanding GitHub Actions".

Create a Repo and Push to GitHub
Once you have your GitHub Actions workflow setup, then all you need to do is Create a repo on GitHub or push your code to an existing repository. Follow the instructions on GitHub and don't forget to initialize a git repository using the git init command so you can add, commit, and push your code.

Create a Repo and Push to GitHub
Opening the Workflows
Click on the Actions tab to see the workflows. Here you see if your tests have passed or failed.

opening the workflow

Viewing Test Logs
Clicking on the workflow run shows you all the actions that GitHub performed and clicking on Run Playwright tests shows the error messages, what was expected and what was received as well as the call log.

Viewing Test Logs

HTML Report
The HTML Report shows you a full report of your tests. You can filter the report by browsers, passed tests, failed tests, skipped tests, and flaky tests.

Downloading the HTML Report
In the Artifacts section, click on the playwright-report to download your report in the format of a zip file.

Downloading the HTML Report
Viewing the HTML Report
Locally opening the report does not work as expected as you need a web server for everything to work correctly. First, extract the zip, preferably in a folder that already has Playwright installed. Using the command line, change into the directory where the report is and use npx playwright show-report followed by the name of the extracted folder. This serves up the report and enables you to view it in your browser.

npx playwright show-report name-of-my-extracted-playwright-report

viewing the HTML report

To learn more about reports, check out our detailed guide on HTML Reporter

Viewing the Trace
Once you have served the report using npx playwright show-report, click on the trace icon next to the test's file name as seen in the image above. You can then view the trace of your tests and inspect each action to try to find out why the tests are failing.

playwright trace viewer

Publishing report on the web
Downloading the HTML report as a zip file is not very convenient. However, we can utilize Azure Storage's static websites hosting capabilities to easily and efficiently serve HTML reports on the Internet, requiring minimal configuration.

Create an Azure Storage account.

Enable Static website hosting for the storage account.

Create a Service Principal in Azure and grant it access to Azure Blob storage. Upon successful execution, the command will display the credentials which will be used in the next step.

az ad sp create-for-rbac --name "github-actions" --role "Storage Blob Data Contributor" --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP_NAME>/providers/Microsoft.Storage/storageAccounts/<STORAGE_ACCOUNT_NAME>


Use the credentials from the previous step to set up encrypted secrets in your GitHub repository. Go to your repository's settings, under GitHub Actions secrets, and add the following secrets:

AZCOPY_SPA_APPLICATION_ID
AZCOPY_SPA_CLIENT_SECRET
AZCOPY_TENANT_ID
For a detailed guide on how to authorize a service principal using a client secret, refer to this Microsoft documentation.

Add a step that uploads the HTML report to Azure Storage.

.github/workflows/playwright.yml
...
    - name: Upload HTML report to Azure
      shell: bash
      run: |
        REPORT_DIR='run-${{ github.run_id }}-${{ github.run_attempt }}'
        azcopy cp --recursive "./playwright-report/*" "https://<STORAGE_ACCOUNT_NAME>.blob.core.windows.net/\$web/$REPORT_DIR"
        echo "::notice title=HTML report url::https://<STORAGE_ACCOUNT_NAME>.z1.web.core.windows.net/$REPORT_DIR/index.html"
      env:
        AZCOPY_AUTO_LOGIN_TYPE: SPN
        AZCOPY_SPA_APPLICATION_ID: '${{ secrets.AZCOPY_SPA_APPLICATION_ID }}'
        AZCOPY_SPA_CLIENT_SECRET: '${{ secrets.AZCOPY_SPA_CLIENT_SECRET }}'
        AZCOPY_TENANT_ID: '${{ secrets.AZCOPY_TENANT_ID }}'


The contents of the $web storage container can be accessed from a browser by using the public URL of the website.

note
This step will not work for pull requests created from a forked repository because such workflow doesn't have access to the secrets.

Properly handling Secrets
Artifacts like trace files, HTML reports or even the console logs contain information about your test execution. They can contain sensitive data like user credentials for a test user, access tokens to a staging backend, testing source code, or sometimes even your application source code. Treat these files just as carefully as you treat that sensitive data. If you upload reports and traces as part of your CI workflow, make sure that you only upload them to trusted artifact stores, or that you encrypt the files before upload. The same is true for sharing artifacts with team members: Use a trusted file share or encrypt the files before sharing.

What's Next
Learn how to use Locators
Learn how to perform Actions
Learn how to write Assertions
Learn more about the Trace Viewer
Learn more ways of running tests on GitHub Actions
Learn more about running tests on other CI providers
Previous
Trace viewer
Next
Getting started - VS Code
Introduction
Setting up GitHub Actions
Create a Repo and Push to GitHub
Opening the Workflows
Viewing Test Logs
HTML Report
Downloading the HTML Report
Viewing the HTML Report
Viewing the Trace
Publishing report on the web
Properly handling Secrets
What's Next
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft

Skip to main content
Playwright logo
Playwright
Docs
API
Node.js
Community

Getting Started
Installation
Writing tests
Generating tests
Running and debugging tests
Trace viewer
Setting up CI
Getting started - VS Code
Release notes
Canary releases
Playwright Test
Agents
Annotations
Command line
Configuration
Configuration (use)
Emulation
Fixtures
Global setup and teardown
Parallelism
Parameterize tests
Projects
Reporters
Retries
Sharding
Timeouts
TypeScript
UI Mode
Web server
Guides
Library
Accessibility testing
Actions
Assertions
API testing
Authentication
Auto-waiting
Best Practices
Browsers
Chrome extensions
Clock
Components (experimental)
Debugging Tests
Dialogs
Downloads
Evaluating JavaScript
Events
Extensibility
Frames
Handles
Isolation
Locators
Mock APIs
Mock browser APIs
Navigations
Network
Other locators
Pages
Page object models
Screenshots
Snapshot testing
Test generator
Touch events (legacy)
Trace viewer
Videos
Visual comparisons
WebView2
Migration
Integrations
Docker
Continuous Integration
Selenium Grid (experimental)
Supported languages
GuidesBest Practices
Best Practices
Introduction
This guide should help you to make sure you are following our best practices and writing tests that are more resilient.

Testing philosophy
Test user-visible behavior
Automated tests should verify that the application code works for the end users, and avoid relying on implementation details such as things which users will not typically use, see, or even know about such as the name of a function, whether something is an array, or the CSS class of some element. The end user will see or interact with what is rendered on the page, so your test should typically only see/interact with the same rendered output.

Make tests as isolated as possible
Each test should be completely isolated from another test and should run independently with its own local storage, session storage, data, cookies etc. Test isolation improves reproducibility, makes debugging easier and prevents cascading test failures.

In order to avoid repetition for a particular part of your test you can use before and after hooks. Within your test file add a before hook to run a part of your test before each test such as going to a particular URL or logging in to a part of your app. This keeps your tests isolated as no test relies on another. However it is also ok to have a little duplication when tests are simple enough especially if it keeps your tests clearer and easier to read and maintain.

import { test } from '@playwright/test';

test.beforeEach(async ({ page }) => {
  // Runs before each test and signs in each page.
  await page.goto('https://github.com/login');
  await page.getByLabel('Username or email address').fill('username');
  await page.getByLabel('Password').fill('password');
  await page.getByRole('button', { name: 'Sign in' }).click();
});

test('first', async ({ page }) => {
  // page is signed in.
});

test('second', async ({ page }) => {
  // page is signed in.
});

You can also reuse the signed-in state in the tests with setup project. That way you can log in only once and then skip the log in step for all of the tests.

Avoid testing third-party dependencies
Only test what you control. Don't try to test links to external sites or third party servers that you do not control. Not only is it time consuming and can slow down your tests but also you cannot control the content of the page you are linking to, or if there are cookie banners or overlay pages or anything else that might cause your test to fail.

Instead, use the Playwright Network API and guarantee the response needed.

await page.route('**/api/fetch_data_third_party_dependency', route => route.fulfill({
  status: 200,
  body: testData,
}));
await page.goto('https://example.com');

Testing with a database
If working with a database then make sure you control the data. Test against a staging environment and make sure it doesn't change. For visual regression tests make sure the operating system and browser versions are the same.

Best Practices
Use locators
In order to write end to end tests we need to first find elements on the webpage. We can do this by using Playwright's built in locators. Locators come with auto waiting and retry-ability. Auto waiting means that Playwright performs a range of actionability checks on the elements, such as ensuring the element is visible and enabled before it performs the click. To make tests resilient, we recommend prioritizing user-facing attributes and explicit contracts.

// 👍
page.getByRole('button', { name: 'submit' });

Use chaining and filtering
Locators can be chained to narrow down the search to a particular part of the page.

const product = page.getByRole('listitem').filter({ hasText: 'Product 2' });

You can also filter locators by text or by another locator.

await page
    .getByRole('listitem')
    .filter({ hasText: 'Product 2' })
    .getByRole('button', { name: 'Add to cart' })
    .click();

Prefer user-facing attributes to XPath or CSS selectors
Your DOM can easily change so having your tests depend on your DOM structure can lead to failing tests. For example consider selecting this button by its CSS classes. Should the designer change something then the class might change, thus breaking your test.

// 👎
page.locator('button.buttonIcon.episode-actions-later');

Use locators that are resilient to changes in the DOM.

// 👍
page.getByRole('button', { name: 'submit' });

Generate locators
Playwright has a test generator that can generate tests and pick locators for you. It will look at your page and figure out the best locator, prioritizing role, text and test id locators. If the generator finds multiple elements matching the locator, it will improve the locator to make it resilient and uniquely identify the target element, so you don't have to worry about failing tests due to locators.

Use codegen to generate locators
To pick a locator run the codegen command followed by the URL that you would like to pick a locator from.

npm
yarn
pnpm
npx playwright codegen playwright.dev

This will open a new browser window as well as the Playwright inspector. To pick a locator first click on the 'Record' button to stop the recording. By default when you run the codegen command it will start a new recording. Once you stop the recording the 'Pick Locator' button will be available to click.

You can then hover over any element on your page in the browser window and see the locator highlighted below your cursor. Clicking on an element will add the locator into the Playwright inspector. You can either copy the locator and paste into your test file or continue to explore the locator by editing it in the Playwright Inspector, for example by modifying the text, and seeing the results in the browser window.

generating locators with codegen
Use the VS Code extension to generate locators
You can also use the VS Code Extension to generate locators as well as record a test. The VS Code extension also gives you a great developer experience when writing, running, and debugging tests.

generating locators in vs code with codegen
Use web first assertions
Assertions are a way to verify that the expected result and the actual result matched or not. By using web first assertions Playwright will wait until the expected condition is met. For example, when testing an alert message, a test would click a button that makes a message appear and check that the alert message is there. If the alert message takes half a second to appear, assertions such as toBeVisible() will wait and retry if needed.

// 👍
await expect(page.getByText('welcome')).toBeVisible();

// 👎
expect(await page.getByText('welcome').isVisible()).toBe(true);

Don't use manual assertions
Don't use manual assertions that are not awaiting the expect. In the code below the await is inside the expect rather than before it. When using assertions such as isVisible() the test won't wait a single second, it will just check the locator is there and return immediately.

// 👎
expect(await page.getByText('welcome').isVisible()).toBe(true);

Use web first assertions such as toBeVisible() instead.

// 👍
await expect(page.getByText('welcome')).toBeVisible();

Configure debugging
Local debugging
For local debugging we recommend you debug your tests live in VSCode. by installing the VS Code extension. You can run tests in debug mode by right clicking on the line next to the test you want to run which will open a browser window and pause at where the breakpoint is set.

debugging tests in vscode
You can live debug your test by clicking or editing the locators in your test in VS Code which will highlight this locator in the browser window as well as show you any other matching locators found on the page.

live debugging locators in vscode
You can also debug your tests with the Playwright inspector by running your tests with the --debug flag.

npm
yarn
pnpm
npx playwright test --debug

You can then step through your test, view actionability logs and edit the locator live and see it highlighted in the browser window. This will show you which locators match, how many of them there are.

debugging with the playwright inspector
To debug a specific test add the name of the test file and the line number of the test followed by the --debug flag.

npm
yarn
pnpm
npx playwright test example.spec.ts:9 --debug

Debugging on CI
For CI failures, use the Playwright trace viewer instead of videos and screenshots. The trace viewer gives you a full trace of your tests as a local Progressive Web App (PWA) that can easily be shared. With the trace viewer you can view the timeline, inspect DOM snapshots for each action using dev tools, view network requests and more.

playwrights trace viewer
Traces are configured in the Playwright config file and are set to run on CI on the first retry of a failed test. We don't recommend setting this to on so that traces are run on every test as it's very performance heavy. However you can run a trace locally when developing with the --trace flag.

npm
yarn
pnpm
npx playwright test --trace on

Once you run this command your traces will be recorded for each test and can be viewed directly from the HTML report.

npm
yarn
pnpm
npx playwright show-report

Playwrights HTML report
Traces can be opened by clicking on the icon next to the test file name or by opening each of the test reports and scrolling down to the traces section.

Screenshot 2023-01-13 at 09 58 34
Use Playwright's Tooling
Playwright comes with a range of tooling to help you write tests.

The VS Code extension gives you a great developer experience when writing, running, and debugging tests.
The test generator can generate tests and pick locators for you.
The trace viewer gives you a full trace of your tests as a local PWA that can easily be shared. With the trace viewer you can view the timeline, inspect DOM snapshots for each action, view network requests and more.
The UI Mode lets you explore, run and debug tests with a time travel experience complete with watch mode. All test files are loaded into the testing sidebar where you can expand each file and describe block to individually run, view, watch and debug each test.
TypeScript in Playwright works out of the box and gives you better IDE integrations. Your IDE will show you everything you can do and highlight when you do something wrong. No TypeScript experience is needed and it is not necessary for your code to be in TypeScript, all you need to do is create your tests with a .ts extension.
Test across all browsers
Playwright makes it easy to test your site across all browsers no matter what platform you are on. Testing across all browsers ensures your app works for all users. In your config file you can set up projects adding the name and which browser or device to use.

playwright.config.ts
import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],
});

Keep your Playwright dependency up to date
By keeping your Playwright version up to date you will be able to test your app on the latest browser versions and catch failures before the latest browser version is released to the public.

npm
yarn
pnpm
npm install -D @playwright/test@latest

Check the release notes to see what the latest version is and what changes have been released.

You can see what version of Playwright you have by running the following command.

npm
yarn
pnpm
npx playwright --version

Run tests on CI
Setup CI/CD and run your tests frequently. The more often you run your tests the better. Ideally you should run your tests on each commit and pull request. Playwright comes with a GitHub actions workflow so that tests will run on CI for you with no setup required. Playwright can also be setup on the CI environment of your choice.

Use Linux when running your tests on CI as it is cheaper. Developers can use whatever environment when running locally but use linux on CI. Consider setting up Sharding to make CI faster.

Optimize browser downloads on CI
Only install the browsers that you actually need, especially on CI. For example, if you're only testing with Chromium, install just Chromium.

.github/workflows/playwright.yml
# Instead of installing all browsers
npx playwright install --with-deps

# Install only Chromium
npx playwright install chromium --with-deps

This saves both download time and disk space on your CI machines.

Lint your tests
We recommend TypeScript and linting with ESLint for your tests to catch errors early. Use @typescript-eslint/no-floating-promises ESLint rule to make sure there are no missing awaits before the asynchronous calls to the Playwright API. On your CI you can run tsc --noEmit to ensure that functions are called with the right signature.

Use parallelism and sharding
Playwright runs tests in parallel by default. Tests in a single file are run in order, in the same worker process. If you have many independent tests in a single file, you might want to run them in parallel

import { test } from '@playwright/test';

test.describe.configure({ mode: 'parallel' });

test('runs in parallel 1', async ({ page }) => { /* ... */ });
test('runs in parallel 2', async ({ page }) => { /* ... */ });

Playwright can shard a test suite, so that it can be executed on multiple machines.

npm
yarn
pnpm
npx playwright test --shard=1/3

Productivity tips
Use Soft assertions
If your test fails, Playwright will give you an error message showing what part of the test failed which you can see either in VS Code, the terminal, the HTML report, or the trace viewer. However, you can also use soft assertions. These do not immediately terminate the test execution, but rather compile and display a list of failed assertions once the test ended.

// Make a few checks that will not stop the test when failed...
await expect.soft(page.getByTestId('status')).toHaveText('Success');

// ... and continue the test to check more things.
await page.getByRole('link', { name: 'next page' }).click();

Previous
Auto-waiting
Next
Browsers
Introduction
Testing philosophy
Test user-visible behavior
Make tests as isolated as possible
Avoid testing third-party dependencies
Testing with a database
Best Practices
Use locators
Generate locators
Use web first assertions
Configure debugging
Use Playwright's Tooling
Test across all browsers
Keep your Playwright dependency up to date
Run tests on CI
Lint your tests
Use parallelism and sharding
Productivity tips
Use Soft assertions
Learn
Getting started
Playwright Training
Learn Videos
Feature Videos
Community
Stack Overflow
Discord
Twitter
LinkedIn
More
GitHub
YouTube
Blog
Ambassadors
Copyright © 2025 Microsoft



Based on the story you shared, here's a list of the testing and development gaps it highlights:

  Missing Test Coverage


   * End-to-End (E2E) Testing: The "hydration errors" that only appear in production suggest a lack of E2E tests
      that can accurately simulate a real user environment. Tools like Playwright (mentioned in the story) are
     designed for this.
   * Integration Testing for Authentication: The "race condition in your authentication flow" is a classic
     integration bug. This indicates that the authentication system isn't being tested as a whole, especially
     under concurrent conditions.
   * API Testing: The mention of Supertest implies that the API endpoints are not being thoroughly tested for
     correctness and edge cases.
   * Component-Level Testing for Side Effects: The issue with useEffect running twice and causing unexpected
     behavior points to a need for more robust unit and component-level tests using a framework like Jest to
     catch unintended side effects.
   * Edge Case and Unhappy Path Testing: The "undefined" error message suggests that the code isn't being
     tested for scenarios where data might be missing or in an unexpected format.

  CI/CD and Deployment Issues


   * No Automated CI/CD Pipeline: The "failed CI pipelines" and manual deployments on a Saturday afternoon are
     strong indicators that there's no automated process for testing and deploying code. A proper CI/CD
     pipeline would catch many of these issues before they reach production.
   * High-Stakes, Manual Deployments: The fear of deploying and the need for "prayers to the deployment gods"
     point to a manual, error-prone deployment process that lacks confidence.

  Other Decoded Issues


   * Poor Error Handling and Logging: The vague "undefined" error message highlights a lack of specific error
     handling and a robust logging and monitoring solution that would make debugging production issues easier.
   * Lack of Developer Confidence: The overall theme of fear, stress, and lack of confidence in the codebase is
     a direct result of the inadequate testing and deployment practices.
   * Insufficient Knowledge of Frameworks: The useState vs. useRef mistake and the useEffect confusion suggest
     a need for a deeper understanding of the underlying technologies (React/Next.js) and how to test them
     effectively.