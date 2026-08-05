# Machine Learning Development Lifecycle

A step-by-step overview of how machine learning systems are built, from idea to production.

---

## Step 1: Problem Definition & Framing
> **What we do in this step**: We sit down with business stakeholders to convert a real-world business objective into a technical machine learning prediction task. We evaluate if ML is even needed over simple rules, define the learning type (Supervised vs Unsupervised), and pick the exact evaluation metrics to measure success.

- **Business Goal vs ML Goal**: Business goal is the real-world outcome (e.g., reduce churn by 15%). ML goal is the prediction task (e.g., predict if a user leaves next month).
- **Rule-Based vs ML**: Use simple `if/else` rules if logic is fixed and simple. Use ML when patterns are complex or changing.
- **Supervised Learning**: Learning from historical data with known correct answers.
  - **Regression**: Predicting a continuous number (e.g., house price, salary).
  - **Classification**: Predicting a category (e.g., Fraud vs Legitimate, Spam vs Inbox).
- **Unsupervised Learning**: Finding hidden patterns or groupings in data without answers (e.g., customer segmentation).
- **Key Metrics**:
  - **Accuracy**: Percentage of correct predictions overall.
  - **Precision**: Out of all positive predictions, how many were right (minimizes false alarms).
  - **Recall**: Out of all real positive cases, how many were caught (minimizes missed cases).

---

## Step 2: Data Collection & Ingestion
> **What we do in this step**: We extract raw data from databases, APIs, log files, or streaming pipelines. We inspect data formats (Structured vs Unstructured) and split the data into Train, Validation, and Test sets while preventing future data from leaking into the past.

- **Data Sources**: Databases (SQL, MongoDB), APIs, event streams (Kafka), or static files (CSV, Parquet).
- **Structured vs Unstructured**: Tabular tables vs raw images, text, and audio.
- **Data Splitting**:
  - **Train Set (70%)**: Data used to train the model.
  - **Validation Set (15%)**: Data used to test settings and tune the model.
  - **Test Set (15%)**: Untouched data kept for a final performance check.
- **Time-Based Splitting**: For time-series data, split by time (train on past, test on future) to prevent data leakage.

---

## Step 3: Data Preprocessing
> **What we do in this step**: We clean messy raw data by removing duplicate records, imputing or dropping missing values, capping/removing extreme outliers, and scaling numerical features so all variables share a balanced numeric range.

- **Duplicates & Types**: Drop duplicate rows and fix incorrect data types (e.g., text to date).
- **Missing Values**:
  - **Drop**: Delete rows if missing data is minimal (< 5%).
  - **Impute**: Fill missing values with Average/Median (numerical) or most common value (categorical).
- **Outliers**: Extreme values far from the rest. Treat by capping minimum/maximum bounds or log transformation.
- **Feature Scaling**:
  - **StandardScaler**: Adjusts data so average is 0 and spread is 1 (great for distance-based algorithms like KNN/SVM).
  - **MinMaxScaler**: Scales all values between 0 and 1.

---

## Step 4: Exploratory Data Analysis (EDA)
> **What we do in this step**: We generate summary statistics and draw visual charts (histograms, scatter plots, correlation heatmaps) to discover hidden distributions, spot unexpected anomalies, and understand relationships between input features and the target.

- **Summary Stats**: Check data shape, distributions, mean, and range (`df.describe()`).
- **Visualizations**:
  - **Histograms / Bar plots**: View distribution of single variables.
  - **Scatter plots**: Check relationship between two numerical variables.
  - **Heatmaps**: Check correlations across all features to find strong connections.
- **Outlier Visuals**: Boxplots to highlight extreme points.

---

## Step 5: Feature Engineering & Selection
> **What we do in this step**: We transform raw variables into highly predictive inputs by encoding text categories into numbers, creating domain-specific ratios or time features, and dropping useless or redundant variables to improve model focus.

- **Categorical Encoding**:
  - **One-Hot Encoding**: Converts text categories into separate binary (0 or 1) columns.
  - **Ordinal Encoding**: Converts ordered categories (Low, Medium, High) into numbers (0, 1, 2).
- **Feature Creation**: Combine features (e.g., `price / square_feet`) or extract parts of dates (day, month, hour).
- **Feature Selection**: Drop redundant, constant, or highly correlated features so the model stays simple and accurate.

---

## Step 6: Model Building & Training
> **What we do in this step**: We start by building a simple baseline model to benchmark performance, then select and train candidate algorithms (Linear, Tree-based, or Neural Networks) by feeding processed features to learn underlying patterns.

- **Baseline Model**: Always build a simple model first (e.g., Logistic Regression) to set a minimum benchmark score.
- **Common Model Families**:
  - **Linear Models**: Linear Regression, Logistic Regression.
  - **Tree Models**: Decision Trees, Random Forest, XGBoost.
  - **Distance Models**: K-Nearest Neighbors (KNN), Support Vector Machines (SVM).
  - **Neural Networks**: For complex unstructured data (Text, Images, Audio).
- **Model Fitting**: Passing training data into the algorithm to let it learn weights and rules.

---

## Step 7: Model Evaluation & Hyperparameter Tuning
> **What we do in this step**: We test model performance across K-Fold cross-validation splits, diagnose overfitting vs underfitting, and run search algorithms (Grid/Random search) to tune model hyperparameters for maximum generalization on unseen data.

- **Cross-Validation**: Splitting training data into multiple folds to test stability across different data slices.
- **Hyperparameter Tuning**: Finding the best model settings using Grid Search (checking all options) or Random Search (sampling options).
- **Underfitting vs Overfitting**:
  - **Underfitting**: Model is too simple; performs poorly on both training and test data.
  - **Overfitting**: Model memorized training noise; performs great on training data but poorly on test data.

---

## Step 8: Model Deployment
> **What we do in this step**: We serialize trained models into portable file formats (.pkl, .joblib) and host them on production servers using REST APIs (FastAPI/Flask) for real-time predictions or scheduled scripts for batch processing.

- **Model Saving**: Exporting trained model files (`.pkl` or `.joblib`).
- **Serving Types**:
  - **Batch Serving**: Running predictions periodically in bulk (e.g., nightly database job).
  - **Real-Time Serving**: Exposing the model via a Web API (FastAPI, Flask) for instant predictions.

---

## Step 9: Monitoring & Maintenance (MLOps)
> **What we do in this step**: We set up continuous tracking of production predictions to detect Data Drift (changes in incoming data distribution) or Concept Drift (changes in real-world logic), triggering automated retraining pipelines when performance drops.

- **Data Drift**: Real-world input data distribution changes over time (e.g., new customer demographics).
- **Concept Drift**: The relationship between inputs and outputs changes (e.g., shopping habits post-event).
- **Retraining**: Automatically re-run the pipeline on fresh data when performance drops or drift is detected.