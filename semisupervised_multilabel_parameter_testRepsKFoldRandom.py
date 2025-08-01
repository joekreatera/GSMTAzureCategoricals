import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from  ksm.SSMLKVForestPredictorMPSC import SSMLKVForestPredictor
# from sklearn.model_selection import KFold

from ksm.DownloadHelper import *
from sklearn.model_selection import train_test_split
from sklearn.metrics import average_precision_score, accuracy_score, classification_report, multilabel_confusion_matrix
from sklearn.metrics import label_ranking_average_precision_score
from random import random
from random import randint
from sklearn.metrics import roc_auc_score
# from sklearn.model_selection import GridSearchCV
from ksm.roc_auc_reimplementation import roc_auc as roc_auc_score
from sklearn.metrics import make_scorer
# from sklearn.model_selection import ParameterGrid
from ksm.utils import get_metrics,multilabel_train_test_split, get_features, save_report, multilabel_kfold_split, generate_explainable_datasets
import sys
# from sklearn.preprocessing import StandardScaler, QuantileTransformer, Normalizer
# from ksm.UD3_5Clustering import UD3_5Clustering
import os
import platform
import warnings

from matplotlib.colors import hsv_to_rgb
import seaborn as sns

from ksm.explainability import generate_explainability_files

import multiprocessing as mp
warnings.filterwarnings("ignore")


prefix = './'

input_path = prefix + 'datasets'
output_path = os.path.join(prefix, 'results')
model_path = os.path.join(prefix, 'results')
training_path = input_path




def custom_precision_score(y_true,y_pred, estimator = None):
    y_true = y_true.to_numpy()
    r = roc_auc_score(y_true, y_pred, average='micro')
    
    nm = f'results_{estimator.alpha}_{estimator.beta}_{estimator.gamma}_{estimator.alpha_prime}_{estimator.trees_quantity}_{estimator.leaf_relative_instance_quantity}_.txt'
    save_report('./', nm, y_true = y_true, y_predicted_proba = y_pred)
    
    return r


def calculate_parameters(params_dict):
    params = dict()

    for p in params_dict:
        
        item = params_dict[p]
        
        if(type(item) is tuple):

            tp = item[0]
            mn = item[1]
            mx = item[2]
            if(tp == int):
                params[p] = randint(mn,mx)
            if(tp == float):
                params[p] = mn + (mx-mn)*random()
        elif(type(item) is list):
            if(type(item[0]) is tuple): # is a list of random parameters
                params[p] = []
                for idx in range(len(item)):
                    tp = item[idx][0]
                    mn = item[idx][1]
                    mx = item[idx][2]
                    params[p].append( mn + (mx-mn)*random() )
            else:
                params[p] = item[randint(0,len(item)-1)]
        else:
            params[p] = item # fixed to a value
    return params

def train():
    # for linux platforms, could be forkserver, fork, spawn.... forkserver works in mac
    if( sys.platform.find('linux') > -1 ):
        mp.set_start_method('spawn') # tried all in ubuntu... forkserver eventually had a broken pipe error. 
    ds_name = "amphibians" # changed specs recently for explain tests... original parameters are overriden only. 

    print("Cpus " , mp.cpu_count() )
    print("Info " , platform.processor() )
    print("Sys " , sys.version_info )
    
    total_jobs = 8
    ds_configs = {
    "emotions":6, # multilabel
    "yeast_multi":14, # multilabel
    "birds":19,
    'flags':7,
    'cal500':174,
    'slashdot':21,
    'enron':53,
    'water':14,
    'medical':45,
    'foodtruck':12,
    'plantgo':12,
    'eukaryote':22,
    'genbase':27,
    'gonegative': 8,
    'humanpse': 14,
    'plantpse':12,
    '3sourcesbbc':6,
    'chd49':6,
    'mediamill':101,
    'scene':6,
    'image':5,
    'flagscat':7,
    'fifa':26,
    'amphibians':7,
    'divorce':10,
    'nursery':3,
    }
    # getFromOpenML will convert automatically the classes found to a mutually exclusive multilabel
    print(training_path)
    dataset = getFromOpenML(ds_name,version="active",ospath=training_path+'/', download=False, save=False)

    #dataset = getFromOpenML(ds_name+'-train',version="active",ospath='datasets/', download=False, save=False)
    # test_dataset = getFromOpenML(ds_name+'-test',version="active",ospath='datasets/', download=False, save=False)
    print("Dataset memory usage BEFORE conversion" , dataset.memory_usage(index=True).sum() )
   
    
    #if(ds_name == 'emotions'):
        # print(dataset)
    #    dataset["col_65"] = dataset["col_65"].astype(str)
    #    dataset["col_67"] = dataset["col_67"].astype(str)
    #    dataset["col_68"] = dataset["col_68"].astype(str)

    # multilabel_dataset = transform_multiclass_to_multilabel(dataset, "label_0") # will expand label_0 to the unique values , mutually exclusive as labels
    label_columns = [f"label_{i}" for i in range(0,ds_configs[ds_name])]  # for iris (3) ,for yeast(10) for ecoli(8), satimage(6)
    # convert dataframe to its minimum size possible
    for label in label_columns:
        dataset[label] = pd.to_numeric( dataset[label] , downcast="unsigned" )

    a = 3
    for col in get_features(dataset, label_columns):
        if(dataset[col].dtype == 'float64'):
            dataset[col] = pd.to_numeric( dataset[col] , downcast="float" )

        if(dataset[col].dtype == 'int64'):
            dataset[col] = pd.to_numeric( dataset[col] , downcast="float" )


        
        if( random() > 0.3): # test the other meth
            a = 1
        if dataset[col].nunique() < a: # this could change regarding the dataset, for experiments we could try both, or leave it equal to 0
            dataset[col]  =  dataset[col].astype(str)

    print("Dataset memory usage AFTER conversion" , dataset.memory_usage(index=True).sum() )
    #unique_values_count = dataset.nunique() # different values on each column 
    #unique_values_count = set(unique_values_count[unique_values_count < 4].index).difference(  set(label_columns) )
    #for v in unique_values_count:
    #    dataset[v] = dataset[v].astype(str)
    
    # print(unique_values_count)
    # exit()od on some

    # alpha is used for the ridge classifier 
    # gamma is used for the label spreading 
    # alpha prime is used for label_spreading alpha 
    # beta is used to control the amount of ridge 

    alpha_collection = [50,100]
    alpha_prime_collection = [0.3,0.7]
    beta_collection = [0.3,0.5,0.7] 
    gamma_collection = [50,100]
    trees_collection = [50,100]
    leafs_collection = [0.05,0.1,0.15]


    # alpha is used for the ridge classifier 
    # gamma is used for the label spreading 
    # alpha prime is used for label_spreading alpha 
    # beta is used to control the amount of ridge 
    # parameters = {'trees_quantity':1,'alpha':-1.0, 'C':10, 'eta':0.25, 'gamma':0.001,"M_groups":2, "N_attr":6, 'leaf_relative_instance_quantity':0.05 }
    #parameters = {'trees_quantity':10,'alpha':-1.0, 'C':1 , 'eta':0.01, 'gamma':4,"M_groups":5, "N_attr":15, 'leaf_relative_instance_quantity':0.10, 'scaler':scaler }
    scaler = None
    parameters = {'p':[.4,.1,.1,.4], 'q':[.5,.3,.2], 'trees_quantity':10,'alpha':-1.0, 'C':1 , 'eta':0.01, 'gamma':4,"M_groups":5, "N_attr":15, 'leaf_relative_instance_quantity':0.10, 'scaler':scaler, 'do_ranking_split':False }
    gamma_collection = [1] # altamente dependiente del dataset ooooo , es necesario escalarlo todo
    trees_collection = [50]
    leafs_collection = [0.05]
    m_collection  = [15] # groups, normally we user 8,14,20
    n_collection  = [128,512] # attributes ... 1,20,40,60,80
    scaler_collection = [None]
    do_ranking_split_collection = [True]
    p_collection = [[0.70,0.06,0.06,0.06,0.06,0.06]]
    complex_model_collection = [True] # missing True
    leaves_max_depth_collection = [6] # was 3, changed for a new set
    leaves_min_samples_split_collection = [6]
    leaves_min_samples_leaf_collection = [4]
    leaves_max_features_collection = ['sqrt'] # 'sqrt'
    leaves_SS_N_reps_collection = [7]
    leaves_SS_M_attributes_collection = [15] # it is lineal
    distance_function_collection = ['gower']
    leaves_RF_estimators_collection = [7]
    output_tree_sets_collection = [False]
    depth_limit_collection = [5]
    bagging_collection = [1.00]
    # parameters = {'trees_quantity':10,'alpha':10, 'beta':0.2, 'alpha_prime':0.5, 'gamma':10,'leaf_relative_instance_quantity':0.1 }
    
    

    parameters = {
    'a_r':a,    
    'trees_quantity':(int, 10,130), # 20- 130
    "M_groups":(int,20,120), # 35 - 120 
    "N_attr":(int, 2**5-1 , 2**16+1 ),
    'leaf_relative_instance_quantity':(float,0.05,0.17), 
    'scaler': None,
    'do_ranking_split':True,
    'p':[
        (float, 0,1),
        (float, 0,1),
        (float, 0,1),
        (float, 0,1),
        (float, 0,1),
        (float, 0,1),
        (float, 0,1)],
    'use_complex_model':True,
    'leaves_max_depth': (int,5,12),
    'leaves_min_samples_split':(int, 4,10),
    'leaves_min_samples_leaf':(int, 2,9), 
    'leaves_max_features':'sqrt',
    'leaves_SS_N_reps':(int,10,60),
    'leaves_SS_M_attributes':(int, 3,16), # they cannot be too large. tried with 40. 
    'distance_function':'gower',
    'leaves_RF_estimators':(int, 7,20),
    'output_tree_sets':False,
    'm_iterations':(int, 40,200),
    'bagging_pct':(float, 0.60, 0.90),
    'depth_limit': (int,0,10), # 4 and 20 originally, 0-16
    "output_quality":False
    }

    
    
    
    #param_grid = ParameterGrid(parameters)

    final_list = []

    i = 0
    test_size = .30
    k_fold = 10
    unlabeled_ratio = .70

    train_set,test_set = multilabel_train_test_split(dataset, test_size=test_size, random_state=180, stratify=dataset[label_columns]) # .05 for the CLUS test as it was with train and test datasets
    

    train_set.reset_index(drop=True, inplace=True)
    test_set.reset_index(drop=True , inplace=True)
    
    best_label_rank = 0

    #for parameters in list(param_grid): # it was 3 for original experiment.
    for i in range(1):
        params = calculate_parameters(parameters)
        #print("!!!!!!!!!!!!!! \n \n \n NOT USING PARAMETER COMBINATION  !!!!!!!!!!  \n\n\n\n\n !!!!!!!!!!!! \n ")
        #params = parameters

        print(params)
        auprc_curve = 0
        label_rank_average_precision = 0
        average_precision = 0
        auc_micro = 0
        auc_macro = 0
        hamming_loss = 0
        accuracy = 0

        instance_columns = get_features(train_set, label_columns)

        folds = multilabel_kfold_split(n_splits=k_fold, shuffle=True, random_state= 180)
        fold = -1

        if(True): # go directly to final predictor
            for train_index, test_index in folds.split(train_set[instance_columns], train_set[label_columns] ):
                fold += 1
                print("On fold " , fold , "------>",len(train_index), "    " , len(train_set.index))
                k_train_set = train_set.loc[train_index]
                k_test_set = train_set.loc[test_index] 
                # multilabel_train_test_split(train_set, test_size=1/k_fold, random_state=180+fold, stratify=train_set[label_columns]) # .05 for the CLUS test as it was with train and test datasets
                labeled_instances, unlabeled_instances =  multilabel_train_test_split(k_train_set, test_size=unlabeled_ratio, random_state=141, stratify=k_train_set[label_columns]) # simulate unlabeled instances
                X = k_train_set[instance_columns]        
                y = k_train_set[label_columns]
                predictor = SSMLKVForestPredictor(
                                            unlabeledIndex=unlabeled_instances.index,
                                            tag=ds_name,
                                            hyper_params_dict = params,
                                            is_multiclass = False,
                                            do_random_attribute_selection = True, # wont be needed for this one
                                            njobs=total_jobs
                                            )                 
                predictor.fit(X,y)
                y_true = k_test_set[label_columns].to_numpy()
                x_test = k_test_set[instance_columns]
        
                predictions, probabilities = predictor.predict_with_proba(x_test) #y_true = y_true

                # print( predictor.get_tree_structure(y_true) )
                results_pred = pd.DataFrame(predictions)
                results_prob = pd.DataFrame(probabilities)
                results_true = pd.DataFrame(y_true)

                metrics = get_metrics(y_true, predictions, probabilities) 
                auprc_curve += metrics["auprc_curve"]
                label_rank_average_precision+= metrics["label_rank_average_precision"]
                average_precision+= metrics["average_precision"]
                auc_micro+= metrics["auc_micro"]
                auc_macro+= metrics["auc_macro"]
                hamming_loss+= metrics["hamming_loss"]
                accuracy+= metrics["accuracy"]   
                print("AUPRC" , metrics["auprc_curve"])
                print("LR" , metrics["label_rank_average_precision"])
                print("AUC" , metrics["auc_macro"]) 

        # one last time
        # we are not selecting the best one, yet. Just exploring the space with random. 
        labeled_instances, unlabeled_instances =  multilabel_train_test_split(train_set, test_size=unlabeled_ratio, random_state=141, stratify=train_set[label_columns]) # simulate unlabeled instances
        X = train_set[instance_columns]
        y = train_set[label_columns] 

        #print(y)
        labels_distrib = y.mean(axis=0)
        labels_distrib_supervised = y.loc[labeled_instances.index].mean(axis=0)
        predictor = SSMLKVForestPredictor(
                                unlabeledIndex=unlabeled_instances.index,
                                tag=ds_name,
                                hyper_params_dict = params,
                                is_multiclass = False,
                                do_random_attribute_selection = True, # wont be needed for this one
                                njobs=total_jobs # for mediamill case, too much memory
                                )
        predictor.fit(X,y)

        y_true = test_set[label_columns].to_numpy()
        x_test = test_set[instance_columns]

        explain = ""

        if( False ): # not doing explanation
            explain = "explain"
            rules_list = []
            print("Getting tree structure")
            predictor.get_tree_structure_df(rules_list)
            rules_df = pd.DataFrame(rules_list)
            rules_df["id"] =  rules_df["tree_id"].astype(str) + "_"  +   rules_df["node_id"].astype(str) 
            #rules_df.to_csv("rules.csv")
            del rules_list

            activations_list = [] 
            predictions, probabilities = predictor.predict_with_proba(x_test, y_true=y_true, activations_list=activations_list, explain_decisions = True) #y_true = y_true
            activation_df = pd.DataFrame(activations_list)
            activation_df["id"] =  activation_df["tree_id"].astype(str) + "_"  +   activation_df["node_id"].astype(str) 
            generate_explainable_datasets(rules_df,activation_df, label_columns )
            del activations_list
            generate_explainability_files(rules_df, labels_distrib,  labels_distrib_supervised, params["trees_quantity"])
            


        else:
            predictions, probabilities = predictor.predict_with_proba(x_test) #y_true = y_true

        results_pred = pd.DataFrame(predictions)
        results_prob = pd.DataFrame(probabilities)
        results_true = pd.DataFrame(y_true)

        params["auprc_curve_average_k_fold"] = auprc_curve/k_fold
        params["label_rank_average_precision_average_k_fold"] = label_rank_average_precision/k_fold
        params["average_precision_average_k_fold"] = average_precision/k_fold
        params["auc_micro_average_k_fold"] = auc_micro/k_fold
        params["auc_macro_average_k_fold"] = auc_macro/k_fold
        params["hamming_loss_average_k_fold"] = hamming_loss/k_fold
        params["accuracy_average_k_fold"] = accuracy/k_fold

        # as only the last model is kept, we are trusting that the performance is pretty close to the average
        o = save_report( model_path + '/', ds_name+f"{explain}_{unlabeled_ratio}_kfold_", y_true, predictions, probabilities, do_output=True, parameters=params)
        #print(o)
        final_list.append(o)

        if( explain == "explain"):
            print("testing on training data just supervised")
            y_true_train = train_set[label_columns].loc[labeled_instances.index].to_numpy()
            x_test_train = train_set[instance_columns].loc[labeled_instances.index]

            predictions, probabilities = predictor.predict_with_proba(x_test_train) #y_true = y_true
            o = save_report( model_path + '/', ds_name+f"test_on_train_{explain}_{unlabeled_ratio}_kfold_", y_true_train, predictions, probabilities, do_output=False, parameters=params)
        
        # predictor.save_model("./export")



    df = pd.DataFrame(data=final_list)
    df.to_csv(f'{explain}all_{ds_name}_{unlabeled_ratio}_params_kfold.csv')
    


if __name__ == '__main__':
    train()
    # A zero exit code causes the job to be marked a Succeeded.
    sys.exit(0)