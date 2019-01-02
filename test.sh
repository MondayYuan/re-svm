#predict
################################
echo "predict by svm ..."
cd ./predict
python predict.py
################################

#evalute result
###############################
echo "evaluating results ..."
cd ../test
#fuzzy evaluate
echo "fuzzy result:"
python test_fuzzy.py

#exact evalute
echo "exact result:"
python test_exact.py
