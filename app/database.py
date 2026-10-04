# ============================================
# SCHOLARSHIP DATABASE - FINAL VERSION
# ============================================

import os

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    Float
)

from sqlalchemy.orm import (
    declarative_base,
    sessionmaker
)


# ============================================
# DATABASE PATH
# ============================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

DATA_DIR = os.path.join(
    BASE_DIR,
    "data"
)

os.makedirs(
    DATA_DIR,
    exist_ok=True
)

DATABASE_PATH = os.path.join(
    DATA_DIR,
    "scholarships.db"
)

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ============================================
# DATABASE CONNECTION
# ============================================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


# ============================================
# SCHOLARSHIP TABLE
# ============================================

class ScholarshipDB(Base):

    __tablename__ = "scholarships"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # ----------------------------------------
    # BASIC INFORMATION
    # ----------------------------------------

    name = Column(
        String
    )

    provider = Column(
        String
    )

    official_source_url = Column(
        String
    )

    application_url = Column(
        String
    )

    # ----------------------------------------
    # SCHOLARSHIP BENEFIT
    # ----------------------------------------

    amount = Column(
        String
    )

    # ----------------------------------------
    # ELIGIBILITY
    # ----------------------------------------

    eligibility = Column(
        Text
    )

    academic_requirements = Column(
        Text
    )

    course_level = Column(
        String
    )

    income_criteria = Column(
        String
    )

    age_criteria = Column(
        String
    )

    gender_criteria = Column(
        String
    )

    category_criteria = Column(
        String
    )

    domicile_criteria = Column(
        String
    )

    institution_requirements = Column(
        Text
    )

    # ----------------------------------------
    # DATES
    # ----------------------------------------

    opening_date = Column(
        String
    )

    deadline = Column(
        String
    )

    # ----------------------------------------
    # SOURCE
    # ----------------------------------------

    source_type = Column(
        String
    )

    evidence = Column(
        Text
    )

    # ----------------------------------------
    # VERIFICATION
    # ----------------------------------------

    confidence_score = Column(
        Float
    )

    status = Column(
        String
    )

    last_verified = Column(
        String
    )

    verification_reason = Column(
        Text
    )


# ============================================
# INITIALIZE DATABASE
# ============================================

def init_db():

    Base.metadata.create_all(
        bind=engine
    )

    print("=" * 60)
    print("DATABASE INITIALIZED")
    print("=" * 60)

    print(
        "Database:",
        DATABASE_PATH
    )

    print(
        "Table: scholarships"
    )

    print("=" * 60)


# ============================================
# SAVE SCHOLARSHIP
# ============================================

def save_scholarship(scholarship):

    db = SessionLocal()

    try:

        # ====================================
        # GET BASIC VALUES
        # ====================================

        name = scholarship.get("name") or "Not specified"

        source_url = (
            scholarship.get("official_source_url")
            or scholarship.get("source_url")
            or ""
        )

        application_url = (
            scholarship.get("application_url")
            or ""
        )

        # ====================================
        # CHECK FOR DUPLICATE
        # ====================================

        existing = db.query(ScholarshipDB).filter(
            ScholarshipDB.name == name,
            ScholarshipDB.official_source_url == source_url
        ).first()

        if existing:

            # Update existing record
            existing.provider = scholarship.get("provider")
            existing.application_url = application_url
            existing.amount = scholarship.get("amount")
            existing.eligibility = scholarship.get("eligibility")
            existing.academic_requirements = scholarship.get(
                "academic_requirements"
            )
            existing.course_level = scholarship.get("course_level")
            existing.income_criteria = scholarship.get("income_criteria")
            existing.age_criteria = scholarship.get("age_criteria")
            existing.gender_criteria = scholarship.get("gender_criteria")
            existing.category_criteria = scholarship.get(
                "category_criteria"
            )
            existing.domicile_criteria = scholarship.get(
                "domicile_criteria"
            )
            existing.institution_requirements = scholarship.get(
                "institution_requirements"
            )
            existing.opening_date = scholarship.get("opening_date")
            existing.deadline = scholarship.get("deadline")
            existing.source_type = scholarship.get("source_type")
            existing.evidence = scholarship.get("evidence")
            existing.confidence_score = scholarship.get(
                "confidence_score"
            )
            existing.status = scholarship.get("status")
            existing.last_verified = scholarship.get(
                "last_verified"
            )
            existing.verification_reason = scholarship.get(
                "verification_reason"
            )

            db.commit()

            print("Updated:", name)

            return existing.id

        # ====================================
        # CREATE NEW SCHOLARSHIP
        # ====================================

        new_scholarship = ScholarshipDB(

            name=name,

            provider=scholarship.get(
                "provider"
            ),

            official_source_url=source_url,

            application_url=application_url,

            amount=scholarship.get(
                "amount"
            ),

            eligibility=scholarship.get(
                "eligibility"
            ),

            academic_requirements=scholarship.get(
                "academic_requirements"
            ),

            course_level=scholarship.get(
                "course_level"
            ),

            income_criteria=scholarship.get(
                "income_criteria"
            ),

            age_criteria=scholarship.get(
                "age_criteria"
            ),

            gender_criteria=scholarship.get(
                "gender_criteria"
            ),

            category_criteria=scholarship.get(
                "category_criteria"
            ),

            domicile_criteria=scholarship.get(
                "domicile_criteria"
            ),

            institution_requirements=scholarship.get(
                "institution_requirements"
            ),

            opening_date=scholarship.get(
                "opening_date"
            ),

            deadline=scholarship.get(
                "deadline"
            ),

            source_type=scholarship.get(
                "source_type"
            ),

            evidence=scholarship.get(
                "evidence"
            ),

            confidence_score=scholarship.get(
                "confidence_score"
            ),

            status=scholarship.get(
                "status"
            ),

            last_verified=scholarship.get(
                "last_verified"
            ),

            verification_reason=scholarship.get(
                "verification_reason"
            )
        )

        # ====================================
        # SAVE TO DATABASE
        # ====================================

        db.add(new_scholarship)

        db.commit()

        db.refresh(new_scholarship)

        print("Saved:", name)

        return new_scholarship.id

    except Exception as error:

        db.rollback()

        print("Database save error:")
        print(error)

        return None

    finally:

        db.close()