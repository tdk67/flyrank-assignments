-- liquibase formatted sql

-- changeset developer:4
ALTER TABLE tasks DROP CONSTRAINT fk_tasks_assignee_user;
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_assignee_user
    FOREIGN KEY (assignee_user_id) REFERENCES users(id) ON DELETE SET NULL;
