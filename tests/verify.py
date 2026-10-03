"""Verify Flask predictions and exported C++ SVM against Python."""
from pathlib import Path
import importlib.util, json, subprocess, tempfile
import numpy as np
import pandas as pd
import joblib
ROOT=Path(__file__).resolve().parents[1]
model=joblib.load(ROOT/'model/soil_model.joblib')
spec=importlib.util.spec_from_file_location('soil_app',ROOT/'app/app.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
client=module.app.test_client()
assert client.get('/').status_code==200
assert 'SVM' in client.get('/api/health').json['model']
df=pd.read_csv(ROOT/'dataset/soil_data.csv')
indices=pd.read_csv(ROOT/'model/test_predictions.csv')['row_index']
X=df.loc[indices, module.FEATURES]
for row in X.iloc[:30].to_dict('records'):
 expected=model.predict(pd.DataFrame([row],columns=module.FEATURES))[0]
 for endpoint in ['/api/predict','/api/sensor']:
  res=client.post(endpoint,json=row)
  assert res.status_code==200 and res.json['prediction']==expected
assert client.get('/api/latest').json['soil_moisture'] is not None
for bad in [{},{'soil_moisture':101,'temperature':24,'humidity':40},{'soil_moisture':20,'temperature':float('nan'),'humidity':40}]:
 assert client.post('/api/predict',json=bad).status_code==400
rng=np.random.default_rng(42)
extra=pd.DataFrame({'soil_moisture':rng.integers(0,101,2000),'temperature':rng.uniform(-10,60,2000),'humidity':rng.uniform(0,100,2000)})
allX=pd.concat([X,extra],ignore_index=True)
with tempfile.TemporaryDirectory() as td:
 td=Path(td);src=td/'verify.cpp';exe=td/'verify'
 src.write_text('#include <iostream>\n#include "soil_svm.h"\nint main(){double a,b,c;while(std::cin>>a>>b>>c)std::cout<<predictSoil(a,b,c)<<"\\n";}\n')
 subprocess.run(['g++','-std=c++11','-O2','-I',str(ROOT/'wokwi'),str(src),'-o',str(exe)],check=True)
 data='\n'.join(' '.join(format(float(v),'.17g') for v in row) for row in allX.to_numpy())
 out=subprocess.run([str(exe)],input=data,text=True,capture_output=True,check=True).stdout.splitlines()
 expected=model.predict(allX)
 matches=int(np.sum(expected==out));assert matches==len(allX),(matches,len(allX))
result={'flask_routes':'passed','invalid_input_checks':'passed','cpp_compilation':'passed with host g++','cpp_python_prediction_matches':matches,'comparison_rows':len(allX),'wokwi_browser_simulation':'not run','esp32_arduino_compilation':'not run; Arduino toolchain unavailable'}
(ROOT/'model/verification.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))
