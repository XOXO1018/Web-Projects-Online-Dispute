package database;

import java.sql.Connection;
import java.sql.Statement;
import javax.swing.JOptionPane;

/**
 * 数据库初始化类 - 创建表和初始化数据
 */
public class DBInitializer {

    /**
     * 创建所有表
     */
    public static boolean createTables() {
        DBConnection db = DBConnection.getInstance();
        Connection conn = null;
        Statement stmt = null;

        try {
            conn = db.getConnection();
            stmt = conn.createStatement();

            // 1. 创建教师表（根据您的思维导图）
            String createTeacherTable =
                    "CREATE TABLE IF NOT EXISTS teacher (" +
                            "teacher_id INT PRIMARY KEY AUTO_INCREMENT, " +
                            "teacher_name VARCHAR(50) NOT NULL, " +
                            "title VARCHAR(50), " +
                            "department VARCHAR(100), " +
                            "email VARCHAR(100), " +
                            "phone VARCHAR(20)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

            // 2. 创建课程表（根据您的思维导图）
            String createCourseTable =
                    "CREATE TABLE IF NOT EXISTS course (" +
                            "course_id VARCHAR(20) PRIMARY KEY, " +
                            "course_name VARCHAR(100) NOT NULL, " +        // 课程名
                            "class_time VARCHAR(50), " +                    // 上课时间
                            "teacher_id INT, " +                            // 授课老师
                            "credits INT NOT NULL, " +                      // 学分
                            "classroom VARCHAR(50), " +                     // 上课地点（扩展）
                            "course_description TEXT, " +                   // 课程描述（扩展）
                            "max_capacity INT, " +                          // 最大容量（扩展）
                            "current_selected INT DEFAULT 0, " +            // 当前选课人数（扩展）
                            "FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id) ON DELETE SET NULL" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

            // 3. 创建学生表
            String createStudentTable =
                    "CREATE TABLE IF NOT EXISTS student (" +
                            "student_id VARCHAR(20) PRIMARY KEY, " +
                            "student_name VARCHAR(50) NOT NULL, " +
                            "gender VARCHAR(10), " +
                            "major VARCHAR(100), " +
                            "grade VARCHAR(20), " +
                            "class_name VARCHAR(50), " +
                            "phone VARCHAR(20), " +
                            "email VARCHAR(100)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

            // 4. 创建选课表（根据您的思维导图 - 已选课程）
            String createSelectionTable =
                    "CREATE TABLE IF NOT EXISTS course_selection (" +
                            "selection_id INT PRIMARY KEY AUTO_INCREMENT, " +
                            "student_id VARCHAR(20), " +
                            "course_id VARCHAR(20), " +
                            "selection_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP, " +
                            "status VARCHAR(20) DEFAULT '已选', " +
                            "score DECIMAL(4,1), " +                          // 成绩（扩展）
                            "evaluation TEXT, " +                             // 评价（扩展）
                            "FOREIGN KEY (student_id) REFERENCES student(student_id) ON DELETE CASCADE, " +
                            "FOREIGN KEY (course_id) REFERENCES course(course_id) ON DELETE CASCADE, " +
                            "UNIQUE KEY unique_selection (student_id, course_id)" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

            // 5. 创建用户表（用于登录）
            String createUserTable =
                    "CREATE TABLE IF NOT EXISTS user_account (" +
                            "user_id VARCHAR(20) PRIMARY KEY, " +
                            "password VARCHAR(100) NOT NULL, " +
                            "user_type VARCHAR(20) DEFAULT 'student', " +     // student, teacher, admin
                            "last_login_time TIMESTAMP NULL, " +
                            "is_locked TINYINT(1) DEFAULT 0, " +
                            "created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP" +
                            ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4";

            // 执行所有建表语句
            stmt.execute(createTeacherTable);
            System.out.println("教师表创建成功");

            stmt.execute(createCourseTable);
            System.out.println("课程表创建成功");

            stmt.execute(createStudentTable);
            System.out.println("学生表创建成功");

            stmt.execute(createSelectionTable);
            System.out.println("选课表创建成功");

            stmt.execute(createUserTable);
            System.out.println("用户表创建成功");

            return true;

        } catch (Exception e) {
            System.err.println("创建表失败: " + e.getMessage());
            JOptionPane.showMessageDialog(null,
                    "数据库表创建失败: " + e.getMessage(),
                    "数据库错误", JOptionPane.ERROR_MESSAGE);
            return false;
        } finally {
            db.closeResources(null, stmt, conn);
        }
    }

    /**
     * 插入初始化数据
     */
    public static boolean initSampleData() {
        DBConnection db = DBConnection.getInstance();

        try {
            // 1. 插入教师数据
            String insertTeachers =
                    "INSERT IGNORE INTO teacher (teacher_name, title, department) VALUES " +
                            "('张教授', '教授', '计算机科学与技术系'), " +
                            "('李副教授', '副教授', '软件工程系'), " +
                            "('王老师', '讲师', '信息管理系'), " +
                            "('赵教授', '教授', '人工智能学院')";

            // 2. 插入课程数据（根据您的思维导图字段）
            String insertCourses =
                    "INSERT IGNORE INTO course (course_id, course_name, class_time, teacher_id, credits, classroom) VALUES " +
                            "('CS101', '计算机基础', '周一 8:00-9:40', 1, 3, '教101'), " +
                            "('CS201', '数据结构', '周三 10:00-11:40', 1, 4, '教102'), " +
                            "('CS301', '算法设计与分析', '周五 13:30-15:10', 1, 4, '教103'), " +
                            "('SE101', '软件工程', '周二 8:00-9:40', 2, 3, '教201'), " +
                            "('SE201', '软件测试', '周四 10:00-11:40', 2, 3, '教202'), " +
                            "('IM101', '数据库原理', '周三 13:30-15:10', 3, 3, '教301'), " +
                            "('IM201', '数据挖掘', '周五 10:00-11:40', 3, 3, '教302'), " +
                            "('AI101', '人工智能导论', '周二 13:30-15:10', 4, 4, '教401'), " +
                            "('AI201', '机器学习', '周四 15:30-17:10', 4, 4, '教402')";

            // 3. 插入学生数据
            String insertStudents =
                    "INSERT IGNORE INTO student (student_id, student_name, gender, major, grade) VALUES " +
                            "('2021001', '张三', '男', '计算机科学与技术', '2021级'), " +
                            "('2021002', '李四', '女', '软件工程', '2021级'), " +
                            "('2021003', '王五', '男', '信息管理与信息系统', '2021级'), " +
                            "('2021004', '赵六', '女', '人工智能', '2021级'), " +
                            "('2022001', '钱七', '男', '计算机科学与技术', '2022级')";

            // 4. 插入选课数据
            String insertSelections =
                    "INSERT IGNORE INTO course_selection (student_id, course_id) VALUES " +
                            "('2021001', 'CS101'), " +
                            "('2021001', 'CS201'), " +
                            "('2021001', 'SE101'), " +
                            "('2021001', 'IM101'), " +
                            "('2021002', 'CS101'), " +
                            "('2021002', 'IM101'), " +
                            "('2021002', 'AI101'), " +
                            "('2021003', 'CS201'), " +
                            "('2021003', 'SE101'), " +
                            "('2021004', 'AI101'), " +
                            "('2021004', 'AI201'), " +
                            "('2021004', 'IM201')";

            // 5. 插入用户数据（密码使用MD5加密）
            String insertUsers =
                    "INSERT IGNORE INTO user_account (user_id, password, user_type) VALUES " +
                            "('2021001', 'e10adc3949ba59abbe56e057f20f883e', 'student'), " +  // 密码：123456
                            "('2021002', 'e10adc3949ba59abbe56e057f20f883e', 'student'), " +
                            "('2021003', 'e10adc3949ba59abbe56e057f20f883e', 'student'), " +
                            "('2021004', 'e10adc3949ba59abbe56e057f20f883e', 'student'), " +
                            "('teacher001', 'e10adc3949ba59abbe56e057f20f883e', 'teacher'), " +
                            "('admin001', 'e10adc3949ba59abbe56e057f20f883e', 'admin')";

            // 执行所有插入语句
            db.executeUpdate(insertTeachers);
            db.executeUpdate(insertCourses);
            db.executeUpdate(insertStudents);
            db.executeUpdate(insertSelections);
            db.executeUpdate(insertUsers);

            System.out.println("初始化数据插入成功");
            return true;

        } catch (Exception e) {
            System.err.println("插入初始化数据失败: " + e.getMessage());
            return false;
        }
    }

    /**
     * 数据库完整初始化
     */
    public static void initializeDatabase() {
        System.out.println("开始初始化数据库...");

        if (createTables()) {
            System.out.println("数据库表创建成功");

            if (initSampleData()) {
                System.out.println("初始化数据插入成功");
                JOptionPane.showMessageDialog(null,
                        "数据库初始化完成！\n用户名: 2021001\n密码: 123456",
                        "初始化成功", JOptionPane.INFORMATION_MESSAGE);
            } else {
                System.out.println("初始化数据插入失败");
            }
        } else {
            System.out.println("数据库表创建失败");
        }

        System.out.println("数据库初始化完成");
    }
}