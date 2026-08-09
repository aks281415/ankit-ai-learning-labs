# ML Fundamentals: Learning Types (Instance vs Model-Based) & EDA Guide

A comprehensive guide covering Instance vs Model-Based Learning, Data Preprocessing Rules, Bivariate/Multivariate EDA, and Correlation.

---

## Key Similarities & Fundamental Differences

```
                     RAW DATASET
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
  [Instance-Based Learning]   [Model-Based Learning]
  (e.g., K-Nearest Neighbors)  (e.g., Linear Regression)
            │                           │
  Data Preparation Needed?    Data Preparation Needed?
    Generally YES (Scaling)        Generally YES (Encoding/Scaling)
            │                           │
      Model Training?             Model Training?
      NO (Lazy Storage)           YES (Learns Parameters)
            │                           │
     What is Stored?             What is Stored?
  FULL Training Dataset       Learned Parameters / Model Structure
  (Data MUST be kept!)        (Data can often be discarded)
```

---

## 1. Data Preparation (Generally Required for BOTH)

> **Key Point**: Preprocessing is generally required in **both** approaches, but the exact steps depend on the specific algorithm being used.

- **For Model-Based Learning**: Categorical variables typically need encoding (e.g. One-Hot, Label, or Target Encoding — the choice depends on the algorithm and cardinality). Missing values should be handled, and feature scaling helps algorithms like gradient descent converge properly.
- **For Instance-Based Learning**: Feature scaling (e.g. `StandardScaler`) is **extremely critical**! Since distance metrics (like Euclidean Distance in KNN) are used, unscaled features with large ranges will completely dominate the distance calculations.

---

## 2. Model Training Difference

| Aspect | Instance-Based Learning | Model-Based Learning |
| :--- | :--- | :--- |
| **Is an explicit model trained?** | ❌ **NO**. There is no model-fitting phase (Lazy Learning). Data is simply memorized/indexed. | ✅ **YES**. Model learns parameters (e.g. weights, splits, centroids) by minimizing a Loss Function (Eager Learning). |
| **Training Time** | **Negligible** — Very little model-fitting work during training, though indexing/storing can still take some time. | **Varies by algorithm** — Can range from fast (e.g. simple Linear Regression) to very slow (e.g. large Neural Networks). |
| **Underlying Mechanism** | Remembers individual data instances directly. | Extracts abstract generalizations, rules, and learned parameters from data. |

---

## 3. Storing the Model & Memory Footprint

| Aspect | Instance-Based Learning | Model-Based Learning |
| :--- | :--- | :--- |
| **What MUST be stored?** | **The FULL (or subset of) Training Dataset MUST be kept in memory.** | **Learned parameters and model structure** (e.g. weights for Linear Regression, tree splits for Decision Trees, etc.). |
| **Can training data be deleted after setup?** | ❌ **NO**. Predictions directly rely on comparing new test queries against the saved training instances. | **Generally YES** for standard parametric models (e.g. Linear/Logistic Regression). Once parameters are learned, the original data is typically not needed for prediction. |
| **Memory Requirement** | **HIGH** (Grows as dataset size $N$ grows). | **Typically much LOWER** than retaining the full training dataset, though exact footprint depends on model complexity and algorithm. |
| **Prediction Speed** | **Slow** (Must compute distance against stored instances). | **Instant**

---

## 4. Exploratory Data Analysis (EDA): Bivariate & Multivariate Analysis

### Bivariate Analysis (2 Variables)

| Variable Pair | Best Plot / Chart | One-Liner Description |
| :--- | :--- | :--- |
| **Numerical vs Numerical** | `Scatter Plot` (or `Line Plot`) | Checks linear/non-linear relationship, trend, and correlation between two continuous numbers. |
| **Categorical vs Numerical** | `Box Plot` / `Violin Plot` / `Bar Plot` | Compares data distribution, median, spread, and outliers of a continuous number across categories. |
| **Categorical vs Categorical** | `Stacked / Grouped Bar Plot` / `Crosstab Heatmap` | Shows frequency count and proportion breakdown between two discrete categories. |

### Multivariate Analysis (3+ Variables)

| Variable Combination | Best Plot / Chart | One-Liner Description |
| :--- | :--- | :--- |
| **Numerical vs Numerical vs Categorical** | `Scatter Plot with Hue (Color)` | Shows relationship between two numbers while highlighting how a third category modifies the trend. |
| **Numerical vs Numerical vs Numerical** | `3D Scatter Plot` / `Bubble Chart` | Plots 2 numbers on X-Y axes and uses bubble size/depth to represent the 3rd numerical magnitude. |
| **All Numerical Features (All vs All)** | `Correlation Heatmap` / `Pair Plot` | Displays pairwise Pearson correlation matrix to quickly detect multicollinearity across all numbers. |
| **Multiple Categorical Features** | `Heatmap of Crosstab` / `Sunburst Chart` | Visualizes proportions, multi-level breakdowns, and flow relationships across multiple categorical variables. |

### Key Concept: Correlation ($r$)

- **Definition**: Measures the strength and direction of a linear relationship between two continuous variables ($X$ and $Y$). Range: $[-1.0, +1.0]$.
- **Positive ($+1.0$)**: As $X$ increases, $Y$ increases (e.g. Study Hours vs Exam Score).
- **Negative ($-1.0$)**: As $X$ increases, $Y$ decreases (e.g. Car Age vs Car Price).
- **Zero ($0.0$)**: No linear relationship (e.g. Shoe Size vs IQ Score).
- **Golden Rule**: **Correlation $\neq$ Causation** (Statistical association between 2 variables does NOT mean one directly causes the other).

---

## Summary Cheat Sheet for Interviews

1. **Both** instance-based and model-based learning require proper **Data Preparation & Feature Scaling**.
2. **Model-Based**: Trains learned parameters $\rightarrow$ Stores model structure $\rightarrow$ Original dataset can often be discarded.
3. **Instance-Based**: No parameter training $\rightarrow$ Must keep training dataset stored in memory to search during prediction.
4. **EDA Selection Rule**:
   - `Num vs Num` $\rightarrow$ Scatter Plot
   - `Cat vs Num` $\rightarrow$ Box Plot / Bar Plot
   - `Cat vs Cat` $\rightarrow$ Stacked Bar / Crosstab
   - `3+ Vars` $\rightarrow$ Scatter with Hue / Heatmap