#!/usr/bin/env python3
"""
KTU Syllabus PDF Scraper & Downloader
Commit this script to your GitHub repository!

This script uses Playwright to automate the APJ Abdul Kalam Technological University (KTU) website,
locates the B.Tech scheme (default: 2024 Scheme), scans all available branches, detects if a syllabus 
PDF is uploaded, and downloads it.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python scrape_syllabus.py --scheme "B.TECH FULL TIME 2024 SCHEME" --outdir "./raw_pdfs"
"""

import asyncio
import os
import argparse
import json
import sys
from playwright.async_api import async_playwright

async def scrape_ktu_syllabi(scheme_name, out_dir, headless, max_branches):
    os.makedirs(out_dir, exist_ok=True)
    
    print(f"Starting KTU Scraper for scheme: '{scheme_name}'")
    print(f"Output directory: '{out_dir}'")
    
    async with async_playwright() as p:
        print("Launching Chromium browser...")
        browser = await p.chromium.launch(headless=headless)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # 1. Load the schemes page
        print("Navigating to KTU Academics Scheme page...")
        await page.goto("https://ktu.edu.in/academics/scheme", wait_until="networkidle", timeout=60000)
        
        # 2. Find and click the 'Branch' link for the targeted scheme
        print(f"Locating block for scheme: '{scheme_name}'...")
        clicked_branch = await page.evaluate("""(targetScheme) => {
            const elements = Array.from(document.querySelectorAll('*'));
            let targetCard = null;
            // Search for the element with the scheme name
            for (let el of elements) {
                if (el.innerText && el.innerText.toUpperCase().includes(targetScheme.toUpperCase())) {
                    if (!targetCard || el.innerText.length < targetCard.innerText.length) {
                        targetCard = el;
                    }
                }
            }
            if (targetCard) {
                let container = targetCard;
                // Go up to find the section/card container
                for (let i = 0; i < 5; i++) {
                    if (container.parentElement && (
                        container.className.includes('card') || 
                        container.className.includes('box') || 
                        container.className.includes('border') || 
                        container.className.includes('p-')
                    )) {
                        container = container.parentElement;
                        break;
                    }
                    if (container.parentElement) container = container.parentElement;
                }
                
                // Find 'Branch' button/link inside this container
                const branchLink = Array.from(container.querySelectorAll('a, button')).find(
                    a => a.innerText.trim() === 'Branch'
                );
                if (branchLink) {
                    branchLink.click();
                    return { success: true, message: "Clicked 'Branch' link." };
                }
                return { success: false, message: `Found card but no 'Branch' link inside container for ${targetScheme}` };
            }
            return { success: false, message: `Scheme card not found for ${targetScheme}` };
        }""", scheme_name)
        
        print("Navigation click result:", clicked_branch)
        if not clicked_branch["success"]:
            print(f"Error: {clicked_branch['message']}", file=sys.stderr)
            await browser.close()
            return
            
        await page.wait_for_timeout(5000)
        print(f"Loaded branch page. Current URL: {page.url}")
        
        # 3. Detect and count all branches
        branches_list = await page.evaluate("""() => {
            const results = [];
            const rows = document.querySelectorAll('.border-bottom-dotted.p-b-10.p-t-5.row');
            rows.forEach((row, idx) => {
                const branchAnchor = row.querySelector('a.font-weight-bold');
                if (branchAnchor) {
                    results.push({
                        index: idx,
                        branchName: branchAnchor.innerText.trim()
                    });
                }
            });
            return results;
        }""")
        
        total_branches = len(branches_list)
        print(f"Discovered {total_branches} branches under this scheme.")
        
        if max_branches:
            branches_list = branches_list[:max_branches]
            print(f"Limiting scrape to first {len(branches_list)} branches (test run).")
            
        downloaded_summary = []
        
        # Helper to load branch page fresh if needed
        async def ensure_on_branch_page():
            if "/academics/branch" not in page.url:
                print("Not on branch page. Reloading branch list...")
                await page.goto("https://ktu.edu.in/academics/scheme", wait_until="networkidle", timeout=60000)
                
                # BUGFIX: Removed the 'f' string prefix and duplicate curly braces
                await page.evaluate("""(targetScheme) => {
                    const elements = Array.from(document.querySelectorAll('*'));
                    let targetCard = null;
                    for (let el of elements) {
                        if (el.innerText && el.innerText.toUpperCase().includes(targetScheme.toUpperCase())) {
                            if (!targetCard || el.innerText.length < targetCard.innerText.length) {
                                targetCard = el;
                            }
                        }
                    }
                    if (targetCard) {
                        let container = targetCard;
                        for (let i = 0; i < 5; i++) {
                            if (container.parentElement && (container.className.includes('card') || container.className.includes('box') || container.className.includes('border') || container.className.includes('p-'))) {
                                container = container.parentElement;
                                break;
                            }
                            if (container.parentElement) container = container.parentElement;
                        }
                        const branchLink = Array.from(container.querySelectorAll('a, button')).find(a => a.innerText.trim() === 'Branch');
                        if (branchLink) branchLink.click();
                    }
                }""", scheme_name)
                await page.wait_for_timeout(5000)
        
        # 4. Loop through branches and download available PDFs
        for b in branches_list:
            idx = b["index"]
            b_name = b["branchName"]
            
            await ensure_on_branch_page()
            
            print(f"\n--- [{idx+1}/{total_branches}] Checking branch: {b_name} ---")
            
            # Click on 'Syllabus' link for this specific branch
            clicked_syl = await page.evaluate("""(rowIdx) => {
                const rows = document.querySelectorAll('.border-bottom-dotted.p-b-10.p-t-5.row');
                if (rows.length > rowIdx) {
                    const btn = Array.from(rows[rowIdx].querySelectorAll('a, button, [role="button"]')).find(
                        el => el.innerText.trim() === 'Syllabus'
                    );
                    if (btn) {
                        btn.click();
                        return true;
                    }
                }
                return false;
            }""", idx)
            
            if not clicked_syl:
                print(f"  [Skip] No syllabus button found in row {idx+1}")
                continue
                
            await page.wait_for_timeout(3500)
            
            # Check if syllabus download button is present
            has_syllabus_btn = await page.evaluate("""() => {
                const btns = Array.from(document.querySelectorAll('button')).filter(btn => {
                    const text = btn.innerText ? btn.innerText.trim() : '';
                    return text === 'Syllabus' && btn.className.includes('btn-hover-blue');
                });
                return btns.length > 0;
            }""")
            
            if not has_syllabus_btn:
                print(f"  [Skip] No syllabus PDF file uploaded on page for this branch.")
                await page.go_back()
                await page.wait_for_timeout(1500)
                continue
                
            # Perform download
            print("  Syllabus PDF detected! Starting download...")
            try:
                async with page.expect_download(timeout=15000) as download_info:
                    await page.evaluate("""() => {
                        const btns = Array.from(document.querySelectorAll('button')).filter(btn => {
                            const text = btn.innerText ? btn.innerText.trim() : '';
                            return text === 'Syllabus' && btn.className.includes('btn-hover-blue');
                        });
                        if (btns.length > 0) {
                            btns[0].click();
                        }
                    }""")
                    
                download = await download_info.value
                suggested_fn = download.suggested_filename
                
                # Make filename safe and save
                out_path = os.path.join(out_dir, suggested_fn)
                await download.save_as(out_path)
                
                size = os.path.getsize(out_path)
                print(f"  [SUCCESS] Saved PDF to {out_path} ({size} bytes)")
                
                downloaded_summary.append({
                    "branch_name": b_name,
                    "filename": suggested_fn,
                    "local_path": out_path,
                    "file_size": size
                })
                
            except Exception as e:
                print(f"  [ERROR] Failed downloading syllabus for {b_name}: {e}")
                
            # Go back to branch list
            print("  Returning to branch page...")
            await page.go_back()
            await page.wait_for_timeout(2000)
            
        # 5. Output summary
        summary_path = os.path.join(out_dir, "downloaded_syllabi.json")
        with open(summary_path, "w") as jf:
            json.dump(downloaded_summary, jf, indent=2)
            
        print("\n" + "="*40)
        print("Syllabus scraping completed!")
        print(f"Successfully downloaded {len(downloaded_summary)} files.")
        print(f"Summary written to: {summary_path}")
        print("="*40)
        
        await browser.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KTU Website Playwright Syllabus Scraper")
    parser.add_argument("--scheme", default="B.TECH FULL TIME 2024 SCHEME", help="Target scheme name to scrape (e.g. B.TECH FULL TIME 2024 SCHEME)")
    parser.add_argument("--outdir", default="./raw_pdfs", help="Directory where raw syllabus PDFs should be downloaded")
    parser.add_argument("--headless", type=bool, default=True, help="Run browser in headless mode")
    parser.add_argument("--max-branches", type=int, default=None, help="Limit number of branches to scrape for testing")
    
    args = parser.parse_args()
    
    # Run the async loop
    asyncio.run(scrape_ktu_syllabi(
        scheme_name=args.scheme,
        out_dir=args.outdir,
        headless=args.headless,
        max_branches=args.max_branches
    ))
