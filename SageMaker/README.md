# SageMaker for Image Classification

We provide pretrained model using SageMaker Image Classification algorithm and you can deploy this model in SageMaker Endpoint. However, this model was trained using small amount of training data set.
If you want to train using your own training dataset, we provide sample notebook with image augmentation process and hyperparameter tuning.

You need to provide training dataset in zipped file with following structures:

```
ROOT_FOLDER
    \_ CLASS_1
        \_ file_1
        \_ file_2
        \_ file_n
    \_ CLASS_2
    \_ CLASS_N
```

## Model Deployment
1. Upload model file to S3
2. Create SageMaker model using image classification container image based on your preferred region, for example, use `75088953585.dkr.ecr.ap-southeast-1.amazonaws.com/image-classification:1` for Singapore region
3. Create SageMaker Endpoint Configuration with those model
4. Create SageMaker Endpoint based on those endpoint configuration
