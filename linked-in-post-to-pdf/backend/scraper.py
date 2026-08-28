"""
scraper.py — Playwright-based LinkedIn post image carousel capture.

Strategy:
  1. Navigate to the LinkedIn post URL.
  2. Locate the images section within the post.
  3. Click the image area to open LinkedIn's fullscreen lightbox/carousel overlay.
  4. Inside the lightbox dialog, screenshot each image and navigate with Next.
  5. Save all screenshots sequentially at 2× retina resolution.

Supports both:
  • Multi-image posts  (up to 9 images displayed as a grid → opens lightbox)
  • Document posts     (PDF/PPT rendered as a slide viewer)
"""

import os
import re
import tempfile
from pathlib import Path
from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError

# Persistent browser profile directory (stores LinkedIn session cookies)
BROWSER_DATA_DIR = Path(__file__).parent / ".browser-data"


def _ensure_browser_data_dir():
    """Create the persistent browser data directory if it doesn't exist."""
    BROWSER_DATA_DIR.mkdir(parents=True, exist_ok=True)


def _wait_for_login(page, timeout_seconds=300):
    """
    If the user is not logged in, wait for them to complete LinkedIn login.
    Shows the browser window so the user can interact.
    """
    try:
        page.wait_for_selector(
            '[data-test-id="nav-header"], .global-nav, .feed-identity-module, '
            '[class*="global-nav"], [class*="feed-identity"]',
            timeout=10_000,
        )
        print("[scraper] User appears to be logged in.")
    except PWTimeoutError:
        print(
            f"[scraper] Login required. Please log in within {timeout_seconds}s..."
        )
        page.wait_for_selector(
            '[data-test-id="nav-header"], .global-nav, .feed-identity-module, '
            '[class*="global-nav"], [class*="feed-identity"]',
            timeout=timeout_seconds * 1000,
        )
        print("[scraper] Login detected. Continuing...")


# ─────────────────────────────────────────────────────────────────────────────
#  Step 1 — Find and click the image area in the post to open the lightbox
# ─────────────────────────────────────────────────────────────────────────────

def _click_post_image(page) -> bool:
    """
    Locate the images section in the LinkedIn post and click on it
    to trigger the fullscreen lightbox/carousel overlay.

    Returns True if an image was found and clicked.
    """

    # --- Strategy A: Click any <img> inside the post content area ---
    post_image_selectors = [
        # Multi-image posts — images in the feed
        '.feed-shared-image__container img',
        '[class*="feed-shared-image"] img',
        '[class*="feed-shared-carousel"] img',
        '[class*="update-components-image"] img',
        '[class*="update-components"] img[src*="media.licdn"]',
        # Document posts — embedded viewer thumbnails
        '[class*="document"] img',
        '[class*="ssplayer"] img',
        # Generic: any image in the main post content
        '[class*="feed-shared"] [class*="image"] img',
        '[class*="feed-shared-update"] img',
        # Broader fallback: any large image in the post
        'article img[src*="media.licdn"]',
        '.feed-shared-update-v2 img[src*="media.licdn"]',
    ]

    for sel in post_image_selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=2000):
                print(f"[scraper] Found post image via: {sel}")
                loc.click()
                return True
        except Exception:
            continue

    # --- Strategy B: Click by ARIA role — images or buttons within the post ---
    try:
        # LinkedIn sometimes wraps images in buttons or links with aria roles
        img_btn = page.locator(
            '[class*="feed-shared"] [role="button"] img, '
            '[class*="feed-shared"] [role="link"] img, '
            '[class*="feed-shared"] button img'
        ).first
        if img_btn.is_visible(timeout=2000):
            print("[scraper] Found post image via role-wrapped img.")
            img_btn.click()
            return True
    except Exception:
        pass

    # --- Strategy C: Click the image container (not the img itself) ---
    container_selectors = [
        '.feed-shared-image__container',
        '[class*="feed-shared-image"]',
        '[class*="update-components-image"]',
        '[class*="feed-shared-carousel"]',
    ]

    for sel in container_selectors:
        try:
            loc = page.locator(sel).first
            if loc.is_visible(timeout=2000):
                print(f"[scraper] Found image container via: {sel}")
                loc.click()
                return True
        except Exception:
            continue

    # --- Strategy D: Broadest fallback — any clickable image on the page ---
    try:
        all_imgs = page.locator('img[src*="media.licdn.com"]')
        count = all_imgs.count()
        for i in range(min(count, 5)):
            img = all_imgs.nth(i)
            # Skip tiny images (profile pics, icons)
            box = img.bounding_box()
            if box and box["width"] > 200 and box["height"] > 200:
                print(f"[scraper] Found large LinkedIn-hosted image #{i+1}.")
                img.click()
                return True
    except Exception:
        pass

    return False


# ─────────────────────────────────────────────────────────────────────────────
#  Step 2 — Wait for the lightbox/overlay dialog to open
# ─────────────────────────────────────────────────────────────────────────────

def _wait_for_lightbox(page, timeout_ms=10_000):
    """
    After clicking an image, wait for LinkedIn's fullscreen lightbox/overlay
    to appear.  Returns the lightbox locator or None.
    """
    lightbox_selectors = [
        '[role="dialog"]',
        '[class*="image-viewer"]',
        '[class*="lightbox"]',
        '[class*="media-viewer"]',
        '[class*="carousel-modal"]',
        '[class*="overlay"]',
        '.artdeco-modal',
        '[class*="artdeco-modal"]',
        # Document viewer fullscreen
        '[class*="document-viewer"]',
        '[class*="ssplayer"]',
    ]

    for sel in lightbox_selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=timeout_ms)
            print(f"[scraper] Lightbox opened via: {sel}")
            return loc
        except Exception:
            continue

    # Final fallback: any new modal/overlay that appeared
    try:
        loc = page.locator('[role="dialog"], [role="presentation"]').first
        loc.wait_for(state="visible", timeout=3000)
        print("[scraper] Lightbox opened via role fallback.")
        return loc
    except Exception:
        pass

    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Step 3 — Extract the image count from the lightbox indicator
# ─────────────────────────────────────────────────────────────────────────────

def _get_image_count(page, lightbox) -> int:
    """
    Try to determine total images from an indicator like '1 of 12' or '1/12'.
    Returns -1 if count can't be determined (we'll navigate until Next is gone).
    """

    # Look inside the lightbox first, then the full page
    search_contexts = [lightbox, page] if lightbox else [page]

    for ctx in search_contexts:
        try:
            text = ctx.inner_text()
            matches = re.findall(r'(\d+)\s*(?:of|/)\s*(\d+)', text)
            for _, total in matches:
                total_int = int(total)
                if 2 <= total_int <= 100:
                    print(f"[scraper] Detected {total_int} images from indicator.")
                    return total_int
        except Exception:
            continue

    return -1


# ─────────────────────────────────────────────────────────────────────────────
#  Step 4 — Find the Next button inside the lightbox
# ─────────────────────────────────────────────────────────────────────────────

def _find_next_button(page, lightbox):
    """
    Find the 'Next' navigation button inside the lightbox/overlay.
    Searches by aria-label, role, and common class patterns.
    """

    # Prefer searching within the lightbox, fall back to page
    search_contexts = [lightbox, page] if lightbox else [page]

    next_selectors = [
        'button[aria-label="Next"]',
        'button[aria-label="Next image"]',
        'button[aria-label="Next page"]',
        'button[aria-label="next"]',
        'button[aria-label="Go forward"]',
        '[class*="next-btn"]',
        '[class*="right-arrow"]',
        '[class*="nav-next"]',
        'button[class*="next"]',
        '[class*="carousel"] button:last-of-type',
    ]

    for ctx in search_contexts:
        for sel in next_selectors:
            try:
                loc = ctx.locator(sel).first
                if loc.is_visible(timeout=800):
                    return loc
            except Exception:
                continue

    # Try by role with name pattern
    for ctx in search_contexts:
        try:
            loc = ctx.get_by_role(
                "button", name=re.compile(r"next", re.IGNORECASE)
            ).first
            if loc.is_visible(timeout=800):
                return loc
        except Exception:
            continue

    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Step 5 — Find the active image element to screenshot inside the lightbox
# ─────────────────────────────────────────────────────────────────────────────

def _find_active_image(page, lightbox):
    """
    Locate the currently displayed image inside the lightbox to take a
    targeted screenshot of just the image (not the surrounding UI).
    """

    search_contexts = [lightbox, page] if lightbox else [page]

    active_image_selectors = [
        'img[class*="viewer"]',
        'img[class*="lightbox"]',
        'img[class*="media-viewer"]',
        '[class*="image-viewer"] img',
        '[class*="media-viewer"] img',
        '[role="dialog"] img[src*="media.licdn"]',
        '[role="dialog"] img',
        '[class*="carousel"] img',
        # Document viewer slides
        '[class*="ssplayer"] img',
        '[class*="document-viewer"] img',
    ]

    for ctx in search_contexts:
        for sel in active_image_selectors:
            try:
                loc = ctx.locator(sel).first
                if loc.is_visible(timeout=1500):
                    # Skip tiny images (buttons, icons) — require at least 100×100
                    box = loc.bounding_box()
                    if box and box["width"] > 100 and box["height"] > 100:
                        return loc
            except Exception:
                continue

    # Broadest fallback: any large visible img inside the lightbox
    if lightbox:
        try:
            all_imgs = lightbox.locator("img")
            count = all_imgs.count()
            for i in range(count):
                img = all_imgs.nth(i)
                if img.is_visible():
                    box = img.bounding_box()
                    if box and box["width"] > 100 and box["height"] > 100:
                        return img
        except Exception:
            pass

    return None


# ─────────────────────────────────────────────────────────────────────────────
#  Main entry point
# ─────────────────────────────────────────────────────────────────────────────

def scrape_carousel(
    post_url: str,
    on_progress=None,
) -> list[str]:
    """
    Scrapes all images from a LinkedIn post's image carousel.

    Workflow:
      1. Navigate to the post URL.
      2. Find the images section in the post and click it.
      3. Wait for the fullscreen lightbox/overlay to open.
      4. Screenshot each image, clicking Next to advance.
      5. Stop when Next is gone/disabled or we've looped back.

    Args:
        post_url:    Full URL of the LinkedIn post.
        on_progress: Optional callback  (current, total, message) -> None

    Returns:
        List of absolute file paths to captured images, in order.
    """
    _ensure_browser_data_dir()
    tmp_dir = tempfile.mkdtemp(prefix="linkedin_slides_")

    def _progress(current, total, msg):
        if on_progress:
            on_progress(current, total, msg)
        print(f"[scraper] [{current}/{total}] {msg}")

    image_paths: list[str] = []

    with sync_playwright() as p:
        _progress(0, 0, "Launching browser...")

        browser = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA_DIR),
            headless=False,
            viewport={"width": 1920, "height": 1080},
            device_scale_factor=2,       # retina-quality screenshots
            slow_mo=200,                 # human-like pace
            args=[
                "--disable-blink-features=AutomationControlled",
            ],
        )

        page = browser.pages[0] if browser.pages else browser.new_page()

        try:
            # ── Navigate ──────────────────────────────────────────────
            _progress(0, 0, "Navigating to LinkedIn post...")
            page.goto(post_url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_load_state("networkidle", timeout=30_000)

            # ── Login check ───────────────────────────────────────────
            _wait_for_login(page)

            _progress(0, 0, "Looking for images in the post...")
            page.wait_for_timeout(3000)  # let the post fully render

            # ── Step 1: Click the image area to open lightbox ─────────
            clicked = _click_post_image(page)
            if not clicked:
                raise RuntimeError(
                    "Could not find any images in this LinkedIn post. "
                    "Make sure the URL points to a post that contains "
                    "multiple images or a document carousel."
                )

            _progress(0, 0, "Image clicked — waiting for carousel to open...")
            page.wait_for_timeout(2000)  # give lightbox time to animate in

            # ── Step 2: Wait for lightbox overlay ─────────────────────
            lightbox = _wait_for_lightbox(page)
            if lightbox is None:
                # Lightbox may not have opened — maybe it's a document
                # viewer that expanded in-place. Continue anyway with page.
                print("[scraper] No lightbox detected — will try in-page capture.")
                lightbox = None

            # ── Step 3: Count images ──────────────────────────────────
            total = _get_image_count(page, lightbox)
            max_slides = total if total > 0 else 50  # safety cap
            _progress(0, max_slides, f"Detected {total if total > 0 else 'unknown number of'} images.")

            # ── Step 4: Capture loop ──────────────────────────────────
            slide_num = 0
            first_screenshot_hash = None

            while slide_num < max_slides:
                slide_num += 1
                _progress(slide_num, max_slides, f"Capturing image {slide_num}...")
                page.wait_for_timeout(1000)  # wait for image to load

                img_path = os.path.join(tmp_dir, f"slide_{slide_num:03d}.png")

                # Try to screenshot just the active image element
                active_img = _find_active_image(page, lightbox)
                if active_img:
                    try:
                        active_img.screenshot(path=img_path)
                    except Exception:
                        # Element went stale — screenshot the lightbox or page
                        if lightbox:
                            lightbox.screenshot(path=img_path)
                        else:
                            page.screenshot(path=img_path, full_page=False)
                elif lightbox:
                    lightbox.screenshot(path=img_path)
                else:
                    page.screenshot(path=img_path, full_page=False)

                # Detect duplicates (loop-back detection)
                try:
                    file_size = os.path.getsize(img_path)
                    if slide_num == 1:
                        first_screenshot_hash = file_size
                    elif slide_num > 2 and file_size == first_screenshot_hash:
                        # Likely looped back to the first image
                        os.remove(img_path)
                        _progress(slide_num - 1, slide_num - 1,
                                  "Loop detected — removing duplicate, all images captured.")
                        break
                except Exception:
                    pass

                image_paths.append(img_path)

                # ── Navigate to next ──────────────────────────────────
                next_btn = _find_next_button(page, lightbox)
                if next_btn is None:
                    _progress(slide_num, slide_num,
                              "No Next button found — all images captured.")
                    break

                try:
                    if not next_btn.is_enabled():
                        _progress(slide_num, slide_num,
                                  "Next button disabled — all images captured.")
                        break
                except Exception:
                    pass

                try:
                    next_btn.click()
                    page.wait_for_timeout(1200)  # wait for slide transition
                except Exception as e:
                    _progress(slide_num, slide_num, f"Could not click Next: {e}")
                    break

            _progress(len(image_paths), len(image_paths), "All images captured!")

        finally:
            browser.close()

    return image_paths
