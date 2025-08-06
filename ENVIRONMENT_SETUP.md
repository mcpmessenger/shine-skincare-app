# Environment Setup Guide

## For Development/Testing

The app now includes fallback values for Supabase configuration, so you can run it without setting up environment variables. The app will show a warning in the console but will continue to function for testing purposes.

## For Production

Create a `.env.local` file in the root directory with the following variables:

```bash
# Supabase Configuration
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here

# Other environment variables
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-key
STRIPE_SECRET_KEY=sk_test_your-stripe-secret
```

## Getting Supabase Credentials

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Navigate to Settings > API in your project dashboard
3. Copy the URL and anon key from the API settings
4. For the service role key, go to Settings > API > Project API keys

## Development Mode

When running in development mode without proper environment variables, the app will:
- Show console warnings about placeholder values
- Continue to function for UI/UX testing
- Disable Supabase-dependent features gracefully
- Allow you to test the core functionality

This setup allows you to develop and test the UI/UX improvements without requiring a full Supabase setup. 