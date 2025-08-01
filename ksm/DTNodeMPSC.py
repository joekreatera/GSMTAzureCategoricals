import pandas as pd
from random import random, sample
import numpy as np
import traceback
from numpy.random import default_rng
import warnings
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.semi_supervised import LabelSpreading, LabelPropagation
from sklearn.linear_model import LogisticRegression, RidgeClassifier
from sklearn.tree import DecisionTreeClassifier
import traceback
import time
import sklearn
from sklearn import manifold
from .SSLearnerLeafNN import SSLearnerLeaf
from sklearn.metrics.pairwise import  euclidean_distances
from .utils import pairwise_distances, print_numba_signatures


generator = default_rng()

def get_min(x):
    # print("tryinm to get min from " , x)
    try:
        return np.min(x)
    except:
        pass
    return 0.0
def get_max(x):
    try:
        return np.max(x)
    except:
        pass
    return 0.0


class DecisionTreeNodeV2:
    
    node_id = 0
    function_to_draw = None
    def __init__(self, node, index,labels_data,level = 0, is_leaf = False, dataset = None , hyper_params_dict = None,tree_id=0 ):
        self.id = DecisionTreeNodeV2.node_id 
        DecisionTreeNodeV2.node_id += 1
        self.parent = node
        self.instance_index = index
        self.right = None
        self.left = None
        self.level = level
        self.label_vector = None
        self.label_vector_mean = None
        self.right_centroid = None 
        self.left_centroid = None
        self.tree_id = tree_id
        self.labels = labels_data
        self.dataset = dataset
        #self.is_leaf = is_leaf
        self.hyper_params_dict = hyper_params_dict
        self.is_leaf = False
        #self.do_label_proc = random() > hyper_params_dict["eta"]
        if(is_leaf):
            self.set_leaf(True) # calculate the model 
        self.decision_columns = None
        self.decision_value = -1
        self.get_distance_values = None
        self.decision_column_value_tuple = None
        self.global_labels_distribution = None

    def set_global_labels_distribution(self, global_labels_distribution):
        self.global_labels_distribution = global_labels_distribution
        
        if(self.left is not None):
            self.left.set_global_labels_distribution(global_labels_distribution)
        if(self.left is not None):
            self.right.set_global_labels_distribution(global_labels_distribution)

    def set_decision_value(self, value):
        self.decision_value = value
        
    def set_decision_instance_values(self, get_distance_values):
        self.get_distance_values = get_distance_values
    
    def set_decision_column_and_value(self, col, val):
        self.decision_column_value_tuple = (col,val)
        
    def set_decision_columns(self, cols):
        self.decision_columns = cols
    
    def set_left_centroid(self, centroid):
        self.left_centroid = centroid
    
    def set_right_centroid(self, centroid):
        self.right_centroid = centroid
        
    def get_instance_index(self):
        return self.instance_index

    def set_decision_column(self, label, value):
        self.decision_column_label = label
        self.decision_column_value = value
    def set_left(self, node):
        self.left = node
    def set_right(self, node):
        self.right = node
        
    def fill_semisupervised(self):
        pass

    def draw_data_set(self, dataset=None, labelset = None):
        
        # print("-*********************2", dataset)
        a  = int(random()*1000)
        b=  int(random()*1000)
        #joined_labels = self.labels.loc[self.instance_index ].copy()
        
        #final_joined_labels = joined_labels[self.labels.columns[0]].map(str)
        for label in range(0, len(labelset.columns.array)):
            
            l = labelset.columns[label]
            example = dataset.copy()
            
            # print( example.columns)
            example["category"] = labelset[l]
            example = example.reset_index()
            xvars = example.columns[1:50]
            yvars = ['index']
            # DecisionTreeNodeV2.function_to_draw(example,xvars, yvars,f'output_leaf_parent_{b}_node_{a}_label_{l}.png')
    
            #final_joined_labels = final_joined_labels + joined_labels[l].map(str)
        #print(final_joined_labels)
        # final_joined_labels.loc[row.name] = 'new_one'
        #instances_to_get =  self.instance_index 
        #print(final_joined_labels)
        #example = self.dataset.loc[self.instance_index].copy()
        # example.loc[row.name] = row
        #example["category"] = final_joined_labels
        #example["one"] = 0
        #print(xvars)
        #print(example)
        
        
        
        
    def set_leaf(self, is_leaf):
        
        self.is_leaf = is_leaf
        
        # print the dataset with their labels... 
        
        """
        if(is_leaf):
            example = SSLearnerLeaf.complete_train_dataset.loc[self.instance_index, list(self.dataset.columns.array)]
            example["category"] = SSLearnerLeaf.complete_train_dataset.loc[self.instance_index,self.labels.columns[0]]
            #example.loc[ right_cluster , "category" ] = 1
            example = example.reset_index()
            xvars = example.columns[1:50] #  just a subset
            yvars=['index']
            example = example.loc[:] # to see only the same subset as cols
            DecisionTreeNodeV2.function_to_draw(example,xvars, yvars,f'output_leaf_node_{self.id}_{0}_alt.png')
        """    
        if(not is_leaf):
            return
        
        if(self.hyper_params_dict["use_complex_model"]):
        
            self.model = SSLearnerLeaf(hyper_params_dict=self.hyper_params_dict)
            
            # instance_space, label_space = 
            """
            if(is_leaf):
                this_df = SSLearnerLeaf.complete_train_dataset.loc[self.instance_index]
                labeled_index = self.labels.loc[self.instance_index]
                labeled_index = labeled_index[ labeled_index[self.labels.columns[0]] != -1 ].index
                this_df["supervised"] = 0
                this_df.loc[labeled_index, "supervised"] = 1
                a  = int(random()*1000)
                this_df.to_csv(f"./datasets_tests/e_ds_{a}.csv")
            """
            #labels = self.labels.loc[self.instance_index]
            #supervised_instances = labels[ labels[labels.columns[0]] != -1 ].index 
            self.model.set_dataset_indices(self.instance_index )
            #self.model.set_dataset_indices(supervised_instances )
            
            complete_labels = self.model.fit(self.dataset,self.labels, self.tree_id, self.level ) # , self.parent.decision_columns for the test of KNN 
            # self.draw_data_set(dataset=instance_space, labelset =label_space )

            # self.label_vector = np.array(complete_labels).mean(axis=0)
            self.label_vector_mean = np.array(complete_labels).mean(axis=1) # do not yse label_vector to set this, as this conflicts with a decision inside predict_with_proba
        else:
            dataset = self.labels.loc[self.instance_index]
            #print(dataset)
            supervised_instances = dataset[ dataset[dataset.columns[0]] != -1 ].index 
            labels = dataset.loc[ supervised_instances ]    
            #print(labels)
            label_vector = labels.to_numpy().mean(axis=0)
            #print(f'Label vector is {label_vector}')
            self.label_vector = label_vector
            self.label_vector_mean = label_vector
        
    def get_draw_repr(self):
        # print(f' exporting {self.id} parent : {self.parent.id if self.parent is not None else -1 }')
        me = self.id
        left = f'' if self.left is None else self.left.get_draw_repr()
        right = f'' if self.right is None else self.right.get_draw_repr()
        return me + '\n' + left + '\n' + right
    

    def get_structure_df(self, rules_list, depth, columns_subset = set() ):
        structure = {"left":None, "right":None}
        if( self.parent is not None):
            structure["parent_id"] = self.parent.id

        if self.left is not None:
            structure["left"] = self.left.id 
            self.left.get_structure_df(rules_list, depth, set(self.decision_columns).union( columns_subset )  )
        
        if self.right is not None: 
            structure["right"] = self.right.id 
            self.right.get_structure_df(rules_list, depth, set(self.decision_columns).union( columns_subset ) )

        # centroid = self.dataset.loc[self.instance_index].mean(axis=0)
        # structure["centroid"] = centroid
        #for col in self.dataset.columns:
        #    structure[f"c_{col}"] = centroid[col]

        structure["depth"] = depth + 1
        structure["index"] = list(self.instance_index.array)
        structure["index_count"] = len(self.instance_index.array)
        
        structure["node_id"] = self.id
        structure["tree_id"] = self.tree_id
       
        if( not self.is_leaf ):
            for cn in self.decision_columns:
                structure[cn] = 1
           

        structure["is_leaf"] = self.is_leaf
        
        structure["supervised"] = self.labels.loc[self.instance_index.array]
        df = structure["supervised"]
        structure["supervised"] = list(df[df[self.labels.columns[0]] > -1 ].index.array)
        structure["unsupervised"] = list(df[df[self.labels.columns[0]] == -1 ].index.array)

        structure["supervised_count"] = len(df[df[self.labels.columns[0]] > -1 ].index.array)
        structure["unsupervised_count"] = len(df[df[self.labels.columns[0]] == -1 ].index.array)
        
        counter = 0
        
        if( self.is_leaf): # includes transductive learning 
            arr = self.model.get_models_feature_importance()
            for i,a in zip(self.label_vector_mean, arr):
                structure[f"label_{counter}"] = i
                structure[f"model_{counter}"] = a
                counter += 1

            min_max_values = dict()
            for c in  columns_subset:
                data = self.dataset.loc[self.instance_index]
                min_max_values[c] = (data[c].min(), data[c].max())
                
            structure["mm_limits"] = min_max_values
            structure["pred_label_probs"] = self.label_vector_mean               
        
        rules_list.append(structure)


    def import_node(self, tree_id= 0, node_id = 0, nodes = None, folder="", params = None):
        self.id = node_id
        self.tree_id = tree_id
        self.hyper_params_dict = params
        #print("NODE ID , TREE_ID " , node_id , " // " , tree_id)
        if(nodes is not None):
            node_info = nodes[ (nodes["tree_id"] == tree_id) & (nodes["node_id"] == node_id)  ]

            self.is_leaf =   not (node_info["decision_columns"].astype(str).values[0]  != "nan")   
            #print(f"IS LEAF??? decision for {node_id} on {tree_id}", self.is_leaf , "   based : "  , node_info["decision_columns"].astype(str).values[0] ) 
            self.instance_index = pd.Index(eval(node_info["instance_index"].values[0] ))

            label_names = []

            for cn in nodes.columns:
                if( cn.find("model_") >= 0 ):
                    label_names.append( cn.replace("model_","") )

            self.labels = pd.DataFrame(columns=label_names)
            # print(self.labels)

            # now build the model!
            if( self.is_leaf ):
                self.model = SSLearnerLeaf(hyper_params_dict=self.hyper_params_dict)
                # generate sslearnerleaf build model for the label specific models loading
                self.model.import_model(node_info)
                print(f"model built for {node_id} on {tree_id}")
            else:
                self.decision_columns = eval( node_info["decision_columns"].astype(str).values[0] )
                self.left = DecisionTreeNodeV2(self, None, None,dataset=self.dataset, hyper_params_dict=self.hyper_params_dict, tree_id = tree_id, level=self.level+1 )
                self.left.import_node(tree_id=tree_id, node_id = node_info["left_id"].values[0] , nodes = nodes, folder=folder, params = params )
                
                self.right = DecisionTreeNodeV2(self, None, None,dataset=self.dataset, hyper_params_dict=self.hyper_params_dict, tree_id = tree_id, level=self.level+1 )
                self.right.import_node(tree_id=tree_id, node_id = node_info["right_id"].values[0] , nodes = nodes, folder=folder , params=params )
                
           
            
            #print(node_info.info())
            #print(self.instance_index )


        return 

    def export_node(self,  nodes_list, is_root = False, export_folder=""):
        
        n = None
        n = dict()
        n["is_root"] = is_root
        n["instance_index"] = self.instance_index.to_list()
        n["decision_columns"] = self.decision_columns
        n["node_id"] = self.id
        n["tree_id"] = self.tree_id
            
        # print(" node " , self.id , "  " , self.is_leaf )
        if( self.is_leaf ):
            n["is_leaf"] = True    
            nodes_list.append( n  )
            n["output_features"] = self.model.output_features_
            models_exported = self.model.export_model(export_folder,self.tree_id,self.id)
            
            t = 0
            for label,me in zip(self.labels.columns, models_exported):
                n[f"model_{label}"] = me
                n[f'threshold_{label}'] = self.model.thresholds[t]
                t += 1           
        else:
            n["is_leaf"] = True

            n["left_id"] = self.left.id
            n["right_id"] = self.right.id
            
            self.left.export_node(nodes_list , export_folder = export_folder)
            self.right.export_node(nodes_list,  export_folder = export_folder)
            nodes_list.append( n  )
            


    def get_structure(self, true_y_df):
        structure = {"left":None, "right":None}


        structure["left"] = None if self.left is None else self.left.get_structure(true_y_df)
        structure["right"] = None if self.right is None else self.right.get_structure(true_y_df)

        structure["depth"] = 1 + max( 0 if self.left is None else structure["left"]["depth"], 0 if self.right is None else structure["right"]["depth"] )
        structure["index"] = self.instance_index.array
        structure["node_id"] = self.id
        structure["tree_id"] = self.tree_id
        structure["columns"] = self.decision_columns
        structure["is_leaf"] = self.is_leaf

        structure["supervised"] = self.labels.loc[self.instance_index.array]
        df = structure["supervised"]
        structure["supervised"] = df[df[self.labels.columns[0]] > -1 ].index.array
        structure["unsupervised"] = df[df[self.labels.columns[0]] == -1 ].index.array
        
        return structure

    def predict_with_proba(self, row, original_labels=None, activations_list = None, explain_decisions = False, rule_explain_dict = None, labels_names=None ):
        #print(row)
        
        val = None 
        
        if( self.label_vector is not None):
            if(explain_decisions):
                step = len(rule_explain_dict) - row.shape()[0]
                rule_explain_dict[f"step_{step+1}"] = f"[{self.tree_id}_{self.node_id}] label_vector_all_simple_model:{np.where(self.label_vector >= 0.5,1,0)}"
            return np.where(self.label_vector >= 0.5,1,0) , self.label_vector
            
        if( self.decision_columns is not None): # this does not happens on leaves
            # print(self.decision_columns)
            val = row[self.decision_columns]
        #print(val)
        
        if( self.is_leaf ):
            # print( row.name , " arrived  to " , self.tree_id , " --> " , self.id )
            r = np.array([row.to_numpy()])
            pred, prob = self.model.predict_with_proba(r, self.global_labels_distribution)
            
            # print( row.name , " arrived  to " , self.tree_id , " --> " , self.id , " prob" , prob )
            
            if(explain_decisions):
                step = len(rule_explain_dict) - row.shape[0]
                #rule_explain_dict[f"step_{step+1}"] = f"[{self.tree_id}_{self.id}] model_decision:{pred}({prob})"
                rule_explain_dict[f"final_decision_node_id"] = f"{self.tree_id}_{self.id}"
                rule_explain_dict[f"final_decision"] = f"{pred}"
                rule_explain_dict[f"final_decision_probs"] = f"{prob}"


            if(activations_list is not None):
                # output id, tree id, predicted vector, real vector (should have original_labels set), TP FP TN FN count
                # ideally the label vector should be separated in columns. 
                # 
                activation = {'node_id':self.id , 'tree_id':self.tree_id}
                counter = 0
                for lpd, lpr in zip(pred, prob): 
                    activation[f"label_{counter}_pred"] = lpd
                    activation[f"label_{counter}_prob"] = lpr
                    activation[f"label_{counter}_real"] = original_labels[counter]
                    
                    label_title = f'label_{counter}' if labels_names is None else f'{labels_names[counter]}'
                    
                    if( lpd ==  original_labels[counter] ):    
                        if( lpd == 1):
                            activation[f"{label_title}_tp"] = 1
                            activation[f"{label_title}_tn"] = 0
                            activation[f"{label_title}_fp"] = 0
                            activation[f"{label_title}_fn"] = 0
                        if( lpd == 0):
                            activation[f"{label_title}_tp"] = 0
                            activation[f"{label_title}_tn"] = 1
                            activation[f"{label_title}_fp"] = 0
                            activation[f"{label_title}_fn"] = 0
                    if( lpd !=  original_labels[counter] ):
                        if( lpd == 1):
                            activation[f"{label_title}_tp"] = 0
                            activation[f"{label_title}_tn"] = 0
                            activation[f"{label_title}_fp"] = 1
                            activation[f"{label_title}_fn"] = 0
                        if( lpd == 0):
                            activation[f"{label_title}_tp"] = 0
                            activation[f"{label_title}_tn"] = 0
                            activation[f"{label_title}_fp"] = 0
                            activation[f"{label_title}_fn"] = 1      
                    counter += 1
                
                activations_list.append(activation)
            # pred = pred[0]
            return pred, prob
            
        
        left_side = self.dataset.loc[ self.left.instance_index , self.decision_columns ].to_numpy()
        right_side = self.dataset.loc[ self.right.instance_index , self.decision_columns ].to_numpy()

        lsmin  = np.apply_along_axis( get_min , 0, left_side).astype(np.float32)
        lsmax = np.apply_along_axis( get_max , 0, left_side).astype(np.float32)
        
        rsmin  = np.apply_along_axis( get_min , 0, right_side).astype(np.float32)
        rsmax = np.apply_along_axis( get_max , 0, right_side).astype(np.float32)
        
        
        try:
            total_min = np.min( np.array([lsmin,rsmin]) , axis = 0)
            total_max = np.max( np.array([lsmax,rsmax]) , axis = 0)
        except Exception as e:
            print("these are the cols --- " , self.decision_columns)
            print("rrrr- should be one vector--- " , lsmin)
            print("rrrrr- should be one vector--- " , rsmin)

            print(left_side)
            print(right_side)
            
            raise(e)

        # print("- should be one vector--- " , total_min)
        # print("+ should be one vector+++  " , total_max)
        
        # we should get the max and min distances here , or when it is leaf, and pass it to pairwise_distances
        # check what happens with numpy trying top get max of strings
        # we should change any np nans to 0. 
        # the total min and total max homologate the distances on the gower. Just used when the gower is on. 

        if( "loaded_categorical_dictionary" in self.hyper_params_dict ):
            cat_feats = self.hyper_params_dict["loaded_categorical_dictionary"]
        else:
            cat_feats = self.hyper_params_dict["categorical_dictionary"].get_categorical_features( self.decision_columns, arr_name_based=True )

        left_distances = pairwise_distances(  val.to_numpy().reshape(1,-1) , left_side ,metric=self.hyper_params_dict['distance_function'] , min_max_array = [total_min,total_max] , cat_features=cat_feats )
        right_distances = pairwise_distances(  val.to_numpy().reshape(1,-1) , right_side,metric=self.hyper_params_dict['distance_function'] , min_max_array =  [total_min,total_max]  , cat_features=cat_feats )
        # print_numba_signatures()
        
        if( explain_decisions ):
            # get the selected properties from test row, left min row and right min row 
            
            
            instanceL_values = left_side[np.argmin(left_distances)]
            instanceR_values = right_side[np.argmin(right_distances)]
            ld = np.min(left_distances) 
            rd = np.min(right_distances)

            # print(f":: {left_distances} \n {right_distances} indices {instanceL} {instanceR} ")
            #print(f":: {self.left.instance_index} indices {instanceL} {instanceR} ")
            
            symb = ">"
            w_l = False # won left
            if(ld < rd):
                w_l = True # won left
                symb = "<"
            
            c_i = 0
            v = val.to_numpy().reshape(1,-1)
            for col in self.decision_columns: # determine thje range/region of values to get here
                if(f'exp_{col}' not in rule_explain_dict):
                    rule_explain_dict[f'exp_{col}'] = []
                test_v = instanceL_values[c_i] if w_l else instanceR_values[c_i]

                if( v[0,c_i] < test_v ):
                    mod=False
                    
                    for i_index,prev_range in  zip(  range(0, len(rule_explain_dict[f'exp_{col}']) ) ,rule_explain_dict[f'exp_{col}']):
                        if(prev_range[1] == '<='):
                            mod = True # the range will be considered anyway
                            if(test_v > prev_range[2] ):
                                rule_explain_dict[f'exp_{col}'][i_index][2] = test_v
                                rule_explain_dict[f'exp_{col}'][i_index].append("e")
                    if not mod:
                        rule_explain_dict[f'exp_{col}'].append( [v[0,c_i] , '<=',test_v ] )
                else:
                    mod=False
                    
                    for i_index,prev_range in  zip(  range(0, len(rule_explain_dict[f'exp_{col}']) ) ,rule_explain_dict[f'exp_{col}']):
                        if(prev_range[1] == '>='):
                            mod = True # the range will be considered anyway
                            if(test_v < prev_range[2] ):
                                rule_explain_dict[f'exp_{col}'][i_index][2] = test_v
                                rule_explain_dict[f'exp_{col}'][i_index].append("e")
                    if not mod:
                        rule_explain_dict[f'exp_{col}'].append( [v[0,c_i] , '>=',test_v ] )
                
                c_i +=1
            step = len(rule_explain_dict) - row.shape[0]
            rule_explain_dict[f"step_{step+1}"] = f"{ld} {symb} {rd} -> {list(instanceL_values)} {list(instanceR_values)} cols: {self.decision_columns}"
            
        #print( np.min(left_distances) , " ============ " , np.min(right_distances) )
        if( np.min(left_distances) < np.min(right_distances) ):
            
            p1,p2 = self.left.predict_with_proba(row, original_labels=original_labels, activations_list=activations_list, explain_decisions = explain_decisions, rule_explain_dict=rule_explain_dict)
            return p1, p2
        p1, p2 = self.right.predict_with_proba(row, original_labels=original_labels, activations_list=activations_list, explain_decisions = explain_decisions, rule_explain_dict=rule_explain_dict)
        return p1, p2 
            
            
class DecisionTree:
    
    def set_truth_rate(self, tr):
        self.truth_rate = tr
    def get_truth_rate(self):
        return self.truth_rate
    def add_root_node(self,node):
        self.root = node
    def print_tree(self):
        print( self.root.print_node(0) )
    def classify(self, row):
        return self.root.decide(row)
    def read_tree(self, file):
        print("when reading file rebuild tree to classify")
    def get_id(self):
        return self.root.tree_id
    