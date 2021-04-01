from flask import *
import boto3
import json
import base64   
from stegano import lsb
import requests
import io
from PIL import Image

app = Flask(__name__)

resource = boto3.resource('s3',aws_access_key_id='AKIAILPSC5UXRNDE5SZA',aws_secret_access_key='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')
client = boto3.client('s3',aws_access_key_id='AKIAILPSC5UXRNDE5SZA',aws_secret_access_key='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')
bucket = resource.Bucket('pdf-save-repo')
summary = bucket.objects.all()


@app.route("/",methods=["GET"])
def test():
    return "Hello From the App"

    
@app.route("/encode", methods=['POST'])
def encode():
    cover_image = request.form['cover_image']
    encode_string = request.form['data_to_be_encoded']
    password = request.form['pwd']
    UID = request.form['UID']
    count = 0
    for i in summary:
        if i.key.startswith('encoded_images/'):
            count = count + 1
    file_name = 'cover_images/img'+str(count)+'.png'
    image = base64.decodebytes(cover_image.encode())
    client.put_object(Bucket='pdf-save-repo',Body=image,Key=file_name)
    object_acl = resource.ObjectAcl('pdf-save-repo',file_name)
    object_acl = object_acl.put(ACL='public-read')
    response = requests.get("https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+file_name)
    img = Image.open(io.BytesIO(response.content))
    data = {'encoded_data':encode_string,'pwd':password}
    data = json.dumps(data)
    secret = lsb.hide(img, data)
    imgByteArr = io.BytesIO()
    secret.save(imgByteArr, format='PNG')
    imgByteArr = imgByteArr.getvalue()
    secret_image_string = base64.b64encode(imgByteArr)
    secret_file_name = 'encoded_images/img'+str(count)+'.png'
    client.put_object(Bucket='pdf-save-repo',Body=imgByteArr,Key=secret_file_name)
    object_acl = resource.ObjectAcl('pdf-save-repo',secret_file_name)
    object_acl = object_acl.put(ACL='public-read')
    obj = resource.Object("pdf-save-repo",file_name)
    obj.delete()
    link = "https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+secret_file_name
    url = 'https://us-central1-spd-app-7afb5.cloudfunctions.net/addingLink'
    myobj = {'UID':UID,'link':link}
    x = requests.post(url,data = myobj)
    if json.loads(x.text)['message'] == "Link Added Successfully":
        return {
            'secret_image_link': "https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+secret_file_name,
            'message' : "Link Added to DB"
        }
    else:
        return {
            'message' : "Link addition error"
        }

@app.route("/decodeText",methods=['POST'])
def decodeText():
    secret_image = request.form['secret_image']
    password = request.form['pwd']
    image = base64.decodebytes(secret_image.encode())
    count = 0
    for i in summary:
        if i.key.startswith('secret_decoder_images/'):
            count = count + 1
    secret_file_received = 'secret_decoder_images/img'+str(count)+'.png'
    client.put_object(Bucket='pdf-save-repo',Body=image,Key=secret_file_received)
    object_acl = resource.ObjectAcl('pdf-save-repo',secret_file_received)
    object_acl = object_acl.put(ACL='public-read')
    response = requests.get("https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+secret_file_received)
    img = Image.open(io.BytesIO(response.content))
    message = lsb.reveal(img)
    json_data = json.loads(message)
    obj = resource.Object("pdf-save-repo",secret_file_received)
    obj.delete()
    if json_data['pwd'] != password:
        return {
            'message': "Wrong password for the image"
        }
    else :
        return {
            'encoded_data': json_data['encoded_data']
        }

@app.route("/decodeImage",methods=['POST'])
def decodeImage():
    secret_image = request.form['secret_image']
    password = request.form['pwd']
    image = base64.decodebytes(secret_image.encode())
    count = 0
    for i in summary:
        if i.key.startswith('secret_decoder_images/'):
            count = count + 1
    file_name = 'secret_decoder_images/img'+str(count)+'.png'
    client.put_object(Bucket='pdf-save-repo',Body=image,Key=file_name)
    object_acl = resource.ObjectAcl('pdf-save-repo',file_name)
    object_acl = object_acl.put(ACL='public-read')
    response = requests.get("https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+file_name)
    img = Image.open(io.BytesIO(response.content))
    message = lsb.reveal(img)
    json_data = json.loads(message)
    obj = resource.Object("pdf-save-repo",file_name)
    obj.delete()
    if json_data['pwd'] != password:
        return {
            'message': "Wrong password for the image"
        }
    else :
        image_string = json_data['encoded_data']
        image = base64.decodebytes(image_string.encode())
        hidden_images_count = 0
        for i in summary:
            if i.key.startswith('decoded_hidden_images/'):
                hidden_images_count = hidden_images_count + 1
        hidden_image_file_name = 'decoded_hidden_images/img'+str(hidden_images_count)+'.png'
        client.put_object(Bucket='pdf-save-repo',Body=image,Key=hidden_image_file_name)
        object_acl = resource.ObjectAcl('pdf-save-repo',hidden_image_file_name)
        object_acl = object_acl.put(ACL='public-read')
        
        return {
            'link' : "https://pdf-save-repo.s3.ap-south-1.amazonaws.com/"+hidden_image_file_name
        }

if __name__ == '__main__':
    app.run(debug=True)