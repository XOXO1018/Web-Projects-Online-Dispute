import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.sql.*;
import java.util.Vector;

public class CourseSelectionSystem {
    public static void main(String[] args) {
        // 启动选课系统
        SwingUtilities.invokeLater(() -> {
            new SelectionQueryFrame();
        });
    }
}

// 数据库连接工具类
class DatabaseConnection {
    private static final String URL = "jdbc:mysql://localhost:3306/school_system?useSSL=false&serverTimezone=Asia/Shanghai";
    private static final String USER = "root";
    private static final String PASSWORD = "lzz1212147474";

    public static Connection getConnection() {
        try {
            // 加载MySQL驱动[6,8](@ref)
            Class.forName("com.mysql.cj.jdbc.Driver");
            return DriverManager.getConnection(URL, USER, PASSWORD);
        } catch (Exception e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(null, "数据库连接失败！\n" + e.getMessage(),
                    "错误", JOptionPane.ERROR_MESSAGE);
            return null;
        }
    }
}

// 选课查询主界面
class SelectionQueryFrame extends JFrame {
    private JTextField studentIdField;
    private JButton queryButton;
    private JButton resetButton;
    private JTable courseTable;
    private DefaultTableModel tableModel;
    private JLabel infoLabel; // 统计信息标签

    public SelectionQueryFrame() {
        setTitle("教务处网上选课系统 - 已选课程查询");
        setSize(900, 600);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLayout(new BorderLayout(10, 10));

        // 设置背景色
        getContentPane().setBackground(new Color(240, 240, 240));

        // 创建顶部面板
        JPanel topPanel = createTopPanel();
        add(topPanel, BorderLayout.NORTH);

        // 创建表格面板
        JPanel tablePanel = createTablePanel();
        add(tablePanel, BorderLayout.CENTER);

        // 创建底部按钮面板
        JPanel bottomPanel = createBottomPanel();
        add(bottomPanel, BorderLayout.SOUTH);

        setVisible(true);
    }

    // 创建顶部查询面板
    private JPanel createTopPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(new Color(240, 240, 240));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        // 标题
        JLabel titleLabel = new JLabel("已选课程查询", SwingConstants.CENTER);
        titleLabel.setFont(new Font("微软雅黑", Font.BOLD, 24));
        titleLabel.setForeground(new Color(0, 120, 215));
        panel.add(titleLabel, BorderLayout.NORTH);

        // 查询条件面板
        JPanel queryPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 20));
        queryPanel.setBackground(new Color(240, 240, 240));

        JLabel studentIdLabel = new JLabel("学号/工号：");
        studentIdLabel.setFont(new Font("微软雅黑", Font.PLAIN, 16));

        studentIdField = new JTextField(20);
        studentIdField.setFont(new Font("微软雅黑", Font.PLAIN, 16));
        studentIdField.setPreferredSize(new Dimension(200, 35));
        studentIdField.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(new Color(200, 200, 200), 1),
                BorderFactory.createEmptyBorder(5, 10, 5, 10)
        ));

        queryButton = new JButton("查询课程");
        queryButton.setFont(new Font("微软雅黑", Font.BOLD, 16));
        queryButton.setForeground(Color.WHITE);
        queryButton.setBackground(new Color(64, 158, 255));
        queryButton.setPreferredSize(new Dimension(120, 40));
        queryButton.setBorderPainted(false);
        queryButton.setFocusPainted(false);
        queryButton.setCursor(new Cursor(Cursor.HAND_CURSOR));

        resetButton = new JButton("重置");
        resetButton.setFont(new Font("微软雅黑", Font.PLAIN, 16));
        resetButton.setPreferredSize(new Dimension(100, 40));
        resetButton.setCursor(new Cursor(Cursor.HAND_CURSOR));

        queryPanel.add(studentIdLabel);
        queryPanel.add(studentIdField);
        queryPanel.add(queryButton);
        queryPanel.add(resetButton);

        panel.add(queryPanel, BorderLayout.CENTER);

        // 添加事件监听器
        addEventListeners();

        return panel;
    }

    // 创建表格面板
    private JPanel createTablePanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(BorderFactory.createEmptyBorder(0, 20, 20, 20));

        // 创建表格
        String[] columnNames = {"课程编号", "课程名称", "上课时间", "授课老师", "学分", "上课地点"};
        tableModel = new DefaultTableModel(columnNames, 0) {
            @Override
            public boolean isCellEditable(int row, int column) {
                return false; // 表格不可编辑
            }
        };

        courseTable = new JTable(tableModel);
        courseTable.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        courseTable.setRowHeight(35);
        courseTable.getTableHeader().setFont(new Font("微软雅黑", Font.BOLD, 14));
        courseTable.getTableHeader().setBackground(new Color(64, 158, 255));
        courseTable.getTableHeader().setForeground(Color.WHITE);
        courseTable.setSelectionBackground(new Color(220, 240, 255));
        courseTable.setSelectionForeground(Color.BLACK);

        // 设置列宽
        courseTable.getColumnModel().getColumn(0).setPreferredWidth(80);
        courseTable.getColumnModel().getColumn(1).setPreferredWidth(200);
        courseTable.getColumnModel().getColumn(2).setPreferredWidth(150);
        courseTable.getColumnModel().getColumn(3).setPreferredWidth(100);
        courseTable.getColumnModel().getColumn(4).setPreferredWidth(60);
        courseTable.getColumnModel().getColumn(5).setPreferredWidth(150);

        // 添加表格到滚动面板
        JScrollPane scrollPane = new JScrollPane(courseTable);
        scrollPane.setBorder(BorderFactory.createLineBorder(new Color(200, 200, 200)));

        panel.add(scrollPane, BorderLayout.CENTER);

        return panel;
    }

    // 创建底部面板
    private JPanel createBottomPanel() {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
        panel.setBackground(new Color(240, 240, 240));

        // 统计信息标签
        infoLabel = new JLabel("总计：0 门课程 | 总学分：0");
        infoLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        infoLabel.setForeground(Color.GRAY);
        panel.add(infoLabel);

        return panel;
    }

    // 添加事件监听器
    private void addEventListeners() {
        // 查询按钮点击事件[1,2](@ref)
        queryButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                queryCourses();
            }
        });

        // 重置按钮点击事件
        resetButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                resetForm();
            }
        });

        // 按回车键查询
        studentIdField.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                queryCourses();
            }
        });
    }

    // 查询课程信息[3,7](@ref)
    private void queryCourses() {
        String studentId = studentIdField.getText().trim();

        if (studentId.isEmpty()) {
            JOptionPane.showMessageDialog(this, "请输入学号/工号！",
                    "提示", JOptionPane.WARNING_MESSAGE);
            studentIdField.requestFocus(); // 焦点回到输入框
            return;
        }

        // 清空表格
        tableModel.setRowCount(0);

        // 从数据库查询数据[6,8](@ref)
        Connection conn = null;
        PreparedStatement pstmt = null;
        ResultSet rs = null;

        try {
            conn = DatabaseConnection.getConnection();
            if (conn == null) return;

            // 修正后的SQL查询语句 - 使用正确的字段名[3](@ref)
            String sql = "SELECT c.id, c.course_name, c.class_time, " +
                    "t.name AS teacher_name, c.credits, c.classroom " +  // 关联教师表获取姓名
                    "FROM enrollment sc " +
                    "JOIN courses c ON sc.course_id = c.id " +
                    "JOIN teachers t ON c.teacher_id = t.id " +  // 关联teachers表
                    "WHERE sc.student_id = ? " +
                    "ORDER BY sc.course_id ;";

            pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, studentId); // 设置参数[7](@ref)
            rs = pstmt.executeQuery();

            int totalRows = 0;
            int totalCredits = 0;

            // 遍历结果集[7](@ref)
            while (rs.next()) {
                String courseId = rs.getString("id");
                String courseName = rs.getString("course_name");
                String classTime = rs.getString("class_time");
                String teacher = rs.getString("id"); // 修正字段名
                int credits = rs.getInt("credits");
                String classroom = rs.getString("classroom");

                // 添加到表格
                Vector<Object> row = new Vector<>();
                row.add(courseId);
                row.add(courseName);
                row.add(classTime);
                row.add(teacher);
                row.add(credits);
                row.add(classroom);

                tableModel.addRow(row);
                totalRows++;
                totalCredits += credits;
            }

            if (totalRows == 0) {
                JOptionPane.showMessageDialog(this,
                        "没有找到学号为 " + studentId + " 的选课记录！",
                        "查询结果", JOptionPane.INFORMATION_MESSAGE);
                infoLabel.setText("总计：0 门课程 | 总学分：0");
            } else {
                // 更新统计信息
                updateStats(totalRows, totalCredits);

                // 显示成功消息
                JOptionPane.showMessageDialog(this,
                        "成功查询到 " + totalRows + " 门课程，总学分：" + totalCredits,
                        "查询成功", JOptionPane.INFORMATION_MESSAGE);
            }

        } catch (SQLException e) {
            e.printStackTrace();
            JOptionPane.showMessageDialog(this,
                    "查询失败！\n" + e.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            infoLabel.setText("总计：0 门课程 | 总学分：0");
        } finally {
            // 关闭资源[6](@ref)
            try {
                if (rs != null) rs.close();
                if (pstmt != null) pstmt.close();
                if (conn != null) conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }
    }

    // 更新统计信息
    private void updateStats(int totalCourses, int totalCredits) {
        infoLabel.setText("总计：" + totalCourses + " 门课程 | 总学分：" + totalCredits);
    }

    // 重置表单
    private void resetForm() {
        studentIdField.setText("");
        tableModel.setRowCount(0);
        infoLabel.setText("总计：0 门课程 | 总学分：0");
        studentIdField.requestFocus(); // 焦点回到输入框
    }
}