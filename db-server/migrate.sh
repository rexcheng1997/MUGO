#!/bin/sh

CREATE_USER_ENDPOINT=localhost:5001/create-user
CREATE_MEDIA_ENDPOINT=localhost:5001/create-media
CREATE_AUCTION_ENDPOINT=localhost:5001/create-auction
CREATE_BID_ENDPOINT=localhost:5001/create-bid
CREATE_OWNERSHIP_ENDPOINT=localhost:5001/create-ownership

curl -X PUT localhost:5001/init

curl -X POST -H "Content-Type: application/json" -d '{"name":"Scott Joplin", "email":"scott@passed.com", "password":"my_pass", "mnemonic":"apple banana orange juice ham harbor execute", "identity":0, "title":"An admirable artist"}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"name":"Ben Kessler", "email":"ben.k@studio.eu", "password":"secret-pass", "mnemonic":"should be encrypted this is a sample mnemonic for testing purpose", "identity":0, "title":"Amateur guitarist / songwriter"}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"name":"Jo Ramsey", "email":"jo.ram@berkeley.edu", "password":"password", "mnemonic":"should be encrypted this is a sample mnemonic for testing purpose", "identity":1}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"title":"Maple Leaf Rag", "uid":1, "full_audio":"test-cases/audios/Maple Leaf Rag.mp3", "demo_segment":"test-cases/audios/Maple Leaf Rag.mp3", "cover":"test-cases/images/maple-leaf-rag.jpg", "dist_type":0, "plays":3121, "earnings":110.1245}' $CREATE_MEDIA_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"title":"OH JESUS CHRIS (Remix)", "uid":2, "full_audio":"test-cases/audios/OH JESUS CHRIS (Remix).mp3", "demo_segment":"test-cases/audios/OH JESUS CHRIS (Remix).mp3", "cover":"test-cases/images/oh-jesus-chris.png", "dist_type":1}' $CREATE_MEDIA_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"uid":2, "mid":2, "assetId":100234, "start":"2021-04-08T09:00:00-07:00", "end":"2021-05-12T23:59:59-07:00", "amount":10}' $CREATE_AUCTION_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"bid":3.33, "uid":3, "aid":1}' $CREATE_BID_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"uid":3, "aid":1, "mid":2}' $CREATE_OWNERSHIP_ENDPOINT
