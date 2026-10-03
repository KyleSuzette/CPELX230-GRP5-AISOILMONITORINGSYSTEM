# SVM training results

Trained on the supplied 6,000-row synthetic dataset. No new labels or measurements were collected.

- Inputs, in order: soil_moisture (%), temperature (C), humidity (air relative humidity %).
- StandardScaler + SVC, RBF kernel; C=1, gamma=0.1.
- Stratified 80/20 split, seed 42: 4,800 training and 1,200 test rows.
- Nine parameter combinations evaluated with three stratified training-only folds, scored by macro F1.
- Accuracy: 92.17% (1106/1,200 correct).
- Macro F1: 0.9080.
- Weighted F1: 0.9218.
- 1,325 support vectors. Scaling is fitted within the training pipeline, and included in the C++ export.
- Probability estimation fitted on the training set only; offline ESP32 returns class predictions only.

| Actual / predicted | NO_WATER | WATER_NOW | WATER_SOON |
|---|---:|---:|---:|
| NO_WATER | 570 | 0 | 27 |
| WATER_NOW | 0 | 159 | 27 |
| WATER_SOON | 22 | 18 | 377 |

The dataset generator uses an assumed watering-demand formula and random noise. Accuracy measures agreement with those synthetic labels, not agricultural effectiveness or real sensor accuracy. Training moisture range is roughly 5–95%, temperature 15–42 C, humidity 20–98%; predictions beyond these ranges are extrapolations.

The test set was excluded from scaler fitting, parameter selection, SVM fitting, and probability estimation. The shipped model is the evaluated training-set model; it was not subsequently refitted on test rows.
