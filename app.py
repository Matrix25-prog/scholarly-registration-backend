
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash
from models import db, Student, Course, Section, SectionMeeting, Enrollment, Prerequisite

DAY_LABEL = {1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri"}
TERM_LABEL = {"FALL": "Fall", "SPRING": "Spring", "SUMMER": "Summer"}


def parse_time_to_minutes(t: str) -> int:
  
  h, m = t.split(":")
  return int(h) * 60 + int(m)


def meetings_conflict(sec_a: Section, sec_b: Section) -> bool:
    """
    True if two sections overlap in time on at least one common day.
    """
    for ma in sec_a.meetings:
        for mb in sec_b.meetings:
            if ma.day_of_week != mb.day_of_week:
                continue
            start_a = parse_time_to_minutes(ma.start_time)
            end_a = parse_time_to_minutes(ma.end_time)
            start_b = parse_time_to_minutes(mb.start_time)
            end_b = parse_time_to_minutes(mb.end_time)
            if start_a < end_b and start_b < end_a:
                return True
    return False


def create_app():
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///registration.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    
    CORS(app)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    

    def get_current_student():
        """
        Uses the 'email' provided by the frontend (either as a query parameter
        ?email=... or in JSON body {"email": "..."} ) to identify the Student.
        """
        email = (request.args.get("email") or "").strip()
        if not email:
            data = request.get_json(silent=True) or {}
            email = (data.get("email") or "").strip()
        if not email:
            return None
        return Student.query.filter_by(email=email).first()

    def section_to_dict(section, enrollment_status=None):
        course = section.course
        meetings = [
            {
                "day": m.day_of_week,
                "day_label": DAY_LABEL.get(m.day_of_week, str(m.day_of_week)),
                "start": m.start_time,
                "end": m.end_time,
            }
            for m in sorted(section.meetings, key=lambda x: x.day_of_week)
        ]
        prereq_codes = [p.prereq_course.code for p in course.prereqs]

        return {
            "section_id": section.id,
            "crn": section.crn,
            "term": section.term,
            "term_label": TERM_LABEL.get(section.term, section.term),
            "section_code": section.section_code,
            "course": {
                "id": course.id,
                "code": course.code,
                "title": course.title,
                "subject": course.subject,
                "credits": course.credits,
                "instructor": course.instructor,
                "prereqs": prereq_codes,
            },
            "meetings": meetings,
            "status": enrollment_status or "PENDING",
        }

    
    @app.route("/api/hello")
    def hello():
        return jsonify({"message": "Backend is running ✅"})

    
    @app.route("/api/login", methods=["POST"])
    def login():
        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        password = data.get("password") or ""

        if not email or not password:
            return jsonify({"error": "Email and password are required."}), 400

        user = Student.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password_hash, password):
            return jsonify({"error": "Invalid email or password."}), 401

        return jsonify({
            "email": user.email,
            "name": user.name,
            "role": user.role or "student",
        })

    
    @app.route("/api/courses")
    def list_courses():
        q = (request.args.get("q") or "").strip().lower()
        subject = request.args.get("subject") or ""
        credits = request.args.get("credits") or ""
        term = (request.args.get("term") or "").upper()
        day = request.args.get("day") or ""

        query = Course.query

        if subject:
            query = query.filter(Course.subject == subject)
        if credits:
            try:
                c = int(credits)
                query = query.filter(Course.credits == c)
            except ValueError:
                pass

        courses = query.all()
        result = []

        for course in courses:
            if q and (q not in course.title.lower()) and (q not in course.code.lower()):
                continue

            for section in course.sections:
                if term and section.term.upper() != term:
                    continue

                if day:
                    try:
                        d_int = int(day)
                    except ValueError:
                        d_int = None
                    if d_int:
                        has_day = any(m.day_of_week == d_int for m in section.meetings)
                        if not has_day:
                            continue

                result.append(section_to_dict(section))

        return jsonify(result)

    
    @app.route("/api/schedule")
    def get_schedule():
        student = get_current_student()
        if not student:
            return jsonify({"error": "Student not found (missing or invalid email)."}), 404

        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        sections = [
            section_to_dict(en.section, enrollment_status=en.status)
            for en in enrollments
        ]
        return jsonify(sections)

    
    @app.route("/api/schedule/add", methods=["POST"])
    def add_to_schedule():
        student = get_current_student()
        if not student:
            return jsonify({"error": "Student not found (missing or invalid email)."}), 404

        data = request.get_json() or {}
        section_id = data.get("section_id")
        if not section_id:
            return jsonify({"error": "section_id is required"}), 400

        section = Section.query.get(section_id)
        if not section:
            return jsonify({"error": "Section not found"}), 404

        existing = Enrollment.query.filter_by(
            student_id=student.id,
            section_id=section.id
        ).first()
        if existing:
            return jsonify({"message": "Already in schedule"}), 200

        
        same_term_enrollments = Enrollment.query.join(Section).filter(
            Enrollment.student_id == student.id,
            Section.term == section.term
        ).all()

        for en in same_term_enrollments:
            other_sec = en.section
            if meetings_conflict(section, other_sec):
                return jsonify({
                    "error": (
                        f"{section.course.code} (CRN {section.crn}) conflicts with "
                        f"{other_sec.course.code} (CRN {other_sec.crn}) in {section.term}."
                    )
                }), 400

        enrollment = Enrollment(
            student_id=student.id,
            section_id=section.id,
            status="PENDING",
        )
        db.session.add(enrollment)
        db.session.commit()

        return jsonify({"message": "Added to schedule"}), 201

    
    @app.route("/api/schedule/remove", methods=["POST"])
    def remove_from_schedule():
        student = get_current_student()
        if not student:
            return jsonify({"error": "Student not found (missing or invalid email)."}), 404

        data = request.get_json() or {}
        section_id = data.get("section_id")
        if not section_id:
            return jsonify({"error": "section_id is required"}), 400

        enrollment = Enrollment.query.filter_by(
            student_id=student.id,
            section_id=section_id
        ).first()

        if not enrollment:
            return jsonify({"error": "Not in schedule"}), 404

        db.session.delete(enrollment)
        db.session.commit()

        return jsonify({"message": "Removed from schedule"}), 200

    
    @app.route("/api/schedule/confirm", methods=["POST"])
    def confirm_schedule():
        student = get_current_student()
        if not student:
            return jsonify({"error": "Student not found (missing or invalid email)."}), 404

        enrollments = Enrollment.query.filter_by(student_id=student.id).all()
        if not enrollments:
            return jsonify({"error": "No sections to confirm"}), 400

        for en in enrollments:
            en.status = "CONFIRMED"
        db.session.commit()

        return jsonify({"message": "Schedule confirmed"}), 200

   
    @app.route("/api/admin/enrollments")
    def admin_enrollments():
        admin = get_current_student()
        if not admin or (admin.role or "student") != "admin":
            return jsonify({"error": "Admin access only."}), 403

        enrollments = Enrollment.query.all()
        result = []
        for en in enrollments:
            stu = en.student
            sec = en.section
            course = sec.course

            result.append({
                "student_email": stu.email,
                "student_name": stu.name,
                "course_code": course.code,
                "course_title": course.title,
                "term": sec.term,
                "term_label": TERM_LABEL.get(sec.term, sec.term),
                "crn": sec.crn,
                "status": en.status,
            })

        return jsonify(result)

    return app

app = create_app()
  

if __name__ == "__main__":
    
    app.run(debug=True)

