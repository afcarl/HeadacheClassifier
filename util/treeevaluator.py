from pandas import read_csv, DataFrame

import operator
import os
import sklearn
import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
import pandas as pd

from constructors.cartconstructor import CARTConstructor
from constructors.questconstructor import QuestConstructor
from constructors.c45orangeconstructor import C45Constructor
from constructors.treemerger import DecisionTreeMerger
from objects.decisiontree import DecisionTree
from objects.featuredescriptors import DISCRETE, CONTINUOUS


class TreeEvaluator(object):

    def __init__(self):
        pass

    def evaluate_trees(self, data, tree_constructors, n_folds=2):
        kf = sklearn.cross_validation.KFold(len(data.index), n_folds=n_folds)
        tree_confusion_matrices = {}
        labels_df = DataFrame()
        labels_df['cat'] = data['disease'].copy()
        data = data.drop('disease', axis=1)
        feature_vectors_df = data.copy()
        for train, test in kf:
            X_train = DataFrame(feature_vectors_df, index=train)
            X_test = DataFrame(feature_vectors_df, index=test)
            y_train = DataFrame(labels_df, index=train)
            y_test = DataFrame(labels_df, index=test)
            for tree_constructor in tree_constructors:
                tree = tree_constructor.construct_tree(X_train, y_train)
                tree.visualise(tree_constructor.get_name())
                predicted_labels = tree.evaluate_multiple(X_test)
                print tree_constructor.get_name(), predicted_labels
                if tree_constructor not in tree_confusion_matrices:
                    tree_confusion_matrices[tree_constructor] = [tree.plot_confusion_matrix(y_test['cat'].values.astype(str), predicted_labels)]
                else:
                    tree_confusion_matrices[tree_constructor].append(tree.plot_confusion_matrix(y_test['cat'].values.astype(str), predicted_labels))

        fig = plt.figure()
        tree_confusion_matrices_mean = {}
        counter = 1
        for tree_constructor in tree_constructors:
            tree_confusion_matrices_mean[tree_constructor] = np.zeros(tree_confusion_matrices[tree_constructor][0].shape)
            for i in range(n_folds):
                tree_confusion_matrices_mean[tree_constructor] = np.add(tree_confusion_matrices_mean[tree_constructor], tree_confusion_matrices[tree_constructor][i])
            tree_confusion_matrices[tree_constructor] = np.divide(tree_confusion_matrices_mean[tree_constructor], len(tree_confusion_matrices[tree_constructor]))
            tree_confusion_matrices[tree_constructor] = np.divide(tree_confusion_matrices_mean[tree_constructor], np.matrix.sum(np.asmatrix(tree_confusion_matrices_mean[tree_constructor]))).round(3)

            ax = fig.add_subplot(len(tree_constructors), 1, counter)
            cax = ax.matshow(tree_confusion_matrices[tree_constructor], cmap=plt.get_cmap('RdYlGn'))
            ax.set_title(tree_constructor.get_name())
            for (j,i),label in np.ndenumerate(tree_confusion_matrices[tree_constructor]):
                ax.text(i,j,label,ha='center',va='center')
            fig.colorbar(cax)
            counter += 1

        pl.show()



"""
np.random.seed(26101993)    # 84846513



# Read csv into pandas frame
# columns = ['buying', 'maint', 'doors', 'persons', 'lug_boot', 'safety', 'class']
columns = ['age', 'sex', 'chest pain type', 'resting blood pressure', 'serum cholestoral', 'fasting blood sugar', \
           'resting electrocardio', 'max heartrate', 'exercise induced angina', 'oldpeak', 'slope peak', \
           'number of vessels', 'thal', 'disease']
df = read_csv(os.path.join(os.path.join('..', 'data'), 'heart.dat'), sep=' ')
# df = read_csv(os.path.join(os.path.join('..', 'data'), 'car.data'), sep=',')
df.columns = columns

print len(np.unique(df['age']))
descriptors = [(DISCRETE, len(np.unique(df['age']))), (DISCRETE, len(np.unique(df['sex']))),
               (DISCRETE, len(np.unique(df['chest pain type']))), (CONTINUOUS), (CONTINUOUS),
               (DISCRETE, len(np.unique(df['fasting blood sugar']))),
               (DISCRETE, len(np.unique(df['resting electrocardio']))), (CONTINUOUS),
               (DISCRETE, len(np.unique(df['exercise induced angina']))), (CONTINUOUS),
               (DISCRETE, len(np.unique(df['slope peak']))), (DISCRETE, len(np.unique(df['number of vessels']))),
               (DISCRETE, len(np.unique(df['thal']))), (DISCRETE, len(np.unique(df['disease'])))]
# mapping_buy_maint = {'low': 0, 'med': 1, 'high': 2, 'vhigh': 3}
# mapping_doors = {'2': 0, '3': 1, '4': 2, '5more': 3}
# mapping_persons = {'2': 0, '4': 1, 'more': 2}
# mapping_lug = {'small': 0, 'med': 1, 'big': 2}
# mapping_safety = {'low': 0, 'med': 1, 'high': 2}
# mapping_class = {'unacc': 1, 'acc': 2, 'good': 3, 'vgood': 4}
# df['maint'] = df['maint'].map(mapping_buy_maint)
# df['buying'] = df['buying'].map(mapping_buy_maint)
# df['doors'] = df['doors'].map(mapping_doors)
# df['persons'] = df['persons'].map(mapping_persons)
# df['lug_boot'] = df['lug_boot'].map(mapping_lug)
# df['safety'] = df['safety'].map(mapping_safety)
# df['class'] = df['class'].map(mapping_class)
# permutation = np.random.permutation(df.index)
# df = df.reindex(permutation)
# df = df.reset_index(drop=True)
# df = df.head(300)

#features_column_names = ['resting blood pressure', 'serum cholestoral', 'max heartrate', 'oldpeak']
#feature_descriptors = [CONTINUOUS, CONTINUOUS, CONTINUOUS, CONTINUOUS]
#column_names = ['resting blood pressure', 'serum cholestoral', 'max heartrate', 'oldpeak', 'disease']
features_column_names = ['number of vessels', 'max heartrate', 'thal', 'chest pain type', 'serum cholestoral', 'age']
feature_descriptors = [(DISCRETE, len(np.unique(df['number of vessels']))), (CONTINUOUS,),
                       (DISCRETE, len(np.unique(df['thal']))), (DISCRETE, len(np.unique(df['chest pain type']))),
                       (CONTINUOUS, ), (DISCRETE, len(np.unique(df['age'])))]
column_names = ['number of vessels', 'max heartrate', 'thal', 'chest pain type', 'serum cholestoral', 'age', 'disease']
df = df[column_names]
labels_df = DataFrame()
labels_df['cat'] = df['disease'].copy()
features_df = df.copy()
features_df = features_df.drop('disease', axis=1)
features_df = features_df/features_df.max()

print features_df

permutation = np.random.permutation(features_df.index)
features_df = features_df.reindex(permutation)
features_df = features_df.reset_index(drop=True)
labels_df = labels_df.reindex(permutation)
labels_df = labels_df.reset_index(drop=True)

train_features_df = features_df.head(int(0.8*len(features_df.index)))
test_features_df = features_df.tail(int(0.2*len(features_df.index)))
train_labels_df = labels_df.head(int(0.8*len(labels_df.index)))
test_labels_df = labels_df.tail(int(0.2*len(labels_df.index)))


c45 = C45Constructor()
cart = CARTConstructor(min_samples_leaf=3)
quest = QuestConstructor()
tree_constructors = [c45, cart, quest]

evaluator = TreeEvaluator()
#evaluator.evaluate_trees(df, tree_constructors)
merger = DecisionTreeMerger()
regions_list = []
constructed_trees = []
for tree_constructor in tree_constructors:
    tree = tree_constructor.construct_tree(train_features_df, train_labels_df)
    tree.populate_samples(train_features_df, train_labels_df['cat'])
    #tree.visualise(os.path.join(os.path.join('..', 'data'), tree_constructor.get_name()))
    regions = merger.decision_tree_to_decision_table(tree, train_features_df)
    regions_list.append(regions)
    constructed_trees.append(tree)
    # merger.plot_regions("rect_"+tree_constructor.get_name()+".png", regions, ['1', '2'], features_column_names[0],
    #                     features_column_names[1], x_max=np.max(features_df[features_column_names[0]].values),
    #                     y_max=np.max(features_df[features_column_names[1]].values),
    #                     x_min=np.min(features_df[features_column_names[0]].values),
    #                     y_min=np.min(features_df[features_column_names[1]].values))
feature_mins = {}
feature_maxs = {}

for feature in features_column_names:
    feature_mins[feature] = np.min(train_features_df[feature])
    feature_maxs[feature] = np.max(train_features_df[feature])


merged_regions = merger.calculate_intersection(regions_list[0], regions_list[2], features_column_names, feature_maxs,
                                               feature_mins)
merged_regions = merger.calculate_intersection(merged_regions, regions_list[1], features_column_names, feature_maxs,
                                               feature_mins)
samples_df = merger.generate_samples(merged_regions, features_column_names, feature_descriptors)

# merger.plot_regions_with_points("rect_with_points.png", merged_regions, ['1', '2'], features_column_names[0],
#                                 features_column_names[1], samples_df,
#                                 x_max=np.max(features_df[features_column_names[0]].values),
#                                 y_max=np.max(features_df[features_column_names[1]].values),
#                                 x_min=np.min(features_df[features_column_names[0]].values),
#                                 y_min=np.min(features_df[features_column_names[1]].values))

new_labels_df = DataFrame()
new_labels_df['cat'] = samples_df['cat'].copy()
new_features_df = samples_df.copy()
new_features_df = new_features_df.drop('cat', axis=1)
new_features_df = new_features_df.astype(float)

print new_features_df

cart_new = CARTConstructor(min_samples_leaf=1)
c45_new = C45Constructor(cf=1.0)
new_tree = c45_new.construct_tree(new_features_df, new_labels_df)
new_tree.visualise(os.path.join(os.path.join('..', 'data'), "new_tree"))
"""
"""
new_tree = merger.regions_to_tree(train_features_df, train_labels_df, merged_regions, features_column_names, feature_mins, feature_maxs)
new_tree.visualise(os.path.join(os.path.join('..', 'data'), 'new_tree'))
"""
"""
trees = [constructed_trees[0], constructed_trees[1], constructed_trees[2], new_tree]

tree_confusion_matrices = {}
for tree in trees:
    predicted_labels = tree.evaluate_multiple(test_features_df)
    if tree not in tree_confusion_matrices:
        tree_confusion_matrices[tree] = [tree.plot_confusion_matrix(test_labels_df['cat'].values.astype(str), predicted_labels.astype(str))]
    else:
        tree_confusion_matrices[tree].append(tree.plot_confusion_matrix(test_labels_df['cat'].values.astype(str), predicted_labels.astype(str)))

fig = plt.figure()
tree_confusion_matrices_mean = {}
counter = 1
for tree in trees:
    tree_confusion_matrices_mean[tree] = np.zeros(tree_confusion_matrices[tree][0].shape)
    for i in range(len(tree_confusion_matrices[tree])):
        tree_confusion_matrices_mean[tree] = np.add(tree_confusion_matrices_mean[tree], tree_confusion_matrices[tree][i])
    tree_confusion_matrices[tree] = np.divide(tree_confusion_matrices_mean[tree], len(tree_confusion_matrices[tree]))
    tree_confusion_matrices[tree] = np.divide(tree_confusion_matrices_mean[tree], np.matrix.sum(np.asmatrix(tree_confusion_matrices_mean[tree]))).round(3)

    ax = fig.add_subplot(len(trees), 1, counter)
    cax = ax.matshow(tree_confusion_matrices[tree], cmap=plt.get_cmap('RdYlGn'))
    for (j,i),label in np.ndenumerate(tree_confusion_matrices[tree]):
        ax.text(i,j,label,ha='center',va='center')
    fig.colorbar(cax)
    counter += 1

pl.show()
"""

# Read csv into pandas frame
columns = ['PassengerId','Survived','Pclass','Name','Sex','Age','SibSp','Parch','Ticket','Fare','Cabin','Embarked']
df = read_csv(os.path.join(os.path.join('..', 'data'), 'titanic_train.csv'), sep=',')
df.columns = columns

useful_df = df[['Survived', 'Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']]
useful_df = useful_df.dropna()

train_features_df = useful_df[['Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']].copy()
train_labels_df = useful_df[['Survived']].copy()
train_labels_df.columns = ['cat']
train_labels_df = train_labels_df.reset_index(drop=True)

mapping_sex = {'male': 1, 'female': 2}
mapping_embarked = {'C': 1, 'Q': 2, 'S': 3}
train_features_df['Sex'] = train_features_df['Sex'].map(mapping_sex)
train_features_df['Embarked'] = train_features_df['Embarked'].map(mapping_embarked)

train_features_df = train_features_df/train_features_df.max()
train_features_df = train_features_df.reset_index(drop=True)

c45 = C45Constructor()
cart = CARTConstructor(min_samples_leaf=3)
quest = QuestConstructor()
tree_constructors = [c45, cart, quest]
merger = DecisionTreeMerger()
regions_list = []
constructed_trees = []
for tree_constructor in tree_constructors:
    tree = tree_constructor.construct_tree(train_features_df, train_labels_df)
    tree.populate_samples(train_features_df, train_labels_df['cat'])
    #tree.visualise(os.path.join(os.path.join('..', 'data'), tree_constructor.get_name()+"_titanic"))
    regions = merger.decision_tree_to_decision_table(tree, train_features_df)
    regions_list.append(regions)
    constructed_trees.append(tree)

features_column_names = ['Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']
feature_descriptors = [(DISCRETE, len(np.unique(train_features_df['Pclass']))),
                       (DISCRETE, len(np.unique(train_features_df['Sex']))),
                       (DISCRETE, len(np.unique(train_features_df['Age']))),
                       (DISCRETE, len(np.unique(train_features_df['SibSp']))),
                       (CONTINUOUS, ), (DISCRETE, len(np.unique(train_features_df['Embarked'])))]
feature_mins = {}
feature_maxs = {}

for feature in features_column_names:
    feature_mins[feature] = np.min(train_features_df[feature])
    feature_maxs[feature] = np.max(train_features_df[feature])

merged_regions = merger.calculate_intersection(regions_list[0], regions_list[2], features_column_names, feature_maxs,
                                               feature_mins)
merged_regions = merger.calculate_intersection(merged_regions, regions_list[1], features_column_names, feature_maxs,
                                               feature_mins)
"""
samples_df = merger.generate_samples(merged_regions, features_column_names, feature_descriptors)

print samples_df
new_labels_df = DataFrame()
new_labels_df['cat'] = samples_df['cat'].copy()
new_features_df = samples_df.copy()
new_features_df = new_features_df.drop('cat', axis=1)
new_features_df = new_features_df.astype(float)
"""
new_tree = merger.regions_to_tree(train_features_df, train_labels_df, merged_regions, features_column_names, feature_mins, feature_maxs)

constructed_trees.append(new_tree)

columns = ['PassengerId','Pclass','Name','Sex','Age','SibSp','Parch','Ticket','Fare','Cabin','Embarked']
df = read_csv(os.path.join(os.path.join('..', 'data'), 'titanic_test.csv'), sep=',')
df.columns = columns

test_features_df = df[['PassengerId', 'Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']]
test_features_df['Sex'] = test_features_df['Sex'].map(mapping_sex)
test_features_df['Embarked'] = test_features_df['Embarked'].map(mapping_embarked)
print test_features_df
test_features_df[['Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']] = test_features_df[['Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']]/test_features_df[['Pclass', 'Sex', 'Age', 'SibSp', 'Fare', 'Embarked']].max()
print test_features_df

columns = ['PassengerId', 'Survived']
submission_c45 = DataFrame(columns=columns)
submission_cart = DataFrame(columns=columns)
submission_quest = DataFrame(columns=columns)
submission_merge = DataFrame(columns=columns)

for i in range(len(test_features_df.index)):
    sample = test_features_df.loc[i]
    submission_c45.loc[len(submission_c45)] = [int(sample['PassengerId']), constructed_trees[0].evaluate(sample)]
    submission_cart.loc[len(submission_cart)] = [int(sample['PassengerId']), constructed_trees[1].evaluate(sample)]
    submission_quest.loc[len(submission_quest)] = [int(sample['PassengerId']), constructed_trees[2].evaluate(sample)]
    submission_merge.loc[len(submission_merge)] = [int(sample['PassengerId']), constructed_trees[3].evaluate(sample)]

submission_c45.to_csv('submission_c45', index=False)
submission_cart.to_csv('submission_cart', index=False)
submission_quest.to_csv('submission_quest', index=False)
submission_merge.to_csv('submission_merge', index=False)


