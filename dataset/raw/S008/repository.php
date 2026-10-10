<?php
/**
 * 数据访问层：按姓名查询 lab_people 表。
 * 由 index.php 调用，接收已建立的数据库连接与待查询姓名。
 */
function find_people_by_name($db, $name) {
    $stmt = $db->prepare('SELECT id, name FROM lab_people WHERE name = ?');
    if ($stmt === false) {
        return false;
    }
    $stmt->bind_param('s', $name);
    $stmt->execute();
    return $stmt->get_result();
}
