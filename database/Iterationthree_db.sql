CREATE TABLE if NOT EXISTS `route`(
    route_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',

    park_id INT NOT NULL COMMENT 'FK to park',

    difficulty_level ENUM('easy', 'medium', 'hard') NOT NULL COMMENT 'Route difficulty level',

    distance_m DECIMAL(8,2) NOT NULL COMMENT 'Estimated route distance in meters',

    estimated_time_min INT UNSIGNED NOT NULL COMMENT 'Estimated route completion time in minutes',

    checkpoint_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Number of checkpoints in this route',

    start_point POINT SRID 4326 NOT NULL COMMENT 'Route start point for map display and spatial query',

    st_line LINESTRING SRID 4326 NOT NULL COMMENT 'Route path as a spatial linestring',

    task_cluster_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Number of task clusters used to generate this route',

    original_task_count INT UNSIGNED NOT NULL DEFAULT 0 COMMENT 'Original number of candidate tasks before clustering',

    CONSTRAINT fk_route_park
        FOREIGN KEY (park_id) REFERENCES park(park_id),

    CONSTRAINT chk_route_distance
        CHECK (distance_m > 0),

    CONSTRAINT chk_route_estimated_time
        CHECK (estimated_time_min > 0),

    CONSTRAINT chk_route_checkpoint_count
        CHECK (checkpoint_count >= 0),

    SPATIAL INDEX idx_route_start_point (start_point),
    SPATIAL INDEX idx_route_st_line (st_line),

    INDEX idx_route_park_difficulty (park_id, difficulty_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE if NOT EXISTS `route_task` (
    route_task_id INT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key',

    route_id INT NOT NULL COMMENT 'FK to route',
    task_id INT NOT NULL COMMENT 'FK to task checkpoint',

    distance_from_route_m DECIMAL(8,2) NOT NULL COMMENT 'Distance from task checkpoint to route line in meters',

    CONSTRAINT fk_route_task_route
        FOREIGN KEY (route_id) REFERENCES route(route_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_route_task_task
        FOREIGN KEY (task_id) REFERENCES task(task_id)
        ON DELETE CASCADE,

    UNIQUE KEY uk_route_task_route_task (route_id, task_id),
    INDEX idx_route_task_task_id (task_id),
    INDEX idx_route_task_distance (route_id, distance_from_route_m)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
