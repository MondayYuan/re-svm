#process data
#######################
echo "process data ..."
cd ./data
#remove ?
python preprocess.py
#transform corpus to standard input xml
python transform_to_standard_input.py
#generate lexicon for pyltp
python generate_lexicon.py
#########################

#generate features for svm to train and test
##########################
echo "generate features ..."
cd ../features
python feature_extraction.py
##########################

#train svm model
echo "training svm ..."
cd ../train
python train.py
