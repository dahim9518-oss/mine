        # 1. في دالة __init__، أضف ربط الزر الجديد
        self.finishButton.clicked.connect(self.finish_registration)

    # 2. أضف دالة إنهاء التسجيل
    def finish_registration(self):
        # أ. نجيب المواد اللي الطالب سجلها
        registered_courses = self.logic.get_registered_courses_objects(self.student_id)
        
        if not registered_courses:
            QtWidgets.QMessageBox.warning(self, "تنبيه", "لم تسجل أي مواد بعد!")
            return

        # ب. نفحص الساعات (مع تفعيل شرط الحد الأدنى check_min=True)
        result = self.logic.check_credit_hours(registered_courses, check_min=True)
        
        if result is True:
            QtWidgets.QMessageBox.information(self, "تم", "تم إنهاء التسجيل بنجاح! جدولك مطابق للشروط.")
            # هنا ممكن تقفل الشاشة أو تمنع التعديل
        else:
            QtWidgets.QMessageBox.warning(self, "خطأ في الساعات", str(result))
