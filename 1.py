    def login(self):
        # ... (كود سحب البيانات والتحقق من user كما هو) ...

        if user:
            # -- حالة النجاح --
            self.statusLabel.setText("Login Successful!")
            
            if user.role == "student":
                # (1) فتح شاشة الطالب (المنطق سليم هنا)
                self.dashboard = StudentDashboard(user.student_id) 
                self.widget.addWidget(self.dashboard)
                self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
                
            elif user.role == "admin":
                # 🔴 التعديل: فتح شاشة الأدمن ونقل التحكم للستاك
                self.admin_screen = AdminDashboard()
                self.widget.addWidget(self.admin_screen)
                self.widget.setCurrentIndex(self.widget.currentIndex() + 1)
                # (اختياري) نغير حجم النافذة الرئيسية ليناسب الداشبورد
                self.widget.window().resize(900, 600)
            
            # ملاحظة: سنحذف self.close() لأننا نستخدم QStackedWidget
            
        else:
            self.statusLabel.setText("Invalid email or password")


