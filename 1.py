import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QMessageBox, QTableWidgetItem, QInputDialog
from PyQt5.uic import loadUi
from Data_Base import get_connection

class AdminDashboard(QWidget):
    def __init__(self):
        super(AdminDashboard, self).__init__()
        # 1. تحميل ملف التصميم لتوحيد العمل مع باقي المشروع
        loadUi("ui/Admindashboard.ui", self)
        
        # تنسيق الجدول
        self.course_table.setColumnWidth(0, 100)
        self.course_table.setColumnWidth(1, 250)
        
        # 2. ربط الأزرار بالدوال (بأسمائها الصحيحة)
        self.btn_add.clicked.connect(self.add_course)
        self.btn_refresh.clicked.connect(self.load_courses)
        self.btn_delete.clicked.connect(self.delete_course)
        self.btn_edit.clicked.connect(self.edit_course)
        
        self.load_courses()

    def load_courses(self):
        """سحب المواد وعرضها في الجدول"""
        self.course_table.setRowCount(0)
        conn = get_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT course_code, name, credits, max_capacity FROM courses")
            rows = cursor.fetchall()
            
            self.course_table.setRowCount(len(rows))
            for row_idx, row_data in enumerate(rows):
                for col_idx, data in enumerate(row_data):
                    self.course_table.setItem(row_idx, col_idx, QTableWidgetItem(str(data)))
            conn.close()

    def add_course(self):
        """إضافة مادة جديدة + ربطها بالخطة والشعب"""
        
        # طلب البيانات
        code, ok1 = QInputDialog.getText(self, "إضافة مادة", "كود المادة (مثال: COE310):")
        if not ok1 or not code: return

        name, ok2 = QInputDialog.getText(self, "إضافة مادة", "اسم المادة:")
        if not ok2 or not name: return

        credits, ok3 = QInputDialog.getInt(self, "إضافة مادة", "عدد الساعات:", 3, 1, 6)
        if not ok3: return

        capacity, ok4 = QInputDialog.getInt(self, "إضافة مادة", "سعة القاعة:", 30, 1, 100)
        if not ok4: return

        # طلب بيانات الخطة (كما فعلت في كودك الممتاز)
        program, ok5 = QInputDialog.getItem(self, "الخطة الدراسية", "تابع لأي تخصص؟", 
                                          ["Computer", "Communications", "Power", "Biomedical"], 0, False)
        if not ok5: return

        level, ok6 = QInputDialog.getInt(self, "الخطة الدراسية", "لأي مستوى (1-10)؟", 4, 1, 10)
        if not ok6: return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 1. جدول المواد
            cursor.execute("""
                INSERT INTO courses (course_code, name, credits, lecture_hours, lab_hours, max_capacity)
                VALUES (?, ?, ?, 3, 0, ?)
            """, (code, name, credits, capacity))
            
            # 2. جدول الشعب
            cursor.execute("""
                INSERT INTO offerings (course_code, term, day_of_week, start_time, end_time, max_capacity)
                VALUES (?, '202510', 'U', '09:00', '10:00', ?)
            """, (code, capacity))

            # 3. جدول الخطة
            cursor.execute("""
                INSERT INTO program_plans (program, level, course_code)
                VALUES (?, ?, ?)
            """, (program, level, code))

            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "تم", f"تم إضافة {code} بنجاح!")
            self.load_courses() # (تم التصحيح: استدعاء الاسم الصحيح)
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل الحفظ: {e}")

    def delete_course(self):
        """حذف المادة"""
        row = self.course_table.currentRow()
        if row == -1:
            QMessageBox.warning(self, "تنبيه", "الرجاء اختيار مادة للحذف")
            return
            
        code = self.course_table.item(row, 0).text()
        
        confirm = QMessageBox.question(self, "تأكيد", f"حذف {code}؟", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                # الحذف من الجداول المرتبطة أولاً
                cursor.execute("DELETE FROM program_plans WHERE course_code = ?", (code,))
                cursor.execute("DELETE FROM offerings WHERE course_code = ?", (code,))
                cursor.execute("DELETE FROM courses WHERE course_code = ?", (code,))
                conn.commit()
                conn.close()
                self.load_courses()
                QMessageBox.information(self, "تم", "تم الحذف بنجاح")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", str(e))

    def edit_course(self):
        """تعديل المادة"""
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



