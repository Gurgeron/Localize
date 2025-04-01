#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Browser Module

This module handles browser automation using Playwright.
It provides functionality for browser setup, navigation, and screenshot capture.
Enhanced with automatic page discovery and intelligent modal detection.
"""

import os
import time
import logging
import asyncio
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Set
from datetime import datetime

# Import Playwright
from playwright.async_api import async_playwright, Browser, Page, ElementHandle, TimeoutError, Locator

# Import our modules
from .config_loader import get

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Interactive elements that may trigger modals
MODAL_TRIGGER_SELECTORS = [
    'button',
    'a[role="button"]',
    '[data-testid*="modal"]',
    '[aria-haspopup="dialog"]',
    '.modal-trigger',
    '[class*="modal"]',
    '[class*="button"]',
    '[class*="btn"]',
    '[aria-label*="settings"]',
    '[aria-label*="options"]',
    '[aria-label*="menu"]',
    'a[href="#"][class*="icon"]',
    '[data-bs-toggle="modal"]',
]

# Modal container selectors
MODAL_CONTAINER_SELECTORS = [
    '.modal',
    '[role="dialog"]',
    '[aria-modal="true"]',
    '.dialog',
    '.popup',
    '[class*="modal"]',
    '[class*="dialog"]',
    '[class*="overlay"]',
    '[class*="popup"]',
]

class BrowserController:
    """
    BrowserController class for handling browser automation using Playwright
    """
    
    def __init__(self):
        """
        Initialize the BrowserController
        """
        self.browser = None
        self.context = None
        self.page = None
        self.playwright = None
        self.screenshot_dir = Path(get('output.screenshot_dir', './screenshots'))
        
        # Ensure screenshot directory exists
        if not self.screenshot_dir.exists():
            self.screenshot_dir.mkdir(parents=True, exist_ok=True)
            
        # Keep track of visited pages
        self.visited_pages = set()
        self.visited_modals = set()
        self.discovered_pages = set()
        self.base_url = ""
    
    async def setup(self) -> None:
        """
        Set up the browser and context
        
        Raises:
            Exception: If there's an error setting up the browser
        """
        try:
            logger.info("Setting up browser...")
            
            # Get browser settings from config
            browser_type = get('browser.type', 'chromium')
            headless = get('application.headless', False)
            width = get('browser.width', 1920)
            height = get('browser.height', 1080)
            user_agent = get('browser.user_agent', '')
            
            # Launch browser
            self.playwright = await async_playwright().start()
            browser_module = getattr(self.playwright, browser_type)
            
            # Set launch options
            launch_options = {
                "headless": headless
            }
            
            self.browser = await browser_module.launch(**launch_options)
            
            # Create context with viewport and user agent settings
            context_options = {
                "viewport": {"width": width, "height": height}
            }
            
            if user_agent:
                context_options["user_agent"] = user_agent
                
            self.context = await self.browser.new_context(**context_options)
            self.page = await self.context.new_page()
            
            # Set default timeout
            timeout = get('application.default_timeout', 30000)
            self.page.set_default_timeout(timeout)
            
            logger.info(f"Browser setup complete: {browser_type}, headless={headless}, viewport={width}x{height}")
            
        except Exception as e:
            logger.error(f"Error setting up browser: {e}")
            await self.teardown()
            raise e
    
    async def teardown(self) -> None:
        """
        Clean up browser resources
        """
        logger.info("Tearing down browser resources...")
        
        try:
            if self.page:
                await self.page.close()
                self.page = None
                
            if self.context:
                await self.context.close()
                self.context = None
                
            if self.browser:
                await self.browser.close()
                self.browser = None
                
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
                
            logger.info("Browser resources released")
            
        except Exception as e:
            logger.error(f"Error during browser teardown: {e}")
    
    async def navigate_to_url(self, url: str) -> bool:
        """
        Navigate to a URL
        
        Args:
            url (str): The URL to navigate to
            
        Returns:
            bool: True if navigation was successful, False otherwise
        """
        if not self.page:
            logger.error("Cannot navigate: browser page not initialized")
            return False
            
        try:
            # If URL doesn't start with http(s), assume it's a relative URL
            if not url.startswith(('http://', 'https://')):
                base_url = get('application.base_url', '')
                if not base_url:
                    logger.error("Cannot navigate to relative URL: base_url not set in config")
                    return False
                full_url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                # Save base URL for page discovery
                self.base_url = base_url
            else:
                full_url = url
                # Extract base URL for page discovery
                parsed_url = urllib.parse.urlparse(url)
                self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
            logger.info(f"Navigating to: {full_url}")
            
            # Navigate to the URL
            await self.page.goto(full_url)
            
            # Wait for page to stabilize
            stabilization_time = get('application.stabilization_time', 1000)
            if stabilization_time > 0:
                await asyncio.sleep(stabilization_time / 1000)  # Convert to seconds
                
            logger.info(f"Successfully navigated to: {full_url}")
            self.visited_pages.add(url)
            
            # After navigating, discover links on the page
            await self._discover_page_links()
            
            return True
            
        except TimeoutError as e:
            logger.error(f"Timeout navigating to {url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error navigating to {url}: {e}")
            return False
    
    async def _discover_page_links(self) -> None:
        """
        Discover links on the current page that might be navigation targets
        """
        if not self.page:
            return
            
        try:
            # Get all links on the page
            links = await self.page.query_selector_all('a[href]')
            
            for link in links:
                href = await link.get_attribute('href')
                
                if not href:
                    continue
                    
                # Skip external links, anchors, and non-HTTP protocols
                if (href.startswith('#') or 
                    href.startswith('mailto:') or 
                    href.startswith('tel:') or
                    href.startswith('javascript:')):
                    continue
                    
                # If it's a relative URL, add the base URL
                if not href.startswith(('http://', 'https://')):
                    if href.startswith('/'):
                        href = f"{self.base_url}{href}"
                    else:
                        href = f"{self.base_url}/{href}"
                
                # Only consider URLs from the same domain
                if self.base_url in href:
                    # Extract the path part for discovered_pages
                    parsed_url = urllib.parse.urlparse(href)
                    path = parsed_url.path
                    
                    # Skip very long paths or those with query parameters (likely dynamic)
                    if len(path) > 100 or '?' in href:
                        continue
                        
                    # Add to discovered pages
                    self.discovered_pages.add(path)
            
            logger.debug(f"Discovered {len(self.discovered_pages)} potential navigation targets")
            
        except Exception as e:
            logger.error(f"Error discovering page links: {e}")
    
    async def take_screenshot(self, name: str, modal: bool = False) -> Optional[str]:
        """
        Take a screenshot of the current page
        
        Args:
            name (str): Name for the screenshot file
            modal (bool): Whether this is a screenshot of a modal
            
        Returns:
            Optional[str]: Path to the screenshot file, or None if failed
        """
        if not self.page:
            logger.error("Cannot take screenshot: browser page not initialized")
            return None
            
        try:
            # Create a safe filename from the name
            safe_name = "".join([c if c.isalnum() else "_" for c in name])
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{safe_name}_{timestamp}.png"
            
            if modal:
                # Create a modal subdirectory if needed
                modal_dir = self.screenshot_dir / "modals"
                if not modal_dir.exists():
                    modal_dir.mkdir(parents=True, exist_ok=True)
                filepath = modal_dir / filename
                logger.info(f"Taking screenshot of modal: {name}")
            else:
                filepath = self.screenshot_dir / filename
                logger.info(f"Taking screenshot of page: {name}")
                
            # Take the screenshot
            await self.page.screenshot(path=str(filepath), full_page=True)
            
            logger.info(f"Screenshot saved to: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Error taking screenshot of {name}: {e}")
            return None
    
    async def click_element(self, selector: str) -> bool:
        """
        Click an element on the page
        
        Args:
            selector (str): CSS selector for the element
            
        Returns:
            bool: True if click was successful, False otherwise
        """
        if not self.page:
            logger.error("Cannot click element: browser page not initialized")
            return False
            
        try:
            logger.info(f"Attempting to click element: {selector}")
            
            # First check if element exists
            element = await self.page.query_selector(selector)
            if not element:
                logger.warning(f"Element not found: {selector}")
                return False
                
            # Check if element is visible
            is_visible = await element.is_visible()
            if not is_visible:
                logger.warning(f"Element is not visible: {selector}")
                return False
                
            # Click the element
            await element.click()
            
            # Wait for any potential navigation or modal to appear
            stabilization_time = get('application.stabilization_time', 1000)
            if stabilization_time > 0:
                await asyncio.sleep(stabilization_time / 1000)  # Convert to seconds
                
            logger.info(f"Successfully clicked element: {selector}")
            return True
            
        except TimeoutError as e:
            logger.error(f"Timeout clicking element {selector}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
            return False
    
    async def wait_for_user_login(self, url: str, prompt_message: str = "Please log in manually and press Enter when ready...") -> bool:
        """
        Open a URL and wait for the user to manually log in
        
        Args:
            url (str): The URL to navigate to
            prompt_message (str): Message to display to user
            
        Returns:
            bool: True if login appears successful, False otherwise
        """
        if not self.page:
            logger.error("Cannot wait for login: browser page not initialized")
            return False
            
        try:
            # If URL doesn't start with http(s), assume it's a relative URL
            if not url.startswith(('http://', 'https://')):
                base_url = get('application.base_url', '')
                if not base_url:
                    logger.error("Cannot navigate to relative URL: base_url not set in config")
                    return False
                full_url = f"{base_url.rstrip('/')}/{url.lstrip('/')}"
                # Save base URL for page discovery
                self.base_url = base_url
            else:
                full_url = url
                # Extract base URL for page discovery
                parsed_url = urllib.parse.urlparse(url)
                self.base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
                
            logger.info(f"Navigating to login page: {full_url}")
            
            # Navigate to the URL
            await self.page.goto(full_url)
            
            # Prompt the user to manually log in
            print("\n" + "=" * 80)
            print(prompt_message)
            print("=" * 80 + "\n")
            
            # Wait for user to press Enter
            input()
            
            # Check if the login was successful (this is a simple check and may need customization)
            current_url = self.page.url
            logger.info(f"Current URL after login: {current_url}")
            
            # Simple check - if URL changed, assume login was successful
            login_successful = current_url != full_url
            
            if login_successful:
                logger.info("Login appears to be successful")
                # After login, discover links on the page
                await self._discover_page_links()
            else:
                logger.warning("Login may not have been successful (URL did not change)")
                
            return login_successful
            
        except Exception as e:
            logger.error(f"Error during login process: {e}")
            return False
    
    async def process_page(self, page_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a page according to its configuration
        
        Args:
            page_config (Dict[str, Any]): Configuration for the page
            
        Returns:
            Dict[str, Any]: Results including screenshots and visited status
        """
        results = {
            "page_name": page_config.get("name", "Unknown Page"),
            "url": page_config.get("url", ""),
            "success": False,
            "screenshot_path": None,
            "modals": []
        }
        
        try:
            # Navigate to the page
            page_url = page_config.get("url", "")
            if not page_url:
                logger.error(f"Cannot process page '{results['page_name']}': URL not specified")
                return results
                
            navigation_success = await self.navigate_to_url(page_url)
            if not navigation_success:
                logger.error(f"Failed to navigate to page: {page_url}")
                return results
                
            # Take a screenshot of the main page
            screenshot_path = await self.take_screenshot(results["page_name"])
            results["screenshot_path"] = screenshot_path
            results["success"] = screenshot_path is not None
            
            # Process modals if defined in config
            modals = page_config.get("modals", [])
            if modals:
                for modal_config in modals:
                    modal_result = await self.process_modal(modal_config)
                    results["modals"].append(modal_result)
                    
                    # Re-navigate to the page after processing each modal
                    # This ensures we start from a clean state for each modal
                    await self.navigate_to_url(page_url)
            else:
                # Auto-discover and process modals
                modal_results = await self.discover_and_process_modals()
                results["modals"].extend(modal_results)
                # Re-navigate to the page to clean up any open modals
                await self.navigate_to_url(page_url)
                
            return results
            
        except Exception as e:
            logger.error(f"Error processing page {results['page_name']}: {e}")
            return results
    
    async def discover_and_process_modals(self) -> List[Dict[str, Any]]:
        """
        Automatically discover and process modals on the current page
        
        Returns:
            List[Dict[str, Any]]: Results for each modal discovered and processed
        """
        modal_results = []
        
        if not self.page:
            logger.error("Cannot discover modals: browser page not initialized")
            return modal_results
            
        try:
            # First, look for common modal trigger elements
            logger.info("Discovering potential modal triggers")
            
            # Combine all modal trigger selectors
            combined_selector = ', '.join(MODAL_TRIGGER_SELECTORS)
            potential_triggers = await self.page.query_selector_all(combined_selector)
            
            if not potential_triggers:
                logger.info("No potential modal triggers found")
                return modal_results
                
            logger.info(f"Found {len(potential_triggers)} potential modal triggers")
            
            # Limit the number of modals to try (to avoid spending too much time)
            max_modals = 5
            trigger_count = min(len(potential_triggers), max_modals)
            
            # Store initial state of modal containers
            initial_modal_state = await self._check_modal_container_visibility()
            
            # Get the current URL to return to after each modal
            current_url = self.page.url
            
            # Try each potential trigger
            for i in range(trigger_count):
                # Get a fresh reference to the element for each attempt
                current_page_url = self.page.url
                triggers = await self.page.query_selector_all(combined_selector)
                
                if i >= len(triggers):
                    break
                    
                trigger = triggers[i]
                
                # Try to get some identifying information about the trigger
                try:
                    trigger_text = await trigger.text_content()
                    trigger_text = trigger_text.strip() if trigger_text else ""
                    
                    # Get element attributes that might help identify it
                    attr_map = {}
                    for attr in ['id', 'class', 'name', 'aria-label', 'title', 'data-testid']:
                        attr_value = await trigger.get_attribute(attr)
                        if attr_value:
                            attr_map[attr] = attr_value
                            
                    # Create a name for the modal from available attributes
                    modal_name = None
                    if trigger_text and len(trigger_text) < 30:
                        modal_name = f"Modal_{trigger_text}"
                    elif 'aria-label' in attr_map:
                        modal_name = f"Modal_{attr_map['aria-label']}"
                    elif 'title' in attr_map:
                        modal_name = f"Modal_{attr_map['title']}"
                    elif 'id' in attr_map:
                        modal_name = f"Modal_{attr_map['id']}"
                    else:
                        modal_name = f"Modal_{i+1}"
                        
                    # Clean the modal name
                    modal_name = "".join([c if c.isalnum() or c == '_' else '_' for c in modal_name])
                    modal_name = re.sub(r'_+', '_', modal_name)  # Replace consecutive underscores
                    
                    # Skip if we've already visited this modal
                    if modal_name in self.visited_modals:
                        continue
                        
                    logger.info(f"Attempting to open modal: {modal_name}")
                    
                    # Click the trigger
                    await trigger.click()
                    
                    # Wait for any animations
                    await asyncio.sleep(0.5)
                    
                    # Check if a modal appeared
                    current_modal_state = await self._check_modal_container_visibility()
                    modal_appeared = current_modal_state != initial_modal_state
                    url_changed = current_page_url != self.page.url
                    
                    if modal_appeared or url_changed:
                        logger.info(f"Modal or page change detected after clicking {modal_name}")
                        
                        # Take a screenshot of the modal
                        screenshot_path = await self.take_screenshot(modal_name, modal=True)
                        
                        if screenshot_path:
                            # Add to visited modals
                            self.visited_modals.add(modal_name)
                            
                            # Add to results
                            modal_result = {
                                "modal_name": modal_name,
                                "selector": f"Auto-discovered modal trigger #{i+1}",
                                "success": True,
                                "screenshot_path": screenshot_path
                            }
                            modal_results.append(modal_result)
                        
                        # Try to close the modal or navigate back
                        await self._close_modal_or_go_back(current_page_url)
                        
                except Exception as e:
                    logger.error(f"Error processing potential modal trigger #{i+1}: {e}")
                    # Navigate back to the original page
                    if self.page.url != current_url:
                        await self.page.goto(current_url)
                    continue
                    
            return modal_results
            
        except Exception as e:
            logger.error(f"Error discovering and processing modals: {e}")
            return modal_results
    
    async def _check_modal_container_visibility(self) -> bool:
        """
        Check if any modal containers are visible on the page
        
        Returns:
            bool: True if any modal containers are visible
        """
        try:
            # Combine all modal container selectors
            combined_selector = ', '.join(MODAL_CONTAINER_SELECTORS)
            modal_containers = await self.page.query_selector_all(combined_selector)
            
            for container in modal_containers:
                is_visible = await container.is_visible()
                if is_visible:
                    return True
                    
            return False
            
        except Exception:
            return False
    
    async def _close_modal_or_go_back(self, original_url: str) -> None:
        """
        Attempt to close a modal or navigate back to the original URL
        
        Args:
            original_url (str): The URL to return to if needed
        """
        try:
            # Try pressing Escape first
            await self.page.keyboard.press('Escape')
            await asyncio.sleep(0.3)
            
            # Check if modal is still visible
            modal_visible = await self._check_modal_container_visibility()
            
            if not modal_visible and self.page.url == original_url:
                # Modal closed successfully
                return
                
            # Try clicking common close buttons
            close_selectors = [
                '.modal-close', 
                '.close', 
                '[aria-label="Close"]',
                '[data-dismiss="modal"]',
                'button.close',
                '.modal button',
                '[class*="close"]',
                '[class*="cancel"]',
                'button:has([aria-label="close"])'
            ]
            
            for selector in close_selectors:
                try:
                    close_btn = await self.page.query_selector(selector)
                    if close_btn and await close_btn.is_visible():
                        await close_btn.click()
                        await asyncio.sleep(0.3)
                        
                        # Check if modal is still visible
                        modal_still_visible = await self._check_modal_container_visibility()
                        if not modal_still_visible and self.page.url == original_url:
                            # Modal closed successfully
                            return
                except Exception:
                    # Ignore errors for individual close attempts
                    pass
            
            # If the above didn't work, navigate back to the original URL
            if self.page.url != original_url:
                await self.page.goto(original_url)
                
        except Exception as e:
            logger.error(f"Error trying to close modal: {e}")
            # Last resort: try to navigate back to original URL
            try:
                await self.page.goto(original_url)
            except Exception:
                pass
    
    async def process_modal(self, modal_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a modal according to its configuration
        
        Args:
            modal_config (Dict[str, Any]): Configuration for the modal
            
        Returns:
            Dict[str, Any]: Results including screenshot and visited status
        """
        modal_name = modal_config.get("name", "Unknown Modal")
        selector = modal_config.get("selector", "")
        
        results = {
            "modal_name": modal_name,
            "selector": selector,
            "success": False,
            "screenshot_path": None
        }
        
        if not selector:
            logger.error(f"Cannot process modal '{modal_name}': selector not specified")
            return results
            
        try:
            # Click the element to open the modal
            click_success = await self.click_element(selector)
            if not click_success:
                logger.error(f"Failed to click element to open modal: {selector}")
                return results
                
            # Give the modal time to fully open
            stabilization_time = get('application.stabilization_time', 1000)
            await asyncio.sleep(stabilization_time / 1000 * 2)  # Extra time for modal animations
            
            # Take a screenshot of the modal
            screenshot_path = await self.take_screenshot(modal_name, modal=True)
            results["screenshot_path"] = screenshot_path
            results["success"] = screenshot_path is not None
            
            if results["success"]:
                self.visited_modals.add(modal_name)
                
            # Try to close the modal
            current_url = self.page.url
            await self._close_modal_or_go_back(current_url)
                
            return results
            
        except Exception as e:
            logger.error(f"Error processing modal {modal_name}: {e}")
            return results
    
    async def get_discovered_pages(self) -> List[str]:
        """
        Get a list of discovered pages that haven't been visited yet
        
        Returns:
            List[str]: List of page paths that could be visited
        """
        # Filter out already visited pages
        unvisited = [page for page in self.discovered_pages if page not in self.visited_pages]
        return unvisited[:10]  # Limit to 10 to avoid overwhelming
    
    async def auto_discover_and_test_pages(self, max_pages: int = 5) -> List[Dict[str, Any]]:
        """
        Automatically discover and test pages
        
        Args:
            max_pages (int): Maximum number of pages to discover and test
            
        Returns:
            List[Dict[str, Any]]: Results for each page discovered and tested
        """
        results = []
        
        # Get unvisited discovered pages
        unvisited_pages = await self.get_discovered_pages()
        
        # Limit the number of pages to test
        pages_to_test = unvisited_pages[:max_pages]
        
        logger.info(f"Auto-discovering and testing {len(pages_to_test)} pages")
        
        for i, page_path in enumerate(pages_to_test):
            # Create a simple page config
            page_name = page_path.replace('/', '_').strip('_')
            if not page_name:
                page_name = f"DiscoveredPage_{i+1}"
                
            page_config = {
                "name": page_name,
                "url": page_path
            }
            
            # Process the page
            page_result = await self.process_page(page_config)
            results.append(page_result)
            
        return results
    
    def get_visited_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about visited pages and modals
        
        Returns:
            Dict[str, Any]: Statistics about visited pages and modals
        """
        return {
            "pages_visited": len(self.visited_pages),
            "modals_visited": len(self.visited_modals),
            "pages": list(self.visited_pages),
            "modals": list(self.visited_modals),
            "pages_discovered": len(self.discovered_pages)
        }


# Async entry point for testing this module directly
async def main():
    """Main function for testing the browser module"""
    controller = BrowserController()
    try:
        await controller.setup()
        # Add your test code here
        await controller.wait_for_user_login("https://app.guesty.com")
        await asyncio.sleep(2)
        print("Taking screenshot...")
        await controller.take_screenshot("test_screenshot")
        
        # Test auto-discovery of modals
        modals = await controller.discover_and_process_modals()
        print(f"Discovered {len(modals)} modals")
        
        # Test auto-discovery of pages
        pages = await controller.get_discovered_pages()
        print(f"Discovered {len(pages)} pages")
        
    finally:
        await controller.teardown()

if __name__ == "__main__":
    asyncio.run(main()) 