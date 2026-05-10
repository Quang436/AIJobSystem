CREATE DATABASE AIJobSystem
GO
USE AIJobSystem
GO
CREATE TABLE users (

    id INT PRIMARY KEY IDENTITY(1,1),

    fullname NVARCHAR(100),

    email NVARCHAR(100) UNIQUE,

    password_hash NVARCHAR(255),

    role NVARCHAR(20),

    gps_lat FLOAT,

    gps_lng FLOAT,

    ready_to_work BIT DEFAULT 0,

    created_at DATETIME DEFAULT GETDATE()
)
Go
CREATE TABLE jobs (

    id INT PRIMARY KEY IDENTITY(1,1),

    title NVARCHAR(255),

    company NVARCHAR(255),

    description NVARCHAR(MAX),

    salary NVARCHAR(100),

    address NVARCHAR(255),

    gps_lat FLOAT,

    gps_lng FLOAT,

    skills NVARCHAR(MAX),

    source NVARCHAR(100),

    status NVARCHAR(20),

    created_by INT,

    created_at DATETIME DEFAULT GETDATE()
)
Go
CREATE TABLE applications (

    id INT PRIMARY KEY IDENTITY(1,1),

    user_id INT,

    job_id INT,

    status NVARCHAR(50) DEFAULT 'pending',

    applied_at DATETIME DEFAULT GETDATE(),

    FOREIGN KEY (user_id) REFERENCES users(id),

    FOREIGN KEY (job_id) REFERENCES jobs(id)
)
Go
