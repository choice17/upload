## Export decision tree from model  

**Reference**  
* [LINK to reference](https://stackoverflow.com/questions/20224526/how-to-extract-the-decision-rules-from-scikit-learn-decision-tree)  


## Export to python code  

```python  
from sklearn.tree import _tree
# export tree to python https://stackoverflow.com/questions/20224526/how-to-extract-the-decision-rules-from-scikit-learn-decision-tree
def tree_to_code(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    print("int tree({}):".format(", ".join("int " + feature_names)))

    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            print("{}if {} <= {} {".format(indent, name, threshold))
            recurse(tree_.children_left[node], depth + 1)
            print ("{}} else { // if {} > {}".format(indent, name, threshold))
            recurse(tree_.children_right[node], depth + 1)
        else:
            print ("{}return {};".format(indent, np.argmax(tree_.value[node])))
    recurse(0, 1)
```  

## Export to C model  

```python  
from sklearn.tree import _tree
# export tree to python https://stackoverflow.com/questions/20224526/how-to-extract-the-decision-rules-from-scikit-learn-decision-tree
def tree_to_codeC(tree, feature_names):
    tree_ = tree.tree_
    feature_name = [
        feature_names[i] if i != _tree.TREE_UNDEFINED else "undefined!"
        for i in tree_.feature
    ]
    print("int tree({}):".format(", ".join(["int " + f for f in feature_names])))

    def recurse(node, depth):
        indent = "    " * depth
        if tree_.feature[node] != _tree.TREE_UNDEFINED:
            name = feature_name[node]
            threshold = tree_.threshold[node]
            // threshold = int(np.floor(threshold)) // <==== remove this for integer version
            print("{}if ({} <= {:d}) {{".format(indent, name, threshold))
            recurse(tree_.children_left[node], depth + 1)
            print ("{}}} else {{ // if {} > {:d}".format(indent, name, threshold))
            recurse(tree_.children_right[node], depth + 1)
            print("{}}}".format(indent))
        else:
            print ("{}return {};".format(indent, np.argmax(tree_.value[node])))
    recurse(0, 1)
```
 
