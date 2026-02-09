-- AI Micro Break System Database Schema
-- MySQL (XAMPP)

-- Create Database
CREATE DATABASE IF NOT EXISTS ai_microbreak_system;
USE ai_microbreak_system;

-- Users Table
CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(100) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    PasswordHash VARCHAR(255) NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    LastLogin TIMESTAMP NULL,
    IsActive BOOLEAN DEFAULT TRUE,
    PreferredBreakDuration INT DEFAULT 5,
    BreakInterval INT DEFAULT 30,
    BiometricDataConsent BOOLEAN DEFAULT FALSE,
    INDEX idx_username (Username),
    INDEX idx_email (Email)
);

-- Activity Log Table
CREATE TABLE ActivityLog (
    ActivityID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    MouseActivity INT DEFAULT 0,
    KeyboardActivity INT DEFAULT 0,
    ScreenInteractionTime INT DEFAULT 0,
    IdlePeriod INT DEFAULT 0,
    ApplicationName VARCHAR(255),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid_timestamp (UserID, Timestamp)
);

-- Fatigue Detection Data Table
CREATE TABLE FatigueDetection (
    FatigueID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FatigueScore FLOAT DEFAULT 0.0,
    EyeStrainLevel INT DEFAULT 0,
    BlinkRate FLOAT DEFAULT 0.0,
    PostureScore FLOAT DEFAULT 0.0,
    FacialExpression VARCHAR(50),
    WebcamDataUsed BOOLEAN DEFAULT FALSE,
    AlertGenerated BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid_timestamp (UserID, Timestamp)
);

-- Break Records Table
CREATE TABLE BreakRecords (
    BreakID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    BreakStartTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    BreakEndTime TIMESTAMP NULL,
    BreakDuration INT,
    BreakType VARCHAR(50),
    Reason VARCHAR(255),
    ComplianceStatus VARCHAR(20) DEFAULT 'Pending',
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid_starttime (UserID, BreakStartTime)
);

-- Recommendations Table
CREATE TABLE Recommendations (
    RecommendationID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    RecommendationType VARCHAR(100),
    Activity VARCHAR(255),
    Duration INT,
    Priority INT DEFAULT 1,
    UserFeedback VARCHAR(20),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid_timestamp (UserID, Timestamp)
);

-- Personalization Profile Table
CREATE TABLE PersonalizationProfile (
    ProfileID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL UNIQUE,
    LastUpdated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PreferredActivities JSON,
    OptimalBreakTime TIME,
    FatigueThreshold FLOAT DEFAULT 0.7,
    PeakProductivityHours JSON,
    BreakPreferences JSON,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid (UserID)
);

-- Productivity Analytics Table
CREATE TABLE ProductivityAnalytics (
    AnalyticsID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    Date DATE NOT NULL,
    TotalWorkTime INT DEFAULT 0,
    TotalBreakTime INT DEFAULT 0,
    ProductivityScore INT DEFAULT 0,
    AverageFatigueLevel FLOAT DEFAULT 0.0,
    BreakCompliance FLOAT DEFAULT 0.0,
    FocusScore INT DEFAULT 0,
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    UNIQUE KEY unique_user_date (UserID, Date),
    INDEX idx_userid_date (UserID, Date)
);

-- Break Enforcement Log Table
CREATE TABLE BreakEnforcementLog (
    EnforcementID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    EnforcementTime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    EnforcementType VARCHAR(50),
    ScreenLocked BOOLEAN DEFAULT FALSE,
    InputMuted BOOLEAN DEFAULT FALSE,
    Duration INT,
    UserCompliance VARCHAR(20),
    FOREIGN KEY (UserID) REFERENCES Users(UserID) ON DELETE CASCADE,
    INDEX idx_userid_time (UserID, EnforcementTime)
);

-- Wellness Tips Table (Pre-loaded with 10 activities)
CREATE TABLE WellnessTips (
    TipID INT PRIMARY KEY AUTO_INCREMENT,
    Category VARCHAR(50),
    TipText VARCHAR(500),
    Duration INT,
    Difficulty VARCHAR(20),
    Benefits VARCHAR(500),
    IsActive BOOLEAN DEFAULT TRUE,
    INDEX idx_category (Category)
);

-- Model Performance Table
CREATE TABLE ModelPerformance (
    ModelID INT PRIMARY KEY AUTO_INCREMENT,
    ModelName VARCHAR(100),
    TrainingDate DATE,
    Version VARCHAR(20),
    Accuracy FLOAT,
    Precision FLOAT,
    Recall FLOAT,
    F1Score FLOAT,
    INDEX idx_modelname (ModelName)
);

-- ==================== INSERT SAMPLE DATA ====================

-- Insert Sample Users
INSERT INTO Users (Username, Email, PasswordHash, PreferredBreakDuration, BreakInterval, BiometricDataConsent)
VALUES 
('john_doe', 'john@example.com', 'hashed_password_1', 5, 30, TRUE),
('jane_smith', 'jane@example.com', 'hashed_password_2', 5, 30, TRUE),
('admin_user', 'admin@example.com', 'hashed_admin_password', 5, 30, FALSE);

-- Insert Wellness Tips (10 pre-loaded activities)
INSERT INTO WellnessTips (Category, TipText, Duration, Difficulty, Benefits, IsActive) VALUES
('Eye Exercise', '20-20-20 Rule: Look at something 20 feet away for 20 seconds, every 20 minutes. Reduces eye strain and digital eye fatigue.', 1, 'Easy', 'Reduces eye strain, improves focus, prevents myopia progression', TRUE),
('Stretching', 'Neck Rolls: Slowly roll your head in circles, 5 times clockwise, 5 times counter-clockwise. Release tension in neck and shoulders.', 2, 'Easy', 'Relieves neck tension, improves circulation, reduces headaches', TRUE),
('Breathing', '4-7-8 Breathing: Breathe in for 4 counts, hold for 7, exhale for 8. Calms nervous system instantly.', 2, 'Easy', 'Reduces stress, lowers heart rate, improves focus', TRUE),
('Hydration', 'Drink Water: Consume 250ml of water. Hydration improves cognitive function and energy levels.', 2, 'Easy', 'Improves alertness, boosts metabolism, reduces headaches', TRUE),
('Posture', 'Posture Stretch: Stand up, reach arms up, lean backward gently for 10 seconds. Correct posture slouching.', 2, 'Easy', 'Corrects posture, reduces back pain, improves breathing', TRUE),
('Mindfulness', 'Guided Breathing: Close eyes, focus on breath for 2 minutes. Ground yourself in the present moment.', 3, 'Medium', 'Reduces anxiety, improves focus, enhances wellbeing', TRUE),
('Shoulder Work', 'Shoulder Shrugs: Lift shoulders to ears, hold 2 seconds, release. Repeat 10 times. Release tension.', 2, 'Easy', 'Relieves shoulder tension, improves circulation, reduces stress', TRUE),
('Hand Exercises', 'Hand Stretches: Extend arms, spread fingers wide, hold 10 seconds. Release tension from typing.', 2, 'Easy', 'Prevents carpal tunnel, improves grip strength, reduces pain', TRUE),
('Walking', 'Take a Walk: Walk around for 5 minutes. Improves circulation and provides mental reset.', 5, 'Medium', 'Boosts energy, improves circulation, enhances creativity', TRUE),
('Meditation', 'Guided Meditation: Follow a 5-minute guided meditation. Calm mind and reduce mental fatigue.', 5, 'Medium', 'Reduces stress, improves focus, enhances emotional wellbeing', TRUE);

-- Insert Sample Personalization Profile
INSERT INTO PersonalizationProfile (UserID, PreferredActivities, OptimalBreakTime, FatigueThreshold, PeakProductivityHours, BreakPreferences)
VALUES 
(1, '["Eye Exercise", "Stretching", "Walking"]', '09:00:00', 0.7, '["09:00-11:00", "14:00-16:00"]', '{"frequency": "every_30_mins", "duration": 5}');

-- Insert sample activity log entry
INSERT INTO ActivityLog (UserID, MouseActivity, KeyboardActivity, ScreenInteractionTime, IdlePeriod, ApplicationName)
VALUES (1, 45, 120, 600, 30, 'Visual Studio Code');

-- Insert sample fatigue detection entry
INSERT INTO FatigueDetection (UserID, FatigueScore, EyeStrainLevel, BlinkRate, PostureScore, FacialExpression, WebcamDataUsed, AlertGenerated)
VALUES (1, 0.45, 2, 14.5, 0.8, 'focused', TRUE, FALSE);
