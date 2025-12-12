
from werkzeug.security import generate_password_hash
from app import create_app
from models import db, Student, Course, Section, SectionMeeting, Prerequisite


def add_course(code, title, subject, credits, instructor,
               term, section_code, crn, meetings):
    """
    meetings: list of dicts like {"day": 1, "start": "09:00", "end": "10:15"}
    """
    course = Course.query.filter_by(code=code).first()
    if not course:
        course = Course(
            code=code,
            title=title,
            subject=subject,
            credits=credits,
            instructor=instructor,
        )
        db.session.add(course)
        db.session.flush()

    section = Section(
        crn=crn,
        term=term,
        section_code=section_code,
        course=course,
    )
    db.session.add(section)
    db.session.flush()

    for m in meetings:
        db.session.add(
            SectionMeeting(
                day_of_week=m["day"],
                start_time=m["start"],
                end_time=m["end"],
                section=section,
            )
        )

    return course


def seed():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        

        s1 = Student(
            email="student1@scholar.edu",
            name="Alice Student",
            password_hash=generate_password_hash("Student123!"),
            role="student",
        )
        s2 = Student(
            email="student2@scholar.edu",
            name="Bob Student",
            password_hash=generate_password_hash("Student234!"),
            role="student",
        )
        s3 = Student(
            email="student3@scholar.edu",
            name="Charlie Student",
            password_hash=generate_password_hash("Student345!"),
            role="student",
        )
        admin = Student(
            email="admin@scholar.edu",
            name="System Admin",
            password_hash=generate_password_hash("Admin123!"),
            role="admin",
        )

        db.session.add_all([s1, s2, s3, admin])
        db.session.flush()

        
        def MW(s, e):
            return [
                {"day": 1, "start": s, "end": e},
                {"day": 3, "start": s, "end": e},
            ]

        def TTh(s, e):
            return [
                {"day": 2, "start": s, "end": e},
                {"day": 4, "start": s, "end": e},
            ]

        def F(s, e):
            return [
                {"day": 5, "start": s, "end": e},
            ]

        

        add_course(
            code="CS 101", title="Intro to CS", subject="CS", credits=3,
            instructor="John Lee",
            term="FALL", section_code="001", crn=10001,
            meetings=MW("09:00", "10:15"),
        )

        add_course(
            code="CS 220", title="Data Structures", subject="CS", credits=4,
            instructor="Christopher Hernandez",
            term="FALL", section_code="002", crn=10002,
            meetings=TTh("10:30", "11:45"),
        )

        add_course(
            code="MATH 201", title="Calculus II", subject="MATH", credits=4,
            instructor="Sandra Rivera",
            term="FALL", section_code="001", crn=10003,
            meetings=MW("12:00", "13:15"),
        )

        add_course(
            code="MATH 140", title="Discrete Math", subject="MATH", credits=3,
            instructor="Johnny Perez",
            term="FALL", section_code="003", crn=10004,
            meetings=TTh("09:00", "10:15"),
        )

        add_course(
            code="ENG 110", title="English Writing", subject="ENG", credits=3,
            instructor="Chris Baker",
            term="FALL", section_code="001", crn=10005,
            meetings=F("11:00", "12:40"),
        )

        add_course(
            code="PHY 150", title="Physics I", subject="PHY", credits=4,
            instructor="Isabella Monje",
            term="FALL", section_code="002", crn=10006,
            meetings=MW("10:30", "11:45"),
        )

        add_course(
            code="HIST 210", title="Modern History", subject="HIST", credits=3,
            instructor="Max Ramirez",
            term="FALL", section_code="001", crn=10007,
            meetings=MW("09:30", "10:45"),
        )

        add_course(
            code="BIO 130", title="General Biology", subject="BIO", credits=4,
            instructor="Chloe Cena",
            term="FALL", section_code="001", crn=10008,
            meetings=TTh("10:30", "11:45"),
        )

        add_course(
            code="ART 105", title="Intro to Drawing", subject="ART", credits=2,
            instructor="Loida Sanchez",
            term="FALL", section_code="001", crn=10009,
            meetings=F("14:00", "15:15"),
        )

        add_course(
            code="STAT 250", title="Statistics I", subject="STAT", credits=3,
            instructor="Mark Cuban",
            term="FALL", section_code="001", crn=10010,
            meetings=TTh("13:30", "14:45"),
        )

        

        add_course(
            code="CS 102", title="Programming Fundamentals", subject="CS", credits=3,
            instructor="Grace Monroe",
            term="SPRING", section_code="001", crn=11001,
            meetings=MW("09:00", "10:15"),
        )

        add_course(
            code="CS 221", title="Algorithms", subject="CS", credits=4,
            instructor="Emma Harper",
            term="SPRING", section_code="001", crn=11002,
            meetings=TTh("10:30", "11:45"),
        )

        add_course(
            code="MATH 202", title="Calculus III", subject="MATH", credits=4,
            instructor="Olivia Addison",
            term="SPRING", section_code="001", crn=11003,
            meetings=MW("12:00", "13:15"),
        )

        add_course(
            code="MATH 240", title="Linear Algebra", subject="MATH", credits=3,
            instructor="Charlotte Garcia",
            term="SPRING", section_code="001", crn=11004,
            meetings=TTh("09:00", "10:15"),
        )

        add_course(
            code="ENG 210", title="Literary Analysis", subject="ENG", credits=3,
            instructor="Noah Smith",
            term="SPRING", section_code="001", crn=11005,
            meetings=F("11:00", "12:40"),
        )

        add_course(
            code="PHY 250", title="Physics II", subject="PHY", credits=4,
            instructor="John Williams",
            term="SPRING", section_code="001", crn=11006,
            meetings=MW("10:30", "11:45"),
        )

        add_course(
            code="HIST 220", title="World History", subject="HIST", credits=3,
            instructor="James Ramirez",
            term="SPRING", section_code="001", crn=11007,
            meetings=MW("09:30", "10:45"),
        )

        add_course(
            code="BIO 230", title="Cell Biology", subject="BIO", credits=4,
            instructor="Lucas Miller",
            term="SPRING", section_code="001", crn=11008,
            meetings=TTh("10:30", "11:45"),
        )

        add_course(
            code="ART 205", title="Painting I", subject="ART", credits=2,
            instructor="Ezra Martin",
            term="SPRING", section_code="001", crn=11009,
            meetings=F("14:00", "15:15"),
        )

        add_course(
            code="PSY 101", title="Intro to Psychology", subject="PSY", credits=3,
            instructor="Sebastian Garcia",
            term="SPRING", section_code="001", crn=11010,
            meetings=TTh("14:00", "15:15"),
        )

        

        add_course(
            code="CS 210", title="Web Development", subject="CS", credits=3,
            instructor="Morgan",
            term="SUMMER", section_code="001", crn=12001,
            meetings=TTh("09:00", "10:15"),
        )

        add_course(
            code="CS 330", title="Databases", subject="CS", credits=3,
            instructor="Hernandez",
            term="SUMMER", section_code="001", crn=12002,
            meetings=MW("10:30", "11:45"),
        )

        add_course(
            code="MATH 210", title="Probability", subject="MATH", credits=3,
            instructor="Chen",
            term="SUMMER", section_code="001", crn=12003,
            meetings=TTh("12:00", "13:15"),
        )

        add_course(
            code="STAT 320", title="Applied Statistics", subject="STAT", credits=3,
            instructor="Kim",
            term="SUMMER", section_code="001", crn=12004,
            meetings=MW("13:30", "14:45"),
        )

        add_course(
            code="ENG 230", title="Technical Writing", subject="ENG", credits=3,
            instructor="Jake",
            term="SUMMER", section_code="001", crn=12005,
            meetings=F("11:00", "12:40"),
        )

        add_course(
            code="PHY 210", title="Engineering Physics II", subject="PHY", credits=4,
            instructor="Ariana",
            term="SUMMER", section_code="001", crn=12006,
            meetings=MW("09:00", "10:15"),
        )

        add_course(
            code="HIST 230", title="US History", subject="HIST", credits=3,
            instructor="Valdez",
            term="SUMMER", section_code="001", crn=12007,
            meetings=MW("09:30", "10:45"),
        )

        add_course(
            code="BIO 240", title="Genetics", subject="BIO", credits=4,
            instructor="Peter",
            term="SUMMER", section_code="001", crn=12008,
            meetings=TTh("12:00", "13:15"),
        )

        add_course(
            code="ART 215", title="Digital Photography", subject="ART", credits=2,
            instructor="Bill",
            term="SUMMER", section_code="001", crn=12009,
            meetings=F("14:00", "15:15"),
        )

        add_course(
            code="PSY 220", title="Developmental Psychology", subject="PSY", credits=3,
            instructor="Jill",
            term="SUMMER", section_code="001", crn=12010,
            meetings=TTh("14:00", "15:15"),
        )

        db.session.commit()

        

        def get_course(code):
            return Course.query.filter_by(code=code).first()

        def add_prereq(course_code, prereq_code):
            course = get_course(course_code)
            prereq = get_course(prereq_code)
            if not course or not prereq:
                return
            exists = Prerequisite.query.filter_by(
                course_id=course.id,
                prereq_course_id=prereq.id
            ).first()
            if not exists:
                db.session.add(
                    Prerequisite(course_id=course.id, prereq_course_id=prereq.id)
                )

        
        add_prereq("CS 220", "CS 101")
        add_prereq("CS 221", "CS 220")
        add_prereq("CS 210", "CS 102")
        add_prereq("CS 330", "CS 220")

        
        add_prereq("MATH 202", "MATH 201")
        add_prereq("MATH 210", "MATH 140")
        add_prereq("STAT 250", "MATH 201")
        add_prereq("STAT 320", "STAT 250")

        
        add_prereq("PHY 250", "PHY 150")
        add_prereq("PHY 210", "PHY 150")
        add_prereq("BIO 230", "BIO 130")
        add_prereq("BIO 240", "BIO 230")

        
        add_prereq("PSY 220", "PSY 101")

        db.session.commit()
        print("Database seeded successfully with 3 students + 1 admin and 30 courses.")


if __name__ == "__main__":
    seed()
