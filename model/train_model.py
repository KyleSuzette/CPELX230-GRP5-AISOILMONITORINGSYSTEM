"""Train scaled RBF SVM; tune on training folds only, evaluate untouched 20%."""
from pathlib import Path
import json, hashlib, time
import numpy as np
import pandas as pd
import sklearn, joblib
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
ROOT = Path(__file__).resolve().parents[1]
FEATURES = ['soil_moisture','temperature','humidity']
def train():
    df = pd.read_csv(ROOT/'dataset/soil_data.csv')
    X, y = df[FEATURES], df['label']
    if df.isna().any().any(): raise ValueError('Missing data')
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    pipe=Pipeline([('scaler',StandardScaler()),('svm',SVC(kernel='rbf',decision_function_shape='ovo'))])
    search=GridSearchCV(pipe,{'svm__C':[1,10,100], 'svm__gamma':[.1,.5,1]},scoring='f1_macro',cv=StratifiedKFold(3,shuffle=True,random_state=42),n_jobs=2)
    started=time.perf_counter();search.fit(Xtr,ytr);elapsed=time.perf_counter()-started
    model=search.best_estimator_
    model.set_params(svm__probability=True, svm__random_state=42)
    model.fit(Xtr,ytr)
    pred=model.predict(Xte)
    joblib.dump(model,ROOT/'model/soil_model.joblib')
    metrics={'model':'StandardScaler + RBF SVC','accuracy':float(accuracy_score(yte,pred)), 'classification_report':classification_report(yte,pred,output_dict=True),'confusion_matrix':confusion_matrix(yte,pred,labels=model.classes_).tolist(),'classes':model.classes_.tolist(),'features':FEATURES,'train_rows':len(Xtr),'test_rows':len(Xte),'best_parameters':search.best_params_,'training_cv_macro_f1':search.best_score_,'search_seconds':elapsed,'sklearn_version':sklearn.__version__,'support_vectors':int(len(model['svm'].support_)),'dataset_sha256':hashlib.sha256((ROOT/'dataset/soil_data.csv').read_bytes()).hexdigest(),'data_source':'Existing synthetic demonstration dataset; labels from assumed demand formula, not observed irrigation outcomes.'}
    pd.DataFrame(search.cv_results_).to_csv(ROOT/'model/cv_results.csv',index=False)
    pd.DataFrame({'row_index':Xte.index,'actual':yte.to_numpy(),'predicted':pred}).to_csv(ROOT/'model/test_predictions.csv',index=False)
    export_header(model)
    (ROOT/'model/metrics.json').write_text(json.dumps(metrics,indent=2))
    print(json.dumps(metrics,indent=2))
    return model,Xte

def export_header(model):
    s=model['scaler'];m=model['svm'];n=len(m.support_)
    def arr(a):
        a=np.asarray(a)
        if a.ndim==1:return '{'+','.join(format(float(x),'.17g') for x in a)+'}'
        return '{'+','.join(arr(row) for row in a)+'}'
    text='''#pragma once
#include <math.h>
// Generated from the trained sklearn pipeline. Input: moisture %, Celsius, RH %.
'''
    text+=f'const int SVM_N = {n};\n'
    for name,a in [('SVM_MEAN',s.mean_),('SVM_SCALE',s.scale_),('SVM_INTERCEPT',m.intercept_)]: text+=f'const double {name}[3] = {arr(a)};\n'
    text+=f'const double SVM_GAMMA = {m._gamma:.17g};\n'
    text+='const int SVM_COUNTS[3] = {'+','.join(str(int(x)) for x in m.n_support_)+'};\n'
    text+=f'const double SVM_SUPPORT[{n}][3] = {arr(m.support_vectors_)};\n'
    text+=f'const double SVM_DUAL[2][{n}] = {arr(m.dual_coef_)};\n'
    text+='const char* const SVM_LABELS[3] = {'+','.join(json.dumps(str(x)) for x in m.classes_)+'};\n'
    text+='''
int predictSoilClass(double soil, double temp, double hum) {
  double input[3] = {soil, temp, hum};
  for (int f=0; f<3; f++) input[f]=(input[f]-SVM_MEAN[f])/SVM_SCALE[f];
  static double kernels[SVM_N];
  for(int v=0; v<SVM_N; v++) {
    double dist=0;
    for(int f=0; f<3; f++){double d=input[f]-SVM_SUPPORT[v][f];dist+=d*d;}
    kernels[v]=exp(-SVM_GAMMA*dist);
  }
  int starts[3]={0,SVM_COUNTS[0],SVM_COUNTS[0]+SVM_COUNTS[1]};
  int votes[3]={0,0,0};int p=0;
  for(int i=0;i<3;i++)for(int j=i+1;j<3;j++) {
    double score=SVM_INTERCEPT[p++];
    for(int k=starts[i];k<starts[i]+SVM_COUNTS[i];k++)score+=SVM_DUAL[j-1][k]*kernels[k];
    for(int k=starts[j];k<starts[j]+SVM_COUNTS[j];k++)score+=SVM_DUAL[i][k]*kernels[k];
    if(score>0)votes[i]++;else votes[j]++;
  }
  int best=0;for(int i=1;i<3;i++)if(votes[i]>votes[best])best=i;
  return best;
}
const char* predictSoil(double soil,double temp,double hum) {
  return SVM_LABELS[predictSoilClass(soil,temp,hum)];
}
'''
    (ROOT/'wokwi/soil_svm.h').write_text(text)
if __name__=='__main__':train()
