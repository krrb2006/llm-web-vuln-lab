<?php
/**
 * 共享数据库连接（教学样本公共 bootstrap，由 D 统一维护）
 *
 * 接口约定（与 D 商定）：
 *   - 建立 mysqli 连接并赋值给全局变量 $db；
 *   - 连接字符集设为 utf8mb4；
 *   - 连接参数只从环境变量读取，绝不写死在源码：
 *       DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD
 *   - 教学表 lab_people(id INT PRIMARY KEY, name VARCHAR(80) NOT NULL) 由 D 初始化。
 *
 * 待集成条件：
 *   - 若 D 提供自己的共享外壳/连接实现，则以 D 的实现替换本文件，
 *     保持「$db 变量 + utf8mb4 字符集 + lab_people 表」约定不变；
 *   - 密码通过容器/进程环境变量注入，不出现在仓库任何提交文件中。
 *
 * 本文件不含任何真实密码。
 */

$db = @new mysqli(
    getenv('DB_HOST') ?: '127.0.0.1',
    getenv('DB_USER') ?: 'lab_user',
    getenv('DB_PASSWORD'),
    getenv('DB_NAME') ?: 'teaching_lab',
    (int)(getenv('DB_PORT') ?: 3306)
);

if ($db->connect_errno) {
    error_log('lab db connect failed: ' . $db->connect_error);
    exit('数据库不可用，请稍后重试。');
}

$db->set_charset('utf8mb4');
