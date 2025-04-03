import os

required_envs = ["BOT_TOKEN", "CALENDAR_ID", "GOOGLE_CREDENTIALS"]
missing = [env for env in required_envs if not os.environ.get(env)]

if missing:
    print(f"⚠️ Missing environment variables: {', '.join(missing)}")
    print("➡️ Please set them in Replit Secrets (Tools > Secrets).")
else:
    import ashraf_bot
