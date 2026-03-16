#!/usr/bin/env python3
"""
Use Playwright to load each MapGeo property page and extract the
ViewpointCloud location ID from the "View Permits" link in the sidebar.
Saves results to vpc_locations.json: { "PARCEL_ID": VPC_LOCATION_ID, ... }
"""

import json
import time
import asyncio
from playwright.async_api import async_playwright

PROPERTIES = [
    # Area S — Peacock Farm Historic District
    ("2 Peacock Farm Rd", "8-82"),
    ("3 Peacock Farm Rd", "7-91C"),
    ("4 Peacock Farm Rd", "8-83"),
    ("6 Peacock Farm Rd", "8-84"),
    ("8 Peacock Farm Rd", "8-85"),
    ("9 Peacock Farm Rd", "8-94"),
    ("10 Peacock Farm Rd", "8-86"),
    ("12 Peacock Farm Rd", "8-87"),
    ("15 Peacock Farm Rd", "8-93"),
    ("17 Peacock Farm Rd", "7-89"),
    ("18 Peacock Farm Rd", "7-10"),
    ("19 Peacock Farm Rd", "7-88"),
    ("22 Peacock Farm Rd", "7-22"),
    ("23 Peacock Farm Rd", "7-87"),
    ("24 Peacock Farm Rd", "7-23"),
    ("25 Peacock Farm Rd", "7-86"),
    ("26 Peacock Farm Rd", "7-24"),
    ("27 Peacock Farm Rd", "7-85"),
    ("28 Peacock Farm Rd", "7-25"),
    ("29 Peacock Farm Rd", "7-84"),
    ("30 Peacock Farm Rd", "7-26"),
    ("31 Peacock Farm Rd", "7-83"),
    ("32 Peacock Farm Rd", "7-27"),
    ("33 Peacock Farm Rd", "7-82"),
    ("34 Peacock Farm Rd", "7-28"),
    ("35 Peacock Farm Rd", "7-81A"),
    ("37 Peacock Farm Rd", "7-80C"),
    ("38 Peacock Farm Rd", "7-29"),
    ("39 Peacock Farm Rd", "7-79A"),
    ("40 Peacock Farm Rd", "7-30"),
    ("41 Peacock Farm Rd", "7-78"),
    ("42 Peacock Farm Rd", "7-31"),
    ("43 Peacock Farm Rd", "7-76"),
    ("45 Peacock Farm Rd", "7-75"),
    ("46 Peacock Farm Rd", "7-37"),
    ("47 Peacock Farm Rd", "7-74"),
    ("48 Peacock Farm Rd", "7-38"),
    ("49 Peacock Farm Rd", "7-73"),
    ("50 Peacock Farm Rd", "7-39"),
    ("51 Peacock Farm Rd", "7-72"),
    ("52 Peacock Farm Rd", "7-40"),
    ("53 Peacock Farm Rd", "7-71"),
    ("1 Compton Cir", "7-36"),
    ("3 Compton Cir", "7-35"),
    ("4 Compton Cir", "7-32"),
    ("5 Compton Cir", "7-34"),
    ("6 Compton Cir", "7-33"),
    ("1 Mason St", "8-92"),
    ("2 Mason St", "8-88"),
    ("4 Mason St", "8-89"),
    ("5 Mason St", "8-91"),
    ("4 Trotting Horse Dr", "7-11"),
    ("6 Trotting Horse Dr", "7-12"),
    ("7 Trotting Horse Dr", "7-21"),
    ("8 Trotting Horse Dr", "7-13"),
    ("10 Trotting Horse Dr", "7-14"),
    ("11 Trotting Horse Dr", "7-20"),
    ("12 Trotting Horse Dr", "7-15"),
    ("14 Trotting Horse Dr", "7-16"),
    ("15 Trotting Horse Dr", "7-19"),
    ("16 Trotting Horse Dr", "7-17"),
    ("17 Trotting Horse Dr", "7-18"),
    # Area AK — Shaker Glen
    ("4 Fessenden Way", "53-49"),
    ("5 Fessenden Way", "53-45"),
    ("6 Fessenden Way", "53-50"),
    ("7 Fessenden Way", "53-44"),
    ("9 Fessenden Way", "53-43"),
    ("10 Fessenden Way", "53-56"),
    ("11 Fessenden Way", "53-42"),
    ("12 Fessenden Way", "53-57"),
    ("2 Marshall Rd", "53-40"),
    ("3 Marshall Rd", "53-64A"),
    ("4 Marshall Rd", "53-41"),
    ("5 Marshall Rd", "53-63"),
    ("7 Marshall Rd", "53-62"),
    ("8 Marshall Rd", "53-58"),
    ("9 Marshall Rd", "53-61"),
    ("10 Marshall Rd", "53-59"),
    ("11 Marshall Rd", "53-60"),
    ("2 Rogers Rd", "53-51"),
    ("3 Rogers Rd", "53-55"),
    ("4 Rogers Rd", "53-52"),
    ("5 Rogers Rd", "53-54"),
    ("6 Rogers Rd", "53-53"),
    ("3 Rolfe Rd", "53-47"),
    ("4 Rolfe Rd", "54-102"),
    ("6 Rolfe Rd", "54-103"),
    ("7 Rolfe Rd", "53-48"),
    ("1 Rolfe Rd", "53-31"),
    ("8 Rolfe Rd", "54-104"),
    # Area AL — The Grove
    ("2 Angier Rd", "77-164"),
    ("3 Angier Rd", "77-163"),
    ("4 Angier Rd", "77-165"),
    ("5 Angier Rd", "77-162"),
    ("6 Angier Rd", "77-166"),
    ("7 Angier Rd", "77-161"),
    ("8 Angier Rd", "82-93"),
    ("10 Angier Rd", "82-92"),
    ("11 Angier Rd", "77-160"),
    ("2 Diamond Rd", "77-142"),
    ("3 Diamond Rd", "77-172"),
    ("5 Diamond Rd", "77-171"),
    ("7 Diamond Rd", "77-170"),
    ("8 Diamond Rd", "77-178"),
    ("9 Diamond Rd", "77-169"),
    ("10 Diamond Rd", "77-179"),
    ("11 Diamond Rd", "77-168"),
    ("12 Diamond Rd", "82-99"),
    ("15 Diamond Rd", "82-98"),
    ("16 Diamond Rd", "82-100"),
    ("17 Diamond Rd", "82-97"),
    ("18 Diamond Rd", "82-101A"),
    ("351 North Emerson Rd", "82-83B"),
    ("352 North Emerson Rd", "77-159"),
    ("353 North Emerson Rd", "82-91"),
    ("355 North Emerson Rd", "82-90"),
    ("357 North Emerson Rd", "82-89"),
    ("358 North Emerson Rd", "82-94"),
    ("359 North Emerson Rd", "82-88"),
    ("360 North Emerson Rd", "82-95"),
    ("361 North Emerson Rd", "82-87"),
    ("362 North Emerson Rd", "82-96"),
    ("363 North Emerson Rd", "82-86"),
    ("365 North Emerson Rd", "82-85"),
    ("2 White Ter", "77-173"),
    ("3 White Ter", "77-177"),
    ("4 White Ter", "77-174"),
    ("5 White Ter", "77-176"),
    ("7 White Ter", "77-175"),
    ("5 Grove St", "77-145"),
    ("11 Grove St", "77-144"),
    ("60 Burlington St", "77-91"),
    ("96 Burlington St", "77-146"),
    ("105 Burlington St", "77-38"),
    # Area AM — Rumford Road
    ("4 Rumford Rd", "46-16"),
    ("5 Rumford Rd", "46-18"),
    ("6 Rumford Rd", "46-17"),
    ("7 Rumford Rd", "54-123"),
    ("8 Rumford Rd", "54-128"),
    ("9 Rumford Rd", "54-122"),
    ("10 Rumford Rd", "54-129"),
    ("11 Rumford Rd", "54-121"),
    ("12 Rumford Rd", "54-130"),
    ("13 Rumford Rd", "54-120"),
    ("14 Rumford Rd", "54-131"),
    ("15 Rumford Rd", "54-119"),
    ("16 Rumford Rd", "54-132"),
    ("17 Rumford Rd", "54-118"),
    ("2 Rumford Rd", "46-15"),
    # Area AN — Upper Turning Mill Road
    ("4 Turning Mill Rd", "82-32"),
    ("7 Turning Mill Rd", "82-79"),
    ("9 Turning Mill Rd", "82-78"),
    ("11 Turning Mill Rd", "82-77"),
    ("12 Turning Mill Rd", "82-45"),
    ("13 Turning Mill Rd", "82-76"),
    ("13A Turning Mill Rd", "82-53"),
    ("14 Turning Mill Rd", "82-46"),
    ("15 Turning Mill Rd", "82-52"),
    ("16 Turning Mill Rd", "82-47"),
    ("17 Turning Mill Rd", "82-51"),
    ("18 Turning Mill Rd", "82-48"),
    ("19 Turning Mill Rd", "82-50A"),
    ("20 Turning Mill Rd", "82-49"),
    ("21 Turning Mill Rd", "86-51A"),
    ("22 Turning Mill Rd", "86-52"),
    ("23 Turning Mill Rd", "86-50A"),
    ("24 Turning Mill Rd", "86-53"),
    ("25 Turning Mill Rd", "86-49A"),
    ("26 Turning Mill Rd", "86-54"),
    ("27 Turning Mill Rd", "86-48A"),
    ("28 Turning Mill Rd", "86-55"),
    ("29 Turning Mill Rd", "86-47"),
    ("30 Turning Mill Rd", "86-56"),
    ("31 Turning Mill Rd", "86-31"),
    ("32 Turning Mill Rd", "86-57"),
    ("34 Turning Mill Rd", "86-58"),
    ("36 Turning Mill Rd", "86-10"),
    ("38 Turning Mill Rd", "86-11"),
    ("39 Turning Mill Rd", "86-25"),
    ("40 Turning Mill Rd", "86-12"),
    ("41 Turning Mill Rd", "86-24"),
    ("45 Turning Mill Rd", "86-18A"),
    ("46 Turning Mill Rd", "86-16"),
    ("47 Turning Mill Rd", "89-31"),
    ("48 Turning Mill Rd", "86-17"),
    ("49 Turning Mill Rd", "89-30"),
    ("50 Turning Mill Rd", "89-33"),
    ("51 Turning Mill Rd", "89-29"),
    ("52 Turning Mill Rd", "89-34"),
    ("53 Turning Mill Rd", "89-28"),
    ("54 Turning Mill Rd", "89-35"),
    ("55 Turning Mill Rd", "89-27"),
    ("57 Turning Mill Rd", "89-26"),
    ("58 Turning Mill Rd", "89-37"),
    ("59 Turning Mill Rd", "89-25"),
    ("60 Turning Mill Rd", "89-38"),
    ("61 Turning Mill Rd", "89-24"),
    ("62 Turning Mill Rd", "89-39"),
    ("64 Turning Mill Rd", "89-40"),
    ("65 Turning Mill Rd", "89-23"),
    ("5 Dewey Rd", "89-14"),
    ("8 Dewey Rd", "89-41"),
    ("10 Dewey Rd", "89-42"),
    ("14 Dewey Rd", "89-43"),
    ("15 Dewey Rd", "89-46"),
    ("16 Dewey Rd", "89-44"),
    ("3 Gould Rd", "89-51"),
    ("4 Gould Rd", "89-12"),
    ("5 Gould Rd", "89-50"),
    ("7 Gould Rd", "89-49"),
    ("8 Gould Rd", "89-19"),
    ("9 Gould Rd", "89-48"),
    ("10 Gould Rd", "89-20"),
    ("2 Grimes Rd", "86-20A"),
    ("4 Grimes Rd", "86-21"),
    ("5 Grimes Rd", "86-22"),
    # Area BA — Pleasant Brook
    ("6 Mason St", "8-155"),
    ("7 Mason St", "8-153"),
    ("8 Mason St", "8-156"),
    ("9 Mason St", "8-154"),
    ("11 Mason St", "14-139"),
    ("15 Mason St", "14-140"),
    ("17 Mason St", "14-145"),
    ("18 Mason St", "14-138"),
    ("19 Mason St", "14-144"),
    ("20 Mason St", "14-137"),
    ("21 Mason St", "14-143A"),
    ("22 Mason St", "14-136"),
    ("23 Mason St", "14-149"),
    ("24 Mason St", "14-135"),
    ("25 Mason St", "14-148"),
    ("26 Mason St", "14-134B"),
    ("27 Mason St", "14-147"),
    ("28 Mason St", "14-133B"),
    ("29 Mason St", "14-146"),
    ("1 White Pine Ln", "14-129"),
    ("2 White Pine Ln", "8-157"),
    ("3 White Pine Ln", "14-130"),
    ("4 White Pine Ln", "8-158"),
    ("5 White Pine Ln", "14-131"),
    ("6 White Pine Ln", "8-159"),
    ("7 White Pine Ln", "14-132A"),
    ("8 White Pine Ln", "8-160"),
    ("9 White Pine Ln", "8-162A"),
    ("10 White Pine Ln", "8-161"),
    ("11 White Pine Ln", "8-163C"),
    ("12 White Pine Ln", "8-164"),
    ("13 White Pine Ln", "8-163B"),
    ("14 White Pine Ln", "8-165"),
    ("64 Pleasant St", "14-56C"),
]

OUTPUT_FILE = "vpc_locations.json"


async def get_vpc_location_id(page, parcel_id):
    """Load MapGeo page for parcel and extract ViewpointCloud location ID."""
    url = f"https://lexingtonma.mapgeo.io/datasets/properties?previewId={parcel_id}"
    try:
        await page.goto(url, wait_until="networkidle", timeout=30000)
        # Wait for the sidebar panel with the permits link
        await page.wait_for_selector("a[href*='viewpointcloud.com/locations/']", timeout=15000)
        link = await page.get_attribute("a[href*='viewpointcloud.com/locations/']", "href")
        if link:
            loc_id = link.rstrip("/").split("/")[-1]
            return int(loc_id)
    except Exception:
        pass
    return None


async def main():
    # Load existing results if any
    try:
        with open(OUTPUT_FILE) as f:
            results = json.load(f)
        print(f"Resuming — already have {len(results)} entries")
    except FileNotFoundError:
        results = {}

    total = len(PROPERTIES)
    ok = 0
    failed = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Accept the MapGeo disclaimer once
        await page.goto("https://lexingtonma.mapgeo.io", wait_until="networkidle", timeout=20000)
        try:
            await page.click("button:has-text('Accept')", timeout=5000)
        except Exception:
            pass

        for i, (addr, parcel) in enumerate(PROPERTIES, 1):
            if parcel in results:
                print(f"  [{i:3}/{total}] SKIP  {addr} (loc_id={results[parcel]})")
                ok += 1
                continue

            loc_id = await get_vpc_location_id(page, parcel)
            if loc_id:
                results[parcel] = loc_id
                print(f"  [{i:3}/{total}] OK    {addr} → {loc_id}")
                ok += 1
                # Save after every successful lookup
                with open(OUTPUT_FILE, "w") as f:
                    json.dump(results, f, indent=2)
            else:
                print(f"  [{i:3}/{total}] ERR   {addr} (not found)")
                failed.append((addr, parcel))

            await asyncio.sleep(0.5)

        await browser.close()

    print(f"\nDone. Found: {ok}  Failed: {len(failed)}")
    if failed:
        print("Failed properties:")
        for addr, parcel in failed:
            print(f"  {addr} ({parcel})")
    print(f"Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    asyncio.run(main())
