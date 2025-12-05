import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication, QMessageBox
from PyQt5.uic import loadUi
        
# 🔴 التعديلات الجديدة (الإضافات):
from Users import User                  # استيراد كلاس المستخدم للتحقق من الدخول
from Students import Student            # استيراد كلاس الطالب لإنشاء طالب جديد
from student_dashboard import StudentDashboard  # استيراد شاشة الطالب للانتقال لها
from admin_dashboard import AdminDashboard # استيراد شاشة الأدمن (لو احتجناها لاحقاً)

class Login(QDialog):
    def __init__(self,widget):
        super(Login,self).__init__()
        loadUi("ui/login.ui",self)
        self.widget=widget
        self.loginButton.clicked.connect(self.login)
        self.passwordInput.setEchoMode(QtWidgets.QLineEdit.Password)
        self.createButton.clicked.connect(self.open_signup)
    def login(self):
        email = self.emailInput.text()
        password = self.passwordInput.text()

        if email == "" or password == "":
            self.statusLabel.setText("Please enter email and password")
            return

        user = User.authenticate(email, password)

        if user:
            # -- حالة النجاح --
            self.statusLabel.setText("Login Successful!")
            
            # نفحص الدور: هل هو طالب؟
            if user.role == "student":
                # نفتح شاشة الطالب ونمرر لها رقم الطالب (مهم جداً عشان تطلع بياناته)
                self.dashboard = StudentDashboard(user.student_id) 
                self.dashboard.show()
                self.close() # نقفل شاشة الدخول الحالية
            else:
                self.statusLabel.setText("Welcome Admin (Dashboard not linked)")
        else:
            # -- حالة الفشل --
            self.statusLabel.setText("Invalid email or password")
    def open_signup(self):
        signup_window = signup(self.widget)
        self.widget.addWidget(signup_window)
        self.widget.setCurrentIndex(self.widget.currentIndex()+1)

class signup(QDialog):      
    def __init__(self,widget):
        self.widget=widget
        super(signup,self).__init__()
        loadUi("ui/signup.ui",self)
        self.signupButton.clicked.connect(self.signup)

    def signup(self):
        # 1. سحب البيانات من الحقول
        name = self.NameInput.text()
        student_id = self.IdInput.text()
        email = self.emailInput.text()
        program = self.programInput.text()
        level= self.levelInput.text()
        password = self.passwordInput.text()
        # تحويل المستوى لرقم (مهم عشان الداتا بيس)
        try:
            # تحويل المستوى لرقم
            level_int = int(level)

            # 1. حفظ بيانات الطالب
            new_student = Student(student_id=student_id, name=name, email=email, program=program, level=level_int)
            new_student.save_to_db()

            # 2. إنشاء حساب دخول
            User.create_user(email=email, password=password, role="student", student_id=student_id)

            print("تم التسجيل بنجاح!")
            
            # العودة لشاشة الدخول
            #login_window = Login()
            #self.widget.addWidget(login_window)
            #self.widget.setCurrentIndex(self.widget.currentIndex()+1)
            self.widget.removeWidget(self)

        except Exception as e:
            print("حدث خطأ:", e)
#app = QtWidgets.QApplication(sys.argv)
#window = Login()
#widget=QtWidgets.QStackedWidget()
#widget.addWidget(window)
#widget.setFixedWidth(400)
#widget.setFixedHeight(500)
#widget.show()
#app.exec_()
