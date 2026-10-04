from flask import Flask, render_template, request
import sqlite3
import os


app = Flask(__name__)


# ============================================================
# DATABASE PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE = os.path.join(BASE_DIR, "data", "scholarships.db")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# HOME / DASHBOARD
# ============================================================

@app.route("/")
def index():

    search = request.args.get("search", "").strip()
    provider = request.args.get("provider", "").strip()

    conn = get_db_connection()

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = """
        SELECT
            id,
            name,
            provider,
            official_source_url,
            application_url,
            amount,
            eligibility,
            academic_requirements,
            course_level,
            income_criteria,
            age_criteria,
            gender_criteria,
            category_criteria,
            domicile_criteria,
            institution_requirements,
            opening_date,
            deadline,
            source_type,
            evidence,
            confidence_score,
            status,
            last_verified,
            verification_reason
        FROM scholarships
        WHERE 1=1
    """

    params = []

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    if search:
        query += """
            AND (
                name LIKE ?
                OR provider LIKE ?
                OR eligibility LIKE ?
                OR course_level LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value,
            search_value
        ])

    # --------------------------------------------------------
    # Provider filter
    # --------------------------------------------------------

    if provider:
        query += " AND provider = ?"
        params.append(provider)

    # --------------------------------------------------------
    # Order
    # --------------------------------------------------------

    query += """
        ORDER BY
            CASE
                WHEN deadline IS NULL OR deadline = '' THEN 1
                ELSE 0
            END,
            id
    """

    scholarships = conn.execute(query, params).fetchall()

    # --------------------------------------------------------
    # Provider list
    # --------------------------------------------------------

    providers = conn.execute("""
        SELECT DISTINCT provider
        FROM scholarships
        WHERE provider IS NOT NULL
        AND provider != ''
        ORDER BY provider
    """).fetchall()

    # --------------------------------------------------------
    # Statistics
    # --------------------------------------------------------

    total = conn.execute("""
        SELECT COUNT(*)
        FROM scholarships
    """).fetchone()[0]

    verified = conn.execute("""
        SELECT COUNT(*)
        FROM scholarships
        WHERE status = 'VERIFIED'
    """).fetchone()[0]

    review_required = conn.execute("""
        SELECT COUNT(*)
        FROM scholarships
        WHERE status = 'REVIEW REQUIRED'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "index.html",
        scholarships=scholarships,
        providers=providers,
        total=total,
        verified=verified,
        review_required=review_required,
        search=search,
        selected_provider=provider
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print("SCHOLARSHIP INTELLIGENCE DASHBOARD")
    print("=" * 60)
    print("Database:", DATABASE)
    print("Starting Flask server...")
    print("Open: http://127.0.0.1:5000")
    print("=" * 60)

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )