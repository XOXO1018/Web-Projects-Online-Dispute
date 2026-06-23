import java.sql.*;
import java.util.Scanner;

public class SchoolManager {

    // 数据库配置
    static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";
    static final String DB_URL = "jdbc:mysql://localhost:3306/school_system?useSSL=false&serverTimezone=UTC&characterEncoding=utf8&allowPublicKeyRetrieval=true";
    static final String USER = "root";
    static final String PASS = "lzz1212147474";

    static Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        Connection conn = null;
        try {
            Class.forName(JDBC_DRIVER);
            System.out.println("正在连接数据库...");
            conn = DriverManager.getConnection(DB_URL, USER, PASS);
            System.out.println("数据库连接成功！");

            while (true) {
                System.out.println("\n========== 用户与课程管理系统 ==========");
                System.out.println("1. 学生信息管理 (录入/修改)");
                System.out.println("2. 教师信息管理 (录入/修改)");
                System.out.println("3. 课程信息管理 (添加/删除/设置详情)");
                System.out.println("0. 退出系统");
                System.out.print("请选择操作: ");

                int choice = scanner.nextInt();
                if (choice == 0) break;

                switch (choice) {
                    case 1: manageStudents(conn); break;
                    case 2: manageTeachers(conn); break;
                    case 3: manageCourses(conn); break;
                    default: System.out.println("无效输入，请重试。");
                }
            }

        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            try { if (conn != null) conn.close(); } catch (SQLException se) { se.printStackTrace(); }
        }
    }

    // ================== 学生管理模块 (修正版) ==================
    private static void manageStudents(Connection conn) throws SQLException {
        System.out.println("\n--- 学生管理 ---");
        System.out.println("1. 录入新学生");
        System.out.println("2. 修改学生信息");
        int op = scanner.nextInt();

        if (op == 1) {
            System.out.print("输入学生学号: ");
            String studentId = scanner.next();
            System.out.print("输入学生姓名: ");
            String name = scanner.next();
            System.out.print("输入年龄: ");
            int age = scanner.nextInt();
            System.out.print("输入性别: ");
            String gender = scanner.next();

            // 数据库表结构：name, age, gender, id
            String sql = "INSERT INTO students (id, name, age, gender) VALUES (?, ?, ?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, studentId);
            pstmt.setString(2, name);
            pstmt.setInt(3, age);
            pstmt.setString(4, gender);
            try {
                pstmt.executeUpdate();
                System.out.println(">> 学生录入成功！");
            } catch (SQLIntegrityConstraintViolationException e) {
                System.out.println(">> 录入失败：该学号已存在！");
            }
            pstmt.close();

        } else if (op == 2) {
            System.out.print("输入要修改的学生学号: ");
            String oldId = scanner.next();
            System.out.print("输入新学号: ");
            String newId = scanner.next();
            System.out.print("输入新姓名: ");
            String name = scanner.next();
            System.out.print("输入新年龄: ");
            int age = scanner.nextInt();
            System.out.print("输入新性别: ");
            String gender = scanner.next();

            // 修改所有字段，包括学号
            String sql = "UPDATE students SET id=?, name=?, age=?, gender=? WHERE id=?";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, newId);
            pstmt.setString(2, name);
            pstmt.setInt(3, age);
            pstmt.setString(4, gender);
            pstmt.setString(5, oldId);
            try {
                int rows = pstmt.executeUpdate();
                if(rows > 0) System.out.println(">> 学生信息修改成功！");
                else System.out.println(">> 未找到该学号的学生。");
            } catch (SQLIntegrityConstraintViolationException e) {
                System.out.println(">> 修改失败：新学号已存在！");
            }
            pstmt.close();
        }
    }

    // ================== 教师管理模块 (修正版) ==================
    private static void manageTeachers(Connection conn) throws SQLException {
        System.out.println("\n--- 教师管理 ---");
        System.out.println("1. 录入新教师");
        System.out.println("2. 修改教师信息");
        int op = scanner.nextInt();

        if (op == 1) {
            System.out.print("输入教师工号: ");
            String teacherId = scanner.next();
            System.out.print("输入教师姓名: ");
            String name = scanner.next();
            System.out.print("输入教学科目: ");
            String subject = scanner.next();

            // 数据库表结构：name, subject, id
            String sql = "INSERT INTO teachers (id, name, subject) VALUES (?, ?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, teacherId);
            pstmt.setString(2, name);
            pstmt.setString(3, subject);
            try {
                pstmt.executeUpdate();
                System.out.println(">> 教师录入成功！");
            } catch (SQLIntegrityConstraintViolationException e) {
                System.out.println(">> 录入失败：该工号已存在！");
            }
            pstmt.close();

        } else if (op == 2) {
            System.out.print("输入要修改的教师工号: ");
            String oldId = scanner.next();
            System.out.print("输入新工号: ");
            String newId = scanner.next();
            System.out.print("输入新姓名: ");
            String name = scanner.next();
            System.out.print("输入新科目: ");
            String subject = scanner.next();

            // 修改所有字段，包括工号
            String sql = "UPDATE teachers SET id=?, name=?, subject=? WHERE id=?";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, newId);
            pstmt.setString(2, name);
            pstmt.setString(3, subject);
            pstmt.setString(4, oldId);
            try {
                int rows = pstmt.executeUpdate();
                if(rows > 0) System.out.println(">> 教师信息修改成功！");
                else System.out.println(">> 未找到该工号的教师。");
            } catch (SQLIntegrityConstraintViolationException e) {
                System.out.println(">> 修改失败：新工号已存在！");
            }
            pstmt.close();
        }
    }

    // ================== 课程管理模块 (修正版) ==================
    private static void manageCourses(Connection conn) throws SQLException {
        System.out.println("\n--- 课程管理 ---");
        System.out.println("1. 添加新课程");
        System.out.println("2. 修改课程信息 (设置教室/时间/容量)");
        System.out.println("3. 删除课程");
        int op = scanner.nextInt();

        if (op == 1) {
            System.out.print("输入课程名称: ");
            String name = scanner.next();
            System.out.print("输入任课教师工号: ");
            String teacherId = scanner.next(); // 改为String类型，对应教师的id字段

            String sql = "INSERT INTO courses (course_name, teacher_id) VALUES (?, ?)";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, name);
            pstmt.setString(2, teacherId); // 使用String类型
            try {
                pstmt.executeUpdate();
                System.out.println(">> 课程添加成功！后续请使用修改功能完善教室和时间。");
            } catch (SQLException e) {
                System.out.println(">> 添加失败，请确保教师工号存在。");
            }
            pstmt.close();

        } else if (op == 2) {
            System.out.print("输入要修改的课程ID: ");
            int cid = scanner.nextInt();

            System.out.print("设置新教室: ");
            String room = scanner.next();
            System.out.print("设置上课时间 (如 周一8:00): ");
            String time = scanner.next();
            System.out.print("设置课程容量: ");
            int capacity = scanner.nextInt();

            String sql = "UPDATE courses SET classroom=?, class_time=?, capacity=? WHERE id=?";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, room);
            pstmt.setString(2, time);
            pstmt.setInt(3, capacity);
            pstmt.setInt(4, cid);

            int rows = pstmt.executeUpdate();
            if(rows > 0) System.out.println(">> 课程详细信息已更新 (教室/时间/容量)！");
            else System.out.println(">> 未找到该ID的课程。");
            pstmt.close();

        } else if (op == 3) {
            System.out.print("输入要删除的课程ID: ");
            int cid = scanner.nextInt();

            String sql = "DELETE FROM courses WHERE id=?";
            PreparedStatement pstmt = conn.prepareStatement(sql);
            pstmt.setInt(1, cid);
            int rows = pstmt.executeUpdate();
            if(rows > 0) System.out.println(">> 课程已删除。");
            else System.out.println(">> 未找到该ID的课程。");
            pstmt.close();
        }
    }
}