
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="student")  

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Student {self.email} ({self.role})>"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.Integer, nullable=False)
    instructor = db.Column(db.String(255), nullable=False)

    sections = db.relationship(
        "Section",
        back_populates="course",
        cascade="all, delete-orphan"
    )
    prereqs = db.relationship(
        "Prerequisite",
        foreign_keys="Prerequisite.course_id",
        back_populates="course",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Course {self.code}>"


class Section(db.Model):
    __tablename__ = "sections"

    id = db.Column(db.Integer, primary_key=True)
    crn = db.Column(db.Integer, unique=True, nullable=False)
    term = db.Column(db.String(20), nullable=False)   
    section_code = db.Column(db.String(20), nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    course = db.relationship("Course", back_populates="sections")

    meetings = db.relationship(
        "SectionMeeting",
        back_populates="section",
        cascade="all, delete-orphan"
    )
    enrollments = db.relationship(
        "Enrollment",
        back_populates="section",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Section CRN={self.crn} term={self.term}>"


class SectionMeeting(db.Model):
    __tablename__ = "section_meetings"

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey("sections.id"), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  
    start_time = db.Column(db.String(5), nullable=False)  
    end_time = db.Column(db.String(5), nullable=False)    

    section = db.relationship("Section", back_populates="meetings")

    def __repr__(self):
        return f"<Meeting day={self.day_of_week} {self.start_time}-{self.end_time}>"


class Prerequisite(db.Model):
    __tablename__ = "prerequisites"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    prereq_course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)

    
    course = db.relationship(
        "Course",
        foreign_keys=[course_id],
        back_populates="prereqs"
    )
    
    prereq_course = db.relationship("Course", foreign_keys=[prereq_course_id])

    def __repr__(self):
        return f"<Prereq {self.course_id} requires {self.prereq_course_id}>"


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey("sections.id"), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="PENDING")  

    student = db.relationship("Student", back_populates="enrollments")
    section = db.relationship("Section", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment student={self.student_id} section={self.section_id} status={self.status}>"
