-- Sample seed data for Azure SQL Server
-- Creates tables and inserts company knowledge data for retrieval testing

-- Create Companies table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Companies')
BEGIN
    CREATE TABLE Companies (
        CompanyID INT PRIMARY KEY IDENTITY(1,1),
        CompanyName NVARCHAR(255) NOT NULL,
        Industry NVARCHAR(100),
        FoundedYear INT,
        HeadquartersLocation NVARCHAR(255),
        EmployeeCount INT,
        Description NVARCHAR(MAX),
        CreatedDate DATETIME DEFAULT GETDATE(),
        ModifiedDate DATETIME DEFAULT GETDATE()
    );
    PRINT 'Companies table created';
END

-- Create Services table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Services')
BEGIN
    CREATE TABLE Services (
        ServiceID INT PRIMARY KEY IDENTITY(1,1),
        ServiceName NVARCHAR(255) NOT NULL,
        Category NVARCHAR(100),
        Description NVARCHAR(MAX),
        CompanyID INT FOREIGN KEY REFERENCES Companies(CompanyID),
        CreatedDate DATETIME DEFAULT GETDATE()
    );
    PRINT 'Services table created';
END

-- Create Leadership table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'Leadership')
BEGIN
    CREATE TABLE Leadership (
        LeaderID INT PRIMARY KEY IDENTITY(1,1),
        FullName NVARCHAR(255) NOT NULL,
        Title NVARCHAR(255),
        Bio NVARCHAR(MAX),
        CompanyID INT FOREIGN KEY REFERENCES Companies(CompanyID),
        LinkedInURL NVARCHAR(500),
        JoinedDate DATE,
        CreatedDate DATETIME DEFAULT GETDATE()
    );
    PRINT 'Leadership table created';
END

-- Create TechnologyPlatforms table
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'TechnologyPlatforms')
BEGIN
    CREATE TABLE TechnologyPlatforms (
        TechID INT PRIMARY KEY IDENTITY(1,1),
        PlatformName NVARCHAR(255) NOT NULL,
        Category NVARCHAR(100),
        Description NVARCHAR(MAX),
        CompanyID INT FOREIGN KEY REFERENCES Companies(CompanyID),
        Version NVARCHAR(50),
        CreatedDate DATETIME DEFAULT GETDATE()
    );
    PRINT 'TechnologyPlatforms table created';
END

-- Insert sample company data
IF NOT EXISTS (SELECT * FROM Companies WHERE CompanyName = 'Raoq Tech')
BEGIN
    INSERT INTO Companies (CompanyName, Industry, FoundedYear, HeadquartersLocation, EmployeeCount, Description)
    VALUES (
        'Raoq Tech',
        'Technology Consulting',
        2020,
        'United States',
        150,
        'Raoq Tech is a technology consulting firm specializing in AI, cloud infrastructure, and digital transformation. The company delivers enterprise-grade solutions using cutting-edge technologies including Microsoft Azure, AWS, and modern AI frameworks.'
    );
    PRINT 'Company data inserted';
END

-- Get CompanyID for foreign key references
DECLARE @CompanyID INT = (SELECT CompanyID FROM Companies WHERE CompanyName = 'Raoq Tech');

-- Insert sample services
IF NOT EXISTS (SELECT * FROM Services WHERE ServiceName = 'AI & Machine Learning')
BEGIN
    INSERT INTO Services (ServiceName, Category, Description, CompanyID)
    VALUES 
        ('AI & Machine Learning', 'Artificial Intelligence', 'Custom AI solutions including NLP, computer vision, and predictive analytics powered by Azure OpenAI and LangChain frameworks.', @CompanyID),
        ('Cloud Infrastructure', 'Cloud Services', 'End-to-end cloud architecture design and implementation on Azure, AWS, and hybrid environments with focus on scalability and security.', @CompanyID),
        ('Data Engineering', 'Data & Analytics', 'Big data pipelines, ETL processes, and data lake implementations using Azure Synapse, Databricks, and modern data stack tools.', @CompanyID),
        ('DevOps & Automation', 'Engineering', 'CI/CD pipeline automation, infrastructure as code, and container orchestration using Kubernetes and GitHub Actions.', @CompanyID);
    PRINT 'Services data inserted';
END

-- Insert sample leadership
IF NOT EXISTS (SELECT * FROM Leadership WHERE FullName = 'Jane Smith')
BEGIN
    INSERT INTO Leadership (FullName, Title, Bio, CompanyID, JoinedDate)
    VALUES 
        ('Jane Smith', 'Chief Executive Officer', 'Visionary leader with 20+ years in enterprise technology. Former VP at Microsoft Azure, specializing in cloud architecture and AI strategy.', @CompanyID, '2020-01-15'),
        ('John Doe', 'Chief Technology Officer', 'Expert in distributed systems and AI/ML infrastructure. Previously led engineering teams at major tech companies building scalable platforms.', @CompanyID, '2020-03-01'),
        ('Sarah Johnson', 'VP of Engineering', 'Passionate about building high-performing engineering teams. Specializes in agile methodologies and technical excellence.', @CompanyID, '2021-06-15');
    PRINT 'Leadership data inserted';
END

-- Insert sample technology platforms
IF NOT EXISTS (SELECT * FROM TechnologyPlatforms WHERE PlatformName = 'Microsoft Azure')
BEGIN
    INSERT INTO TechnologyPlatforms (PlatformName, Category, Description, CompanyID, Version)
    VALUES 
        ('Microsoft Azure', 'Cloud Platform', 'Primary cloud infrastructure platform for hosting applications, data services, and AI workloads. Includes Azure OpenAI Service integration.', @CompanyID, 'Latest'),
        ('LangChain', 'AI Framework', 'Core framework for building LLM-powered applications with retrieval-augmented generation (RAG) capabilities.', @CompanyID, '0.1.0'),
        ('Docker & Kubernetes', 'Containerization', 'Container orchestration and deployment platform for microservices architecture and scalable applications.', @CompanyID, 'K8s 1.28'),
        ('PostgreSQL', 'Database', 'Primary relational database with pgvector extension for vector similarity search in AI applications.', @CompanyID, '16.0'),
        ('Elasticsearch', 'Search Engine', 'Full-text search and analytics engine used for log aggregation and semantic search capabilities.', @CompanyID, '8.15');
    PRINT 'Technology platforms data inserted';
END

PRINT '✅ Seed data initialization completed successfully!';
