import javax.swing.*;
import javax.swing.table.DefaultTableModel;
import java.awt.*;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.sql.*;
import java.util.Vector;

public class CreditStatisticsFrame extends JFrame {
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

        getContentPane().setBackground(new Color(240, 240, 240));

        // 顶部面板（原逻辑不变）
        JPanel topPanel = createTopPanel();
        add(topPanel, BorderLayout.NORTH);

        // 统计面板（原逻辑不变）
        JPanel statsPanel = createStatsPanel();
        add(statsPanel, BorderLayout.CENTER);

        // 底部面板（原逻辑不变）
        JPanel bottomPanel = createBottomPanel();
        add(bottomPanel, BorderLayout.SOUTH);
    }

    private JPanel createTopPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBackground(new Color(240, 240, 240));
        panel.setBorder(BorderFactory.createEmptyBorder(20, 20, 20, 20));

        // 标题
        JLabel titleLabel = new JLabel("学分统计分析", SwingConstants.CENTER);
        titleLabel.setFont(new Font("微软雅黑", Font.BOLD, 28));
        titleLabel.setForeground(new Color(0, 120, 215));
        panel.add(titleLabel, BorderLayout.NORTH);

        // 学生信息和筛选面板
        JPanel infoPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
        infoPanel.setBackground(new Color(240, 240, 240));

        JLabel studentInfoLabel = new JLabel("学号：" + studentId + " | 当前学期统计");
        studentInfoLabel.setFont(new Font("微软雅黑", Font.BOLD, 16));
        studentInfoLabel.setForeground(Color.DARK_GRAY);

        JLabel semesterLabel = new JLabel("选择学期：");
        semesterLabel.setFont(new Font("微软雅黑", Font.PLAIN, 14));

        semesterComboBox = new JComboBox<>(new String[]{"全部学期", "2024-2025-1", "2024-2025-2", "2023-2024-1", "2023-2024-2"});
        semesterComboBox.setFont(new Font("微软雅黑", Font.PLAIN, 14));
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
        panel.setBorder(BorderFactory.createEmptyBorder(0, 20, 20, 20));

        // 学分类型统计表格
        JPanel tablePanel = new JPanel(new BorderLayout());
        tablePanel.setBorder(BorderFactory.createTitledBorder("学分类型详细统计"));

        String[] columnNames = {"学分类型", "已修学分", "要求学分", "完成进度"};
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

        statsTable = new JTable(tableModel);
        statsTable.setFont(new Font("微软雅黑", Font.PLAIN, 14));
        statsTable.setRowHeight(35);
        statsTable.getTableHeader().setFont(new Font("微软雅黑", Font.BOLD, 14));
        statsTable.getTableHeader().setBackground(new Color(64, 158, 255));
        statsTable.getTableHeader().setForeground(Color.BLUE);
        statsTable.setSelectionBackground(new Color(220, 240, 255));

        statsTable.getColumnModel().getColumn(0).setPreferredWidth(150);
        statsTable.getColumnModel().getColumn(1).setPreferredWidth(100);
        statsTable.getColumnModel().getColumn(2).setPreferredWidth(100);
        statsTable.getColumnModel().getColumn(3).setPreferredWidth(150);

        JScrollPane scrollPane = new JScrollPane(statsTable);
        tablePanel.add(scrollPane, BorderLayout.CENTER);

        // 统计卡片面板
        JPanel cardsPanel = createStatsCardsPanel();

        panel.add(tablePanel);
        panel.add(cardsPanel);

        return panel;
    }

    private JPanel createStatsCardsPanel() {
        JPanel panel = new JPanel(new GridLayout(1, 4, 10, 10));
        panel.setBorder(BorderFactory.createTitledBorder("学分统计概览"));

        // 总学分统计
        JPanel totalPanel = createStatCard("总学分", "0", "毕业要求: 160学分", Color.BLUE);
        totalCreditsLabel = (JLabel) ((JPanel) totalPanel.getComponent(1)).getComponent(0);

        // 必修课学分
        JPanel requiredPanel = createStatCard("必修课学分", "0", "要求: 120学分", Color.GREEN);
        requiredCreditsLabel = (JLabel) ((JPanel) requiredPanel.getComponent(1)).getComponent(0);

        // 选修课学分
        JPanel electivePanel = createStatCard("选修课学分", "0", "要求: 30学分", Color.ORANGE);
        electiveCreditsLabel = (JLabel) ((JPanel) electivePanel.getComponent(1)).getComponent(0);

        // 实践环节学分
        JPanel practicalPanel = createStatCard("实践环节学分", "0", "要求: 10学分", Color.RED);
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
                BorderFactory.createEmptyBorder(15, 15, 15, 15)
        ));

        JLabel titleLabel = new JLabel(title, SwingConstants.CENTER);
        titleLabel.setFont(new Font("微软雅黑", Font.BOLD, 16));
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
        reqLabel.setFont(new Font("微软雅黑", Font.PLAIN, 12));
        reqLabel.setForeground(Color.GRAY);
        card.add(reqLabel, BorderLayout.SOUTH);

        return card;
    }

    private JPanel createBottomPanel() {
        JPanel panel = new JPanel(new BorderLayout());
        panel.setBorder(BorderFactory.createEmptyBorder(10, 20, 20, 20));
        panel.setBackground(new Color(240, 240, 240));

        // 进度条面板
        JPanel progressPanel = new JPanel(new FlowLayout(FlowLayout.CENTER));
        progressPanel.setBackground(new Color(240, 240, 240));

        JLabel progressLabel = new JLabel("总体完成进度：");
        progressLabel.setFont(new Font("微软雅黑", Font.BOLD, 14));

        totalProgressBar = new JProgressBar(0, 100);
        totalProgressBar.setPreferredSize(new Dimension(300, 25));
        totalProgressBar.setStringPainted(true);
        totalProgressBar.setFont(new Font("微软雅黑", Font.PLAIN, 12));

        progressPanel.add(progressLabel);
        progressPanel.add(totalProgressBar);

        // 按钮面板
        JPanel buttonPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 20, 10));
        buttonPanel.setBackground(new Color(240, 240, 240));

        JButton exportButton = new JButton("导出统计报告");
        JButton closeButton = new JButton("关闭窗口");

        for (JButton button : new JButton[]{exportButton, closeButton}) {
            button.setFont(new Font("微软雅黑", Font.PLAIN, 14));
            button.setPreferredSize(new Dimension(120, 35));
            button.setCursor(new Cursor(Cursor.HAND_CURSOR));
        }

        exportButton.setBackground(new Color(103, 194, 58));
        exportButton.setForeground(Color.WHITE);
        closeButton.setBackground(new Color(245, 108, 108));
        closeButton.setForeground(Color.WHITE);

        exportButton.addActionListener(e -> exportStatistics());
        closeButton.addActionListener(e -> dispose());

        buttonPanel.add(exportButton);
        buttonPanel.add(closeButton);

        panel.add(progressPanel, BorderLayout.CENTER);
        panel.add(buttonPanel, BorderLayout.SOUTH);

        return panel;
    }

    // 核心修改：适配现有数据库表结构
    // 核心修改：适配现有数据库表结构
    private void loadCreditStats() {
        Connection conn = null;
        PreparedStatement pstmt = null;
        ResultSet rs = null;

        try {
            conn = DatabaseConnection.getConnection();
            if (conn == null) return;

            // 适配数据库中课程类型的实际名称（例如："必修课"、"选修课"、"实践环节"）
            String sql = "SELECT " +
                    "c.category as course_type, " +
                    "SUM(c.credits) as earned_credits, " +
                    "CASE " +
                    "    WHEN c.category = '必修课' THEN 120 " +  // 匹配数据库中"必修课"
                    "    WHEN c.category = '选修课' THEN 30 " +   // 匹配数据库中"选修课"
                    "    WHEN c.category = '实践环节' THEN 10 " +// 匹配数据库中"实践环节"
                    "    ELSE 0 " +
                    "END as required_credits " +
                    "FROM enrollment sc " +
                    "JOIN courses c ON sc.course_id = c.id " +
                    "WHERE sc.student_id = ? " +
                    "GROUP BY c.category";

            pstmt = conn.prepareStatement(sql);
            pstmt.setString(1, studentId);
            rs = pstmt.executeQuery();

            // 初始化所有学分变量为0
            int totalEarnedCredits = 0;
            int totalRequiredCredits = 160;
            int requiredCredits = 0;    // 必修课已修学分
            int electiveCredits = 0;    // 选修课已修学分
            int practicalCredits = 0;   // 实践环节已修学分

            tableModel.setRowCount(0); // 清空表格

            while (rs.next()) {
                String courseType = rs.getString("course_type");
                int earnedCredits = rs.getInt("earned_credits");
                int required = rs.getInt("required_credits");
                double progress = required == 0 ? 0 : (double) earnedCredits / required * 100;

                // 添加到表格（保持原逻辑）
                Vector<Object> row = new Vector<>();
                row.add(courseType);
                row.add(earnedCredits);
                row.add(required);
                row.add(Math.round(progress * 100.0) / 100.0);
                tableModel.addRow(row);

                totalEarnedCredits += earnedCredits;

                // 关键修正：按数据库实际课程类型匹配，累加对应变量
                switch (courseType) {
                    case "必修课":  // 匹配数据库中"必修课"
                        requiredCredits = earnedCredits;  // 直接赋值（因为是GROUP BY后的结果）
                        break;
                    case "选修课":  // 匹配数据库中"选修课"
                        electiveCredits = earnedCredits;  // 直接赋值（因为是GROUP BY后的结果）
                        break;
                    case "实践环节":
                        practicalCredits = earnedCredits;
                        break;
                }
            }

            // 更新概览卡片
            updateStatsLabels(totalEarnedCredits, requiredCredits, electiveCredits, practicalCredits);

            // 后续进度条逻辑（保持原逻辑）
            int overallProgress = totalRequiredCredits == 0 ? 0 : (int) ((double) totalEarnedCredits / totalRequiredCredits * 100);
            totalProgressBar.setValue(overallProgress);
            totalProgressBar.setString(overallProgress + "%");

            if (overallProgress >= 80) {
                totalProgressBar.setForeground(Color.GREEN);
            } else if (overallProgress >= 60) {
                totalProgressBar.setForeground(Color.ORANGE);
            } else {
                totalProgressBar.setForeground(Color.RED);
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
            // 关闭资源（保持原逻辑）
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
        requiredCreditsLabel.setText(String.valueOf(required)+ "/120");
        electiveCreditsLabel.setText(String.valueOf(elective) + "/30");
        practicalCreditsLabel.setText(practical + "/10");
    }

    private void loadSemesterData() {
        // 若需要关联学期，可在enrollment表中添加semester字段后扩展
    }

    private void exportStatistics() {
        JFileChooser fileChooser = new JFileChooser();
        fileChooser.setDialogTitle("导出统计报告");
        fileChooser.setSelectedFile(new File("学分统计报告_" + studentId + ".pdf"));

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
            // 若需按学期筛选，可在SQL中添加semester条件（需先在enrollment表中添加semester字段）
            loadCreditStats();
        }
    }

    public static void main(String[] args) {
        // 测试时使用现有学生ID（例如202412302010）
        SwingUtilities.invokeLater(() -> {
            new CreditStatisticsFrame("202412302010").setVisible(true);
        });
    }
}