# Putting your site online — beginner guide (no coding required)

This walks you through getting the Community Resource Map live on the internet,
for free, using **GitHub** (to store the code) and **Render** (to run it).
You will not need to use a terminal or write any code.

Total time: about 20–30 minutes, most of it waiting for the build.

---

## What you'll end up with

- A public website at an address like `https://community-resource-map.onrender.com`
- A map with sample resources already loaded
- An admin login so you can approve submissions and add real resources

Two things to know about the **free** plan up front (both are fine for a demo
or a small project, and you can upgrade later):

1. **It falls asleep.** After ~15 minutes with no visitors, the site sleeps.
   The next visitor waits about a minute while it wakes up, then it's fast again.
2. **The free database is temporary.** Render deletes free databases about 30
   days after they're created. Before then, upgrade the database to a paid plan
   (a few dollars a month) to keep your data, or treat this as a throwaway demo.

---

## Step 1 — Make a GitHub account and upload the code

GitHub is where your code lives so Render can read it.

1. Go to https://github.com and sign up (free). Verify your email.
2. Click the **+** in the top-right corner, then **New repository**.
3. Name it `community-resource-map`. Leave it **Public**. Click
   **Create repository**.
4. On the next page, click the link **"uploading an existing file"**.
5. Unzip the project on your computer, then drag the **contents** of the
   `community-resource-map` folder onto the upload area. (Drag the files and
   folders inside it — `config`, `resources`, `templates`, `render.yaml`,
   `build.sh`, and so on — not the outer folder itself.)
6. Wait for the files to finish uploading, then click **Commit changes**.

That's it — your code is now on GitHub.

---

## Step 2 — Create a Render account

1. Go to https://render.com and click **Get Started**.
2. Choose **Sign in with GitHub** (this lets Render see your repository).
3. When asked, give Render permission to access your repositories. You can
   limit it to just the `community-resource-map` repo.

No credit card is required for the free plan.

---

## Step 3 — Deploy with one click using the Blueprint

The project includes a file called `render.yaml` that tells Render exactly
what to build, so you don't have to configure anything by hand.

1. In the Render dashboard, open the **Blueprints** section
   (https://dashboard.render.com/blueprints).
2. Click **New Blueprint Instance**.
3. Select your `community-resource-map` repository and click **Connect**.
4. Render reads `render.yaml` and shows what it will create: a web service and
   a database. It will ask you to fill in one secret value:
   - **DJANGO_SUPERUSER_PASSWORD** — type a strong password here and remember
     it. This is the password for your admin login (the username is `admin`).
5. Give the blueprint a name if asked, then click **Apply**.

Render now builds everything. This takes a few minutes — you'll see logs
scrolling. When it's done, the web service shows a green **Live** badge and a
URL ending in `.onrender.com`.

---

## Step 4 — Visit your site and log in as admin

1. Click your site's `.onrender.com` URL. You should see the map with sample
   resources. (If it's the first visit in a while, give it a minute to wake up.)
2. Go to your URL with `/admin/` on the end, for example
   `https://community-resource-map.onrender.com/admin/`.
3. Log in with username `admin` and the password you chose in Step 3.

From the admin you can add real resources, edit categories, and manage
everything. There's also a simpler approval screen at `/manage/queue/` for
reviewing resources that the public submits through the **Submit** form.

---

## Step 5 — (Optional) Turn off the sample data

The sample resources are fictional, placed at real Denver coordinates just so
the map looks alive. Once you've added your own:

1. In Render, open your web service, go to **Environment**.
2. Find `SEED` and change its value from `true` to `false`. Save.
   (This only stops *re-loading* samples on future deploys; it doesn't delete
   anything. Remove unwanted sample entries in the admin.)

---

## Updating the site later

Any time you change a file on GitHub (even by editing it in the GitHub website
and clicking **Commit changes**), Render automatically rebuilds and redeploys.
You don't need to do anything in Render.

---

## If something goes wrong

- **Build failed:** open the web service in Render and read the **Logs** tab —
  the error is usually near the bottom. The most common cause is a file that
  didn't upload to GitHub; check that `requirements.txt`, `build.sh`,
  `render.yaml`, and the `config` and `resources` folders are all there.
- **"Bad Request (400)" when visiting the site:** this means the site address
  isn't recognized. It normally fixes itself because the app detects its Render
  address automatically — wait for the deploy to finish and refresh.
- **Site shows a long blank load:** that's the free plan waking up. Wait ~1 min.
- **Forgot the admin password:** in Render, open the web service → **Shell**,
  and run `python manage.py changepassword admin`.
