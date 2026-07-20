-- liquibase formatted sql

-- changeset developer:2
CREATE TABLE tasks (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    status VARCHAR(50) NOT NULL DEFAULT 'PLANNED',
    estimated_duration_days INTEGER,
    start_date TIMESTAMP WITH TIME ZONE,
    end_date TIMESTAMP WITH TIME ZONE,
    assignee_user_id UUID,
    CONSTRAINT fk_tasks_assignee_user
        FOREIGN KEY (assignee_user_id) REFERENCES users(id)
);

CREATE TABLE task_prerequisites (
    task_id UUID NOT NULL,
    prerequisite_task_id UUID NOT NULL,
    PRIMARY KEY (task_id, prerequisite_task_id),
    CONSTRAINT fk_task_prerequisites_task
        FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT fk_task_prerequisites_prerequisite
        FOREIGN KEY (prerequisite_task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    CONSTRAINT chk_task_prerequisites_not_same
        CHECK (task_id <> prerequisite_task_id)
);
