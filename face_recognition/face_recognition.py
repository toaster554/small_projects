import boto3
import io
import os
import dill
import argparse
from PIL import Image, ImageDraw, ExifTags, ImageColor
from cv2 import *

parser = argparse.ArgumentParser()
parser.add_argument('--path', default = 'user_to_id.pkl')
parser.add_argument('--user_type')
parser.add_argument('--user_name')
parser.add_argument('--bucket')
parser.add_argument('--collection')

args = parser.parse_args()

# create collection for storing face_id
def create_collection(collection_id, verbose = False):

    client = boto3.client('rekognition')

    #Create a collection
    response = client.create_collection(CollectionId = collection_id)
    if verbose:
        print('Creating collection:' + collection_id)
        print('Collection ARN: ' + response['CollectionArn'])
        print('Status code: ' + str(response['StatusCode']))
        print('Done...')

# upload local_file to aws s3b bucket as s3_file
def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3')
    
    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

# add photo from bucket to collection_id
# returns the number of faces indexed their ids, 
# and their bounding boxes
def add_faces_to_collection(bucket, photo, collection_id, verbose = False):
    indexed_face_box = None
    indexed_face_id = None
    client = boto3.client('rekognition')

    response = client.index_faces(CollectionId = collection_id,
                                  Image = {'S3Object': {'Bucket': bucket,'Name': photo}},
                                  ExternalImageId = photo,
                                  MaxFaces = 1,
                                  QualityFilter = "AUTO",
                                  DetectionAttributes = ['ALL'])

    face_record = response['FaceRecords'][0]
    indexed_face_box = face_record['Face']['BoundingBox']
    indexed_face_id = face_record['Face']['FaceId']

    if verbose:
        print ('Results for ' + photo)
        print('Face indexed:')
        print('  Face ID: ' + face_record['Face']['FaceId'])
        print('  Location: {}'.format(face_record['Face']['BoundingBox']))

    return indexed_face_id

# given an image and values of face box, draw box on image
def draw_face_box(photo, box):
    with open(photo, 'rb') as image_file:
        stream = io.BytesIO(image_file.read())
        image = Image.open(stream)
        
        imgWidth, imgHeight = image.size
        draw = ImageDraw.Draw(image)
        
        left = imgWidth * box['Left']
        top = imgHeight * box['Top']
        width = imgWidth * box['Width']
        height = imgHeight * box['Height']
        
        points = (
            (left,top),
            (left + width, top),
            (left + width, top + height),
            (left , top + height),
            (left, top)
        )
        draw.line(points, fill = '#00d400', width = 2)
    
    image.show()

# given a photo, get (max_faces) most similar faces with similarity above
# threshold in collection (collection_id)
def face_lookup(photo, collection_id, threshold = 99, max_faces = 1, verbose = False):
    client = boto3.client('rekognition')
    
    with open(photo, 'rb') as image_file:
        stream = io.BytesIO(image_file.read())
        image = Image.open(stream)
  
    response = client.search_faces_by_image(CollectionId = collection_id,
                                            Image = {'Bytes': stream.getvalue()},
                                            FaceMatchThreshold = threshold,
                                            MaxFaces = max_faces)
    if not response['FaceMatches']:
        raise Exception('No faces detected')

    faceMatch = response['FaceMatches'][0]
    face_id = faceMatch['Face']['FaceId']
    similarity = int(faceMatch['Similarity'])
    if verbose:
        print ('Matching face')
        print (f'FaceId: {face_id}')
        print (f'Similarity: {similarity}%')

    return face_id, similarity


def main():
    path = args.path
    user_type = args.user_type
    user_name = args.user_name
    collection = args.collection
    bucket = args.bucket
    # load user_to_id
    with open(path, 'rb') as file:
        user_to_id = dill.load(file)

    id_to_user = {v: k for k, v in user_to_id.items()}

    # initialize camera
    cam = VideoCapture(0)
    # set resolution
    cam.set(CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(CAP_PROP_FRAME_HEIGHT, 720)
    s, img = cam.read()
    imwrite('temp.jpg', img)
    cam.release()
    destroyAllWindows()

    if user_type == 'new':
        upload_to_aws('temp.jpg', bucket, f'{user_name}.jpg')
        face_id = add_faces_to_collection(bucket, f'{user_name}.jpg', collection)
        user_to_id[user_name] = face_id

    elif user_type == 'existing':
        face_id, similarity = face_lookup('temp.jpg', collection)

        if similarity < 95 or face_id != user_to_id[user_name]:
            print('User\'s face does not match what is on database')
            print(f'User found: {id_to_user[face_id]}')
            return

        print(f'User found: {id_to_user[face_id]}')

    with open(path, 'wb') as file:
        dill.dump(user_to_id, file)


if __name__ == '__main__':
    main()