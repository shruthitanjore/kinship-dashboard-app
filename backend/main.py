from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import pymysql

app = FastAPI(title="Kinship Dashboard API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://kinship-dashboard-app.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return pymysql.connect(
        host="be14sqnbtagrcglmv7c8-mysql.services.clever-cloud.com",
        user="uxgotsy7klnloo5l",
        password="4NoYBCrwGKpyOf2zaBRd",
        database="be14sqnbtagrcglmv7c8",
        port=3306,
        cursorclass=pymysql.cursors.DictCursor,
    )


@app.get("/")
def home():
    return {"message": "Kinship Dashboard API v2.0 Running"}


# ════════════════════════════════════════════════════════════════════════════
# REFERENCE DATA
# ════════════════════════════════════════════════════════════════════════════

@app.get("/social-workers")
def get_social_workers():
    """Field social workers only (sw_type = 1)."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT ROW_ID AS id, USER_NAME AS name
        FROM user_master_v2
        WHERE SW_FLAG = 'Yes'
          AND IS_ACTIVE = 'Yes'
          AND sw_type = 1
        ORDER BY USER_NAME
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


@app.get("/academic-years")
def get_academic_years():
    """Distinct academic years, filters out junk rows like '0'."""
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT aca_year AS year
        FROM academic_report
        WHERE aca_year IS NOT NULL
          AND aca_year NOT IN ('', '0')
          AND aca_year REGEXP '^[0-9]{4}-[0-9]{4}$'
        ORDER BY aca_year DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ════════════════════════════════════════════════════════════════════════════
# DASHBOARD — MONITORING SUMMARY
# ════════════════════════════════════════════════════════════════════════════

@app.get("/academic-monitoring-summary/{year}")
def academic_monitoring_summary(
    year: str,
    sw_id: Optional[int] = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    # When sw_id provided use INNER JOIN to filter, else LEFT JOIN to keep all children
    if sw_id:
        sw_join  = "JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID"
        sw_where = "AND fm.sw_id = %s"
        p_base   = (sw_id,)
        p_year   = (year, sw_id)
    else:
        sw_join  = "LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID"
        sw_where = ""
        p_base   = ()
        p_year   = (year,)

    cur.execute(f"""
        SELECT COUNT(DISTINCT cm.ROW_ID) AS total
        FROM child_master cm
        {sw_join}
        WHERE cm.C_STATUS = 'A'
        {sw_where}
    """, p_base)
    total_children = cur.fetchone()["total"]

    cur.execute(f"""
        SELECT COUNT(*) AS completed
        FROM (
            SELECT ar.child_id
            FROM academic_report ar
            JOIN child_master cm ON ar.child_id = cm.ROW_ID
            {sw_join}
            WHERE ar.aca_year = %s
              AND ar.IS_ACTIVE = 'A'
              AND ar.test_type IN ('Quarterly', 'Halfyearly', 'Annual')
              AND cm.C_STATUS = 'A'
              {sw_where}
            GROUP BY ar.child_id
            HAVING COUNT(DISTINCT ar.test_type) = 3
        ) AS complete_children
    """, p_year)
    academic_completed = cur.fetchone()["completed"]

    cur.execute(f"""
        SELECT COUNT(DISTINCT sv.CHILD_ID) AS completed
        FROM child_master cm
        {sw_join}
        JOIN school_visit sv ON cm.ROW_ID = sv.CHILD_ID
        WHERE cm.C_STATUS = 'A'
        {sw_where}
    """, p_base)
    school_visit_completed = cur.fetchone()["completed"]

    cur.execute(f"""
        SELECT COUNT(DISTINCT sfd.CHILD_ID) AS completed
        FROM child_master cm
        {sw_join}
        JOIN school_fees_details sfd ON cm.ROW_ID = sfd.CHILD_ID
        WHERE cm.C_STATUS = 'A'
          AND sfd.ACADEMIC_YEAR = %s
          {sw_where}
    """, p_year)
    school_fee_completed = cur.fetchone()["completed"]

    cur.close()
    conn.close()

    return {
        "totalChildren": total_children,
        "academicCompleted": academic_completed,
        "academicPending": max(total_children - academic_completed, 0),
        "schoolVisitCompleted": school_visit_completed,
        "schoolVisitPending": max(total_children - school_visit_completed, 0),
        "schoolFeeCompleted": school_fee_completed,
        "schoolFeePending": max(total_children - school_fee_completed, 0),
    }


# ════════════════════════════════════════════════════════════════════════════
# MISSING AADHAAR
# ════════════════════════════════════════════════════════════════════════════

@app.get("/children/missing-aadhaar")
def missing_aadhaar(
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * page_size

    sw_where     = "AND fm.sw_id = %s" if sw_id else ""
    count_params = (sw_id,) if sw_id else ()

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        WHERE cm.C_STATUS = 'A'
          AND (cm.AADHAR_NO IS NULL OR cm.AADHAR_NO = '')
          {sw_where}
    """, count_params)
    total = cur.fetchone()["total"]

    data_params = (sw_id, page_size, offset) if sw_id else (page_size, offset)
    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker
        FROM child_master cm
        JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        WHERE cm.C_STATUS = 'A'
          AND (cm.AADHAR_NO IS NULL OR cm.AADHAR_NO = '')
          {sw_where}
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, data_params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# MISSING PROFILE
# ════════════════════════════════════════════════════════════════════════════

@app.get("/children/missing-profile")
def missing_profile(
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * page_size

    sw_where     = "AND fm.sw_id = %s" if sw_id else ""
    count_params = (sw_id,) if sw_id else ()

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN child_profile cp ON cm.ROW_ID = cp.child_id
        WHERE cm.C_STATUS = 'A'
          AND cp.child_id IS NULL
          {sw_where}
    """, count_params)
    total = cur.fetchone()["total"]

    data_params = (sw_id, page_size, offset) if sw_id else (page_size, offset)
    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker
        FROM child_master cm
        JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN child_profile cp ON cm.ROW_ID = cp.child_id
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        WHERE cm.C_STATUS = 'A'
          AND cp.child_id IS NULL
          {sw_where}
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, data_params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# ACADEMIC REPORTS MODULE
# ════════════════════════════════════════════════════════════════════════════

@app.get("/academic-reports/summary/{year}")
def academic_reports_summary(
    year: str,
    sw_id: Optional[int] = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    sw_where = "AND fm.sw_id = %s" if sw_id else ""
    p        = (year, sw_id) if sw_id else (year,)

    cur.execute(f"""
        SELECT
            IFNULL(um.ROW_ID, 0)                 AS sw_id,
            IFNULL(um.USER_NAME, 'Unassigned')   AS social_worker,
            COUNT(DISTINCT cm.ROW_ID)            AS total_children,
            COUNT(DISTINCT fc.child_id)          AS completed,
            COUNT(DISTINCT cm.ROW_ID)
                - COUNT(DISTINCT fc.child_id)    AS pending,
            ROUND(
                COUNT(DISTINCT fc.child_id) * 100.0
                / NULLIF(COUNT(DISTINCT cm.ROW_ID), 0),
                1
            )                                    AS completion_pct
        FROM child_master cm
        LEFT JOIN family_master fm  ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id  = um.ROW_ID
        LEFT JOIN (
            SELECT child_id
            FROM academic_report
            WHERE aca_year  = %s
              AND IS_ACTIVE = 'A'
              AND test_type IN ('Quarterly', 'Halfyearly', 'Annual')
            GROUP BY child_id
            HAVING COUNT(DISTINCT test_type) = 3
        ) AS fc ON cm.ROW_ID = fc.child_id
        WHERE cm.C_STATUS = 'A'
          {sw_where}
        GROUP BY IFNULL(um.ROW_ID, 0), IFNULL(um.USER_NAME, 'Unassigned')
        ORDER BY completion_pct DESC
    """, p)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total_children  = sum(r["total_children"] for r in rows)
    total_completed = sum(r["completed"] for r in rows)
    total_pending   = sum(r["pending"] for r in rows)
    overall_pct     = round(total_completed * 100.0 / total_children, 1) if total_children else 0

    return {
        "year": year,
        "summary": {
            "total_children": total_children,
            "completed": total_completed,
            "pending": total_pending,
            "completion_pct": overall_pct,
        },
        "by_worker": rows,
    }


@app.get("/academic-reports/missing/{year}")
def academic_reports_missing(
    year: str,
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * page_size

    sw_where = "AND fm.sw_id = %s" if sw_id else ""

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        WHERE cm.C_STATUS = 'A'
          {sw_where}
          AND cm.ROW_ID NOT IN (
              SELECT child_id
              FROM academic_report
              WHERE aca_year  = %s
                AND IS_ACTIVE = 'A'
                AND test_type IN ('Quarterly', 'Halfyearly', 'Annual')
              GROUP BY child_id
              HAVING COUNT(DISTINCT test_type) = 3
          )
    """, (sw_id, year) if sw_id else (year,))
    total = cur.fetchone()["total"]

    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker,
            IFNULL(
                GROUP_CONCAT(
                    DISTINCT ar.test_type
                    ORDER BY ar.test_type
                    SEPARATOR ', '
                ),
                'None'
            ) AS submitted_types
        FROM child_master cm
        LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        LEFT JOIN academic_report ar
               ON cm.ROW_ID    = ar.child_id
              AND ar.aca_year  = %s
              AND ar.IS_ACTIVE = 'A'
        WHERE cm.C_STATUS = 'A'
          {sw_where}
          AND cm.ROW_ID NOT IN (
              SELECT child_id
              FROM academic_report
              WHERE aca_year  = %s
                AND IS_ACTIVE = 'A'
                AND test_type IN ('Quarterly', 'Halfyearly', 'Annual')
              GROUP BY child_id
              HAVING COUNT(DISTINCT test_type) = 3
          )
        GROUP BY cm.ROW_ID, cm.CHILD_NAME, fm.fam_code, um.USER_NAME
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, (year, sw_id, year, page_size, offset) if sw_id else (year, year, page_size, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# SCHOOL VISITS MODULE
# ════════════════════════════════════════════════════════════════════════════

@app.get("/school-visits/summary")
def school_visits_summary(
    sw_id: Optional[int] = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    sw_where = "AND fm.sw_id = %s" if sw_id else ""
    params   = (sw_id,) if sw_id else ()

    cur.execute(f"""
        SELECT
            IFNULL(um.ROW_ID, 0)                  AS sw_id,
            IFNULL(um.USER_NAME, 'Unassigned')    AS social_worker,
            COUNT(DISTINCT cm.ROW_ID)             AS total_children,
            COUNT(DISTINCT sv.CHILD_ID)           AS completed,
            COUNT(DISTINCT cm.ROW_ID)
                - COUNT(DISTINCT sv.CHILD_ID)     AS pending,
            ROUND(
                COUNT(DISTINCT sv.CHILD_ID) * 100.0
                / NULLIF(COUNT(DISTINCT cm.ROW_ID), 0),
                1
            )                                     AS completion_pct
        FROM child_master cm
        LEFT JOIN family_master fm  ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id  = um.ROW_ID
        LEFT JOIN school_visit sv ON cm.ROW_ID = sv.CHILD_ID
        WHERE cm.C_STATUS = 'A'
          {sw_where}
        GROUP BY IFNULL(um.ROW_ID, 0), IFNULL(um.USER_NAME, 'Unassigned')
        ORDER BY completion_pct DESC
    """, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total_children  = sum(r["total_children"] for r in rows)
    total_completed = sum(r["completed"] for r in rows)
    total_pending   = sum(r["pending"] for r in rows)
    overall_pct     = round(total_completed * 100.0 / total_children, 1) if total_children else 0

    return {
        "summary": {
            "total_children": total_children,
            "completed": total_completed,
            "pending": total_pending,
            "completion_pct": overall_pct,
        },
        "by_worker": rows,
    }


@app.get("/school-visits/pending")
def school_visits_pending(
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * page_size

    sw_where     = "AND fm.sw_id = %s" if sw_id else ""
    count_params = (sw_id,) if sw_id else ()

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN school_visit sv ON cm.ROW_ID = sv.CHILD_ID
        WHERE cm.C_STATUS = 'A'
          AND sv.CHILD_ID IS NULL
          {sw_where}
    """, count_params)
    total = cur.fetchone()["total"]

    data_params = (sw_id, page_size, offset) if sw_id else (page_size, offset)
    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker
        FROM child_master cm
        LEFT JOIN family_master fm  ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        LEFT JOIN school_visit sv ON cm.ROW_ID = sv.CHILD_ID
        WHERE cm.C_STATUS = 'A'
          AND sv.CHILD_ID IS NULL
          {sw_where}
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, data_params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# SCHOOL FEES MODULE
# ════════════════════════════════════════════════════════════════════════════

@app.get("/school-fees/summary/{year}")
def school_fees_summary(
    year: str,
    sw_id: Optional[int] = Query(None),
):
    conn = get_db()
    cur = conn.cursor()

    sw_where = "AND fm.sw_id = %s" if sw_id else ""
    params   = (year, sw_id) if sw_id else (year,)

    cur.execute(f"""
        SELECT
            IFNULL(um.ROW_ID, 0)                   AS sw_id,
            IFNULL(um.USER_NAME, 'Unassigned')     AS social_worker,
            COUNT(DISTINCT cm.ROW_ID)              AS total_children,
            COUNT(DISTINCT sfd.CHILD_ID)           AS completed,
            COUNT(DISTINCT cm.ROW_ID)
                - COUNT(DISTINCT sfd.CHILD_ID)     AS pending,
            ROUND(
                COUNT(DISTINCT sfd.CHILD_ID) * 100.0
                / NULLIF(COUNT(DISTINCT cm.ROW_ID), 0),
                1
            )                                      AS completion_pct
        FROM child_master cm
        LEFT JOIN family_master fm  ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id  = um.ROW_ID
        LEFT JOIN school_fees_details sfd
               ON cm.ROW_ID = sfd.CHILD_ID
              AND sfd.ACADEMIC_YEAR = %s
        WHERE cm.C_STATUS = 'A'
          {sw_where}
        GROUP BY IFNULL(um.ROW_ID, 0), IFNULL(um.USER_NAME, 'Unassigned')
        ORDER BY completion_pct DESC
    """, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    total_children  = sum(r["total_children"] for r in rows)
    total_completed = sum(r["completed"] for r in rows)
    total_pending   = sum(r["pending"] for r in rows)
    overall_pct     = round(total_completed * 100.0 / total_children, 1) if total_children else 0

    return {
        "year": year,
        "summary": {
            "total_children": total_children,
            "completed": total_completed,
            "pending": total_pending,
            "completion_pct": overall_pct,
        },
        "by_worker": rows,
    }


@app.get("/school-fees/pending/{year}")
def school_fees_pending(
    year: str,
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    conn = get_db()
    cur = conn.cursor()
    offset = (page - 1) * page_size

    sw_where     = "AND fm.sw_id = %s" if sw_id else ""
    count_params = (year, sw_id) if sw_id else (year,)

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN school_fees_details sfd
               ON cm.ROW_ID = sfd.CHILD_ID AND sfd.ACADEMIC_YEAR = %s
        WHERE cm.C_STATUS = 'A'
          AND sfd.CHILD_ID IS NULL
          {sw_where}
    """, count_params)
    total = cur.fetchone()["total"]

    data_params = (year, sw_id, page_size, offset) if sw_id else (year, page_size, offset)
    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker
        FROM child_master cm
        LEFT JOIN family_master fm  ON cm.FAM_ID = fm.ROW_ID
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        LEFT JOIN school_fees_details sfd
               ON cm.ROW_ID = sfd.CHILD_ID AND sfd.ACADEMIC_YEAR = %s
        WHERE cm.C_STATUS = 'A'
          AND sfd.CHILD_ID IS NULL
          {sw_where}
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, data_params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# CHILD DATA — MISSING FIELDS
# ════════════════════════════════════════════════════════════════════════════

# Date columns — can only check IS NULL, not = ''
DATE_COLUMNS = {"DOB", "ADM_DATE", "UADM_DATE"}

# Integer columns — can only check IS NULL, not = ''
INT_COLUMNS = {"FATHER_INCOME", "MOTHER_INCOME"}

# All allowed columns — whitelist prevents SQL injection
ALLOWED_CHILD_COLUMNS = {
    "CHILD_NAME", "GENDER", "DOB", "UNIT_CODE", "GBL_ADM_NO",
    "UNT_ADM_NO", "ADM_DATE", "CHILD_EDU", "AADHAR_NO", "PHOTO_FILE",
    "NATIONALITY", "CASTE", "SCHOOL_ID", "school_fees", "SB_ACC_NO",
    "FATHER_NAME", "FATHER_ALIVE", "FATHER_OCCUP", "FATHER_INCOME", "FATHER_PH",
    "MOTHER_NAME", "MOTHER_ALIVE", "MOTHER_OCCUP", "MOTHER_INCOME", "MOTHER_PH",
    "GUARD_NAME", "GUARD_RELN", "GUARD_PHNO_1",
    "ADDR_LINE1", "STATE", "CITY", "PINCODE",
    "TRAVEL_TIME", "SP_LANG", "IDENTITY_1", "DCPO_ADDRESS", "FAMILY_HISTORY",
}

# Full column list with display labels
CHILD_COLUMNS = [
    ("CHILD_NAME",     "Child Name"),
    ("GENDER",         "Gender"),
    ("DOB",            "Date of Birth"),
    ("UNIT_CODE",      "Unit Code"),
    ("GBL_ADM_NO",     "Global Admission No"),
    ("UNT_ADM_NO",     "Unit Admission No"),
    ("ADM_DATE",       "Admission Date"),
    ("CHILD_EDU",      "Education"),
    ("AADHAR_NO",      "Aadhaar Number"),
    ("PHOTO_FILE",     "Photo"),
    ("NATIONALITY",    "Nationality"),
    ("CASTE",          "Caste"),
    ("SCHOOL_ID",      "School"),
    ("school_fees",    "School Fee Type"),
    ("SB_ACC_NO",      "Bank Account"),
    ("FATHER_NAME",    "Father Name"),
    ("FATHER_ALIVE",   "Father Alive Status"),
    ("FATHER_OCCUP",   "Father Occupation"),
    ("FATHER_INCOME",  "Father Income"),
    ("FATHER_PH",      "Father Phone"),
    ("MOTHER_NAME",    "Mother Name"),
    ("MOTHER_ALIVE",   "Mother Alive Status"),
    ("MOTHER_OCCUP",   "Mother Occupation"),
    ("MOTHER_INCOME",  "Mother Income"),
    ("MOTHER_PH",      "Mother Phone"),
    ("GUARD_NAME",     "Guardian Name"),
    ("GUARD_RELN",     "Guardian Relation"),
    ("GUARD_PHNO_1",   "Guardian Phone"),
    ("ADDR_LINE1",     "Address"),
    ("STATE",          "State"),
    ("CITY",           "City"),
    ("PINCODE",        "Pincode"),
    ("TRAVEL_TIME",    "Travel Time"),
    ("SP_LANG",        "Special Language"),
    ("IDENTITY_1",     "Identity Proof"),
    ("DCPO_ADDRESS",   "DCPO Address"),
    ("FAMILY_HISTORY", "Family History"),
]


def get_missing_condition(col):
    """Return the correct SQL condition for checking missing values."""
    if col in DATE_COLUMNS or col in INT_COLUMNS:
        return f"cm.{col} IS NULL"
    return f"(cm.{col} IS NULL OR cm.{col} = '')"


@app.get("/child-data/missing-counts")
def child_data_missing_counts(
    sw_id: Optional[int] = Query(None),
):
    """Returns count of children missing each field."""
    conn = get_db()
    cur = conn.cursor()

    sw_join  = "JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID" if sw_id else "LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID"
    sw_where = "AND fm.sw_id = %s" if sw_id else ""
    params   = (sw_id,) if sw_id else ()

    result = []
    for col, label in CHILD_COLUMNS:
        condition = get_missing_condition(col)
        cur.execute(f"""
            SELECT COUNT(*) AS missing_count
            FROM child_master cm
            {sw_join}
            WHERE cm.C_STATUS = 'A'
              AND {condition}
              {sw_where}
        """, params)
        count = cur.fetchone()["missing_count"]
        result.append({
            "column": col,
            "label": label,
            "missing_count": count,
        })

    cur.close()
    conn.close()
    return result


@app.get("/child-data/missing-children")
def child_data_missing_children(
    column: str = Query(..., description="Column name from child_master"),
    sw_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Returns paginated list of children missing the specified field."""
    if column not in ALLOWED_CHILD_COLUMNS:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=f"Column '{column}' is not allowed.")

    conn = get_db()
    cur = conn.cursor()
    offset   = (page - 1) * page_size
    condition = get_missing_condition(column)

    sw_join  = "JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID" if sw_id else "LEFT JOIN family_master fm ON cm.FAM_ID = fm.ROW_ID"
    sw_where = "AND fm.sw_id = %s" if sw_id else ""
    params   = (sw_id,) if sw_id else ()

    cur.execute(f"""
        SELECT COUNT(*) AS total
        FROM child_master cm
        {sw_join}
        WHERE cm.C_STATUS = 'A'
          AND {condition}
          {sw_where}
    """, params)
    total = cur.fetchone()["total"]

    data_params = (*params, page_size, offset)
    cur.execute(f"""
        SELECT
            cm.ROW_ID,
            cm.CHILD_NAME,
            fm.fam_code,
            um.USER_NAME AS social_worker
        FROM child_master cm
        {sw_join}
        LEFT JOIN user_master_v2 um ON fm.sw_id = um.ROW_ID
        WHERE cm.C_STATUS = 'A'
          AND {condition}
          {sw_where}
        ORDER BY cm.CHILD_NAME
        LIMIT %s OFFSET %s
    """, data_params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return {
        "column": column,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": max(1, -(-total // page_size)),
        "data": rows,
    }


# ════════════════════════════════════════════════════════════════════════════
# LEGACY ENDPOINTS
# ════════════════════════════════════════════════════════════════════════════

@app.get("/dashboard/summary")
def dashboard_summary_legacy():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM child_master WHERE C_STATUS='A'")
    total = cur.fetchone()["total"]
    cur.execute("SELECT COUNT(*) AS total FROM child_master WHERE C_STATUS='A' AND (AADHAR_NO IS NULL OR AADHAR_NO='')")
    missing_aadhaar = cur.fetchone()["total"]
    cur.execute("""
        SELECT COUNT(*) AS total FROM child_master cm
        LEFT JOIN child_profile cp ON cm.ROW_ID = cp.child_id
        WHERE cm.C_STATUS='A' AND cp.child_id IS NULL
    """)
    missing_profile = cur.fetchone()["total"]
    cur.execute("""
        SELECT COUNT(*) AS total FROM child_master cm
        LEFT JOIN academic_report ar ON cm.ROW_ID = ar.child_id
        WHERE cm.C_STATUS='A' AND ar.child_id IS NULL
    """)
    missing_academic = cur.fetchone()["total"]
    cur.close()
    conn.close()
    return {
        "totalChildren": total,
        "missingAadhaar": missing_aadhaar,
        "missingProfile": missing_profile,
        "missingAcademic": missing_academic,
    }


@app.get("/sw-academic-performance/{year}")
def sw_academic_performance(year: str):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT
            um.USER_NAME,
            COUNT(DISTINCT cm.ROW_ID)          AS total_children,
            COUNT(DISTINCT fc.child_id)        AS completed_reports,
            COUNT(DISTINCT cm.ROW_ID)
                - COUNT(DISTINCT fc.child_id)  AS missing_reports,
            ROUND(
                COUNT(DISTINCT fc.child_id) * 100.0
                / NULLIF(COUNT(DISTINCT cm.ROW_ID), 0),
                2
            )                                  AS completion_percent
        FROM child_master cm
        JOIN user_master_v2 um ON cm.coord = um.ROW_ID
        LEFT JOIN (
            SELECT child_id
            FROM academic_report
            WHERE aca_year  = %s
              AND IS_ACTIVE = 'A'
              AND test_type IN ('Quarterly', 'Halfyearly', 'Annual')
            GROUP BY child_id
            HAVING COUNT(DISTINCT test_type) = 3
        ) AS fc ON cm.ROW_ID = fc.child_id
        WHERE cm.C_STATUS = 'A'
        GROUP BY um.USER_NAME
        ORDER BY completion_percent ASC
    """, (year,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows