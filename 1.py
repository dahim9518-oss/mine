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

