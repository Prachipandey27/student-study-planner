const menuButton = document.getElementById("menuButton");
const navLinks = document.getElementById("navLinks");


if (menuButton && navLinks) {

    menuButton.addEventListener("click", function () {

        navLinks.classList.toggle("active");

    });

}

const passwordButtons =
    document.querySelectorAll(".password-toggle");


passwordButtons.forEach(function (button) {

    button.addEventListener("click", function () {

        const targetId =
            button.dataset.passwordTarget;

        const passwordInput =
            document.getElementById(targetId);

        if (!passwordInput) {
            return;
        }

        if (passwordInput.type === "password") {

            passwordInput.type = "text";

            button.textContent = "Hide";

        } else {

            passwordInput.type = "password";

            button.textContent = "Show";

        }

    });

});


const sidebarOpen =
    document.getElementById("sidebarOpen");

const sidebarClose =
    document.getElementById("sidebarClose");

const appSidebar =
    document.getElementById("appSidebar");

const sidebarOverlay =
    document.getElementById("sidebarOverlay");


function openSidebar() {

    if (!appSidebar || !sidebarOverlay) {
        return;
    }

    appSidebar.classList.add("active");

    sidebarOverlay.classList.add("active");

}


function closeSidebar() {

    if (!appSidebar || !sidebarOverlay) {
        return;
    }

    appSidebar.classList.remove("active");

    sidebarOverlay.classList.remove("active");

}


if (sidebarOpen) {

    sidebarOpen.addEventListener(
        "click",
        openSidebar
    );

}


if (sidebarClose) {

    sidebarClose.addEventListener(
        "click",
        closeSidebar
    );

}


if (sidebarOverlay) {

    sidebarOverlay.addEventListener(
        "click",
        closeSidebar
    );

}


const dashboardDate =
    document.getElementById("dashboardDate");


if (dashboardDate) {

    const today =
        new Date();

    const dateOptions = {
        day: "numeric",
        month: "short",
        year: "numeric"
    };

    dashboardDate.textContent =
        today.toLocaleDateString(
            "en-IN",
            dateOptions
        );

}

const deleteButtons =
    document.querySelectorAll(
        ".subject-delete-button"
    );

const deleteModalOverlay =
    document.getElementById(
        "deleteModalOverlay"
    );

const deleteCancelButton =
    document.getElementById(
        "deleteCancelButton"
    );

const deleteSubjectForm =
    document.getElementById(
        "deleteSubjectForm"
    );

const deleteSubjectName =
    document.getElementById(
        "deleteSubjectName"
    );


deleteButtons.forEach(function (button) {

    button.addEventListener(
        "click",
        function () {

            if (
                !deleteModalOverlay
                || !deleteSubjectForm
                || !deleteSubjectName
            ) {
                return;
            }

            const deleteUrl =
                button.dataset.deleteUrl;

            const subjectName =
                button.dataset.subjectName;


            deleteSubjectForm.action =
                deleteUrl;

            deleteSubjectName.textContent =
                subjectName;

            deleteModalOverlay.classList.add(
                "active"
            );

        }
    );

});


function closeDeleteModal() {

    if (!deleteModalOverlay) {
        return;
    }

    deleteModalOverlay.classList.remove(
        "active"
    );

}


if (deleteCancelButton) {

    deleteCancelButton.addEventListener(
        "click",
        closeDeleteModal
    );

}


if (deleteModalOverlay) {

    deleteModalOverlay.addEventListener(
        "click",
        function (event) {

            if (
                event.target
                === deleteModalOverlay
            ) {

                closeDeleteModal();

            }

        }
    );

}

// ========================================
// DELETE STUDY TASK
// ========================================

const taskDeleteButtons =
    document.querySelectorAll(
        ".task-delete-button"
    );


const taskDeleteModalOverlay =
    document.getElementById(
        "taskDeleteModalOverlay"
    );


const taskDeleteCancelButton =
    document.getElementById(
        "taskDeleteCancelButton"
    );


const deleteTaskForm =
    document.getElementById(
        "deleteTaskForm"
    );


const deleteTaskName =
    document.getElementById(
        "deleteTaskName"
    );


taskDeleteButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                if (
                    !taskDeleteModalOverlay
                    || !deleteTaskForm
                    || !deleteTaskName
                ) {
                    return;
                }


                const deleteUrl =
                    button.dataset.deleteUrl;


                const taskName =
                    button.dataset.taskName;


                deleteTaskForm.action =
                    deleteUrl;


                deleteTaskName.textContent =
                    taskName;


                taskDeleteModalOverlay
                    .classList
                    .add("active");

            }
        );

    }
);


function closeTaskDeleteModal() {

    if (!taskDeleteModalOverlay) {
        return;
    }


    taskDeleteModalOverlay
        .classList
        .remove("active");

}


if (taskDeleteCancelButton) {

    taskDeleteCancelButton
        .addEventListener(
            "click",
            closeTaskDeleteModal
        );

}


if (taskDeleteModalOverlay) {

    taskDeleteModalOverlay
        .addEventListener(
            "click",
            function (event) {

                if (
                    event.target
                    === taskDeleteModalOverlay
                ) {

                    closeTaskDeleteModal();

                }

            }
        );

}

// ========================================
// DELETE STUDY SESSION
// ========================================

const studySessionDeleteButtons =
    document.querySelectorAll(
        ".study-session-delete-button, " +
        ".subject-session-delete-button"
    );


const studySessionDeleteOverlay =
    document.getElementById(
        "studySessionDeleteOverlay"
    );


const studySessionDeleteCancel =
    document.getElementById(
        "studySessionDeleteCancel"
    );


const studySessionDeleteForm =
    document.getElementById(
        "studySessionDeleteForm"
    );


const studySessionDeleteSubject =
    document.getElementById(
        "studySessionDeleteSubject"
    );


const studySessionDeleteDate =
    document.getElementById(
        "studySessionDeleteDate"
    );


studySessionDeleteButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                if (
                    !studySessionDeleteOverlay
                    || !studySessionDeleteForm
                    || !studySessionDeleteSubject
                    || !studySessionDeleteDate
                ) {
                    return;
                }


                const deleteUrl =
                    button.dataset.deleteUrl;

                const subjectName =
                    button.dataset.sessionSubject;

                const sessionDate =
                    button.dataset.sessionDate;


                studySessionDeleteForm.action =
                    deleteUrl;


                studySessionDeleteSubject.textContent =
                    subjectName;


                studySessionDeleteDate.textContent =
                    sessionDate;


                studySessionDeleteOverlay
                    .classList
                    .add("active");

            }
        );

    }
);


function closeStudySessionDeleteModal() {

    if (!studySessionDeleteOverlay) {
        return;
    }


    studySessionDeleteOverlay
        .classList
        .remove("active");

}


if (studySessionDeleteCancel) {

    studySessionDeleteCancel
        .addEventListener(
            "click",
            closeStudySessionDeleteModal
        );

}


if (studySessionDeleteOverlay) {

    studySessionDeleteOverlay
        .addEventListener(
            "click",
            function (event) {

                if (
                    event.target
                    === studySessionDeleteOverlay
                ) {

                    closeStudySessionDeleteModal();

                }

            }
        );

}

// ========================================
// DELETE ASSESSMENT RESULT
// ========================================

const markDeleteButtons =
    document.querySelectorAll(
        ".performance-mark-delete, " +
        ".subject-mark-delete"
    );


const markDeleteOverlay =
    document.getElementById(
        "markDeleteOverlay"
    );


const markDeleteCancel =
    document.getElementById(
        "markDeleteCancel"
    );


const markDeleteForm =
    document.getElementById(
        "markDeleteForm"
    );


const markDeleteAssessment =
    document.getElementById(
        "markDeleteAssessment"
    );


const markDeleteSubject =
    document.getElementById(
        "markDeleteSubject"
    );


markDeleteButtons.forEach(
    function (button) {

        button.addEventListener(
            "click",
            function () {

                if (
                    !markDeleteOverlay
                    || !markDeleteForm
                    || !markDeleteAssessment
                    || !markDeleteSubject
                ) {
                    return;
                }


                const deleteUrl =
                    button.dataset.deleteUrl;


                const assessmentName =
                    button.dataset.assessmentName;


                const subjectName =
                    button.dataset.subjectName;


                markDeleteForm.action =
                    deleteUrl;


                markDeleteAssessment.textContent =
                    assessmentName;


                markDeleteSubject.textContent =
                    subjectName;


                markDeleteOverlay
                    .classList
                    .add("active");

            }
        );

    }
);


function closeMarkDeleteModal() {

    if (!markDeleteOverlay) {
        return;
    }


    markDeleteOverlay
        .classList
        .remove("active");

}


if (markDeleteCancel) {

    markDeleteCancel
        .addEventListener(
            "click",
            closeMarkDeleteModal
        );

}


if (markDeleteOverlay) {

    markDeleteOverlay
        .addEventListener(
            "click",
            function (event) {

                if (
                    event.target
                    === markDeleteOverlay
                ) {

                    closeMarkDeleteModal();

                }

            }
        );

}

// ========================================
// ATTENDANCE PERCENTAGE PREVIEW
// ========================================

const classesHeldInput =
    document.getElementById(
        "classes_held"
    );


const classesAttendedInput =
    document.getElementById(
        "classes_attended"
    );


const attendancePreview =
    document.getElementById(
        "attendancePreview"
    );


const attendancePreviewText =
    document.getElementById(
        "attendancePreviewText"
    );


function updateAttendancePreview() {

    if (
        !classesHeldInput
        || !classesAttendedInput
        || !attendancePreview
        || !attendancePreviewText
    ) {
        return;
    }


    const held = parseInt(
        classesHeldInput.value,
        10
    );


    const attended = parseInt(
        classesAttendedInput.value,
        10
    );


    if (
        Number.isNaN(held)
        || Number.isNaN(attended)
        || held <= 0
    ) {

        attendancePreview.textContent =
            "--%";


        attendancePreviewText.textContent =
            "Enter the class counts to preview " +
            "the attendance percentage.";


        return;
    }


    if (
        attended < 0
        || attended > held
    ) {

        attendancePreview.textContent =
            "Invalid";


        attendancePreviewText.textContent =
            "Classes attended cannot exceed " +
            "classes held.";


        return;
    }


    const percentage =
        (
            attended
            / held
        )
        * 100;


    attendancePreview.textContent =
        percentage.toFixed(1)
        + "%";


    attendancePreviewText.textContent =
        attended
        + " attended out of "
        + held
        + " classes.";

}


if (classesHeldInput) {

    classesHeldInput.addEventListener(
        "input",
        updateAttendancePreview
    );

}


if (classesAttendedInput) {

    classesAttendedInput.addEventListener(
        "input",
        updateAttendancePreview
    );

}


updateAttendancePreview();