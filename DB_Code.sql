-- MySQL Workbench code for Collaborative Research Platform

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS research_platform;
USE research_platform;

-- User table
CREATE TABLE user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) NOT NULL,  -- 'student', 'professor', 'company'
    profile_image VARCHAR(120) DEFAULT 'default.jpg',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    college VARCHAR(120),  -- For students and professors
    field VARCHAR(120),  -- For professors
    company_name VARCHAR(120),  -- For companies
    date_of_birth DATE,  -- For students and professors
    CONSTRAINT chk_role CHECK (role IN ('student', 'professor', 'company'))
);

-- Document table
CREATE TABLE document (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(120) NOT NULL,
    description TEXT,
    file_path VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INT NOT NULL,  -- in bytes
    is_public BOOLEAN DEFAULT FALSE,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_modified DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- Collaboration table
CREATE TABLE collaboration (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    document_id INT NOT NULL,
    permission VARCHAR(20) DEFAULT 'view',  -- 'view', 'edit', 'comment'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (document_id) REFERENCES document(id) ON DELETE CASCADE,
    UNIQUE KEY unique_collaboration (user_id, document_id)
);

-- Notification table
CREATE TABLE notification (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    related_document_id INT,
    related_user_id INT,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE,
    FOREIGN KEY (related_document_id) REFERENCES document(id) ON DELETE SET NULL,
    FOREIGN KEY (related_user_id) REFERENCES user(id) ON DELETE SET NULL
);

-- Add indexes for better performance
CREATE INDEX idx_document_user ON document(user_id);
CREATE INDEX idx_document_public ON document(is_public);
CREATE INDEX idx_collaboration_user ON collaboration(user_id);
CREATE INDEX idx_collaboration_document ON collaboration(document_id);
CREATE INDEX idx_notification_user ON notification(user_id);
CREATE INDEX idx_notification_read ON notification(is_read);
select * from user;