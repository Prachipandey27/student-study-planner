import os
from datetime import datetime, timedelta, timezone

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)


app = Flask(__name__)


# --------------------------------------------------
# APPLICATION CONFIGURATION
# --------------------------------------------------

app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY",
    "studytrack-local-development-key"
)


database_url = os.environ.get(
    "DATABASE_URL"
)


if database_url:

    # Some hosting providers may return
    # postgres:// instead of postgresql://
    if database_url.startswith(
        "postgres://"
    ):

        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )


    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = database_url

else:

    # Local development database
    app.config[
        "SQLALCHEMY_DATABASE_URI"
    ] = "sqlite:///studytrack.db"


app.config[
    "SQLALCHEMY_TRACK_MODIFICATIONS"
] = False


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

db = SQLAlchemy(app)


# --------------------------------------------------
# LOGIN MANAGER
# --------------------------------------------------

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = "login"

login_manager.login_message = (
    "Please log in to access your dashboard."
)

login_manager.login_message_category = "error"


# --------------------------------------------------
# USER MODEL
# --------------------------------------------------

class User(UserMixin, db.Model):

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False,
        index=True
    )

    password_hash = db.Column(
        db.String(255),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    subjects = db.relationship(
    "Subject",
    back_populates="user",
    cascade="all, delete-orphan"
    )

    tasks = db.relationship(
    "StudyTask",
    back_populates="user",
    cascade="all, delete-orphan"
    )

    study_sessions = db.relationship(
    "StudySession",
    back_populates="user",
    cascade="all, delete-orphan"
    )

    mark_records = db.relationship(
    "MarkRecord",
    back_populates="user",
    cascade="all, delete-orphan"
    )

    attendance_records = db.relationship(
    "AttendanceRecord",
    back_populates="user",
    cascade="all, delete-orphan"
    )


    def __repr__(self):

        return f"<User {self.email}>"



# --------------------------------------------------
# SUBJECT MODEL
# --------------------------------------------------

class Subject(db.Model):

    __tablename__ = "subjects"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    code = db.Column(
        db.String(30),
        nullable=True
    )

    target_marks = db.Column(
        db.Integer,
        default=75,
        nullable=False
    )

    target_study_hours = db.Column(
        db.Float,
        default=5.0,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="subjects"
    )

    tasks = db.relationship(
    "StudyTask",
    back_populates="subject",
    cascade="all, delete-orphan"
    )

    study_sessions = db.relationship(
    "StudySession",
    back_populates="subject",
    cascade="all, delete-orphan"
    )

    mark_records = db.relationship(
    "MarkRecord",
    back_populates="subject",
    cascade="all, delete-orphan"
    )

    attendance_records = db.relationship(
    "AttendanceRecord",
    back_populates="subject",
    cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "name",
            name="uq_user_subject_name"
        ),
    )

    def __repr__(self):

        return (
            f"<Subject {self.name} "
            f"User {self.user_id}>"
        )


# --------------------------------------------------
# STUDY TASK MODEL
# --------------------------------------------------

class StudyTask(db.Model):

    __tablename__ = "study_tasks"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    task_name = db.Column(
        db.String(150),
        nullable=False
    )

    deadline = db.Column(
        db.Date,
        nullable=False
    )

    priority = db.Column(
        db.String(20),
        default="Medium",
        nullable=False
    )

    status = db.Column(
        db.String(20),
        default="Pending",
        nullable=False
    )

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False,
        index=True
    )

    user = db.relationship(
        "User",
        back_populates="tasks"
    )

    subject = db.relationship(
        "Subject",
        back_populates="tasks"
    )

    def __repr__(self):

        return (
            f"<StudyTask {self.task_name} "
            f"User {self.user_id}>"
        )


# --------------------------------------------------
# STUDY SESSION MODEL
# --------------------------------------------------

class StudySession(db.Model):

    __tablename__ = "study_sessions"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    study_date = db.Column(
        db.Date,
        nullable=False
    )


    duration_minutes = db.Column(
        db.Integer,
        nullable=False
    )


    notes = db.Column(
        db.String(300),
        nullable=True
    )


    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )


    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False,
        index=True
    )


    user = db.relationship(
        "User",
        back_populates="study_sessions"
    )


    subject = db.relationship(
        "Subject",
        back_populates="study_sessions"
    )


    def __repr__(self):

        return (
            f"<StudySession "
            f"{self.duration_minutes} minutes "
            f"User {self.user_id}>"
        )

# --------------------------------------------------
# MARK RECORD MODEL
# --------------------------------------------------

class MarkRecord(db.Model):

    __tablename__ = "mark_records"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    assessment_name = db.Column(
        db.String(120),
        nullable=False
    )


    marks_obtained = db.Column(
        db.Float,
        nullable=False
    )


    maximum_marks = db.Column(
        db.Float,
        nullable=False
    )


    assessment_date = db.Column(
        db.Date,
        nullable=False
    )


    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )


    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False,
        index=True
    )


    user = db.relationship(
        "User",
        back_populates="mark_records"
    )


    subject = db.relationship(
        "Subject",
        back_populates="mark_records"
    )


    @property
    def percentage(self):

        if self.maximum_marks <= 0:
            return 0

        return round(
            (
                self.marks_obtained
                / self.maximum_marks
            )
            * 100,
            1
        )


    def __repr__(self):

        return (
            f"<MarkRecord "
            f"{self.assessment_name} "
            f"User {self.user_id}>"
        )

# --------------------------------------------------
# ATTENDANCE RECORD MODEL
# --------------------------------------------------

class AttendanceRecord(db.Model):

    __tablename__ = "attendance_records"


    id = db.Column(
        db.Integer,
        primary_key=True
    )


    attendance_date = db.Column(
        db.Date,
        nullable=False
    )


    classes_held = db.Column(
        db.Integer,
        nullable=False
    )


    classes_attended = db.Column(
        db.Integer,
        nullable=False
    )


    notes = db.Column(
        db.String(300),
        nullable=True
    )


    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )


    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False,
        index=True
    )


    user = db.relationship(
        "User",
        back_populates="attendance_records"
    )


    subject = db.relationship(
        "Subject",
        back_populates="attendance_records"
    )


    @property
    def percentage(self):

        if self.classes_held <= 0:
            return 0

        return round(
            (
                self.classes_attended
                / self.classes_held
            )
            * 100,
            1
        )


    def __repr__(self):

        return (
            f"<AttendanceRecord "
            f"{self.attendance_date} "
            f"User {self.user_id}>"
        )
# --------------------------------------------------
# LOAD LOGGED-IN USER
# --------------------------------------------------

@login_manager.user_loader
def load_user(user_id):

    return db.session.get(
        User,
        int(user_id)
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# --------------------------------------------------
# SIGNUP
# --------------------------------------------------

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        full_name = (
            request.form
            .get("full_name", "")
            .strip()
        )

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        if not full_name:

            flash(
                "Please enter your full name.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if not email:

            flash(
                "Please enter your email address.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if len(password) < 8:

            flash(
                "Password must contain at least 8 characters.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        existing_user = (
            User.query
            .filter_by(email=email)
            .first()
        )

        if existing_user:

            flash(
                "An account with this email already exists.",
                "error"
            )

            return render_template(
                "signup.html"
            )

        password_hash = generate_password_hash(
            password
        )

        new_user = User(
            full_name=full_name,
            email=email,
            password_hash=password_hash
        )

        db.session.add(
            new_user
        )

        db.session.commit()

        flash(
            "Account created successfully. Please log in.",
            "success"
        )

        return redirect(
            url_for("login")
        )

    return render_template(
        "signup.html"
    )


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if current_user.is_authenticated:

        return redirect(
            url_for("dashboard")
        )

    if request.method == "POST":

        email = (
            request.form
            .get("email", "")
            .strip()
            .lower()
        )

        password = request.form.get(
            "password",
            ""
        )

        user = (
            User.query
            .filter_by(email=email)
            .first()
        )

        if (
            user
            and check_password_hash(
                user.password_hash,
                password
            )
        ):

            login_user(user)

            flash(
                "Welcome back to StudyTrack.",
                "success"
            )

            return redirect(
                url_for("dashboard")
            )

        flash(
            "Invalid email address or password.",
            "error"
        )

    return render_template(
        "login.html"
    )

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():

    today = datetime.now(
        timezone.utc
    ).date()


    # ------------------------------------------
    # SUBJECT DATA
    # ------------------------------------------

    total_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .count()
    )


    # ------------------------------------------
    # TASK DATA
    # ------------------------------------------

    student_tasks = (
        StudyTask.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            StudyTask.deadline.asc()
        )
        .all()
    )


    pending_tasks = []

    overdue_tasks = []

    completed_tasks = []


    for task in student_tasks:

        if task.status == "Completed":

            completed_tasks.append(
                task
            )

        elif task.deadline < today:

            overdue_tasks.append(
                task
            )

        else:

            pending_tasks.append(
                task
            )


    # ------------------------------------------
    # UPCOMING TASKS
    # ------------------------------------------

    upcoming_tasks = (
        pending_tasks[:5]
    )


    # ------------------------------------------
    # TASK COMPLETION RATE
    # ------------------------------------------

    total_tasks = len(
        student_tasks
    )


    if total_tasks > 0:

        completion_rate = round(
            (
                len(completed_tasks)
                / total_tasks
            )
            * 100
        )

    else:

        completion_rate = 0

    # ==========================================
    # DASHBOARD STUDY TIME
    # ==========================================

    today = datetime.now(
        timezone.utc
    ).date()


    week_start = (
        today
        - timedelta(
            days=today.weekday()
        )
    )


    dashboard_week_sessions = (
        StudySession.query
        .filter(
            StudySession.user_id
            == current_user.id,

            StudySession.study_date
            >= week_start,

            StudySession.study_date
            <= today
        )
        .all()
    )


    dashboard_week_minutes = sum(
        session.duration_minutes
        for session in dashboard_week_sessions
    )


    dashboard_week_hours = round(
        dashboard_week_minutes / 60,
        1
    )

    # ==========================================
    # DASHBOARD PERFORMANCE
    # ==========================================

    dashboard_marks = (
        MarkRecord.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )


    dashboard_marks_obtained = sum(
        mark.marks_obtained
        for mark in dashboard_marks
    )


    dashboard_maximum_marks = sum(
        mark.maximum_marks
        for mark in dashboard_marks
    )


    if dashboard_maximum_marks > 0:

        dashboard_performance = round(
            (
                dashboard_marks_obtained
                / dashboard_maximum_marks
            )
            * 100,
            1
        )

    else:

        dashboard_performance = 0

    # ==========================================
    # DASHBOARD ATTENDANCE
    # ==========================================

    dashboard_attendance_records = (
        AttendanceRecord.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )


    dashboard_classes_attended = sum(
        record.classes_attended
        for record in dashboard_attendance_records
    )


    dashboard_classes_held = sum(
        record.classes_held
        for record in dashboard_attendance_records
    )


    if dashboard_classes_held > 0:

        dashboard_attendance = round(
            (
                dashboard_classes_attended
                / dashboard_classes_held
            )
            * 100,
            1
        )

    else:

        dashboard_attendance = 0

    


    # ------------------------------------------
    # DASHBOARD TEMPLATE
    # ------------------------------------------

    return render_template(
        "dashboard.html",

        total_subjects=total_subjects,

        total_tasks=total_tasks,

        pending_tasks=pending_tasks,

        overdue_tasks=overdue_tasks,

        completed_tasks=completed_tasks,

        upcoming_tasks=upcoming_tasks,

        completion_rate=completion_rate,

        today=today,

        dashboard_week_hours=dashboard_week_hours,
        dashboard_week_minutes=dashboard_week_minutes,
        dashboard_performance=dashboard_performance,
        dashboard_attendance=dashboard_attendance,
        dashboard_classes_attended=dashboard_classes_attended,
        dashboard_classes_held=dashboard_classes_held,
    )


# --------------------------------------------------
# SUBJECTS
# --------------------------------------------------

@app.route("/subjects")
@login_required
def subjects():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.created_at.desc()
        )
        .all()
    )

    return render_template(
        "subjects.html",
        subjects=student_subjects
    )

# --------------------------------------------------
# SUBJECT DETAIL
# --------------------------------------------------

@app.route("/subjects/<int:subject_id>")
@login_required
def subject_detail(subject_id):

    subject = (
        Subject.query
        .filter_by(
            id=subject_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    today = datetime.now(
        timezone.utc
    ).date()


    week_start = (
        today
        - timedelta(
            days=today.weekday()
        )
    )


    # ==========================================
    # SUBJECT TASKS
    # ==========================================

    subject_tasks = (
        StudyTask.query
        .filter_by(
            subject_id=subject.id,
            user_id=current_user.id
        )
        .order_by(
            StudyTask.deadline.asc()
        )
        .all()
    )


    pending_subject_tasks = []

    overdue_subject_tasks = []

    completed_subject_tasks = []


    for task in subject_tasks:

        if task.status == "Completed":

            completed_subject_tasks.append(
                task
            )

        elif task.deadline < today:

            overdue_subject_tasks.append(
                task
            )

        else:

            pending_subject_tasks.append(
                task
            )


    # ==========================================
    # SUBJECT STUDY SESSIONS
    # ==========================================

    subject_sessions = (
        StudySession.query
        .filter_by(
            subject_id=subject.id,
            user_id=current_user.id
        )
        .order_by(
            StudySession.study_date.desc(),
            StudySession.created_at.desc()
        )
        .all()
    )


    subject_total_minutes = sum(
        session.duration_minutes
        for session in subject_sessions
    )


    subject_week_minutes = sum(
        session.duration_minutes
        for session in subject_sessions
        if (
            week_start
            <= session.study_date
            <= today
        )
    )


    subject_target_minutes = round(
        subject.target_study_hours
        * 60
    )


    if subject_target_minutes > 0:

        subject_week_progress = round(
            (
                subject_week_minutes
                / subject_target_minutes
            )
            * 100
        )

        subject_week_progress = min(
            subject_week_progress,
            100
        )

    else:

        subject_week_progress = 0


    recent_subject_sessions = (
        subject_sessions[:5]
    )


    # ==========================================
    # SUBJECT MARKS
    # ==========================================

    subject_marks = (
        MarkRecord.query
        .filter_by(
            subject_id=subject.id,
            user_id=current_user.id
        )
        .order_by(
            MarkRecord.assessment_date.desc(),
            MarkRecord.created_at.desc()
        )
        .all()
    )


    subject_marks_obtained = sum(
        mark.marks_obtained
        for mark in subject_marks
    )


    subject_maximum_marks = sum(
        mark.maximum_marks
        for mark in subject_marks
    )


    if subject_maximum_marks > 0:

        subject_current_percentage = round(
            (
                subject_marks_obtained
                / subject_maximum_marks
            )
            * 100,
            1
        )

    else:

        subject_current_percentage = 0


    subject_target_difference = round(
        subject_current_percentage
        - subject.target_marks,
        1
    )


    recent_subject_marks = (
        subject_marks[:5]
    )

    # ==========================================
    # SUBJECT ATTENDANCE
    # ==========================================

    subject_attendance_records = (
        AttendanceRecord.query
        .filter_by(
            subject_id=subject.id,
            user_id=current_user.id
        )
        .order_by(
            AttendanceRecord.attendance_date.desc(),
            AttendanceRecord.created_at.desc()
        )
        .all()
    )


    subject_classes_held = sum(
        record.classes_held
        for record in subject_attendance_records
    )


    subject_classes_attended = sum(
        record.classes_attended
        for record in subject_attendance_records
    )


    if subject_classes_held > 0:

        subject_attendance_percentage = round(
            (
                subject_classes_attended
                / subject_classes_held
            )
            * 100,
            1
        )

    else:

        subject_attendance_percentage = 0


    recent_subject_attendance = (
        subject_attendance_records[:5]
    )



    # ==========================================
    # TEMPLATE
    # ==========================================

    return render_template(
        "subject_detail.html",

        subject=subject,

        # Tasks
        subject_tasks=subject_tasks,
        pending_subject_tasks=pending_subject_tasks,
        overdue_subject_tasks=overdue_subject_tasks,
        completed_subject_tasks=completed_subject_tasks,

        # Study sessions
        subject_sessions=subject_sessions,
        recent_subject_sessions=recent_subject_sessions,
        subject_total_minutes=subject_total_minutes,
        subject_week_minutes=subject_week_minutes,
        subject_target_minutes=subject_target_minutes,
        subject_week_progress=subject_week_progress,

        # Marks
        subject_marks=subject_marks,
        recent_subject_marks=recent_subject_marks,
        subject_marks_obtained=subject_marks_obtained,
        subject_maximum_marks=subject_maximum_marks,
        subject_current_percentage=subject_current_percentage,
        subject_target_difference=subject_target_difference,
        assessment_count=len(subject_marks),

        # Attendance
        subject_attendance_records=subject_attendance_records,
        recent_subject_attendance=recent_subject_attendance,
        subject_classes_held=subject_classes_held,
        subject_classes_attended=subject_classes_attended,
        subject_attendance_percentage=subject_attendance_percentage,
        attendance_record_count=len(subject_attendance_records),

        today=today,
        week_start=week_start
    )



# --------------------------------------------------
# ADD SUBJECT
# --------------------------------------------------

@app.route(
    "/subjects/add",
    methods=["GET", "POST"]
)
@login_required
def add_subject():

    if request.method == "POST":

        name = (
            request.form
            .get("name", "")
            .strip()
        )

        code = (
            request.form
            .get("code", "")
            .strip()
        )

        target_marks_raw = request.form.get(
            "target_marks",
            "75"
        )

        target_study_hours_raw = request.form.get(
            "target_study_hours",
            "5"
        )


        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not name:

            flash(
                "Please enter a subject name.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        if len(name) > 100:

            flash(
                "Subject name must be 100 characters or fewer.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        if len(code) > 30:

            flash(
                "Subject code must be 30 characters or fewer.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        try:

            target_marks = int(
                target_marks_raw
            )

        except ValueError:

            flash(
                "Target marks must be a valid number.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        try:

            target_study_hours = float(
                target_study_hours_raw
            )

        except ValueError:

            flash(
                "Weekly study target must be a valid number.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        if not 1 <= target_marks <= 100:

            flash(
                "Target marks must be between 1 and 100.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        if not 0.5 <= target_study_hours <= 100:

            flash(
                "Weekly study target must be between 0.5 and 100 hours.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        existing_subject = (
            Subject.query
            .filter(
                Subject.user_id
                == current_user.id,

                db.func.lower(
                    Subject.name
                )
                == name.lower()
            )
            .first()
        )


        if existing_subject:

            flash(
                "You already have a subject with this name.",
                "error"
            )

            return render_template(
                "add_subject.html"
            )


        # ------------------------------------------
        # CREATE SUBJECT
        # ------------------------------------------

        new_subject = Subject(
            name=name,
            code=code if code else None,
            target_marks=target_marks,
            target_study_hours=target_study_hours,
            user_id=current_user.id
        )


        db.session.add(
            new_subject
        )

        db.session.commit()


        flash(
            f"{name} was added successfully.",
            "success"
        )


        return redirect(
            url_for("subjects")
        )


    return render_template(
        "add_subject.html"
    )


# --------------------------------------------------
# EDIT SUBJECT
# --------------------------------------------------

@app.route(
    "/subjects/<int:subject_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_subject(subject_id):

    subject = (
        Subject.query
        .filter_by(
            id=subject_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    if request.method == "POST":

        name = (
            request.form
            .get("name", "")
            .strip()
        )

        code = (
            request.form
            .get("code", "")
            .strip()
        )

        target_marks_raw = request.form.get(
            "target_marks",
            "75"
        )

        target_study_hours_raw = request.form.get(
            "target_study_hours",
            "5"
        )


        # ------------------------------------------
        # VALIDATION
        # ------------------------------------------

        if not name:

            flash(
                "Please enter a subject name.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        if len(name) > 100:

            flash(
                "Subject name must be 100 characters or fewer.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        if len(code) > 30:

            flash(
                "Subject code must be 30 characters or fewer.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        try:

            target_marks = int(
                target_marks_raw
            )

        except ValueError:

            flash(
                "Target marks must be a valid number.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        try:

            target_study_hours = float(
                target_study_hours_raw
            )

        except ValueError:

            flash(
                "Weekly study target must be a valid number.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        if not 1 <= target_marks <= 100:

            flash(
                "Target marks must be between 1 and 100.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        if not 0.5 <= target_study_hours <= 100:

            flash(
                "Weekly study target must be between 0.5 and 100 hours.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        # ------------------------------------------
        # DUPLICATE CHECK
        # ------------------------------------------

        existing_subject = (
            Subject.query
            .filter(
                Subject.user_id
                == current_user.id,

                Subject.id
                != subject.id,

                db.func.lower(
                    Subject.name
                )
                == name.lower()
            )
            .first()
        )


        if existing_subject:

            flash(
                "You already have another subject with this name.",
                "error"
            )

            return render_template(
                "edit_subject.html",
                subject=subject
            )


        # ------------------------------------------
        # UPDATE SUBJECT
        # ------------------------------------------

        subject.name = name

        subject.code = (
            code if code else None
        )

        subject.target_marks = (
            target_marks
        )

        subject.target_study_hours = (
            target_study_hours
        )


        db.session.commit()


        flash(
            f"{subject.name} was updated successfully.",
            "success"
        )


        return redirect(
            url_for("subjects")
        )


    return render_template(
        "edit_subject.html",
        subject=subject
    )

# --------------------------------------------------
# DELETE SUBJECT
# --------------------------------------------------

@app.route(
    "/subjects/<int:subject_id>/delete",
    methods=["POST"]
)
@login_required
def delete_subject(subject_id):

    subject = (
        Subject.query
        .filter_by(
            id=subject_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    subject_name = subject.name

    db.session.delete(subject)

    db.session.commit()

    flash(
        f"{subject_name} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("subjects")
    )

# --------------------------------------------------
# STUDY PLANNER
# --------------------------------------------------

@app.route("/planner")
@login_required
def planner():

    today = datetime.now(
        timezone.utc
    ).date()

    student_tasks = (
        StudyTask.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            StudyTask.deadline.asc()
        )
        .all()
    )

    pending_tasks = []

    overdue_tasks = []

    completed_tasks = []


    for task in student_tasks:

        if task.status == "Completed":

            completed_tasks.append(
                task
            )

        elif task.deadline < today:

            overdue_tasks.append(
                task
            )

        else:

            pending_tasks.append(
                task
            )


    return render_template(
        "planner.html",
        pending_tasks=pending_tasks,
        overdue_tasks=overdue_tasks,
        completed_tasks=completed_tasks,
        today=today
    )


# --------------------------------------------------
# STUDY LOG
# --------------------------------------------------

@app.route("/study-log")
@login_required
def study_log():

    today = datetime.now(
        timezone.utc
    ).date()


    # Monday of the current week
    week_start = (
        today
        - timedelta(
            days=today.weekday()
        )
    )


    # ------------------------------------------
    # STUDY SESSIONS
    # ------------------------------------------

    student_sessions = (
        StudySession.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            StudySession.study_date.desc(),
            StudySession.created_at.desc()
        )
        .all()
    )


    # ------------------------------------------
    # TOTAL STUDY TIME
    # ------------------------------------------

    total_minutes = sum(
        session.duration_minutes
        for session in student_sessions
    )


    # ------------------------------------------
    # TODAY'S STUDY TIME
    # ------------------------------------------

    today_minutes = sum(
        session.duration_minutes
        for session in student_sessions
        if session.study_date == today
    )


    # ------------------------------------------
    # THIS WEEK'S STUDY TIME
    # ------------------------------------------

    week_minutes = sum(
        session.duration_minutes
        for session in student_sessions
        if (
            week_start
            <= session.study_date
            <= today
        )
    )


    # ------------------------------------------
    # WEEKLY STUDY TARGET
    # ------------------------------------------

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .all()
    )


    weekly_target_minutes = round(
        sum(
            subject.target_study_hours
            for subject in student_subjects
        )
        * 60
    )


    if weekly_target_minutes > 0:

        weekly_progress = round(
            (
                week_minutes
                / weekly_target_minutes
            )
            * 100
        )

        weekly_progress = min(
            weekly_progress,
            100
        )

    else:

        weekly_progress = 0


    return render_template(
        "study_log.html",

        sessions=student_sessions,
        recent_sessions=student_sessions[:6],

        total_minutes=total_minutes,
        today_minutes=today_minutes,
        week_minutes=week_minutes,

        session_count=len(
            student_sessions
        ),

        weekly_target_minutes=weekly_target_minutes,
        weekly_progress=weekly_progress,

        today=today,
        week_start=week_start
    )

# --------------------------------------------------
# PERFORMANCE
# --------------------------------------------------

@app.route("/performance")
@login_required
def performance():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    student_marks = (
        MarkRecord.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            MarkRecord.assessment_date.desc(),
            MarkRecord.created_at.desc()
        )
        .all()
    )


    # ------------------------------------------
    # OVERALL PERFORMANCE
    # ------------------------------------------

    total_marks_obtained = sum(
        mark.marks_obtained
        for mark in student_marks
    )


    total_maximum_marks = sum(
        mark.maximum_marks
        for mark in student_marks
    )


    if total_maximum_marks > 0:

        overall_percentage = round(
            (
                total_marks_obtained
                / total_maximum_marks
            )
            * 100,
            1
        )

    else:

        overall_percentage = 0


    # ------------------------------------------
    # SUBJECT-WISE PERFORMANCE
    # ------------------------------------------

    subject_performance = []


    for subject in student_subjects:

        subject_marks = [
            mark
            for mark in student_marks
            if mark.subject_id == subject.id
        ]


        obtained = sum(
            mark.marks_obtained
            for mark in subject_marks
        )


        maximum = sum(
            mark.maximum_marks
            for mark in subject_marks
        )


        if maximum > 0:

            current_percentage = round(
                (
                    obtained
                    / maximum
                )
                * 100,
                1
            )

        else:

            current_percentage = 0


        difference = round(
            current_percentage
            - subject.target_marks,
            1
        )


        subject_performance.append(
            {
                "subject": subject,
                "assessment_count": len(
                    subject_marks
                ),
                "current_percentage":
                    current_percentage,
                "difference": difference
            }
        )


    return render_template(
        "performance.html",

        subjects=student_subjects,

        marks=student_marks,

        recent_marks=student_marks[:6],

        subject_performance=
            subject_performance,

        overall_percentage=
            overall_percentage,

        assessment_count=len(
            student_marks
        ),

        total_marks_obtained=
            total_marks_obtained,

        total_maximum_marks=
            total_maximum_marks
    )

# --------------------------------------------------
# ATTENDANCE
# --------------------------------------------------

@app.route("/attendance")
@login_required
def attendance():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    attendance_records = (
        AttendanceRecord.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            AttendanceRecord.attendance_date.desc(),
            AttendanceRecord.created_at.desc()
        )
        .all()
    )


    # ------------------------------------------
    # OVERALL ATTENDANCE
    # ------------------------------------------

    total_classes_held = sum(
        record.classes_held
        for record in attendance_records
    )


    total_classes_attended = sum(
        record.classes_attended
        for record in attendance_records
    )


    if total_classes_held > 0:

        overall_attendance = round(
            (
                total_classes_attended
                / total_classes_held
            )
            * 100,
            1
        )

    else:

        overall_attendance = 0


    # ------------------------------------------
    # SUBJECT-WISE ATTENDANCE
    # ------------------------------------------

    subject_attendance = []


    for subject in student_subjects:

        subject_records = [
            record
            for record in attendance_records
            if record.subject_id == subject.id
        ]


        subject_classes_held = sum(
            record.classes_held
            for record in subject_records
        )


        subject_classes_attended = sum(
            record.classes_attended
            for record in subject_records
        )


        if subject_classes_held > 0:

            subject_percentage = round(
                (
                    subject_classes_attended
                    / subject_classes_held
                )
                * 100,
                1
            )

        else:

            subject_percentage = 0


        subject_attendance.append(
            {
                "subject": subject,
                "records": subject_records,
                "record_count": len(
                    subject_records
                ),
                "classes_held":
                    subject_classes_held,
                "classes_attended":
                    subject_classes_attended,
                "percentage":
                    subject_percentage
            }
        )


    subjects_with_attendance = sum(
        1
        for item in subject_attendance
        if item["record_count"] > 0
    )


    return render_template(
        "attendance.html",

        subjects=student_subjects,

        records=attendance_records,

        recent_records=
            attendance_records[:6],

        subject_attendance=
            subject_attendance,

        overall_attendance=
            overall_attendance,

        total_classes_held=
            total_classes_held,

        total_classes_attended=
            total_classes_attended,

        attendance_record_count=len(
            attendance_records
        ),

        subjects_with_attendance=
            subjects_with_attendance
    )

# --------------------------------------------------
# ADD ATTENDANCE
# --------------------------------------------------

@app.route(
    "/attendance/add",
    methods=["GET", "POST"]
)
@login_required
def add_attendance():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    # A subject is required before attendance
    # can be recorded.
    if not student_subjects:

        flash(
            "Add at least one subject before recording attendance.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )


    today = datetime.now(
        timezone.utc
    ).date()


    selected_subject_id = request.args.get(
        "subject_id",
        type=int
    )


    if request.method == "POST":

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        attendance_date_raw = request.form.get(
            "attendance_date",
            ""
        )

        classes_held_raw = request.form.get(
            "classes_held",
            ""
        )

        classes_attended_raw = request.form.get(
            "classes_attended",
            ""
        )

        notes = (
            request.form
            .get("notes", "")
            .strip()
        )


        # ------------------------------------------
        # SUBJECT
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # DATE
        # ------------------------------------------

        try:

            attendance_date = datetime.strptime(
                attendance_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid attendance date.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if attendance_date > today:

            flash(
                "Attendance cannot be recorded for a future date.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # CLASSES
        # ------------------------------------------

        try:

            classes_held = int(
                classes_held_raw
            )

            classes_attended = int(
                classes_attended_raw
            )

        except ValueError:

            flash(
                "Please enter valid class counts.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if classes_held <= 0:

            flash(
                "Classes held must be greater than zero.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if classes_attended < 0:

            flash(
                "Classes attended cannot be negative.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if classes_attended > classes_held:

            flash(
                "Classes attended cannot be greater than classes held.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # Prevent unrealistic accidental entries
        if classes_held > 50:

            flash(
                "A single attendance record cannot contain more than 50 classes.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # NOTES
        # ------------------------------------------

        if len(notes) > 300:

            flash(
                "Notes must be 300 characters or fewer.",
                "error"
            )

            return render_template(
                "add_attendance.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # CREATE RECORD
        # ------------------------------------------

        new_attendance = AttendanceRecord(
            attendance_date=attendance_date,
            classes_held=classes_held,
            classes_attended=classes_attended,
            notes=notes if notes else None,
            user_id=current_user.id,
            subject_id=subject.id
        )


        db.session.add(
            new_attendance
        )

        db.session.commit()


        flash(
            f"Attendance for {subject.name} was recorded successfully.",
            "success"
        )


        return redirect(
            url_for("attendance")
        )


    return render_template(
        "add_attendance.html",
        subjects=student_subjects,
        today=today,
        selected_subject_id=selected_subject_id
    )

# --------------------------------------------------
# ANALYTICS
# --------------------------------------------------

@app.route("/analytics")
@login_required
def analytics():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    subject_analytics = []


    # Used for mathematically correct overall values
    overall_marks_obtained = 0
    overall_maximum_marks = 0

    overall_classes_attended = 0
    overall_classes_held = 0

    overall_task_count = 0
    overall_completed_tasks = 0

    overall_study_minutes = 0


    for subject in student_subjects:


        # ==========================================
        # STUDY TIME
        # ==========================================

        sessions = (
            StudySession.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        subject_study_minutes = sum(
            session.duration_minutes
            for session in sessions
        )


        overall_study_minutes += (
            subject_study_minutes
        )


        study_hours = round(
            subject_study_minutes / 60,
            1
        )


        # ==========================================
        # PERFORMANCE
        # ==========================================

        marks = (
            MarkRecord.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        marks_obtained = sum(
            mark.marks_obtained
            for mark in marks
        )


        maximum_marks = sum(
            mark.maximum_marks
            for mark in marks
        )


        overall_marks_obtained += (
            marks_obtained
        )

        overall_maximum_marks += (
            maximum_marks
        )


        if maximum_marks > 0:

            performance_percentage = round(
                (
                    marks_obtained
                    / maximum_marks
                )
                * 100,
                1
            )

        else:

            performance_percentage = 0


        # ==========================================
        # ATTENDANCE
        # ==========================================

        attendance_entries = (
            AttendanceRecord.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        classes_attended = sum(
            record.classes_attended
            for record in attendance_entries
        )


        classes_held = sum(
            record.classes_held
            for record in attendance_entries
        )


        overall_classes_attended += (
            classes_attended
        )

        overall_classes_held += (
            classes_held
        )


        if classes_held > 0:

            attendance_percentage = round(
                (
                    classes_attended
                    / classes_held
                )
                * 100,
                1
            )

        else:

            attendance_percentage = 0


        # ==========================================
        # TASKS
        # ==========================================

        tasks = (
            StudyTask.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        completed_tasks = sum(
            1
            for task in tasks
            if task.status == "Completed"
        )


        overall_task_count += len(
            tasks
        )

        overall_completed_tasks += (
            completed_tasks
        )


        if tasks:

            task_completion = round(
                (
                    completed_tasks
                    / len(tasks)
                )
                * 100,
                1
            )

        else:

            task_completion = 0


        # ==========================================
        # COMBINED SUBJECT DATA
        # ==========================================

        subject_analytics.append(
            {
                "name": subject.name,
                "code": subject.code,
                "study_hours": study_hours,
                "performance":
                    performance_percentage,
                "attendance":
                    attendance_percentage,
                "task_completion":
                    task_completion
            }
        )


    # ==========================================
    # OVERALL STUDY HOURS
    # ==========================================

    total_study_hours = round(
        overall_study_minutes / 60,
        1
    )


    # ==========================================
    # OVERALL PERFORMANCE
    # ==========================================

    if overall_maximum_marks > 0:

        overall_performance = round(
            (
                overall_marks_obtained
                / overall_maximum_marks
            )
            * 100,
            1
        )

    else:

        overall_performance = 0


    # ==========================================
    # OVERALL ATTENDANCE
    # ==========================================

    if overall_classes_held > 0:

        overall_attendance = round(
            (
                overall_classes_attended
                / overall_classes_held
            )
            * 100,
            1
        )

    else:

        overall_attendance = 0


    # ==========================================
    # OVERALL TASK COMPLETION
    # ==========================================

    if overall_task_count > 0:

        overall_task_completion = round(
            (
                overall_completed_tasks
                / overall_task_count
            )
            * 100,
            1
        )

    else:

        overall_task_completion = 0


    # ==========================================
    # CHART DATA
    # ==========================================

    chart_labels = [
        item["name"]
        for item in subject_analytics
    ]


    study_hours_data = [
        item["study_hours"]
        for item in subject_analytics
    ]


    performance_data = [
        item["performance"]
        for item in subject_analytics
    ]


    attendance_data = [
        item["attendance"]
        for item in subject_analytics
    ]


    task_completion_data = [
        item["task_completion"]
        for item in subject_analytics
    ]


    return render_template(
        "analytics.html",

        subject_analytics=
            subject_analytics,

        total_study_hours=
            total_study_hours,

        overall_performance=
            overall_performance,

        overall_attendance=
            overall_attendance,

        overall_task_completion=
            overall_task_completion,

        subject_count=len(
            student_subjects
        ),

        chart_labels=
            chart_labels,

        study_hours_data=
            study_hours_data,

        performance_data=
            performance_data,

        attendance_data=
            attendance_data,

        task_completion_data=
            task_completion_data
    )

# --------------------------------------------------
# STUDY PRIORITIES
# --------------------------------------------------

@app.route("/priorities")
@login_required
def priorities():

    today = datetime.now(
        timezone.utc
    ).date()


    week_start = (
        today
        - timedelta(
            days=today.weekday()
        )
    )


    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    priority_items = []


    for subject in student_subjects:


        # ==========================================
        # PERFORMANCE
        # ==========================================

        marks = (
            MarkRecord.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        total_obtained = sum(
            mark.marks_obtained
            for mark in marks
        )


        total_maximum = sum(
            mark.maximum_marks
            for mark in marks
        )


        if total_maximum > 0:

            performance = round(
                (
                    total_obtained
                    / total_maximum
                )
                * 100,
                1
            )

        else:

            performance = None


        if performance is not None:

            performance_gap = max(
                subject.target_marks
                - performance,
                0
            )

        else:

            performance_gap = 0


        # ==========================================
        # WEEKLY STUDY TIME
        # ==========================================

        week_sessions = (
            StudySession.query
            .filter(
                StudySession.user_id
                == current_user.id,

                StudySession.subject_id
                == subject.id,

                StudySession.study_date
                >= week_start,

                StudySession.study_date
                <= today
            )
            .all()
        )


        week_minutes = sum(
            session.duration_minutes
            for session in week_sessions
        )


        week_hours = round(
            week_minutes / 60,
            1
        )


        study_target = (
            subject.target_study_hours
        )


        study_gap = max(
            study_target
            - week_hours,
            0
        )


        # ==========================================
        # TASKS
        # ==========================================

        subject_tasks = (
            StudyTask.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        overdue_tasks = [
            task
            for task in subject_tasks
            if (
                task.status != "Completed"
                and
                task.deadline < today
            )
        ]


        pending_tasks = [
            task
            for task in subject_tasks
            if (
                task.status != "Completed"
                and
                task.deadline >= today
            )
        ]


        # ==========================================
        # ATTENDANCE
        # ==========================================

        attendance_records = (
            AttendanceRecord.query
            .filter_by(
                user_id=current_user.id,
                subject_id=subject.id
            )
            .all()
        )


        classes_attended = sum(
            record.classes_attended
            for record in attendance_records
        )


        classes_held = sum(
            record.classes_held
            for record in attendance_records
        )


        if classes_held > 0:

            attendance = round(
                (
                    classes_attended
                    / classes_held
                )
                * 100,
                1
            )

        else:

            attendance = None


        # ==========================================
        # PRIORITY SCORE
        # ==========================================

        priority_score = 0


        # Performance contributes up to 40 points
        if (
            performance is not None
            and subject.target_marks > 0
        ):

            priority_score += min(
                (
                    performance_gap
                    / subject.target_marks
                )
                * 40,
                40
            )


        # Study gap contributes up to 25 points
        if study_target > 0:

            priority_score += min(
                (
                    study_gap
                    / study_target
                )
                * 25,
                25
            )


        # Overdue tasks contribute up to 25 points
        priority_score += min(
            len(overdue_tasks) * 10,
            25
        )


        # Attendance contributes up to 10 points
        if attendance is not None:

            priority_score += (
                (
                    100
                    - attendance
                )
                / 100
            ) * 10


        priority_score = round(
            min(priority_score, 100),
            1
        )


        # ==========================================
        # PRIORITY LEVEL
        # ==========================================

        if priority_score >= 60:

            priority_level = "High"

        elif priority_score >= 30:

            priority_level = "Medium"

        else:

            priority_level = "Low"


        # ==========================================
        # REASONS
        # ==========================================

        reasons = []


        if (
            performance is not None
            and performance < subject.target_marks
        ):

            reasons.append(
                f"Performance is "
                f"{round(performance_gap, 1)}% "
                f"below target"
            )


        if week_hours < study_target:

            reasons.append(
                f"{round(study_gap, 1)}h "
                f"remaining toward weekly target"
            )


        if overdue_tasks:

            reasons.append(
                f"{len(overdue_tasks)} "
                f"overdue task"
                f"{'s' if len(overdue_tasks) != 1 else ''}"
            )


        if (
            attendance is not None
            and attendance < 100
        ):

            reasons.append(
                f"Attendance currently "
                f"{attendance}%"
            )


        if not reasons:

            reasons.append(
                "No major issues detected"
            )


        priority_items.append(
            {
                "subject": subject,
                "score": priority_score,
                "level": priority_level,
                "performance": performance,
                "target_marks":
                    subject.target_marks,
                "week_hours": week_hours,
                "study_target":
                    study_target,
                "attendance": attendance,
                "overdue_count":
                    len(overdue_tasks),
                "pending_count":
                    len(pending_tasks),
                "reasons": reasons
            }
        )


    # Highest priority first
    priority_items.sort(
        key=lambda item: item["score"],
        reverse=True
    )


    high_count = sum(
        1
        for item in priority_items
        if item["level"] == "High"
    )


    medium_count = sum(
        1
        for item in priority_items
        if item["level"] == "Medium"
    )


    low_count = sum(
        1
        for item in priority_items
        if item["level"] == "Low"
    )


    return render_template(
        "priorities.html",
        priority_items=priority_items,
        high_count=high_count,
        medium_count=medium_count,
        low_count=low_count,
        subject_count=len(student_subjects)
    )

# --------------------------------------------------
# ADD MARKS
# --------------------------------------------------

@app.route(
    "/performance/add",
    methods=["GET", "POST"]
)
@login_required
def add_mark():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    # Student needs at least one subject
    if not student_subjects:

        flash(
            "Add at least one subject before recording marks.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )


    today = datetime.now(
        timezone.utc
    ).date()


    selected_subject_id = request.args.get(
        "subject_id",
        type=int
    )


    if request.method == "POST":

        assessment_name = (
            request.form
            .get("assessment_name", "")
            .strip()
        )

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        marks_obtained_raw = request.form.get(
            "marks_obtained",
            ""
        )

        maximum_marks_raw = request.form.get(
            "maximum_marks",
            ""
        )

        assessment_date_raw = request.form.get(
            "assessment_date",
            ""
        )


        # ------------------------------------------
        # ASSESSMENT NAME
        # ------------------------------------------

        if not assessment_name:

            flash(
                "Please enter an assessment name.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if len(assessment_name) > 120:

            flash(
                "Assessment name must be 120 characters or fewer.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # SUBJECT
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # MARKS
        # ------------------------------------------

        try:

            marks_obtained = float(
                marks_obtained_raw
            )

            maximum_marks = float(
                maximum_marks_raw
            )

        except ValueError:

            flash(
                "Please enter valid marks.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if marks_obtained < 0:

            flash(
                "Marks obtained cannot be negative.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if maximum_marks <= 0:

            flash(
                "Maximum marks must be greater than zero.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if marks_obtained > maximum_marks:

            flash(
                "Marks obtained cannot be greater than maximum marks.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # ASSESSMENT DATE
        # ------------------------------------------

        try:

            assessment_date = datetime.strptime(
                assessment_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid assessment date.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if assessment_date > today:

            flash(
                "Assessment results cannot be recorded for a future date.",
                "error"
            )

            return render_template(
                "add_mark.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # CREATE MARK RECORD
        # ------------------------------------------

        new_mark = MarkRecord(
            assessment_name=assessment_name,
            marks_obtained=marks_obtained,
            maximum_marks=maximum_marks,
            assessment_date=assessment_date,
            user_id=current_user.id,
            subject_id=subject.id
        )


        db.session.add(
            new_mark
        )

        db.session.commit()


        flash(
            f"{assessment_name} result added successfully.",
            "success"
        )


        return redirect(
            url_for("performance")
        )


    return render_template(
        "add_mark.html",
        subjects=student_subjects,
        today=today,
        selected_subject_id=selected_subject_id
    )

# --------------------------------------------------
# EDIT MARK RECORD
# --------------------------------------------------

@app.route(
    "/performance/<int:mark_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_mark(mark_id):

    mark = (
        MarkRecord.query
        .filter_by(
            id=mark_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    today = datetime.now(
        timezone.utc
    ).date()


    if request.method == "POST":

        assessment_name = (
            request.form
            .get("assessment_name", "")
            .strip()
        )

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        marks_obtained_raw = request.form.get(
            "marks_obtained",
            ""
        )

        maximum_marks_raw = request.form.get(
            "maximum_marks",
            ""
        )

        assessment_date_raw = request.form.get(
            "assessment_date",
            ""
        )


        # ------------------------------------------
        # ASSESSMENT NAME
        # ------------------------------------------

        if not assessment_name:

            flash(
                "Please enter an assessment name.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        if len(assessment_name) > 120:

            flash(
                "Assessment name must be 120 characters or fewer.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # SUBJECT
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # MARKS
        # ------------------------------------------

        try:

            marks_obtained = float(
                marks_obtained_raw
            )

            maximum_marks = float(
                maximum_marks_raw
            )

        except ValueError:

            flash(
                "Please enter valid marks.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        if marks_obtained < 0:

            flash(
                "Marks obtained cannot be negative.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        if maximum_marks <= 0:

            flash(
                "Maximum marks must be greater than zero.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        if marks_obtained > maximum_marks:

            flash(
                "Marks obtained cannot be greater than maximum marks.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # DATE
        # ------------------------------------------

        try:

            assessment_date = datetime.strptime(
                assessment_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid assessment date.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        if assessment_date > today:

            flash(
                "Assessment results cannot be recorded for a future date.",
                "error"
            )

            return render_template(
                "edit_mark.html",
                mark=mark,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # UPDATE RECORD
        # ------------------------------------------

        mark.assessment_name = (
            assessment_name
        )

        mark.subject_id = (
            subject.id
        )

        mark.marks_obtained = (
            marks_obtained
        )

        mark.maximum_marks = (
            maximum_marks
        )

        mark.assessment_date = (
            assessment_date
        )


        db.session.commit()


        flash(
            f"{mark.assessment_name} was updated successfully.",
            "success"
        )


        return redirect(
            url_for("performance")
        )


    return render_template(
        "edit_mark.html",
        mark=mark,
        subjects=student_subjects,
        today=today
    )

# --------------------------------------------------
# DELETE MARK RECORD
# --------------------------------------------------

@app.route(
    "/performance/<int:mark_id>/delete",
    methods=["POST"]
)
@login_required
def delete_mark(mark_id):

    mark = (
        MarkRecord.query
        .filter_by(
            id=mark_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    assessment_name = (
        mark.assessment_name
    )


    db.session.delete(
        mark
    )

    db.session.commit()


    flash(
        f"{assessment_name} was deleted successfully.",
        "success"
    )


    return redirect(
        url_for("performance")
    )

# --------------------------------------------------
# ADD STUDY SESSION
# --------------------------------------------------

@app.route(
    "/study-log/add",
    methods=["GET", "POST"]
)
@login_required
def add_study_session():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    # Student needs a subject first
    if not student_subjects:

        flash(
            "Add at least one subject before logging study time.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )


    today = datetime.now(
        timezone.utc
    ).date()


    selected_subject_id = request.args.get(
        "subject_id",
        type=int
    )


    if request.method == "POST":

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        study_date_raw = request.form.get(
            "study_date",
            ""
        )

        hours_raw = request.form.get(
            "hours",
            "0"
        )

        minutes_raw = request.form.get(
            "minutes",
            "0"
        )

        notes = (
            request.form
            .get("notes", "")
            .strip()
        )


        # ------------------------------------------
        # SUBJECT VALIDATION
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # DATE VALIDATION
        # ------------------------------------------

        try:

            study_date = datetime.strptime(
                study_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid study date.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if study_date > today:

            flash(
                "Study sessions cannot be logged for a future date.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # DURATION VALIDATION
        # ------------------------------------------

        try:

            hours = int(
                hours_raw
            )

            minutes = int(
                minutes_raw
            )

        except ValueError:

            flash(
                "Please enter a valid study duration.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if hours < 0:

            flash(
                "Study hours cannot be negative.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if not 0 <= minutes <= 59:

            flash(
                "Minutes must be between 0 and 59.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        duration_minutes = (
            hours * 60
            + minutes
        )


        if duration_minutes <= 0:

            flash(
                "Study duration must be greater than zero.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if duration_minutes > 1440:

            flash(
                "A study session cannot be longer than 24 hours.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # NOTES VALIDATION
        # ------------------------------------------

        if len(notes) > 300:

            flash(
                "Notes must be 300 characters or fewer.",
                "error"
            )

            return render_template(
                "add_study_session.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # CREATE SESSION
        # ------------------------------------------

        new_session = StudySession(
            study_date=study_date,
            duration_minutes=duration_minutes,
            notes=notes if notes else None,
            user_id=current_user.id,
            subject_id=subject.id
        )


        db.session.add(
            new_session
        )

        db.session.commit()


        flash(
            "Study session added successfully.",
            "success"
        )


        return redirect(
            url_for("study_log")
        )


    return render_template(
        "add_study_session.html",
        subjects=student_subjects,
        today=today,
        selected_subject_id=selected_subject_id
    )


# --------------------------------------------------
# EDIT STUDY SESSION
# --------------------------------------------------

@app.route(
    "/study-log/<int:session_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_study_session(session_id):

    session = (
        StudySession.query
        .filter_by(
            id=session_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    today = datetime.now(
        timezone.utc
    ).date()


    if request.method == "POST":

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        study_date_raw = request.form.get(
            "study_date",
            ""
        )

        hours_raw = request.form.get(
            "hours",
            "0"
        )

        minutes_raw = request.form.get(
            "minutes",
            "0"
        )

        notes = (
            request.form
            .get("notes", "")
            .strip()
        )


        # ------------------------------------------
        # SUBJECT
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # DATE
        # ------------------------------------------

        try:

            study_date = datetime.strptime(
                study_date_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid study date.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        if study_date > today:

            flash(
                "Study sessions cannot be logged for a future date.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # DURATION
        # ------------------------------------------

        try:

            hours = int(
                hours_raw
            )

            minutes = int(
                minutes_raw
            )

        except ValueError:

            flash(
                "Please enter a valid study duration.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        if hours < 0:

            flash(
                "Study hours cannot be negative.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        if not 0 <= minutes <= 59:

            flash(
                "Minutes must be between 0 and 59.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        duration_minutes = (
            hours * 60
            + minutes
        )


        if duration_minutes <= 0:

            flash(
                "Study duration must be greater than zero.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        if duration_minutes > 1440:

            flash(
                "A study session cannot be longer than 24 hours.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # NOTES
        # ------------------------------------------

        if len(notes) > 300:

            flash(
                "Notes must be 300 characters or fewer.",
                "error"
            )

            return render_template(
                "edit_study_session.html",
                session=session,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # UPDATE SESSION
        # ------------------------------------------

        session.subject_id = subject.id

        session.study_date = study_date

        session.duration_minutes = (
            duration_minutes
        )

        session.notes = (
            notes if notes else None
        )


        db.session.commit()


        flash(
            "Study session updated successfully.",
            "success"
        )


        return redirect(
            url_for("study_log")
        )


    return render_template(
        "edit_study_session.html",
        session=session,
        subjects=student_subjects,
        today=today
    )

# --------------------------------------------------
# DELETE STUDY SESSION
# --------------------------------------------------

@app.route(
    "/study-log/<int:session_id>/delete",
    methods=["POST"]
)
@login_required
def delete_study_session(session_id):

    session = (
        StudySession.query
        .filter_by(
            id=session_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    subject_name = (
        session.subject.name
    )


    db.session.delete(
        session
    )

    db.session.commit()


    flash(
        f"Study session for {subject_name} was deleted successfully.",
        "success"
    )


    return redirect(
        url_for("study_log")
    )
    

# --------------------------------------------------
# ADD STUDY TASK
# --------------------------------------------------

@app.route(
    "/planner/add",
    methods=["GET", "POST"]
)
@login_required
def add_task():

    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    # Student must have at least one subject
    if not student_subjects:

        flash(
            "Add at least one subject before creating a study task.",
            "error"
        )

        return redirect(
            url_for("add_subject")
        )


    today = datetime.now(
        timezone.utc
    ).date()


    selected_subject_id = request.args.get(
        "subject_id",
        type=int
    )


    if request.method == "POST":

        task_name = (
            request.form
            .get("task_name", "")
            .strip()
        )

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        deadline_raw = request.form.get(
            "deadline",
            ""
        )

        priority = request.form.get(
            "priority",
            "Medium"
        )


        # ------------------------------------------
        # TASK NAME VALIDATION
        # ------------------------------------------

        if not task_name:

            flash(
                "Please enter a task name.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if len(task_name) > 150:

            flash(
                "Task name must be 150 characters or fewer.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # SUBJECT VALIDATION
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # DEADLINE VALIDATION
        # ------------------------------------------

        try:

            deadline = datetime.strptime(
                deadline_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid deadline.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        if deadline < today:

            flash(
                "The deadline cannot be in the past.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # PRIORITY VALIDATION
        # ------------------------------------------

        allowed_priorities = {
            "High",
            "Medium",
            "Low"
        }


        if priority not in allowed_priorities:

            flash(
                "Please choose a valid priority.",
                "error"
            )

            return render_template(
                "add_task.html",
                subjects=student_subjects,
                today=today,
                selected_subject_id=selected_subject_id
            )


        # ------------------------------------------
        # CREATE TASK
        # ------------------------------------------

        new_task = StudyTask(
            task_name=task_name,
            deadline=deadline,
            priority=priority,
            status="Pending",
            user_id=current_user.id,
            subject_id=subject.id
        )


        db.session.add(
            new_task
        )

        db.session.commit()


        flash(
            f"{task_name} was added to your study planner.",
            "success"
        )


        return redirect(
            url_for("planner")
        )


    return render_template(
        "add_task.html",
        subjects=student_subjects,
        today=today,
        selected_subject_id=selected_subject_id
    )

# --------------------------------------------------
# COMPLETE STUDY TASK
# --------------------------------------------------

@app.route(
    "/planner/tasks/<int:task_id>/complete",
    methods=["POST"]
)
@login_required
def complete_task(task_id):

    task = (
        StudyTask.query
        .filter_by(
            id=task_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    task.status = "Completed"

    db.session.commit()

    flash(
        f"{task.task_name} marked as completed.",
        "success"
    )

    return redirect(
        url_for("planner")
    )

# --------------------------------------------------
# EDIT STUDY TASK
# --------------------------------------------------

@app.route(
    "/planner/tasks/<int:task_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_task(task_id):

    task = (
        StudyTask.query
        .filter_by(
            id=task_id,
            user_id=current_user.id
        )
        .first_or_404()
    )


    student_subjects = (
        Subject.query
        .filter_by(
            user_id=current_user.id
        )
        .order_by(
            Subject.name.asc()
        )
        .all()
    )


    today = datetime.now(
        timezone.utc
    ).date()


    if request.method == "POST":

        task_name = (
            request.form
            .get("task_name", "")
            .strip()
        )

        subject_id_raw = request.form.get(
            "subject_id",
            ""
        )

        deadline_raw = request.form.get(
            "deadline",
            ""
        )

        priority = request.form.get(
            "priority",
            "Medium"
        )


        # ------------------------------------------
        # TASK NAME
        # ------------------------------------------

        if not task_name:

            flash(
                "Please enter a task name.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        if len(task_name) > 150:

            flash(
                "Task name must be 150 characters or fewer.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # SUBJECT
        # ------------------------------------------

        try:

            subject_id = int(
                subject_id_raw
            )

        except (
            ValueError,
            TypeError
        ):

            flash(
                "Please choose a valid subject.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        subject = (
            Subject.query
            .filter_by(
                id=subject_id,
                user_id=current_user.id
            )
            .first()
        )


        if not subject:

            flash(
                "The selected subject is not available.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # DEADLINE
        # ------------------------------------------

        try:

            deadline = datetime.strptime(
                deadline_raw,
                "%Y-%m-%d"
            ).date()

        except ValueError:

            flash(
                "Please choose a valid deadline.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        if deadline < today:

            flash(
                "Please choose today or a future date.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # PRIORITY
        # ------------------------------------------

        allowed_priorities = {
            "High",
            "Medium",
            "Low"
        }


        if priority not in allowed_priorities:

            flash(
                "Please choose a valid priority.",
                "error"
            )

            return render_template(
                "edit_task.html",
                task=task,
                subjects=student_subjects,
                today=today
            )


        # ------------------------------------------
        # UPDATE TASK
        # ------------------------------------------

        task.task_name = task_name
        task.subject_id = subject.id
        task.deadline = deadline
        task.priority = priority

        db.session.commit()


        flash(
            f"{task.task_name} was updated successfully.",
            "success"
        )


        return redirect(
            url_for("planner")
        )


    return render_template(
        "edit_task.html",
        task=task,
        subjects=student_subjects,
        today=today
    )

# --------------------------------------------------
# DELETE STUDY TASK
# --------------------------------------------------

@app.route(
    "/planner/tasks/<int:task_id>/delete",
    methods=["POST"]
)
@login_required
def delete_task(task_id):

    task = (
        StudyTask.query
        .filter_by(
            id=task_id,
            user_id=current_user.id
        )
        .first_or_404()
    )

    task_name = task.task_name

    db.session.delete(task)

    db.session.commit()

    flash(
        f"{task_name} was deleted successfully.",
        "success"
    )

    return redirect(
        url_for("planner")
    )



# --------------------------------------------------
# LOGOUT
# --------------------------------------------------

@app.route("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "You have been logged out successfully.",
        "success"
    )

    return redirect(
        url_for("login")
    )


# --------------------------------------------------
# START APPLICATION
# --------------------------------------------------

if __name__ == "__main__":

    with app.app_context():

        db.create_all()

    app.run(
        debug=True
    )