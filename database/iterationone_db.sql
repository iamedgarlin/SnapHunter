USE snaphunter;

-- user
-- Store user information. Firebase UID is used for authentication and linking to user's google account.
CREATE TABLE if not exists user (
    user_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    firebase_uid VARCHAR(128) NOT NULL UNIQUE COMMENT 'Firebase UID for authentication',
    username VARCHAR(100) NOT NULL COMMENT 'Display name',
    total_point INT NOT NULL DEFAULT 0 COMMENT 'User total award points',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation time'
);

-- series
-- Store task in series for better organization and potential series-based badges.
CREATE TABLE if not exists series (
    series_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    series_name VARCHAR(255) NOT NULL COMMENT 'Series name',
    description TEXT NULL COMMENT 'Series description'
);

-- task
-- All the task which user can complete.
-- Task form now is only photo, but we can add more form in the future, such as video, text answer, etc.
CREATE TABLE if not exists task (
    task_id               INT            AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    series_id             INT            NOT NULL                   COMMENT 'FK to series',
    task_name             VARCHAR(255)   NOT NULL                   COMMENT 'Task name',
    task_description      TEXT           NULL                       COMMENT 'Task description',
    evaluation_criteria   TEXT           NULL                       COMMENT 'Rules used to judge whether the task is successfully completed',
    environment_type      ENUM('indoor', 'outdoor') NOT NULL        COMMENT 'Task environment',
    task_type             VARCHAR(50)    NOT NULL                   COMMENT 'Task form',
    location_label        VARCHAR(255)   NULL                       COMMENT 'Human-readable location name (outdoor only)',
    latitude              DECIMAL(10, 7) NULL                       COMMENT 'Latitude (outdoor only)',
    longitude             DECIMAL(10, 7) NULL                       COMMENT 'Longitude (outdoor only)',
    st_point              POINT SRID 4326 NULL                      COMMENT 'Spatial point for location queries',
    geofence_radius_meter INT            NULL                       COMMENT 'Geofence radius in meters (outdoor only)',
    base_difficulty       INT            NOT NULL DEFAULT 1         COMMENT 'Base difficulty (> 0)',
    reward_point          INT            NOT NULL DEFAULT 10        COMMENT 'Base reward points',
    is_active             BOOLEAN        NOT NULL DEFAULT TRUE      COMMENT 'Visible to users',
    create_time           DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Record creation time',

    CONSTRAINT fk_task_series
        FOREIGN KEY (series_id) REFERENCES series(series_id),
    CONSTRAINT chk_task_type_non_empty
        CHECK (CHAR_LENGTH(TRIM(task_type)) > 0),
    CONSTRAINT chk_task_base_difficulty
        CHECK (base_difficulty > 0),
    CONSTRAINT chk_task_reward_point
        CHECK (reward_point >= 0),
    CONSTRAINT chk_geofence_positive
        CHECK (geofence_radius_meter IS NULL OR geofence_radius_meter > 0),
    CONSTRAINT chk_outdoor_location
        CHECK (
            environment_type = 'indoor'
            OR (
                latitude IS NOT NULL
                AND longitude IS NOT NULL
                AND st_point IS NOT NULL
                AND geofence_radius_meter IS NOT NULL
            )
        ),
    CONSTRAINT chk_indoor_no_location
        CHECK (
            environment_type = 'outdoor'
            OR (
                latitude IS NULL
                AND longitude IS NULL
                AND st_point IS NULL
                AND geofence_radius_meter IS NULL
            )
        )
);

-- user_task
-- Store the user task status and submission details.
CREATE TABLE if not exists user_task (
    user_task_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    user_id INT NOT NULL COMMENT 'FK to user',
    task_id INT NOT NULL COMMENT 'FK to task',
    status BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'Task completion status: FALSE=in_progress, TRUE=completed',
    complete_time DATETIME NULL COMMENT 'Completion timestamp; NULL while in_progress',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Row creation time',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last update time',
    CONSTRAINT fk_ut_user FOREIGN KEY (user_id) REFERENCES user (user_id),
    CONSTRAINT fk_ut_task FOREIGN KEY (task_id) REFERENCES task (task_id),
    CONSTRAINT uk_ut_once UNIQUE (user_id, task_id)
);

-- badge
-- Store badge definitions. trigger_type defines the unlocking logic, and related fields are conditionally required based on the type.
-- trigger_type ENUM enforces valid values.
-- CHECK constraints enforce FK exclusivity and required_count rules per type.

CREATE TABLE if not exists badge (
    badge_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    badge_name VARCHAR(255) NOT NULL COMMENT 'Badge name',
    description TEXT NULL COMMENT 'Badge description',
    trigger_type ENUM(
        'task_completion', -- completing a specific task
        'series_completion', -- completing every task in a series
        'global_count' -- completing a number of tasks in total
    ) NOT NULL COMMENT 'Unlock trigger',
    target_task_id INT NULL COMMENT 'FK to task   (task_completion only)',
    target_series_id INT NULL COMMENT 'FK to series (series_completion only)',
    required_count INT NULL COMMENT 'Threshold    (global_count only)',
    CONSTRAINT fk_badge_task FOREIGN KEY (target_task_id) REFERENCES task (task_id),
    CONSTRAINT fk_badge_series FOREIGN KEY (target_series_id) REFERENCES series (series_id),
    CONSTRAINT chk_badge_task_completion CHECK (
        trigger_type <> 'task_completion'
        OR (
            target_task_id IS NOT NULL
            AND target_series_id IS NULL
            AND required_count IS NULL
        )
    ),
    CONSTRAINT chk_badge_series_completion CHECK (
        trigger_type <> 'series_completion'
        OR (
            target_series_id IS NOT NULL
            AND target_task_id IS NULL
            AND required_count IS NULL
        )
    ),
    CONSTRAINT chk_badge_global_count CHECK (
        trigger_type <> 'global_count'
        OR (
            target_task_id IS NULL
            AND target_series_id IS NULL
            AND required_count IS NOT NULL
            AND required_count > 0
        )
    )
);

-- user_badge
-- UNIQUE(user_id, badge_id) prevents duplicate awards.
-- To allow re-awarding (e.g. annual resets), drop uk_ub_once and add a
-- nullable award_period column as the uniqueness discriminator instead.
CREATE TABLE if not exists user_badge (
    user_badge_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',
    user_id INT NOT NULL COMMENT 'FK to user',
    badge_id INT NOT NULL COMMENT 'FK to badge',
    unlocked_time DATETIME NOT NULL COMMENT 'Award timestamp',
    CONSTRAINT fk_ub_user FOREIGN KEY (user_id) REFERENCES user (user_id),
    CONSTRAINT fk_ub_badge FOREIGN KEY (badge_id) REFERENCES badge (badge_id),
    CONSTRAINT uk_ub_once UNIQUE (user_id, badge_id)
);

-- insert series data "Nature": 1,"Urban": 2, "Art": 3.
INSERT INTO series (series_name, description) VALUES
('Nature', 'Tasks related to natural environments, such as flowers, trees, rivers, and wildlife.'),
('Urban', 'Tasks related to urban environments, such as city streets, buildings, and public spaces.'),
('Art', 'Tasks related to artworks and cultural landmarks, such as murals, sculptures, and historical sites.');