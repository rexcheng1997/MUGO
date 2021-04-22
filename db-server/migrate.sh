#!/bin/sh

CREATE_USER_ENDPOINT=localhost:5001/create-user
CREATE_MEDIA_ENDPOINT=localhost:5001/create-media
CREATE_AUCTION_ENDPOINT=localhost:5001/create-auction
CREATE_BID_ENDPOINT=localhost:5001/create-bid
CREATE_OWNERSHIP_ENDPOINT=localhost:5001/create-ownership

curl -X PUT localhost:5001/init

curl -X POST -H "Content-Type: application/json" -d '{"name":"Scott Joplin", "email":"scott@passed.com", "password":"my_pass", "mnemonic":"muffin put monster mandate execute enemy used truly defy poverty sorry target disease weather cook effort force awful shoulder until spring fiber medal abstract involve", "identity":0, "title":"An admirable artist"}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"name":"Ben Kessler", "email":"ben.k@studio.io", "password":"d6ae4b0a7d589ab549e7d6ecf268c1a7891f71ff5b9d08ef8dbae75d0bdb667d", "mnemonic":"wealth shoe talent prison disease protect during voyage moon balance enough want trouble all eye cinnamon wild sun someone poet candy change tide able tennis", "identity":0, "title":"Amateur guitarist / songwriter", "subscription":"2021-04-22 08:00:00"}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"name":"Jo Ramsey", "email":"jo.ram@berkeley.edu", "password":"c677562887601c784c72300f5b3a06db93225b3ccf1f8afbe2052890cc46b4de", "mnemonic":"ceiling decline arrive blind february surprise begin rib gauge iron member loan adult prosper bright fan false damage hope toilet mobile solve clown abstract damage", "identity":1, "subscription":"2021-04-22 08:00:00"}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"name":"James Go", "email":"james@google.com", "password":"9f15d310c422448135eb3c0e8ed7c6097c124f59e9590edd9112e8f6f70e0dba", "mnemonic":"young method olympic female plastic right tennis caution empty liar skirt armor gym void chimney erode become weasel wing peanut envelope carpet exotic about cushion", "identity":1, "subscription":"2021-04-22 08:00:00"}' $CREATE_USER_ENDPOINT

#curl -X POST -H "Content-Type: application/json" -d '{"name":"", "email":"", "password":"secret-pass", "mnemonic":"ski clarify dawn leopard grab amazing output fashion coin delay zero virtual demand pattern glance grocery critic mandate fever country cushion used reject able bone", "identity":0, "title":""}' $CREATE_USER_ENDPOINT

#curl -X POST -H "Content-Type: application/json" -d '{"name":"", "email":"", "password":"myPWD", "mnemonic":"ocean cup genius super exclude leaf attract wish trim gauge mutual twenty oyster spike mean prosper state adjust injury jeans fix payment release absorb host", "identity":0, "title":""}' $CREATE_USER_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"title":"Maple Leaf Rag", "uid":1, "full_audio":"test-cases/audios/Maple Leaf Rag.mp3", "demo_segment":"test-cases/audios/Maple Leaf Rag (demo).mp3", "cover":"test-cases/images/maple-leaf-rag.jpg", "dist_type":0, "plays":3121, "earnings":11.145}' $CREATE_MEDIA_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"title":"Blind", "uid":2, "full_audio":"test-cases/audios/Blind.mp3", "demo_segment":"test-cases/audios/demo-Blind.mp3", "cover":"test-cases/images/blind.png", "dist_type":1}' $CREATE_MEDIA_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"uid":2, "mid":2, "assetId":15440121, "start":"2021-04-22 18:00:00", "end":"2021-04-22 19:08:00", "amount":2, "minBid":0.21, "sold":2, "earnings":1.125}' $CREATE_AUCTION_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"bid":0.67, "uid":4, "aid":1}' $CREATE_BID_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"bid":0.58, "uid":3, "aid":1}' $CREATE_BID_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"uid":3, "aid":1, "mid":2}' $CREATE_OWNERSHIP_ENDPOINT

curl -X POST -H "Content-Type: application/json" -d '{"uid":4, "aid":1, "mid":2}' $CREATE_OWNERSHIP_ENDPOINT
