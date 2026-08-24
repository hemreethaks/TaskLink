-- Step 1: Create and select database
CREATE DATABASE IF NOT EXISTS tasklink_db
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tasklink_db;

-- TABLE: users
CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  NOT NULL UNIQUE,
    password_hash VARCHAR(256)  NOT NULL,
    role          ENUM('ADMIN','CLIENT','FREELANCER') NOT NULL,
    rating        FLOAT         DEFAULT 0.0,
    is_active     TINYINT(1)    DEFAULT 1,
    created_at    DATETIME      DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_users_email (email),
    INDEX idx_users_role  (role)
);


-- TABLE: categories
CREATE TABLE IF NOT EXISTS categories (
    category_id   INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

-- TABLE: tasks
CREATE TABLE IF NOT EXISTS tasks (
    task_id        INT AUTO_INCREMENT PRIMARY KEY,
    client_id      INT  NOT NULL,
    category_id    INT  NOT NULL,
    title          VARCHAR(200) NOT NULL,
    description    TEXT         NOT NULL,
    workload_level ENUM('LOW','MEDIUM','HIGH') NOT NULL,
    budget         DECIMAL(10,2) NOT NULL,
    deadline       DATETIME      NOT NULL,
    status         ENUM('OPEN','ASSIGNED','SUBMITTED','COMPLETED','CANCELLED') DEFAULT 'OPEN',
    created_at     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (client_id)   REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_tasks_status    (status),
    INDEX idx_tasks_client    (client_id),
    INDEX idx_tasks_deadline  (deadline)
);

-- TABLE: applications
CREATE TABLE IF NOT EXISTS applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id        INT  NOT NULL,
    freelancer_id  INT  NOT NULL,
    bid_amount     DECIMAL(10,2) NOT NULL,
    proposal       TEXT          NOT NULL,
    applied_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id)       REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_application (task_id, freelancer_id)
);

-- TABLE: assignments
CREATE TABLE IF NOT EXISTS assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    task_id       INT NOT NULL,
    freelancer_id INT NOT NULL,
    assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id)       REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_assignment (task_id)
);

-- TABLE: submissions
CREATE TABLE IF NOT EXISTS submissions (
    submission_id   INT AUTO_INCREMENT PRIMARY KEY,
    task_id         INT          NOT NULL,
    freelancer_id   INT          NOT NULL,
    file_url        VARCHAR(500) NOT NULL,
    submission_note TEXT,
    submission_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id)       REFERENCES tasks(task_id) ON DELETE CASCADE,
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- TABLE: payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id     INT AUTO_INCREMENT PRIMARY KEY,
    task_id        INT NOT NULL,
    client_id      INT NOT NULL,
    freelancer_id  INT NOT NULL,
    amount         DECIMAL(10,2) NOT NULL,
    payment_status ENUM('PENDING','RELEASED') DEFAULT 'PENDING',
    payment_date   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id)       REFERENCES tasks(task_id),
    FOREIGN KEY (client_id)     REFERENCES users(user_id),
    FOREIGN KEY (freelancer_id) REFERENCES users(user_id),
    INDEX idx_payments_freelancer (freelancer_id),
    INDEX idx_payments_status     (payment_status)
);

-- TABLE: reviews
CREATE TABLE IF NOT EXISTS reviews (
    review_id   INT AUTO_INCREMENT PRIMARY KEY,
    task_id     INT NOT NULL,
    reviewer_id INT NOT NULL,
    reviewee_id INT NOT NULL,
    rating      INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comments    TEXT,
    review_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id)     REFERENCES tasks(task_id),
    FOREIGN KEY (reviewer_id) REFERENCES users(user_id),
    FOREIGN KEY (reviewee_id) REFERENCES users(user_id),
    UNIQUE KEY unique_review (task_id, reviewer_id)
);

-- TABLE: notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    message         VARCHAR(500) NOT NULL,
    status          ENUM('UNREAD','READ') DEFAULT 'UNREAD',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_notif_user   (user_id),
    INDEX idx_notif_status (status)
);

-- TABLE: activity_logs
CREATE TABLE IF NOT EXISTS activity_logs (
    log_id   INT AUTO_INCREMENT PRIMARY KEY,
    user_id  INT          NOT NULL,
    task_id  INT          NULL,
    action   VARCHAR(300) NOT NULL,
    log_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (task_id) REFERENCES tasks(task_id) ON DELETE SET NULL,
    INDEX idx_logs_user (user_id),
    INDEX idx_logs_date (log_date)
);

-- TABLE: monthly_reports

CREATE TABLE IF NOT EXISTS monthly_reports (
    report_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    report_month    VARCHAR(7)   NOT NULL,   -- e.g. '2024-04'
    total_tasks     INT          DEFAULT 0,
    completed_tasks INT          DEFAULT 0,
    active_tasks    INT          DEFAULT 0,
    total_earnings  DECIMAL(10,2) DEFAULT 0.00,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_report (user_id, report_month)
);

-- SEED DATA: Categories
INSERT IGNORE INTO categories (category_name) VALUES
  ('Data Entry'),
  ('Logo Design'),
  ('Code Debugging'),
  ('Translation'),
  ('Writing'),
  ('Resume Review'),
  ('PPT Creation'),
  ('Research Work'),
  ('Others');


DELIMITER $$
CREATE PROCEDURE IF NOT EXISTS GetFreelancerSummary(IN f_id INT)
BEGIN
    SELECT
        u.name,
        u.rating,
        COUNT(DISTINCT a.assignment_id) AS total_assigned,
        COUNT(DISTINCT p.payment_id)    AS total_paid,
        IFNULL(SUM(p.amount), 0)        AS total_earned
    FROM users u
    LEFT JOIN assignments a ON a.freelancer_id = u.user_id
    LEFT JOIN payments    p ON p.freelancer_id = u.user_id AND p.payment_status = 'RELEASED'
    WHERE u.user_id = f_id
    GROUP BY u.user_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER IF NOT EXISTS after_task_completed
AFTER UPDATE ON tasks
FOR EACH ROW
BEGIN
    IF NEW.status = 'COMPLETED' AND OLD.status != 'COMPLETED' THEN
        INSERT INTO activity_logs (user_id, task_id, action, log_date)
        VALUES (NEW.client_id, NEW.task_id, CONCAT('Task marked COMPLETED: ', NEW.title), NOW());
    END IF;
END$$
DELIMITER ;
