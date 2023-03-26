import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, roc_auc_score, f1_score, precision_score, recall_score
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder
from joblib import dump, load

data = pd.read_csv("data.csv", names = [f"feature_{str(x)}" for x in range(1,7)], index_col = False)
data.head()
data.info()

data.feature_6.value_counts().plot(kind="bar")

X, y = data.drop(columns = ['feature_6']), data['feature_6']

scaler = StandardScaler()
X = scaler.fit_transform(X, y)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=69)

lr = LogisticRegression(max_iter = 1000, random_state = 69)
lr.fit(X_train, y_train)

prediction = lr.predict(X_test)
print("accuracy:", accuracy_score(y_test, prediction))
print("F1 Score:", f1_score(y_test, prediction, average="macro"))
print("Precision Score:", precision_score(y_test, prediction, average="macro"))
print("Recall Score:", precision_score(y_test, prediction, average="macro"))

svm = SVC(C = 2**12, random_state=69)
svm.fit(X_train, y_train)

prediction = svm.predict(X_test)
print("accuracy:", accuracy_score(y_test, prediction))
print("F1 Score:", f1_score(y_test, prediction, average="macro"))
print("Precision Score:", precision_score(y_test, prediction, average="macro"))
print("Recall Score:", precision_score(y_test, prediction, average="macro"))

dt = DecisionTreeClassifier(max_features = 5, random_state=69)
dt.fit(X_train, y_train)

prediction = dt.predict(X_test)
print("accuracy:", accuracy_score(y_test, prediction))
print("F1 Score:", f1_score(y_test, prediction, average="macro"))
print("Precision Score:", precision_score(y_test, prediction, average="macro"))
print("Recall Score:", precision_score(y_test, prediction, average="macro"))

rf = RandomForestClassifier(n_estimators = 10,random_state=69)
rf.fit(X_train, y_train)

prediction = rf.predict(X_test)
print("accuracy:", accuracy_score(y_test, prediction))
print("F1 Score:", f1_score(y_test, prediction, average="macro"))
print("Precision Score:", precision_score(y_test, prediction, average="macro"))
print("Recall Score:", precision_score(y_test, prediction, average="macro"))

le = LabelEncoder()
y_train = le.fit_transform(y_train)

xgb = XGBClassifier(random_state=69)
xgb.fit(X_train, y_train)

predictions = xgb.predict(X_test)
predictions = le.inverse_transform(predictions)
print("accuracy:", accuracy_score(y_test, prediction))
print("F1 Score:", f1_score(y_test, prediction, average="macro"))
print("Precision Score:", precision_score(y_test, prediction, average="macro"))
print("Recall Score:", precision_score(y_test, prediction, average="macro"))

best_model = svm
dump(best_model, 'model.joblib') 