# Face detection
**Description:** Face detection program using Amazon's Rekognition API. When ran, takes a picture of the user through available camera device. If user_type is "new", turns user image to face ID and store to a user name to face ID dictionary. If user_type is "existing", determine whether or not user's face is in the dictionary if above a certain threshold.  
**Packages used:** boto3, dill, open-cv, Pillow
## **Usage:**
```
python face_detection [--path] [--user_type] [--user_name] [--threshold] [--bucket] [--collection]
```
**Argument Descriptions:***  
- **path:** path to .pkl file containing user_to_id, a .pkl that contains User_name to face_ID dictionary. (Default = 'user_to_id.pkl')
- **user_type:** explained above
- **user_name:** name of user
- **threshold:** threshold for similarity between image taken and user_name's face ID in the database (Default = 99)
- **bucket:** name of S3 bucket ([How to create a bucket](https://docs.aws.amazon.com/AmazonS3/latest/gsg/CreatingABucket.html))
- **collection:** name of face ID collection ([How to create a collection](https://docs.aws.amazon.com/rekognition/latest/dg/create-collection-procedure.html))
