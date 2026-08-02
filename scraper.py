import json
import csv
from playwright.sync_api import sync_playwright


WEBSITES = [
    "https://www.ideo.com",
    
     
]


def clean(text):
    if not text:
        return ""
    return " ".join(text.split())


def extract_services(page):

    services = []

    keywords = [
        "Design",
        "Research",
        "Innovation",
        "Strategy",
        "AI",
        "Engineering",
        "Experience",
        "Brand",
        "Digital",
        "Technology",
        "Product"
    ]

    body = page.locator("body").inner_text()

    for word in keywords:
        if word.lower() in body.lower():
            services.append(word)

    return sorted(list(set(services)))


def scrape_company(page, url):

    page.goto(url, wait_until="networkidle")

    title = ""

    try:
        title = clean(page.title())
    except:
        pass

    description = ""

    try:
        description = page.locator(
            'meta[name="description"]'
        ).get_attribute("content")
        description = clean(description)
    except:
        pass

    headings = []

    try:
        h = page.locator("h1,h2,h3").all_inner_texts()

        headings = [clean(x) for x in h[:10]]
    except:
        pass

    links = page.locator("a").evaluate_all(
        """
        elements => elements.map(e => e.href)
        """
    )

    linkedin = ""
    careers = ""
    contact = ""

    for link in links:

        l = link.lower()

        if "linkedin" in l and not linkedin:
            linkedin = link

        if "career" in l or "jobs" in l:
            careers = link

        if "contact" in l:
            contact = link

    company = url.replace("https://", "").replace("www.", "").split(".")[0].title()

    return {

        "Company": company,

        "Website": url,

        "Page Title": title,

        "Description": description,

        "Top Headings": headings,

        "Detected Services": extract_services(page),

        "LinkedIn": linkedin,

        "Careers": careers,

        "Contact Page": contact
    }


def save_json(data):

    with open("competitor_data.json", "w", encoding="utf-8") as f:

        json.dump(data, f, indent=4, ensure_ascii=False)


def save_csv(data):

    fields = list(data[0].keys())

    with open(
        "competitor_data.csv",
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.DictWriter(f, fieldnames=fields)

        writer.writeheader()

        for row in data:

            row = row.copy()

            row["Top Headings"] = ", ".join(row["Top Headings"])

            row["Detected Services"] = ", ".join(row["Detected Services"])

            writer.writerow(row)


def main():

    results = []

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        for website in WEBSITES:

            print(f"\nScraping {website}...")

            try:

                data = scrape_company(page, website)

                results.append(data)

                print("Completed")

            except Exception as e:

                print("Error:", e)

        browser.close()

    save_json(results)

    save_csv(results)

    print("\nDone!")
    print("JSON -> competitor_data.json")
    print("CSV  -> competitor_data.csv")


if __name__ == "__main__":
    main()