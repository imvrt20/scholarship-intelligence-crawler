# ============================================================
# SCHOLARSHIP VERIFIER
# ============================================================

from datetime import datetime
from urllib.parse import urlparse


# ------------------------------------------------------------
# BASIC URL VALIDATION
# ------------------------------------------------------------

def is_valid_url(url):
    """
    Check whether a URL is valid.
    """

    if not url:
        return False

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
        )

    except Exception:
        return False


# ------------------------------------------------------------
# OFFICIAL SOURCE CHECK
# ------------------------------------------------------------

def is_official_source(url):
    """
    Check whether the scholarship comes from an
    official government / trusted source.
    """

    if not url:
        return False

    url = url.lower()

    official_domains = [
        "scholarships.gov.in",
        "ugc.gov.in",
        "aicte-india.org",
        "education.gov.in",
        "socialjustice.gov.in",
        "tribal.nic.in",
        "depwd.gov.in",
        "labour.gov.in",
        "agri.gov.in",
        "mha.gov.in",
        "railnet.gov.in",
        "railway.gov.in",
        "nic.in",
        "gov.in",
    ]

    return any(domain in url for domain in official_domains)


# ------------------------------------------------------------
# OFFICIAL DOMAIN CHECK
# ------------------------------------------------------------

def is_official_domain(url):
    """
    More strict official-domain verification.
    """

    if not is_valid_url(url):
        return False

    try:
        hostname = urlparse(url).netloc.lower()

        hostname = hostname.split(":")[0]

        official_domains = [
            "scholarships.gov.in",
            "ugc.gov.in",
            "aicte-india.org",
            "education.gov.in",
            "socialjustice.gov.in",
            "tribal.nic.in",
            "depwd.gov.in",
            "labour.gov.in",
            "agri.gov.in",
            "mha.gov.in",
            "railway.gov.in",
            "railnet.gov.in",
        ]

        for domain in official_domains:

            if hostname == domain:
                return True

            if hostname.endswith("." + domain):
                return True

        return False

    except Exception:
        return False


# ------------------------------------------------------------
# REAL VALUE CHECK
# ------------------------------------------------------------

def has_real_value(value):
    """
    Check whether a field contains meaningful information.
    """

    if value is None:
        return False

    value = str(value).strip()

    if not value:
        return False

    invalid_values = {
        "not specified",
        "n/a",
        "na",
        "none",
        "null",
        "unknown",
        "-",
        "--",
    }

    return value.lower() not in invalid_values


# ------------------------------------------------------------
# EVIDENCE CHECK
# ------------------------------------------------------------

def evidence_is_present(scholarship):
    """
    Check whether extracted evidence exists.
    """

    evidence = scholarship.get("evidence")

    if not has_real_value(evidence):
        return False

    evidence = str(evidence).strip()

    return len(evidence) >= 30


# ------------------------------------------------------------
# APPLICATION URL CHECK
# ------------------------------------------------------------

def has_application_url(scholarship):
    """
    Check whether an application URL exists.
    """

    application_url = scholarship.get("application_url")

    return is_valid_url(application_url)


# ------------------------------------------------------------
# DEADLINE CHECK
# ------------------------------------------------------------

def has_deadline(scholarship):
    """
    Check whether a scholarship has a deadline.
    """

    deadline = scholarship.get("deadline")

    return has_real_value(deadline)


# ------------------------------------------------------------
# CORE SCHOLARSHIP DATA CHECK
# ------------------------------------------------------------

def has_core_information(scholarship):
    """
    Check whether the scholarship has the minimum
    information required to be considered useful.
    """

    name = scholarship.get("name")
    provider = scholarship.get("provider")

    return (
        has_real_value(name)
        and has_real_value(provider)
    )


# ------------------------------------------------------------
# VERIFICATION CHECKS
# ------------------------------------------------------------

def verification_checks(scholarship):
    """
    Perform individual verification checks.
    """

    source_url = (
        scholarship.get("official_source_url")
        or scholarship.get("source_url")
        or ""
    )

    checks = {

        "official_source":
            is_official_source(source_url),

        "official_domain":
            is_official_domain(source_url),

        "scholarship_name":
            has_real_value(
                scholarship.get("name")
            ),

        "provider":
            has_real_value(
                scholarship.get("provider")
            ),

        "evidence":
            evidence_is_present(scholarship),

        "eligibility":
            has_real_value(
                scholarship.get("eligibility")
            ),

        "application_url":
            has_application_url(scholarship),

        "deadline":
            has_deadline(scholarship),

        "core_information":
            has_core_information(scholarship),
    }

    return checks


# ------------------------------------------------------------
# CONFIDENCE SCORE
# ------------------------------------------------------------

def calculate_confidence(scholarship):
    """
    Calculate confidence score from 0 to 100.
    """

    source_url = (
        scholarship.get("official_source_url")
        or scholarship.get("source_url")
        or ""
    )

    score = 0

    # Official URL
    if is_valid_url(source_url):
        score += 20

    # Official government domain
    if is_official_domain(source_url):
        score += 20

    # Scholarship name
    if has_real_value(
        scholarship.get("name")
    ):
        score += 10

    # Provider
    if has_real_value(
        scholarship.get("provider")
    ):
        score += 10

    # Evidence
    if evidence_is_present(scholarship):
        score += 15

    # Eligibility
    if has_real_value(
        scholarship.get("eligibility")
    ):
        score += 10

    # Application URL
    if has_application_url(scholarship):
        score += 5

    # Deadline
    if has_deadline(scholarship):
        score += 5

    # Amount
    if has_real_value(
        scholarship.get("amount")
    ):
        score += 5

    return min(score, 100)


# ------------------------------------------------------------
# VERIFICATION REASON
# ------------------------------------------------------------

def build_verification_reason(
    scholarship,
    checks,
    confidence_score
):
    """
    Create a human-readable explanation
    for the verification result.
    """

    failed_checks = [
        key
        for key, value in checks.items()
        if not value
    ]

    if confidence_score >= 90 and checks["official_domain"]:

        return (
            "Verified from an official government source. "
            "Core scholarship information and supporting "
            "evidence are available."
        )

    if confidence_score >= 75 and checks["official_domain"]:

        if failed_checks:

            return (
                "Official government source detected, but "
                "some scholarship information requires review: "
                + ", ".join(failed_checks)
            )

        return (
            "Official government source detected. "
            "Scholarship information appears reliable."
        )

    if not checks["official_domain"]:

        return (
            "Source could not be fully verified as an "
            "official government domain."
        )

    return (
        "Scholarship requires additional verification. "
        "Missing or incomplete information: "
        + ", ".join(failed_checks)
    )


# ------------------------------------------------------------
# MAIN VERIFICATION FUNCTION
# ------------------------------------------------------------

def verify_scholarship(scholarship):
    """
    Verify one scholarship and return the updated record.
    """

    if scholarship is None:
        return None

    # Make a copy so original dictionary is not modified
    scholarship = dict(scholarship)

    # Run verification checks
    checks = verification_checks(scholarship)

    # Calculate confidence
    confidence_score = calculate_confidence(
        scholarship
    )

    # --------------------------------------------------------
    # DECIDE STATUS
    # --------------------------------------------------------

    # Official government source + strong information
    if (
        checks["official_domain"]
        and checks["scholarship_name"]
        and checks["provider"]
        and checks["evidence"]
        and checks["deadline"]
        and confidence_score >= 90
    ):

        status = "VERIFIED"

    # Official source but incomplete information
    elif (
        checks["official_domain"]
        and checks["scholarship_name"]
        and checks["provider"]
        and confidence_score >= 75
    ):

        status = "REVIEW REQUIRED"

    # Everything else
    else:

        status = "REVIEW REQUIRED"

    # --------------------------------------------------------
    # ADD VERIFICATION DATA
    # --------------------------------------------------------

    scholarship["confidence_score"] = confidence_score

    scholarship["status"] = status

    scholarship["last_verified"] = datetime.utcnow()

    scholarship["verification_reason"] = (
        build_verification_reason(
            scholarship,
            checks,
            confidence_score
        )
    )

    # Store checks in dictionary as well
    scholarship["verification_checks"] = checks

    return scholarship


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_scholarship = {

        "name":
            "AICTE - Swanath Scholarship Scheme",

        "provider":
            "All India Council For Technical Education",

        "official_source_url":
            "https://scholarships.gov.in/All-Scholarships",

        "application_url":
            "https://scholarships.gov.in/",

        "amount":
            "Scholarship assistance",

        "eligibility":
            "Students pursuing technical education",

        "deadline":
            "31-10-2026",

        "evidence":
            (
                "AICTE - Swanath Scholarship Scheme "
                "is listed on the National Scholarship Portal "
                "for Academic Year 2026-27."
            ),
    }

    result = verify_scholarship(
        test_scholarship
    )

    print("\n====================================")
    print("VERIFICATION TEST")
    print("====================================")

    print(
        "Name:",
        result.get("name")
    )

    print(
        "Provider:",
        result.get("provider")
    )

    print(
        "Confidence:",
        result.get("confidence_score")
    )

    print(
        "Status:",
        result.get("status")
    )

    print(
        "Reason:",
        result.get("verification_reason")
    )

    print(
        "Checks:",
        result.get("verification_checks")
    )

    print("====================================")