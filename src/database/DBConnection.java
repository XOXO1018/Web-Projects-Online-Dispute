package database;

import java.sql.*;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;

/**
 * 数据库连接管理类 - 单例模式
 * 支持连接池，提高性能
 */
public class DBConnection {
    // 单例实例
    private static DBConnection instance;

    // 连接池相关
    private List<Connection> connectionPool;
    private List<Connection> usedConnections;
    private static final int MAX_POOL_SIZE;
    private static final int INITIAL_POOL_SIZE;

    // 静态初始化块
    static {
        MAX_POOL_SIZE = DatabaseConfig.getMaxConnections();
        INITIAL_POOL_SIZE = DatabaseConfig.getPoolSize();
    }

    // 私有构造函数
    private DBConnection() {
        initializeConnectionPool();
    }

    /**
     * 获取单例实例
     */
    public static synchronized DBConnection getInstance() {
        if (instance == null) {
            instance = new DBConnection();
        }
        return instance;
    }

    /**
     * 初始化连接池
     */
    private void initializeConnectionPool() {
        connectionPool = new ArrayList<>(INITIAL_POOL_SIZE);
        usedConnections = new ArrayList<>();

        try {
            Class.forName(DatabaseConfig.getDriver());

            // 创建初始连接
            for (int i = 0; i < INITIAL_POOL_SIZE; i++) {
                Connection connection = createConnection();
                if (connection != null) {
                    connectionPool.add(connection);
                }
            }

            System.out.println("数据库连接池初始化完成，当前连接数: " + connectionPool.size());
        } catch (ClassNotFoundException e) {
            System.err.println("找不到数据库驱动: " + e.getMessage());
            JOptionPane.showMessageDialog(null,
                    "数据库驱动加载失败，请检查lib目录下是否有mysql-connector-java.jar文件",
                    "数据库错误", JOptionPane.ERROR_MESSAGE);
        }
    }

    /**
     * 创建新连接
     */
    private Connection createConnection() {
        try {
            return DriverManager.getConnection(
                    DatabaseConfig.getUrl(),
                    DatabaseConfig.getUsername(),
                    DatabaseConfig.getPassword()
            );
        } catch (SQLException e) {
            System.err.println("创建数据库连接失败: " + e.getMessage());
            return null;
        }
    }

    /**
     * 从连接池获取连接
     */
    public synchronized Connection getConnection() {
        if (connectionPool.isEmpty()) {
            // 如果连接池为空，检查是否可以创建新连接
            if (usedConnections.size() < MAX_POOL_SIZE) {
                Connection newConnection = createConnection();
                if (newConnection != null) {
                    usedConnections.add(newConnection);
                    return newConnection;
                }
            } else {
                System.err.println("已达到最大连接数限制");
                return null;
            }
        }

        // 从连接池获取一个连接
        Connection connection = connectionPool.remove(connectionPool.size() - 1);
        usedConnections.add(connection);

        return connection;
    }

    /**
     * 释放连接回连接池
     */
    public synchronized boolean releaseConnection(Connection connection) {
        if (connection != null) {
            usedConnections.remove(connection);
            connectionPool.add(connection);
            return true;
        }
        return false;
    }

    /**
     * 关闭所有连接
     */
    public synchronized void shutdown() {
        System.out.println("正在关闭数据库连接...");

        // 关闭连接池中的所有连接
        for (Connection connection : connectionPool) {
            closeConnection(connection);
        }

        // 关闭使用中的连接
        for (Connection connection : usedConnections) {
            closeConnection(connection);
        }

        connectionPool.clear();
        usedConnections.clear();
        System.out.println("所有数据库连接已关闭");
    }

    /**
     * 安全关闭连接
     */
    private void closeConnection(Connection connection) {
        try {
            if (connection != null && !connection.isClosed()) {
                connection.close();
            }
        } catch (SQLException e) {
            System.err.println("关闭数据库连接时出错: " + e.getMessage());
        }
    }

    /**
     * 获取连接池状态
     */
    public String getPoolStatus() {
        return String.format("连接池状态: 空闲连接数=%d, 使用中连接数=%d, 总连接数=%d",
                connectionPool.size(), usedConnections.size(),
                connectionPool.size() + usedConnections.size());
    }

    /**
     * 测试数据库连接
     */
    public boolean testConnection() {
        Connection conn = null;
        try {
            conn = getConnection();
            if (conn != null && !conn.isClosed()) {
                System.out.println("数据库连接测试成功！");
                return true;
            }
        } catch (SQLException e) {
            System.err.println("数据库连接测试失败: " + e.getMessage());
        } finally {
            if (conn != null) {
                releaseConnection(conn);
            }
        }
        return false;
    }

    /**
     * 执行查询并返回结果集
     */
    public ResultSet executeQuery(String sql, Object... params) {
        Connection conn = null;
        PreparedStatement pstmt = null;
        ResultSet rs = null;

        try {
            conn = getConnection();
            pstmt = conn.prepareStatement(sql);

            // 设置参数
            for (int i = 0; i < params.length; i++) {
                pstmt.setObject(i + 1, params[i]);
            }

            rs = pstmt.executeQuery();
            return rs;

        } catch (SQLException e) {
            System.err.println("执行查询失败: " + e.getMessage());
            System.err.println("SQL: " + sql);
            return null;
        } finally {
            // 注意：调用者需要自己关闭ResultSet和Statement
        }
    }

    /**
     * 执行更新操作（INSERT, UPDATE, DELETE）
     * @return 受影响的行数
     */
    public int executeUpdate(String sql, Object... params) {
        Connection conn = null;
        PreparedStatement pstmt = null;

        try {
            conn = getConnection();
            pstmt = conn.prepareStatement(sql);

            // 设置参数
            for (int i = 0; i < params.length; i++) {
                pstmt.setObject(i + 1, params[i]);
            }

            int rowsAffected = pstmt.executeUpdate();
            return rowsAffected;

        } catch (SQLException e) {
            System.err.println("执行更新失败: " + e.getMessage());
            System.err.println("SQL: " + sql);
            return -1;
        } finally {
            closeResources(null, pstmt, conn);
        }
    }

    /**
     * 关闭数据库资源
     */
    public void closeResources(ResultSet rs, Statement stmt, Connection conn) {
        try {
            if (rs != null) rs.close();
            if (stmt != null) stmt.close();
            if (conn != null) releaseConnection(conn);
        } catch (SQLException e) {
            System.err.println("关闭数据库资源时出错: " + e.getMessage());
        }
    }

    /**
     * 开始事务
     */
    public void beginTransaction(Connection conn) throws SQLException {
        if (conn != null) {
            conn.setAutoCommit(false);
        }
    }

    /**
     * 提交事务
     */
    public void commitTransaction(Connection conn) throws SQLException {
        if (conn != null) {
            conn.commit();
            conn.setAutoCommit(true);
        }
    }

    /**
     * 回滚事务
     */
    public void rollbackTransaction(Connection conn) {
        if (conn != null) {
            try {
                conn.rollback();
                conn.setAutoCommit(true);
            } catch (SQLException e) {
                System.err.println("回滚事务失败: " + e.getMessage());
            }
        }
    }
}