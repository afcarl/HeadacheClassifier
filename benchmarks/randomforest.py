# Read csv into pandas frame
import matplotlib.pyplot as plt
import numpy as np
import sklearn
from pandas import read_csv, DataFrame
from sklearn.ensemble import RandomForestClassifier


def plot_confusion_matrix(cm, title='Confusion matrix'):
    fig = plt.figure()
    cm = np.divide(cm, len(cm))
    cm = np.divide(cm, np.matrix.sum(np.asmatrix(cm))).round(3)

    ax = fig.add_subplot(1, 1, 1)
    cax = ax.matshow(cm, cmap=plt.get_cmap('RdYlGn'))
    for (j, i), label in np.ndenumerate(cm):
        ax.text(i, j, label, ha='center', va='center')
    fig.colorbar(cax)
    plt.show()


def evaluate_random_forests(features_df, labels_df, n_folds=2):
    kf = sklearn.cross_validation.KFold(len(labels_df.index), n_folds=n_folds)

    confusion_matrices_folds = []

    for train, test in kf:
        X_train = DataFrame(features_df, index=train)
        X_test = DataFrame(features_df, index=test)
        y_train = DataFrame(labels_df, index=train)
        y_test = DataFrame(labels_df, index=test)

        rf = RandomForestClassifier(n_estimators=500, n_jobs=-1)
        rf.fit(X_train.values.tolist(), y_train['cat'].tolist())

        predicted_labels = []
        for index, vector in enumerate(X_test.values):
            predicted_labels.append(rf.predict(vector.reshape(1, -1))[0])

        y_test_np = y_test['cat']
        predicted_labels_np = np.array(predicted_labels)
        y_test_np = np.array(y_test_np)
        equal_positions = 1.0 * np.sum(predicted_labels_np == y_test_np)
        accuracy = equal_positions / len(predicted_labels)
        print accuracy

        # Save the confusion matrix for this fold and plot it
        confusion_matrix = sklearn.metrics.confusion_matrix(y_test_np, predicted_labels)
        confusion_matrices_folds.append(confusion_matrix)
        # plt.figure()
        # cm_normalized = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]

    #     Let's plot the confusion matrix of the avarage confusion matrix
    sum = confusion_matrices_folds[0] * 1.0
    for i in range(1, len(confusion_matrices_folds)):
        sum += confusion_matrices_folds[i]
    sum /= len(confusion_matrices_folds)
    plot_confusion_matrix(sum)


# TODO: De run code moet hier weg
columns = ['age', 'sex', 'chest pain type', 'resting blood pressure', 'serum cholestoral', 'fasting blood sugar', \
           'resting electrocardio', 'max heartrate', 'exercise induced angina', 'oldpeak', 'slope peak', \
           'number of vessels', 'thal', 'disease']

df = read_csv('../data/heart.dat', sep=' ')
# df = df.iloc[np.random.permutation(len(df))]
# df = df.reset_index(drop=True)
df.columns = columns

features_column_names = ['age', 'sex', 'chest pain type', 'resting blood pressure', 'serum cholestoral',
                         'fasting blood sugar', \
                         'resting electrocardio', 'max heartrate', 'exercise induced angina', 'oldpeak', 'slope peak', \
                         'number of vessels', 'thal']
# labels_column_names = 'disease'
column_names = ['age', 'sex', 'chest pain type', 'resting blood pressure', 'serum cholestoral', 'fasting blood sugar', \
                'resting electrocardio', 'max heartrate', 'exercise induced angina', 'oldpeak', 'slope peak', \
                'number of vessels', 'thal', 'disease']
df = df[column_names]
# df = df.drop(columns[:3], axis=1)
# df = df.drop(columns[4:7], axis=1)
# df = df.drop(columns[8:-1], axis=1)
labels_df = DataFrame()
labels_df['cat'] = df['disease'].copy()
features_df = df.copy()
features_df = features_df.drop('disease', axis=1)
features_column_names = features_df.columns

rf = RandomForestClassifier(n_estimators=50, n_jobs=-1)
rf.fit(DataFrame(features_df.values.tolist()), labels_df['cat'].tolist())
importances = rf.feature_importances_
std = np.std([tree.feature_importances_ for tree in rf.estimators_],
             axis=0)
indices = np.argsort(importances)[::-1]

# Print the feature ranking
print("Feature ranking:")

for f in range(DataFrame(features_df.values.tolist()).shape[1]):
    print("%d. feature %s [%d] (%f)" % (f + 1, features_column_names[indices[f]], indices[f], importances[indices[f]]))

# Plot the feature importances of the forest
plt.figure()
plt.title("Feature importances")
plt.bar(range(DataFrame(features_df.values.tolist()).shape[1]), importances[indices],
        color="r", yerr=std[indices], align="center")
plt.xticks(range(DataFrame(features_df.values.tolist()).shape[1]), indices)
plt.xlim([-1, DataFrame(features_df.values.tolist()).shape[1]])
plt.show()

evaluate_random_forests(features_df=features_df, labels_df=labels_df, n_folds=10)