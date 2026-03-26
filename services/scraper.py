import asyncio
import httpx
from playwright.async_api import async_playwright
from playwright_stealth import Stealth # Note the change here

async def run_stealth_scraper():
    async with async_playwright() as p:
        # Directory to save your session (so you don't have to login every time)
        user_data_dir = "./x_user_session"
        
        # 1. Initialize Stealth
        stealth = Stealth()

        # 2. Launch with a persistent context
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False,  # Keep it False to perform the manual login
            args=["--disable-blink-features=AutomationControlled"],
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        
        page = context.pages[0]
        
        # 3. Apply stealth to the page
        # In newer versions, we use apply_stealth_async
        await stealth.apply_stealth_async(page)
        
        print("🌍 Navigating to X...")
        await page.goto("https://x.com/login")
        
        print("🛑 Please log in manually in the browser window.")
        print("The script will wait for you to reach the home feed...")

        # Wait for the "Home" or "Post/Tweet" button to appear (indicates login success)
        try:
            # This waits up to 2 minutes for you to finish logging in
            await page.wait_for_selector('a[data-testid="SideNav_NewTweet_Button"]', timeout=120000)
            print("✅ Login Successful! Navigating to search...")
            
            # Now go to your specific search
            await page.goto("https://x.com/search?q=%23OxygenNeeded&f=live")
            await page.wait_for_timeout(5000) # Wait for tweets to load

            # 4. Extract real data
            tweets = await page.locator('div[data-testid="tweetText"]').all_inner_texts()
            user_elements = await page.locator('div[data-testid="User-Name"]').all_inner_texts()
            async with httpx.AsyncClient() as client:
                for i, t in enumerate(tweets[:5]):
                    user_name = user_elements[i].split('\n')[0] if i < len(user_elements) else "Unknown"
                    payload = {"text": t, "user": user_name}
                    
                    try:
                        # Now 'client' refers to httpx.AsyncClient()
                        response = await client.post("http://localhost:8000/ingest", json=payload)
                        print(f"🧠 Brain Response: {response.json()}")
                    except Exception as e:
                        print(f"❌ Connection Error: {e}")
                    
                    print(f"📡 Tweet {i+1}: {t[:70]}...")

        except Exception as e:
            print(f"⚠️ Error: {e}")
        
        print("\n🎉 Your session is saved. You can close the browser now.")
        await context.close()

if __name__ == "__main__":
    asyncio.run(run_stealth_scraper())