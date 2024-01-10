## HDB Resale Price System

 The HDB Resale Price System is a python-based application designed to predict real-time resale price for a specified location. By utilising advanced machine learning models such as the Linear Regression and Random Forest, this system provides accurate forecasts for future public home prices. With comprehensive data integration that incorporates essential macroeconomic factors like the Consumer Price Index(CPI), the application offers users a holistic understanding of property price fluctuations. Hyperparameter tuning further enhances the performance and generalisation of the machine learning models, ensuring reliable predictions validated through extensive testing.


## Installation Guide:
The HDB Resale Price System is shipped as a complete package, follow these steps to install it:

Download the Zip File: 
Go to the provided download link and download the zip file containing all the necessary components, including datasets and ipynb file for the models

Extract the Zip File: 
After downloading, extract the content of the zip file to a preferred location on your computer 

Obtaining Dataset (if not shipped):
If the dataset is not included, you can obtain the required datasets here:
Resale flat transaction prices: https://data.gov.sg/dataset/resale-flat-prices

Consumer Price Index Dataset: https://www.singstat.gov.sg/find-data/search-by-theme/economy/prices-and-price-indices/latest-data

Graphical User Interface: The GUI link to our HDB resale price system is already hosted, and no installation is required. Please click on the link at the front page of the report to explore our HDB resale price system

https://resale-price-final-wujhysfbyrvtsjzlbohyfh.streamlit.app/

## Justification of used measures / methods:


Before Outlier Removal:

![image](https://github.com/samuelgjy/resale_price/assets/110824653/5032d2fb-17d4-4797-9530-a3ff6b18a7e3)

After Outlier Removal:

![image](https://github.com/samuelgjy/resale_price/assets/110824653/a8c83528-4f82-4e68-8a6d-415fc44abb4a)

## Random Forest:

![image](https://github.com/samuelgjy/resale_price/assets/110824653/9f1b0256-635f-4195-9276-faa912b853f9)

Random Forest (Out-Of-Bag) -R²: 0.966: 
Test data R² score: 0.966 (Approximately 96.6% of price variance explained)
Test data Spearman correlation: 0.979 (Strong positive monotonic relationship)
Test data Pearson correlation: 0.983 (Strong positive linear relationship)
Test data Mean Absolute Error: 20,966 (The average prediction error for this model is  approximately 20,966, which means, on average, the predicted HDB resale prices deviate by around $20,966 from the true prices. )

Random Forest (K-fold Cross Validation) - 
Test data R² score: 0.967 (Approximately 96.7% of price variance explained)
Test data Spearman correlation: 0.981 (Strong positive monotonic relationship)
Test data Pearson correlation: 0.984 (Strong positive linear relationship)
Test data Mean Absolute Error: 20,339 (The average prediction error for this model is  approximately 20,366, which means, on average, the predicted HDB resale prices deviate by around $20,366 from the true prices.)


## Feature Importance:

The analysis of feature importance in both Linear Regression and Random Forest models reveals that floor area and lease commence date significantly influence resale prices. Additionally, distance from MRT and flat type also demonstrate notable impacts on housing prices. The difference in feature importance arises because tree-based models like Random Forest measure importance based on the frequency of feature selection for splitting and the gain in purity achieved. Consequently, tree-based models tend to assign lower importance scores to categorical values. Notably, despite this variation in importance scoring, the Random Forest model outperforms Linear Regression in predictive accuracy for the given task.


![image](https://github.com/samuelgjy/resale_price/assets/110824653/caed3c20-ae58-4911-8f13-8c7aac177b29)

