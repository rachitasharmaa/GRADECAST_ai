# GradeCast AI — Supabase Auth Files
# =====================================
# HOW TO USE THESE FILES
# =====================================

## Files included:
- src/supabaseClient.js  → Connects to your Supabase project
- src/SignUp.jsx         → Sign Up page (shown first to new users)
- src/Login.jsx          → Login page (for returning users)
- src/App.jsx            → Main app that controls auth flow

## STEP-BY-STEP INSTRUCTIONS:

### Step 1 — Download your existing website
Go to your Netlify dashboard → Deploys → click the latest deploy → Download the files

### Step 2 — Replace / Add these files
Copy these 4 files into your project's `src/` folder:
- Replace your existing App.jsx with the new one
- Add supabaseClient.js (new file)
- Add SignUp.jsx (new file)  
- Add Login.jsx (new file)

### Step 3 — Install Supabase
Open terminal in your project folder and run:
  npm install @supabase/supabase-js

### Step 4 — Connect your existing dashboard
In App.jsx, find this comment:
  // YOUR EXISTING APP COMPONENTS GO HERE
And replace it with your actual dashboard components.

### Step 5 — Deploy to Netlify
Drag and drop your updated project folder onto Netlify.

## HOW IT WORKS:
- New user visits site → sees Sign Up page
- After signing up → email confirmation sent
- Returns to site → sees Login page
- Logs in → sees dashboard with their email shown
- All users stored in Supabase → Authentication → Users

## SUPABASE SETTINGS (important!):
To skip email confirmation during testing:
1. Go to supabase.com → your project → Authentication → Settings
2. Turn OFF "Enable email confirmations"
3. Users can then log in immediately after signing up

## ⚠️ SECURITY NOTE:
Consider regenerating your Supabase anon key since it was shared publicly.
Go to: Supabase → Settings → API Keys → Regenerate
Then update the key in supabaseClient.js
