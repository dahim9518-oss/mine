from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTableWidget, QTableWidgetItem,QMessageBox,QInputDialog
)
import sys
from Data_Base import get_connection



class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QVBoxLayout()
        header = QLabel("Admin Dashboard - Course Management")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        main_layout.addWidget(header)

        self.course_table = QTableWidget(0, 4)
        self.course_table.setHorizontalHeaderLabels(
            ["Course Code", "Course Name", "Credit Hours", "Capacity"]
        )
        main_layout.addWidget(self.course_table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("Add Course")
        self.btn_edit = QPushButton("Edit Selected")
        self.btn_delete = QPushButton("Delete Selected")
        self.btn_refresh = QPushButton("Refresh")

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_refresh)

        main_layout.addLayout(btn_layout)
        self.setLayout(main_layout)

        self.btn_add.clicked.connect(self.add_course)
        self.btn_edit.clicked.connect(self.edit_course_dummy)
        self.btn_delete.clicked.connect(self.delete_course_dummy)
        self.btn_refresh.clicked.connect(self.load_courses_dummy)

        self.load_courses_dummy()

    def load_courses_dummy(self):
        self.course_table.setRowCount(0) 
        
        conn = get_connection() 
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT course_code, name, credits, max_capacity FROM courses")
            rows = cursor.fetchall()
            
            self.course_table.setRowCount(len(rows))
            for i, row_data in enumerate(rows):
                self.course_table.setItem(i, 0, QTableWidgetItem(str(row_data[0])))
                self.course_table.setItem(i, 1, QTableWidgetItem(str(row_data[1])))
                self.course_table.setItem(i, 2, QTableWidgetItem(str(row_data[2])))
                self.course_table.setItem(i, 3, QTableWidgetItem(str(row_data[3])))
            conn.close()

    def add_course(self):
        """إضافة مادة جديدة + ربطها بالخطة الدراسية"""
        
        # 1. طلب البيانات الأساسية للمادة
        code, ok1 = QInputDialog.getText(self, "إضافة مادة", "كود المادة (مثال: COE310):")
        if not ok1 or not code: return

        name, ok2 = QInputDialog.getText(self, "إضافة مادة", "اسم المادة:")
        if not ok2 or not name: return

        credits, ok3 = QInputDialog.getInt(self, "إضافة مادة", "عدد الساعات:", 3, 1, 6)
        if not ok3: return

        capacity, ok4 = QInputDialog.getInt(self, "إضافة مادة", "سعة القاعة:", 30, 1, 100)
        if not ok4: return

        # 2. 🟢 الإضافة الجديدة: طلب بيانات الخطة الدراسية
        # نطلب البرنامج (Computer, Power, etc.)
        program, ok5 = QInputDialog.getItem(self, "الخطة الدراسية", "تابع لأي تخصص؟", 
                                          ["Computer", "Communications", "Power", "Biomedical"], 0, False)
        if not ok5: return

        # نطلب المستوى (1-10)
        level, ok6 = QInputDialog.getInt(self, "الخطة الدراسية", "لأي مستوى (1-10)؟", 4, 1, 10)
        if not ok6: return

        # 3. الحفظ في قاعدة البيانات (3 جداول)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # أ. جدول المواد (courses)
            cursor.execute("""
                INSERT INTO courses (course_code, name, credits, lecture_hours, lab_hours, max_capacity)
                VALUES (?, ?, ?, 3, 0, ?)
            """, (code, name, credits, capacity))
            
            # ب. جدول الشعب (offerings) - عشان تطلع للطالب
            cursor.execute("""
                INSERT INTO offerings (course_code, term, day_of_week, start_time, end_time, max_capacity)
                VALUES (?, '202510', 'U', '09:00', '10:00', ?)
            """, (code, capacity))

            # ج. 🟢 جدول الخطة (program_plans) - عشان ينجح فحص check_plan
            cursor.execute("""
                INSERT INTO program_plans (program, level, course_code)
                VALUES (?, ?, ?)
            """, (program, level, code))

            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "تم", f"تم إضافة المادة {code} إلى خطة {program} - مستوى {level} بنجاح!")
            self.load_courses() 
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل الحفظ: {e}")

    def edit_course_dummy(self):
        print("Edit Course")

    def delete_course_dummy(self):
        row = self.course_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "Error", "Select a course first")
            return
            
        code = self.course_table.item(row, 0).text()
        
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM offerings WHERE course_code = ?", (code,))
            cursor.execute("DELETE FROM courses WHERE course_code = ?", (code,))
            conn.commit()
            conn.close()
            self.load_courses_dummy() 
            QMessageBox.information(self, "Deleted", f"Course {code} deleted")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


