-- 创建数据库和表结构
CREATE DATABASE IF NOT EXISTS course_selection_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;


USE course_selection_db;

-- 创建表
CREATE TABLE students (
                          student_id VARCHAR(20) PRIMARY KEY,
                          student_name VARCHAR(50) NOT NULL,
                          gender VARCHAR(10),
                          major VARCHAR(100),
                          grade VARCHAR(20)
);

CREATE TABLE courses (
                         course_id VARCHAR(20) PRIMARY KEY,
                         course_name VARCHAR(100) NOT NULL,
                         teacher VARCHAR(100),
                         credits INT,
                         class_time VARCHAR(50),
                         classroom VARCHAR(50)
);

CREATE TABLE course_selection (
                                  selection_id INT AUTO_INCREMENT PRIMARY KEY,
                                  student_id VARCHAR(20),
                                  course_id VARCHAR(20),
                                  selection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                  FOREIGN KEY (student_id) REFERENCES students(student_id),
                                  FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- 插入测试数据
INSERT INTO students VALUES
                         ('2021001', '张三', '男', '计算机科学与技术', '2021级'),
                         ('2021002', '李四', '女', '软件工程', '2021级');

INSERT INTO courses VALUES
                        ('CS101', '计算机基础', '张老师', 3, '周一 8:00-9:40', '教101'),
                        ('CS201', '数据结构', '李老师', 4, '周三 10:00-11:40', '教102');

INSERT INTO course_selection (student_id, course_id) VALUES
                                                         ('2021001', 'CS101'),
                                                         ('2021001', 'CS201');

ALTER TABLE courses ADD COLUMN course_type VARCHAR(20) DEFAULT '必修';