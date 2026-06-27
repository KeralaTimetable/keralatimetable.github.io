const masterQuestionPool = [
    {
        "q": "The workings of the Blockchain technology is such that if you make a change to the information recorded in a particular block, you don't rewrite it, instead the change is stored in a new block.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "How did Blockchain technology impact Walmart Canada's supply chain management?",
        "o": [
            "It increased disputed invoices to 90%.",
            "It reduced disputed invoices from 70% to 1%.",
            "It eliminated all manual work in payables.",
            "It doubled the time required for carrier payments."
        ],
        "a": "B"
    },
    {
        "q": "What major trend is associated with the adoption of Blockchain technology?",
        "o": [
            "Mass adoption of centralization",
            "Mass adoption of decentralization",
            "Decreased security",
            "Increased regulation"
        ],
        "a": "B"
    },
    {
        "q": "Which one of the following Blockchain trends enables users to build their own digital products with Blockchain technology?",
        "o": [
            "Blockchain as a Product",
            "Blockchain as a Service",
            "Blockchain with AI",
            "Blockchain with IoT"
        ],
        "a": "B"
    },
    {
        "q": "Federated Blockchain is a type of Private Blockchain.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What is a key characteristic of Blockchain technology?",
        "o": [
            "High transaction fees",
            "Centralized control",
            "Decentralization",
            "Limited access"
        ],
        "a": "C"
    },
    {
        "q": "What does the term 'digital ledger' refer to in the context of Blockchain?",
        "o": [
            "A type of cryptocurrency",
            "A shared record of transactions",
            "A physical notebook",
            "A banking system"
        ],
        "a": "B"
    },
    {
        "q": "While using Blockchain, fragmented internal systems are centralized allowing interoperability.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Cryptocurrency is the technology that serves as the Distributed Ledger that forms the Network.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Bitcoin allows anyone to send money across borders almost instantly and with very low fees.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following are the benefits of employing Blockchain in financial transactions? A. Faster Transactions B. Error-Free Transactions C. Centralized Verification",
        "o": [
            "A and B",
            "B and C",
            "A and C"
        ],
        "a": "A"
    },
    {
        "q": "Which factor of blockchain makes it disruptive for the banking sector?",
        "o": [
            "The fact that it is fast.",
            "The fact that it reduces interactions with intermediaries.",
            "The fact that it is secure."
        ],
        "a": "B"
    },
    {
        "q": "How can Blockchain technology enhance Central Bank Digital Currencies (CBDCs)?",
        "o": [
            "By reducing financial access for individuals",
            "By compromising user security and privacy",
            "By providing transparency to track transactions",
            "By increasing the need for physical currency"
        ],
        "a": "C"
    },
    {
        "q": "In financial services, Blockchain technology is used for:",
        "o": [
            "Automation",
            "Digital Connection",
            "Digital Instruments"
        ],
        "a": "C"
    },
    {
        "q": "Blockchain can improve data quality for banks by ensuring that data does not exist in duplicate locations.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Blockchain makes data private and secure by using cryptographic techniques and Merkle trees, which makes it possible for only permissioned users within the ecosystem to access even publicly accessible data.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "On a blockchain, private data such as medical conditions or performance history can be immutably recorded. Once recorded, employees do not have control on their own data because records cannot be deleted from a blockchain.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is NOT true about the impact of Blockchain on the workforce?",
        "o": [
            "Salaries and bonuses will be more transparent if they are put on an open blockchain.",
            "Workplaces can use blockchain to track the work outsourced to independent or freelance staff, having a verified and tracked record of completed tasks.",
            "In the near future, all employers and universities will adopt blockchain technology, which will significantly simplify the resume verification process for recruiters.",
            "Blockchain as a career tool can help refugees and immigrants find jobs in the new country according to their skillsets and professional experience."
        ],
        "a": "C"
    },
    {
        "q": "Blue Prism is a RPA tool used widely in the industry.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "A well-controlled and scalable RPA platform in any organization needs a partnership between:",
        "o": [
            "HR and IT",
            "Operation and IT",
            "Support and IT"
        ],
        "a": "B"
    },
    {
        "q": "One RPA process can work with only one application.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "What are the two things necessary for the execution of a complete RPA solution?",
        "o": [
            "Operation Studio and HBO",
            "Process Studio and VBO",
            "Automation Studio and RBO"
        ],
        "a": "B"
    },
    {
        "q": "RPA tools enable a robust integration into the UI layer, which ensures that the layout and screen resolution changes in your application do not adjust.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Screen Scraping is useful when working with application interfaces that are _____________ through available UI frameworks or code.",
        "o": [
            "accessible",
            "not accessible",
            "readable",
            "not formattable"
        ],
        "a": "B"
    },
    {
        "q": "In Insurance Industry, workers spend more than half of their time in:",
        "o": [
            "Collecting and processing data",
            "Arranging offline paper data",
            "Printing reports"
        ],
        "a": "A"
    },
    {
        "q": "Using RPA bots, which one of the following functions can NOT be automated?",
        "o": [
            "Data entry into key systems",
            "Meeting customers one-to-one",
            "Downloading policyholder data from multiple sources",
            "Reading and scanning data"
        ],
        "a": "B"
    },
    {
        "q": "RPA implementation should never involve orchestrating the robots to automate processes, the robots can do it without supervision.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following will be a huge field of application of RPA in regulatory compliance processes in Insurance and Banking sectors? A. Process workflows B. Control costs",
        "o": [
            "Only A",
            "Only B",
            "Both A and B"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following are considered to be the core components of Phase 1.0 of the evolution of Big Data?",
        "o": [
            "Database management and Data warehousing",
            "Semi-structured and Unstructured Data",
            "Sensor-based and Internet-enabled devices"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following would Big Data Analytics majorly help with in the natural assets industry?",
        "o": [
            "Improving relationships with the customer",
            "Preventing production downtimes",
            "Analyzing geographical, text, and temporal data",
            "Predict customers demand from their choices"
        ],
        "a": "C"
    },
    {
        "q": "___ is a serverless, cost-effective enterprise data warehouse that operates across clouds and scales with your data.",
        "o": [
            "BigQuery",
            "Azure",
            "IBM Cloud",
            "Teradata"
        ],
        "a": "A"
    },
    {
        "q": "Generative AI revolutionizes data analysis by generating synthetic datasets and automating content creation, paving the way for advanced predictive analytics and data visualization.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which Big Data trend helps organizations maintain control over data usage while allowing multiple stakeholders to access data for their specific needs?",
        "o": [
            "Dark Data",
            "Data Lake",
            "Data Governance",
            "Data as Service"
        ],
        "a": "C"
    },
    {
        "q": "Traditional structured data is now complemented by unstructured text, images, audio, video files, and semi-structured formats like sensor data, which cannot be organized in a fixed schema.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "A centralized repository that allows you to store all your structured, unstructured and semi-structured data at any scale is called a:",
        "o": [
            "Dataset",
            "Database",
            "Data Lake",
            "Data Warehouse"
        ],
        "a": "C"
    },
    {
        "q": "Data visualization is a visual representation of data. It shows statistical and numerical data in visual ways to communicate their ____.",
        "o": [
            "meanings",
            "decisions",
            "conclusions",
            "reference"
        ],
        "a": "A"
    },
    {
        "q": "Which type of analytics describes or summarizes existing data to understand what is going on or what has happened?",
        "o": [
            "Descriptive Analytics",
            "Diagnostic Analytics",
            "Predictive Analytics",
            "Prescriptive Analytics"
        ],
        "a": "A"
    },
    {
        "q": "Big Data Analytics is a complete process of examining large sets of data through varied tools and processes in order to discover unknown patterns, hidden correlations, meaningful trends, and other insights for making data-driven decisions in the pursuit of better results.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which type of analytics ensures that the path is predicted for the future course of action?",
        "o": [
            "Predictive Analytics",
            "Prescriptive Analytics",
            "Diagnostic Analytics"
        ],
        "a": "B"
    },
    {
        "q": "Customer Segmentation and Differential Pricing Strategy can be easily achieved through Big Data Analytics.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which data analysis fails to cope with the advent of Big Data which is essentially huge data, both structured and unstructured?",
        "o": [
            "Traditional",
            "New",
            "Low"
        ],
        "a": "A"
    },
    {
        "q": "Healthcare big data refers to collecting, analyzing and leveraging consumer, patient, physical, and clinical data that is too vast or complex to be understood by traditional means of data processing.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which one of the following is NOT a key component of DBMS?",
        "o": [
            "Runtime Database Manager",
            "Equitable Manager",
            "Database Manager"
        ],
        "a": "B"
    },
    {
        "q": "RDBMSes store Data in the form of tables, with most commercial Relational Database Management Systems using:",
        "o": [
            "SQL",
            "Apache",
            "WorkFusion"
        ],
        "a": "A"
    },
    {
        "q": "The table format used in RDBMSes is easy to understand but does not provide an organized and structural manner through which entries are matched by firing queries.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which is an open source relational database management system (RDBMS) with a client-server model?",
        "o": [
            "Oracle",
            "MySQL",
            "MS-Access"
        ],
        "a": "B"
    },
    {
        "q": "MongoDB supports ad-hoc queries and document-based queries.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Identify the logo of following chatbot developed by OPEN AI:",
        "img": "images/chatgpt-logo.jpg",
        "o": [
            "GEMINI",
            "CHATGPT",
            "BING AI",
            "CLAUDE"
        ],
        "a": "B"
    },
    {
        "q": "What role do data science engineers play in the synergy between AI and data science engineering?",
        "o": [
            "Handling electronic health records in healthcare",
            "Optimizing investment portfolios in finance",
            "Evaluating AI models using statistical methods",
            "Developing AI algorithms and models"
        ],
        "a": "D"
    },
    {
        "q": "Arrange the following milestones in the order of their occurrence in the field of Artificial Intelligence (AI): 1. Introduction of the term \"Artificial Intelligence\" by John McCarthy. 2. IBM's Deep Blue defeats Garry Kasparov in a chess match. 3. Development of the first neural network model.",
        "o": [
            "1 > 3 > 2",
            "3 > 2 > 1",
            "2 > 3 > 1",
            "2 > 1 > 3"
        ],
        "a": "A"
    },
    {
        "q": "Match the following AI terms with their definitions: Column A | Column B 1. Machine Learning | A. A branch of AI that deals with algorithms that can learn from and make predictions on data. 2. Neural Networks | B. A type of AI model inspired by the human brain's neural structure, used for pattern recognition and classification in data. 3. Natural Language Processing | C. A technique in AI that enables machines to mimic cognitive functions such as learning and problem-solving.",
        "o": [
            "1-C, 2-B, 3-A",
            "1-A, 2-B, 3-C",
            "1-C, 2-A, 3-B",
            "1-A, 2-C, 3-B"
        ],
        "a": "B"
    },
    {
        "q": "A healthcare startup is developing an AI-powered diagnostic tool using neural networks to improve accuracy in detecting rare diseases. Which aspect of neural networks is crucial for achieving this goal?",
        "o": [
            "Loss functions",
            "Activation functions",
            "Gradient descent optimization",
            "Regularization techniques"
        ],
        "a": "B"
    },
    {
        "q": "How can understanding the business processes in a given domain help optimize operations?",
        "o": [
            "Enhancing decision-making",
            "Strengthening manual errors",
            "Enhancing fictional scenarios",
            "Promoting irrelevant details"
        ],
        "a": "A"
    },
    {
        "q": "A company wants to develop an AI model to improve its sales forecasting. Which of the following must be enhanced to achieve this?",
        "o": [
            "6-month forecast",
            "Dashboard reports",
            "Sales",
            "Model & report"
        ],
        "a": "D"
    },
    {
        "q": "A business wishes to improve its customer service procedure by utilizing AI. Put the steps in the proper order: 1. Put AI technologies into practice 2. Determine the main issues that customers face 3. Use consumer interaction data to train the AI model.",
        "o": [
            "3 → 1 → 2",
            "2 → 3 → 1",
            "1 → 2 → 3",
            "2 → 1 → 3"
        ],
        "a": "B"
    },
    {
        "q": "Identify the following chat bot:",
        "img": "images/gemini-logo-1.jpg",
        "o": [
            "CLAUDE",
            "GEMINI",
            "BING AI",
            "CHATGPT"
        ],
        "a": "B"
    },
    {
        "q": "A company wants to use AI to personalize its website content for individual users based on their browsing history. Which is the most important technical requirement for this project?",
        "o": [
            "Increased staff for customer service",
            "High-quality website design",
            "Low operational cost",
            "AI model for content recommendation"
        ],
        "a": "D"
    },
    {
        "q": "What historical event paved the way for the ability to build skyscrapers and mass-produced goods like cars?",
        "o": [
            "The Renaissance",
            "The French Revolution",
            "The Industrial Revolution",
            "The Enlightenment"
        ],
        "a": "C"
    },
    {
        "q": "A company is developing an AI assistant that can access and analyze user's personal data across multiple platforms to provide personalized recommendations. Which of the following is the most significant ethical concern in this scenario?",
        "o": [
            "Transparency of AI decision-making processes",
            "Impact on human jobs and employment",
            "User privacy and data protection",
            "Potential bias in AI algorithms"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following AI frameworks is being determined in the below image?",
        "img": "images/pytorch-logo.jpg",
        "o": [
            "Deep learning IO",
            "Neural networks",
            "Pytorch",
            "Python"
        ],
        "a": "C"
    },
    {
        "q": "A company decides to use Google Gemini AI to analyze sensitive customer data for personalized marketing. Which of the following is the most pressing concern in this scenario?",
        "o": [
            "Customer privacy and data protection",
            "Natural language processing capabilities",
            "Integration with existing cloud infrastructure",
            "Competition from other AI platforms"
        ],
        "a": "A"
    },
    {
        "q": "An AI-powered medical imaging system misdiagnoses a patient's condition, leading to inappropriate treatment. Which of the following is the most critical ethical consideration in this scenario?",
        "o": [
            "Potential job displacement of radiologists",
            "Algorithm accuracy and reliability",
            "Transparency and accountability of AI decision-making",
            "Patient privacy and data security"
        ],
        "a": "C"
    },
    {
        "q": "Artificial Intelligence (AI), Machine Learning (ML), and Deep Learning (DL) are often mentioned interchangeably, but they represent distinct aspects of technology. What distinguishes Deep Learning (DL) from Artificial Intelligence (AI) and Machine Learning (ML)?",
        "o": [
            "DL involves algorithms learning from data without explicit programming.",
            "DL focuses on achieving AI through algorithms and data training.",
            "DL mimics brain functions with layered neural networks for pattern recognition.",
            "DL encompasses tasks like language understanding and problem-solving."
        ],
        "a": "C"
    },
    {
        "q": "Match the following AI tools with their relevant use cases in healthcare: AI Tool | Use Case A. Neural Network 1. Predicting Patient Outcomes Based on Data B. Decision Trees 2. Detecting Tumors in medical images C. Natural Language Processing 3. Understanding and interpreting doctor's notes",
        "o": [
            "1-A, 2-C, 3-B",
            "1-B, 2-A, 3-C",
            "1-B, 2-C, 3-A",
            "1-C, 2-B, 3-A"
        ],
        "a": "A"
    },
    {
        "q": "Identify the following coding language which is used in ML:",
        "img": "images/python-logo.jpg",
        "o": [
            "JAVA",
            "PYTHON",
            "C++",
            "C"
        ],
        "a": "B"
    },
    {
        "q": "What analogy does Tomaso Poggio use to describe the periodicity of scientific ideas like neural networks?",
        "o": [
            "Waves in the ocean",
            "Epidemics of viruses",
            "Cycles of the moon",
            "Growth of plants"
        ],
        "a": "A"
    },
    {
        "q": "Arrange the following steps in the correct order for developing a Machine Learning model: 1. Model Evaluation 2. Data Preprocessing 3. Model Training",
        "o": [
            "2 > 3 > 1",
            "2 > 1 > 3",
            "1 > 3 > 2",
            "3 > 2 > 1"
        ],
        "a": "A"
    },
    {
        "q": "Arrange the following steps in correct order to describe the training process of a neural network: 1. Activation Function Application 2. Backpropagation 3. Forward Propagation",
        "o": [
            "2 > 1 > 3",
            "2 > 3 > 1",
            "1 > 3 > 2",
            "3 > 2 > 1"
        ],
        "a": "D"
    },
    {
        "q": "How can AI improve a recommendation system?",
        "o": [
            "Use collaborative filtering",
            "Use decision trees",
            "Use clustering",
            "Use linear regression"
        ],
        "a": "A"
    },
    {
        "q": "Which AI method helps in predicting future sales based on past data?",
        "o": [
            "Clustering",
            "Data visualization",
            "Regression analysis",
            "Decision trees"
        ],
        "a": "C"
    },
    {
        "q": "A retail company uses AI to predict demand and manage inventory. Which area will AI improve?",
        "o": [
            "Stock levels",
            "Warehouse construction",
            "Customer feedback",
            "Employee training"
        ],
        "a": "A"
    },
    {
        "q": "Which of the best is illustrated in the image below?",
        "img": "images/ai-lifecycle.jpg",
        "o": [
            "AI Process management",
            "AI Applications",
            "AI Future scope",
            "AI life cycle"
        ],
        "a": "D"
    },
    {
        "q": "Which stage of the machine learning process is shown in the image?",
        "img": "images/model-training.jpg",
        "o": [
            "Model Training",
            "Data Collection",
            "Model Evaluation",
            "Model Deployment"
        ],
        "a": "A"
    },
    {
        "q": "Match the Machine Learning concept with its description: Column A | Column B 1. Supervised Learning | A. Learns patterns and structures in data 2. Unsupervised Learning | B. Uses labeled data for training 3. Reinforcement Learning | C. Learns through trial and error feedback",
        "o": [
            "1-B, 2-A, 3-C",
            "1-C, 2-A, 3-B",
            "1-C, 2-B, 3-A",
            "1-A, 2-C, 3-B"
        ],
        "a": "A"
    },
    {
        "q": "Identify the following Learning from ML:",
        "img": "images/unsupervised.jpg",
        "o": [
            "Supervised",
            "Unsupervised",
            "Reinforcement",
            "Overfitting"
        ],
        "a": "B"
    },
    {
        "q": "Which type of AI exhibits specific facets of human intelligence such as recognizing images, but lacks other capabilities?",
        "o": [
            "Narrow AI",
            "General AI",
            "Deep Learning",
            "Machine Learning"
        ],
        "a": "A"
    },
    {
        "q": "A healthcare startup is evaluating AI applications to enhance patient diagnosis accuracy and treatment effectiveness. What consideration is crucial to ensure ethical and unbiased use of AI in healthcare?",
        "o": [
            "Minimizing human intervention",
            "Optimizing storage efficiency",
            "Implementing diverse datasets",
            "Enhancing computational speed"
        ],
        "a": "C"
    },
    {
        "q": "Arrange the following steps in correct order to train a deep learning model using supervised learning: 1. Evaluation of Model performance 2. Backpropagation to Update Weights 3. Initialization of Model Parameters",
        "o": [
            "2 > 3 > 1",
            "1 > 3 > 2",
            "3 > 2 > 1",
            "2 > 1 > 3"
        ],
        "a": "C"
    },
    {
        "q": "Which technology makes Deep Learning (DL) possible by mimicking the biological structure of the brain?",
        "o": [
            "Clustering",
            "Artificial Neural Networks (ANNs)",
            "Reinforcement Learning",
            "Decision Tree Learning"
        ],
        "a": "B"
    },
    {
        "q": "Match the terms in Column A with their corresponding descriptions in Column B: Column A | Column B 1. Google Gemini AI | a. Google's technology for understanding and generating human language 2. Multimodal Tasks | b. Tasks that involve multiple data types, such as text and images 3. NLP Capabilities | c. Google's AI model designed for multimodal task",
        "o": [
            "1-A, 2-C, 3-B",
            "1-C, 2-B, 3-A",
            "1-B, 2-A, 3-C",
            "1-C, 2-A, 3-B"
        ],
        "a": "B"
    },
    {
        "q": "A healthcare provider is considering implementing AI-driven diagnostic tools to streamline patient care and reduce diagnostic errors. Which ethical consideration is most critical in this scenario?",
        "o": [
            "Algorithm accuracy and reliability",
            "Regulatory compliance and legal implications",
            "Patient privacy and data security",
            "Staff training and adoption challenges"
        ],
        "a": "A"
    },
    {
        "q": "What is the relationship between artificial intelligence (AI), machine learning (ML), and deep learning (DL)?",
        "o": [
            "AI encompasses ML and DL with DL being a subset of ML",
            "AI encompasses ML and DL with ML being a subset of DL",
            "DL is a subset of ML which is a subset of AI",
            "AI is a subset of ML which in turn is a subset of DL"
        ],
        "a": "C"
    },
    {
        "q": "Arrange the following steps in order to describe how ChatGPT processes a user query: 1. Interpret the user query and identify the intent. 2. Retrieve relevant information from its training data. 3. Generate a response based on the identified intent and available data.",
        "o": [
            "3 > 2 > 1",
            "2 > 1 > 3",
            "1 > 3 > 2",
            "2 > 3 > 1"
        ],
        "a": "C"
    },
    {
        "q": "Identify the following Learning from ML:",
        "img": "images/supervised.jpg",
        "o": [
            "Overfitting",
            "Reinforcement",
            "Unsupervised",
            "Supervised"
        ],
        "a": "D"
    },
    {
        "q": "Identify the following chat bot:",
        "img": "images/gemini-logo-2.jpg",
        "o": [
            "BING AI",
            "CLAUDE",
            "GEMINI",
            "CHATGPT"
        ],
        "a": "C"
    },
    {
        "q": "What are the adjustable parameters in the Neurons called?",
        "o": [
            "Weights and Biases",
            "Input and Hidden layers",
            "Units and Cells",
            "Data and Biases"
        ],
        "a": "A"
    },
    {
        "q": "Systems that only react without creating memories or using any past experiences are called:",
        "o": [
            "Limited Memory",
            "Reactive Machines",
            "Theory of Mind",
            "Self-awareness"
        ],
        "a": "B"
    },
    {
        "q": "Deep learning uses multiple layers of Neural Networks to process unstructured data, unlike Machine Learning which relies on structured data.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Just like the PC, Internet and Cloud Computing, AI is also a disruptive technology.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "In Machine Learning, decisions are based on the type of algorithm selected.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Naïve Bayes Classifier algorithm is useful for predicting class of the test dataset.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Unsupervised Machine Learning algorithms are used when the information used to train is neither classified nor labelled.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which type of Machine Learning Algorithm is used by Stock Market Analysis?",
        "o": [
            "Unsupervised Learning Algorithms",
            "Supervised Learning Algorithms",
            "Reinforcement Learning Algorithms",
            "Semi-supervised Machine Learning"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following Machine Learning Algorithms is a learning method that interacts with its environment by producing actions and discovering errors or rewards?",
        "o": [
            "Supervised Learning",
            "Semi Supervised Learning",
            "Reinforcement Learning"
        ],
        "a": "C"
    },
    {
        "q": "What is differential privacy?",
        "o": [
            "A method to collect personal data.",
            "A way to protect our privacy.",
            "A technique for making AI secure.",
            "A method for making AI systems private."
        ],
        "a": "B"
    },
    {
        "q": "AI has the potential to amplify and scale the human biases at an unprecedented rate.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What is one of the benefits of having a strong AI code of ethics?",
        "o": [
            "It guarantees profit for the companies that implement AI.",
            "It ensures a secure and humane approach to AI.",
            "It eliminates the need for government regulations.",
            "It increases the speed of AI developments."
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is a challenge in establishing AI ethics?",
        "o": [
            "The lack of data for AI development.",
            "The absence of a wide-scale governing body.",
            "The high costs incurred to implement AI technologies.",
            "The rapid advancement of AI tools."
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is NOT a risk associated with Deepfakes?",
        "o": [
            "Increased attacks on celebrities and politicians",
            "Creation and dissemination of misleading information",
            "Creation of fake accounts or hacking into legitimate accounts",
            "Creation of a hyper personalized customer experience"
        ],
        "a": "D"
    },
    {
        "q": "In India, the ethical use of AI is detailed in a draft of _____________.",
        "o": [
            "National Artificial Intelligence Bureau",
            "National Artificial Intelligence Strategy",
            "National Artificial Intelligence Plan",
            "National Artificial Intelligence Federation"
        ],
        "a": "B"
    },
    {
        "q": "Generative AI can have significant environmental impact due to _____________.",
        "o": [
            "CO2 Emission",
            "NO2 Emission",
            "Computer Waste",
            "Heat Generation"
        ],
        "a": "A"
    },
    {
        "q": "Wearable technology using AI is making big strides in the healthcare industry through natural language processing and computer vision, by which it can learn visual cues and then convert them into natural voice cues for people with visual impairment.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following AI-powered wearables can calculate cardiovascular age and cardio capacity to give users insights into their long-term heart health?",
        "o": [
            "Apple Watch",
            "Ultrahuman Ring",
            "Fitbit",
            "Oura Ring"
        ],
        "a": "B"
    },
    {
        "q": "How are the nerve endings of 'phantom limb syndrome' used in bionics?",
        "o": [
            "A mechanical device with electrodes is controlled via computers.",
            "An e-sensor device electrically stimulates peripheral nerves of the amputated part.",
            "The nerve ending of the amputated part is cauterized and prosthetics are connected.",
            "Microprocessors embedded in the prosthetic arm can be externally guided."
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is not an intelligent wearable?",
        "o": [
            "Smart hearing aids",
            "Vision performance glasses",
            "Smart thermostat",
            "Pet tracking collars"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following sensors is used by AI to ensure there are no accidents caused by user parties?",
        "o": [
            "Lidar",
            "Mass Airflow",
            "NOx"
        ],
        "a": "A"
    },
    {
        "q": "EVs can be upgraded with the use of smart charging technologies.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "In EV manufacturing, _____ helps minimize downtime and keep operations running smoothly.",
        "o": [
            "Predictive maintenance",
            "Defect detection",
            "Visual inspection system",
            "Root cause analysis"
        ],
        "a": "A"
    },
    {
        "q": "For the upkeep and monitoring of EV batteries, AI is particularly crucial.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Users in the form of Digital Avatars interact with the online virtual space in the Metaverse.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which among the following makes sure that the Metaverse is always on and massively scalable?",
        "o": [
            "Inclusive User Interfaces",
            "Artificial Intelligence Operations (AIOps)",
            "Enhanced Smart Contracts",
            "Metaverse Support"
        ],
        "a": "B"
    },
    {
        "q": "Emotional Recognition is possible for customisation within the virtual world in Metaverse.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Metaverse helps to manage ____.",
        "o": [
            "Augmented Reality",
            "Virtual Reality",
            "Crypto Portfolio",
            "Artificial Intelligence"
        ],
        "a": "B"
    },
    {
        "q": "Antidemocratic activities in the Metaverse can be identified using ____.",
        "o": [
            "Enhanced Smart Contracts",
            "Intelligent Networking",
            "AIOps",
            "NVIDIA Omniverse"
        ],
        "a": "C"
    },
    {
        "q": "AI is not able to magnify the possibilities for human-complementary technological change, and developing a wide array of tools that provide better information to human decision-makers is challenging.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is NOT true?",
        "o": [
            "AI in the workplace is increasing the skill sets of workers, but not remuneration.",
            "Chatbots are being used by HR to support training activities.",
            "While automation and AI in the workforce may eliminate some positions, it can also create jobs and help job seekers avoid unemployment.",
            "The growth in AI is also creating new opportunities in other areas of emerging technology closely linked with it, such as Augmented Reality or IoT."
        ],
        "a": "A"
    },
    {
        "q": "For a career in AI, it is critical to understand the requirements of the business domain that can be solved through AI.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Through ____ companies can analyze customer preferences and behaviors to deliver tailored recommendations and services.",
        "o": [
            "AI-driven algorithms",
            "Predictive analytics",
            "Automation techniques",
            "Data analysis and insights"
        ],
        "a": "A"
    },
    {
        "q": "AI has the power to reduce busywork and enable workers to work better and focus on more strategic tasks.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "AI tools enable designers to rapidly explore new concepts and refine designs before they are produced.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "All current AI solutions belong to the _____ class.",
        "o": [
            "Artificial Intelligence Primer",
            "Artificial Network",
            "Artificial Model Foundation",
            "Artificial Narrow Intelligence"
        ],
        "a": "D"
    },
    {
        "q": "Reactive machines use past experiences to determine future actions.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Self-driving cars usually use Limited Memory technology to:",
        "o": [
            "Store data",
            "Automate",
            "Detect Motion"
        ],
        "a": "A"
    },
    {
        "q": "Which of these is NOT an application of AI?",
        "o": [
            "Language Translation",
            "Voice Recognition",
            "Robotics",
            "Obtain massive training data sets"
        ],
        "a": "D"
    },
    {
        "q": "Predictive maintenance, an application of AI, prevents unplanned downtime.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What is the name of the Artificial Intelligence firm that introduced ChatGPT?",
        "o": [
            "OpenAI",
            "Nuro",
            "Stem"
        ],
        "a": "A"
    },
    {
        "q": "ChatGPT is a type of natural language processing model known as a generative pre-trained Transformer",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "ChatGPT gives customers tailored responses that are more likely to lead to ________.",
        "o": [
            "Personalized experience",
            "Sales Support",
            "Lead generation"
        ],
        "a": "A"
    },
    {
        "q": "ChatGPT is trained to understand human inputs using the Reinforcement Learning from Human Feedback (RLHF) model.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "An e-commerce platform is planning to integrate ChatGPT AI chatbots to enhance customer service and increase sales. What is a primary benefit of using ChatGPT in this context?",
        "o": [
            "Enhancing website security",
            "Optimizing supply chain logistics",
            "Reducing customer wait times",
            "Automating inventory management"
        ],
        "a": "C"
    },
    {
        "q": "An machine learning company is enhancing its recommendation system, but users are increasingly reporting inaccurate suggestions. What could be a potential cause of this issue?",
        "o": [
            "Insufficient training data",
            "Overfitting of the model",
            "Low computational power",
            "Inappropriate algorithm choice"
        ],
        "a": "A"
    },
    {
        "q": "A retail company plans to integrate ChatGPT AI chatbots to enhance customer support and increase sales. Which capability of ChatGPT is most advantageous for this application?",
        "o": [
            "Personalizing shopping experiences",
            "Generating creative content",
            "Providing medical information",
            "Automating administrative tasks"
        ],
        "a": "A"
    },
    {
        "q": "In the context of neural networks and deep learning, a tech startup aims to enhance its product recommendations using AI. What application is most suitable for achieving this goal?",
        "o": [
            "Enhance customer engagement",
            "Optimize manufacturing processes",
            "Secure financial transaction",
            "Streamline project management"
        ],
        "a": "A"
    },
    {
        "q": "Marketers can use ChatGPT to find previously successful Marketing campaigns that can ideally resonate with an unrestricted audience.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "ChatGPT can analyze customer Data and offer tailored recommendations to address specific preferences.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "AI Text Classifier can be used for flagging potentially AI-generated text. However, one should not use it as a definitive measure for making a verdict.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "AI Text Classifier from OpenAI is a ________ detector.",
        "o": [
            "GPT-2 and OpenAI",
            "GPT-3 and ChatGPT",
            "GPT and OpenAI Tool"
        ],
        "a": "B"
    },
    {
        "q": "What is the purpose of using Blender in the OpenAI Point-E?",
        "o": [
            "To create a collection of 3D models",
            "To cluster 3D models based on CLIP properties",
            "To transform point clouds into meshes",
            "To develop a novel approach to point cloud diffusion"
        ],
        "a": "C"
    },
    {
        "q": "What are the two AI models used in Point-E and what is their function?",
        "o": [
            "Text-to-speech and image-to-video models for creating rendered objects",
            "Text-to-image and image-to-3D models for creating Point Clouds",
            "Text-to-3D and image-to-point cloud models for creating Meshes",
            "Text-to-object and image-to-Mesh models for creating 3D objects"
        ],
        "a": "B"
    },
    {
        "q": "What is the potential benefit of AI-powered text-to-3D model generators, Point-E for the entertainment industry?",
        "o": [
            "Reducing the cost of high-end 2D animation",
            "Generating real-world images for 3D object rendering",
            "Creating more detail but slower and computationally expensive 3D models",
            "Producing high-quality 3D representations such as meshes or NeRFs"
        ],
        "a": "D"
    },
    {
        "q": "What is one application of Point-E's AI system of point clouds that the OpenAI team believes could be used for in the long run?",
        "o": [
            "Production of virtual objects for gaming and animation sectors",
            "Creation of 2D animations for marketing",
            "Design of 3D printers for real objects production",
            "Enhancement of image quality for photography industries"
        ],
        "a": "A"
    },
    {
        "q": "What is the purpose of Point-E's image-to-3D model?",
        "o": [
            "To generate images without any 3D objects",
            "To generate 3D objects without any images",
            "To understand associations between words and their corresponding images",
            "To generate a more efficient understanding of 3D objects in combination with images"
        ],
        "a": "D"
    },
    {
        "q": "What is DALL-E?",
        "o": [
            "A Chatbot developed by Open AI.",
            "A language model used for Natural Language Processing.",
            "A generative AI model that can create images from text prompts.",
            "A Dataset containing millions of pictures with text captions."
        ],
        "a": "C"
    },
    {
        "q": "What is the name of the language model used to build DALL-E?",
        "o": [
            "Generative Pre-trained Transformer",
            "ChatGPT",
            "Diffusion Model",
            "Pixilated Image Model"
        ],
        "a": "A"
    },
    {
        "q": "What is the main difference between DALL-E 1 and DALL-E 2?",
        "o": [
            "DALL-E 1 can only render cartoonish images, while DALL-E 2 can produce realistic ones.",
            "DALL-E 2 is faster than DALL-E 1 at generating images.",
            "DALL-E 1 can only generate one image from a text, while DALL-E 2 can produce variations.",
            "DALL-E 2 is better at editing and retouching images than DALL-E 1."
        ],
        "a": "C"
    },
    {
        "q": "What is one way DALL-E can be utilized in the business world?",
        "o": [
            "Generating website traffic",
            "Creating social media campaigns",
            "Producing website layouts",
            "Generating customer reviews"
        ],
        "a": "C"
    },
    {
        "q": "How does DALL-E work?",
        "o": [
            "It generates images based on natural language descriptions",
            "It analyzes user behavior to predict preferences",
            "It uses machine learning to generate images from scratch",
            "It scans the internet for images and compiles them into new designs"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following tools will allow users to turn photos into art pieces?",
        "o": [
            "DeepArt.io",
            "StyleGAN",
            "Adobe Sensei",
            "GauGAN"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following is NOT among the 5Ds of Digital Marketing?",
        "o": [
            "Digital Platform",
            "Digital Systems",
            "Digital Data",
            "Digital",
            "Digital Media"
        ],
        "a": "B"
    },
    {
        "q": "A multi-touch attribution model makes data-driven decisions about where to invest your marketing budget, ensuring the highest Return-on-Investment (ROI) possible.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Digital Storytelling is versatile and can cover a wide variety of topics such as explaining a concept, reflecting a personal experience or making an argument",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Digital Storytelling in online education has only been adapted to create student engagement.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following statements is NOT true about storyboarding?",
        "o": [
            "Storyboarding is a visual blueprint of how a video will look and feel.",
            "A storyboard is a good step in a staged, longer-term project in a course to gauge if students are on the right track.",
            "Since a storyboard visualizes the final look of the project, it is very elaborate and detail-oriented."
        ],
        "a": "C"
    },
    {
        "q": "Which is the first stage involved in 3D Printing?",
        "o": [
            "Additive Manufacturing",
            "Strategy",
            "Printing"
        ],
        "a": "A"
    },
    {
        "q": "3D Printing is a tool used to create 3-Dimensional objects designed on computer.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which process is widely recognized as the first 3D Printing process?",
        "o": [
            "Stereolithography (SL)",
            "Digital Light Process",
            "Inkjet"
        ],
        "a": "A"
    },
    {
        "q": "Which 3D Printing process builds parts layer by layer using standard copier paper?",
        "o": [
            "Selective Deposition Lamination",
            "Extrusion",
            "Stereolithography"
        ],
        "a": "A"
    },
    {
        "q": "3D Printing creates parts by building up objects one layer at a time.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Digital Manufacturing technologies connect systems and processes across all aspects of production to produce an integrated manufacturing approach that spans design, production, and product service.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What are the key elements of Digital Manufacturing?",
        "o": [
            "Connected Design and Production, Connected Smart Factory and Connected Value Chain",
            "Digital Twins, Connected Smart Factory and Connected Value Chain",
            "Connected Design and Production, Manufacturing Software and Connected Value Chain",
            "RPA Production, Connected Smart Factory and Connected Management Software"
        ],
        "a": "A"
    },
    {
        "q": "What are the business units that adopt 3D Printing techniques and methodologies in an organization called?",
        "o": [
            "Digital manufacturers",
            "Digital factories",
            "Digital manufactory"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is an upcoming trend in 3D Printing?",
        "o": [
            "Polymer 3D Printing will dominate",
            "Hardware advances will amplify 3D Printing",
            "Automation will become a key focus"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following is predicted to be the next frontier as for the future of 3D Printing?",
        "o": [
            "Design validation, prototyping, jigs, and fixtures",
            "Mass production, functional end-use applications",
            "Product design with extensive tooling"
        ],
        "a": "B"
    },
    {
        "q": "From a reduction in cost, production speed, and risks to accelerating innovation, 3D Printing technology could dramatically change the future of Supply Chains.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following should be the first step to delivering technological and conceptual impact of 3D Printing in the Manufacturing Industry?",
        "o": [
            "Accepting new ways of designing parts",
            "Implementing advanced technology",
            "Focusing more on Rapid Prototyping"
        ],
        "a": "A"
    },
    {
        "q": "Personalized Healthcare represents one of the most significant areas of growth potential for 3D Printing technology in the medical space.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "The parking assistant feature in the car is an example of Augmented Reality.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which among these is a key element of the Virtual Reality experience?",
        "o": [
            "Over laying 3D images",
            "Immersion",
            "Simulation"
        ],
        "a": "B"
    },
    {
        "q": "The Snapchat face filters could be termed as primitive forms of Augmented Reality.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of this is more appropriate when it comes to AR and VR technologies?",
        "o": [
            "The fun quotient makes AR and VR different from the other technologies.",
            "AR and VR directly affects the perceptions and processes of human mind.",
            "The element of interactivity in AR and VR makes them different."
        ],
        "a": "B"
    },
    {
        "q": "What is the name of the first VR headset invented by Ivan Sutherland?",
        "o": [
            "Solomon's Golden Table",
            "The Sword of Damocles",
            "The Shroud of Turin"
        ],
        "a": "B"
    },
    {
        "q": "Metaverse is large scale and multifunctional; not limited to only VR/AR experience but fully revealed when using these technologies.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "When purchasing a digital item in the Metaverse, you need to secure your rights to be able to use it only on separate individual platforms.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of these applications is NOT possible with VR / AR in the financial industry?",
        "o": [
            "Data visualisation",
            "Virtual trading",
            "Human interaction",
            "Virtual Reality payments",
            "Customer acquisition"
        ],
        "a": "C"
    },
    {
        "q": "With augmented reality (AR), it is possible to see more information about a product in an engaging way, and also interact with a holographic salesperson right from where you are.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "By introducing biometric security in an AR system connected with a VR world, customers can securely access several banking processes such as VR bank services, ATM transactions, and payments.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "In a VR environment, the relationship between the properties of an object and the user's ability to act on it is based on the concept of ________.",
        "o": [
            "Allowances",
            "Affordances",
            "Spatial Awareness"
        ],
        "a": "B"
    },
    {
        "q": "Our own sight is curved. So displaying the text and images that aren't part of the VR environment as slightly curved will not look smooth and badly affect the visual immersion.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "You're developing a 360° VR video. You want your users to look in the left direction. Which of the following is the best way to do it without breaking the immersive experience?",
        "o": [
            "Pan the camera automatically to the speaker",
            "Avoid and create an alternative interaction",
            "Add audio cues such as make the character speak"
        ],
        "a": "C"
    },
    {
        "q": "What type of audio is most commonly used in VR?",
        "o": [
            "Monoscopic",
            "Stereoscopic",
            "Both Monoscopic and Stereoscopic"
        ],
        "a": "C"
    },
    {
        "q": "In immersive technology, _______ merges real and virtual worlds, where physical and digital objects interact in real time. This emerging technology requires wearable hardware, such as headsets or glasses.",
        "o": [
            "Virtual Reality",
            "Augmented Reality",
            "Mixed Reality",
            "Mirrored Reality"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following tools is best suited for creating and presenting AI-generated reports in a professional format?",
        "o": [
            "PowerPoint",
            "Excel",
            "Microsoft Word",
            "Gemini"
        ],
        "a": "A"
    },
    {
        "q": "Which type of visualization chart is represented in the image?",
        "img": "images/pie-chart.jpg",
        "o": [
            "Line chart",
            "Scatter plot",
            "Pie chart",
            "Doughnut chart"
        ],
        "a": "C"
    },
    {
        "q": "What type of AI model architecture is depicted in the image?",
        "img": "images/feedforward-nn.jpg",
        "o": [
            "Recurrent Neural Network (RNN)",
            "Reinforcement Learning Model",
            "Feedforward Neural Network",
            "Convolutional Neural Network (CNN)"
        ],
        "a": "C"
    },
    {
        "q": "What technological advancement contributed significantly to the resurgence of neural networks in recent years?",
        "o": [
            "Support vector machines (SVMs)",
            "Quantum computing",
            "Analog computing",
            "Graphics processing units (GPUs)"
        ],
        "a": "D"
    },
    {
        "q": "You need to visualize the sales growth trend over the last 12 months. Which type of chart would best display this data?",
        "o": [
            "Line chart",
            "Bar chart",
            "Pie chart",
            "Heat map"
        ],
        "a": "A"
    },
    {
        "q": "Match the tools in Column A with their primary uses in Column B. Column A | Column B 1. Microsoft Word | A. Creating visual presentations 2. Google Sheets | B. Organizing and analyzing data 3. Microsoft PowerPoint | C. Writing and formatting text documents",
        "o": [
            "1-B, 2-C, 3-A",
            "1-C, 2-B, 3-A",
            "1-A, 2-C, 3-B",
            "1-B, 2-A, 3-C"
        ],
        "a": "B"
    },
    {
        "q": "You have analyzed the number of hospital visits for different diseases over the past year. Which of the following visualizations would be most suitable for representing this data?",
        "o": [
            "Pie chart",
            "Line chart",
            "Bar chart",
            "Heat map"
        ],
        "a": "C"
    },
    {
        "q": "A Virtual Reality developer must have an understanding of textures, scripts, objects, components, and other Unity basics.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Select the statement that holds true for Virtual Reality:",
        "o": [
            "It is computationally Intensive.",
            "It requires less computation."
        ],
        "a": "A"
    },
    {
        "q": "Which language allows developers to quickly and easily create AR and VR experiences using features such as animations, physics, and sound effects?",
        "o": [
            "Rust",
            "UnityScript",
            "JavaScript",
            "C++"
        ],
        "a": "B"
    },
    {
        "q": "How did OpenAI evaluate GPT-4 efficiency and performance?",
        "o": [
            "By giving pre-recorded directions to self driving cars",
            "By simulating exams designed for humans like LSAT",
            "By providing reference images to a custom website"
        ],
        "a": "B"
    },
    {
        "q": "GPT-4 has more Data and can solve complex problems however GPT-3 has more Computing Power.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "OpenAI also claims that GPT-4 has a high degree of ________. It has also made it harder for the AI to break character.",
        "o": [
            "Steerability",
            "Summarization",
            "Tokenization"
        ],
        "a": "A"
    },
    {
        "q": "GPT-4 has been developed to improve model \"alignment\" - the ability to follow user intentions while also making it more truthful and generating less offensive or dangerous output.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Convolutional Neural Networks (CNNs) learn to recognize patterns in images by extracting features using convolutional and pooling layers.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What kind of settings and configurations does a Convolutional Neural Network (CNN) require before training the model?",
        "o": [
            "Hyperparameters",
            "Precise localization",
            "High-level interface",
            "Segmentation"
        ],
        "a": "A"
    },
    {
        "q": "In Neural Networks, the information is transferred to the next layer using:",
        "o": [
            "lengths and biases",
            "weights and biases",
            "input and output layer"
        ],
        "a": "B"
    },
    {
        "q": "The __________ determines the error in the prediction and reports it back to the Neural Network.",
        "o": [
            "Cost function",
            "Activation function",
            "Bias parameters",
            "Weighted sum"
        ],
        "a": "A"
    },
    {
        "q": "The Energy sector leverages IoT devices in _____________.",
        "o": [
            "Wireless grid communication",
            "Smart wearables",
            "Robotics",
            "Engine management"
        ],
        "a": "A"
    },
    {
        "q": "Which is the first stage in every IoT architecture?",
        "o": [
            "Sensors and Actuators",
            "Internet Getaways and Data Acquisition Systems",
            "Edge IT",
            "Data Center and Cloud"
        ],
        "a": "A"
    },
    {
        "q": "IoT devices are naturally vulnerable to _______ threats.",
        "o": [
            "Sensors",
            "Heterogeneity",
            "Security",
            "Connectivity"
        ],
        "a": "C"
    },
    {
        "q": "IoT is a paradigm that involves ubiquitous presence in the environment.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "You're hosting a party in your home and your guests have arrived. The smart security camera will:",
        "o": [
            "Detect the number of people who have entered the home, report to the AI Control Center and automatically turn on the lights",
            "Wait to receive the instructions from the owner of the house to turn on the lights"
        ],
        "a": "A"
    },
    {
        "q": "The latest advances of technology have tremendous potential to:",
        "o": [
            "Impact the jobs of the people",
            "Benefit people by Increasing efficiency and reducing waste"
        ],
        "a": "B"
    },
    {
        "q": "IoT can analyze mall traffic so that stores located in malls, can make the necessary adjustments that enhance the customer's shopping experience while reducing overhead.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "The IoT is a network of Internet-linked devices, vehicles, and appliances that can collect and share data without the need of human interaction.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following IIoT elements can be used in factories to tackle manufacturing challenges? A. Installing sensors throughout the factory to monitor production flow in real time to eliminate waste B. Creating predictive models based on the data gathered with the help of IoT devices",
        "o": [
            "Only A",
            "Only B",
            "Both A and B"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following are the biggest users of IIoT? A. Automotive Fleet Management B. Manufacturing C. Media and Entertainment",
        "o": [
            "A and B",
            "B and C",
            "A and C"
        ],
        "a": "A"
    },
    {
        "q": "As IoT devices collect vast amounts of user data, the potential for hacking and data breaches increases.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following are the top benefits of IIoT in manufacturing? A. Improvement of operational performance B. Ensuring safety and compliance C. Increasing flexibility and agility",
        "o": [
            "A and B",
            "A, B and C",
            "B and C"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is NOT an example of digital payment?",
        "o": [
            "Debit card",
            "Mobile wallet",
            "Cheque",
            "SWIFT",
            "UPI"
        ],
        "a": "C"
    },
    {
        "q": "Which of the following statements is NOT true about digital payments?",
        "o": [
            "An UPI payment can be made directly from your bank account, without typing in your card or bank details",
            "The most common type of PoS machine is a Debit or Credit card swiping machine which allows customers to pay after typing in a PIN",
            "A prepaid bank card is linked with your bank account and can be used numerous times",
            "Paytm, Freecharge, and Mobikwik are examples of mobile wallets"
        ],
        "a": "C"
    },
    {
        "q": "Which step in a digital payment transaction involves the encryption of your payment information?",
        "o": [
            "Initiation",
            "Authentication",
            "Authorization",
            "Completion"
        ],
        "a": "B"
    },
    {
        "q": "Which digital payments app has opened its own bank that is registered under the RBI?",
        "o": [
            "Paytm",
            "PhonePe",
            "GPay",
            "Amazon Pay"
        ],
        "a": "A"
    },
    {
        "q": "Digital payments are making a significant impact on various parts of the economy, such as financial inclusion, boosting small businesses, enhancing customer convenience, and promoting economic growth.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following statements is NOT true about Edge AI?",
        "o": [
            "With Edge AI, it is possible to achieve near real-time analytics.",
            "Edge often operates in an open network, which makes stealing information easier.",
            "With Edge AI, the model works in an edge device without requiring connection to the outside world at all times.",
            "Due to scalability of analytics and reduced latency in making critical decisions, edge AI can bring significant cost reductions in business operations."
        ],
        "a": "B"
    },
    {
        "q": "Predictive Maintenance is likely to be one of the most common use cases for TinyML.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Edge AI basically enables one to perform Machine Learning tasks on a _____ device.",
        "o": [
            "Cloud-enabled",
            "Local",
            "Internet-connected",
            "Battery-operated"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following is True about Quantum Computers?",
        "o": [
            "Quantum Computing deals with many options to compute information.",
            "It is based on quantum physics which makes it slower.",
            "Quantum Computers study atoms and particles.",
            "Because Quantum Computers use properties of quantum physics, they use much more energy than traditional computers."
        ],
        "a": "A"
    },
    {
        "q": "Quantum Computers use quantum bits instead of classical bits. Their special quantum properties allow them to represent both a '1' and a '0' at once in superposition and work together in an entangled group.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which company's research team discovered that entangling qubits on a Quantum Computer during a data-classification experiment reduced the error rate by half compared to unentangled qubits?",
        "o": [
            "JPMorgan Chase",
            "IBM",
            "Microsoft",
            "Rigetti Computing"
        ],
        "a": "A"
    },
    {
        "q": "In which domain will you find that Quantum Computing cannot be used?",
        "o": [
            "Complex manufacturing",
            "Drug discovery",
            "Financial services",
            "Classical computing"
        ],
        "a": "D"
    },
    {
        "q": "An educational institution is facing challenges in securely managing sensitive student data across multiple campuses. What technological solution should they prioritize?",
        "o": [
            "Cloud computing security solutions",
            "Quantum computing",
            "Blockchain technology",
            "Machine learning algorithms"
        ],
        "a": "A"
    },
    {
        "q": "_________ uses software and hardware methods to tackle external threats that can arise in the development stage of an application.",
        "o": [
            "Disaster Recovery",
            "Application Security",
            "Information Security",
            "Endpoint Security"
        ],
        "a": "B"
    },
    {
        "q": "Critical Infrastructure does not include:",
        "o": [
            "Electricity Grid",
            "Water Purification",
            "Traffic Lights",
            "Cooking Gas Lines"
        ],
        "a": "D"
    },
    {
        "q": "The full form of SEG is:",
        "o": [
            "Secure Email Gateway",
            "Secure Ecommerce Gateway",
            "Security Email Gateway",
            "Secure Email Gate"
        ],
        "a": "A"
    },
    {
        "q": "Application security uses software and hardware methods to tackle external threats.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Who alongside the FDA recently launched a joint initiative to \"increase coordination in dealing with threats related to medical devices?",
        "o": [
            "HHS",
            "DHS",
            "LHS",
            "AHS"
        ],
        "a": "B"
    },
    {
        "q": "Prioritizing simple security strategies is the best way to defeat evolving security threats.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "The easiest way for attackers to gain network access is to:",
        "o": [
            "Leverage existing vulnerabilities",
            "Creating new vulnerabilities",
            "Send Spam mails"
        ],
        "a": "A"
    },
    {
        "q": "A cybersecurity framework can be any document that defines procedures and goals to guide more detailed cybersecurity policies.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following is the recommended security standard for electronic payment processing?",
        "o": [
            "COBIT",
            "HiPAA rules",
            "PCI DSS"
        ],
        "a": "C"
    },
    {
        "q": "It's impractical to use multiple cybersecurity solutions to address different threats to your infrastructure.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Hackers are always looking for opportunities to invade privacy and steal data that's of crucial importance.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "A cyber attack is any type of offensive action that targets computer Information systems, infrastructures, computer networks or personal computer devices, using various methods to steal, alter or destroy data or information systems.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "One of the easiest ways your information can become hacked is through easy-to-guess passwords.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Which attack involves using IP spoofing and the ICMP to saturate a target network with traffic?",
        "o": [
            "Smurf attack",
            "Teardrop attack",
            "Replay attack"
        ],
        "a": "A"
    },
    {
        "q": "Botnets are the millions of systems infected with malware under hacker control in order to carry out DDoS attacks.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Automating process helps in reducing the number of data silos and the risk of human error.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Deepfakes are manipulated content powered by Machine Learning and are produced in different forms, such as text, audio, images, videos, and even real-time streams.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "What type of cybercrime is described as potentially becoming more financially damaging due to deepfakes?",
        "o": [
            "Ransomware attacks",
            "Distributed Denial of Service (DDoS) attacks",
            "Business Email Compromise (BEC) scams",
            "Man-in-the-middle attacks"
        ],
        "a": "C"
    },
    {
        "q": "Which one of these are not one of the big names in the FinTech cloud computing sector?",
        "o": [
            "Amazon Web Services",
            "Microsoft Silverlight",
            "Google Virtual Cloud",
            "Microsoft Azure"
        ],
        "a": "B"
    },
    {
        "q": "The resilience of Cloud deployments:",
        "o": [
            "Increases Uptime",
            "Simplifies Disaster Recovery",
            "Both of the above"
        ],
        "a": "C"
    },
    {
        "q": "An example of PaaS is:",
        "o": [
            "Rackspace Cloud",
            "Mosso",
            "Amazon EC2",
            "GMail"
        ],
        "a": "B"
    },
    {
        "q": "Which cloud service model is the most widely used in the world?",
        "o": [
            "SaaS",
            "PaaS",
            "IaaS",
            "All of them"
        ],
        "a": "A"
    },
    {
        "q": "Amazon Elastic MapReduce offers a ______ framework to process large amounts of data.",
        "o": [
            "R",
            "Hadoop",
            "Python",
            "None of the above."
        ],
        "a": "B"
    },
    {
        "q": "Cloud Computing can store a tremendous amount of data which can also help:",
        "o": [
            "Big Data Analytics",
            "Action Items",
            "Cloud Networks"
        ],
        "a": "A"
    },
    {
        "q": "Disaster Recovery is one of the major benefits of Cloud Computing.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Cloud Computing in e-commerce refers to the hosting and delivering of information through computer device on the internet via a network of servers.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Cloud Computing architect also depends on:",
        "o": [
            "Information, Technology, and Application",
            "Information, Bandwidth, and Application",
            "Type, Security, and Application"
        ],
        "a": "A"
    },
    {
        "q": "Computing is believed to facilitate greater collaboration and enhance the learning opportunities.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "SaaS is also known as hosted software or on-demand software.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "The PaaS service delivery model allows a customer to rent virtualized servers and associated services used to run existing applications, or to design, develop, test, deploy and host applications.",
        "o": [
            "True",
            "False"
        ],
        "a": "A"
    },
    {
        "q": "Grunge Computing is about moving local computing to local devices in a highly distributed system, typically as a layer around a cloud computing core.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "iPaaS offerings in the cloud from which providers let users implement data mapping, transformations is/are:",
        "o": [
            "Apache Spark",
            "Dell Boomi",
            "WorkFusion"
        ],
        "a": "B"
    },
    {
        "q": "Infrastructure as a Service and Hardware as a Service are two completely different things.",
        "o": [
            "True",
            "False"
        ],
        "a": "B"
    },
    {
        "q": "Which of the following Cloud Services is a user-friendly, no-code platform that allows one to create business applications?",
        "o": [
            "Ninox",
            "Amazon Aurora",
            "IBM DB2"
        ],
        "a": "A"
    },
    {
        "q": "Which Cloud programming language is known for its reusability and modular approach which makes writing codes easy?",
        "o": [
            "Python",
            "Java",
            "Ruby"
        ],
        "a": "B"
    },
    {
        "q": "Which among the following Cloud-based IDE is web-based and offers full stack browser environment to code anywhere, anytime?",
        "o": [
            "Codeanywhere",
            "Eclipse Orion",
            "Codenvy"
        ],
        "a": "C"
    },
    {
        "q": "Which Cloud Monitoring tool manages all aspects of the business's Private, Public, and Hybrid cloud?",
        "o": [
            "CA Unified Infrastructure Management",
            "Microsoft Cloud Monitoring",
            "Amazon Cloud Watch"
        ],
        "a": "A"
    },
    {
        "q": "Which of the following is the second phase of a typical Cloud Migration Framework?",
        "o": [
            "IT Infrastructure Discovery and Assessment",
            "Operate and Optimize",
            "Legacy IT to Cloud Operations Migration"
        ],
        "a": "C"
    }
];
