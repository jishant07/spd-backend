const functions = require('firebase-functions');
var admin = require("firebase-admin");
var serviceAccount = require("./creds.json");

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  apiKey: "AIzaSyCvOnhAMLieROhj4Izn11_fOWUysMJr2l0",
    authDomain: "spd-app-7afb5.firebaseapp.com",
    databaseURL: "https://spd-app-7afb5.firebaseio.com",
    projectId: "spd-app-7afb5",
    storageBucket: "spd-app-7afb5.appspot.com",
    messagingSenderId: "96825037575",
    appId: "1:96825037575:web:35700e96b2441d12cf2ba2"
});

dbref = admin.firestore();

exports.addUID = functions.https.onRequest((request, response) => {
    if(request.method === "POST")
    {
        if(request.body.UID !== "")
        {
            dbref.collection('users').doc(request.body.UID).get()
            .then(snapshot => {
                if(snapshot.exists)
                {
                    response.status(200)
                    .json({
                        message: "User Added"
                    })
                }
                else
                {
                    dbref.collection('users').doc(request.body.UID).set({
                        UID:request.body.UID
                    })
                    .then(doc =>{
                        response.status(200)
                        .json({
                            message: "User Added"
                        })
                        return null
                    })
                    .catch(err => {
                        response.json({
                            err
                        })
                    })
                }
                return null
            })
            .catch(err => {
                response.json({
                    err
                })
            })
        }
        else
        {
            response.status(404)
            .json({
                message:"Incomplete request"
            })
        }
    }
});


exports.addingLink = functions.https.onRequest((req,res) => {
    if(req.method === 'POST')
    {
        UID = req.body.UID;
        link = req.body.link;
        dbref.collection('users').doc(UID).get()
        .then(snapshot => {
            if(snapshot.exists)
            {
                doc_data = snapshot.data()
                if(doc_data['links'] === undefined)
                {
                    var link_array = [];
                    link_array.push(link)
                    link_string = JSON.stringify(link_array)
                }
                else
                {
                    json_data = JSON.parse(doc_data['links'])
                    json_data.push(link)
                    link_string = JSON.stringify(json_data)
                }
                dbref.collection('users').doc(UID).set({links:link_string})
                .then(ret => {
                    res.status(200)
                    .json({
                        message:"Link Added Successfully",
                    })
                    return null
                })
                .catch(err => {
                    res.json({
                        err
                    })
                })
                return null;
            }
            else
            {
                res.status(404)
                .json({
                    message : "UID Error"
                })
            }
            return null;
        })
        .catch(err => {
            res.json({
                err
            })
        })
    }
})


exports.gettingLinks = functions.https.onRequest((req,res)=>{
    if(req.method === 'POST')
    {
        UID = req.body.UID
        dbref.collection('users').doc(UID).get()
        .then(snapshot => {
            if(snapshot.exists)
            {
                doc_data = snapshot.data()
                if(doc_data['links'] !== undefined)
                {
                    json_data = JSON.parse(doc_data['links'])
                    res.status(200)
                    .json({
                        links_list : json_data
                    })
                }
                else
                {
                    res.status(200)
                    .json({
                        message: "No Encoded images"
                    })
                }
            }
            else
            {
                res.status(404)
                .json({
                    message:"UID Error"
                })
            }
            return null
        })
        .catch(err => {
            res.json({
                err
            })
        })
    }
})