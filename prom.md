I want you to act as a Senior SDET Architect and design a production-grade Custom Reporting Platform for a Java Selenium Maven Cucumber BDD automation framework.

Current framework already supports:

* Selenium WebDriver
* Java
* Maven
* Cucumber BDD
* Spark Reports
* Video Recording
* Screenshot Capture
* Jenkins Integration

I DO NOT want another Spark or Allure clone.

I want a next-generation reporting platform focused on debugging, traceability, analytics, execution intelligence, and beautiful UI/UX.

Main Goal

Create a reporting system that allows QA Engineers, Developers, QA Leads and Managers to understand:

* What happened
* Why it failed
* Where it failed
* How long it took
* Which tests are risky
* Which tests are flaky
* Whether the release is healthy

Architecture

Design the solution as:

Cucumber Hooks
↓
Execution Event Collector
↓
JSON Execution Store
↓
HTML Report Generator
↓
Interactive Dashboard

Use clean architecture and modular design.

Capture Step-Level Telemetry

For every Cucumber step collect:

* Feature Name
* Scenario Name
* Step Name
* Start Timestamp
* End Timestamp
* Duration
* Status
* Exception
* Browser
* Environment
* Build Number
* Thread ID

Store everything in JSON.

Step Timeout Analysis

This is one of the most important requirements.

Measure:

* Step execution duration
* Time gap between steps
* Waiting time before next step
* Selenium explicit waits
* Page load duration
* AJAX/network wait duration

Generate:

Step Performance Table

Example:

Step Duration Risk

Open Login Page 2.1s Normal
Enter Username 0.5s Fast
Click Login 15.3s Warning
Dashboard Load 35.2s Critical

Use color coding:

Green
Yellow
Orange
Red

Create automatic bottleneck detection.

Show:

Top 10 Slowest Steps
Top 10 Slowest Scenarios
Top 10 Slowest Features

Timeline Replay View

Create a Playwright Trace Viewer style page.

Display:

Browser Launch
Step 1
Step 2
Step 3
Failure

in a horizontal timeline.

Each node must be clickable.

When clicked:

Show screenshot
Show logs
Show DOM snapshot
Show network calls
Show execution duration

Screenshot Intelligence

Do NOT only capture screenshots on failure.

Capture screenshots:

* Scenario Start
* Before critical actions
* After critical actions
* On failures
* On warnings
* On performance bottlenecks

Embed screenshots directly inside HTML.

Allow image zoom.

Allow image gallery mode.

Allow timeline screenshot navigation.

Failure Analysis Engine

Automatically classify failures.

Categories:

* TimeoutException
* NoSuchElementException
* StaleElementException
* AssertionError
* Network Failure
* Environment Failure
* Unknown

Generate charts.

Show:

Failure Distribution
Failure Trends
Most Frequent Failure Causes

Flaky Test Detection

Analyze historical executions.

Calculate:

Flaky Score

Example:

PASS
FAIL
PASS
PASS
FAIL

Generate:

Flaky Score %
Stability Index
Confidence Score

Show visual badges:

Stable
Warning
Highly Flaky

Risk Heatmap

Create module-level heatmaps.

Example:

Authentication
Checkout
Payment
Profile
Orders

Color based on:

Failure Rate
Execution Time
Flakiness

Release Readiness Score

Calculate a release score using:

Pass Rate
Critical Failures
Flaky Tests
Execution Stability
Performance Health

Generate:

Release Readiness %

Display as a gauge chart.

Historical Analytics

Store all executions.

Compare builds.

Example:

Build 102
Build 103

Show:

New Failures
Fixed Failures
Execution Time Delta
Pass Rate Delta

Network Monitoring

Use Selenium DevTools.

Collect:

Request URL
Response Status
Response Time

Display slow APIs.

Highlight:

4xx
5xx
Slow Responses

DOM Snapshot Viewer

Capture page source on:

Failure
Warning
Slow Step

Allow expandable DOM inspection inside report.

Video Integration

Embed execution videos directly.

Allow:

Play
Pause
Seek

Connect video timestamps with timeline events.

Clicking a failed step should jump to the corresponding video timestamp.

HTML UI Requirements

This is extremely important.

The report must look like a modern SaaS dashboard.

Use:

* Modern design
* Responsive layout
* Dark Mode
* Light Mode
* Animations
* Charts
* Glassmorphism
* Professional color palette

Avoid old-style reporting layouts.

Use:

* TailwindCSS
* Bootstrap 5
* Chart.js
* ApexCharts
* DataTables

Create:

Dashboard
Execution Summary
Timeline
Failures
Performance
Screenshots
Videos
Analytics
History
Release Readiness

Dashboard Widgets

Total Tests
Passed
Failed
Skipped
Execution Time
Pass Rate
Flaky Tests
Critical Failures
Release Score

Search and Filters

Allow filtering by:

Feature
Scenario
Status
Environment
Build
Browser
Date

Deliverables

Generate:

1. Complete folder structure
2. Architecture diagram
3. Java classes
4. Event collector design
5. JSON schema
6. HTML generation strategy
7. Timeline page design
8. Screenshot embedding strategy
9. Analytics engine design
10. Release readiness algorithm
11. Sample HTML mockups
12. Recommended libraries
13. Extensible plugin architecture

The final result should feel like a combination of:

Playwright Trace Viewer
Datadog
Grafana
Allure
Spark Report

but designed specifically for Selenium + Cucumber automation frameworks.
