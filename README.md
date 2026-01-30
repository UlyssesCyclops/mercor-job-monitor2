# Mercor Job Monitor

Automatically monitor Mercor.com for new job postings and receive email notifications.

## Features

- 🔍 Checks Mercor.com every 30 minutes for new jobs
- 📧 Sends email notifications when new positions are posted
- 🤖 Runs automatically via GitHub Actions (no server needed)
- 🆓 Completely free to use
- 👥 Easy to fork and customize for your own use

## Setup Instructions

### 1. Fork this repository
Click the "Fork" button at the top right of this page to create your own copy.

### 2. Configure your email
Edit `config.json` and replace with your email address:
```json
{
  "email": "your-email@gmail.com",
  "smtp_user": "your-email@gmail.com",
  "smtp_from": "Mercor Job Monitor <your-email@gmail.com>"
}
```

### 3. Set up Gmail App Password

To send email notifications, you need a Gmail App Password:

1. Go to your Google Account: https://myaccount.google.com/
2. Select **Security** from the left menu
3. Under "How you sign in to Google," select **2-Step Verification** (you must enable this first if not already enabled)
4. Scroll to the bottom and select **App passwords**
5. Select **Mail** and **Other (Custom name)**, name it "Mercor Monitor"
6. Google will generate a 16-character password - copy this

### 4. Add the App Password to GitHub Secrets

1. In your forked repository, go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `SMTP_PASSWORD`
4. Value: Paste the 16-character app password from Gmail
5. Click **Add secret**

### 5. Enable GitHub Actions

1. Go to the **Actions** tab in your repository
2. Click "I understand my workflows, go ahead and enable them"

### 6. Run it manually (optional)

To test immediately:
1. Go to **Actions** tab
2. Click "Monitor Mercor Jobs" workflow
3. Click "Run workflow" → "Run workflow"

## How It Works

- The monitor runs every 30 minutes automatically
- It scrapes the Mercor job listings page
- Compares against previously seen jobs (stored in `seen_jobs.json`)
- Sends an email notification for any new jobs found
- Updates the `seen_jobs.json` file to track what's been seen

## Customization

### Change Check Frequency

Edit `.github/workflows/monitor.yml` and modify the cron schedule:

```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 */2 * * *'   # Every 2 hours
  # - cron: '0 9,17 * * *'  # 9 AM and 5 PM daily
```

### Add Filters

Edit `monitor.py` to filter jobs by keywords, pay rate, etc. Look for the `scrape_jobs()` function.

### Change Email Settings

Edit `config.json` to customize email addresses and display name.

## For Other Users

Anyone can use this! Just:
1. Fork this repository
2. Update `config.json` with your email
3. Add your Gmail app password as a GitHub secret
4. Enable Actions

That's it!

## Troubleshooting

**No emails arriving?**
- Check spam/junk folder
- Verify the `SMTP_PASSWORD` secret is set correctly
- Check the Actions tab for error messages

**Actions not running?**
- Make sure Actions are enabled in your repository settings
- Check that the workflow file is in `.github/workflows/`

**Want to see what jobs were found?**
- Check the Actions logs under the "Run job monitor" step
- Look at `seen_jobs.json` in your repository

## Privacy

- Your email and app password are stored as GitHub secrets (encrypted)
- Job data is only stored in your repository
- No data is shared with third parties

## License

MIT License - feel free to modify and share!
