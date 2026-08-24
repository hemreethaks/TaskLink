USE tasklink_db;

-- ── 1. All open tasks 
SELECT
    t.task_id,
    t.title,
    c.category_name,
    u.name        AS client_name,
    t.budget,
    t.workload_level,
    t.deadline,
    t.status
FROM tasks t
JOIN categories c ON t.category_id = c.category_id
JOIN users      u ON t.client_id   = u.user_id
WHERE t.status = 'OPEN'
ORDER BY t.created_at DESC;

-- ── 2. Number of applications per task 
SELECT
    t.task_id,
    t.title,
    COUNT(a.application_id) AS total_applications
FROM tasks       t
LEFT JOIN applications a ON a.task_id = t.task_id
GROUP BY t.task_id, t.title
ORDER BY total_applications DESC;

-- ── 3. All completed tasks by a specific freelancer 
-- Change 3 to any freelancer's user_id
SELECT
    t.task_id,
    t.title,
    t.budget,
    t.workload_level,
    t.status,
    ass.assigned_date,
    sub.submission_date
FROM tasks       t
JOIN assignments ass ON ass.task_id      = t.task_id
JOIN submissions sub ON sub.task_id      = t.task_id
WHERE ass.freelancer_id = 3
  AND t.status = 'COMPLETED';

-- ── 4. Monthly earnings of a specific freelancer 
-- Change 3 to any freelancer's user_id
SELECT
    report_month,
    total_tasks,
    completed_tasks,
    active_tasks,
    total_earnings
FROM monthly_reports
WHERE user_id = 3
ORDER BY report_month DESC;

-- ── 5. Average rating of all freelancers 
SELECT
    u.user_id,
    u.name,
    u.rating              AS stored_rating,
    AVG(r.rating)         AS calculated_avg,
    COUNT(r.review_id)    AS total_reviews
FROM users  u
LEFT JOIN reviews r ON r.reviewee_id = u.user_id
WHERE u.role = 'FREELANCER'
GROUP BY u.user_id, u.name, u.rating;

-- ── 6. All released payments 
SELECT
    p.payment_id,
    t.title       AS task_title,
    uc.name       AS client_name,
    uf.name       AS freelancer_name,
    p.amount,
    p.payment_status,
    p.payment_date
FROM payments p
JOIN tasks t  ON p.task_id       = t.task_id
JOIN users uc ON p.client_id     = uc.user_id
JOIN users uf ON p.freelancer_id = uf.user_id
WHERE p.payment_status = 'RELEASED'
ORDER BY p.payment_date DESC;

-- ── 7. Tasks with deadline within next 24 hours 
SELECT
    t.task_id,
    t.title,
    t.deadline,
    t.status,
    u.name AS client_name
FROM tasks t
JOIN users u ON t.client_id = u.user_id
WHERE t.deadline BETWEEN NOW() AND DATE_ADD(NOW(), INTERVAL 24 HOUR)
  AND t.status IN ('OPEN', 'ASSIGNED')
ORDER BY t.deadline ASC;

-- ── 8. Freelancer leaderboard by total earnings 
SELECT
    u.user_id,
    u.name,
    u.rating,
    IFNULL(SUM(p.amount), 0) AS total_earned,
    COUNT(p.payment_id)      AS tasks_paid
FROM users   u
LEFT JOIN payments p ON p.freelancer_id = u.user_id AND p.payment_status = 'RELEASED'
WHERE u.role = 'FREELANCER'
GROUP BY u.user_id, u.name, u.rating
ORDER BY total_earned DESC;

-- ── 9. Recent activity logs 
SELECT
    al.log_id,
    u.name  AS user_name,
    u.role,
    al.action,
    al.task_id,
    al.log_date
FROM activity_logs al
JOIN users u ON al.user_id = u.user_id
ORDER BY al.log_date DESC
LIMIT 50;

-- ── 10. Call the stored procedure for freelancer summary 
-- Change 3 to any freelancer's user_id
CALL GetFreelancerSummary(3);
