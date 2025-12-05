from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTableWidget, QTableWidgetItem, QHBoxLayout, 
    QMessageBox, QInputDialog
)
from PyQt5.uic import loadUi
from Data_Base import get_connection

class AdminDashboard(QWidget):
    def __init__(self):
        super().__init__()
        # تحميل الواجهة
        loadUi("ui/Admindashboard.ui", self)

        # تنسيق الجدول
        self.course_table.setColumnWidth(0, 100)
        self.course_table.setColumnWidth(1, 250)

        # ربط الأزرار (بالأسماء الصحيحة الجديدة)
        self.btn_add.clicked.connect(self.add_course)
        self.btn_edit.clicked.connect(self.edit_course)
        self.btn_delete.clicked.connect(self.delete_course)
        self.btn_refresh.clicked.connect(self.load_courses)

        # تحميل البيانات عند البدء
        self.load_courses()

    # ---------------------------------------------------------
    # 1. دالة عرض المواد (تم تعديل الاسم من load_courses_dummy)
    # ---------------------------------------------------------
    def load_courses(self):
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

    # ---------------------------------------------------------
    # 2. دالة إضافة مادة (مربوطة مع 3 جداول)
    # ---------------------------------------------------------
    def add_course(self):
        # طلب البيانات
        code, ok1 = QInputDialog.getText(self, "إضافة مادة", "كود المادة (مثال: COE310):")
        if not ok1 or not code: return

        name, ok2 = QInputDialog.getText(self, "إضافة مادة", "اسم المادة:")
        if not ok2 or not name: return

        credits, ok3 = QInputDialog.getInt(self, "إضافة مادة", "عدد الساعات:", 3, 1, 6)
        if not ok3: return

        capacity, ok4 = QInputDialog.getInt(self, "إضافة مادة", "سعة القاعة:", 30, 1, 100)
        if not ok4: return

        # القائمة المنسدلة للبرنامج والمستوى
        program, ok5 = QInputDialog.getItem(self, "الخطة", "التخصص:", 
                                          ["Computer", "Communications", "Power", "Biomedical"], 0, False)
        if not ok5: return

        level, ok6 = QInputDialog.getInt(self, "الخطة", "المستوى (1-10):", 4, 1, 10)
        if not ok6: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # أ. جدول المواد
            cursor.execute("""
                INSERT INTO courses (course_code, name, credits, lecture_hours, lab_hours, max_capacity)
                VALUES (?, ?, ?, 3, 0, ?)
            """, (code, name, credits, capacity))
            
            # ب. جدول الشعب (للتسجيل)
            cursor.execute("""
                INSERT INTO offerings (course_code, term, day_of_week, start_time, end_time, max_capacity)
                VALUES (?, '202510', 'U', '09:00', '10:00', ?)
            """, (code, capacity))

            # ج. جدول الخطة (للتحقق)
            cursor.execute("""
                INSERT INTO program_plans (program, level, course_code)
                VALUES (?, ?, ?)
            """, (program, level, code))

            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "تم", f"تمت إضافة {code} بنجاح!")
            self.load_courses() # استدعاء الدالة بالاسم الصحيح
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل الحفظ: {e}")

    # ---------------------------------------------------------
    # 3. دالة تعديل مادة (تم تعديل الاسم من edit_course_dummy)
    # ---------------------------------------------------------
    def edit_course(self):
        row = self.course_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "تنبيه", "اختر مادة للتعديل")
            return

        code = self.course_table.item(row, 0).text()
        old_name = self.course_table.item(row, 1).text()
        
        new_name, ok = QInputDialog.getText(self, "تعديل", f"الاسم الجديد لـ {code}:", text=old_name)
        
        if ok and new_name:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE courses SET name = ? WHERE course_code = ?", (new_name, code))
                conn.commit()
                conn.close()
                self.load_courses()
                QMessageBox.information(self, "تم", "تم التحديث")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))

    # ---------------------------------------------------------
    # 4. دالة حذف مادة (تم تعديل الاسم من delete_course_dummy)
    # ---------------------------------------------------------
    def delete_course(self):
        row = self.course_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "تنبيه", "اختر مادة للحذف")
            return
            
        code = self.course_table.item(row, 0).text()
        
        confirm = QMessageBox.question(self, "تأكيد", f"حذف {code}؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM program_plans WHERE course_code = ?", (code,))
                cursor.execute("DELETE FROM offerings WHERE course_code = ?", (code,))
                cursor.execute("DELETE FROM courses WHERE course_code = ?", (code,))
                conn.commit()
                conn.close()
                self.load_courses()
                QMessageBox.information(self, "تم", "تم الحذف")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))
