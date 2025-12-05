import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QInputDialog
from PyQt5.uic import loadUi
from Data_Base import get_connection

class AdminDashboard(QWidget):
    def __init__(self):
        super(AdminDashboard, self).__init__()
        loadUi("ui/Admindashboard.ui", self)
        
        # 1. تعديل الجدول ليشمل 5 أعمدة بدلاً من 4
        self.course_table.setColumnCount(5) # زدنا عمود
        self.course_table.setHorizontalHeaderLabels(
            ["Course Code", "Course Name", "Credit Hours", "Capacity", "Time"] # أضفنا عنوان Time
        )
        
        # تنسيق عرض الأعمدة
        self.course_table.setColumnWidth(0, 80)  # Code
        self.course_table.setColumnWidth(1, 200) # Name
        self.course_table.setColumnWidth(2, 80)  # Credits
        self.course_table.setColumnWidth(3, 80)  # Capacity
        self.course_table.setColumnWidth(4, 150) # Time (العمود الجديد)
        
        # ربط الأزرار
        self.btn_add.clicked.connect(self.add_course)
        self.btn_refresh.clicked.connect(self.load_courses)
        self.btn_delete.clicked.connect(self.delete_course)
        self.btn_edit.clicked.connect(self.edit_course)
        
        self.load_courses()

    def load_courses(self):
        """سحب المواد مع أوقاتها وعرضها"""
        self.course_table.setRowCount(0)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            
            # 2. تعديل الاستعلام: نستخدم LEFT JOIN لنجلب الوقت من جدول offerings
            # نقوم بدمج اليوم والبداية والنهاية في نص واحد للعرض
            query = """
                SELECT c.course_code, c.name, c.credits, c.max_capacity, 
                       (o.day_of_week || ' ' || o.start_time || '-' || o.end_time) as time
                FROM courses c
                LEFT JOIN offerings o ON c.course_code = o.course_code
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            
            self.course_table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                # row_data = (Code, Name, Credits, Capacity, TimeString)
                self.course_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data[0])))
                self.course_table.setItem(row_idx, 1, QTableWidgetItem(str(row_data[1])))
                self.course_table.setItem(row_idx, 2, QTableWidgetItem(str(row_data[2])))
                self.course_table.setItem(row_idx, 3, QTableWidgetItem(str(row_data[3])))
                
                # 3. عرض الوقت في العمود الخامس
                time_str = row_data[4] if row_data[4] else "No Offer"
                self.course_table.setItem(row_idx, 4, QTableWidgetItem(time_str))
                
            conn.close()

    def add_course(self):
        # ... (نفس كود الإضافة السابق تماماً، لا تغيير فيه) ...
        # (تأكد أنك تستخدم النسخة الأخيرة التي تطلب اليوم والوقت)
        
        # طلب البيانات
        code, ok1 = QInputDialog.getText(self, "إضافة مادة", "كود المادة (مثال: COE310):")
        if not ok1 or not code: return

        name, ok2 = QInputDialog.getText(self, "إضافة مادة", "اسم المادة:")
        if not ok2 or not name: return

        credits, ok3 = QInputDialog.getInt(self, "إضافة مادة", "عدد الساعات:", 3, 1, 6)
        if not ok3: return

        capacity, ok4 = QInputDialog.getInt(self, "إضافة مادة", "سعة القاعة:", 30, 1, 100)
        if not ok4: return

        # طلب الموعد
        days = ["U", "M", "T", "W", "R"]
        day, ok_day = QInputDialog.getItem(self, "الموعد", "اختر اليوم:", days, 0, False)
        if not ok_day: return

        start_time, ok_start = QInputDialog.getText(self, "الموعد", "وقت البداية (مثال 08:00):")
        if not ok_start or not start_time: return

        end_time, ok_end = QInputDialog.getText(self, "الموعد", "وقت النهاية (مثال 09:00):")
        if not ok_end or not end_time: return

        # طلب الخطة
        program, ok5 = QInputDialog.getItem(self, "الخطة", "التخصص:", ["Computer", "Communications", "Power", "Biomedical"], 0, False)
        if not ok5: return

        level, ok6 = QInputDialog.getInt(self, "الخطة", "المستوى:", 4, 1, 10)
        if not ok6: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO courses (course_code, name, credits, lecture_hours, lab_hours, max_capacity) VALUES (?, ?, ?, 3, 0, ?)", (code, name, credits, capacity))
            cursor.execute("INSERT INTO offerings (course_code, term, day_of_week, start_time, end_time, max_capacity) VALUES (?, '202510', ?, ?, ?, ?)", (code, day, start_time, end_time, capacity))
            cursor.execute("INSERT INTO program_plans (program, level, course_code) VALUES (?, ?, ?)", (program, level, code))

            conn.commit()
            conn.close()
            QMessageBox.information(self, "تم", "تمت الإضافة بنجاح")
            self.load_courses()
        except Exception as e:
            QMessageBox.warning(self, "خطأ", str(e))

    def delete_course(self):
        # ... (نفس كود الحذف السابق) ...
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
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))
                
    def edit_course(self):
        # ... (نفس كود التعديل السابق، ولكن تأكد أنه لا يعدل الكود الأساسي) ...
        row = self.course_table.currentRow()
        if row == -1:
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
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))


