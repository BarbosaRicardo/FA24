from playwright.sync_api import sync_playwright
import time
import sys
from datetime import datetime

def log(msg):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def send_logout_email(page):
    try:
        log("Sending logout email via EmailJS in browser context...")
        page.evaluate("""
            emailjs.send("service_68nsjgw", "template_rbgedad", {
                name: "Adumb Bot",
                email: "ricardo.barbosa@edf-re.com",
                message: "⚠️ The Adumb bot logged out at " + new Date().toLocaleString()
            }).then(function(response) {
                console.log('Email sent!', response.status, response.text);
            }, function(error) {
                console.error('Failed to send email:', error);
            });
        """)
        log("EmailJS script injected successfully")
    except Exception as e:
        log(f"EmailJS injection error: {e}")

def login(page):
    try:
        page.fill("#username", "adumb")
        page.fill("#password", "password")
        page.click("input[type='submit']")
        log("Attempted login")
        page.wait_for_selector("#logout", timeout=5000)
        log("Logged in successfully")
    except Exception as e:
        log(f"Login failed: {e}")
        raise

def run_bot():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        try:
            page.goto("https://adumb.netlify.app/", timeout=10000)
            log("Navigated to local site")
        except Exception as e:
            log(f"Failed to navigate to site: {e}")
            sys.exit(1)

        try:
            login(page)
        except:
            sys.exit(1)

        while True:
            try:
                if page.is_closed():
                    log("Browser window was closed. Sending alert and exiting...")
                    send_logout_email(page)
                    sys.exit(1)

                if page.is_visible("#login"):
                    log("Detected login screen again. Sending alert and re-logging in...")
                    send_logout_email(page)
                    login(page)
                    time.sleep(2)
                    continue

                dispatch_form = page.query_selector("#dispatchForm")
                if not dispatch_form:
                    log("No dispatch form found. Waiting...")
                    time.sleep(1)
                    continue

                radios = dispatch_form.query_selector_all("input[type='radio']")
                if radios:
                    checked_count = 0
                    for radio in radios:
                        if not radio.is_checked():
                            try:
                                radio.check(force=True)
                                checked_count += 1
                            except Exception as e:
                                log(f"Could not check radio: {e}")
                    log(f"Selected {checked_count} radio buttons")

                    submit_btn = dispatch_form.query_selector("button.ack-button")
                    if submit_btn:
                        try:
                            submit_btn.click()
                            log("Clicked Submit button")
                        except Exception as e:
                            log(f"Error clicking submit: {e}")
                    else:
                        log("Submit button not found")
                else:
                    log("No radio buttons found")

                time.sleep(3)

            except Exception as e:
                log(f"Error in main loop: {e}")
                time.sleep(5)

if __name__ == "__main__":
    run_bot()
