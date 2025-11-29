from Data_Base import get_connection
import sqlite3
 


# اوبجكت فيه كل معلومات المادة
class CourseData:
    def __init__(self,code,name,credits,lecture_houre,lap_hour,capacity,prerequisites):
        self.code=code
        self.name=name
        self.creditis=credits
        self.lecture_houre=lecture_houre
        self.lap_hour=lap_hour
        self.capacity=capacity
        self.prerequisites=prerequisites
    
# اوبجكت فيه معلومات البلوك الزمني للمادة
class TimeBlock:
    def __init__(self,course_code,day,start_tim,end_tim):
        self.course_code=course_code
        self.day=day
        self.start_tim=start_tim
        self.end_tim=end_tim
    





class RegistrationSystem: 
    def __init__(self): 
        self.con=get_connection()  #   (بس تفتح الملف)   الاتصال مع ملف الداتا 
       
        self.cursor=self.con.cursor         # هاذا زي الموشر تستعمله عشان تتعامل مع الداتابيس 
    


#----------------------------------------------------------------------------------------------------------
#دوال القيت (جلب البيانات من الداتا بيز)
#----------------------------------------------------------------------------------------------------------


#1 تججيب بيانات الطالب من الداتا بيز

    def get_student_information(self,student_id):     # Student id -----GUI
        try: 
           sql_code_for_Student_Information= f""" SELECT name, program, level FROM students WHERE student_id ={student_id} """
           
           self.cursor.execute(sql_code_for_Student_Information)
           info = self.cursor.fetchone()
           return info
        except sqlite3.Error as e:
            print(print("Database Error: Could not  fetch info  for", student_id, ". Details:", e))
            return None



           
  #2 تججيب الكورسات المكتملة للطالب من الداتا بيز          
 
    def get_student_transcript(self,student_id):  #  STUDENT ID -------GUI
 
       try:
        sql_code_for_getCorseCompleted=f"""SELECT course_code FROM transcripts WHERE student_id = {student_id} AND grade != 'F'"""
 
        
        self.cursor.execute(sql_code_for_getCorseCompleted)
         
        Results_corses_completed = self.cursor.fetchall()
        corses_Completed=[]
        for row in Results_corses_completed:
            corses_Completed.append(row[0])
            return corses_Completed
            
       except sqlite3.Error as e:
            print("Database Error: Could not fetch transcript for", student_id, ". Details:", e)
            return []

            
            
            
  #3 تججيب بيانات المادة من الداتا بيز          
    def get_Course_Data(self,course_code): # Course code-------------GUI


        try:
            sql_code_for_getCourseData=f""" SELECT name, credits, max_capacity, lecture_hours, lab_hours 
                               FROM courses WHERE course_code = ={course_code} """
            
            self.cursor.execute(sql_code_for_getCourseData)
            Corse_Data= self.cursor.fetchone()
            if not Corse_Data:
                return None
            

            sql_code_for_prerequisites= f"""SELECT prereq_code FROM prerequisites WHERE course_code ={course_code} """
           
            self.cursor.execute(sql_code_for_prerequisites)
            course_pre_results=self.cursor.fetchall()
            course_pre=[]

            for row in course_pre_results:
                course_pre.append(row[0])

            return CourseData(code=course_code,name=Corse_Data[0],credits=Corse_Data[1],lecture_houre=Corse_Data[2],lap_hour=Corse_Data[3],capacity=Corse_Data[4],prerequisites=course_pre)
        except sqlite3.Error as e:
            print("Database Error: Could not fetch Course data for", Course_Code, ". Details:", e)


#4 تججيب خطة البرنامج من الداتا بيز
    def get_program_plan(self,program,levle,course_code):
        try:
            sql_Code_for_GetProgramLevle= f""" SELECT course_code FROM program_plans WHERE program = {program} AND level = {levle} AND course_code = {course_code} """ # يتحقق اذا كلهم في نفس الخطة ولا لا
            self.cursor.execute(sql_Code_for_GetProgramLevle)
            result=self.cursor.fetchone()
            return result
    
        except sqlite3.Error as e:
            print(f"Database Error: Failed to check program plan for {course_code}. {e}")
            return None
  #5 تججيب عدد التسجيل الحالي من قاعدة التسجيل  

    def get_current_regestion(self, course_code): # دالة تاخد عدد التسجيل الحالي من قاعدة التسجيل 
     try:
    
         sql_code_for_CuurentRegestion= f"SELECT COUNT(r.student_id) FROM registrations r JOIN offerings o ON r.offering_id = o.offering_id WHERE o.course_code =  {course_code}"
         self.cursor.execute(sql_code_for_CuurentRegestion)
    
         Current_Regestion = self.cursor.fetchone()[0]

         return Current_Regestion
    
     except sqlite3.Error as e:
        print(f"Database Error: Failed to check enrollment for {course_code}. {e}")
        return 0
    

#6تججيب الجدول الزمني للمادة من قاعدة offering            
    def get_schedule_for_course(self, selected_Corses_Code): # selected_Corses_Code -------------GUI
        all_time_blocks=[]
        for course in selected_Corses_Code:
          try:
             sql_code_for_schedule = f"""SELECT day_of_week, start_time, end_time FROM offering WHERE course_code = {course.code}"""
             self.cursor.execute(sql_code_for_schedule)
             schedule_results = self.cursor.fetchall()
          except sqlite3.Error as e:
               
                print("DB Error: Failed to fetch offerings for", course.code , e)
                continue 
          for raw_block in schedule_results:
                day = raw_block[0]
                start_time_raw = raw_block[1]
                end_time_raw = raw_block[2]
                try:

                #تحويل الوقت
                 start_time_parts = start_time_raw.split(':')
                 start_hours = int(start_time_parts[0])
                 start_minutes = int(start_time_parts[1])
                 processed_start_time_in_minutes = start_hours * 60 + start_minutes
                 end_time_parts = end_time_raw.split(':')
                 end_hours = int(end_time_parts[0])
                 end_minutes = int(end_time_parts[1])
                 processed_end_time_in_minutes = end_hours * 60 + end_minutes
                 all_time_blocks.append(TimeBlock(course.code,day,processed_start_time_in_minutes,processed_end_time_in_minutes))

                except ValueError:
                    print("Error parsing time format for course ",course.code,"Invalid time format.")
                    continue

        return all_time_blocks



               
         
     
   #----------------------------------------------------------------------------------------------------------
   # دوال التشييك (التحقق من الشروط)
#----------------------------------------------------------------------------------------------------------
# الناتج من كل دالة يكون يا اما ترو يا رسالة خطأ
#----------------------------------------------------------------------------------------------------------


#1 دالة التشييك على عدد الساعات المتاحة لكل ترم 
    def check_credit_hours(self,Corses_with_data):
        Min_credits=12
        Max_credits=18
        total_credits=0
        for i in Corses_with_data:
            total_credits+=i.credits 
        
        if total_credits<Min_credits:
            return f"Total credit hours {total_credits} is less than minimum required {Min_credits}."
        if total_credits>Max_credits:
            return f"Total credit hours {total_credits} exceeds maximum allowed {Max_credits}."


        return True
        


#2 دالة التشييك على المتطلبات المسبقة لكل مادة
    def check_prerequisites(self,student_transcipt,Courses_with_data):
        Course_prerequisites=Courses_with_data.prerequisites
        if not Course_prerequisites:    # لو ما فيها متطلبات اعتبرها ترو
            return True
        for pre in Course_prerequisites:
            if pre not in student_transcipt:
                return f"Cannot registor for {Courses_with_data.code}.prerequisites {pre} not completed."
            
        return True

        


#3 دالة التشييك على خطة الطالب
    def check_plan(self,student_info,Courses_with_data):
        student_program=student_info[1]   # x اسم برنامج الطالب من القادة
        student_levle=student_info[2] # x لفل الطالب من القاعدة 
        Courses_Allowed=self.get_program_plan(student_program,student_levle,Courses_with_data.code)
        if Courses_Allowed is None:
            return "Cannot register:", Courses_with_data.code, "is not part of the standard plan for your current level and program."
        
        return True

        

#4 دالة التشييك على التعارض الزمني بين المواد
    def check_conflict(self,selected_Corses_Code):   # Selected_Corses_Code -------------GUI
        all_schedule_blocks=self.get_schedule_for_course(selected_Corses_Code)
        for i in range(len(all_schedule_blocks)):
            for j in range(i+1,len(all_schedule_blocks)):
                block1=all_schedule_blocks[i]
                block2=all_schedule_blocks[j]
                if block1.start < block2.end and block2.start < block1.end:
                        
                        
                        return f"Time conflict detected: Course {block1.code} overlaps with {block2.code} on {block1.day}."
                
        return True 
        

#5 دالة التشييك على اعلى عدد لي الطلاب 
    def check_capacity(self,Corse_Data):
     max_capacity=Corse_Data.capacity
     course_code=Corse_Data.code
     current_re=self.get_current_regestion
    
     if current_re >= max_capacity:
        return f"Cannot register for {course_code}: Course capacity of {max_capacity} has been reached."
     return True

    
    
#----------------------------------------------------------------------------------------------------------
# دالة التحقق النهائية (تستدعي كل الدوال السابقة)






    def validate_schedule(self,Student_id,Selected_Corses_Code): # Student_id and Selected_Corses_Code ----------------GUI
        try:
            student_transcipt=self.get_student_transcript(Student_id)# استدعاء الدالة حق الكورسات المكتملة
            student_info=self.get_student_information(Student_id)# استدعاء الدالة حق معلومات الطالب
            Courses_with_data=[] 
            #تجهيز قائمة فاضية عشان تخزن فيها بيانات الكورسات اللي الطالب اختارها

            for i in Selected_Corses_Code:
                course_data=self.get_Course_Data(i)
                if course_data is None:
                    return "One of Courses does not exist."
                Courses_with_data.append(course_data)



                #تشييك cresit hours
            result=self.check_credit_hours(Courses_with_data)
            if result is not True:  
                return result




                #تشييك prerequisites   لكل مادة 
            for Corse in Courses_with_data:
                result=self.check_prerequisites(student_transcipt,Corse)
                if result is not True:
                    return result
                

                #تشييك plan
            for course in Courses_with_data:
             
             result=self.check_plan(student_info,course)
             if result is not True: 
              return result




                #تشييك التعارض
            for course in Courses_with_data:
               result=self.check_conflict(Courses_with_data)
               if result is not True: 
                return result




                
            #تشييك capacity
            for Corse in Courses_with_data:
                result=self.check_capacity(course)
                if result is not True:
                    return result
        pass
pass


