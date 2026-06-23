import javax.swing.*;
import javax.swing.border.EmptyBorder;
import javax.swing.table.DefaultTableCellRenderer;
import javax.swing.table.DefaultTableModel;
import javax.swing.table.TableRowSorter;
import javax.swing.table.JTableHeader;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import java.util.Vector;
import java.awt.image.BufferedImage;
import javax.imageio.ImageIO;
import java.io.IOException;

public class Main {
    // 统一数据库连接配置（全局共用）
    public static final String DB_URL = "jdbc:mysql://localhost:3306/school_system?useSSL=false&serverTimezone=UTC&characterEncoding=utf8&allowPublicKeyRetrieval=true";
    static final String DB_USER = "root";//连接至本地数据库账户
    static final String DB_PASSWORD = "lzz1212147474";
    static final String JDBC_DRIVER = "com.mysql.cj.jdbc.Driver";

    // 存储当前登录的学生ID
    private static long CURRENT_LOGIN_STUDENT_ID;

    // 全局UI样式常量
    public static final Color PRIMARY_COLOR = new Color(51, 102, 204); // 主色调-蓝色
    public static final Color SECONDARY_COLOR = new Color(245, 247, 250); // 背景色-浅灰蓝
    public static final Color ACCENT_COLOR = new Color(255, 102, 0); // 强调色-橙色
    public static final Color SUCCESS_COLOR = new Color(76, 175, 80); // 成功色-绿色
    public static final Color ERROR_COLOR = new Color(244, 67, 54); // 错误色-红色
    public static final Font FONT_MAIN = new Font("微软雅黑", Font.PLAIN, 14);
    public static final Font FONT_BOLD = new Font("微软雅黑", Font.BOLD, 14);
    public static final Font FONT_TITLE = new Font("微软雅黑", Font.BOLD, 18);
    public static final Font FONT_HEADING = new Font("微软雅黑", Font.BOLD, 22);

    public static void main(String[] args) {
        // 设置全局UI风格
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            // 全局UI样式设置
            UIManager.put("Button.font", FONT_MAIN);
            UIManager.put("Label.font", FONT_MAIN);
            UIManager.put("TextField.font", FONT_MAIN);
            UIManager.put("PasswordField.font", FONT_MAIN);
            UIManager.put("ComboBox.font", FONT_MAIN);
            UIManager.put("CheckBox.font", FONT_MAIN);
        } catch (Exception ignored) {}

        // 初始化数据库连接（测试连接）
        try (Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD)) {
            System.out.println("数据库连接成功");
        } catch (SQLException e) {
            JOptionPane.showMessageDialog(null, "数据库连接失败：" + e.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            e.printStackTrace();
            return;
        }

        // 启动登录窗口
        LoginFrame loginFrame = new LoginFrame();
        loginFrame.setVisible(true);
    }

    // 数据库工具类：获取连接
    public static Connection getDBConnection() throws SQLException {
        return DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
    }

    // 设置当前登录学生ID
    public static void setCurrentStudentId(long studentId) {
        CURRENT_LOGIN_STUDENT_ID = studentId;
    }

    // 获取当前登录学生ID
    public static long getCurrentStudentId() {
        return CURRENT_LOGIN_STUDENT_ID;
    }
}
// 登录界面类 - 优化版
class LoginFrame extends JFrame {
    private JTextField idField;
    private JPasswordField passwordField;

    public LoginFrame() {
        // 窗口基础配置
        setTitle("广西师范大学教务处网上选课系统 - 登录");
        setSize(650, 450);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setResizable(false);

        // 主面板 - 使用边框布局，添加背景色
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(Main.SECONDARY_COLOR);
        mainPanel.setBorder(new EmptyBorder(20, 20, 20, 20));

        // 顶部标题面板
        JPanel titlePanel = new JPanel();
        titlePanel.setBackground(Main.SECONDARY_COLOR);
        titlePanel.setBorder(new EmptyBorder(0, 0, 30, 0));
        JLabel titleLabel = new JLabel("广西师范大学教务处网上选课系统");
        titleLabel.setFont(Main.FONT_HEADING);
        titleLabel.setForeground(Main.PRIMARY_COLOR);
        titlePanel.add(titleLabel);
        mainPanel.add(titlePanel, BorderLayout.NORTH);

        // 登录表单面板 - 居中显示，白色背景，圆角边框
        JPanel formPanel = new JPanel();
        formPanel.setLayout(new BoxLayout(formPanel, BoxLayout.Y_AXIS));
        formPanel.setBackground(Color.WHITE);
        formPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(Color.LIGHT_GRAY, 1),
                new EmptyBorder(30, 40, 30, 40)
        ));
        formPanel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // 学号/工号输入面板
        JPanel idPanel = createInputPanel("学号/工号：", true);
        formPanel.add(idPanel);
        formPanel.add(Box.createVerticalStrut(20));

        // 密码输入面板
        JPanel passwordPanel = createInputPanel("密码：", false);
        formPanel.add(passwordPanel);
        formPanel.add(Box.createVerticalStrut(30));

        // 按钮面板
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 15, 0));
        buttonPanel.setBackground(Color.WHITE);

        // 登录按钮 - 美化样式
        JButton loginButton = new JButton("登录");
        styleButton(loginButton, Main.PRIMARY_COLOR, Color.DARK_GRAY);

        // 忘记密码按钮 - 文字按钮样式
        JButton forgotPasswordButton = new JButton("忘记密码");
        forgotPasswordButton.setFont(new Font("微软雅黑", Font.PLAIN, 13));
        forgotPasswordButton.setForeground(Main.PRIMARY_COLOR);
        forgotPasswordButton.setBorderPainted(false);
        forgotPasswordButton.setContentAreaFilled(false);
        forgotPasswordButton.setCursor(new Cursor(Cursor.HAND_CURSOR));

        buttonPanel.add(loginButton);
        buttonPanel.add(forgotPasswordButton);
        formPanel.add(buttonPanel);

        // 中间面板用于居中表单
        JPanel centerPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        centerPanel.setBackground(Main.SECONDARY_COLOR);
        centerPanel.add(formPanel);
        mainPanel.add(centerPanel, BorderLayout.CENTER);

        setContentPane(mainPanel);

        // 登录按钮事件（核心修改：区分学生/教师跳转）
        loginButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                String id = idField.getText().trim();
                String password = new String(passwordField.getPassword()).trim();

                if (id.isEmpty() || password.isEmpty()) {
                    JOptionPane.showMessageDialog(LoginFrame.this, "请输入学号/工号和密码！", "提示", JOptionPane.WARNING_MESSAGE);
                    return;
                }

                // 验证身份（学生/教师）
                boolean isLoginSuccess = false;
                String role = "";
                long studentId = 0; // 存储学生ID

                try (Connection conn = Main.getDBConnection()) {
                    // 1. 先查学生表
                    String studentSql = "SELECT * FROM students WHERE id = ? AND password = ?";
                    try (PreparedStatement pstmt = conn.prepareStatement(studentSql)) {
                        pstmt.setString(1, id);
                        pstmt.setString(2, password);
                        ResultSet rs = pstmt.executeQuery();
                        if (rs.next()) {
                            isLoginSuccess = true;
                            role = "学生";
                            // 获取学生ID（转为long类型）
                            studentId = Long.parseLong(rs.getString("id"));
                        }
                    }

                    // 2. 学生表没找到，查教师表
                    if (!isLoginSuccess) {
                        String teacherSql = "SELECT * FROM teachers WHERE id = ? AND password = ?";
                        try (PreparedStatement pstmt = conn.prepareStatement(teacherSql)) {
                            pstmt.setString(1, id);
                            pstmt.setString(2, password);
                            ResultSet rs = pstmt.executeQuery();
                            if (rs.next()) {
                                isLoginSuccess = true;
                                role = "教师";
                            }
                        }
                    }
                } catch (SQLException ex) {
                    JOptionPane.showMessageDialog(LoginFrame.this, "登录失败：" + ex.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
                    ex.printStackTrace();
                    return;
                }

                // 登录结果处理
                if (isLoginSuccess) {
                    JOptionPane.showMessageDialog(LoginFrame.this, role + "登录成功！", "成功", JOptionPane.INFORMATION_MESSAGE);

                    // 学生登录成功 → 跳转到选课界面
                    if ("学生".equals(role)) {
                        Main.setCurrentStudentId(studentId);
                        LoginFrame.this.dispose();
                        SwingUtilities.invokeLater(() -> new CourseSelectionMySQLUI().setVisible(true));
                    }
                    // 教师登录成功 → 跳转到管理界面（核心修改）
                    else if ("教师".equals(role)) {
                        LoginFrame.this.dispose();
                        SwingUtilities.invokeLater(() -> new SchoolManagerGUI().setVisible(true));
                    }
                } else {
                    JOptionPane.showMessageDialog(LoginFrame.this, "学号/工号或密码错误！", "错误", JOptionPane.ERROR_MESSAGE);
                }
            }
        });

        // 忘记密码按钮事件
        forgotPasswordButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                openForgotPasswordFrame();
            }
        });
    }

    // 创建输入面板 - 统一样式
    private JPanel createInputPanel(String labelText, boolean isUsername) {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        panel.setBackground(Color.WHITE);

        JLabel label = new JLabel(labelText);
        label.setFont(Main.FONT_BOLD);
        label.setPreferredSize(new Dimension(80, 30));
        panel.add(label);

        JComponent inputComponent;
        if (isUsername) {
            idField = new JTextField(20);
            inputComponent = idField;
        } else {
            passwordField = new JPasswordField(20);
            inputComponent = passwordField;
        }

        inputComponent.setPreferredSize(new Dimension(220, 35));
        inputComponent.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(Color.LIGHT_GRAY, 1),
                new EmptyBorder(5, 10, 5, 10)
        ));

        panel.add(inputComponent);
        return panel;
    }

    // 美化按钮样式
    private void styleButton(JButton button, Color bgColor, Color fgColor) {
        button.setPreferredSize(new Dimension(120, 40));
        button.setFont(Main.FONT_BOLD);
        button.setBackground(bgColor);
        button.setForeground(fgColor);
        button.setBorder(BorderFactory.createEmptyBorder());
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));
        // 添加悬停效果
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor.darker());
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor);
            }
        });
    }

    // 打开忘记密码窗口
    private void openForgotPasswordFrame() {
        this.setVisible(false);
        ForgotPasswordFrame forgotPasswordFrame = new ForgotPasswordFrame(this);
        forgotPasswordFrame.setVisible(true);
    }

    // 返回登录窗口
    public void returnToLogin() {
        this.setVisible(true);
        idField.setText("");
        passwordField.setText("");
    }
}

// 忘记密码界面类 - 优化版
class ForgotPasswordFrame extends JFrame {
    private JTextField usernameField;
    private JPasswordField newPasswordField;
    private JPasswordField confirmPasswordField;
    private LoginFrame loginFrame;

    public ForgotPasswordFrame(LoginFrame loginFrame) {
        this.loginFrame = loginFrame;

        // 窗口基础配置
        setTitle("修改密码 - 广西师范大学选课系统");
        setSize(550, 480);
        setLocationRelativeTo(null);
        setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
        setResizable(false);

        // 主面板
        JPanel mainPanel = new JPanel(new BorderLayout());
        mainPanel.setBackground(Main.SECONDARY_COLOR);
        mainPanel.setBorder(new EmptyBorder(20, 20, 20, 20));

        // 标题面板
        JPanel titlePanel = new JPanel();
        titlePanel.setBackground(Main.SECONDARY_COLOR);
        titlePanel.setBorder(new EmptyBorder(0, 0, 20, 0));
        JLabel titleLabel = new JLabel("修改密码");
        titleLabel.setFont(Main.FONT_HEADING);
        titleLabel.setForeground(Main.PRIMARY_COLOR);
        titlePanel.add(titleLabel);
        mainPanel.add(titlePanel, BorderLayout.NORTH);

        // 表单面板
        JPanel formPanel = new JPanel();
        formPanel.setLayout(new BoxLayout(formPanel, BoxLayout.Y_AXIS));
        formPanel.setBackground(Color.WHITE);
        formPanel.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(Color.LIGHT_GRAY, 1),
                new EmptyBorder(30, 30, 30, 30)
        ));
        formPanel.setAlignmentX(Component.CENTER_ALIGNMENT);

        // 学号/工号输入面板
        JPanel usernamePanel = createInputPanel("学号/工号：", true);
        formPanel.add(usernamePanel);
        formPanel.add(Box.createVerticalStrut(15));

        // 新密码输入面板
        JPanel newPasswordPanel = createInputPanel("新密码：", false);
        formPanel.add(newPasswordPanel);
        formPanel.add(Box.createVerticalStrut(15));

        // 确认密码输入面板
        JPanel confirmPasswordPanel = createInputPanel("确认密码：", false);
        formPanel.add(confirmPasswordPanel);
        formPanel.add(Box.createVerticalStrut(30));

        // 按钮面板
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 0));
        buttonPanel.setBackground(Color.WHITE);

        JButton submitButton = new JButton("提交");
        JButton backButton = new JButton("返回登录");

        styleButton(submitButton, Main.PRIMARY_COLOR, Color.DARK_GRAY);
        styleButton(backButton, Color.GRAY, Color.DARK_GRAY);

        buttonPanel.add(submitButton);
        buttonPanel.add(backButton);
        formPanel.add(buttonPanel);

        // 中间面板
        JPanel centerPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        centerPanel.setBackground(Main.SECONDARY_COLOR);
        centerPanel.add(formPanel);
        mainPanel.add(centerPanel, BorderLayout.CENTER);

        setContentPane(mainPanel);

        // 提交按钮事件
        submitButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                submitPasswordChange();
            }
        });

        // 返回按钮事件
        backButton.addActionListener(new ActionListener() {
            @Override
            public void actionPerformed(ActionEvent e) {
                returnToLogin();
            }
        });
    }

    // 创建输入面板
    private JPanel createInputPanel(String labelText, boolean isUsername) {
        JPanel panel = new JPanel(new FlowLayout(FlowLayout.LEFT, 10, 0));
        panel.setBackground(Color.WHITE);

        JLabel label = new JLabel(labelText);
        label.setFont(Main.FONT_BOLD);
        label.setPreferredSize(new Dimension(80, 30));
        panel.add(label);

        JComponent inputComponent;
        if (isUsername) {
            usernameField = new JTextField(20);
            inputComponent = usernameField;
        } else if (labelText.equals("新密码：")) {
            newPasswordField = new JPasswordField(20);
            inputComponent = newPasswordField;
        } else {
            confirmPasswordField = new JPasswordField(20);
            inputComponent = confirmPasswordField;
        }

        inputComponent.setPreferredSize(new Dimension(220, 35));
        inputComponent.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createLineBorder(Color.LIGHT_GRAY, 1),
                new EmptyBorder(5, 10, 5, 10)
        ));

        panel.add(inputComponent);
        return panel;
    }

    // 美化按钮
    private void styleButton(JButton button, Color bgColor, Color fgColor) {
        button.setPreferredSize(new Dimension(100, 35));
        button.setFont(Main.FONT_BOLD);
        button.setBackground(bgColor);
        button.setForeground(fgColor);
        button.setBorder(BorderFactory.createEmptyBorder());
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor.darker());
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor);
            }
        });
    }

    // 提交密码修改
    private void submitPasswordChange() {
        String username = usernameField.getText().trim();
        String newPassword = new String(newPasswordField.getPassword()).trim();
        String confirmPassword = new String(confirmPasswordField.getPassword()).trim();

        // 输入验证
        if (username.isEmpty()) {
            JOptionPane.showMessageDialog(this, "请输入学号/工号！", "提示", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (newPassword.isEmpty()) {
            JOptionPane.showMessageDialog(this, "请输入新密码！", "提示", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (confirmPassword.isEmpty()) {
            JOptionPane.showMessageDialog(this, "请确认新密码！", "提示", JOptionPane.WARNING_MESSAGE);
            return;
        }
        if (!newPassword.equals(confirmPassword)) {
            JOptionPane.showMessageDialog(this, "两次输入的密码不一致！", "错误", JOptionPane.ERROR_MESSAGE);
            return;
        }
        if (newPassword.length() < 6) {
            JOptionPane.showMessageDialog(this, "密码长度不能少于6位！", "提示", JOptionPane.WARNING_MESSAGE);
            return;
        }

        // 数据库修改密码
        boolean isUpdateSuccess = false;
        try (Connection conn = Main.getDBConnection()) {
            // 1. 先尝试更新学生表
            String studentSql = "UPDATE students SET password = ? WHERE id = ?";
            try (PreparedStatement pstmt = conn.prepareStatement(studentSql)) {
                pstmt.setString(1, newPassword);
                pstmt.setString(2, username);
                int affectedRows = pstmt.executeUpdate();
                if (affectedRows > 0) {
                    isUpdateSuccess = true;
                }
            }

            // 2. 学生表没找到，尝试更新教师表
            if (!isUpdateSuccess) {
                String teacherSql = "UPDATE teachers SET password = ? WHERE id = ?";
                try (PreparedStatement pstmt = conn.prepareStatement(teacherSql)) {
                    pstmt.setString(1, newPassword);
                    pstmt.setString(2, username);
                    int affectedRows = pstmt.executeUpdate();
                    if (affectedRows > 0) {
                        isUpdateSuccess = true;
                    }
                }
            }
        } catch (SQLException ex) {
            JOptionPane.showMessageDialog(this, "密码修改失败：" + ex.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            ex.printStackTrace();
            return;
        }

        // 修改结果
        if (isUpdateSuccess) {
            JOptionPane.showMessageDialog(this, "密码修改成功！", "成功", JOptionPane.INFORMATION_MESSAGE);
            returnToLogin();
        } else {
            JOptionPane.showMessageDialog(this, "学号/工号不存在！", "错误", JOptionPane.ERROR_MESSAGE);
        }
    }

    // 返回登录界面
    private void returnToLogin() {
        this.dispose();
        loginFrame.returnToLogin();
    }
}

// 学生选课系统界面类 - 优化版
class CourseSelectionMySQLUI extends JFrame {
    // 改为使用动态获取的登录学生ID
    private final long CURRENT_STUDENT_ID = Main.getCurrentStudentId();
    private final CourseDAO courseDAO = new CourseDAO();
    private final EnrollmentDAO enrollmentDAO = new EnrollmentDAO();
    private final DefaultTableModel allModel;
    private final JTable allTable;
    private final TableRowSorter<DefaultTableModel> sorter;
    private final DefaultTableModel selModel;
    private final JTable selTable;
    private final JComboBox<String> categoryBox;
    private final JCheckBox onlyNotFullBox;
    private final JLabel creditLabel;
    private final JLabel statusLabel;

    public CourseSelectionMySQLUI() {
        super("课程选择 - 广西师范大学教务处网上选课系统");
        this.setDefaultCloseOperation(EXIT_ON_CLOSE);
        this.setSize(1100, 700);
        this.setLocationRelativeTo((Component)null);
        this.setMinimumSize(new Dimension(900, 600));

        // 主面板
        JPanel root = new JPanel(new BorderLayout());
        root.setBackground(Main.SECONDARY_COLOR);

        // 顶部面板 - 优化布局和样式
        JPanel top = new JPanel(new BorderLayout());
        top.setBackground(Color.WHITE);
        top.setBorder(new EmptyBorder(15, 20, 15, 20));

        // 左侧筛选面板
        JPanel filterPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 0));
        filterPanel.setBackground(Color.WHITE);
        filterPanel.add(new JLabel("课程分类："));

        // 美化下拉框
        this.categoryBox = new JComboBox(new String[]{"全部"});
        styleComboBox(categoryBox);
        filterPanel.add(this.categoryBox);

        this.onlyNotFullBox = new JCheckBox("只显示未选满课程");
        this.onlyNotFullBox.setBackground(Color.WHITE);
        filterPanel.add(this.onlyNotFullBox);

        // 右侧信息面板
        JPanel infoPanel = new JPanel(new FlowLayout(FlowLayout.RIGHT, 20, 0));
        infoPanel.setBackground(Color.WHITE);

        // 美化信息标签
        this.creditLabel = new JLabel("总学分：0");
        styleInfoLabel(creditLabel);
        infoPanel.add(this.creditLabel);

        this.statusLabel = new JLabel("已选课程：0 门");
        styleInfoLabel(statusLabel);
        infoPanel.add(this.statusLabel);

        top.add(filterPanel, BorderLayout.WEST);
        top.add(infoPanel, BorderLayout.EAST);

        // 表格面板
        String[] allCols = new String[]{"课程编号", "课程名称", "上课时间", "任课老师", "课程容量", "已选人数", "课程分类", "学分"};
        this.allModel = new DefaultTableModel(allCols, 0) {
            public boolean isCellEditable(int r, int c) {
                return false;
            }
        };
        this.allTable = createStyledTable(this.allModel);
        this.sorter = new TableRowSorter(this.allModel);
        this.allTable.setRowSorter(this.sorter);

        JScrollPane allScroll = createStyledScrollPane(this.allTable, "可选课程");

        String[] selCols = new String[]{"课程编号", "课程名称", "上课时间", "任课老师", "课程分类", "学分"};
        this.selModel = new DefaultTableModel(selCols, 0) {
            public boolean isCellEditable(int r, int c) {
                return false;
            }
        };
        this.selTable = createStyledTable(this.selModel);

        JScrollPane selScroll = createStyledScrollPane(this.selTable, "已选课程");

        JSplitPane split = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, allScroll, selScroll);
        split.setResizeWeight(0.6);
        split.setDividerLocation(600);
        split.setDividerSize(8);
        split.setBackground(Main.SECONDARY_COLOR);

        // 底部按钮面板
        JPanel bottom = new JPanel(new FlowLayout(FlowLayout.RIGHT, 15, 10));
        bottom.setBackground(Main.SECONDARY_COLOR);

        JButton refreshBtn = new JButton("刷新");
        JButton selectBtn = new JButton("选课");
        JButton dropBtn = new JButton("退课");
        JButton creditStatsBtn = new JButton("学分统计");

        // 美化按钮
        styleActionButton(refreshBtn, Main.PRIMARY_COLOR);
        styleActionButton(selectBtn, Main.SUCCESS_COLOR);
        styleActionButton(dropBtn, Main.ERROR_COLOR);
        styleActionButton(creditStatsBtn, Main.ACCENT_COLOR);

        bottom.add(refreshBtn);
        bottom.add(selectBtn);
        bottom.add(dropBtn);
        bottom.add(creditStatsBtn);

        // 组装主面板
        root.add(top, BorderLayout.NORTH);
        root.add(split, BorderLayout.CENTER);
        root.add(bottom, BorderLayout.SOUTH);
        this.setContentPane(root);

        // 事件监听
        creditStatsBtn.addActionListener((e) -> {
            // 打开学分统计窗口，传递当前登录学生ID
            SwingUtilities.invokeLater(() -> {
                new CreditStatisticsFrame(String.valueOf(CURRENT_STUDENT_ID)).setVisible(true);
            });
        });

        refreshBtn.addActionListener((e) -> this.reloadAll());
        this.categoryBox.addActionListener((e) -> this.reloadAll());
        this.onlyNotFullBox.addActionListener((e) -> this.reloadAll());
        selectBtn.addActionListener((e) -> this.enrollSelected());
        dropBtn.addActionListener((e) -> this.dropSelected());

        this.reloadCategoriesThenData();
    }

    // 创建美化的表格
    private JTable createStyledTable(DefaultTableModel model) {
        JTable table = new JTable(model);
        table.setRowHeight(30);
        table.setSelectionMode(ListSelectionModel.SINGLE_SELECTION);
        table.getTableHeader().setReorderingAllowed(false);
        table.getTableHeader().setBackground(Color.WHITE);
        table.getTableHeader().setForeground(Color.DARK_GRAY);
        table.getTableHeader().setFont(Main.FONT_BOLD);
        table.getTableHeader().setPreferredSize(new Dimension(table.getTableHeader().getWidth(), 35));

        // 设置表格选中行样式
        table.setSelectionBackground(new Color(204, 229, 255));
        table.setSelectionForeground(Color.BLACK);

        // 单元格居中对齐
        DefaultTableCellRenderer centerRenderer = new DefaultTableCellRenderer();
        centerRenderer.setHorizontalAlignment(JLabel.CENTER);
        for (int i = 0; i < table.getColumnCount(); i++) {
            table.getColumnModel().getColumn(i).setCellRenderer(centerRenderer);
        }

        return table;
    }

    // 创建美化的滚动面板
    private JScrollPane createStyledScrollPane(JTable table, String title) {
        JScrollPane scroll = new JScrollPane(table);
        scroll.setBorder(BorderFactory.createCompoundBorder(
                BorderFactory.createTitledBorder(
                        BorderFactory.createLineBorder(Color.LIGHT_GRAY),
                        title,
                        0,
                        0,
                        Main.FONT_BOLD,
                        Main.PRIMARY_COLOR
                ),
                new EmptyBorder(5, 5, 5, 5)
        ));
        scroll.setBackground(Color.WHITE);
        return scroll;
    }

    // 美化下拉框
    private void styleComboBox(JComboBox<?> comboBox) {
        comboBox.setPreferredSize(new Dimension(150, 30));
        comboBox.setBackground(Color.WHITE);
        comboBox.setBorder(BorderFactory.createLineBorder(Color.LIGHT_GRAY));
    }

    // 美化信息标签
    private void styleInfoLabel(JLabel label) {
        label.setFont(Main.FONT_BOLD);
        label.setForeground(Main.PRIMARY_COLOR);
        label.setBorder(new EmptyBorder(5, 10, 5, 10));
    }

    // 美化操作按钮
    private void styleActionButton(JButton button, Color bgColor) {
        button.setPreferredSize(new Dimension(100, 35));
        button.setFont(Main.FONT_BOLD);
        button.setBackground(bgColor);
        button.setForeground(Color.DARK_GRAY);
        button.setBorder(BorderFactory.createEmptyBorder());
        button.setCursor(new Cursor(Cursor.HAND_CURSOR));

        // 悬停效果
        button.addMouseListener(new java.awt.event.MouseAdapter() {
            public void mouseEntered(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor.darker());
            }
            public void mouseExited(java.awt.event.MouseEvent evt) {
                button.setBackground(bgColor);
            }
        });
    }

    // 学分统计窗口类（优化UI）
    class CreditStatisticsFrame extends JFrame {
        private String studentId;
        private JTable statsTable;
        private DefaultTableModel tableModel;
        private JLabel totalCreditsLabel;
        private JLabel requiredCreditsLabel;
        private JLabel electiveCreditsLabel;
        private JLabel practicalCreditsLabel;
        private JProgressBar totalProgressBar;
        private JComboBox<String> semesterComboBox;

        public CreditStatisticsFrame(String studentId) {
            this.studentId = studentId;
            initializeUI();
            loadCreditStats();
            loadSemesterData();
        }

        private void initializeUI() {
            setTitle("学分统计分析 - 学号：" + studentId);
            setSize(1000, 700);
            setLocationRelativeTo(null);
            setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
            setLayout(new BorderLayout(10, 10));
            getContentPane().setBackground(Main.SECONDARY_COLOR);

            // 顶部面板
            JPanel topPanel = createTopPanel();
            add(topPanel, BorderLayout.NORTH);

            // 统计面板
            JPanel statsPanel = createStatsPanel();
            add(statsPanel, BorderLayout.CENTER);

            // 底部面板
            JPanel bottomPanel = createBottomPanel();
            add(bottomPanel, BorderLayout.SOUTH);
        }

        private JPanel createTopPanel() {
            JPanel panel = new JPanel(new BorderLayout());
            panel.setBackground(Color.WHITE);
            panel.setBorder(new EmptyBorder(20, 20, 20, 20));

            // 标题
            JLabel titleLabel = new JLabel("学分统计分析", SwingConstants.CENTER);
            titleLabel.setFont(Main.FONT_HEADING);
            titleLabel.setForeground(Main.PRIMARY_COLOR);
            panel.add(titleLabel, BorderLayout.NORTH);

            // 学生信息和筛选面板
            JPanel infoPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
            infoPanel.setBackground(Color.WHITE);

            JLabel studentInfoLabel = new JLabel("学号：" + studentId + " | 当前学期统计");
            studentInfoLabel.setFont(Main.FONT_BOLD);
            studentInfoLabel.setForeground(Color.DARK_GRAY);

            JLabel semesterLabel = new JLabel("选择学期：");
            semesterLabel.setFont(Main.FONT_MAIN);

            semesterComboBox = new JComboBox<>(new String[]{"全部学期", "2024-2025-1", "2024-2025-2", "2023-2024-1", "2023-2024-2"});
            styleComboBox(semesterComboBox);
            semesterComboBox.addActionListener(new SemesterFilterListener());

            infoPanel.add(studentInfoLabel);
            infoPanel.add(Box.createHorizontalStrut(50));
            infoPanel.add(semesterLabel);
            infoPanel.add(semesterComboBox);

            panel.add(infoPanel, BorderLayout.CENTER);

            return panel;
        }

        private JPanel createStatsPanel() {
            JPanel panel = new JPanel(new GridLayout(2, 1, 10, 10));
            panel.setBorder(new EmptyBorder(0, 20, 20, 20));
            panel.setBackground(Main.SECONDARY_COLOR);

            // 学分类型统计表格
            JPanel tablePanel = new JPanel(new BorderLayout());
            tablePanel.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createTitledBorder(
                            BorderFactory.createLineBorder(Color.LIGHT_GRAY),
                            "学分类型详细统计",
                            0,
                            0,
                            Main.FONT_BOLD,
                            Main.PRIMARY_COLOR
                    ),
                    new EmptyBorder(10, 10, 10, 10)
            ));
            tablePanel.setBackground(Color.WHITE);

            String[] columnNames = {"学分类型", "已修学分", "要求学分", "完成进度(%)"};
            tableModel = new DefaultTableModel(columnNames, 0) {
                @Override
                public boolean isCellEditable(int row, int column) {
                    return false;
                }

                @Override
                public Class<?> getColumnClass(int columnIndex) {
                    if (columnIndex == 3) return Double.class;
                    return String.class;
                }
            };

            statsTable = createStyledTable(tableModel);
            JScrollPane scrollPane = new JScrollPane(statsTable);
            scrollPane.setBorder(BorderFactory.createEmptyBorder());
            tablePanel.add(scrollPane, BorderLayout.CENTER);

            // 统计卡片面板
            JPanel cardsPanel = createStatsCardsPanel();

            panel.add(tablePanel);
            panel.add(cardsPanel);

            return panel;
        }

        private JPanel createStatsCardsPanel() {
            JPanel panel = new JPanel(new GridLayout(1, 4, 15, 10));
            panel.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createTitledBorder(
                            BorderFactory.createLineBorder(Color.LIGHT_GRAY),
                            "学分统计概览",
                            0,
                            0,
                            Main.FONT_BOLD,
                            Main.PRIMARY_COLOR
                    ),
                    new EmptyBorder(10, 10, 10, 10)
            ));
            panel.setBackground(Color.WHITE);

            // 总学分统计
            JPanel totalPanel = createStatCard("总学分", "0", "毕业要求: 160学分", Main.PRIMARY_COLOR);
            totalCreditsLabel = (JLabel) ((JPanel) totalPanel.getComponent(1)).getComponent(0);

            // 必修课学分
            JPanel requiredPanel = createStatCard("必修课学分", "0", "要求: 120学分", Main.SUCCESS_COLOR);
            requiredCreditsLabel = (JLabel) ((JPanel) requiredPanel.getComponent(1)).getComponent(0);

            // 选修课学分
            JPanel electivePanel = createStatCard("选修课学分", "0", "要求: 30学分", Main.ACCENT_COLOR);
            electiveCreditsLabel = (JLabel) ((JPanel) electivePanel.getComponent(1)).getComponent(0);

            // 实践环节学分
            JPanel practicalPanel = createStatCard("实践环节学分", "0", "要求: 10学分", Main.ERROR_COLOR);
            practicalCreditsLabel = (JLabel) ((JPanel) practicalPanel.getComponent(1)).getComponent(0);

            panel.add(totalPanel);
            panel.add(requiredPanel);
            panel.add(electivePanel);
            panel.add(practicalPanel);

            return panel;
        }

        private JPanel createStatCard(String title, String value, String requirement, Color color) {
            JPanel card = new JPanel(new BorderLayout());
            card.setBackground(Color.WHITE);
            card.setBorder(BorderFactory.createCompoundBorder(
                    BorderFactory.createLineBorder(color, 2),
                    new EmptyBorder(15, 15, 15, 15)
            ));

            JLabel titleLabel = new JLabel(title, SwingConstants.CENTER);
            titleLabel.setFont(Main.FONT_BOLD);
            titleLabel.setForeground(color);
            card.add(titleLabel, BorderLayout.NORTH);

            JPanel valuePanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
            valuePanel.setBackground(Color.WHITE);
            JLabel valueLabel = new JLabel(value);
            valueLabel.setFont(new Font("微软雅黑", Font.BOLD, 24));
            valueLabel.setForeground(color);
            valuePanel.add(valueLabel);

            card.add(valuePanel, BorderLayout.CENTER);

            JLabel reqLabel = new JLabel(requirement, SwingConstants.CENTER);
            reqLabel.setFont(Main.FONT_MAIN.deriveFont(12f));
            reqLabel.setForeground(Color.GRAY);
            card.add(reqLabel, BorderLayout.SOUTH);

            return card;
        }

        private JPanel createBottomPanel() {
            JPanel panel = new JPanel(new BorderLayout());
            panel.setBorder(new EmptyBorder(10, 20, 20, 20));
            panel.setBackground(Main.SECONDARY_COLOR);

            // 进度条面板
            JPanel progressPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
            progressPanel.setBackground(Main.SECONDARY_COLOR);

            JLabel progressLabel = new JLabel("总体完成进度：");
            progressLabel.setFont(Main.FONT_BOLD);

            totalProgressBar = new JProgressBar(0, 100);
            totalProgressBar.setPreferredSize(new Dimension(300, 30));
            totalProgressBar.setStringPainted(true);
            totalProgressBar.setFont(Main.FONT_MAIN);
            totalProgressBar.setForeground(Main.PRIMARY_COLOR);

            progressPanel.add(progressLabel);
            progressPanel.add(totalProgressBar);

            // 按钮面板
            JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
            buttonPanel.setBackground(Main.SECONDARY_COLOR);

            JButton exportButton = new JButton("导出统计报告");
            JButton closeButton = new JButton("关闭窗口");

            styleActionButton(exportButton, Color.LIGHT_GRAY);
            exportButton.setForeground(Color.DARK_GRAY); // 绿色背景→白色文字
            styleActionButton(closeButton, Color.LIGHT_GRAY);
            closeButton.setForeground(Color.DARK_GRAY); // 浅灰背景→深灰文字

            exportButton.addActionListener(e -> exportStatistics());
            closeButton.addActionListener(e -> dispose());

            buttonPanel.add(exportButton);
            buttonPanel.add(closeButton);

            panel.add(progressPanel, BorderLayout.CENTER);
            panel.add(buttonPanel, BorderLayout.SOUTH);

            return panel;
        }

        // 修复：适配数据库字段+分类匹配+空值处理
        private void loadCreditStats() {
            Connection conn = null;
            PreparedStatement pstmt = null;
            ResultSet rs = null;

            try {
                conn = Main.getDBConnection();
                if (conn == null) return;

                // 关键修复1：匹配数据库中真实的课程分类（必修课/选修课/实践环节）
                String sql = "SELECT " +
                        "c.category as course_type, " +
                        "SUM(IFNULL(c.credits, 0)) as earned_credits, " + // 处理NULL值
                        "CASE " +
                        "    WHEN c.category = '必修课' THEN 120 " +
                        "    WHEN c.category = '选修课' THEN 30 " +
                        "    WHEN c.category = '实践环节' THEN 10 " +
                        "    ELSE 0 " +
                        "END as required_credits " +
                        "FROM enrollment sc " +
                        "JOIN courses c ON sc.course_id = c.id " +
                        "WHERE sc.student_id = ? " +
                        "GROUP BY c.category";

                pstmt = conn.prepareStatement(sql);
                // 关键修复2：统一数据类型（studentId是String，避免long转String的问题）
                pstmt.setString(1, this.studentId);
                rs = pstmt.executeQuery();

                int totalEarnedCredits = 0;
                int totalRequiredCredits = 160;
                int requiredCredits = 0;    // 必修课已修
                int electiveCredits = 0;    // 选修课已修
                int practicalCredits = 0;   // 实践环节已修

                tableModel.setRowCount(0);

                while (rs.next()) {
                    String courseType = rs.getString("course_type");
                    // 关键修复3：用getInt时指定默认值，避免NULL报错
                    int earnedCredits = rs.getInt("earned_credits");
                    int required = rs.getInt("required_credits");
                    double progress = required == 0 ? 0 : (double) earnedCredits / required * 100;

                    Vector<Object> row = new Vector<>();
                    row.add(courseType);
                    row.add(earnedCredits);
                    row.add(required);
                    row.add(Math.round(progress * 100.0) / 100.0);
                    tableModel.addRow(row);

                    totalEarnedCredits += earnedCredits;

                    // 关键修复4：匹配数据库中的分类名称
                    switch (courseType) {
                        case "必修课":
                            requiredCredits = earnedCredits;
                            break;
                        case "选修课":
                            electiveCredits = earnedCredits;
                            break;
                        case "实践环节":
                            practicalCredits = earnedCredits;
                            break;
                    }
                }

                // 更新概览卡片
                updateStatsLabels(totalEarnedCredits, requiredCredits, electiveCredits, practicalCredits);

                // 更新进度条
                int overallProgress = totalRequiredCredits == 0 ? 0 : (int) ((double) totalEarnedCredits / totalRequiredCredits * 100);
                totalProgressBar.setValue(overallProgress);
                totalProgressBar.setString(overallProgress + "%");

                if (overallProgress >= 80) {
                    totalProgressBar.setForeground(Main.SUCCESS_COLOR);
                } else if (overallProgress >= 60) {
                    totalProgressBar.setForeground(Main.ACCENT_COLOR);
                } else {
                    totalProgressBar.setForeground(Main.ERROR_COLOR);
                }

                if (tableModel.getRowCount() == 0) {
                    JOptionPane.showMessageDialog(this,
                            "没有找到学号为 " + studentId + " 的选课记录！",
                            "提示", JOptionPane.INFORMATION_MESSAGE);
                }

            } catch (SQLException e) {
                e.printStackTrace();
                JOptionPane.showMessageDialog(this,
                        "统计查询失败！\n" + e.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            } finally {
                try {
                    if (rs != null) rs.close();
                    if (pstmt != null) pstmt.close();
                    if (conn != null) conn.close();
                } catch (SQLException e) {
                    e.printStackTrace();
                }
            }
        }

        private void updateStatsLabels(int total, int required, int elective, int practical) {
            totalCreditsLabel.setText(String.valueOf(total));
            requiredCreditsLabel.setText(required + "/120");
            electiveCreditsLabel.setText(elective + "/30");
            practicalCreditsLabel.setText(practical + "/10");
        }

        private void loadSemesterData() {
            // 若需要按学期筛选，可在enrollment表中添加semester字段后扩展
        }

        private void exportStatistics() {
            JFileChooser fileChooser = new JFileChooser();
            fileChooser.setDialogTitle("导出统计报告");
            fileChooser.setSelectedFile(new File("学分统计报告_" + studentId + ".txt")); // 简化：导出为txt

            int userSelection = fileChooser.showSaveDialog(this);
            if (userSelection == JFileChooser.APPROVE_OPTION) {
                File fileToSave = fileChooser.getSelectedFile();
                JOptionPane.showMessageDialog(this,
                        "统计报告已导出到: " + fileToSave.getAbsolutePath(),
                        "导出成功", JOptionPane.INFORMATION_MESSAGE);
            }
        }

        private class SemesterFilterListener implements ActionListener {
            @Override
            public void actionPerformed(ActionEvent e) {
                String selectedSemester = (String) semesterComboBox.getSelectedItem();
                // 暂不实现学期筛选，仅刷新数据
                loadCreditStats();
            }
        }
    }

    private void reloadCategoriesThenData() {
        (new SwingWorker<Void, Void>() {
            List<String> cats;

            protected Void doInBackground() throws Exception {
                this.cats = CourseSelectionMySQLUI.this.courseDAO.listCategories();
                return null;
            }

            protected void done() {
                try {
                    this.get();
                } catch (Exception ex) {
                    CourseSelectionMySQLUI.this.showErr("加载分类失败：" + ex.getMessage());
                    return;
                }

                CourseSelectionMySQLUI.this.categoryBox.removeAllItems();
                CourseSelectionMySQLUI.this.categoryBox.addItem("全部");

                for(String c : this.cats) {
                    CourseSelectionMySQLUI.this.categoryBox.addItem(c);
                }

                CourseSelectionMySQLUI.this.reloadAll();
            }
        }).execute();
    }

    private void reloadAll() {
        String tempCategory = (String)this.categoryBox.getSelectedItem();
        final boolean tempOnlyNotFull = this.onlyNotFullBox.isSelected();
        final String finalCategory = tempCategory == null ? "全部" : tempCategory;
        (new SwingWorker<Void, Void>() {
            List<CourseRow> all;
            List<CourseRow> selected;
            int totalCredits;

            protected Void doInBackground() throws Exception {
                this.all = CourseSelectionMySQLUI.this.courseDAO.listCourses(finalCategory, tempOnlyNotFull);
                this.selected = CourseSelectionMySQLUI.this.enrollmentDAO.listSelected(CURRENT_STUDENT_ID);
                this.totalCredits = CourseSelectionMySQLUI.this.enrollmentDAO.sumCredits(CURRENT_STUDENT_ID);
                return null;
            }

            protected void done() {
                try {
                    this.get();
                } catch (Exception ex) {
                    CourseSelectionMySQLUI.this.showErr("加载数据失败：" + ex.getMessage());
                    return;
                }

                CourseSelectionMySQLUI.this.allModel.setRowCount(0);

                for(CourseRow c : this.all) {
                    CourseSelectionMySQLUI.this.allModel.addRow(new Object[]{c.id, c.name, c.timeText, c.teacher, c.capacity, c.enrolled, c.category, c.credits});
                }

                CourseSelectionMySQLUI.this.selModel.setRowCount(0);

                for(CourseRow c : this.selected) {
                    CourseSelectionMySQLUI.this.selModel.addRow(new Object[]{c.id, c.name, c.timeText, c.teacher, c.category, c.credits});
                }

                CourseSelectionMySQLUI.this.creditLabel.setText("总学分：" + this.totalCredits);
                CourseSelectionMySQLUI.this.statusLabel.setText("已选课程：" + this.selected.size() + " 门");
            }
        }).execute();
    }

    private void enrollSelected() {
        int viewRow = this.allTable.getSelectedRow();
        if (viewRow < 0) {
            JOptionPane.showMessageDialog(this, "请先在可选课程表中选中一门课。", "提示", JOptionPane.INFORMATION_MESSAGE);
        } else {
            int modelRow = this.allTable.convertRowIndexToModel(viewRow);
            final String courseId = String.valueOf(this.allModel.getValueAt(modelRow, 0));
            (new SwingWorker<Void, Void>() {
                protected Void doInBackground() throws Exception {
                    CourseSelectionMySQLUI.this.enrollmentDAO.enroll(CURRENT_STUDENT_ID, courseId);
                    return null;
                }

                protected void done() {
                    try {
                        this.get();
                        CourseSelectionMySQLUI.this.reloadAll();
                    } catch (Exception ex) {
                        String msg = ex.getCause() != null ? ex.getCause().getMessage() : ex.getMessage();
                        CourseSelectionMySQLUI.this.handleEnrollError(msg);
                    }

                }
            }).execute();
        }
    }

    private void dropSelected() {
        int row = this.selTable.getSelectedRow();
        if (row < 0) {
            JOptionPane.showMessageDialog(this, "请先在已选课程表中选中要退课的课程。", "提示", JOptionPane.INFORMATION_MESSAGE);
        } else {
            final String courseId = String.valueOf(this.selModel.getValueAt(row, 0));
            (new SwingWorker<Void, Void>() {
                protected Void doInBackground() throws Exception {
                    CourseSelectionMySQLUI.this.enrollmentDAO.drop(CURRENT_STUDENT_ID, courseId);
                    return null;
                }

                protected void done() {
                    try {
                        this.get();
                        CourseSelectionMySQLUI.this.reloadAll();
                    } catch (Exception ex) {
                        CourseSelectionMySQLUI.this.showErr("退课失败：" + ex.getMessage());
                    }

                }
            }).execute();
        }
    }

    private void handleEnrollError(String code) {
        String text;
        switch (code) {
            case "FULL" -> text = "该课程已选满，无法选课。";
            case "CONFLICT" -> text = "该课程与已选课程时间冲突，无法选课。";
            case "DUPLICATE" -> text = "你已选过该课程。";
            case "NOT_FOUND" -> text = "课程不存在。";
            default -> text = "选课失败：" + code;
        }
        JOptionPane.showMessageDialog(this, text, "选课失败", JOptionPane.ERROR_MESSAGE);
    }

    private void showErr(String text) {
        JOptionPane.showMessageDialog(this, text, "错误", JOptionPane.ERROR_MESSAGE);
    }

    // 数据库连接复用Main类的配置
    static class DB {
        private static final String URL = Main.DB_URL;
        private static final String USER = Main.DB_USER;
        private static final String PASS = Main.DB_PASSWORD;

        static Connection getConn() throws SQLException {
            return DriverManager.getConnection(URL, USER, PASS);
        }
    }

    static class CourseRow {
        String id;
        String name;
        String timeText;
        String teacher;
        String category;
        int capacity;
        int enrolled;
        int credits;
        int dayOfWeek;
        int startMin;
        int endMin;

        CourseRow(String id, String name, String timeText, String teacher, String category, int capacity, int enrolled, int credit, int dayOfWeek, int startMin, int endMin) {
            this.id = id;
            this.name = name;
            this.timeText = timeText;
            this.teacher = teacher;
            this.category = category;
            this.capacity = capacity;
            this.enrolled = enrolled;
            this.credits = credit;
            this.dayOfWeek = dayOfWeek;
            this.startMin = startMin;
            this.endMin = endMin;
        }
    }

    // 适配courses、teachers表的字段
    static class CourseDAO {
        List<String> listCategories() throws SQLException {
            String sql = "SELECT DISTINCT category FROM courses ORDER BY category";

            try (Connection conn = DB.getConn();
                 PreparedStatement ps = conn.prepareStatement(sql);
                 ResultSet rs = ps.executeQuery()) {
                List<String> cats = new ArrayList<>();
                while (rs.next()) {
                    cats.add(rs.getString(1));
                }
                return cats;
            }
        }

        List<CourseRow> listCourses(String category, boolean onlyNotFull) throws SQLException {
            String sql = "SELECT c.id, c.course_name AS name, t.name AS teacher, " +
                    "c.category, c.capacity, COALESCE(e.cnt,0) AS enrolled, " +
                    "c.credits AS credit, 1 AS day_of_week, 480 AS start_min, 600 AS end_min, " +
                    "c.class_time " +
                    "FROM courses c "+
                    "LEFT JOIN teachers t ON c.teacher_id = t.id " +
                    "LEFT JOIN (SELECT course_id, COUNT(*) cnt FROM enrollment GROUP BY course_id) e ON e.course_id=c.id " +
                    "WHERE (?='全部' OR c.category=?) " +
                    (onlyNotFull ? "AND COALESCE(e.cnt,0) < c.capacity " : "") +
                    "ORDER BY c.id";

            try (Connection conn = DB.getConn();
                 PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setString(1, category);
                ps.setString(2, category);
                List<CourseRow> list = new ArrayList<>();
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) {
                        String timeText = rs.getString("class_time");
                        list.add(new CourseRow(
                                rs.getString("id"),
                                rs.getString("name"),
                                timeText,
                                rs.getString("teacher"),
                                rs.getString("category"),
                                rs.getInt("capacity"),
                                rs.getInt("enrolled"),
                                rs.getInt("credit"), // 这里用credit是因为别名，和数据库credits对应
                                rs.getInt("day_of_week"),
                                rs.getInt("start_min"),
                                rs.getInt("end_min")
                        ));
                    }
                }
                return list;
            }
        }

        private static String toHM(int min) {
            int h = min / 60;
            int m = min % 60;
            return String.format("%02d:%02d", h, m);
        }

        private static String dowToCN(int dow) {
            return switch (dow) {
                case 1 -> "一";
                case 2 -> "二";
                case 3 -> "三";
                case 4 -> "四";
                case 5 -> "五";
                case 6 -> "六";
                case 7 -> "日";
                default -> "?";
            };
        }
    }

    // 适配enrollment、courses表的字段
    static class EnrollmentDAO {
        List<CourseRow> listSelected(long studentId) throws SQLException {
            String sql = "SELECT c.id, c.course_name AS name, t.name AS teacher, " +
                    "c.category, c.capacity, c.credits AS credit, " +  // 替换为credits
                    "1 AS day_of_week, 480 AS start_min, 600 AS end_min, " +
                    "c.class_time " +
                    "FROM enrollment e "+
                    "JOIN courses c ON c.id=e.course_id " +
                    "JOIN teachers t ON c.teacher_id = t.id " +
                    "WHERE e.student_id=? " +
                    "ORDER BY c.class_time";

            try (Connection conn = DB.getConn();
                 PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setLong(1, studentId);
                List<CourseRow> list = new ArrayList<>();
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) {
                        String timeText = rs.getString("class_time");
                        list.add(new CourseRow(
                                rs.getString("id"),
                                rs.getString("name"),
                                timeText,
                                rs.getString("teacher"),
                                rs.getString("category"),
                                rs.getInt("capacity"),
                                -1,
                                rs.getInt("credit"),
                                rs.getInt("day_of_week"),
                                rs.getInt("start_min"),
                                rs.getInt("end_min")
                        ));
                    }
                }
                return list;
            }
        }

        int sumCredits(long studentId) throws SQLException {
            String sql = "SELECT COALESCE(SUM(c.credits), 0) total " +
                    "FROM enrollment e JOIN courses c ON c.id=e.course_id " +
                    "WHERE e.student_id=?";

            try (Connection conn = DB.getConn();
                 PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setLong(1, studentId);
                try (ResultSet rs = ps.executeQuery()) {
                    rs.next();
                    return rs.getInt(1);
                }
            }
        }

        void enroll(long studentId, String courseId) throws SQLException {
            try (Connection conn = DB.getConn()) {
                conn.setAutoCommit(false);
                try {
                    String checkCourseSql = "SELECT capacity, (SELECT COUNT(*) FROM enrollment WHERE course_id=?) enrolled FROM courses WHERE id=? FOR UPDATE";
                    try (PreparedStatement ps = conn.prepareStatement(checkCourseSql)) {
                        ps.setString(1, courseId);
                        ps.setString(2, courseId);
                        try (ResultSet rs = ps.executeQuery()) {
                            if (!rs.next()) {
                                throw new SQLException("NOT_FOUND");
                            }
                            int capacity = rs.getInt("capacity");
                            int enrolled = rs.getInt("enrolled");
                            if (enrolled >= capacity) {
                                throw new SQLException("FULL");
                            }
                        }
                    }

                    String checkConflictSql = "SELECT 1 FROM enrollment en JOIN courses c1 ON c1.id=en.course_id JOIN courses c2 ON c2.id=? " +
                            "WHERE en.student_id=? AND c1.class_time = c2.class_time LIMIT 1";
                    try (PreparedStatement ps = conn.prepareStatement(checkConflictSql)) {
                        ps.setString(1, courseId);
                        ps.setLong(2, studentId);
                        try (ResultSet rs = ps.executeQuery()) {
                            if (rs.next()) {
                                throw new SQLException("CONFLICT");
                            }
                        }
                    }

                    String insertSql = "INSERT INTO enrollment(student_id,course_id) VALUES (?,?)";
                    try (PreparedStatement ps = conn.prepareStatement(insertSql)) {
                        ps.setLong(1, studentId);
                        ps.setString(2, courseId);
                        ps.executeUpdate();
                    }

                    conn.commit();
                } catch (SQLException ex) {
                    conn.rollback();
                    if ("23000".equals(ex.getSQLState())) {
                        throw new SQLException("DUPLICATE");
                    }
                    throw ex;
                } finally {
                    conn.setAutoCommit(true);
                }
            }
        }

        void drop(long studentId, String courseId) throws SQLException {
            String sql = "DELETE FROM enrollment WHERE student_id=? AND course_id=?";
            try (Connection conn = DB.getConn();
                 PreparedStatement ps = conn.prepareStatement(sql)) {
                ps.setLong(1, studentId);
                ps.setString(2, courseId);
                ps.executeUpdate();
            }
        }

        private static String toHM(int min) {
            int h = min / 60;
            int m = min % 60;
            return String.format("%02d:%02d", h, m);
        }

        private static String dowToCN(int dow) {
            return switch (dow) {
                case 1 -> "一";
                case 2 -> "二";
                case 3 -> "三";
                case 4 -> "四";
                case 5 -> "五";
                case 6 -> "六";
                case 7 -> "日";
                default -> "?";
            };
        }
    }
}

// 教师管理界面类
class SchoolManagerGUI extends JFrame {

    // ================== 全局变量 ==================
    private Connection conn;
    private JTable studentTable, teacherTable, courseTable;
    private DefaultTableModel studentModel, teacherModel, courseModel;
    private BufferedImage backgroundImage;

    // 全局字体和颜色定义
    private final Font MAIN_FONT = new Font("微软雅黑", Font.PLAIN, 14);
    private final Font HEADER_FONT = new Font("微软雅黑", Font.BOLD, 15);
    // 半透明白色背景 (255,255,255, 200) -> 200是透明度(0-255)
    private final Color TRANSLUCENT_BG = new Color(255, 255, 255, 220);

    public SchoolManagerGUI() {
        // 1. 窗口基础设置
        setTitle("广西师范大学学生选课管理系统");
        setSize(1200, 650); // 稍微调大一点
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        // 2. 加载资源（增加背景图片容错）
        loadBackgroundImage("background.jpg");
        connectDatabase();

        // 3. 初始化自定义背景面板作为内容面板
        initBackgroundPanel();

        // 4. 加载数据
        loadStudentData();
        loadTeacherData();
        loadCourseData();
    }

    // 加载背景图片（增加容错处理）
    private void loadBackgroundImage(String imagePath) {
        try {
            // 尝试加载指定路径的图片
            File imgFile = new File(imagePath);
            if (imgFile.exists()) {
                backgroundImage = ImageIO.read(imgFile);
            } else {
                System.err.println("背景图片不存在，使用默认背景色");
                getContentPane().setBackground(new Color(240, 240, 240));
            }
        } catch (IOException e) {
            System.err.println("背景图片加载失败，使用默认背景色: " + e.getMessage());
            getContentPane().setBackground(new Color(240, 240, 240));
        }
    }

    // 初始化背景和主容器
    private void initBackgroundPanel() {
        // 使用自定义面板绘制背景图
        JPanel rootPanel = new JPanel() {
            @Override
            protected void paintComponent(Graphics g) {
                super.paintComponent(g);
                if (backgroundImage != null) {
                    // 保持比例铺满或者拉伸铺满，这里选择拉伸铺满
                    g.drawImage(backgroundImage, 0, 0, getWidth(), getHeight(), this);
                }
            }
        };
        rootPanel.setLayout(new BorderLayout());
        setContentPane(rootPanel); // 设置为窗口的主容器

        // 顶部菜单栏
        initMenuBar();

        // 中间标签页
        JTabbedPane tabbedPane = new JTabbedPane();
        tabbedPane.setFont(HEADER_FONT);
        // 让TabbedPane本身透明，不遮挡背景
        UIManager.put("TabbedPane.contentOpaque", false);
        tabbedPane.setOpaque(false);

        // 添加标签页（注意：内容面板内部会处理半透明逻辑）
        tabbedPane.addTab("  学生管理  ", createManagerPanel("Student"));
        tabbedPane.addTab("  教师管理  ", createManagerPanel("Teacher"));
        tabbedPane.addTab("  课程管理  ", createManagerPanel("Course"));

        // 给整个TabbedPane增加一些边距，不让内容贴着窗体边缘
        JPanel paddingPanel = new JPanel(new BorderLayout());
        paddingPanel.setOpaque(false);
        paddingPanel.setBorder(new EmptyBorder(20, 20, 20, 20));
        paddingPanel.add(tabbedPane, BorderLayout.CENTER);

        rootPanel.add(paddingPanel, BorderLayout.CENTER);
    }

    private void initMenuBar() {
        JMenuBar menuBar = new JMenuBar();
        // 菜单栏也可以半透明，或者保持默认
        JMenu fileMenu = new JMenu("系统选项");
        fileMenu.setFont(MAIN_FONT);
        JMenuItem exitItem = new JMenuItem("退出系统");
        exitItem.setFont(MAIN_FONT);
        exitItem.addActionListener(e -> System.exit(0));
        fileMenu.add(exitItem);
        menuBar.add(fileMenu);
        setJMenuBar(menuBar);
    }

    /**
     * 通用面板创建工厂方法
     * 这里的核心思路是：
     * 1. 外部容器完全透明
     * 2. 内部创建一个圆角半透明容器(TranslucentPanel)来包裹 表格 和 按钮
     */
    private JPanel createManagerPanel(String type) {
        // 1. 外层容器：完全透明，用于布局
        JPanel container = new JPanel(new BorderLayout());
        container.setOpaque(false);
        container.setBorder(new EmptyBorder(10, 0, 0, 0)); // Tab内容和Tab标签的间距

        // 2. 核心内容容器：半透明圆角背景
        TranslucentPanel contentPanel = new TranslucentPanel(TRANSLUCENT_BG);
        contentPanel.setLayout(new BorderLayout(10, 10)); // 组件间距
        contentPanel.setBorder(new EmptyBorder(15, 15, 15, 15)); // 内部留白

        // 3. 顶部按钮区
        JPanel btnPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 15, 0));
        btnPanel.setOpaque(false); // 按钮区域背景透明，透出contentPanel的颜色

        JButton addBtn = createStyledButton("添加");
        JButton editBtn = createStyledButton("修改");
        JButton delBtn = createStyledButton("删除");
        JButton refreshBtn = createStyledButton("刷新");

        btnPanel.add(addBtn);
        btnPanel.add(editBtn);
        btnPanel.add(delBtn);
        btnPanel.add(refreshBtn);

        // 4. 表格区
        JTable table;
        DefaultTableModel model;

        // 根据类型初始化不同的Model和Table
        if ("Student".equals(type)) {
            String[] cols = {"学号", "姓名", "年龄", "性别"};
            studentModel = new DefaultTableModel(cols, 0) {
                @Override public boolean isCellEditable(int r, int c) { return false; }
            };
            studentTable = createStyledTable(studentModel);
            table = studentTable;
            model = studentModel;
            // 绑定事件
            addBtn.addActionListener(e -> showStudentDialog(null));
            editBtn.addActionListener(e -> editStudent());
            delBtn.addActionListener(e -> deleteStudent());
            refreshBtn.addActionListener(e -> loadStudentData());
        } else if ("Teacher".equals(type)) {
            String[] cols = {"工号", "姓名", "科目"};
            teacherModel = new DefaultTableModel(cols, 0) {
                @Override public boolean isCellEditable(int r, int c) { return false; }
            };
            teacherTable = createStyledTable(teacherModel);
            table = teacherTable;
            model = teacherModel;
            // 绑定事件
            addBtn.addActionListener(e -> showTeacherDialog(null));
            editBtn.addActionListener(e -> editTeacher());
            delBtn.addActionListener(e -> deleteTeacher());
            refreshBtn.addActionListener(e -> loadTeacherData());
        } else {
            String[] cols = {"课程ID", "课程名称", "教师工号", "教室", "时间", "容量","学分","课程分类"};
            courseModel = new DefaultTableModel(cols, 0) {
                @Override public boolean isCellEditable(int r, int c) { return false; }
            };
            courseTable = createStyledTable(courseModel);
            table = courseTable;
            model = courseModel;
            // 绑定事件
            addBtn.addActionListener(e -> showCourseDialog(null));
            editBtn.addActionListener(e -> editCourse());
            delBtn.addActionListener(e -> deleteCourse());
            refreshBtn.addActionListener(e -> loadCourseData());
        }

        // 5. 滚动条处理（关键点：让滚动面板透明）
        JScrollPane scrollPane = new JScrollPane(table);
        scrollPane.getViewport().setOpaque(false); // 视口透明
        scrollPane.setOpaque(false); // 滚动条整体透明
        scrollPane.setBorder(BorderFactory.createEmptyBorder()); // 去掉边框

        // 组装
        contentPanel.add(btnPanel, BorderLayout.NORTH);
        contentPanel.add(scrollPane, BorderLayout.CENTER);

        container.add(contentPanel, BorderLayout.CENTER);
        return container;
    }

    // ================== UI 组件工厂 ==================

    /**
     * 创建风格化按钮
     */
    private JButton createStyledButton(String text) {
        JButton btn = new JButton(text);
        btn.setFont(MAIN_FONT);
        btn.setBackground(new Color(245, 245, 245));
        btn.setFocusPainted(false);
        btn.setCursor(new Cursor(Cursor.HAND_CURSOR));
        return btn;
    }

    /**
     * 创建风格化表格（半透明支持）
     */
    private JTable createStyledTable(DefaultTableModel model) {
        JTable table = new JTable(model);
        table.setFont(MAIN_FONT);
        table.setRowHeight(30); // 增加行高
        table.setOpaque(false); // 表格本身透明
        // 设置透明背景渲染器
        ((DefaultTableCellRenderer)table.getDefaultRenderer(Object.class)).setOpaque(false);

        // 设置表头样式
        JTableHeader header = table.getTableHeader();
        header.setFont(HEADER_FONT);
        header.setBackground(new Color(255, 255, 255, 200)); // 表头深色半透明
        header.setForeground(new Color(83,132,237));
        header.setReorderingAllowed(false);
        header.setBorder(BorderFactory.createEmptyBorder());

        // 设置选中行的颜色
        table.setSelectionBackground(new Color(30, 144, 255, 50)); // 蓝色半透明
        table.setSelectionForeground(Color.BLACK);

        // 隐藏网格线，看起来更现代
        table.setShowGrid(false);
        table.setIntercellSpacing(new Dimension(0, 0));

        // 关键：自定义单元格渲染器来实现交替行颜色和透明效果
        table.setDefaultRenderer(Object.class, new DefaultTableCellRenderer() {
            @Override
            public Component getTableCellRendererComponent(JTable table, Object value, boolean isSelected, boolean hasFocus, int row, int column) {
                Component c = super.getTableCellRendererComponent(table, value, isSelected, hasFocus, row, column);
                if (isSelected) {
                    c.setBackground(table.getSelectionBackground());
                } else {
                    // 奇偶行不同颜色，带透明度
                    c.setBackground(row % 2 == 0 ? new Color(230, 230, 230, 100) : new Color(255, 255, 255, 100));
                }
                return c;
            }
        });

        return table;
    }

    // ================== 自定义组件类 ==================

    /**
     * 一个支持自定义背景色（含透明度）和圆角的面板
     */
    class TranslucentPanel extends JPanel {
        private Color bgColor;

        public TranslucentPanel(Color bgColor) {
            this.bgColor = bgColor;
            setOpaque(false); // 必须设置为false，完全交由paintComponent绘制
        }

        @Override
        protected void paintComponent(Graphics g) {
            Graphics2D g2 = (Graphics2D) g.create();
            // 开启抗锯齿
            g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);

            g2.setColor(bgColor);
            // 绘制圆角矩形背景
            g2.fillRoundRect(0, 0, getWidth(), getHeight(), 20, 20);

            g2.dispose();
            super.paintComponent(g);
        }
    }

    // ================== 业务逻辑区 (保留原有逻辑，稍微包装一下) ==================

    private void connectDatabase() {
        try {
            Class.forName(Main.JDBC_DRIVER);
            conn = Main.getDBConnection();
        } catch (Exception e) {
            JOptionPane.showMessageDialog(this, "数据库连接失败: " + e.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            System.exit(1);
        }
    }

    // --- 学生操作 ---
    private void editStudent() {
        int row = studentTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择学生"); return; }
        String[] data = new String[4];
        for(int i=0; i<4; i++) data[i] = studentModel.getValueAt(row, i).toString();
        showStudentDialog(data);
    }

    private void deleteStudent() {
        int row = studentTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择学生"); return; }
        if (JOptionPane.showConfirmDialog(this, "确定删除?", "提示", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try (PreparedStatement ps = conn.prepareStatement("DELETE FROM students WHERE id=?")) {
                ps.setString(1, studentModel.getValueAt(row, 0).toString());
                ps.executeUpdate();
                loadStudentData();
            } catch (SQLException e) { JOptionPane.showMessageDialog(this, "删除失败: " + e.getMessage()); }
        }
    }

    private void loadStudentData() {
        studentModel.setRowCount(0);
        try (Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery("SELECT * FROM students")) {
            while (rs.next()) studentModel.addRow(new Object[]{rs.getString("id"), rs.getString("name"), rs.getInt("age"), rs.getString("gender")});
        } catch (SQLException e) { e.printStackTrace(); }
    }

    // --- 教师操作 ---
    private void editTeacher() {
        int row = teacherTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择教师"); return; }
        String[] data = new String[3];
        for(int i=0; i<3; i++) data[i] = teacherModel.getValueAt(row, i).toString();
        showTeacherDialog(data);
    }

    private void deleteTeacher() {
        int row = teacherTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择教师"); return; }
        if (JOptionPane.showConfirmDialog(this, "确定删除?", "提示", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try (PreparedStatement ps = conn.prepareStatement("DELETE FROM teachers WHERE id=?")) {
                ps.setString(1, teacherModel.getValueAt(row, 0).toString());
                ps.executeUpdate();
                loadTeacherData();
            } catch (SQLException e) { JOptionPane.showMessageDialog(this, "删除失败: " + e.getMessage()); }
        }
    }

    private void loadTeacherData() {
        teacherModel.setRowCount(0);
        try (Statement stmt = conn.createStatement(); ResultSet rs = stmt.executeQuery("SELECT * FROM teachers")) {
            while (rs.next()) teacherModel.addRow(new Object[]{rs.getString("id"), rs.getString("name"), rs.getString("subject")});
        } catch (SQLException e) { e.printStackTrace(); }
    }

    // --- 课程操作 ---
    private void editCourse() {
        int row = courseTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择课程"); return; }
        String[] data = new String[8];
        for(int i=0; i<8; i++) data[i] = courseModel.getValueAt(row, i).toString();
        showCourseDialog(data);
    }
    private void deleteCourse() {
        int row = courseTable.getSelectedRow();
        if (row < 0) { JOptionPane.showMessageDialog(this, "请选择课程"); return; }
        if (JOptionPane.showConfirmDialog(this, "确定删除?", "提示", JOptionPane.YES_NO_OPTION) == JOptionPane.YES_OPTION) {
            try (PreparedStatement ps = conn.prepareStatement("DELETE FROM courses WHERE id=?")) {
                ps.setString(1, courseModel.getValueAt(row, 0).toString());
                ps.executeUpdate();
                loadCourseData();
            } catch (SQLException e) { JOptionPane.showMessageDialog(this, "删除失败: " + e.getMessage()); }
        }
    }
    private void loadCourseData() {
        courseModel.setRowCount(0);
        try (Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery("SELECT * FROM courses")) {
            // 补充rs.getInt("credits")和rs.getString("category")
            while (rs.next()) {
                courseModel.addRow(new Object[]{
                        rs.getString("id"),
                        rs.getString("course_name"),
                        rs.getString("teacher_id"),
                        rs.getString("classroom"),
                        rs.getString("class_time"),
                        rs.getInt("capacity"),
                        rs.getInt("credits"),  // 新增：学分
                        rs.getString("category")  // 新增：课程分类
                });
            }
        } catch (SQLException e) {
            e.printStackTrace();
        }
    }

    // ================== 弹窗逻辑 (精简版，样式未做深度优化) ==================

    private void showStudentDialog(String[] data) {
        JDialog d = new JDialog(this, data == null ? "添加" : "修改", true);
        d.setSize(300, 250);
        d.setLocationRelativeTo(this);
        JPanel p = new JPanel(new GridLayout(5, 2, 10, 10));
        p.setBorder(new EmptyBorder(20,20,20,20));

        JTextField idF = new JTextField();
        JTextField nameF = new JTextField();
        JTextField ageF = new JTextField();
        JComboBox<String> sexBox = new JComboBox<>(new String[]{"男", "女"});

        p.add(new JLabel("学号:")); p.add(idF);
        p.add(new JLabel("姓名:")); p.add(nameF);
        p.add(new JLabel("年龄:")); p.add(ageF);
        p.add(new JLabel("性别:")); p.add(sexBox);

        if(data != null) {
            idF.setText(data[0]); idF.setEditable(false);
            nameF.setText(data[1]);
            ageF.setText(data[2]);
            sexBox.setSelectedItem(data[3]);
        }

        JButton save = new JButton("保存");
        save.addActionListener(e -> {
            try {
                // 输入校验（避免无效数据）
                String id = idF.getText().trim();
                String name = nameF.getText().trim();
                String ageText = ageF.getText().trim();
                String gender = sexBox.getSelectedItem().toString();

                if (id.isEmpty() || name.isEmpty() || ageText.isEmpty()) {
                    JOptionPane.showMessageDialog(d, "学号、姓名、年龄不能为空！");
                    return;
                }
                if (!ageText.matches("\\d+")) {
                    JOptionPane.showMessageDialog(d, "年龄必须是数字！");
                    return;
                }
                int age = Integer.parseInt(ageText);

                // 显式指定字段顺序，避免依赖表结构
                if(data == null) {
                    String sql = "INSERT INTO students (id, name, age, gender) VALUES (?, ?, ?, ?)";
                    PreparedStatement ps = conn.prepareStatement(sql);
                    ps.setString(1, id);
                    ps.setString(2, name);
                    ps.setInt(3, age);
                    ps.setString(4, gender);
                    ps.executeUpdate();
                } else {
                    String sql = "UPDATE students SET name=?, age=?, gender=? WHERE id=?";
                    PreparedStatement ps = conn.prepareStatement(sql);
                    ps.setString(1, name);  // 第1个参数是name
                    ps.setInt(2, age);      // 第2个参数是age
                    ps.setString(3, gender); // 第3个参数是gender
                    ps.setString(4, id);     // 第4个参数是id（WHERE条件）
                    ps.executeUpdate();
                }
                loadStudentData();
                d.dispose();
            } catch(Exception ex) {
                JOptionPane.showMessageDialog(d, "错误: " + ex.getMessage());
            }
        });

        p.add(save);
        JButton cancelBtn = new JButton("取消");
        cancelBtn.addActionListener(e -> d.dispose());
        p.add(cancelBtn);
        d.add(p);
        d.setVisible(true);
    }

    private void showTeacherDialog(String[] data) {
        JDialog d = new JDialog(this, data==null?"添加":"修改", true);
        d.setSize(300, 200);
        d.setLocationRelativeTo(this);
        JPanel p = new JPanel(new GridLayout(4, 2, 10, 10));
        p.setBorder(new EmptyBorder(20,20,20,20));

        JTextField idF = new JTextField();
        JTextField nameF = new JTextField();
        JTextField subF = new JTextField();
        p.add(new JLabel("工号:")); p.add(idF);
        p.add(new JLabel("姓名:")); p.add(nameF);
        p.add(new JLabel("科目:")); p.add(subF);

        if(data!=null) {
            idF.setText(data[0]); idF.setEditable(false);
            nameF.setText(data[1]);
            subF.setText(data[2]);
        }

        JButton save = new JButton("保存");
        save.addActionListener(e -> {
            try {
                // 输入校验
                String id = idF.getText().trim();
                String name = nameF.getText().trim();
                String subject = subF.getText().trim();

                if (id.isEmpty() || name.isEmpty() || subject.isEmpty()) {
                    JOptionPane.showMessageDialog(d, "工号、姓名、科目不能为空！");
                    return;
                }

                // 显式指定字段顺序
                String sql;
                PreparedStatement ps;
                if(data==null) {
                    sql = "INSERT INTO teachers (id, name, subject) VALUES (?, ?, ?)";
                    ps = conn.prepareStatement(sql);
                    ps.setString(1, id);
                    ps.setString(2, name);
                    ps.setString(3, subject);
                } else {
                    sql = "UPDATE teachers SET name=?, subject=? WHERE id=?";
                    ps = conn.prepareStatement(sql);
                    ps.setString(1, name);
                    ps.setString(2, subject);
                    ps.setString(3, id);
                }
                ps.executeUpdate();
                loadTeacherData();
                d.dispose();
            } catch(Exception ex) {
                JOptionPane.showMessageDialog(d, ex.getMessage());
            }
        });
        p.add(save);
        JButton cancelBtn = new JButton("取消");
        cancelBtn.addActionListener(e -> d.dispose());
        p.add(cancelBtn);
        d.add(p);
        d.setVisible(true);
    }
    // ================== 弹窗逻辑 (完整修正版) ==================
    private void showCourseDialog(String[] data) {
        // 1. 基础弹窗设置
        JDialog d = new JDialog(this, data == null ? "添加课程" : "修改课程", true);
        d.setSize(400, 460); // 调整合适的尺寸
        d.setLocationRelativeTo(this);
        d.setResizable(false); // 禁止缩放，保持布局规整

        // 2. 根面板：使用垂直BoxLayout，整体居中
        JPanel rootPanel = new JPanel();
        rootPanel.setLayout(new BoxLayout(rootPanel, BoxLayout.Y_AXIS));
        rootPanel.setBorder(new EmptyBorder(20, 20, 20, 20)); // 整体外间距

        // 3. 表单面板：用GridBagLayout实现精准对齐（核心优化）
        JPanel formPanel = new JPanel(new GridBagLayout());
        GridBagConstraints gbc = new GridBagConstraints();
        gbc.fill = GridBagConstraints.HORIZONTAL; // 组件水平填充
        gbc.insets = new Insets(8, 8, 8, 8); // 控件间距（上下左右8px）
        gbc.anchor = GridBagConstraints.CENTER; // 组件居中

        // ---- 表单控件定义 ----
        JTextField idF = new JTextField(15); // 指定输入框宽度，统一尺寸
        JTextField nameF = new JTextField(15);
        JTextField teacherIdF = new JTextField(15);
        JTextField classroomF = new JTextField(15);
        JTextField timeF = new JTextField(15);
        JTextField capacityF = new JTextField(15);
        JTextField creditsF = new JTextField(15);
        // 课程分类用下拉框+输入框结合，更规范（也可以只用输入框）
        JComboBox<String> categoryBox = new JComboBox<>(new String[]{"必修课", "选修课", "通识课", "专业课"});
        categoryBox.setEditable(true); // 允许自定义输入

        // ---- 逐个添加控件到表单面板 ----
        // 课程ID
        gbc.gridx = 0; gbc.gridy = 0;
        JLabel idLabel = new JLabel("课程ID：");
        formPanel.add(idLabel, gbc);
        gbc.gridx = 1; gbc.gridy = 0;
        formPanel.add(idF, gbc);
        if (data != null) {
            idF.setText(data[0]);
            idF.setEditable(false); // 修改时ID不可改
            // 显示ID输入框
            idLabel.setVisible(true);
            idF.setVisible(true);
        } else {
            // 添加时隐藏ID输入框
            idLabel.setVisible(false);
            idF.setVisible(false);
        }
        // 课程名称
        gbc.gridx = 0; gbc.gridy = 1;
        formPanel.add(new JLabel("课程名称："), gbc);
        gbc.gridx = 1; gbc.gridy = 1;
        formPanel.add(nameF, gbc);

        // 教师工号
        gbc.gridx = 0; gbc.gridy = 2;
        formPanel.add(new JLabel("教师工号："), gbc);
        gbc.gridx = 1; gbc.gridy = 2;
        formPanel.add(teacherIdF, gbc);

        // 教室
        gbc.gridx = 0; gbc.gridy = 3;
        formPanel.add(new JLabel("教室："), gbc);
        gbc.gridx = 1; gbc.gridy = 3;
        formPanel.add(classroomF, gbc);

        // 上课时间
        gbc.gridx = 0; gbc.gridy = 4;
        formPanel.add(new JLabel("上课时间："), gbc);
        gbc.gridx = 1; gbc.gridy = 4;
        formPanel.add(timeF, gbc);

        // 容量
        gbc.gridx = 0; gbc.gridy = 5;
        formPanel.add(new JLabel("容量："), gbc);
        gbc.gridx = 1; gbc.gridy = 5;
        formPanel.add(capacityF, gbc);

        // 学分
        gbc.gridx = 0; gbc.gridy = 6;
        formPanel.add(new JLabel("学分："), gbc);
        gbc.gridx = 1; gbc.gridy = 6;
        formPanel.add(creditsF, gbc);

        // 课程分类
        gbc.gridx = 0; gbc.gridy = 7;
        formPanel.add(new JLabel("课程分类："), gbc);
        gbc.gridx = 1; gbc.gridy = 7;
        formPanel.add(categoryBox, gbc);

        // 4. 按钮面板：水平排列，居中对齐
        JPanel btnPanel = new JPanel();
        btnPanel.setLayout(new FlowLayout(FlowLayout.CENTER, 20, 10)); // 按钮间距20px
        JButton saveBtn = new JButton("保存");
        JButton cancelBtn = new JButton("取消");
        // 按钮样式优化
        saveBtn.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        cancelBtn.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        saveBtn.setPreferredSize(new Dimension(80, 30)); // 统一按钮尺寸
        cancelBtn.setPreferredSize(new Dimension(80, 30));

        btnPanel.add(saveBtn);
        btnPanel.add(cancelBtn);

        // 5. 回显数据（修改时）
        if (data != null) {
            idF.setText(data[0]);
            idF.setEditable(false); // ID不可修改
            nameF.setText(data[1]);
            teacherIdF.setText(data[2]);
            classroomF.setText(data[3]);
            timeF.setText(data[4]);
            capacityF.setText(data[5]);
            creditsF.setText(data[6]);
            categoryBox.setSelectedItem(data[7]); // 回显分类
        }

        // 6. 保存按钮逻辑（功能不变，仅适配分类控件）
        saveBtn.addActionListener(e -> {
            try {
                // 输入值获取
                String courseName = nameF.getText().trim();
                String teacherId = teacherIdF.getText().trim();
                String classroom = classroomF.getText().trim();
                String classTime = timeF.getText().trim();
                String capacityText = capacityF.getText().trim();
                String creditsText = creditsF.getText().trim();
                String category = categoryBox.getSelectedItem().toString().trim();

                // 非空校验（添加时不需要校验ID）
                if (courseName.isEmpty() || teacherId.isEmpty() ||
                        classroom.isEmpty() || classTime.isEmpty() || capacityText.isEmpty() ||
                        creditsText.isEmpty() || category.isEmpty()) {
                    JOptionPane.showMessageDialog(d, "所有字段不能为空！", "提示", JOptionPane.WARNING_MESSAGE);
                    return;
                }

                // 数字校验
                if (!capacityText.matches("\\d+")) {
                    JOptionPane.showMessageDialog(d, "容量必须是数字！", "提示", JOptionPane.WARNING_MESSAGE);
                    return;
                }
                if (!creditsText.matches("\\d+")) {
                    JOptionPane.showMessageDialog(d, "学分必须是数字！", "提示", JOptionPane.WARNING_MESSAGE);
                    return;
                }
                int capacity = Integer.parseInt(capacityText);
                int credits = Integer.parseInt(creditsText);

                // 教师工号存在性校验
                String checkSql = "SELECT COUNT(*) FROM teachers WHERE id=?";
                PreparedStatement checkPs = conn.prepareStatement(checkSql);
                checkPs.setString(1, teacherId);
                ResultSet rs = checkPs.executeQuery();
                rs.next();
                if (rs.getInt(1) == 0) {
                    JOptionPane.showMessageDialog(d, "该教师工号不存在，请先添加教师！", "提示", JOptionPane.WARNING_MESSAGE);
                    return;
                }

                // 数据库操作
                String sql;
                PreparedStatement ps;
                if (data == null) {
                    // ------------------- 自动生成ID -------------------
                    String nextId = "00000001"; // 默认第一个ID
                    // 1. 查询当前最大的ID
                    String maxIdSql = "SELECT MAX(id) FROM courses";
                    PreparedStatement maxIdPs = conn.prepareStatement(maxIdSql);
                    ResultSet maxRs = maxIdPs.executeQuery();
                    if (maxRs.next() && maxRs.getString(1) != null) {
                        String currentMaxId = maxRs.getString(1);
                        // 2. 转换为数字并+1
                        int nextNum = Integer.parseInt(currentMaxId) + 1;
                        // 3. 格式化为8位字符串（补前导0）
                        nextId = String.format("%08d", nextNum);
                    }
                    // ------------------- 自动生成ID结束 -------------------

                    // 添加课程（使用生成的nextId）
                    sql = "INSERT INTO courses (id, course_name, teacher_id, classroom, class_time, capacity, credits, category) VALUES (?, ?, ?, ?, ?, ?, ?, ?)";
                    ps = conn.prepareStatement(sql);
                    ps.setString(1, nextId); // 自动生成的ID
                    ps.setString(2, courseName);
                    ps.setString(3, teacherId);
                    ps.setString(4, classroom);
                    ps.setString(5, classTime);
                    ps.setInt(6, capacity);
                    ps.setInt(7, credits);
                    ps.setString(8, category);
                } else {
                    // 修改课程（保持原有逻辑）
                    String id = idF.getText().trim();
                    sql = "UPDATE courses SET course_name=?, teacher_id=?, classroom=?, class_time=?, capacity=?, credits=?, category=? WHERE id=?";
                    ps = conn.prepareStatement(sql);
                    ps.setString(1, courseName);
                    ps.setString(2, teacherId);
                    ps.setString(3, classroom);
                    ps.setString(4, classTime);
                    ps.setInt(5, capacity);
                    ps.setInt(6, credits);
                    ps.setString(7, category);
                    ps.setString(8, id);
                }
                ps.executeUpdate();
                loadCourseData(); // 刷新表格
                d.dispose(); // 关闭弹窗
            } catch (Exception ex) {
                JOptionPane.showMessageDialog(d, "操作失败：" + ex.getMessage(), "错误", JOptionPane.ERROR_MESSAGE);
            }
        });

        // 7. 取消按钮逻辑
        cancelBtn.addActionListener(e -> d.dispose());

        // 8. 组装面板
        rootPanel.add(formPanel); // 添加表单
        rootPanel.add(Box.createVerticalStrut(10)); // 表单和按钮之间的间距
        rootPanel.add(btnPanel); // 添加按钮

        d.add(rootPanel);
        d.setVisible(true);
    }
    public static void main(String[] args) {
        // 设置全局UI风格，使其更像系统原生
        try {
            UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
        } catch (Exception ignored) {}

        SwingUtilities.invokeLater(() -> new SchoolManagerGUI().setVisible(true));
    }
}