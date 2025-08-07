# Secure Trigger Setup Using GitHub Secrets

This setup uses GitHub Secrets to store sensitive data and a proxy workflow for secure triggering.

## Step 1: Create a GitHub Secret

1. Go to your repository settings: https://github.com/s1g9/automated-job-agent/settings/secrets/actions
2. Click "New repository secret"
3. Name: `TRIGGER_TOKEN`
4. Value: `job-search-2025` (or any secret string you prefer)
5. Click "Add secret"

## Step 2: How It Works

1. The `trigger-proxy.yml` workflow accepts a public token as input
2. It validates this token against the secret `TRIGGER_TOKEN`
3. If valid, it triggers the actual job search workflow
4. The GitHub PAT is never exposed - it uses GitHub's built-in permissions

## Step 3: Usage

When you click "Trigger New Search" on your GitHub Pages site:
1. It opens the trigger-proxy workflow page
2. You enter the token: `job-search-2025`
3. The proxy workflow validates and triggers the actual job search

## Alternative: Using GitHub Apps (More Advanced)

For a fully automated solution without manual steps:

1. Create a GitHub App for your repository
2. Use the app's authentication instead of PAT
3. Host a simple serverless function (Vercel, Netlify, etc.) that:
   - Receives requests from your GitHub Pages site
   - Uses the GitHub App credentials to trigger workflows
   - No PAT needed, more secure

## Current Implementation Benefits

- ✅ No PAT exposed in code
- ✅ Works with static GitHub Pages
- ✅ Uses GitHub's built-in security
- ✅ Simple to set up
- ✅ Token can be shared publicly (it's validated server-side)

## Note

The current implementation requires one manual step (entering the token in GitHub Actions), but it's the most secure approach for a static site without backend infrastructure.