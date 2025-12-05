import sys
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox, QTableWidgetItem

from Data_Base import get_connection
from registration_system import RegistrationSystem

class StudentDashboard(QDialog):
    def __init__(self, student_id):
        super(StudentDashboard, self).__init__()
        loadUi("ui/student_dashboard.ui", self)

        self.student_id = student_id
        self.logic = RegistrationSystem()

        # تنسيق الجدول
        self.courseTable.setColumnWidth(0, 150)  
        self.courseTable.setColumnWidth(1, 250)  
        self.courseTable.setColumnWidth(2, 80)   
        self.courseTable.setColumnWidth(3, 100)  

        self.loaddata()

        # ---------------------------------------------------------
        # 🔴 تصحيح: ربط جميع الأزرار يجب أن يكون هنا في __init__
        # ---------------------------------------------------------
        self.addCourseButton.clicked.connect(self.add_course)
        self.removeCourseButton.clicked.connect(self.remove_course)
        # ربط الزر الجديد (إنهاء التسجيل)
        self.finishButton.clicked.connect(self.finish_registration)


    # ---------------------------------------------------------
    # دالة إنهاء التسجيل (للتحقق من الحد الأدنى)
    # ---------------------------------------------------------
    def finish_registration(self):
        # أ. نجيب المواد اللي الطالب سجلها فعلياً
        registered_courses = self.logic.get_registered_courses_objects(self.student_id)
        
        if not registered_courses:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لم تسجل أي مواد بعد!")
            return

        # ب. نفحص الساعات (مع تفعيل شرط الحد الأدنى check_min=True)
        result = self.logic.check_credit_hours(registered_courses, check_min=True)
        
        if result is True:
            QtWidgets.QMessageBox.information(self, "تم", "تم إنهاء التسجيل بنجاح! جدولك مطابق للشروط.")
            # (اختياري: يمكن إغلاق الشاشة هنا إذا أردت)
            # self.close()
        else:
            QtWidgets.QMessageBox.warning(self, "خطأ في الساعات", str(result))


    def loaddata(self):
        self.courseTable.setRowCount(0)
        
        conn = get_connection()
        rows = []   
        if conn:
            cursor = conn.cursor()
            
            sql_code = """
                SELECT DISTINCT c.course_code, c.name, c.credits, c.max_capacity 
                FROM courses c
                JOIN offerings o ON c.course_code = o.course_code
            """
            cursor.execute(sql_code)
            rows = cursor.fetchall() 
            conn.close()

        self.courseTable.setRowCount(len(rows))
        row = 0

        for c in rows:
            self.courseTable.setItem(row, 0, QtWidgets.QTableWidgetItem(str(c[0])))
            self.courseTable.setItem(row, 1, QtWidgets.QTableWidgetItem(str(c[1])))
            self.courseTable.setItem(row, 2, QtWidgets.QTableWidgetItem(str(c[2])))
            self.courseTable.setItem(row, 3, QtWidgets.QTableWidgetItem(str(c[3])))
            row += 1

    def add_course(self):
        current_row = self.courseTable.currentRow()
        if current_row == -1:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مادة أولاً")
            return

        course_code = self.courseTable.item(current_row, 0).text()
        
        # التحقق
        validation_result = self.logic.validate_schedule(self.student_id, [course_code])

        if validation_result is True:
            # التسجيل
            final_reg = self.logic.register_sudent(self.student_id, [course_code])
            
            if final_reg is True:
                QtWidgets.QMessageBox.information(self, "نجاح", f"تم تسجيل {course_code} بنجاح!")
            else:
                QtWidgets.QMessageBox.critical(self, "خطأ", str(final_reg))
        else:
            QtWidgets.QMessageBox.warning(self, "فشل التسجيل", str(validation_result))

    def remove_course(self):
        QtWidgets.QMessageBox.information(self, "Remove Course", "Remove Course button clicked!")

