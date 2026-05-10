import requests
from bs4 import BeautifulSoup
import psycopg2
import time

# ==============================
# CONFIG — তোমার DB info দাও
# ==============================
DB_CONFIG = {
    "dbname": "smart_hub_db",
    "user": "postgres",
    "password": "123456",  # ← তোমার password দাও
    "host": "localhost",
    "port": "5432"
}
AUTHOR_ID = 3  # ← তোমার faculty user এর id

HEADERS = {"User-Agent": "Mozilla/5.0"}

# ==============================
# HELPER
# ==============================
def fetch(url):
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        return BeautifulSoup(res.text, "html.parser")
    except Exception as e:
        print(f"  ❌ Fetch error: {url} — {e}")
        return None

def detect_category(title):
    t = title.lower()
    if any(w in t for w in ["exam", "examination", "midterm", "final", "makeup"]):
        return "exam"
    elif any(w in t for w in ["holiday", "eid", "closure", "vacation", "election"]):
        return "holiday"
    elif any(w in t for w in ["event", "seminar", "workshop", "lecture", "reunion", "congratulation"]):
        return "event"
    elif any(w in t for w in ["assignment", "submission", "deadline"]):
        return "assignment"
    else:
        return "general"

def detect_department(title):
    t = title.lower()
    if "cse" in t:
        return "Computer Science & Engineering"
    elif "bba" in t or "mba" in t:
        return "Business Administration"
    else:
        return "all"

# ==============================
# 1. SCRAPE NOTICES
# ==============================
NOTICE_URLS = [
    "https://cust.edu.bd/midterm-examination-schedule-for-cse-program-sprung-2026/",
    "https://cust.edu.bd/midterm-examination-schedule-for-bba-program-sprung-2026/",
    "https://cust.edu.bd/final-examination-schedule-for-mba-program-spring-2025/",
    "https://cust.edu.bd/revised-eid-ul-fitr-holiday-and-govt-declared-notice-for-university-closure/",
    "https://cust.edu.bd/holidays-for-shab-e-qadr-jumatul-widha-eid-ul-fitr-and-independence-day-2026/",
    "https://cust.edu.bd/makeup-examination-schedule-for-cse-program-fall-2025/",
    "https://cust.edu.bd/makeup-examination-schedule-for-bba-program-fall-2025/",
    "https://cust.edu.bd/holiday-notice-for-13-national-parliamentary-election-referendum/",
    "https://cust.edu.bd/makeup-examination-notice-for-cse-bba-program-fall-2025/",
    "https://cust.edu.bd/final-examination-schedule-for-bba-program-fall-2025/",
]

def scrape_notices(conn):
    print("\n📋 NOTICES scraping শুরু...")
    cur = conn.cursor()
    success = 0

    for url in NOTICE_URLS:
        soup = fetch(url)
        if not soup:
            continue

        title_tag = soup.find("h1") or soup.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        content = soup.find("div", class_="entry-content") or soup.find("article")
        if content:
            for tag in content.find_all(["nav", "footer", "script", "style"]):
                tag.decompose()
            lines = [l.strip() for l in content.get_text(separator="\n").splitlines() if l.strip()]
            body = "\n".join(lines[:60])
        else:
            body = title

        category = detect_category(title)
        department = detect_department(title)
        is_pinned = "exam" in category

        try:
            cur.execute("""
                INSERT INTO notices (author_id, title, body, category, department, is_pinned)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (AUTHOR_ID, title[:200], body[:3000], category, department, is_pinned))
            conn.commit()
            print(f"  ✅ {title[:60]}...")
            success += 1
        except Exception as e:
            conn.rollback()
            print(f"  ❌ Insert error: {e}")

        time.sleep(1)

    cur.close()
    print(f"  → {success}/{len(NOTICE_URLS)} notices inserted")


# ==============================
# 2. SCRAPE FACULTY → notices table এ "general" notice হিসেবে
# ==============================
def scrape_faculty(conn):
    print("\n👨‍🏫 FACULTY scraping শুরু...")
    soup = fetch("https://cust.edu.bd/academic/faculty-members/")
    if not soup:
        return

    cur = conn.cursor()
    success = 0

    # Find all faculty member cards
    members = soup.find_all("div", class_="team-member") or soup.find_all("article")

    # fallback: find by h3 tags with links
    faculty_list = []
    current_dept = "Computer Science & Engineering"

    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(strip=True)
        if "Computer Science" in text:
            current_dept = "Computer Science & Engineering"
        elif "Business Administration" in text:
            current_dept = "Business Administration"
        elif tag.name == "h3" and tag.find("a"):
            name = tag.get_text(strip=True)
            designation_tag = tag.find_next("h4")
            designation = designation_tag.get_text(strip=True) if designation_tag else "Faculty"
            faculty_list.append({
                "name": name,
                "designation": designation,
                "department": current_dept
            })

    # Insert as notices
    for f in faculty_list:
        title = f"Faculty Profile: {f['name']}"
        body = f"Name: {f['name']}\nDesignation: {f['designation']}\nDepartment: {f['department']}\n\nDepartment of {f['department']}, Central University of Science and Technology (CUST)."
        try:
            cur.execute("""
                INSERT INTO notices (author_id, title, body, category, department, is_pinned)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (AUTHOR_ID, title, body, "general", f["department"], False))
            conn.commit()
            print(f"  ✅ {f['name']} — {f['designation']}")
            success += 1
        except Exception as e:
            conn.rollback()
            print(f"  ❌ {e}")

    cur.close()
    print(f"  → {success} faculty profiles inserted")


# ==============================
# 3. SCRAPE NEWS & EVENTS
# ==============================
NEWS_URLS = [
    "https://cust.edu.bd/cust-and-university-of-wolverhampton-forge-strategic-tne-partnership-students-and-alumni-celebrate-historic-first-reunion/",
    "https://cust.edu.bd/meeting-with-education-minister-on-tne-expansion/",
    "https://cust.edu.bd/md-zahidul-islam-to-keynote-at-the-16th-world-leaders-summit-2026/",
    "https://cust.edu.bd/heartiest-congratulations/",
    "https://cust.edu.bd/international-recognition-for-cust-chairman/",
]

def scrape_news(conn):
    print("\n📰 NEWS & EVENTS scraping শুরু...")
    cur = conn.cursor()
    success = 0

    for url in NEWS_URLS:
        soup = fetch(url)
        if not soup:
            continue

        title_tag = soup.find("h1") or soup.find("h2")
        title = title_tag.get_text(strip=True) if title_tag else "Untitled"

        content = soup.find("div", class_="entry-content") or soup.find("article")
        if content:
            for tag in content.find_all(["nav", "footer", "script", "style"]):
                tag.decompose()
            lines = [l.strip() for l in content.get_text(separator="\n").splitlines() if l.strip()]
            body = "\n".join(lines[:60])
        else:
            body = title

        try:
            cur.execute("""
                INSERT INTO notices (author_id, title, body, category, department, is_pinned)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (AUTHOR_ID, title[:200], body[:3000], "event", "all", False))
            conn.commit()
            print(f"  ✅ {title[:60]}...")
            success += 1
        except Exception as e:
            conn.rollback()
            print(f"  ❌ {e}")

        time.sleep(1)

    cur.close()
    print(f"  → {success}/{len(NEWS_URLS)} news inserted")


# ==============================
# 4. EXTRA DEMO NOTICES (CSE specific)
# ==============================
def insert_demo_notices(conn):
    print("\n🎓 CSE DEMO NOTICES inserting...")
    cur = conn.cursor()

    demo = [
        ("Project Defense Schedule — CSE Spring 2026",
         "The final project defense for 4th year B.Sc CSE students will be held from June 20–25, 2026. Students must submit their project report by June 15. Defense venue: Lab 301, 3rd Floor. Each group will be allotted 20 minutes for presentation and 10 minutes for Q&A.",
         "exam", "Computer Science & Engineering", True),

        ("Class Suspension Notice — May 12, 2026",
         "All classes of the CSE department will remain suspended on May 12, 2026 due to departmental seminar. Students are requested to attend the seminar at the university auditorium at 10:00 AM.",
         "general", "Computer Science & Engineering", False),

        ("Assignment Deadline Extended — Data Structures",
         "The submission deadline for the Data Structures (CSE 2101) assignment has been extended to May 18, 2026. Students must submit via the Smart Hub Resource Portal. Late submissions will not be accepted.",
         "assignment", "Computer Science & Engineering", False),

        ("Lab Booking System Update",
         "The Computer Lab (Lab 201 and Lab 202) booking system has been updated. Students can now book lab time through the department admin. Maximum booking duration is 2 hours per group per day.",
         "general", "Computer Science & Engineering", False),

        ("Scholarship Application Open — Spring 2026",
         "Applications for the CUST Merit Scholarship for Spring 2026 are now open. Eligible students (CGPA 3.5 and above) can apply through the admission office by May 25, 2026. Required documents: transcript, recommendation letter.",
         "general", "all", True),
    ]

    success = 0
    for title, body, category, department, is_pinned in demo:
        try:
            cur.execute("""
                INSERT INTO notices (author_id, title, body, category, department, is_pinned)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (AUTHOR_ID, title, body, category, department, is_pinned))
            conn.commit()
            print(f"  ✅ {title[:60]}")
            success += 1
        except Exception as e:
            conn.rollback()
            print(f"  ❌ {e}")

    cur.close()
    print(f"  → {success} demo notices inserted")


# ==============================
# MAIN
# ==============================
def main():
    print("=" * 55)
    print("  CUST Full Data Scraper")
    print("=" * 55)

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ DB connection failed: {e}")
        print("DB_CONFIG এ password ঠিক করো!")
        return

    scrape_notices(conn)
    scrape_faculty(conn)
    scrape_news(conn)
    insert_demo_notices(conn)

    conn.close()

    print("\n" + "=" * 55)
    print("✅ সব done! Frontend এ Notice Board refresh করো।")
    print("=" * 55)

if __name__ == "__main__":
    main()