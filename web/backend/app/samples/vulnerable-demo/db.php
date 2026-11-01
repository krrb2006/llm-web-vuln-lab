<?php
$db = new PDO('sqlite::memory:');
$db->exec('CREATE TABLE users (id INTEGER, name TEXT)');
