# GitHub Actions Documentation

This directory contains automated workflows for the repository.

### 1. Keep_alive.yml
*   **Purpose:** Prevents Render Free Tier services from sleeping after 15 minutes of inactivity.
*   **Logic:** Executes an automated ping (HTTP GET) to the backend every 14 minutes.
*   **Benefit:** Eliminates "cold start" delays for users and ensures 24/7 availability.
*   **Manual Trigger:** Navigate to **Actions** > **Keep Render Awake** > **Run workflow**.

> [!IMPORTANT]
> 🚨 **Usage:** Execution is unlimited for public repositories but consumes minutes on private ones.
