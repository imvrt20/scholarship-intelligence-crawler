# ============================================
# SCHOLARSHIP INFORMATION EXTRACTOR - v6
# ============================================

import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup


# ============================================
# BASIC CLEANING
# ============================================

def clean_text(text):
    if not text:
        return None

    text = str(text)
    text = text.replace("\xa0", " ")

    # Remove excessive spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip(" :-|,.;")


def normalize_text(text):
    if not text:
        return ""

    text = str(text)
    text = text.replace("\xa0", " ")

    # Normalize new lines but DON'T destroy punctuation
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n+", "\n", text)

    return text.strip()


# ============================================
# REMOVE COMMON WEBSITE GARBAGE
# ============================================

def clean_navigation(text):

    if not text:
        return ""

    lines = text.splitlines()

    useful_lines = []

    garbage = {
        "home",
        "about us",
        "contact us",
        "search",
        "toggle navigation",
        "menu",
        "navigation",
        "login",
        "register",
        "jobs",
        "tenders",
        "faqs",
    }

    for line in lines:

        line_clean = line.strip()

        if not line_clean:
            continue

        if line_clean.lower() in garbage:
            continue

        useful_lines.append(line_clean)

    return "\n".join(useful_lines)


# ============================================
# REGEX HELPER
# ============================================

def first_match(text, patterns):

    if not text:
        return None

    for pattern in patterns:

        try:

            match = re.search(
                pattern,
                text,
                re.IGNORECASE
            )

            if match:

                value = (
                    match.group(1)
                    if match.lastindex
                    else match.group(0)
                )

                value = clean_text(value)

                if value:
                    return value

        except re.error:
            continue

    return None


# ============================================
# URL EXTRACTION
# ============================================

def find_urls(text):

    if not text:
        return []

    urls = re.findall(
        r"https?://[^\s<>'\"]+",
        text
    )

    result = []

    for url in urls:

        url = url.rstrip(
            ".,);]}>\"'"
        )

        if url not in result:
            result.append(url)

    return result


# ============================================
# APPLICATION URL
# ============================================

def find_application_url(text, source_url=None):

    urls = find_urls(text)

    keywords = (
        "apply",
        "application",
        "registration",
        "register",
        "scholarship",
        "portal",
        "nsp"
    )

    for url in urls:

        lower = url.lower()

        if any(
            keyword in lower
            for keyword in keywords
        ):
            return url

    return source_url


# ============================================
# SCHOLARSHIP NAME
# ============================================

def extract_name(text):

    if not text:
        return "Not specified"

    patterns = [

        r"(?:scholarship\s+name|name\s+of\s+the\s+scholarship)"
        r"\s*[:\-]\s*([^\n]{5,200})",

        r"(?:scheme\s+name|name\s+of\s+the\s+scheme)"
        r"\s*[:\-]\s*([^\n]{5,200})",

        r"(?:title)"
        r"\s*[:\-]\s*([^\n]{5,200})",

        r"([A-Z][A-Za-z0-9&(),.'\- ]{5,150}"
        r"\s+(?:Scholarship|Scheme))",
    ]

    result = first_match(text, patterns)

    if result:

        result = clean_text(result)

        # Don't accept obvious navigation garbage
        bad_words = [
            "home",
            "contact",
            "login",
            "register",
            "search",
            "menu"
        ]

        if not any(
            word in result.lower()
            for word in bad_words
        ):
            return result[:180]

    return "Not specified"


# ============================================
# PROVIDER
# ============================================

def extract_provider(text):

    if not text:
        return "Not specified"

    patterns = [

        r"(?:provider|provided\s+by|offered\s+by|"
        r"awarded\s+by|sponsored\s+by|funded\s+by|"
        r"administered\s+by)"
        r"\s*[:\-]?\s*([^\n]{3,180})",

        r"(Government of India)",

        r"(Government of [A-Za-z ]+)",

        r"(Ministry of [A-Za-z &,\-]+)",

        r"(University Grants Commission)",

        r"(Ministry of Electronics and Information Technology)",
    ]

    result = first_match(text, patterns)

    if result:

        result = clean_text(result)

        if len(result) <= 180:
            return result

    return "Not specified"


# ============================================
# AMOUNT
# ============================================

def extract_amount(text):

    if not text:
        return None

    currency = r"(?:₹|Rs\.?|INR)"

    # Supports:
    # 50,000
    # 50000
    # 1,50,000
    number = r"\d{1,3}(?:,\d{2,3})*|\d+"

    patterns = [

        rf"(?:scholarship\s+amount|"
        rf"amount\s+of\s+scholarship|"
        rf"award\s+amount|"
        rf"financial\s+assistance|"
        rf"financial\s+benefit|"
        rf"stipend)"
        rf"\s*(?:is|of|up\s+to|:|-)?\s*"
        rf"({currency}\s*{number})",

        rf"({currency}\s*{number})"
        rf"\s*(?:per\s+(?:year|annum|month)|annually|monthly)?",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE
        )

        if not match:
            continue

        value = clean_text(match.group(1))

        digits = re.sub(
            r"[^\d]",
            "",
            value
        )

        if not digits:
            continue

        amount = int(digits)

        # Reject obvious garbage
        if amount < 500:
            continue

        if amount > 10000000:
            continue

        return f"₹{amount:,}"

    return None


# ============================================
# ELIGIBILITY
# ============================================

def extract_eligibility(text):

    if not text:
        return None

    patterns = [

        r"(?:eligibility\s+criteria)"
        r"\s*[:\-]?\s*"
        r"(.{30,1000}?)(?="
        r"\n(?:application|deadline|last\s+date|"
        r"documents|amount|scholarship\s+amount|"
        r"how\s+to\s+apply)"
        r"|$)",

        r"(?:who\s+can\s+apply)"
        r"\s*[:\-]?\s*"
        r"(.{30,1000}?)(?="
        r"\n(?:application|deadline|last\s+date|"
        r"documents|amount)"
        r"|$)",
    ]

    result = first_match(text, patterns)

    if not result:
        return None

    result = clean_text(result)

    return result[:800]


# ============================================
# ACADEMIC REQUIREMENTS
# ============================================

def extract_academic_requirements(text):

    if not text:
        return None

    patterns = [

        r"(?:minimum\s+marks)"
        r"\s*[:\-]?\s*([^\n]{5,200})",

        r"(?:minimum\s+percentage)"
        r"\s*[:\-]?\s*([^\n]{5,200})",

        r"(\d{1,3}\s*%\s*"
        r"(?:or\s+above|minimum|required)?)"
    ]

    return first_match(
        text,
        patterns
    )


# ============================================
# COURSE LEVEL
# ============================================

def extract_course_level(text):

    if not text:
        return None

    levels = []

    patterns = {
        "Undergraduate":
            r"\bundergraduate\b|\bUG\b",

        "Postgraduate":
            r"\bpostgraduate\b|\bpost graduate\b|\bPG\b",

        "PhD":
            r"\bPh\.?\s*D\b|\bdoctoral\b",

        "Diploma":
            r"\bdiploma\b",

        "ITI":
            r"\bITI\b",

        "B.Tech":
            r"\bB\.?\s*Tech\b",

        "M.Tech":
            r"\bM\.?\s*Tech\b",

        "MBA":
            r"\bMBA\b",

        "MCA":
            r"\bMCA\b",

        "BCA":
            r"\bBCA\b"
    }

    for name, pattern in patterns.items():

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            levels.append(name)

    if levels:
        return ", ".join(
            dict.fromkeys(levels)
        )

    return None


# ============================================
# INCOME
# ============================================

def extract_income(text):

    if not text:
        return None

    patterns = [

        r"(?:annual\s+family\s+income|"
        r"family\s+income|"
        r"parental\s+income|"
        r"income\s+limit)"
        r"\s*(?:is|of|up\s+to|:|-)?\s*"
        r"((?:₹|Rs\.?|INR)?\s*[\d,]+)"
    ]

    result = first_match(
        text,
        patterns
    )

    if not result:
        return None

    digits = re.sub(
        r"[^\d]",
        "",
        result
    )

    if not digits:
        return None

    amount = int(digits)

    if amount >= 1000 and amount <= 100000000:
        return result

    return None


# ============================================
# AGE
# ============================================

def extract_age(text):

    if not text:
        return None

    patterns = [

        r"(?:age\s+limit|maximum\s+age|minimum\s+age)"
        r"\s*[:\-]?\s*([^\n.;]{3,100})",

        r"(\d{1,2}\s*(?:to|-)\s*\d{1,2}\s*years?)",

        r"(\d{1,2}\s*years?\s*"
        r"(?:or\s+above|or\s+below))"
    ]

    return first_match(
        text,
        patterns
    )


# ============================================
# GENDER
# ============================================

def extract_gender(text):

    if not text:
        return None

    genders = []

    if re.search(
        r"\bfemale\b|\bwomen\b|\bgirls\b",
        text,
        re.IGNORECASE
    ):
        genders.append("Female")

    if re.search(
        r"\bmale\b|\bmen\b|\bboys\b",
        text,
        re.IGNORECASE
    ):
        genders.append("Male")

    if genders:
        return ", ".join(
            dict.fromkeys(genders)
        )

    return None


# ============================================
# CATEGORY
# ============================================

def extract_category(text):

    if not text:
        return None

    categories = []

    patterns = {
        "SC": r"\bSC\b|Scheduled Caste",
        "ST": r"\bST\b|Scheduled Tribe",
        "OBC": r"\bOBC\b|Other Backward Classes",
        "EWS": r"\bEWS\b|Economically Weaker Section",
        "Minority": r"\bMinority\b",
    }

    for name, pattern in patterns.items():

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            categories.append(name)

    if categories:
        return ", ".join(
            dict.fromkeys(categories)
        )

    return None


# ============================================
# DOMICILE
# ============================================

def extract_domicile(text):

    if not text:
        return None

    patterns = [

        r"(?:state\s+domicile|domicile)"
        r"\s*[:\-]?\s*([A-Za-z][A-Za-z ,\-]{2,100})",

        r"(?:permanent\s+resident\s+of)"
        r"\s+([A-Za-z][A-Za-z ,\-]{2,100})"
    ]

    return first_match(
        text,
        patterns
    )


# ============================================
# INSTITUTION
# ============================================

def extract_institution(text):

    if not text:
        return None

    patterns = [

        r"(?:recognized\s+institution)"
        r"\s*[:\-]?\s*([^\n.;]{10,400})",

        r"(?:recognized\s+college)"
        r"\s*[:\-]?\s*([^\n.;]{10,400})",

        r"(?:recognized\s+university)"
        r"\s*[:\-]?\s*([^\n.;]{10,400})"
    ]

    result = first_match(
        text,
        patterns
    )

    if result:
        return clean_text(result)[:600]

    return None


# ============================================
# OPENING DATE
# ============================================

def extract_opening_date(text):

    if not text:
        return None

    patterns = [

        r"(?:opening\s+date|application\s+opens|"
        r"applications\s+open|start\s+date)"
        r"\s*[:\-]?\s*"
        r"([0-9A-Za-z ,/\-]{5,60})"
    ]

    return first_match(
        text,
        patterns
    )


# ============================================
# DEADLINE
# ============================================

def extract_deadline(text):

    if not text:
        return None

    patterns = [

        r"(?:application\s+deadline|"
        r"application\s+last\s+date|"
        r"last\s+date\s+to\s+apply|"
        r"last\s+date|deadline|closing\s+date)"
        r"\s*[:\-]?\s*"
        r"([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})",

        r"(?:application\s+deadline|"
        r"application\s+last\s+date|"
        r"last\s+date\s+to\s+apply|"
        r"last\s+date|deadline|closing\s+date)"
        r"\s*[:\-]?\s*"
        r"([0-9]{1,2}\s+"
        r"(?:January|February|March|April|May|June|July|"
        r"August|September|October|November|December)"
        r"\s+[0-9]{4})",

        r"(?:apply\s+before|apply\s+by)"
        r"\s*[:\-]?\s*"
        r"([0-9]{1,2}[-/][0-9]{1,2}[-/][0-9]{2,4})"
    ]

    return first_match(
        text,
        patterns
    )


# ============================================
# SOURCE TYPE
# ============================================

def detect_source_type(source_url):

    if not source_url:
        return "Unknown"

    try:

        domain = urlparse(
            source_url
        ).netloc.lower()

    except Exception:
        return "Unknown"

    official_domains = (
        ".gov.in",
        ".nic.in",
        ".ac.in",
        ".edu.in"
    )

    if domain.endswith(official_domains):
        return "Official"

    return "Website"


# ============================================
# MAIN EXTRACTION
# ============================================

def extract_scholarship(
    text,
    source_url
):

    if not text:

        return {
            "name": "Not specified",
            "provider": "Not specified",
            "official_source_url": source_url,
            "application_url": source_url,
            "amount": None,
            "eligibility": None,
            "academic_requirements": None,
            "course_level": None,
            "income_criteria": None,
            "age_criteria": None,
            "gender_criteria": None,
            "category_criteria": None,
            "domicile_criteria": None,
            "institution_requirements": None,
            "opening_date": None,
            "deadline": None,
            "source_type": detect_source_type(source_url),
            "evidence": None
        }

    text = normalize_text(text)

    cleaned_text = clean_navigation(text)

    scholarship = {

        "name":
            extract_name(cleaned_text),

        "provider":
            extract_provider(cleaned_text),

        "official_source_url":
            source_url,

        "application_url":
            find_application_url(
                text,
                source_url
            ),

        "amount":
            extract_amount(cleaned_text),

        "eligibility":
            extract_eligibility(cleaned_text),

        "academic_requirements":
            extract_academic_requirements(
                cleaned_text
            ),

        "course_level":
            extract_course_level(cleaned_text),

        "income_criteria":
            extract_income(cleaned_text),

        "age_criteria":
            extract_age(cleaned_text),

        "gender_criteria":
            extract_gender(cleaned_text),

        "category_criteria":
            extract_category(cleaned_text),

        "domicile_criteria":
            extract_domicile(cleaned_text),

        "institution_requirements":
            extract_institution(cleaned_text),

        "opening_date":
            extract_opening_date(cleaned_text),

        "deadline":
            extract_deadline(cleaned_text),

        "source_type":
            detect_source_type(
                source_url
            ),

        # Keep original text as evidence
        "evidence":
            text[:5000]
    }

    return scholarship
# ============================================
# EXTRACT MULTIPLE SCHOLARSHIPS
# ============================================

def extract_multiple_scholarships(
    text,
    source_url,
    html=None
):
    """
    Extract multiple scholarship schemes from
    the NSP All-Scholarships page.

    Parameters:
        text       : cleaned/readable webpage text
        source_url : source webpage URL
        html       : raw HTML returned by crawl_page()

    Returns:
        List of scholarship dictionaries.
    """

    if not text and not html:
        return []

    # ------------------------------------------------
    # IF RAW HTML IS AVAILABLE, USE HTML EXTRACTION
    # ------------------------------------------------

    if html:

        soup = BeautifulSoup(
            html,
            "lxml"
        )

        scholarships = []

        current_provider = "Not specified"

        # Process elements in the same order
        # in which they appear on the webpage.
        for element in soup.find_all(True):

            # ----------------------------------------
            # DETECT PROVIDER BUTTON
            # ----------------------------------------

            if element.name == "button":

                provider_text = clean_text(
                    element.get_text(
                        " ",
                        strip=True
                    )
                )

                if provider_text:

                    provider_lower = (
                        provider_text.lower()
                    )

                    provider_patterns = [
                        r"^ministry of ",
                        r"^department of ",
                        r"^all india council for technical education$",
                        r"^ugc$",
                        r"^north eastern council",
                    ]

                    for pattern in provider_patterns:

                        if re.search(
                            pattern,
                            provider_lower,
                            re.IGNORECASE
                        ):

                            current_provider = (
                                provider_text
                            )

                            break

            # ----------------------------------------
            # DETECT SCHOLARSHIP HEADING
            # ----------------------------------------

            if element.name not in [
                "h1",
                "h2",
                "h3",
                "h4",
                "h5",
                "h6"
            ]:
                continue

            heading_text = clean_text(
                element.get_text(
                    " ",
                    strip=True
                )
            )

            if not heading_text:
                continue

            # NSP scholarship headings contain
            # either Merit Based Scheme or
            # Welfare Based Scheme.
            scheme_match = re.search(
                r"\((?:merit|welfare)\s+based\s+scheme\)",
                heading_text,
                re.IGNORECASE
            )

            if not scheme_match:
                continue

            # ----------------------------------------
            # EXTRACT SCHOLARSHIP NAME
            # ----------------------------------------

            name = re.sub(
                r"\s*\((?:merit|welfare)\s+based\s+scheme\)\s*$",
                "",
                heading_text,
                flags=re.IGNORECASE
            ).strip()

            name = clean_text(name)

            if not name:
                continue

            if len(name) < 8:
                continue

            # ----------------------------------------
            # FIND THE SCHOLARSHIP CONTAINER
            # ----------------------------------------

            container = element

            block_text = ""

            # Move upward until we find the
            # container containing the application dates.
            for _ in range(6):

                if container is None:
                    break

                candidate_text = clean_text(
                    container.get_text(
                        " ",
                        strip=True
                    )
                )

                if candidate_text:

                    if (
                        "Scheme Open from" in candidate_text
                        and
                        (
                            "Student Application Open till"
                            in candidate_text
                            or
                            "Student Application Closed on"
                            in candidate_text
                        )
                    ):

                        block_text = candidate_text
                        break

                container = container.parent

            # ----------------------------------------
            # FALLBACK
            # ----------------------------------------

            if not block_text:

                parent = element.parent

                if parent:

                    block_text = clean_text(
                        parent.get_text(
                            " ",
                            strip=True
                        )
                    )

            # ----------------------------------------
            # OPENING DATE
            # ----------------------------------------

            opening_match = re.search(
                r"Scheme\s+Open\s+from"
                r"(?:\s+\(for\s+Renewal\))?"
                r"\s*:\s*"
                r"([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})",
                block_text,
                re.IGNORECASE
            )

            opening_date = (
                opening_match.group(1)
                if opening_match
                else None
            )

            # ----------------------------------------
            # DEADLINE
            # ----------------------------------------

            deadline_match = re.search(
                r"Student\s+Application\s+"
                r"(?:Open\s+till|Closed\s+on)"
                r"(?:\s+\(for\s+Renewal\))?"
                r"\s*:\s*"
                r"([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})",
                block_text,
                re.IGNORECASE
            )

            deadline = (
                deadline_match.group(1)
                if deadline_match
                else None
            )

            # ----------------------------------------
            # CREATE SCHOLARSHIP RECORD
            # ----------------------------------------

            scholarship = extract_scholarship(
                block_text,
                source_url
            )

            # Override generic extraction with
            # values specifically identified from
            # the NSP HTML structure.
            scholarship["name"] = name

            scholarship["provider"] = (
                current_provider
            )

            scholarship["official_source_url"] = (
                source_url
            )

            scholarship["application_url"] = (
                source_url
            )

            scholarship["opening_date"] = (
                opening_date
            )

            scholarship["deadline"] = (
                deadline
            )

            # The listing page doesn't normally
            # contain the actual scholarship amount.
            scholarship["amount"] = None

            # Store only the relevant scheme block
            # as evidence instead of the entire page.
            scholarship["evidence"] = (
                block_text[:5000]
            )

            scholarships.append(
                scholarship
            )

        # ----------------------------------------
        # REMOVE DUPLICATES
        # ----------------------------------------

        unique = []

        seen = set()

        for scholarship in scholarships:

            name = scholarship.get(
                "name",
                "Not specified"
            )

            key = name.lower().strip()

            if (
                not key
                or key == "not specified"
            ):
                continue

            if key in seen:
                continue

            seen.add(key)

            unique.append(
                scholarship
            )

        return unique

    # ------------------------------------------------
    # FALLBACK: TEXT-BASED EXTRACTION
    # ------------------------------------------------

    if not text:
        return []

    text = normalize_text(text)

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    scholarships = []

    current_provider = "Not specified"

    for index, line in enumerate(lines):

        clean_line = line.strip()

        # ----------------------------------------
        # PROVIDER
        # ----------------------------------------

        provider_patterns = [
            r"^ministry of .+",
            r"^department of .+",
            r"^all india council for technical education$",
            r"^ugc$",
            r"^north eastern council.*",
        ]

        provider_found = False

        for pattern in provider_patterns:

            if re.match(
                pattern,
                clean_line,
                re.IGNORECASE
            ):

                current_provider = clean_text(
                    clean_line
                )

                provider_found = True
                break

        if provider_found:
            continue

        # ----------------------------------------
        # SCHOLARSHIP HEADING
        # ----------------------------------------

        if not re.search(
            r"\((?:merit|welfare)\s+based\s+scheme\)",
            clean_line,
            re.IGNORECASE
        ):
            continue

        name = re.sub(
            r"\s*\((?:merit|welfare)\s+based\s+scheme\)\s*$",
            "",
            clean_line,
            flags=re.IGNORECASE
        ).strip()

        if len(name) < 8:
            continue

        # ----------------------------------------
        # GET FOLLOWING LINES
        # ----------------------------------------

        block_lines = [
            clean_line
        ]

        for next_index in range(
            index + 1,
            min(index + 7, len(lines))
        ):

            next_line = lines[next_index]

            if re.search(
                r"\((?:merit|welfare)\s+based\s+scheme\)",
                next_line,
                re.IGNORECASE
            ):
                break

            block_lines.append(
                next_line
            )

        block = "\n".join(
            block_lines
        )

        # ----------------------------------------
        # DATES
        # ----------------------------------------

        opening_match = re.search(
            r"Scheme\s+Open\s+from"
            r"(?:\s+\(for\s+Renewal\))?"
            r"\s*:\s*"
            r"([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})",
            block,
            re.IGNORECASE
        )

        opening_date = (
            opening_match.group(1)
            if opening_match
            else None
        )

        deadline_match = re.search(
            r"Student\s+Application\s+"
            r"(?:Open\s+till|Closed\s+on)"
            r"(?:\s+\(for\s+Renewal\))?"
            r"\s*:\s*"
            r"([0-9]{1,2}-[0-9]{1,2}-[0-9]{4})",
            block,
            re.IGNORECASE
        )

        deadline = (
            deadline_match.group(1)
            if deadline_match
            else None
        )

        scholarship = extract_scholarship(
            block,
            source_url
        )

        scholarship["name"] = name

        scholarship["provider"] = (
            current_provider
        )

        scholarship["official_source_url"] = (
            source_url
        )

        scholarship["application_url"] = (
            source_url
        )

        scholarship["opening_date"] = (
            opening_date
        )

        scholarship["deadline"] = (
            deadline
        )

        scholarship["amount"] = None

        scholarship["evidence"] = block

        scholarships.append(
            scholarship
        )

    # ----------------------------------------
    # REMOVE DUPLICATES
    # ----------------------------------------

    unique = []

    seen = set()

    for scholarship in scholarships:

        name = scholarship.get(
            "name",
            "Not specified"
        )

        key = name.lower().strip()

        if (
            not key
            or key == "not specified"
        ):
            continue

        if key in seen:
            continue

        seen.add(key)

        unique.append(
            scholarship
        )

    return unique


if __name__ == "__main__":

    sample = """

    Prime Minister Scholarship Scheme

    Provider: Government of India

    Scholarship Amount: Rs. 36,000 per year

    Eligibility Criteria:
    Students studying in recognized institutions
    and meeting the required academic conditions.

    Family Income: Rs. 8,00,000 per annum

    Minimum Marks: 60%

    Course: Undergraduate

    Last Date: 31-10-2026

    """

    result = extract_scholarship(
        sample,
        "https://example.gov.in/scholarship"
    )

    print("\nEXTRACTED SCHOLARSHIP")
    print("=" * 60)

    for key, value in result.items():
        print(f"{key}: {value}")