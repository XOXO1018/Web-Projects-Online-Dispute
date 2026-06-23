package database;

import java.io.FileInputStream;
import java.io.IOException;
import java.util.Properties;

/**
 * 数据库配置类 - 读取配置文件中的数据库连接信息
 */
public class DatabaseConfig {
    private static final String CONFIG_FILE = "config/database.properties";
    private static Properties properties;

    static {
        properties = new Properties();
        try {
            // 从类路径加载配置文件
            FileInputStream input = new FileInputStream("src/resources/config/database.properties");
            properties.load(input);
            input.close();
            System.out.println("数据库配置文件加载成功！");
        } catch (IOException e) {
            System.err.println("无法加载数据库配置文件，使用默认配置");
            setDefaultProperties();
        }
    }

    private static void setDefaultProperties() {
        properties.setProperty("db.url", "jdbc:mysql://localhost:3306/course_selection_system");
        properties.setProperty("db.username", "LINMQ");
        properties.setProperty("db.password", "aa512422410");
        properties.setProperty("db.driver", "com.mysql.cj.jdbc.Driver");
        properties.setProperty("db.pool.size", "10");
        properties.setProperty("db.max.connections", "20");
    }

    public static String getUrl() {
        return properties.getProperty("db.url");
    }

    public static String getUsername() {
        return properties.getProperty("db.username");
    }

    public static String getPassword() {
        return properties.getProperty("db.password");
    }

    public static String getDriver() {
        return properties.getProperty("db.driver");
    }

    public static int getPoolSize() {
        return Integer.parseInt(properties.getProperty("db.pool.size"));
    }

    public static int getMaxConnections() {
        return Integer.parseInt(properties.getProperty("db.max.connections"));
    }

    // 获取所有属性，用于调试
    public static void printConfig() {
        System.out.println("=== 数据库配置信息 ===");
        System.out.println("URL: " + getUrl());
        System.out.println("用户名: " + getUsername());
        System.out.println("驱动: " + getDriver());
        System.out.println("连接池大小: " + getPoolSize());
        System.out.println("最大连接数: " + getMaxConnections());
    }
}