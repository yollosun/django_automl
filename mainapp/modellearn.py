import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor


def choose_target_variable(path_to_csv):
    df = pd.read_csv(path_to_csv, nrows=1)
    return "Выберите целевую переменную: ", df.columns



def main_function(path_to_csv, target_variable):
    df = pd.read_csv(path_to_csv)
    X_train, X_test, y_train, y_test, target_variable_series = split_test_train(df, target_variable)
    X_train = fill_nan(X_train, X_train)
    X_train = categorical_processing(X_train)

    type_of_task, y_train = type_of_learn(target_variable_series, y_train)
    if type_of_task == 'classification':
        logreg = logistic_regression(X_train, y_train)
        rf = RandomForestClas(X_train, y_train)
        X_test = fill_nan(X_test, X_train)
        X_test = categorical_processing(X_test)
        y_predicted_reg = logreg.predict(X_test)
        y_predicted_rf = rf.predict(X_test)
    else:
        logreg = linear_regression(X_train, y_train)
        rf = RandomForestReg(X_train, y_train)
        X_test = fill_nan(X_test, X_train)
        X_test = categorical_processing(X_test)
        y_predicted_reg = logreg.predict(X_test)
        y_predicted_rf = rf.predict(X_test)
    return {"reg":y_predicted_reg, 'rf':y_predicted_rf, "train":X_train, "test":X_test}

def split_test_train(df,target_variable):
    print('split_test_train')
    target_variable_series = df[target_variable]
    if target_variable_series.dtypes == 'object':
        most_frequent_value = target_variable_series.value_counts().index[0]
        target_variable_series = target_variable_series.fillna(most_frequent_value)
    else:
        target_variable_series =target_variable_series.fillna(target_variable_series.median())
    df = df.drop([target_variable], axis=1)
    X_train, X_test, y_train, y_test = train_test_split(df, target_variable_series, test_size=0.2)
    return [X_train, X_test, y_train, y_test, target_variable_series]


def fill_nan(X, X_train):
    print('fill_nan')
    for i, j in zip(X.isna().sum(), X.columns):
        if i > 0:
            if X[j].dtypes == 'object':
                most_frequent_value = X[j].value_counts().index[0]
                X[j] = X[j].fillna(most_frequent_value)
            else:
                X[j] = X[j].fillna(X_train[j].median())

    return X


def categorical_processing(X):
    print('categorical_processing')
    for column in X.columns:
        if X[column].dtypes == 'object':
            if len(X[column].unique()) > 2 and len(X[column].unique()) < 12:
                X = pd.get_dummies(X, columns=[column])
            elif len(X[column].unique()) <= 2:
                unique = X[column].unique()
                for i in range(len(unique)):
                    X[column].mask(X[column] == unique[i], other=i, inplace=True)

    on_delete = []
    for column in X.columns:
        if X[column].dtypes == 'object':
            try:
                X[column] = X[column].apply(lambda x: int(x))
            except:
                on_delete.append(column)
        # удаляем ненужный мусор
        if len(X[column].unique()) == X.shape[0] or len(X[column].unique()) == 1:
            on_delete.append(column)
    X = X.drop(columns=on_delete)
    return X
def type_of_learn(target_variable_series, y_train):
    print('type_of_learn')
    if len(target_variable_series.unique()) == 2:
        if target_variable_series.dtypes == 'object':
            unique = target_variable_series.unique()
            for i in range(len(unique)):
                    y_train.mask(y_train == unique[i], other=i, inplace=True)
        type_of_learn = 'classification'
    else:
        type_of_learn = 'regression'
    if y_train.dtypes == 'object':
        y_train = y_train.apply(lambda x: int(x))
    return [type_of_learn, y_train]
#функции классификации
def logistic_regression(X_train, y_train):
    print('logistic_regression')
    logreg = LogisticRegression()
    logreg.fit(X_train, y_train)
    return logreg
def RandomForestClas(X_train, y_train):
    print('RandomForestClas')
    rf = RandomForestClassifier(n_estimators=20, max_depth=10)
    rf.fit(X_train, y_train)
    return rf
def linear_regression(X_train, y_train):
    print('linear_regression')
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    return lr
def RandomForestReg(X_train, y_train):
    print('RandomForestReg')
    rf = RandomForestRegressor(n_estimators=100, max_depth=7)
    rf.fit(X_train, y_train)
    print('end')
    return rf