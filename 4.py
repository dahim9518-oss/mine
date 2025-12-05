    def get_registered_courses_objects(self, student_id):
        """تجلب كائنات المواد التي سجلها الطالب فعلياً (عشان نحسب ساعاتها)"""
        try:
            # 1. نجيب أكواد المواد من جدول التسجيلات
            query = """
                SELECT o.course_code 
                FROM registrations r
                JOIN offerings o ON r.offering_id = o.offering_id
                WHERE r.student_id = ?
            """
            self.cursor.execute(query, (student_id,))
            rows = self.cursor.fetchall()
            
            # 2. نحول الأكواد إلى كائنات (CourseData)
            course_objects = []
            for row in rows:
                code = row[0]
                course_obj = self.get_Course_Data(code) # نستفيد من دالتنا القديمة
                if course_obj:
                    course_objects.append(course_obj)
            
            return course_objects
        except Exception as e:
            print("Error fetching registered courses:", e)
            return []
