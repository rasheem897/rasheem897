# Hemorrhagic Stroke Detection in Brain CT Images Using YOLOv8

**Academic mini project | December 2024**  
**Focus:** Deep learning, computer vision and medical-image analysis

## Overview

This team project report describes an experimental approach to identifying and localizing suspected hemorrhagic regions in brain CT images using the YOLOv8 object-detection model. The intended use is as a decision-support research concept to help highlight regions for review, not to replace radiologists or provide a clinical diagnosis.

## Problem being addressed

Manual interpretation of CT images is an important part of stroke assessment. The project explores whether an object-detection model can identify image regions associated with hemorrhage and present localized predictions using bounding boxes.

## Dataset described in the report

- **Total images reported:** 5,511 brain CT images.
- **Classes:** hemorrhage-affected and unaffected images.
- **Annotations:** the report describes labeled regions used for supervised learning.
- **Preprocessing:** resizing and normalization; data augmentation is also discussed.

The report does not provide a public dataset link or the annotation files in the supplied material.

## Model and workflow described

1. Collect CT images representing hemorrhage-affected and unaffected cases.
2. Prepare images through resizing, normalization and augmentation.
3. Train a YOLOv8-based detector to identify suspected hemorrhagic regions.
4. Produce localized predictions, including bounding boxes and confidence information.
5. Evaluate the model using accuracy and other detection/classification metrics.

The results section also refers to ResNet-101 feature extraction. The report does not clearly reconcile that description with the YOLOv8 architecture narrative, so the exact end-to-end model pipeline should be confirmed from the original implementation.

## Reported training and result

| Item | Reported detail |
|---|---|
| Model | YOLOv8 |
| Training duration | 240 epochs |
| Dataset size | 5,511 CT images |
| Reported test accuracy | **76.27%** |

### Reproducibility caveats

The report describes more than one data split: a 70/15/15 train/test/validation split in one passage and an 80/20 train/test split later. The exact split used for the reported result must be verified against the training configuration.

The report also labels individual example images with 98% in a results figure. That is not the same as the dataset-level test accuracy, which the report states as 76.27%. Precision, recall and F1-score are mentioned as evaluation measures, but numerical values for those metrics are not supplied in the report.

## Tools and concepts

- YOLOv8 object detection
- Brain CT image preprocessing
- Image resizing and normalization
- Data augmentation
- Supervised annotations
- Bounding-box localization
- Model training, validation and testing

The supplied report does not specify enough implementation detail to confirm exact programming-language versions, package versions, training hyperparameters, random seeds or hardware configuration. Those should be added from the source project rather than inferred.

## Limitations and responsible use

- The reported test accuracy is an experimental result from the project report, not evidence of clinical readiness.
- External validation across hospitals, scanners and patient populations is not demonstrated in the supplied report.
- Dataset composition, annotation protocol and class balance need clearer documentation.
- The project is not a medical device and must not be used to diagnose, triage or make treatment decisions.

## Repository status

This page is based on the supplied academic mini-project report. The report PDF is not published here because it includes student identifiers and other academic-personal details. Source code, trained weights, dataset references, annotation files, exact configuration and reproducible evaluation scripts have not yet been supplied. Add those artifacts before describing the project as independently reproducible.

## Team and contribution

The report identifies this as a team mini project but does not specify individual task ownership. Add a precise personal-contribution section only after confirming the work you personally completed.
